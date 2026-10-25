"""Auditable, repository-style paired filtering for E01 (no model imports)."""
from __future__ import annotations
from collections import Counter, defaultdict
import math


def _numeric_score(row: dict, metric: str) -> float | None:
    value = row.get('scores', {}).get(metric, {})
    if value.get('status') != 'ok':
        return None
    score = value.get('score')
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError(f'Invalid numeric {metric} score for {row.get("sample_id")}')
    return float(score)


def audit_pairs(rows: list[dict], settings: dict) -> tuple[list[dict], dict]:
    """Return retained rows and an audit over *every* original pair.

    No target retention percentage is invented: low coverage is visible in the
    report and does not cause adaptive threshold changes or resampling.
    """
    if settings.get('filter_mode') != 'paired_repo':
        raise ValueError('Only explicitly selected paired_repo filtering is implemented')
    threshold = settings['threshold']
    coherence = settings['coherence_threshold']
    if not 0 <= threshold <= 100 or not 0 <= coherence <= 100:
        raise ValueError('Score thresholds must be in [0,100]')
    if not rows or len({row['trait'] for row in rows}) != 1:
        raise ValueError('Expected nonempty extraction responses for exactly one trait')
    trait = rows[0]['trait']
    grouped = {}
    samples = set()
    for row in rows:
        if row['sample_id'] in samples:
            raise ValueError('Duplicate extraction sample_id')
        samples.add(row['sample_id'])
        polarity = row['polarity']
        if polarity not in ('pos', 'neg'):
            raise ValueError(f'Invalid extraction polarity {polarity!r}')
        group = grouped.setdefault(row['pair_id'], {})
        if polarity in group:
            raise ValueError('Duplicate extraction polarity in pair')
        group[polarity] = row
    accepted, decisions = [], []
    rejection_counts = Counter()
    coverage = {field: defaultdict(lambda: {'total_pairs': 0, 'retained_pairs': 0}) for field in ('question_id', 'instruction_id')}
    truncation = {side: {'responses': 0, 'truncated': 0, 'unknown': 0} for side in ('pos', 'neg')}
    for pair_id, group in grouped.items():
        if set(group) != {'pos', 'neg'}:
            raise ValueError(f'Unpaired extraction record: {pair_id}')
        pos, neg = group['pos'], group['neg']
        for field in ('trait', 'question_id', 'instruction_id', 'rollout'):
            if pos[field] != neg[field]:
                raise ValueError(f'Extraction pair disagrees on {field}: {pair_id}')
        reasons = []
        pair_scores = {}
        for side, row in (('pos', pos), ('neg', neg)):
            truncation[side]['responses'] += 1
            if 'truncated' not in row:
                truncation[side]['unknown'] += 1
            elif row['truncated']:
                truncation[side]['truncated'] += 1
            trait_score = _numeric_score(row, trait)
            coherence_score = _numeric_score(row, 'coherence')
            pair_scores[side] = {'trait': trait_score, 'coherence': coherence_score}
            if trait_score is None:
                reasons.append(f'{side}_trait_non_numeric')
            elif (side == 'pos' and trait_score < threshold) or (side == 'neg' and trait_score >= 100-threshold):
                reasons.append(f'{side}_trait_threshold')
            if coherence_score is None:
                reasons.append(f'{side}_coherence_non_numeric')
            elif coherence_score < coherence:
                reasons.append(f'{side}_coherence_threshold')
        retained = not reasons
        if retained:
            accepted.extend([pos, neg])
        rejection_counts.update(reasons)
        for field in coverage:
            entry = coverage[field][str(pos[field])]
            entry['total_pairs'] += 1
            entry['retained_pairs'] += int(retained)
        decisions.append({'pair_id': pair_id, 'question_id': pos['question_id'],
                          'instruction_id': pos['instruction_id'], 'rollout': pos['rollout'],
                          'pos_sample_id': pos['sample_id'], 'neg_sample_id': neg['sample_id'],
                          'retained': retained, 'reasons': reasons, 'scores': pair_scores,
                          'truncated': {side: group[side].get('truncated') for side in ('pos','neg')}})
    retained_pairs = len(accepted) // 2
    for values in truncation.values():
        values['fraction'] = values['truncated'] / values['responses']
    report = {'trait': trait, 'total_pairs': len(grouped), 'retained_pairs': retained_pairs,
              'rejected_pairs': len(grouped)-retained_pairs, 'retained_fraction': retained_pairs/len(grouped),
              'rejection_counts': dict(rejection_counts),
              'coverage': {field: dict(values) for field,values in coverage.items()},
              'truncation': truncation, 'decisions': decisions,
              'status': 'no_valid_pairs' if not accepted else 'vectors_not_yet_extracted',
              'warnings': []}
    if retained_pairs == 1:
        report['warnings'].append('Only one pair retained; vector output alone is not evidence of adequate coverage.')
    for field, values in coverage.items():
        lost = [key for key, value in values.items() if not value['retained_pairs']]
        if lost:
            report['warnings'].append(f'No retained pairs for {field}: {", ".join(lost)}')
    return accepted, report
