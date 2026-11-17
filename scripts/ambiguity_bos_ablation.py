"""BOS / padding ablation of the Sparse Neurons probe on the original model (LLaMA 3.1 8B Instruct).

Same prompts, split and batching as scripts/ambiguity_faithful.py (the original pipeline), but one forward pass
yields four poolings of hidden_states[14]:
  orig        mean over all positions incl. the two BOS tokens and right padding (the original feature)
  real_nobos  mean over real tokens excluding BOS positions (no padding)
  user        mean over the user-question tokens only
  last        last real token
Analyses per pooling:
  A. the probe trained on `orig`, applied unchanged to this pooling (does the original probe depend on BOS?)
  B. a probe retrained on this pooling (accuracy, AUC, correlation of the score with length)
  C. neuron selection redone: |coef| ranking, noise curve, our automatic rule, the paper's rule
     (top-5 shared across AmbigQA and SituatedQA), AEN-only probe; per-position magnitude of the selected dims
  D. length controls: length-matched AUC (within equal real-token-count strata) and the lexical control
     (context-independent questions with and without an appended phrase, both clear; batched per class)

Usage (inside an allocation): python scripts/ambiguity_bos_ablation.py --run-dir <ambiguity run> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiguity_faithful import (FILES, HF_IDS, PAPER, SUPER_NEURONS, format_prompt, noise_curve,  # noqa: E402
                                original_lists, pick_aen_k)

POOLINGS = ('orig', 'real_nobos', 'user', 'last')
USER_MARKER = {'llama': '<|start_header_id|>user<|end_header_id|>', 'mistral': '[INST]'}
USER_END = {'llama': '<|eot_id|><|start_header_id|>assistant', 'mistral': '[/INST]'}


def user_char_span(prompt: str, model: str):
    start = prompt.index(USER_MARKER[model]) + len(USER_MARKER[model])
    return start, prompt.rindex(USER_END[model])


def pooled(model, tokenizer, prompts, name: str, layer: int = 14, batch_size: int = 20):
    """Original batching; returns {pooling: [N, H]}, real token counts, and BOS-position values of the batch."""
    import numpy as np
    import torch
    out = {p: [] for p in POOLINGS}
    real = []
    bos_id = tokenizer.bos_token_id
    with torch.no_grad():
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, return_tensors='pt', return_offsets_mapping=True)
            offsets = enc.pop('offset_mapping')
            enc = enc.to(model.device)
            h = model(**enc, output_hidden_states=True).hidden_states[layer].float()
            for j, prompt in enumerate(batch):
                mask = enc['attention_mask'][j].bool()
                ids = enc['input_ids'][j]
                hj = h[j]
                out['orig'].append(hj.mean(0).cpu().numpy())                       # original: all positions
                keep = mask & (ids != bos_id)
                out['real_nobos'].append(hj[keep].mean(0).cpu().numpy())
                a, b = user_char_span(prompt, name)
                off = offsets[j]
                user = mask.cpu() & (off[:, 0] >= a) & (off[:, 1] <= b) & (off[:, 1] > off[:, 0])
                out['user'].append(hj[user.to(hj.device)].mean(0).cpu().numpy())
                last = int(mask.nonzero().max())
                out['last'].append(hj[last].cpu().numpy())
                real.append(int(mask.sum()))
    return {p: np.vstack(v) for p, v in out.items()}, np.array(real)


def length_matched_auc(score, y, length):
    """Weighted mean of AUCs within strata of equal length that contain both classes."""
    import numpy as np
    from sklearn.metrics import roc_auc_score
    total, weight = 0.0, 0
    for L in np.unique(length):
        m = length == L
        if len(set(y[m])) == 2:
            total += roc_auc_score(y[m], score[m]) * m.sum()
            weight += m.sum()
    return (total / weight if weight else float('nan')), int(weight)


def split(feats: dict, pooling: str):
    """Original train/test lists -> (x_train, y_train, x_test, y_test, real-token counts of test). Clear = 1."""
    import numpy as np

    def xy(prefix):
        a, c = feats[f'{prefix}_ambig'], feats[f'{prefix}_clean']
        return (np.vstack([a[0][pooling], c[0][pooling]]),
                np.hstack([np.zeros(len(a[1])), np.ones(len(c[1]))]), np.hstack([a[1], c[1]]))
    xtr, ytr, _ = xy('train')
    xte, yte, lte = xy('test')
    return xtr, ytr, xte, yte, lte


def analyse(feats: dict, n_clean: int, ctl: dict, pooling: str, fixed_probe, super_neurons: list[int]):
    """Sections A-D of the module docstring for one dataset and one pooling. Returns (entry, |coef| ranking)."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, roc_auc_score
    xtr, ytr, xte, yte, lte = split(feats, pooling)
    clf = LogisticRegression(max_iter=1000).fit(xtr, ytr)
    score = clf.decision_function(xte)
    top = np.argsort(np.abs(clf.coef_[0]))[::-1]
    curve = noise_curve(clf, xte, yte, top[:50].tolist(), n_clean, max_k=51)
    auto_k = pick_aen_k(curve)
    auto = top[:auto_k].tolist()
    sparse = LogisticRegression(max_iter=1000).fit(xtr[:, auto], ytr)
    lm_auc, lm_n = length_matched_auc(score, yte, lte)
    xc = np.vstack([ctl['base'][0][pooling], ctl['phrased'][0][pooling]])
    is_base = np.hstack([np.ones(len(ctl['base'][1]), bool), np.zeros(len(ctl['phrased'][1]), bool)])
    sc = clf.decision_function(xc)  # > 0 = clear
    entry = {
        'A_fixed_orig_probe_acc': float(accuracy_score(yte, fixed_probe.predict(xte))),
        'B_retrained_acc': float(accuracy_score(yte, clf.predict(xte))),
        'B_retrained_auc': float(roc_auc_score(yte, score)),
        'B_corr_score_vs_real_tokens': float(np.corrcoef(score, lte)[0, 1]),
        'C_top10_dims': top[:10].tolist(),
        'C_feature_abs_mean_top5': [round(float(np.abs(xtr[:, d]).mean()), 3) for d in top[:5]],
        'C_feature_abs_mean_median_all': float(np.median(np.abs(xtr).mean(0))),
        'C_noise_curve_k0_10': [round(c['acc'], 3) for c in curve[:11]],
        'C_auto_aen': {'k': auto_k, 'dims': auto, 'acc': float(accuracy_score(yte, sparse.predict(xte[:, auto])))},
        'C_paper_super_neurons_rank': {d: int(top.tolist().index(d) + 1) for d in super_neurons},
        'D_length_matched_auc': lm_auc, 'D_length_matched_n': lm_n,
        'D_length_only_auc': float(roc_auc_score(yte, lte)),
        'D_lexical_control_auc_phrased_vs_base': float(roc_auc_score(~is_base, sc)),
        'D_lexical_control_pred_ambiguous_base': float((sc[is_base] < 0).mean()),
        'D_lexical_control_pred_ambiguous_phrased': float((sc[~is_base] < 0).mean())}
    return entry, top


