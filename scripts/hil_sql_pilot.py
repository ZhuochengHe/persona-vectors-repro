"""is-hil-sql-pilot: Qwen3.5-9B on HiL-Bench SQL with decision-point activation capture.

Stages (run all but `init`/`summarize` inside a Slurm allocation):
  prepare    select the frozen subset and download its databases/schema CSVs
  init       create ${PV_WORK}/runs/<run_id>/ with frozen config, manifest, source and task list
  preflight  model/template/tokenizer/simulator/tool checks; writes preflight.json in the run dir
  run        execute units (task x condition x seed); --shard k/n splits units across jobs
  summarize  per-condition feasibility table (summary.json) from finished units
  probe      offline readout AUCs and difference-of-means directions (analysis/probe/)
  calibrate-judge  judge all registry example questions with the official and lenient rubrics
  annotate   offline Claude labels on a finished run: step awareness and per-blocker resolution adherence
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _source_root() -> Path:
    """Stages on an existing run import the run's frozen source, not the live repository."""
    if '--run-dir' in sys.argv:
        frozen = Path(sys.argv[sys.argv.index('--run-dir') + 1]).resolve() / 'source' / 'src'
        if not frozen.is_dir():
            raise FileNotFoundError(f'Run has no frozen source: {frozen}')
        return frozen
    return ROOT / 'src'


SOURCE_ROOT = _source_root()
sys.path[:0] = [str(SOURCE_ROOT)]
os.environ['PYTHONPATH'] = str(SOURCE_ROOT) + os.pathsep + os.environ.get('PYTHONPATH', '')

from info_seeking.data import load_sql_rows, load_task, materialize, select_subset  # noqa: E402
from info_seeking.official import OfficialFiles, sha256  # noqa: E402


def subset_file(cfg: dict) -> Path:
    return Path(cfg['data_root']) / f"subset_size{cfg['subset']['size']}_seed{cfg['subset']['seed']}.json"


def stage_prepare(args):
    from info_seeking.runs import load_cfg
    cfg = load_cfg(args.config)
    official = OfficialFiles(cfg['external_root'])
    rows = load_sql_rows(official.path('dataset'))
    if len(rows) != 100:
        raise ValueError(f'Expected 100 public SQL tasks, found {len(rows)}')
    chosen = select_subset(rows, cfg['subset']['size'], cfg['subset']['seed'])
    by_id = {r['task_id']: r for r in rows}
    data_root = Path(cfg['data_root'])
    data_root.mkdir(parents=True, exist_ok=True)
    for task_id in chosen:
        materialize(by_id[task_id], data_root)
        print(json.dumps({'materialized': task_id, 'database': by_id[task_id]['database_name'],
                          'n_blockers': len(by_id[task_id]['blockers'])}), flush=True)
    listing = {'task_ids': chosen, 'subset': cfg['subset'], 'dataset_sha256': sha256(official.path('dataset')),
               'n_blockers': {t: len(by_id[t]['blockers']) for t in chosen},
               'databases': {t: by_id[t]['database_name'] for t in chosen}}
    subset_file(cfg).write_text(json.dumps(listing, indent=1))
    from info_seeking.env import MiniLMRetriever
    MiniLMRetriever(cfg['tools']['retriever_revision'])  # cache the embedding model
    print(json.dumps({'subset_file': str(subset_file(cfg)), 'n': len(chosen)}))


def stage_init(args):
    # Lazy: runs initialised before runs.py existed must still import this script's other stages.
    from info_seeking.runs import create_run_dir, load_cfg
    cfg = load_cfg(args.config)
    official = OfficialFiles(cfg['external_root'])
    listing = json.loads(subset_file(cfg).read_text())
    task_ids = listing['task_ids'][:args.task_limit] if args.task_limit else listing['task_ids']
    run_dir = create_run_dir(run_id=args.run_id, purpose=args.purpose, config_path=args.config, cfg=cfg,
                             entry_files=['scripts/hil_sql_pilot.py', 'scripts/hil_sql_pilot.slurm'],
                             official_hashes=official.hashes(),
                             tasks={**listing, 'task_ids': task_ids, 'task_limit': args.task_limit})
    print(run_dir)


