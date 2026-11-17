"""is-when2call-extraction: Qwen3.5-9B readouts and directions on When2Call (single-turn tool use).

Stages (all but `init`/`summarize` inside a Slurm allocation):
  init       freeze config/source and the split/pilot task list into ${PV_WORK}/runs/<run_id>/
  preflight  template, MCQ candidate rendering, one generation and one judge call; writes preflight.json
  forward    all MCQ items: thinking-on prompt activations (pre, input_mean, user_mean) and
             non-thinking MCQ log-likelihoods; --shard k/n
  generate   pilot free generation with thinking (native and ask_tool conditions) with decision-point
             activations and behaviour labels; --shard k/n
  summarize  MCQ metrics and pilot behaviour table (summary.json)
  probe      train-split readout AUCs and difference-of-means directions (analysis/probe/)
"""
from __future__ import annotations

import argparse
import json
import os
import random
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

from info_seeking import when2call as w2c  # noqa: E402
from info_seeking.runs import create_run_dir, load_cfg  # noqa: E402

FORWARD_KEYS = ('pre', 'input_mean', 'user_mean')
GEN_KEYS = ('pre', 'think_end', 'act_first', 'think_mean', 'input_mean', 'user_mean')
VARIANTS = ('tool_call', 'request_for_info', 'cannot_answer')


# ---- task list --------------------------------------------------------------------------------
def stage_init(args):
    cfg = load_cfg(args.config)
    items = w2c.load_items(w2c.pinned_path(cfg['external_root'], 'mcq'))
    group = w2c.toolset_group(items)
    sp = cfg['split']
    split = {sid: w2c.split_of(g, sp['seed'], (sp['train'], sp['dev'])) for sid, g in group.items()}
    variants = {}
    for item in items:
        variants.setdefault(item['source_id'], set()).add(item['correct_answer'])
    triplets = sorted(sid for sid, v in variants.items() if v == set(VARIANTS) and split[sid] == 'train')
    g = cfg['generate']
    pilot = sorted(random.Random(g['pilot_seed']).sample(triplets, min(g['pilot_source_ids'], len(triplets))))
    if args.pilot_limit:
        pilot = pilot[:args.pilot_limit]
    counts = {s: sum(1 for i in items if split[i['source_id']] == s) for s in ('train', 'dev', 'test')}
    tasks = {'n_items': len(items), 'split_counts': counts, 'n_groups': len(set(group.values())),
             'split': split, 'group': group, 'pilot_source_ids': pilot, 'forward_limit': args.forward_limit}
    run_dir = create_run_dir(run_id=args.run_id, purpose=args.purpose, config_path=args.config, cfg=cfg,
                             entry_files=['scripts/when2call_extract.py', 'scripts/when2call_extract.slurm'],
                             official_hashes=w2c.pinned_hashes(cfg['external_root']), tasks=tasks,
                             subdirs=('forward', 'generate', 'logs'))
    print(json.dumps({'run_dir': str(run_dir), 'split_counts': counts, 'pilot': len(pilot)}))


def run_tasks(run_dir: Path) -> dict:
    return json.loads((run_dir / 'tasks' / 'tasks.json').read_text())


def build(run_dir: Path, need_judge: bool = False):
    from info_seeking.agent import QwenAgentRuntime
    cfg = json.loads((run_dir / 'config.json').read_text())
    m = cfg['model']
    runtime = QwenAgentRuntime(m['id'], m['revision'], m['layers'], m['hidden'], m['attn_implementation'],
                               require_fast_kernels=m.get('require_fast_kernels', False)).load()
    judge = None
    if need_judge:
        j = cfg['judge']
        judge = w2c.When2CallJudge(w2c.judge_prompt_template(cfg['external_root']),
                                   cache_dir=Path(os.environ['PV_WORK']) / 'cache' / 'w2c-judge',
                                   model=j['model'], effort=j['effort'], timeout=j['timeout_seconds'], retries=j['retries'])
    return cfg, runtime, judge


def items_by_uuid(cfg) -> dict:
    return {i['uuid']: i for i in w2c.load_items(w2c.pinned_path(cfg['external_root'], 'mcq'))}


def chunked(work: list, size: int) -> list[list]:
    return [work[i:i + size] for i in range(0, len(work), size)]


