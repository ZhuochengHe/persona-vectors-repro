"""Reproduction of the Sparse Neurons ambiguity probe (arXiv 2509.13664) on Qwen3.5-9B.

Original code: github.com/Zhuoxuan-Zhang/Internal_State_Detect_Ambiguity (commit 63a29bad, no license;
kept under PV_WORK/external, not copied here). Two protocols share one set of activations:

  faithful  the original pair files and split: each class list shuffled with numpy seeds 11-14 from
            the same file, train = first 400, test = last 1000 (train/test can share prompts and pairs);
            sklearn LogisticRegression(max_iter=1000) on raw features; layer 14 (= hidden_states[14] =
            block 14 output); noise test replaces a dimension with N(mean, std) of that test dimension.
  grouped   our fix: pairs built from the raw datasets and split by question id so a prompt and its pair
            never cross train/test; plus a lexical control (context-independent SituatedQA questions with
            and without an appended context phrase, both clear).

The original batches prompts with right padding and averages over padded positions; we run each
prompt alone, so the mean covers real tokens only (a declared deviation).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from .official import sha256

SYSTEM_MESSAGE = 'You are a helpful assistant.'  # original format_prompt default
ORIGINAL_FILES = {
    'ambigqa': ('original/ambig_qa_ambig_questions.json', 'original/ambig_qa_clean_questions.json'),
    'situatedqa': ('original/situated_ambi_combined_question.json', 'original/situated_clean_combined_question.json'),
}
SITUATEDQA_FILES = {(kind, split): f'situatedqa/qa_data/{kind}.{split}.jsonl'
                    for kind in ('geo', 'temp') for split in ('train', 'dev', 'test')}
CONTEXT_DEPENDENT_DATE_TYPES = {'sampled_year', 'sampled_date', 'start'}


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


class PromptTable:
    """Unique prompt texts with stable uids, plus named sets of (uid, label) for each protocol."""

    def __init__(self):
        self.uid_of, self.prompts, self.sets = {}, [], {}

    def add(self, set_name: str, text: str, label: str, pair_id: str):
        if text not in self.uid_of:
            self.uid_of[text] = f'p{len(self.prompts):06d}'
            self.prompts.append({'uid': self.uid_of[text], 'text': text})
        self.sets.setdefault(set_name, []).append({'uid': self.uid_of[text], 'label': label, 'pair_id': pair_id})


# ---- faithful protocol --------------------------------------------------------------------------
def faithful_sets(root: Path, table: PromptTable, n_train: int = 400, n_test: int = 1000) -> dict:
    """Mirror single_layer_classifier.py: legacy numpy shuffles with seeds 11/12/13/14 on the same files."""
    import numpy as np
    info = {}
    for dataset, (ambig_file, clean_file) in ORIGINAL_FILES.items():
        ambig = json.loads((root / ambig_file).read_text())
        clean = json.loads((root / clean_file).read_text())
        lists = {}
        for name, source, seed in (('train_ambig', ambig, 11), ('train_clean', clean, 12),
                                   ('test_ambig', ambig, 13), ('test_clean', clean, 14)):
            entries = list(source)
            np.random.seed(seed)
            np.random.shuffle(entries)
            lists[name] = entries[:n_train] if name.startswith('train') else entries[-n_test:]
        for name, entries in lists.items():
            split, cls = name.split('_')
            label = 'ambiguous' if cls == 'ambig' else 'clear'
            for e in entries:
                table.add(f'faithful/{dataset}/{split}', e['prompt'], label, f'{dataset}:{e["id"]}')
        train_ids = {e['id'] for e in lists['train_ambig']} | {e['id'] for e in lists['train_clean']}
        test_ids = {e['id'] for e in lists['test_ambig']} | {e['id'] for e in lists['test_clean']}
        info[dataset] = {'pairs_in_file': len(ambig), 'pair_ids_on_both_sides': len(train_ids & test_ids)}
    return info


# ---- grouped protocol ---------------------------------------------------------------------------
def situatedqa_questions(root: Path, splits: tuple[str, ...]) -> list[dict]:
    by_id = {}
    for kind in ('geo', 'temp'):
        for split in splits:
            for row in _jsonl(root / SITUATEDQA_FILES[(kind, split)]):
                if kind == 'temp' and row.get('date_type') not in CONTEXT_DEPENDENT_DATE_TYPES:
                    continue  # `orig` marks temporally independent questions
                key = f'{kind}:{row["id"]}'
                entry = by_id.setdefault(key, {'pair_id': key, 'kind': kind, 'question': row['question'], 'edits': []})
                if row['edited_question'] != row['question'] and row['edited_question'] not in entry['edits']:
                    entry['edits'].append(row['edited_question'])
    return [e for e in by_id.values() if e['edits']]


def appended_phrase(question: str, edited: str) -> str | None:
    q, e = question.strip(), edited.strip()
    if e.lower().startswith(q.lower()) and len(e) > len(q):
        return e[len(q):]
    return None


def ambigqa_questions(path: Path) -> list[dict]:
    """Same rule as construct_ambig_qa.py: multipleQAs present, rewrite = qaPairs[0].question[0]."""
    import pandas as pd
    out = []
    for row in pd.read_parquet(path).to_dict('records'):
        ann = row['annotations']
        if not row['question'] or 'multipleQAs' not in list(ann['type']):
            continue
        questions = list(ann['qaPairs'][0]['question'])
        if questions and questions[0]:
            out.append({'pair_id': f'ambigqa:{row["id"]}', 'kind': 'ambigqa', 'question': row['question'],
                        'edits': [questions[0]]})
    return out


def grouped_sets(root: Path, table: PromptTable, n_train: int, n_test: int, n_control: int, seed: int) -> dict:
    rng = random.Random(seed)
    sq_test = situatedqa_questions(root, ('dev', 'test'))
    test_ids = {r['pair_id'] for r in sq_test}
    sq_train = [r for r in situatedqa_questions(root, ('train',)) if r['pair_id'] not in test_ids]
    aq_train = ambigqa_questions(root / 'ambigqa/light_train.parquet')
    aq_test = ambigqa_questions(root / 'ambigqa/light_validation.parquet')
    for dataset, split, records, n in (('situatedqa', 'train', sq_train, n_train), ('situatedqa', 'test', sq_test, n_test),
                                       ('ambigqa', 'train', aq_train, n_train), ('ambigqa', 'test', aq_test, n_test)):
        for rec in sorted(rng.sample(records, min(n, len(records))), key=lambda r: r['pair_id']):
            table.add(f'grouped/{dataset}/{split}', rec['question'], 'ambiguous', rec['pair_id'])
            table.add(f'grouped/{dataset}/{split}', rng.choice(rec['edits']), 'clear', rec['pair_id'])
    phrases = {'geo': [], 'temp': []}
    for rec in sq_train:
        for edit in rec['edits']:
            phrase = appended_phrase(rec['question'], edit)
            if phrase:
                phrases[rec['kind']].append(phrase)
    pool = []
    for kind in ('geo', 'temp'):
        for split in ('dev', 'test'):
            path = root / f'situatedqa/id_data/{kind}.{split}.jsonl'
            if path.exists():
                pool.extend((kind, r) for r in _jsonl(path) if r.get('is_dependent') == 'no')
    for kind, row in rng.sample(pool, min(n_control, len(pool))):
        q = row['question'].rstrip(' ?')
        pid = f'lexctl:{kind}:{row["id"]}'
        table.add('grouped/lexical_control/test', q, 'base', pid)
        table.add('grouped/lexical_control/test', q + rng.choice(phrases[kind]), 'phrased', pid)
    return {'available': {'situatedqa_train': len(sq_train), 'situatedqa_test': len(sq_test),
                          'ambigqa_train': len(aq_train), 'ambigqa_test': len(aq_test), 'control_pool': len(pool)},
            'phrase_pool': {k: len(v) for k, v in phrases.items()}}


def build_task(root: Path, cfg: dict) -> dict:
    table = PromptTable()
    faithful = faithful_sets(root, table, cfg['n_train'], cfg['n_test'])
    grouped = grouped_sets(root, table, cfg['n_train'], cfg['n_test'], cfg['n_control'], cfg['seed'])
    counts = {name: {lab: sum(1 for e in entries if e['label'] == lab) for lab in sorted({e['label'] for e in entries})}
              for name, entries in table.sets.items()}
    return {'prompts': table.prompts, 'sets': table.sets,
            'info': {'faithful': faithful, 'grouped': grouped, 'counts': counts, 'n_unique_prompts': len(table.prompts)}}


def data_hashes(root: Path) -> dict:
    files = [f for pair in ORIGINAL_FILES.values() for f in pair] + list(SITUATEDQA_FILES.values())
    files += ['ambigqa/light_train.parquet', 'ambigqa/light_validation.parquet']
    files += [f'situatedqa/id_data/{k}.{s}.jsonl' for k in ('geo', 'temp') for s in ('dev', 'test')]
    out = {f: sha256(root / f) for f in files if (root / f).exists()}
    for name in ('situatedqa/COMMIT', 'original/COMMIT'):
        path = root / name
        out[name] = path.read_text().strip() if path.exists() else None
    out['ambigqa_revision'] = 'e969d0132f4dd28c2939d55be34f1788c00ccfe7'
    return out


# ---- probes (sklearn, as in the original) ---------------------------------------------------------
def fit_probe(x, y):
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(max_iter=1000).fit(x, y)


def evaluate(clf, x, y) -> dict:
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
    pred = clf.predict(x)
    score = clf.decision_function(x)
    return {'acc': float(accuracy_score(y, pred)), 'auc': float(roc_auc_score(y, score)),
            'macro_precision': float(precision_score(y, pred, average='macro', zero_division=0)),
            'macro_recall': float(recall_score(y, pred, average='macro', zero_division=0)),
            'macro_f1': float(f1_score(y, pred, average='macro', zero_division=0))}


def noise_curve(clf, x, y, ranking, max_k: int, seed: int) -> list[dict]:
    """remove_first_n_dims: replace the first k ranked dims with N(mean, std) of the test column."""
    import numpy as np
    from sklearn.metrics import accuracy_score
    rng = np.random.default_rng(seed)
    out = []
    for k in range(0, max_k + 1):
        noisy = x.copy()
        for dim in ranking[:k]:
            noisy[:, dim] = rng.normal(x[:, dim].mean(), x[:, dim].std(), size=len(x))
        out.append({'k': k, 'acc': float(accuracy_score(y, clf.predict(noisy)))})
    return out


def pick_aen_k(curve: list[dict]) -> int:
    """Smallest k whose accuracy drop reaches half of the largest drop on the curve (our rule; the
    original hand-picked the neurons after inspecting the curve)."""
    base = curve[0]['acc']
    drops = [(c['k'], base - c['acc']) for c in curve[1:]]
    target = max(d for _, d in drops) / 2
    for k, d in drops:
        if d > 0 and d >= target:
            return k
    return drops[-1][0]


def score_with_bundle(bundle: dict, prefix: str, x):
    """Score activations with a saved probe. prefix is either a full-probe tag
    '<mode>/<protocol>/<dataset>/<key>/L<layer>' (x: [N, hidden]) or an AEN tag
    'aen/<mode>/<protocol>/<dataset>/input_mean/L<layer>' (x: [N, hidden]; the AEN dims are selected here).
    Returns decision scores; > 0 means "ambiguous". Activations must be taken the same way
    (same model, layer, position and prompt format)."""
    import numpy as np
    x = np.asarray(x, dtype=np.float32)
    if prefix.startswith('aen/'):
        x = x[:, bundle[prefix + '/dims']]
    return x @ bundle[prefix + '/coef'] + bundle[prefix + '/intercept'][0]
