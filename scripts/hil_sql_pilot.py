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
  rejudge    re-judge every question the agent asked with another rubric (default official)
  kb-map     which knowledge-base entries state each blocker resolution (saved per task; reusable)
  blocker-outcomes  per unit x blocker: info source (asked / retrieved KB / provided / none) and adherence
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


# ---------------------------------------------------------------- offline analysis of a finished run
# These stages read a finished run (--target-run) and use the live repository code; outputs record the commit.

FUNNEL_ACTIONS = ('asked', 'retrieved_kb', 'guessed', 'other_grounded', 'no_commit', 'not_noticed')
INFO_SOURCES = ('asked', 'retrieved_kb', 'provided_context', 'none')
VERDICTS = ('yes', 'partial', 'no', 'unclear')


def finished_units(run: Path, filters: list[str] | None = None) -> list[Path]:
    return sorted(p for p in (run / 'units').iterdir()
                  if p.is_dir() and not p.name.endswith('.tmp') and (p / 'summary.json').exists()
                  and (not filters or any(f in p.name for f in filters)))


def read_json(path: Path):
    return json.loads(path.read_text())


def write_jsonl(path: Path, rows: list[dict]):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))


def annotator_for(model: str):
    from info_seeking import annotate as an
    return an.Annotator(Path(os.environ['PV_WORK']) / 'cache' / 'hil-annotate', model=model, effort='low')


def stage_annotate(args):
    """Step awareness/commit labels and per-blocker resolution adherence for every finished unit."""
    from concurrent.futures import ThreadPoolExecutor
    from info_seeking import annotate as an
    from info_seeking.runs import git
    from info_seeking.trajectory import CONDITIONS
    run = args.target_run
    cfg = read_json(run / 'config.json')
    official = OfficialFiles(cfg['external_root'])
    annotator = annotator_for(args.model)
    out_dir = run / 'analysis' / 'annotations'
    out_dir.mkdir(parents=True, exist_ok=True)
    units = finished_units(run, args.units)
    jobs = []
    for unit in units:
        summary = read_json(unit / 'summary.json')
        task = load_task(Path(cfg['data_root']), summary['task_id'])
        records = [json.loads(line) for line in (unit / 'decisions.jsonl').read_text().splitlines()]
        # The annotator must see the question exactly as the agent did (full-info adds the clarifications).
        seen = (official.render_full_info(task['problem'], task['blockers'])
                if CONDITIONS[summary['condition']]['full_info'] else task['problem'])
        jobs += [(unit.name, 'step', r, an.step_prompt(task, r, seen)) for r in records]
        submitted = [r for r in records if r.get('action') == 'submit_sql']
        if submitted:
            jobs += [(unit.name, 'adherence', {'blocker_id': blocker_id}, prompt)
                     for blocker_id, prompt in an.adherence_prompts(task, submitted[-1]['arguments']['query'])]

    def run_job(job):
        name, kind, record, prompt = job
        verdict = annotator.ask(kind, prompt)
        if kind == 'step':
            record = {'step': record['step'], 'attempt': record.get('attempt', 0), 'action': record['action']}
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
        summary = read_json(unit / 'summary.json')
        task = load_task(Path(cfg['data_root']), summary['task_id'])
        unit_summary = an.summarize_unit(task, steps, adherence)  # also adds normalized blocker ids to steps
        (out_dir / f'{unit.name}.json').write_text(json.dumps({'meta': meta, 'steps': steps, 'adherence': adherence},
                                                              ensure_ascii=False, indent=1))
        overview[unit.name] = {'solve': summary['verify'].get('solve'), 'condition': summary['condition'], **unit_summary}
    (out_dir / 'overview.json').write_text(json.dumps({'meta': meta, 'units': overview}, ensure_ascii=False, indent=1))
    print(json.dumps(overview, ensure_ascii=False, indent=1))


def _resolved_under_cap(rows: list[dict], key_field: str) -> set[tuple[str, str]]:
    """(unit, blocker) pairs resolved in asking order, at most MAX_ANSWERED_QUESTIONS_PER_BLOCKER answers each."""
    from info_seeking.official import MAX_ANSWERED_QUESTIONS_PER_BLOCKER
    resolved, hits = set(), {}
    for r in sorted(rows, key=lambda x: (x['unit'], x['index'])):
        key = r[key_field]
        if key and hits.get((r['unit'], key), 0) < MAX_ANSWERED_QUESTIONS_PER_BLOCKER:
            hits[(r['unit'], key)] = hits.get((r['unit'], key), 0) + 1
            resolved.add((r['unit'], key))
    return resolved