def write_chunk(out_dir: Path, index: int, rows: list[dict], acts, valid, keys) -> None:
    from safetensors.torch import save_file
    stem = out_dir / f'chunk_{index:05d}'
    tmp_rows, tmp_acts = stem.with_suffix('.jsonl.tmp'), stem.with_suffix('.safetensors.tmp')
    tmp_rows.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    save_file({'acts': acts.contiguous(), 'valid': valid.contiguous()}, str(tmp_acts),
              metadata={'position_keys': ','.join(keys), 'layers': '1-based block outputs; row i = layer i+1'})
    tmp_rows.rename(stem.with_suffix('.jsonl'))
    tmp_acts.rename(stem.with_suffix('.safetensors'))
    stem.with_suffix('.done').write_text(datetime.now().isoformat(timespec='seconds'))


def capture_keys(runtime, ids, points, keys):
    """Capture arbitrary named points; returns ([len(keys), L, H] bf16, valid [len(keys)])."""
    acts, valid, _ = runtime.capture(ids, points, keys=keys)
    return acts, valid


# ---- forward: prompt activations + MCQ ----------------------------------------------------------
def forward_work(cfg, tasks) -> list[str]:
    items = sorted(items_by_uuid(cfg).values(), key=lambda i: (i['source_id'], i['correct_answer']))
    uuids = [i['uuid'] for i in items]
    return uuids[:tasks['forward_limit']] if tasks.get('forward_limit') else uuids


def forward_item(runtime, item: dict, tasks: dict) -> tuple[dict, object, object]:
    first = runtime.initial_prompt(None, item['question'], w2c.tool_dicts(item, ask_tool=False))
    ids = first['ids']
    acts, valid = capture_keys(runtime, ids, {'pre': len(ids) - 1, 'input_mean': (0, len(ids)),
                                              'user_mean': first['user_span']}, FORWARD_KEYS)
    prompt, conts, texts = w2c.mcq_sequences(runtime.tokenizer, item)
    logp = {name: runtime.continuation_logprob(prompt, cont) for name, cont in conts.items()}
    nbytes = {name: len(texts[name].encode('utf-8')) for name in conts}
    row = {'uuid': item['uuid'], 'source_id': item['source_id'], 'gold': item['correct_answer'],
           'split': tasks['split'][item['source_id']], 'group': tasks['group'][item['source_id']],
           'held_out_param': item.get('held_out_param'), 'prompt_len': len(ids), 'user_span': first['user_span'],
           'mcq_logp': logp, 'mcq_bytes': nbytes, 'mcq_tokens': {k: len(v) for k, v in conts.items()},
           'pred': max(logp, key=logp.get), 'pred_norm': max(logp, key=lambda k: logp[k] / nbytes[k])}
    return row, acts, valid


def stage_forward(args):
    import torch
    cfg, runtime, _ = build(args.run_dir)
    tasks = run_tasks(args.run_dir)
    by_uuid = items_by_uuid(cfg)
    k, n = (int(x) for x in args.shard.split('/'))
    chunks = chunked(forward_work(cfg, tasks), cfg['forward']['chunk_size'])
    out_dir = args.run_dir / 'forward'
    for index in range(k, len(chunks), n):
        if (out_dir / f'chunk_{index:05d}.done').exists():
            continue
        started = time.time()
        rows, acts, valid = [], [], []
        for uuid in chunks[index]:
            row, a, v = forward_item(runtime, by_uuid[uuid], tasks)
            rows.append(row); acts.append(a); valid.append(v)
        write_chunk(out_dir, index, rows, torch.stack(acts), torch.stack(valid), FORWARD_KEYS)
        print(json.dumps({'forward_chunk': index, 'items': len(rows), 'seconds': round(time.time() - started, 1)}), flush=True)
    write_marker(args, 'forward')


# ---- generate: pilot behaviour + decision-point activations --------------------------------------
def generate_work(cfg, tasks) -> list[tuple[str, str]]:
    by_source = {}
    for item in items_by_uuid(cfg).values():
        by_source.setdefault(item['source_id'], {})[item['correct_answer']] = item['uuid']
    return [(by_source[sid][variant], condition) for sid in tasks['pilot_source_ids'] for variant in VARIANTS
            for condition in cfg['generate']['conditions']]