def run_task_ids(run_dir: Path) -> list[str]:
    tasks = run_dir / 'tasks' / 'tasks.json'
    if not tasks.exists():  # runs initialised before the shared run helper
        tasks = run_dir / 'tasks' / 'subset.json'
    return json.loads(tasks.read_text())['task_ids']


def build(run_dir: Path):
    from info_seeking.agent import QwenAgentRuntime
    from info_seeking.env import MiniLMRetriever, SQLTaskEnv
    from info_seeking.simulator import ClaudeSimulator
    cfg = json.loads((run_dir / 'config.json').read_text())
    official = OfficialFiles(cfg['external_root'])
    m = cfg['model']
    runtime = QwenAgentRuntime(m['id'], m['revision'], m['layers'], m['hidden'], m['attn_implementation'],
                               require_fast_kernels=m.get('require_fast_kernels', False)).load()
    retriever = MiniLMRetriever(cfg['tools']['retriever_revision'])
    s = cfg['simulator']
    simulator = ClaudeSimulator(official.judge_prompt, cache_dir=Path(os.environ['PV_WORK']) / 'cache' / 'hil-ask-judge',
                                model=s['model'], effort=s['effort'], timeout_seconds=s['timeout_seconds'],
                                retries=s['retries'], rubric=s['rubric'])

    def env_factory(task, ask_enabled):
        return SQLTaskEnv(task, ask_enabled=ask_enabled, simulator=simulator if ask_enabled else None,
                          retriever=retriever, sql_timeout_seconds=cfg['tools']['sql_timeout_seconds'],
                          external_root=cfg['external_root'], verify_timeout_seconds=cfg['tools']['verify_timeout_seconds'])
    return cfg, official, runtime, simulator, env_factory


