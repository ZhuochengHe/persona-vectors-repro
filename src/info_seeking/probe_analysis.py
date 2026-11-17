"""Offline readout analysis over captured decision points (no generation).

For each label set x position key x layer: out-of-fold AUC (folds grouped by task) of
  dom      projection on the train-fold difference-of-means direction
  logreg   L2 logistic probe on standardised features
  shuffled logistic probe trained on permuted train labels (chance control)
plus a step-index-only baseline AUC per label set (time confound control). Full-data
difference-of-means directions (raw and unit) are saved for later steering/transfer tests.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

POSITION_KEYS = ('pre', 'think_end', 'act_first', 'obs_mean', 'think_mean', 'input_mean')


def auc(scores, labels) -> float:
    import torch
    scores, labels = torch.as_tensor(scores, dtype=torch.float64), torch.as_tensor(labels, dtype=torch.bool)
    pos, neg = scores[labels], scores[~labels]
    if len(pos) == 0 or len(neg) == 0:
        return float('nan')
    ranks = torch.empty_like(scores)
    order = scores.argsort()
    ranks[order] = torch.arange(1, len(scores) + 1, dtype=torch.float64)
    # average ranks for ties
    uniq, inverse = torch.unique(scores, return_inverse=True)
    for u in range(len(uniq)):
        mask = inverse == u
        if mask.sum() > 1:
            ranks[mask] = ranks[mask].mean()
    return float((ranks[labels].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def load_run(run_dir: Path):
    import torch
    from safetensors.torch import load_file
    rows, acts, paired = [], [], []
    for unit in sorted((run_dir / 'units').iterdir()):
        if unit.name.endswith('.tmp') or not (unit / 'summary.json').exists() or not (unit / 'activations.safetensors').exists():
            continue
        summary = json.loads((unit / 'summary.json').read_text())
        tensors = load_file(str(unit / 'activations.safetensors'))
        decisions = [json.loads(line) for line in (unit / 'decisions.jsonl').read_text().splitlines()]
        n_blockers = summary['ask_metrics']['n_blockers'] if summary['ask_metrics'] else None
        for i, d in enumerate(decisions):
            rows.append({'unit': unit.name, 'task_id': summary['task_id'], 'condition': summary['condition'],
                         'step': d['step'], 'action': d['action'], 'ask_outcome': d.get('ask_outcome'),
                         'remaining_before': d['remaining_before'], 'n_blockers': n_blockers or d['remaining_before'],
                         'valid': tensors['valid'][i].tolist(),
                         'paired_index': len(paired) if 'paired_acts' in tensors else None})
            acts.append(tensors['acts'][i])
            if 'paired_acts' in tensors:
                paired.append(tensors['paired_acts'][i])
    return rows, (torch.stack(acts) if acts else None), (torch.stack(paired) if paired else None)


def label_sets(rows):
    """Yield (name, row indices into acts or ('paired', idx), labels)."""
    def idx(pred):
        return [i for i, r in enumerate(rows) if pred(r)]
    sets = {}
    a = idx(lambda r: r['condition'] in ('blocked_ask', 'fullinfo_ask'))
    sets['cond_ask'] = (a, [rows[i]['condition'] == 'blocked_ask' for i in a])
    a = idx(lambda r: r['condition'] == 'blocked_ask_prompted' and r['action'] != 'format_error')
    sets['ask_action_prompted'] = (a, [rows[i]['action'] == 'ask_human' for i in a])
    a = idx(lambda r: r['condition'] in ('blocked_noask', 'fullinfo_noask'))
    sets['cond_noask'] = (a, [rows[i]['condition'] == 'blocked_noask' for i in a])
    a = idx(lambda r: r['condition'] == 'blocked_ask' and r['action'] != 'format_error')
    sets['ask_action'] = (a, [rows[i]['action'] == 'ask_human' for i in a])
    a = idx(lambda r: r['condition'] == 'blocked_ask')
    sets['nothing_resolved'] = (a, [rows[i]['remaining_before'] == rows[i]['n_blockers'] for i in a])
    return sets


def logistic_scores(x_train, y_train, x_test, l2=1e-2, iters=100):
    import torch
    mean, std = x_train.mean(0), x_train.std(0).clamp(min=1e-4)
    xt, xs = (x_train - mean) / std, (x_test - mean) / std
    w = torch.zeros(xt.shape[1], device=xt.device, requires_grad=True)
    b = torch.zeros((), device=xt.device, requires_grad=True)
    opt = torch.optim.LBFGS([w, b], max_iter=iters, line_search_fn='strong_wolfe')
    y = y_train.float()

    def closure():
        opt.zero_grad()
        loss = torch.nn.functional.binary_cross_entropy_with_logits(xt @ w + b, y) + l2 * (w ** 2).sum()
        loss.backward()
        return loss
    opt.step(closure)
    return (xs @ w + b).detach()


def analyse(run_dir: Path, out_dir: Path, folds: int = 5, seed: int = 0):
    """HiL decision points: label sets from `label_sets` plus the exactly paired full-info set."""
    import torch
    rows, acts, paired = load_run(run_dir)
    if acts is None:
        raise ValueError('No finished units with activations')
    data = {}
    for name, (index, labels) in label_sets(rows).items():
        if index:
            data[name] = {'feats': acts[index], 'y': torch.tensor(labels), 'groups': [rows[i]['task_id'] for i in index],
                          'valid': torch.tensor([rows[i]['valid'] for i in index]),
                          'baseline': torch.tensor([rows[i]['step'] for i in index], dtype=torch.float32)}
    if paired is not None:
        index = [i for i, r in enumerate(rows) if r['paired_index'] is not None]
        if index:  # blocked (1) vs the same decision point with the full-info instance text (0)
            data['paired_fullinfo'] = {
                'feats': torch.cat([acts[index], paired[[rows[i]['paired_index'] for i in index]]]),
                'y': torch.tensor([True] * len(index) + [False] * len(index)),
                'groups': [rows[i]['task_id'] for i in index] * 2,
                'valid': torch.cat([torch.tensor([rows[i]['valid'] for i in index])] * 2),
                'baseline': torch.tensor([rows[i]['step'] for i in index] * 2, dtype=torch.float32)}
    readout(data, POSITION_KEYS, out_dir, folds=folds, seed=seed, baseline_name='step_baseline_auc')


def readout(data: dict, keys, out_dir: Path, folds: int = 5, seed: int = 0, baseline_name: str = 'baseline_auc'):
    """data: name -> {feats [N, K, L, H], y [N] bool, groups [N] (fold grouping), valid [N, K],
    baseline [N] or None (a scalar confound whose AUC is reported)}. Writes CSV, directions,
    cosines and a best-layer summary to out_dir."""
    import torch
    from safetensors.torch import save_file
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    out_dir.mkdir(parents=True, exist_ok=True)
    gen = torch.Generator().manual_seed(seed)
    results, directions = [], {}
    for name, d in data.items():
        feats, y, groups, valid = d['feats'], d['y'], d['groups'], d['valid']
        if len(y) == 0 or y.all() or (~y).all():
            continue
        tasks = sorted(set(groups))
        perm = torch.randperm(len(tasks), generator=gen).tolist()
        fold_of_task = {tasks[p]: k % folds for k, p in enumerate(perm)}
        fold = torch.tensor([fold_of_task[g] for g in groups])
        base = {'label_set': name, 'n': len(y), 'n_pos': int(y.sum()), 'n_groups': len(tasks),
                baseline_name: auc(d['baseline'], y) if d.get('baseline') is not None else float('nan')}
        for k_index, key in enumerate(keys):
            ok = valid[:, k_index]
            if ok.sum() < 10 or y[ok].all() or (~y[ok]).all():
                continue
            x_all = feats[ok, k_index].float().to(device)
            y_ok, fold_ok = y[ok].to(device), fold[ok].to(device)
            raw_dirs = []
            for layer in range(x_all.shape[1]):
                x = x_all[:, layer]
                dom_scores = torch.full((len(y_ok),), float('nan'), device=device)
                lr_scores, sh_scores = dom_scores.clone(), dom_scores.clone()
                for f in range(folds):
                    test, train = fold_ok == f, fold_ok != f
                    if test.sum() == 0 or y_ok[train].all() or (~y_ok[train]).all():
                        continue
                    xtr, ytr = x[train], y_ok[train]
                    direction = xtr[ytr].mean(0) - xtr[~ytr].mean(0)
                    dom_scores[test] = x[test] @ direction
                    lr_scores[test] = logistic_scores(xtr, ytr, x[test])
                    shuffled = ytr[torch.randperm(len(ytr), generator=gen).to(device)]
                    sh_scores[test] = logistic_scores(xtr, shuffled, x[test])
                keep = ~torch.isnan(dom_scores)
                results.append({**base, 'key': key, 'layer': layer + 1, 'n_valid': int(ok.sum()),
                                'dom_auc': auc(dom_scores[keep].cpu(), y_ok[keep].cpu()),
                                'logreg_auc': auc(lr_scores[keep].cpu(), y_ok[keep].cpu()),
                                'shuffled_auc': auc(sh_scores[keep].cpu(), y_ok[keep].cpu())})
                raw_dirs.append((x[y_ok].mean(0) - x[~y_ok].mean(0)).cpu())
            raw = torch.stack(raw_dirs)
            directions[f'{name}.{key}.raw'] = raw.contiguous()
            directions[f'{name}.{key}.unit'] = (raw / raw.norm(dim=-1, keepdim=True).clamp(min=1e-8)).contiguous()
        print(json.dumps({'label_set': name, 'n': len(y), 'n_pos': int(y.sum())}), flush=True)
    if not results:
        raise ValueError('No label set had both classes with enough valid points')
    with open(out_dir / 'probe_auc.csv', 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    save_file(directions, str(out_dir / 'directions.safetensors'),
              metadata={'layers': '1-based block outputs; row i = layer i+1', 'sign': 'positive label minus negative'})
    cosines = {}
    names = sorted({k.rsplit('.', 2)[0] for k in directions})
    for key in keys:
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                ka, kb = f'{a}.{key}.unit', f'{b}.{key}.unit'
                if ka in directions and kb in directions:
                    cosines[f'{a}|{b}|{key}'] = (directions[ka] * directions[kb]).sum(-1).tolist()
    (out_dir / 'direction_cosines.json').write_text(json.dumps(cosines))
    summary = {}
    for name in sorted({r['label_set'] for r in results}):
        candidates = [r for r in results if r['label_set'] == name and r['logreg_auc'] == r['logreg_auc']]
        if candidates:
            best = max(candidates, key=lambda r: r['logreg_auc'])
            summary[name] = {k: best[k] for k in ('key', 'layer', 'logreg_auc', 'dom_auc', 'shuffled_auc',
                                                   baseline_name, 'n', 'n_pos', 'n_groups')}
    (out_dir / 'probe_summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