def decision_slot(runtime, gen: list[int], prefix_len: int, think_rel: int | None) -> int | None:
    """Last position before the first non-whitespace token after </think> (predicts call vs text)."""
    if think_rel is None:
        return None
    for j in range(think_rel + 1, len(gen)):
        if gen[j] == runtime.special['<tool_call>'] or runtime.tokenizer.decode([gen[j]]).strip():
            return prefix_len + j - 1
    return None


def generate_item(runtime, judge, cfg, item: dict, condition: str, tasks: dict):
    from info_seeking.agent import locate_positions, parse_generation, step_seed
    ask_tool = condition == 'ask_tool'
    tools = w2c.tool_dicts(item, ask_tool)
    first = runtime.initial_prompt(None, item['question'], tools)
    ids = first['ids']
    g = cfg['generate']
    t0 = time.time()
    gen = runtime.generate(ids, seed=step_seed(g['seed'], item['uuid'], condition), sampler=cfg['sampler'],
                           max_new_tokens=g['max_new_tokens'])
    gen_seconds = time.time() - t0
    stopped = bool(gen) and gen[-1] in runtime.stop_ids
    text = runtime.tokenizer.decode(gen, skip_special_tokens=False)
    action = parse_generation(text, tools, {})
    pos = locate_positions(runtime, gen, len(ids))
    full = ids + gen
    points = {'pre': pos['pre'], 'think_end': pos['think_end'], 'act_first': pos['act_first'],
              'think_mean': pos['think_span'] if pos['think_span'][1] > pos['think_span'][0] else None,
              'input_mean': (0, len(ids)), 'user_mean': first['user_span']}
    acts, valid = capture_keys(runtime, full, points, GEN_KEYS)
    tool_logprobs = None
    if pos['score_slot'] is not None and pos['score_slot_clean']:
        continuations = runtime.tool_continuations([t['function']['name'] for t in tools])
        _, _, tool_logprobs = runtime.capture(full, {}, pos['score_slot'], continuations)
    think_rel = pos['think_end'] - len(ids) if pos['think_end'] is not None else None
    slot = decision_slot(runtime, gen, len(ids), think_rel)
    logp_call = None
    if slot is not None:
        _, _, scores = runtime.capture(full, {}, slot, {'<tool_call>': [runtime.special['<tool_call>']]})
        logp_call = scores['<tool_call>']
    label = w2c.deterministic_label(action, item, ask_tool)
    judge_record = None
    if label['source'] == 'needs_judge':
        if not stopped or not pos['think_closed'] or not action.content:
            label = {'label': 'no_response', 'source': 'truncated_or_empty'}
        else:
            judge_record = judge.classify(item, action.content, ask_tool)
            label = {'label': judge_record['label'], 'source': 'judge', 'judge_status': judge_record['status']}
    row = {'uuid': item['uuid'], 'source_id': item['source_id'], 'variant': item['correct_answer'],
           'condition': condition, 'split': tasks['split'][item['source_id']],
           'group': tasks['group'][item['source_id']], 'held_out_param': item.get('held_out_param'),
           'prompt_len': len(ids), 'gen_len': len(gen), 'finish': 'eos' if stopped else 'length',
           'think_closed': pos['think_closed'], 'positions': {k: points[k] for k in GEN_KEYS},
           'decision_slot': slot, 'logp_tool_call_at_decision': logp_call, 'tool_logprobs': tool_logprobs,
           **{f'label_{k}' if k != 'label' else 'label': v for k, v in label.items()},
           'judge': judge_record, 'gen_seconds': round(gen_seconds, 2), 'text': text}
    return row, acts, valid


def stage_generate(args):
    import torch
    cfg, runtime, judge = build(args.run_dir, need_judge=True)
    tasks = run_tasks(args.run_dir)
    by_uuid = items_by_uuid(cfg)
    k, n = (int(x) for x in args.shard.split('/'))
    chunks = chunked(generate_work(cfg, tasks), cfg['generate']['chunk_size'])
    out_dir = args.run_dir / 'generate'
    for index in range(k, len(chunks), n):
        if (out_dir / f'chunk_{index:05d}.done').exists():
            continue
        started = time.time()
        rows, acts, valid = [], [], []
        for uuid, condition in chunks[index]:
            row, a, v = generate_item(runtime, judge, cfg, by_uuid[uuid], condition, tasks)
            rows.append(row); acts.append(a); valid.append(v)
        write_chunk(out_dir, index, rows, torch.stack(acts), torch.stack(valid), GEN_KEYS)
        print(json.dumps({'generate_chunk': index, 'items': len(rows), 'seconds': round(time.time() - started, 1)}), flush=True)
    write_marker(args, 'generate')