def stage_preflight(args):
    import torch
    from info_seeking.agent import locate_positions, parse_generation
    from info_seeking.trajectory import instance_text
    cfg, official, runtime, simulator, env_factory = build(args.run_dir)
    report = {'host': os.uname().nodename, 'torch': torch.__version__, 'cuda': torch.cuda.get_device_name(0)}
    import transformers
    report['transformers'] = transformers.__version__
    report['python'] = sys.version
    report['fast_kernels'] = runtime.fast_kernels
    report['special_tokens'] = runtime.special
    report['stop_ids'] = runtime.stop_ids
    task_ids = run_task_ids(args.run_dir)
    task = load_task(Path(cfg['data_root']), task_ids[0])
    tools = official.tool_schemas(True)
    first = runtime.initial_prompt(official.system_prompt(True), instance_text(official, task, False), tools)
    report['first_prompt_tokens'] = len(first['ids'])
    report['first_prompt_tail'] = first['text'][-300:]
    continuations = runtime.tool_continuations([t['function']['name'] for t in tools])
    report['tool_continuations'] = {k: ([runtime.tokenizer.decode([i]) for i in v] if v else None)
                                    for k, v in continuations.items()}
    # Template agreement: canonical rendering of a 1-step conversation vs our appended IDs.
    from info_seeking.trajectory import OBS_FOOTER, OBS_HEADER
    fake_reasoning, fake_call = 'I will inspect the database.', '<tool_call>\n<function=get_database_info>\n<parameter=database_name>\nX\n</parameter>\n</function>\n</tool_call>'
    gen_text = f'{fake_reasoning}\n</think>\n\n{fake_call}<|im_end|>'
    gen = runtime.tokenizer.encode(gen_text, add_special_tokens=False)
    block, span = runtime.append_block(OBS_HEADER, 'OBSERVATION:\nresult', OBS_FOOTER)
    ours = first['ids'] + gen + block
    messages = [{'role': 'system', 'content': official.system_prompt(True)},
                {'role': 'user', 'content': instance_text(official, task, False)},
                {'role': 'assistant', 'content': '', 'reasoning_content': fake_reasoning,
                 'tool_calls': [{'type': 'function', 'function': {'name': 'get_database_info', 'arguments': {'database_name': 'X'}}}]},
                {'role': 'tool', 'content': 'OBSERVATION:\nresult'}]
    canonical = runtime.tokenizer.apply_chat_template(messages, tools=tools, tokenize=False,
                                                      add_generation_prompt=True, enable_thinking=True)
    ours_text = runtime.tokenizer.decode(ours, skip_special_tokens=False)
    report['template_text_equal'] = ours_text == canonical
    if not report['template_text_equal']:
        import difflib
        report['template_diff'] = list(difflib.unified_diff(canonical.splitlines(), ours_text.splitlines(), lineterm='', n=1))[:40]
    report['template_tokens_equal'] = runtime.tokenizer.encode(canonical, add_special_tokens=False) == ours
    report['obs_body_decoded'] = runtime.tokenizer.decode(block[span[0]:span[1]])
    parsed = parse_generation(gen_text, tools, official.end_names())
    report['parse_check'] = {'name': parsed.name, 'arguments': parsed.arguments, 'error': parsed.error_code}
    pos = locate_positions(runtime, gen, len(first['ids']))
    report['positions_check'] = {k: pos[k] for k in ('think_end', 'act_first', 'score_slot', 'score_slot_clean')}
    full = first['ids'] + gen
    report['position_tokens'] = {k: runtime.tokenizer.decode([full[pos[k]]]) for k in ('think_end', 'act_first', 'score_slot') if pos[k] is not None}
    # Capture with continuation scoring; 'pre' must equal a forward over the prompt alone (causality).
    points = {'pre': pos['pre'], 'think_end': pos['think_end'], 'act_first': pos['act_first'],
              'think_mean': pos['think_span'], 'input_mean': (0, len(first['ids']))}
    a_full, v_full, scores = runtime.capture(full, points, pos['score_slot'], continuations)
    a_pre, _, _ = runtime.capture(first['ids'], {'pre': pos['pre']})
    report['capture_pre_maxabs_diff'] = (a_full[0].float() - a_pre[0].float()).abs().max().item()
    report['capture_valid'] = v_full.tolist()
    report['capture_nonfinite'] = int((~torch.isfinite(a_full[v_full].float())).sum())
    report['capture_absmax'] = float(a_full[v_full].float().abs().max())
    report['tool_logprobs'] = scores
    # Cross-check the cached continuation score of the actual tool against full teacher forcing.
    cont = continuations.get('get_database_info')
    if cont and pos['score_slot'] is not None:
        rel = pos['score_slot'] + 1 - len(first['ids'])
        report['generated_matches_continuation'] = gen[rel:rel + len(cont)] == cont
        positions = torch.arange(pos['score_slot'], pos['score_slot'] + len(cont), device=runtime.model.device)
        tensor = torch.tensor([full], device=runtime.model.device)
        with torch.inference_mode():
            logits = runtime.model(input_ids=tensor, use_cache=False, logits_to_keep=positions).logits[0].float()
        reference = float(sum(torch.log_softmax(logits[j], -1)[cont[j]] for j in range(len(cont))))
        report['continuation_score_check'] = {'cached': scores['get_database_info'], 'teacher_forced': reference}
    # Real generation for one step (timing and format).
    t0 = time.time()
    real = runtime.generate(first['ids'], seed=0, sampler=cfg['sampler'], max_new_tokens=cfg['agent']['max_new_tokens'])
    report['gen_one_step'] = {'tokens': len(real), 'seconds': round(time.time() - t0, 1),
                              'text_tail': runtime.tokenizer.decode(real, skip_special_tokens=False)[-600:]}
    report['gen_parse'] = parse_generation(runtime.tokenizer.decode(real, skip_special_tokens=False), tools,
                                           official.end_names()).__dict__
    report['gen_parse'].pop('reasoning', None)
    # Tools and simulator.
    env = env_factory(task, True)
    report['tool_database_info'] = env.get_database_info(task['database_name'])[:500]
    report['tool_business_info'] = env.get_business_info(task['database_name'], task['problem'][:120])[:800]
    report['tool_execute_sql'] = env.execute_sql('SELECT name FROM sqlite_master LIMIT 3')[:300]
    report['tool_execute_write'] = env.execute_sql('CREATE TABLE preflight_should_fail(x INT)')
    blocker = task['blockers'][0]
    for label, question in (('example_question', blocker['example_questions'][0]),
                            ('irrelevant', 'What is your favourite colour?')):
        t1 = time.time()
        answer = env.ask_human(question)
        report[f'ask_{label}'] = {'question': question, 'answer': answer[:200], 'seconds': round(time.time() - t1, 1),
                                  'log': env.questions[-1]}
    report['ask_metrics'] = env.ask_metrics()
    env.submission = task['ground_truth_sql']
    report['verify_ground_truth'] = env.verify()
    out = args.run_dir / 'preflight.json'
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str))
    print(json.dumps(report, indent=1, ensure_ascii=False, default=str))


