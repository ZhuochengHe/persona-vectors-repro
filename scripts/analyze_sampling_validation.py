"""Select matched-trait settings on development data, assess fixed confirmation data."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import statistics

from persona_repro.common import read_jsonl, require_compute, write_json


def score(row, metric):
    value = row['scores'][metric]
    return value['score'] if value['status'] == 'ok' else None


def paired_result(left, right):
    """right minus left; resample questions, retaining all their rollouts."""
    left = {r['sample_id']: r for r in left}
    assert len(left) == len(right) == 40
    assert set(left) == {r['sample_id'] for r in right}
    groups = defaultdict(list)
    trait_values = [[], []]
    for r in right:
        l = left[r['sample_id']]
        assert l['question'] == r['question'] and l['seed'] == r['seed']
        assert score(l, 'coherence') is not None and score(r, 'coherence') is not None
        groups[r['question_id']].append(score(r, 'coherence') - score(l, 'coherence'))
        a, b = score(l, 'evil'), score(r, 'evil')
        if a is not None and b is not None:
            trait_values[0].append(a)
            trait_values[1].append(b)
    qids = sorted(groups)
    rng = random.Random(20261030)
    boot = sorted(statistics.mean(v for q in rng.choices(qids, k=len(qids)) for v in groups[q])
                  for _ in range(2000))
    return {'coherence_difference': statistics.mean(v for values in groups.values() for v in values),
            'coherence_difference_question_bootstrap_95': [boot[49], boot[1949]],
            'paired_numeric_trait_count': len(trait_values[0]),
            'paired_trait_mean_topk0': statistics.mean(trait_values[0]) if trait_values[0] else None,
            'paired_trait_mean_topk20': statistics.mean(trait_values[1]) if trait_values[1] else None}


def select(development, targets):
    choices = {}
    for target in targets:
        pair = {}
        for k in [0, 20]:
            eligible = [v for v in development.values() if v['design']['generation']['top_k'] == k
                        and v['evil_mean'] is not None and v['evil_numeric_count'] >= 30
                        and abs(v['evil_mean'] - target) <= 10]
            best = min(eligible, key=lambda v: (abs(v['evil_mean'] - target), v['design'].get('alpha', 0)),
                       default=None)
            pair[str(k)] = best['design']['id'] if best else None
        choices[str(target)] = pair
    return choices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require_compute()
    run = args.run
    summary = json.loads((run / 'summary.json').read_text())['conditions']
    development = {k: v for k, v in summary.items() if v['design']['split'] == 'development'}
    choices = select(development, [10, 25, 50, 75])
    # Freeze this decision before reading confirmation responses.
    write_json(run / 'matched-trait-selection.json', {'rule': 'Development mean nearest target within 10; >=30 numeric traits; ties lower alpha; no confirmation selection',
               'choices': choices})
    comparisons = {}
    for target, pair in choices.items():
        if any(v is None for v in pair.values()):
            comparisons[target] = {'status': 'unsupported_by_development_grid'}
            continue
        names = [pair[str(k)].replace('development-', 'confirmation-', 1) for k in [0, 20]]
        rows = [read_jsonl(run / 'scored' / (name + '.jsonl')) for name in names]
        result = paired_result(*rows)
        result['conditions'] = names
        means = [result['paired_trait_mean_topk0'], result['paired_trait_mean_topk20']]
        result['confirmation_trait_matched_within_10'] = (
            result['paired_numeric_trait_count'] >= 30 and all(v is not None for v in means)
            and abs(means[0] - means[1]) <= 10)
        result['status'] = 'confirmation_evaluated'
        comparisons[target] = result
    baseline = paired_result(*[read_jsonl(run / 'scored' / f'confirmation-k{k}-a0.jsonl') for k in [0, 20]])
    for result in comparisons.values():
        if 'coherence_difference' in result:
            result['coherence_advantage_minus_baseline_advantage'] = (
                result['coherence_difference'] - baseline['coherence_difference'])
    write_json(run / 'matched-trait-confirmation.json', {'comparisons': comparisons,
               'baseline_topk20_minus_topk0': baseline,
               'warning': 'Exploratory cluster-bootstrap intervals; 10 confirmation questions. Fixed alpha pairs may fail to match trait on confirmation. No extrapolation or forced matching.'})


if __name__ == '__main__':
    main()