def write_marker(args, stage: str):
    job = os.environ.get('SLURM_JOB_ID', 'local')
    (args.run_dir / 'logs' / f'{stage}_shard{args.shard.replace("/", "of")}_{job}.done.json').write_text(
        json.dumps({'job': job, 'stage': stage, 'shard': args.shard, 'finished': datetime.now().isoformat(timespec='seconds')}))


# ---- summaries and probes ---------------------------------------------------------------------
def read_rows(directory: Path) -> list[dict]:
    rows = []
    for done in sorted(directory.glob('chunk_*.done')):
        rows.extend(json.loads(line) for line in done.with_suffix('.jsonl').read_text().splitlines())
    return rows


def stage_summarize(args):
    out = {'run_dir': str(args.run_dir)}
    forward = read_rows(args.run_dir / 'forward')
    if forward:
        out['mcq_nonthinking'] = {'all': w2c.mcq_metrics(forward)}
        for split in ('train', 'dev', 'test'):
            part = [r for r in forward if r['split'] == split]
            if part:
                out['mcq_nonthinking'][split] = w2c.mcq_metrics(part)
    gen = read_rows(args.run_dir / 'generate')
    if gen:
        table = {}
        for condition in sorted({r['condition'] for r in gen}):
            for variant in VARIANTS:
                part = [r for r in gen if r['condition'] == condition and r['variant'] == variant]
                if not part:
                    continue
                labels = [r['label'] for r in part]
                entry = {'n': len(part), 'labels': {l: labels.count(l) for l in sorted(set(map(str, labels)))},
                         'truncated': sum(r['finish'] == 'length' for r in part),
                         'judge_failures': sum(1 for r in part if r.get('label_judge_status') not in (None, 'ok')),
                         'mean_gen_len': sum(r['gen_len'] for r in part) / len(part)}
                calls = [r for r in part if r['label'] == 'tool_call' and r.get('label_held_out_supplied') is not None]
                if calls:
                    entry['tool_calls_supplying_held_out_param'] = sum(r['label_held_out_supplied'] for r in calls)
                    entry['tool_calls_with_held_out_param_field'] = len(calls)
                lp = [r['logp_tool_call_at_decision'] for r in part if r['logp_tool_call_at_decision'] is not None]
                if lp:
                    entry['mean_logp_tool_call_at_decision'] = sum(lp) / len(lp)
                table[f'{condition}/{variant}'] = entry
        out['pilot_generation'] = table
    (args.run_dir / 'summary.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def load_acts(directory: Path):
    import torch
    from safetensors.torch import load_file
    rows, acts, valid = [], [], []
    for done in sorted(directory.glob('chunk_*.done')):
        tensors = load_file(str(done.with_suffix('.safetensors')))
        rows.extend(json.loads(line) for line in done.with_suffix('.jsonl').read_text().splitlines())
        acts.append(tensors['acts']); valid.append(tensors['valid'])
    return rows, (torch.cat(acts) if acts else None), (torch.cat(valid) if valid else None)


def stage_probe(args):
    """Train split only (dev/test untouched). Positive label first in each name."""
    import torch
    from info_seeking.probe_analysis import readout
    out = args.run_dir / 'analysis' / 'probe'
    rows, acts, valid = load_acts(args.run_dir / 'forward')
    data = {}
    if acts is not None:
        def subset(pos_variant, neg_variant):
            index = [i for i, r in enumerate(rows) if r['split'] == 'train' and r['gold'] in (pos_variant, neg_variant)]
            return {'feats': acts[index], 'y': torch.tensor([rows[i]['gold'] == pos_variant for i in index]),
                    'groups': [rows[i]['group'] for i in index], 'valid': valid[index],
                    'baseline': torch.tensor([float(rows[i]['prompt_len']) for i in index])}
        data['rfi_vs_toolcall'] = subset('request_for_info', 'tool_call')     # missing parameter (+ paraphrase)
        data['cannot_vs_toolcall'] = subset('cannot_answer', 'tool_call')     # no suitable tool (same question)
        readout(data, FORWARD_KEYS, out / 'forward', baseline_name='prompt_len_auc')
    rows, acts, valid = load_acts(args.run_dir / 'generate')
    if acts is not None:
        data = {}
        for condition in sorted({r['condition'] for r in rows}):
            index = [i for i, r in enumerate(rows) if r['condition'] == condition and r['variant'] == 'request_for_info'
                     and r['label'] in ('request_for_info', 'tool_call')]
            if index:  # asked vs called the tool anyway, on items that lack a required parameter
                data[f'asked_vs_called_{condition}'] = {
                    'feats': acts[index], 'y': torch.tensor([rows[i]['label'] == 'request_for_info' for i in index]),
                    'groups': [rows[i]['group'] for i in index], 'valid': valid[index],
                    'baseline': torch.tensor([float(rows[i]['gen_len']) for i in index])}
        if data:
            readout(data, GEN_KEYS, out / 'generate', baseline_name='gen_len_auc')


def stage_preflight(args):
    import torch
    from info_seeking.agent import parse_generation
    cfg, runtime, judge = build(args.run_dir, need_judge=True)
    tasks = run_tasks(args.run_dir)
    by_uuid = items_by_uuid(cfg)
    report = {'python': sys.version, 'fast_kernels': runtime.fast_kernels, 'cuda': torch.cuda.get_device_name(0)}
    uuid, condition = generate_work(cfg, tasks)[2]  # a request_for_info item, native condition
    item = by_uuid[uuid]
    first = runtime.initial_prompt(None, item['question'], w2c.tool_dicts(item, False))
    report['prompt_tokens'] = len(first['ids'])
    report['prompt_tail'] = first['text'][-400:]
    report['user_span_text'] = runtime.tokenizer.decode(first['ids'][first['user_span'][0]:first['user_span'][1]])
    prompt, conts, texts = w2c.mcq_sequences(runtime.tokenizer, item)
    report['mcq_prompt_tail'] = runtime.tokenizer.decode(prompt)[-120:]
    report['mcq_candidates'] = texts
    t0 = time.time()
    row, acts, valid = forward_item(runtime, item, tasks)
    report['forward_item'] = {k: row[k] for k in ('gold', 'mcq_logp', 'pred', 'pred_norm')}
    report['forward_seconds'] = round(time.time() - t0, 2)
    report['forward_valid'] = valid.tolist()
    report['forward_nonfinite'] = int((~torch.isfinite(acts[valid].float())).sum())
    row, acts, valid = generate_item(runtime, judge, cfg, item, condition, tasks)
    report['generate_item'] = {k: row[k] for k in row if k not in ('text', 'positions')}
    report['generate_text_tail'] = row['text'][-800:]
    report['generate_valid'] = valid.tolist()
    report['judge_example'] = judge.classify(item, 'Could you tell me which city you mean?', False)
    report['parse_example'] = parse_generation(row['text'], w2c.tool_dicts(item, False), {}).__dict__
    report['parse_example'].pop('reasoning', None)
    (args.run_dir / 'preflight.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str))
    print(json.dumps(report, indent=1, ensure_ascii=False, default=str))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='stage', required=True)
    p = sub.add_parser('init')
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--purpose', choices=('smoke', 'pilot', 'full'), required=True)
    p.add_argument('--pilot-limit', type=int, default=None, help='smoke: first N pilot source_ids')
    p.add_argument('--forward-limit', type=int, default=None, help='smoke: first N forward items')
    for name in ('preflight', 'forward', 'generate', 'summarize', 'probe'):
        p = sub.add_parser(name)
        p.add_argument('--run-dir', type=Path, required=True)
        if name in ('forward', 'generate'):
            p.add_argument('--shard', default='0/1')
    args = parser.parse_args()
    if getattr(args, 'config', None) is not None:
        args.config = args.config.resolve()
    {'init': stage_init, 'preflight': stage_preflight, 'forward': stage_forward, 'generate': stage_generate,
     'summarize': stage_summarize, 'probe': stage_probe}[args.stage](args)


if __name__ == '__main__':
    main()