def stage_rejudge(args):
    """Re-judge every question the agent asked with another rubric (default: official).

    Same questions, different judge: measures how much the rubric alone changes acceptance. It does not
    replay the trajectory (a rejected question would have changed what followed)."""
    from concurrent.futures import ThreadPoolExecutor
    from info_seeking.runs import git
    from info_seeking.simulator import ClaudeSimulator
    run = args.target_run
    cfg = read_json(run / 'config.json')
    official = OfficialFiles(cfg['external_root'])
    s = cfg['simulator']
    sim = ClaudeSimulator(official.judge_prompt, cache_dir=Path(os.environ['PV_WORK']) / 'cache' / 'hil-ask-judge',
                          model=s['model'], effort=s['effort'], timeout_seconds=s['timeout_seconds'],
                          retries=s['retries'], rubric=args.rubric)
    jobs = []
    for unit in finished_units(run):
        traj = read_json(unit / 'trajectory.json')
        task = load_task(Path(cfg['data_root']), traj['task_id'])
        jobs += [(unit.name, traj['condition'], task, i, q) for i, q in enumerate(traj['questions'])]

    def judge(job):
        name, condition, task, i, q = job
        text = q['question'].strip()
        verdict = sim.classify(task['blockers'], text) if len(text) >= 3 else {'status': 'too_short', 'blocker_key': None}
        ids = {b['id'] for b in task['blockers']}
        return {'unit': name, 'condition': condition, 'task_id': task['task_id'], 'index': i, 'question': q['question'],
                'loop_rubric_key': q['judged_blocker_key'], 'loop_outcome': q['outcome'],
                'rejudge_rubric': args.rubric,
                'rejudge_key': verdict.get('blocker_key') if verdict.get('blocker_key') in ids else None,
                'rejudge_status': verdict.get('status'), 'rejudge_parse_mode': verdict.get('parse_mode'),
                'n_blockers': len(task['blockers'])}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(judge, jobs))
    out_dir = run / 'analysis' / 'rejudge'
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / f'questions_{args.rubric}.jsonl', rows)
    summary = {'rejudge_rubric': args.rubric, 'loop_rubric': s['rubric'], 'code_commit': git('rev-parse', 'HEAD'),
               'created': datetime.now().isoformat(timespec='seconds'), 'by_condition': {}}
    for condition in sorted({r['condition'] for r in rows}):
        part = [r for r in rows if r['condition'] == condition]
        loop_rel = [r for r in part if r['loop_rubric_key']]
        re_rel = [r for r in part if r['rejudge_key']]
        loop_resolved = {(r['unit'], r['loop_rubric_key']) for r in part if r['loop_outcome'] == 'matched'}
        summary['by_condition'][condition] = {
            'questions': len(part), 'loop_relevant': len(loop_rel), 're_relevant': len(re_rel),
            'agree_same_key': sum(r['loop_rubric_key'] == r['rejudge_key'] for r in part),
            'loop_relevant_but_rejected': sum(not r['rejudge_key'] for r in loop_rel),
            're_relevant_but_loop_rejected': sum(not r['loop_rubric_key'] for r in re_rel),
            'different_blocker': sum(bool(r['loop_rubric_key'] and r['rejudge_key'] and r['loop_rubric_key'] != r['rejudge_key'])
                                     for r in part),
            'loop_unique_resolved': len(loop_resolved), 're_unique_resolved': len(_resolved_under_cap(part, 'rejudge_key')),
            're_status': {st: sum(str(r['rejudge_status']) == st for r in part)
                          for st in sorted({str(r['rejudge_status']) for r in part})}}
    (out_dir / f'summary_{args.rubric}.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def stage_kb_map(args):
    """Which knowledge-base entries state each blocker's resolution; saved per task as kb_resolution.json."""
    from concurrent.futures import ThreadPoolExecutor
    from info_seeking import annotate as an
    from info_seeking.runs import git
    cfg = read_json(args.target_run / 'config.json')
    data_root = Path(cfg['data_root'])
    annotator = annotator_for(args.model)
    tasks = {task_id: load_task(data_root, task_id) for task_id in run_task_ids(args.target_run)}
    jobs = [(task_id, b['id'], an.kb_map_prompt(task, b)) for task_id, task in tasks.items() for b in task['blockers']]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        verdicts = list(pool.map(lambda j: (j[0], j[1], annotator.ask('kb_map', j[2])), jobs))
    meta = {'annotator_model': args.model, 'code_commit': git('rev-parse', 'HEAD'),
            'annotate_py_sha256': sha256(Path(an.__file__)), 'created': datetime.now().isoformat(timespec='seconds')}
    out = {}
    for task_id, task in tasks.items():
        n_entries = len(task['business_info'])
        entries = {}
        for t, blocker_id, v in verdicts:
            if t == task_id:
                valid = [e for e in (v.get('entries') or [])
                         if isinstance(e, dict) and isinstance(e.get('index'), int) and 0 <= e['index'] < n_entries]
                entries[blocker_id] = {'status': v.get('status'), 'entries': valid, 'reason': v.get('reason')}
        record = {'meta': meta, 'task_id': task_id, 'n_business_info': n_entries, 'blockers': entries}
        (data_root / task_id / 'kb_resolution.json').write_text(json.dumps(record, ensure_ascii=False, indent=1))
        out[task_id] = {b: [(e['index'], e['coverage']) for e in x['entries']] for b, x in entries.items()}
    print(json.dumps(out, indent=1))


def _blocker_row(unit: Path, summary: dict, traj: dict, task: dict, blocker: dict, kb: dict,
                 retrieved: set[int], steps: list[dict], adherence: dict, full_info: bool) -> dict:
    """One unit x blocker: where the resolution was available, how the agent handled it, and whether the SQL follows it."""
    from info_seeking.annotate import GUESS_BASES
    bid = blocker['id']
    asked = any(q['blocker_name'] == bid for q in traj['questions'])
    kb_entries = {e['index']: e['coverage'] for e in kb.get(bid, {}).get('entries', [])}
    kb_hit = sorted(i for i in kb_entries if i in retrieved)
    sources = ['asked'] * asked + ['retrieved_kb'] * bool(kb_hit) + ['provided_context'] * full_info
    about = [s for s in steps if bid in (s.get('blockers_normalized') or [])]
    commit_steps = [s for s in steps if s.get('commits') and bid in (s.get('commit_blockers_normalized') or [])]
    bases = [s.get('basis') for s in commit_steps]
    aware_steps = [s['step'] for s in about if s.get('aware')]
    first_aware = min(aware_steps) if aware_steps else None
    first_commit = min((s['step'] for s in commit_steps), default=None)
    guessed = any(b in GUESS_BASES for b in bases)
    # Funnel action after noticing, by priority asked > retrieved > guessed (a blocker can have several).
    if first_aware is None:
        action = 'not_noticed'
    else:
        action = ('asked' if asked else 'retrieved_kb' if kb_hit else 'guessed' if guessed
                  else 'other_grounded' if bases else 'no_commit')
    return {'unit': unit.name, 'condition': summary['condition'], 'task_id': task['task_id'], 'blocker': bid,
            'type': blocker.get('type'), 'subtype': blocker.get('subtype'),
            'asked_and_answered': asked, 'kb_has_resolution': sorted(kb_entries.items()),
            'kb_retrieved_resolution': kb_hit, 'provided_context': full_info,
            'info_source': sources[0] if sources else 'none', 'all_sources': sources,
            'submitted': summary['end_reason'] == 'submitted', 'implemented': adherence.get(bid),
            'commit_bases': bases, 'last_commit_basis': bases[-1] if bases else None,
            'max_awareness_level': max((s.get('awareness_level') or 0 for s in about), default=0),
            'noticed': first_aware is not None, 'first_aware_step': first_aware, 'first_commit_step': first_commit,
            'noticed_before_first_commit': first_aware is not None and (first_commit is None or first_aware <= first_commit),
            'ever_guessed': guessed, 'action': action}


def _outcome_summary(part: list[dict]) -> dict:
    def count(pred):
        return sum(1 for r in part if pred(r))

    def judged(field, value):
        return [r for r in part if r[field] == value and r['submitted'] and r['implemented']]
    entry = {'blockers': len(part), 'kb_contains_resolution': count(lambda r: r['kb_has_resolution']),
             'kb_contains_full_resolution': count(lambda r: any(c == 'full' for _, c in r['kb_has_resolution'])),
             'asked_and_answered': count(lambda r: r['asked_and_answered']),
             'retrieved_from_kb': count(lambda r: r['kb_retrieved_resolution']),
             'max_awareness_level': {str(k): count(lambda r: r['max_awareness_level'] == k) for k in (0, 1, 2, 3)}}
    funnel = {'noticed': count(lambda r: r['noticed']),
              'noticed_before_first_commit': count(lambda r: r['noticed_before_first_commit'])}
    funnel.update({f'action:{a}': count(lambda r: r['action'] == a) for a in FUNNEL_ACTIONS})
    for a in FUNNEL_ACTIONS:
        rows = judged('action', a)
        funnel[f'{a}:implemented_yes/judged'] = f"{sum(r['implemented'] == 'yes' for r in rows)}/{len(rows)}"
    entry['funnel'] = funnel
    for source in INFO_SOURCES:
        rows = judged('info_source', source)
        entry[f'{source}:n_judged'] = len(rows)
        entry.update({f'{source}:{v}': sum(r['implemented'] == v for r in rows) for v in VERDICTS})
    return entry


def stage_blocker_outcomes(args):
    """Per unit x blocker table (blocker_outcomes.jsonl) and per-condition funnel (blocker_outcomes_summary.json).

    Needs the annotate stage (step labels, adherence) and kb-map (kb_resolution.json per task)."""
    from info_seeking.annotate import retrieved_entries
    from info_seeking.trajectory import CONDITIONS
    run = args.target_run
    data_root = Path(read_json(run / 'config.json')['data_root'])
    ann_dir = run / 'analysis' / 'annotations'
    rows = []
    for unit in finished_units(run):
        summary = read_json(unit / 'summary.json')
        traj = read_json(unit / 'trajectory.json')
        task = load_task(data_root, summary['task_id'])
        kb = read_json(data_root / task['task_id'] / 'kb_resolution.json')['blockers']
        records = [json.loads(line) for line in (unit / 'decisions.jsonl').read_text().splitlines()]
        ann_file = ann_dir / f'{unit.name}.json'
        ann = read_json(ann_file) if ann_file.exists() else {'steps': [], 'adherence': []}
        adherence = {a['blocker_id']: a.get('implemented') for a in ann['adherence']}
        retrieved = retrieved_entries(records, task['business_info'])
        full_info = CONDITIONS[summary['condition']]['full_info']
        rows += [_blocker_row(unit, summary, traj, task, b, kb, retrieved, ann['steps'], adherence, full_info)
                 for b in task['blockers']]
    out_dir = run / 'analysis'
    write_jsonl(out_dir / 'blocker_outcomes.jsonl', rows)
    table = {c: _outcome_summary([r for r in rows if r['condition'] == c]) for c in sorted({r['condition'] for r in rows})}
    (out_dir / 'blocker_outcomes_summary.json').write_text(json.dumps(table, indent=1))
    print(json.dumps(table, indent=1))


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
    p = sub.add_parser('kb-map', help='which knowledge-base entries state each blocker resolution (per task, reusable)')
    p.add_argument('--target-run', type=Path, required=True)
    p.add_argument('--model', default='haiku')
    p.add_argument('--workers', type=int, default=3)
    p = sub.add_parser('blocker-outcomes', help='per unit x blocker: information source and resolution adherence')
    p.add_argument('--target-run', type=Path, required=True)
    p = sub.add_parser('rejudge', help='offline re-judging of the asked questions with another rubric (live code)')
    p.add_argument('--target-run', type=Path, required=True)
    p.add_argument('--rubric', choices=('official', 'lenient'), default='official')
    p.add_argument('--workers', type=int, default=2)
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
     'calibrate-judge': stage_calibrate_judge, 'annotate': stage_annotate, 'rejudge': stage_rejudge,
     'kb-map': stage_kb_map, 'blocker-outcomes': stage_blocker_outcomes}[args.stage](args)


if __name__ == '__main__':
    main()
