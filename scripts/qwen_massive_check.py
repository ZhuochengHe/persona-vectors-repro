"""Check Qwen3.5-9B for first-token / massive activations and their link to length in mean-pooled features.

1. Tokenizer: is a BOS added, and what are the first tokens of the rendered prompt.
2. Per-position block outputs (all layers) for a sample of prompts: dimensions whose absolute value is extreme,
   where they occur (position), and the values of named dimensions (default 2560, 3011) by position.
3. From the saved forward chunks of an ambiguity run: correlation of mean-pooled feature dims with 1/length,
   and the probe's length dependence with and without the extreme dims removed.

Usage (inside an allocation): python scripts/qwen_massive_check.py --run-dir <ambiguity run> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def main():
    import numpy as np
    import torch
    from info_seeking.agent import QwenAgentRuntime
    from info_seeking.ambiguity import SYSTEM_MESSAGE
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--dims', type=int, nargs='*', default=[2560, 3011])
    parser.add_argument('--n-prompts', type=int, default=64)
    parser.add_argument('--layer', type=int, default=14, help='1-based block for the probe analysis')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    task = json.loads((args.run_dir / 'tasks' / 'tasks.json').read_text())
    m = cfg['model']
    rt = QwenAgentRuntime(m['id'], m['revision'], m['layers'], m['hidden'], m['attn_implementation'],
                          require_fast_kernels=m.get('require_fast_kernels', False)).load()
    tok = rt.tokenizer
    report = {'bos_token': tok.bos_token, 'bos_token_id': tok.bos_token_id,
              'add_bos_token': getattr(tok, 'add_bos_token', None)}
    sample_text = task['prompts'][0]['text']
    first = rt.initial_prompt(SYSTEM_MESSAGE, sample_text, None, enable_thinking=False)
    report['first_tokens'] = tok.convert_ids_to_tokens(first['ids'][:12])
    report['plain_encode_first_tokens'] = tok.convert_ids_to_tokens(tok(sample_text)['input_ids'][:6])

    # 2. Per-position activations for a sample of prompts.
    rng = np.random.default_rng(0)
    picks = rng.choice(len(task['prompts']), size=min(args.n_prompts, len(task['prompts'])), replace=False)
    n_layers = len(rt.layers)
    max_abs = torch.zeros(n_layers, m['hidden'])          # max |value| over all positions of all sampled prompts
    max_abs_pos0 = torch.zeros(n_layers, m['hidden'])     # max |value| at position 0
    max_abs_rest = torch.zeros(n_layers, m['hidden'])     # max |value| at positions >= 1
    named = {}
    captured = {}

    def keep_output(layer_index):
        def hook(_module, _inputs, output):
            hidden = output[0] if isinstance(output, (tuple, list)) else output
            captured[layer_index] = hidden[0].float().cpu()  # [positions, hidden] of the single prompt
        return hook
    for n, i in enumerate(picks):
        ids = rt.initial_prompt(SYSTEM_MESSAGE, task['prompts'][int(i)]['text'], None, enable_thinking=False)['ids']
        captured.clear()
        hooks = [blk.register_forward_hook(keep_output(L)) for L, blk in enumerate(rt.layers)]
        try:
            with torch.inference_mode():
                rt.model(input_ids=torch.tensor([ids], device=rt.model.device), use_cache=False, logits_to_keep=1)
        finally:
            for h in hooks:
                h.remove()
        for L in range(n_layers):
            h = captured[L].abs()
            max_abs[L] = torch.maximum(max_abs[L], h.max(0).values)
            max_abs_pos0[L] = torch.maximum(max_abs_pos0[L], h[0])
            if h.shape[0] > 1:
                max_abs_rest[L] = torch.maximum(max_abs_rest[L], h[1:].max(0).values)
        if n == 0:
            L = args.layer - 1
            named = {'tokens': tok.convert_ids_to_tokens(ids),
                     'values_by_position': {str(d): [round(float(v), 3) for v in captured[L][:, d]] for d in args.dims}}
    L = args.layer - 1
    med = float(max_abs[L].median())
    top = torch.argsort(max_abs[L], descending=True)[:15].tolist()
    report['layer'] = args.layer
    report['median_max_abs_over_dims'] = med
    report['top_dims_by_max_abs'] = [{'dim': d, 'max_abs': round(float(max_abs[L, d]), 2),
                                      'max_abs_pos0': round(float(max_abs_pos0[L, d]), 2),
                                      'max_abs_other_positions': round(float(max_abs_rest[L, d]), 2)} for d in top]
    report['named_dims'] = {str(d): {'max_abs': round(float(max_abs[L, d]), 2), 'max_abs_pos0': round(float(max_abs_pos0[L, d]), 2),
                                     'max_abs_other_positions': round(float(max_abs_rest[L, d]), 2),
                                     'rank_by_max_abs': int((max_abs[L] > max_abs[L, d]).sum()) + 1} for d in args.dims}
    report['first_prompt_named_dims'] = named
    report['top_dims_by_max_abs_all_layers'] = {str(l + 1): torch.argsort(max_abs[l], descending=True)[:5].tolist() for l in range(n_layers)}
    massive = [d['dim'] for d in report['top_dims_by_max_abs'] if d['max_abs'] > 20 * med]
    report['massive_dims_layer'] = massive

    # 3. Mean-pooled features from the saved run: link to length, and probe length dependence with/without massive dims.
    from info_seeking.runs import read_chunks
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    rows, tensors = read_chunks(args.run_dir / 'forward')
    keys = ('pre', 'input_mean', 'user_mean')  # position order of the saved forward chunks
    acts = tensors['acts']
    row_of = {(r['uid'], r['mode']): i for i, r in enumerate(rows)}
    plen = {(r['uid'], r['mode']): r['prompt_len'] for r in rows}
    out3 = {}
    for mode in cfg['modes']:
        mode_rows = [i for i, r in enumerate(rows) if r['mode'] == mode]
        x = acts[mode_rows, keys.index('input_mean'), L].float().numpy()
        inv = 1.0 / np.array([rows[i]['prompt_len'] for i in mode_rows], dtype=float)
        corr = {str(d): float(np.corrcoef(x[:, d], inv)[0, 1]) for d in sorted(set(args.dims + massive + top[:5]))}
        entry = {'corr_input_mean_dim_vs_inv_prompt_len': corr}
        for protocol in ('faithful', 'grouped'):
            for dataset in ('ambigqa', 'situatedqa'):
                tr = task['sets'].get(f'{protocol}/{dataset}/train'); te = task['sets'].get(f'{protocol}/{dataset}/test')
                if not tr or not te:
                    continue
                def xy(entries):
                    idx = [row_of[(e['uid'], mode)] for e in entries]
                    return (acts[idx, keys.index('input_mean'), L].float().numpy(),
                            np.array([e['label'] == 'ambiguous' for e in entries], dtype=int),
                            np.array([plen[(e['uid'], mode)] for e in entries], dtype=float))
                xtr, ytr, _ = xy(tr); xte, yte, lte = xy(te)
                res = {}
                for name, drop in (('all_dims', []), ('without_massive', massive)):
                    keep = [d for d in range(xtr.shape[1]) if d not in set(drop)]
                    clf = LogisticRegression(max_iter=1000).fit(xtr[:, keep], ytr)
                    s = clf.decision_function(xte[:, keep])
                    res[name] = {'acc': float((clf.predict(xte[:, keep]) == yte).mean()), 'auc': float(roc_auc_score(yte, s)),
                                 'corr_score_vs_prompt_len': float(np.corrcoef(s, lte)[0, 1])}
                entry[f'{protocol}/{dataset}'] = res
        out3[mode] = entry
    report['mean_pooled_length_link'] = out3
    (args.out / 'qwen_massive_check.json').write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps({k: report[k] for k in ('bos_token', 'add_bos_token', 'first_tokens', 'median_max_abs_over_dims',
                                             'top_dims_by_max_abs', 'named_dims', 'massive_dims_layer', 'mean_pooled_length_link')},
                     indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