def paper_rule(data: dict, pooling: str, tops: dict) -> dict:
    """The paper's selection: dims in the top 5 of both datasets, and a probe on them."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    shared = sorted(set(tops['ambigqa'][:5].tolist()) & set(tops['situatedqa'][:5].tolist()))
    out = {'shared_top5': shared}
    for dataset, d in data.items():
        if shared:
            xtr, ytr, xte, yte, _ = split(d['feats'], pooling)
            clf = LogisticRegression(max_iter=1000).fit(xtr[:, shared], ytr)
            out[f'{dataset}_probe_on_shared_acc'] = float(accuracy_score(yte, clf.predict(xte[:, shared])))
    return out


def main():
    import torch
    from sklearn.linear_model import LogisticRegression
    from transformers import AutoModelForCausalLM, AutoTokenizer
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='llama', choices=sorted(HF_IDS))
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    task = json.loads((args.run_dir / 'tasks' / 'tasks.json').read_text())
    root = Path(cfg['data']['root'])
    tokenizer = AutoTokenizer.from_pretrained(HF_IDS[args.model])
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(HF_IDS[args.model], device_map='auto', torch_dtype=torch.float16).eval()

    def features(prompts):
        return pooled(model, tokenizer, [format_prompt(p, args.model) for p in prompts], args.model)
    text = {p['uid']: p['text'] for p in task['prompts']}
    control = task['sets']['grouped/lexical_control/test']
    ctl = {label: features([text[e['uid']] for e in control if e['label'] == label]) for label in ('base', 'phrased')}
    data = {dataset: {'feats': {k: features(v) for k, v in original_lists(root, dataset).items()},
                      'n_clean': len(json.loads((root / FILES[dataset][1]).read_text()))}
            for dataset in ('ambigqa', 'situatedqa')}

    report = {'model': HF_IDS[args.model], 'paper': PAPER[args.model], 'poolings': list(POOLINGS)}
    fixed = {d: LogisticRegression(max_iter=1000).fit(*split(v['feats'], 'orig')[:2]) for d, v in data.items()}
    for pooling in POOLINGS:
        entry, tops = {}, {}
        for dataset, d in data.items():
            entry[dataset], tops[dataset] = analyse(d['feats'], d['n_clean'], ctl, pooling, fixed[dataset],
                                                    SUPER_NEURONS[args.model])
        entry['C_paper_rule'] = paper_rule(data, pooling, tops)
        report[pooling] = entry
        print(json.dumps({pooling: entry}), flush=True)
    (args.out / f'bos_ablation_{args.model}.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
