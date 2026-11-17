"""is-ambiguity-probe: Sparse Neurons ambiguity probe reproduced on Qwen3.5-9B.

Stages (forward/probe inside a Slurm allocation):
  init     build the faithful (original files and split) and grouped (our fix + lexical control) sets
  forward  activations of each unique prompt (pre, input_mean, user_mean; all layers) per prefix mode; --shard k/n
  probe    sklearn probes per mode x protocol x dataset x position x layer, AEN noise analysis at the default
           layer, cross-dataset transfer, lexical control and length baseline (analysis/)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _source_root() -> Path:
    if '--run-dir' in sys.argv:
        frozen = Path(sys.argv[sys.argv.index('--run-dir') + 1]).resolve() / 'source' / 'src'
        if not frozen.is_dir():
            raise FileNotFoundError(f'Run has no frozen source: {frozen}')
        return frozen
    return ROOT / 'src'


SOURCE_ROOT = _source_root()
sys.path[:0] = [str(SOURCE_ROOT)]
os.environ['PYTHONPATH'] = str(SOURCE_ROOT) + os.pathsep + os.environ.get('PYTHONPATH', '')

from info_seeking import ambiguity as amb  # noqa: E402

KEYS = ('pre', 'input_mean', 'user_mean')


def stage_init(args):
    from info_seeking.runs import create_run_dir, load_cfg
    cfg = load_cfg(args.config)
    root = Path(cfg['data']['root'])
    task = amb.build_task(root, cfg['data'])
    if args.prompt_limit:  # smoke: keep only sets whose prompts fall in the first N
        keep = {p['uid'] for p in task['prompts'][:args.prompt_limit]}
        task['prompts'] = task['prompts'][:args.prompt_limit]
        task['sets'] = {k: [e for e in v if e['uid'] in keep] for k, v in task['sets'].items()}
    run_dir = create_run_dir(run_id=args.run_id, purpose=args.purpose, config_path=args.config, cfg=cfg,
                             entry_files=['scripts/ambiguity_probe.py', 'scripts/ambiguity_probe.slurm'],
                             official_hashes=amb.data_hashes(root), tasks=task, subdirs=('forward', 'analysis', 'logs'))
    print(json.dumps({'run_dir': str(run_dir), **task['info']}, indent=1))


def stage_forward(args):
    import torch
    from info_seeking.agent import QwenAgentRuntime
    from info_seeking.runs import chunk_done, write_chunk
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    prompts = json.loads((args.run_dir / 'tasks' / 'tasks.json').read_text())['prompts']
    m = cfg['model']
    runtime = QwenAgentRuntime(m['id'], m['revision'], m['layers'], m['hidden'], m['attn_implementation'],
                               require_fast_kernels=m.get('require_fast_kernels', False)).load()
    work = [(p, mode) for mode in cfg['modes'] for p in prompts]
    size = cfg['forward']['chunk_size']
    chunks = [work[i:i + size] for i in range(0, len(work), size)]
    k, n = (int(x) for x in args.shard.split('/'))
    out_dir = args.run_dir / 'forward'
    for index in range(k, len(chunks), n):
        if chunk_done(out_dir, index):
            continue
        started = time.time()
        rows, acts, valid = [], [], []
        for prompt, mode in chunks[index]:
            first = runtime.initial_prompt(amb.SYSTEM_MESSAGE, prompt['text'], None, enable_thinking=(mode == 'think'))
            ids = first['ids']
            a, v, _ = runtime.capture(ids, {'pre': len(ids) - 1, 'input_mean': (0, len(ids)),
                                            'user_mean': first['user_span']}, keys=KEYS)
            rows.append({'uid': prompt['uid'], 'mode': mode, 'prompt_len': len(ids),
                         'user_tokens': first['user_span'][1] - first['user_span'][0]})
            acts.append(a); valid.append(v)
        write_chunk(out_dir, index, rows, {'acts': torch.stack(acts), 'valid': torch.stack(valid)},
                    {'position_keys': ','.join(KEYS), 'layers': '1-based block outputs; row i = layer i+1'})
        print(json.dumps({'chunk': index, 'items': len(rows), 'seconds': round(time.time() - started, 1)}), flush=True)
    job = os.environ.get('SLURM_JOB_ID', 'local')
    (args.run_dir / 'logs' / f'forward_shard{k}of{n}_{job}.done.json').write_text(json.dumps({'job': job, 'shard': args.shard}))


def stage_probe(args):
    import csv
    import numpy as np
    from safetensors.numpy import save_file
    from sklearn.metrics import roc_auc_score
    from info_seeking.runs import read_chunks
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    p = cfg['probe']
    task = json.loads((args.run_dir / 'tasks' / 'tasks.json').read_text())
    rows, tensors = read_chunks(args.run_dir / 'forward')
    acts = tensors['acts'].float().numpy()  # [N, keys, layers, hidden]
    row_of = {(r['uid'], r['mode']): i for i, r in enumerate(rows)}
    user_tokens = {r['uid']: r['user_tokens'] for r in rows}
    out = args.run_dir / 'analysis'
    out.mkdir(exist_ok=True)
    n_layers = acts.shape[2]

    def xy(set_name, mode, key, layer, positive=('ambiguous', 'base')):
        entries = task['sets'].get(set_name, [])
        index = [row_of[(e['uid'], mode)] for e in entries]
        y = np.array([e['label'] in positive for e in entries], dtype=int)
        return acts[index, KEYS.index(key), layer], y, entries

    table, directions = [], {}
    summary = {'aen': {}, 'transfer': {}, 'lexical_control': {}, 'length_baseline': {}, 'counts': task['info']['counts']}
    for mode in cfg['modes']:
        for protocol in ('faithful', 'grouped'):
            for dataset in ('situatedqa', 'ambigqa'):
                train, test = f'{protocol}/{dataset}/train', f'{protocol}/{dataset}/test'
                if not task['sets'].get(train) or not task['sets'].get(test):
                    continue
                _, yte, te_entries = xy(test, mode, 'pre', 0)
                lengths = np.array([user_tokens[e['uid']] for e in te_entries], dtype=float)
                summary['length_baseline'][f'{mode}/{protocol}/{dataset}'] = float(roc_auc_score(yte, -lengths))
                for key in KEYS:
                    for layer in range(n_layers):
                        xtr, ytr, _ = xy(train, mode, key, layer)
                        xte, yte, _ = xy(test, mode, key, layer)
                        clf = amb.fit_probe(xtr, ytr)
                        tag = f'{mode}/{protocol}/{dataset}/{key}/L{layer + 1}'
                        table.append({'mode': mode, 'protocol': protocol, 'dataset': dataset, 'key': key,
                                      'layer': layer + 1, 'n_train': len(ytr), 'n_test': len(yte),
                                      **amb.evaluate(clf, xte, yte)})
                        directions[tag + '/dom'] = (xtr[ytr == 1].mean(0) - xtr[ytr == 0].mean(0)).astype(np.float32)
                        directions[tag + '/coef'] = clf.coef_[0].astype(np.float32)
                        directions[tag + '/intercept'] = np.array([clf.intercept_[0]], dtype=np.float32)
                        other = 'ambigqa' if dataset == 'situatedqa' else 'situatedqa'
                        if task['sets'].get(f'{protocol}/{other}/test'):
                            xo, yo, _ = xy(f'{protocol}/{other}/test', mode, key, layer)
                            summary['transfer'].setdefault(f'{mode}/{protocol}/{key}/{dataset}->{other}', []).append(
                                {'layer': layer + 1, **amb.evaluate(clf, xo, yo)})
                        if protocol == 'grouped' and task['sets'].get('grouped/lexical_control/test'):
                            xc, yc, _ = xy('grouped/lexical_control/test', mode, key, layer)
                            score = clf.decision_function(xc)
                            summary['lexical_control'].setdefault(f'{mode}/{key}/{dataset}', []).append(
                                {'layer': layer + 1, 'auc_base_vs_phrased': float(roc_auc_score(yc, score)),
                                 'predicted_ambiguous_base': float((score[yc == 1] > 0).mean()),
                                 'predicted_ambiguous_phrased': float((score[yc == 0] > 0).mean())})
                # AEN analysis: the original's representation (mean over the prompt) at its default layer.
                layer = p['aen_layer'] - 1
                xtr, ytr, _ = xy(train, mode, 'input_mean', layer)
                xte, yte, _ = xy(test, mode, 'input_mean', layer)
                clf = amb.fit_probe(xtr, ytr)
                ranking = np.argsort(np.abs(clf.coef_[0]))[::-1]
                curve = amb.noise_curve(clf, xte, yte, ranking.tolist(), p['max_k'], p['seed'])
                k = amb.pick_aen_k(curve)
                dims = ranking[:k].tolist()
                sparse = amb.fit_probe(xtr[:, dims], ytr)
                summary['aen'][f'{mode}/{protocol}/{dataset}'] = {
                    'layer': p['aen_layer'], 'full_probe': amb.evaluate(clf, xte, yte), 'noise_curve': curve,
                    'aen_k': k, 'aen_dims': dims, 'top50_dims': ranking[:50].tolist(),
                    'aen_probe': amb.evaluate(sparse, xte[:, dims], yte)}
                # Portable AEN bundle: everything needed to score new activations taken the same way.
                aen = f'aen/{mode}/{protocol}/{dataset}/input_mean/L{p["aen_layer"]}'
                directions[aen + '/dims'] = np.array(dims, dtype=np.int64)
                directions[aen + '/coef'] = sparse.coef_[0].astype(np.float32)
                directions[aen + '/intercept'] = np.array([sparse.intercept_[0]], dtype=np.float32)
                directions[aen + '/train_mean'] = xtr[:, dims].mean(0).astype(np.float32)
                directions[aen + '/train_std'] = xtr[:, dims].std(0).astype(np.float32)
                directions[aen + '/top50_dims'] = ranking[:50].astype(np.int64)
    with open(out / 'probe_metrics.csv', 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    save_file(directions, str(out / 'directions.safetensors'),
              metadata={'sign': 'ambiguous minus clear (dom); coef/intercept = sklearn probe (score > 0 = ambiguous)',
                        'layers': 'L = 1-based block output',
                        'representation': 'pre = last prompt token; input_mean = mean over all prompt tokens '
                                          '(chat template, system "You are a helpful assistant.", no padding); '
                                          'user_mean = mean over the user-message tokens',
                        'model': f"{cfg['model']['id']}@{cfg['model']['revision']}",
                        'apply': 'info_seeking.ambiguity.score_with_bundle'})
    best = {}
    for r in table:
        key = f'{r["mode"]}/{r["protocol"]}/{r["dataset"]}/{r["key"]}'
        if key not in best or r['acc'] > best[key]['acc']:
            best[key] = {k: r[k] for k in ('layer', 'acc', 'auc', 'macro_f1')}
    summary['best_layer'] = best
    summary['default_layer'] = {f'{r["mode"]}/{r["protocol"]}/{r["dataset"]}/{r["key"]}': {k: r[k] for k in ('acc', 'auc', 'macro_f1')}
                                for r in table if r['layer'] == p['aen_layer']}
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary[k] for k in ('default_layer', 'length_baseline')}, indent=1))
    print(json.dumps({k: {kk: v[kk] for kk in ('aen_k', 'aen_dims', 'full_probe', 'aen_probe')} for k, v in summary['aen'].items()}, indent=1))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='stage', required=True)
    p = sub.add_parser('init')
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--purpose', choices=('smoke', 'full'), required=True)
    p.add_argument('--prompt-limit', type=int, default=None)
    for name in ('forward', 'probe'):
        p = sub.add_parser(name)
        p.add_argument('--run-dir', type=Path, required=True)
        if name == 'forward':
            p.add_argument('--shard', default='0/1')
    args = parser.parse_args()
    if getattr(args, 'config', None) is not None:
        args.config = args.config.resolve()
    {'init': stage_init, 'forward': stage_forward, 'probe': stage_probe}[args.stage](args)


if __name__ == '__main__':
    main()