def units(run_dir: Path, cfg: dict) -> list[tuple[str, str, int]]:
    task_ids = run_task_ids(run_dir)
    return [(t, c, s) for t in task_ids for c in cfg['conditions'] for s in cfg['seeds']]


def stage_run(args):
    from info_seeking.trajectory import run_unit, unit_name
    cfg, official, runtime, simulator, env_factory = build(args.run_dir)
    k, n = (int(x) for x in args.shard.split('/'))
    todo = units(args.run_dir, cfg)[k::n]
    job = os.environ.get('SLURM_JOB_ID', 'local')
    log = args.run_dir / 'logs' / f'run_shard{k}of{n}_{job}.jsonl'
    finished = []
    for task_id, condition, seed in todo:
        out = args.run_dir / 'units' / unit_name(task_id, condition, seed)
        if (out / 'summary.json').exists():
            continue
        task = load_task(Path(cfg['data_root']), task_id)
        result = run_unit(runtime=runtime, official=official, task=task, condition=condition, seed=seed,
                          cfg=cfg, env_factory=env_factory, out_dir=out)
        line = {k2: result[k2] for k2 in ('task_id', 'condition', 'seed', 'end_reason', 'n_steps', 'seconds')}
        line.update(solve=result['verify'].get('solve'), ask=result['ask_metrics'])
        with open(log, 'a') as handle:
            handle.write(json.dumps(line) + '\n')
        print(json.dumps(line), flush=True)
        finished.append(unit_name(task_id, condition, seed))
    marker = {'job': job, 'shard': args.shard, 'units_assigned': len(todo), 'units_finished_this_job': finished,
              'finished': datetime.now().isoformat(timespec='seconds')}
    (args.run_dir / 'logs' / f'run_shard{k}of{n}_{job}.done.json').write_text(json.dumps(marker, indent=1))


