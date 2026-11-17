"""Faithfulness check for the Sparse Neurons reproduction: the original models and pipeline.

Reimplements Internal_State_Detect_Ambiguity (commit 63a29bad) single_layer_classifier.py exactly:
  - format_prompt strings as written in the original (including indentation inside the f-strings and the
    literal BOS that the tokenizer duplicates);
  - legacy numpy shuffles with seeds 11/12/13/14 on the exported pair files, train = first 400,
    test = last 1000;
  - batches of 20, tokenizer(batch, padding=True) with pad = eos, fp16 weights,
    output_hidden_states=True, hidden_states[14], mean over ALL positions including padding;
  - sklearn LogisticRegression(max_iter=1000), labels ambiguous = 0 / clear = 1;
  - top dims by |coef|; probe on the original's hard-coded super neurons and on our own top-k;
    remove_first_n_dims noise test (replace with N(mean, std) of the test column; RNG continues after the
    seed-14 shuffle, k = 0..9 as in the original, extended to 50 for our automatic AEN rule).
Also scores our lexical control (context-independent questions with and without an appended context
phrase, both clear): base and phrased lists batched separately (batch 20, as the original batches each class)
and without padding (batch 1), plus length correlations and a massive-activation check of the super neurons.

Usage (inside an allocation): python scripts/ambiguity_faithful.py --model llama --run-dir <ambiguity run> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from info_seeking.ambiguity import pick_aen_k  # noqa: E402

HF_IDS = {'llama': 'meta-llama/Llama-3.1-8B-Instruct', 'mistral': 'mistralai/Mistral-7B-Instruct-v0.3'}
SUPER_NEURONS = {'llama': [788, 4062, 1384], 'mistral': [2070]}
PAPER = {'llama': {'ambigqa': 90.65, 'situatedqa': 95.40, 'aen_ambigqa': 88.60, 'aen_situatedqa': 94.00,
                   'top5_ambigqa': [788, 1384, 4062, 4055, 1298], 'top5_situatedqa': [788, 1384, 4062, 4055, 3231]},
         'mistral': {'ambigqa': 93.30, 'situatedqa': 94.14, 'aen_ambigqa': 90.30, 'aen_situatedqa': 92.35,
                     'top5_ambigqa': [2070, 3240, 2043, 1909, 1372], 'top5_situatedqa': [2070, 2388, 2078, 53, 2083]}}
FILES = {'ambigqa': ('original/ambig_qa_ambig_questions.json', 'original/ambig_qa_clean_questions.json'),
         'situatedqa': ('original/situated_ambi_combined_question.json', 'original/situated_clean_combined_question.json')}


def format_prompt(user_input: str, model: str, system_message: str = 'You are a helpful assistant.') -> str:
    """Verbatim behaviour of the original format_prompt (indentation is part of the strings)."""
    if model == 'llama':
        formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

        Cutting Knowledge Date: December 2023
        Today Date: 23 July 2024

        {system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

        {user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
    elif model == 'mistral':
        formatted_prompt = f"""<s>[INST] {system_message}
            {user_input}[/INST]"""
    else:
        raise ValueError(model)
    return formatted_prompt.strip()


def original_lists(root: Path, dataset: str):
    import numpy as np
    ambig = json.loads((root / FILES[dataset][0]).read_text())
    clean = json.loads((root / FILES[dataset][1]).read_text())
    out = {}
    for name, source, seed in (('train_ambig', ambig, 11), ('train_clean', clean, 12),
                               ('test_ambig', ambig, 13), ('test_clean', clean, 14)):
        prompts = [e['prompt'] for e in source]  # the original shuffles the formatted prompt list
        np.random.seed(seed)
        np.random.shuffle(prompts)
        out[name] = prompts[:400] if name.startswith('train') else prompts[-1000:]
    return out


def hiddens(model, tokenizer, prompts, layer: int = 14, batch_size: int = 20, probe_dims=None):
    """Original extraction. Returns (states [N, H] float32, real token counts, padded batch lengths,
    per-position values of probe_dims for the first batch or None)."""
    import numpy as np
    import torch
    states, real, padded, first_batch = [], [], [], None
    with torch.no_grad():
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, return_tensors='pt').to(model.device)
            out = model(**enc, output_hidden_states=True)
            h_layer = out.hidden_states[layer]
            for j, h in enumerate(h_layer):
                states.append(torch.mean(h, dim=0).float().cpu().numpy())  # includes padded positions
                real.append(int(enc['attention_mask'][j].sum()))
                padded.append(int(enc['attention_mask'].shape[1]))
            if first_batch is None and probe_dims is not None:
                first_batch = {'positions_values': h_layer[0][:, probe_dims].float().cpu().numpy().tolist(),
                               'tokens': tokenizer.convert_ids_to_tokens(enc['input_ids'][0]),
                               'abs_mean_all_dims_by_position': h_layer[0].abs().float().mean(-1).cpu().numpy().tolist()}
            del out
    return np.vstack(states), np.array(real), np.array(padded), first_batch


def replay_rng(n_clean: int):
    """The original never reseeds before the noise test: its draws continue after the seed-14 shuffle of
    the clean list (sklearn lbfgs does not consume numpy's global state)."""
    import numpy as np
    np.random.seed(14)
    np.random.shuffle(list(range(n_clean)))


def noise_curve(clf, x, y, dims, n_clean: int, max_k: int = 10) -> list[dict]:
    """remove_first_n_dims(step=1) over k = 0..max_k-1, replacing dims with N(column mean, column std).
    Uses numpy's global RNG in the original's state (see replay_rng)."""
    import numpy as np
    from sklearn.metrics import accuracy_score
    replay_rng(n_clean)
    out = []
    for i in range(0, max_k):
        noisy = x.copy()
        for d in dims[:i]:
            noisy[:, d] = np.random.normal(loc=np.mean(x[:, d]), scale=np.std(x[:, d]), size=x.shape[0])
        out.append({'k': i, 'acc': float(accuracy_score(y, clf.predict(noisy)))})
    return out


def main():
    import importlib.metadata as md
    import numpy as np
    import torch
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
    from transformers import AutoModelForCausalLM, AutoTokenizer
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=sorted(HF_IDS), required=True)
    parser.add_argument('--run-dir', type=Path, required=True, help='ambiguity run (for the data root and control set)')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((args.run_dir / 'config.json').read_text())
    task = json.loads((args.run_dir / 'tasks' / 'tasks.json').read_text())
    root = Path(cfg['data']['root'])
    tokenizer = AutoTokenizer.from_pretrained(HF_IDS[args.model])
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(HF_IDS[args.model], device_map='auto', torch_dtype=torch.float16).eval()
    sup = SUPER_NEURONS[args.model]
    example = format_prompt('who won the world cup', args.model)
    versions = {}
    for name in ('torch', 'transformers', 'tokenizers', 'scikit-learn', 'scipy', 'numpy'):
        try:
            versions[name] = md.version(name)
        except md.PackageNotFoundError:
            versions[name] = None
    report = {'model': HF_IDS[args.model], 'model_revision': getattr(model.config, '_commit_hash', None),
              'versions': versions, 'padding_side': tokenizer.padding_side, 'pad_token_id': tokenizer.pad_token_id,
              'paper': PAPER[args.model], 'example_prompt': example,
              'example_input_ids': tokenizer(example)['input_ids'],
              'example_tokens': tokenizer.convert_ids_to_tokens(tokenizer(example)['input_ids'])}
    text = {p['uid']: p['text'] for p in task['prompts']}
    control = task['sets']['grouped/lexical_control/test']
    # Control: base (no phrase) and phrased lists batched separately, as the original batches each class.
    ctl = {}
    for label in ('base', 'phrased'):
        prompts = [format_prompt(text[e['uid']], args.model) for e in control if e['label'] == label]
        ctl[label] = {'b20': hiddens(model, tokenizer, prompts)[:3], 'b1': hiddens(model, tokenizer, prompts, batch_size=1)[:3]}
    for dataset in ('ambigqa', 'situatedqa'):
        lists = original_lists(root, dataset)
        n_clean = len(json.loads((root / FILES[dataset][1]).read_text()))
        x, real, padded = {}, {}, {}
        first_batch = None
        for k, v in lists.items():
            states, r, pdd, fb = hiddens(model, tokenizer, [format_prompt(p, args.model) for p in v], probe_dims=sup)
            x[k], real[k], padded[k] = states, r, pdd
            first_batch = first_batch or fb
        xtr = np.vstack([x['train_ambig'], x['train_clean']])
        ytr = np.hstack([np.zeros(len(x['train_ambig'])), np.ones(len(x['train_clean']))])
        xte = np.vstack([x['test_ambig'], x['test_clean']])
        yte = np.hstack([np.zeros(len(x['test_ambig'])), np.ones(len(x['test_clean']))])
        pad_tr = np.hstack([padded['train_ambig'], padded['train_clean']])
        real_te = np.hstack([real['test_ambig'], real['test_clean']])
        pad_te = np.hstack([padded['test_ambig'], padded['test_clean']])
        clf = LogisticRegression(max_iter=1000).fit(xtr, ytr)
        pred = clf.predict(xte)
        score = clf.decision_function(xte)
        top = np.argsort(np.abs(clf.coef_[0]))[::-1]
        clf_sup = LogisticRegression(max_iter=1000).fit(xtr[:, sup], ytr)
        curve50 = noise_curve(clf, xte, yte, top[:50].tolist(), n_clean, max_k=51)
        auto_k = pick_aen_k(curve50)
        auto = top[:auto_k].tolist()
        clf_auto = LogisticRegression(max_iter=1000).fit(xtr[:, auto], ytr)
        control_report = {}
        for mode in ('b20', 'b1'):
            xb, rb, pb = ctl['base'][mode]
            xp, rp, pp = ctl['phrased'][mode]
            xc = np.vstack([xb, xp])
            is_base = np.hstack([np.ones(len(xb), bool), np.zeros(len(xp), bool)])
            sc = clf.decision_function(xc)  # > 0 = clear
            control_report[mode] = {
                'auc_phrased_vs_base_by_clear_score': float(roc_auc_score(~is_base, sc)),
                'predicted_ambiguous_base': float((sc[is_base] < 0).mean()),
                'predicted_ambiguous_phrased': float((sc[~is_base] < 0).mean()),
                'super_neuron_auc': float(roc_auc_score(~is_base, clf_sup.decision_function(xc[:, sup]))),
                'mean_real_tokens': {'base': float(rb.mean()), 'phrased': float(rp.mean())},
                'mean_padded_tokens': {'base': float(pb.mean()), 'phrased': float(pp.mean())}}
        corr = {f'dim{d}_vs_inv_padded_len_train': float(np.corrcoef(xtr[:, d], 1.0 / pad_tr)[0, 1]) for d in sup}
        report[dataset] = {
            'full_probe_acc': float(accuracy_score(yte, pred)) * 100,
            'full_probe_macro_f1': float(f1_score(yte, pred, average='macro')) * 100,
            'n_iter': int(clf.n_iter_[0]),
            'top10_dims': top[:10].tolist(),
            'super_neuron_probe_acc': float(accuracy_score(yte, clf_sup.predict(xte[:, sup]))) * 100,
            'noise_curve_top10_original_range': curve50[:10],
            'noise_curve_top50': curve50,
            'auto_aen': {'k': auto_k, 'dims': auto, 'probe_acc': float(accuracy_score(yte, clf_auto.predict(xte[:, auto]))) * 100,
                         'overlap_with_paper_aen': sorted(set(auto) & set(sup)),
                         'paper_aen_ranks_in_top': {d: int(top.tolist().index(d) + 1) for d in sup}},
            'length': {'auc_real_tokens_clear_vs_ambiguous': float(roc_auc_score(yte, real_te)),
                       'auc_padded_len_clear_vs_ambiguous': float(roc_auc_score(yte, pad_te)),
                       'corr_probe_score_vs_real_tokens': float(np.corrcoef(score, real_te)[0, 1]),
                       'corr_probe_score_vs_padded_len': float(np.corrcoef(score, pad_te)[0, 1]),
                       **corr},
            'massive_activation_check': {
                'super_dims': sup, 'first_batch_tokens': first_batch['tokens'],
                'super_dims_by_position': first_batch['positions_values'],
                'abs_mean_all_dims_by_position': first_batch['abs_mean_all_dims_by_position'],
                'feature_abs_mean_super_dims': {d: float(np.abs(xtr[:, d]).mean()) for d in sup},
                'feature_abs_mean_all_dims_median': float(np.median(np.abs(xtr).mean(0))),
                'feature_abs_mean_all_dims_p99': float(np.percentile(np.abs(xtr).mean(0), 99))},
            'lexical_control': control_report}
        np.savez_compressed(args.out / f'hidden_L14_{args.model}_{dataset}.npz', xtr=xtr, ytr=ytr, xte=xte, yte=yte,
                            pad_tr=pad_tr, real_te=real_te, pad_te=pad_te)
        print(json.dumps({dataset: {k: report[dataset][k] for k in ('full_probe_acc', 'top10_dims', 'super_neuron_probe_acc',
                                                                    'auto_aen', 'length', 'lexical_control')}}), flush=True)
    (args.out / f'faithful_{args.model}.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
