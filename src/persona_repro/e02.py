"""Frozen E02 sweep, development-only selection, and held-out evaluation."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

from .common import load_config, read_jsonl, require_compute, write_json, write_jsonl
from .inference_tasks import build_evaluation_tasks


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def condition(trait, layer, coefficient, split='dev'):
    label = f'{coefficient:g}'.replace('.', 'p').replace('-', 'm')
    return {'id': f'{trait}-{split}-l{layer:02d}-a{label}', 'trait': trait,
            'split': split, 'layer': layer, 'coefficient': float(coefficient)}


def tasks_for(config, trait, split):
    ids = config['evaluation']['question_splits'][trait][split]
    return build_evaluation_tasks(Path(config['paths']['upstream']), trait, ids,
                                  config['generation']['rollouts'])


def screen_conditions(config):
    cells = []
    for trait in config['traits']:
        # A zero hook has identical arithmetic at every layer; reuse it globally.
        cells.append(condition(trait, config['steering']['layers'][0], 0))
        cells.extend(condition(trait, layer, 1) for layer in config['steering']['layers'])
    return cells


def verify_run(run, config):
    manifest = json.loads((run / 'manifest.json').read_text())
    if digest(run / 'config.json') != manifest['config_sha256']:
        raise ValueError('Frozen E02 config changed')
    for relative, expected in manifest['source_sha256'].items():
        if digest(run / 'source' / relative) != expected:
            raise ValueError(f'Frozen E02 source changed: {relative}')
    for trait in config['traits']:
        vector = run / 'vectors' / f'{trait}.pt'
        if digest(vector) != manifest['vectors'][trait]['sha256']:
            raise ValueError(f'Frozen E01 vector changed: {trait}')
        metadata = json.loads(vector.with_suffix('.json').read_text())
        if metadata['trait'] != trait or any(metadata['model'][key] != config['model'][key]
                                             for key in ('id', 'revision')):
            raise ValueError('E01/E02 vector model or trait mismatch')
        for split in ('dev', 'test'):
            expected = tasks_for(config, trait, split)
            if read_jsonl(run / 'tasks' / f'{trait}-{split}.jsonl') != expected:
                raise ValueError('Frozen E02 question tasks changed')
        splits = config['evaluation']['question_splits'][trait]
        if set(splits['dev']) & set(splits['test']):
            raise ValueError('Development/test question overlap')


def checked_rows(run, config, cell, folder):
    from .common import generation_fingerprint
    rows = read_jsonl(run / folder / f"{cell['id']}.jsonl")
    tasks = {row['sample_id']: row for row in tasks_for(config, cell['trait'], cell['split'])}
    if len(rows) != len(tasks) or len({r['sample_id'] for r in rows}) != len(tasks):
        raise ValueError(f"Incomplete or duplicate cell: {cell['id']}")
    for row in rows:
        task = tasks.get(row['sample_id'])
        if task is None or any(row[k] != task[k] for k in ('messages', 'question_id', 'rollout', 'trait')):
            raise ValueError('E02 response/task mismatch')
        if row['layer'] != cell['layer'] or row['coefficient'] != cell['coefficient']:
            raise ValueError('E02 layer/coefficient mismatch')
        if row['model_id'] != config['model']['id'] or row['model_revision'] != config['model']['revision']:
            raise ValueError('E02 response/model mismatch')
        if row['checkpoint_id'] != 'base':
            raise ValueError('E02 requires the untrained base checkpoint')
        expected = generation_fingerprint(config, vector_digest=digest(run/'vectors'/f"{cell['trait']}.pt"),
                                          layer=cell['layer'], coefficient=cell['coefficient'])
        if row.get('generation_fingerprint') != expected:
            raise ValueError('E02 generation protocol/fingerprint mismatch')
    if folder == 'scored':
        original = {row['sample_id']: row for row in checked_rows(run, config, cell, 'responses')}
        for row in rows:
            if any(row.get(k) != original[row['sample_id']].get(k) for k in
                   ('answer', 'prompt_token_ids', 'answer_token_ids', 'seed', 'generation_fingerprint')):
                raise ValueError('E02 scored response differs from original generation')
    return rows


def numeric_score(row, metric):
    value = row['scores'][metric]
    if value['status'] != 'ok':
        return None
    score = value['score']
    if isinstance(score, bool) or not isinstance(score, (float, int)) or not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError('Invalid numeric E02 score')
    return float(score)


def summarize_pair(rows, baseline, trait):
    base = {r['sample_id']: r for r in baseline}
    if len(base) != len(baseline) or len(rows) != len(base) or {r['sample_id'] for r in rows} != set(base):
        raise ValueError('E02 paired baseline IDs differ')
    gains, coherence_deltas, questions = [], [], defaultdict(list)
    status_counts = Counter()
    trait_values, coherence_values = [], []
    for row in rows:
        other = base[row['sample_id']]
        if row['seed'] != other['seed'] or row['messages'] != other['messages']:
            raise ValueError('E02 conditions are not seed/prompt paired')
        for metric in (trait, 'coherence'):
            status_counts[metric + ':' + row['scores'][metric]['status']] += 1
        value, reference = numeric_score(row, trait), numeric_score(other, trait)
        coherent, base_coherent = numeric_score(row, 'coherence'), numeric_score(other, 'coherence')
        if value is not None:
            trait_values.append(value)
        if coherent is not None:
            coherence_values.append(coherent)
        if coherent is not None and base_coherent is not None:
            coherence_deltas.append(coherent - base_coherent)
        # Refusals/invalid scores remain explicit; never impute them as zero.
        if value is not None and reference is not None:
            gains.append(value - reference)
            questions[row['question_id']].append(value - reference)
    interval = None
    if len(questions) >= 2:
        rng = random.Random(0)
        groups = list(questions.values())
        draws = sorted(statistics.mean(x for group in rng.choices(groups, k=len(groups)) for x in group)
                       for _ in range(1000))
        interval = [draws[24], draws[974]]
    return {'responses': len(rows), 'paired_numeric_trait_responses': len(gains),
            'paired_numeric_trait_questions': len(questions),
            'paired_numeric_coherence_responses': len(coherence_deltas),
            'trait_mean': statistics.mean(trait_values) if trait_values else None,
            'coherence_mean': statistics.mean(coherence_values) if coherence_values else None,
            'trait_gain': statistics.mean(gains) if gains else None,
            'coherence_change': statistics.mean(coherence_deltas) if coherence_deltas else None,
            'trait_gain_question_bootstrap_95': interval,
            'status_counts': dict(status_counts),
            'truncated_responses': sum(row['truncated'] for row in rows)}


def rank_eligible(summaries, max_drop):
    eligible = [r for r in summaries if r['trait_gain'] is not None and
                r['coherence_change'] is not None and r['coherence_change'] >= -max_drop]
    return sorted(eligible, key=lambda r: (-r['trait_gain'], abs(r['coefficient']), r['layer']))


def development_summary(run, config, cells):
    summaries = []
    for trait in config['traits']:
        baseline_cell = condition(trait, config['steering']['layers'][0], 0)
        baseline = checked_rows(run, config, baseline_cell, 'scored')
        for cell in cells:
            if cell['trait'] == trait:
                rows = checked_rows(run, config, cell, 'scored')
                summaries.append(dict(cell, **summarize_pair(rows, baseline, trait)))
    return summaries


def generate_cells(run, config, cells):
    from .model import ModelRuntime
    from .operations import generate_file
    runtime = ModelRuntime(config['model']['id'], config['model']['revision'],
                           attention_implementation=config['model']['attn_implementation'],
                           require_fast_kernels=config['model']['require_fast_kernels'])
    for cell in cells:
        print(json.dumps({'condition': cell}, ensure_ascii=False), flush=True)
        generate_file(run / 'tasks' / f"{cell['trait']}-{cell['split']}.jsonl",
                      run / 'responses' / f"{cell['id']}.jsonl", config,
                      vector_path=run / 'vectors' / f"{cell['trait']}.pt",
                      layer=cell['layer'], coefficient=cell['coefficient'], runtime=runtime)
        checked_rows(run, config, cell, 'responses')


def score_cells(run, config, cells):
    from .judge import score_files
    files = []
    for cell in cells:
        print(json.dumps({'score_condition': cell}, ensure_ascii=False), flush=True)
        checked_rows(run, config, cell, 'responses')
        files.append((run / 'responses' / f"{cell['id']}.jsonl",
                      run / 'scored' / f"{cell['id']}.jsonl", None))
    score_files(files, config)
    for cell in cells:
        checked_rows(run, config, cell, 'scored')


def smoke(run, config):
    import torch
    from .model import Steering
    from .operations import load_vector, runtime_from_config, generate_file
    runtime = runtime_from_config(config)
    for trait in config['traits']:
        load_vector(run / 'vectors' / f'{trait}.pt', 32)
    probe_trait = config['traits'][0]
    probe_vector = run / 'vectors' / f'{probe_trait}.pt'
    messages = [{'role': 'user', 'content': 'Say hello in a short sentence.'}]
    baseline = runtime.generate(messages, seed=42, max_new_tokens=8)
    for positions in ('last', 'all'):
        with Steering(runtime.layers, 4, load_vector(probe_vector, 4), 0, positions):
            zero = runtime.generate(messages, seed=42, max_new_tokens=8)
        if baseline['answer_token_ids'] != zero['answer_token_ids']:
            raise ValueError(f'Zero-hook baseline changed sampled output: {positions}')
    smoke_config = json.loads(json.dumps(config))
    smoke_config['generation']['max_new_tokens'] = 8
    smoke_tasks = run / 'smoke' / 'tasks.jsonl'
    write_jsonl(smoke_tasks, tasks_for(config, probe_trait, 'dev')[:1])
    for layer in (4, 16, 32):
        generate_file(smoke_tasks, run / 'smoke' / f'layer{layer}.jsonl', smoke_config,
                      vector_path=probe_vector, layer=layer,
                      coefficient=1, runtime=runtime)
    smoke_config['generation']['steering_positions'] = 'all'
    generate_file(smoke_tasks, run / 'smoke' / 'layer12-all.jsonl', smoke_config,
                  vector_path=probe_vector, layer=12, coefficient=1, runtime=runtime)
    if any(layer._forward_hooks for layer in runtime.layers):
        raise ValueError('Steering hook leaked after generation')
    write_json(run / 'smoke' / 'result.json', {'status': 'passed', 'zero_sampled_ids_equal': True,
        'nonzero_layers': [4, 16, 32], 'all_vectors_finite': True, 'backend': runtime.backend_info})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['smoke', 'screen-generate', 'screen-score',
        'refine-generate', 'refine-score', 'test-generate', 'test-score'])
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require_compute()
    run = args.run
    config = load_config(run / 'config.json')
    verify_run(run, config)
    screen = screen_conditions(config)
    if args.stage == 'smoke':
        smoke(run, config)
    elif args.stage == 'screen-generate':
        generate_cells(run, config, screen)
    elif args.stage == 'screen-score':
        score_cells(run, config, screen)
        summaries = development_summary(run, config, screen)
        followup, shortlisted = [], {}
        for trait in config['traits']:
            ranked = rank_eligible([s for s in summaries if s['trait'] == trait and s['coefficient'] == 1],
                                   config['steering']['max_coherence_drop'])
            shortlisted[trait] = [s['layer'] for s in ranked[:config['steering']['shortlist_size']]]
            for layer in shortlisted[trait]:
                followup.extend(condition(trait, layer, a) for a in config['steering']['coefficients'] if a not in (0, 1))
        write_json(run / 'screen-summary.json', summaries)
        write_json(run / 'refine-plan.json', {'shortlisted_layers': shortlisted, 'conditions': followup})
    elif args.stage.startswith('refine-'):
        followup = json.loads((run / 'refine-plan.json').read_text())['conditions']
        if args.stage == 'refine-generate':
            generate_cells(run, config, followup)
        else:
            score_cells(run, config, followup)
            summaries = development_summary(run, config, screen + followup)
            selected, test = {}, []
            for trait in config['traits']:
                ranked = rank_eligible([s for s in summaries if s['trait'] == trait and s['coefficient'] != 0],
                                       config['steering']['max_coherence_drop'])
                best = ranked[0] if ranked and ranked[0]['trait_gain'] > 0 else None
                selected[trait] = best
                if best:
                    test.extend([condition(trait, config['steering']['layers'][0], 0, 'test'),
                                 condition(trait, best['layer'], best['coefficient'], 'test')])
            write_json(run / 'development-summary.json', summaries)
            write_json(run / 'selection.json', {'selected': selected, 'test_conditions': test,
                'rule': 'positive paired trait gain; coherence change >= -5; tie: smaller coefficient then layer',
                'non_numeric_policy': 'metric-wise numeric paired cases only; refusals/invalid remain explicit'})
    else:
        selection = json.loads((run / 'selection.json').read_text())
        cells = selection['test_conditions']
        if args.stage == 'test-generate':
            generate_cells(run, config, cells)
        else:
            score_cells(run, config, cells)
            results = {}
            for trait in config['traits']:
                subset = [c for c in cells if c['trait'] == trait]
                if not subset:
                    results[trait] = {'status': 'no_acceptable_positive_effect_on_development'}
                    continue
                baseline = checked_rows(run, config, subset[0], 'scored')
                steered = checked_rows(run, config, subset[1], 'scored')
                results[trait] = dict(subset[1], **summarize_pair(steered, baseline, trait))
            write_json(run / 'heldout-summary.json', results)
    print(json.dumps({'stage': args.stage, 'status': 'complete'}), flush=True)


if __name__ == '__main__':
    main()