def stage_summarize(args):
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    rows = []
    for task_id, condition, seed in units(args.run_dir, cfg):
        path = args.run_dir / 'units' / f'{task_id}__{condition}__s{seed}' / 'summary.json'
        if path.exists():
            rows.append(json.loads(path.read_text()))
    table = {}
    for condition in cfg['conditions']:
        group = [r for r in rows if r['condition'] == condition]
        if not group:
            continue
        n = len(group)
        entry = {'units': n, 'pass_at_1': sum(r['verify'].get('solve', 0) for r in group) / n,
                 'submitted': sum(r['end_reason'] == 'submitted' for r in group) / n,
                 'end_reasons': {e: sum(r['end_reason'] == e for r in group) for e in sorted({r['end_reason'] for r in group})},
                 'mean_steps': sum(r['n_steps'] for r in group) / n,
                 'format_error_steps': sum(r['n_format_errors'] for r in group),
                 'length_truncated_steps': sum(r['n_length_truncated'] for r in group),
                 'mean_seconds': sum(r['seconds'] for r in group) / n}
        entry['verify_errors'] = sum(1 for r in group if r['verify'].get('verify_error'))
        asks = [r['ask_metrics'] for r in group if r['ask_metrics']]
        if asks:
            def f1(p, r):
                return 2 * p * r / (p + r) if p + r > 0 else 0.0
            q = sum(a['n_questions'] for a in asks)
            resolved = sum(a['blockers_resolved'] for a in asks)
            blockers = sum(a['n_blockers'] for a in asks)
            relevant = sum(a['n_relevant'] for a in asks)
            recall = resolved / blockers if blockers else 0.0
            p_h, p_p = (resolved / q if q else 0.0), (relevant / q if q else 0.0)
            # Micro (pooled) metrics as in official compute_hil_metrics; macro kept as extra columns.
            entry['ask'] = {'share_units_asking': sum(a['n_questions'] > 0 for a in asks) / len(asks),
                            'mean_questions': q / len(asks), 'questions': q, 'blockers': blockers,
                            'blockers_resolved': resolved, 'recall': recall,
                            'precision_harness': p_h, 'f1_harness': f1(p_h, recall),
                            'precision_paper': p_p, 'f1_paper': f1(p_p, recall),
                            'macro': {m: sum(a[m] for a in asks) / len(asks) for m in
                                      ('recall', 'precision_harness', 'f1_harness', 'precision_paper', 'f1_paper')},
                            **{k: sum(a.get(f'n_{k}', 0) for a in asks) for k in
                               ('judge_failures', 'judge_parse_failed', 'judge_transport_failed', 'capped')}}
        table[condition] = entry
    out = {'run_dir': str(args.run_dir), 'units_found': len(rows), 'units_expected': len(units(args.run_dir, cfg)),
           'by_condition': table}
    (args.run_dir / 'summary.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def stage_calibrate_judge(args):
    """Judge every registry example question of the run's tasks with both rubrics (no model needed).

    The examples are the registry's own canonical phrasings, so the match rate to the *correct*
    blocker is an upper reference for judge recall; a strict judge that rejects them will also
    reject the agent's comparable questions."""
    from concurrent.futures import ThreadPoolExecutor
    from info_seeking.simulator import ClaudeSimulator
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    official = OfficialFiles(cfg['external_root'])
    s = cfg['simulator']
    cache = Path(os.environ['PV_WORK']) / 'cache' / 'hil-ask-judge'
    sims = {r: ClaudeSimulator(official.judge_prompt, cache_dir=cache, model=s['model'], effort=s['effort'],
                               timeout_seconds=s['timeout_seconds'], retries=s['retries'], rubric=r)
            for r in ('official', 'lenient')}
    task_ids = json.loads(subset_file(cfg).read_text())['task_ids']  # the full frozen subset, not a smoke limit
    jobs = []
    for task_id in task_ids:
        task = load_task(Path(cfg['data_root']), task_id)
        for blocker in task['blockers']:
            for question in blocker['example_questions']:
                for rubric in sims:
                    jobs.append((task_id, task['blockers'], blocker['id'], question, rubric))

    def judge(job):
        task_id, blockers, expected, question, rubric = job
        verdict = sims[rubric].classify(blockers, question)
        return {'task_id': task_id, 'expected': expected, 'question': question, 'rubric': rubric,
                'status': verdict['status'], 'judged': verdict.get('blocker_key'),
                'parse_mode': verdict.get('parse_mode'), 'correct': verdict.get('blocker_key') == expected}
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(judge, jobs))
    out_dir = args.run_dir / 'analysis'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'judge_calibration.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    summary = {}
    for rubric in sims:
        group = [r for r in rows if r['rubric'] == rubric]
        summary[rubric] = {'n': len(group), 'correct_blocker': sum(r['correct'] for r in group) / len(group),
                           'rejected': sum(r['judged'] is None for r in group) / len(group),
                           'wrong_blocker': sum(r['judged'] is not None and not r['correct'] for r in group) / len(group),
                           'not_ok': sum(r['status'] != 'ok' for r in group),
                           'parse_modes': {m: sum(r['parse_mode'] == m for r in group)
                                           for m in sorted({str(r['parse_mode']) for r in group})}}
    (out_dir / 'judge_calibration_summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def stage_annotate(args):
    """Offline Claude annotation of a finished run's trajectories (live repository code, recorded)."""
    from concurrent.futures import ThreadPoolExecutor
    from info_seeking import annotate as an
    from info_seeking.runs import git
    run = args.target_run
    cfg = json.loads((run / 'config.json').read_text())
    from info_seeking.trajectory import CONDITIONS
    official = OfficialFiles(cfg['external_root'])
    annotator = an.Annotator(Path(os.environ['PV_WORK']) / 'cache' / 'hil-annotate', model=args.model, effort='low')
    out_dir = run / 'analysis' / 'annotations'
    out_dir.mkdir(parents=True, exist_ok=True)
    units = sorted(p for p in (run / 'units').iterdir() if p.is_dir() and not p.name.endswith('.tmp')
                   and (p / 'summary.json').exists() and (not args.units or any(u in p.name for u in args.units)))
    jobs = []
    for unit in units:
        summary = json.loads((unit / 'summary.json').read_text())
        task = load_task(Path(cfg['data_root']), summary['task_id'])
        records = [json.loads(line) for line in (unit / 'decisions.jsonl').read_text().splitlines()]
        spec = CONDITIONS[summary['condition']]
        seen = official.render_full_info(task['problem'], task['blockers']) if spec['full_info'] else task['problem']
        for r in records:
            jobs.append((unit.name, 'step', r, an.step_prompt(task, r, seen)))
        submitted = [r for r in records if r.get('action') == 'submit_sql']
        if submitted:
            for blocker_id, prompt in an.adherence_prompts(task, submitted[-1]['arguments']['query']):
                jobs.append((unit.name, 'adherence', {'blocker_id': blocker_id}, prompt))

    def run_job(job):
        name, kind, record, prompt = job
        verdict = annotator.ask(kind, prompt)
        if kind == 'step':
            return name, kind, {'step': record['step'], 'attempt': record.get('attempt', 0), 'action': record['action'], **verdict}
        return name, kind, {**record, **verdict}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run_job, jobs))
    meta = {'annotator_model': args.model, 'code_commit': git('rev-parse', 'HEAD'),
            'code_dirty': bool(git('status', '--porcelain', '--', 'src/info_seeking/annotate.py')),
            'annotate_py_sha256': sha256(Path(an.__file__)), 'created': datetime.now().isoformat(timespec='seconds')}
    overview = {}
    for unit in units:
        steps = [r for n, k, r in results if n == unit.name and k == 'step']
        adherence = [r for n, k, r in results if n == unit.name and k == 'adherence']
        summary = json.loads((unit / 'summary.json').read_text())
        task = load_task(Path(cfg['data_root']), summary['task_id'])
        unit_summary = an.summarize_unit(task, steps, adherence)  # also adds blockers_normalized to steps
        (out_dir / f'{unit.name}.json').write_text(json.dumps({'meta': meta, 'steps': steps, 'adherence': adherence},
                                                              ensure_ascii=False, indent=1))
        overview[unit.name] = {'solve': summary['verify'].get('solve'), 'condition': summary['condition'], **unit_summary}
    (out_dir / 'overview.json').write_text(json.dumps({'meta': meta, 'units': overview}, ensure_ascii=False, indent=1))
    print(json.dumps(overview, ensure_ascii=False, indent=1))


def stage_probe(args):
    from info_seeking.probe_analysis import analyse
    analyse(args.run_dir, args.run_dir / 'analysis' / 'probe')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='stage', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--config', type=Path, required=True)
    p = sub.add_parser('init'); p.add_argument('--config', type=Path, required=True); p.add_argument('--run-id', required=True)
    p.add_argument('--purpose', choices=('smoke', 'subset', 'full'), required=True)
    p.add_argument('--task-limit', type=int, default=None)
    for name in ('preflight', 'run', 'summarize', 'probe', 'calibrate-judge'):
        p = sub.add_parser(name); p.add_argument('--run-dir', type=Path, required=True)
        if name == 'run':
            p.add_argument('--shard', default='0/1')
    p = sub.add_parser('annotate', help='offline Claude annotation of a finished run (uses live repository code)')
    p.add_argument('--target-run', type=Path, required=True)
    p.add_argument('--units', nargs='*', default=None, help='substring filters on unit names')
    p.add_argument('--model', default='haiku')
    p.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if getattr(args, 'config', None) is not None:
        args.config = args.config.resolve()
    {'prepare': stage_prepare, 'init': stage_init, 'preflight': stage_preflight,
     'run': stage_run, 'summarize': stage_summarize, 'probe': stage_probe,
     'calibrate-judge': stage_calibrate_judge, 'annotate': stage_annotate}[args.stage](args)


if __name__ == '__main__':
    main()
