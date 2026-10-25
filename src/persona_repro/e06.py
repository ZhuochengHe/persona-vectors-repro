"""Prompt-only E06 monitoring, gated by frozen E02 layer selection."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

from .analysis import pearson_correlation
from .common import load_config, read_jsonl, require_compute, write_json, write_jsonl
from .inference_tasks import build_monitoring_tasks
from .reporting import report_e06


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tasks_for(config, trait):
    return build_monitoring_tasks(Path(config['paths']['upstream']), trait,
        config['monitoring']['question_ids'][trait], Path(config['paths']['monitoring_prompts']),
        config['generation']['rollouts'])


def verify_run(run, config):
    manifest = json.loads((run/'manifest.json').read_text())
    if digest(run/'config.json') != manifest['config_sha256']:
        raise ValueError('Frozen E06 configuration changed')
    for relative, expected in manifest['source_sha256'].items():
        if digest(run/'source'/relative) != expected:
            raise ValueError(f'Frozen E06 source changed: {relative}')
    upstream_run = Path(config['monitoring']['e02_run'])
    if digest(upstream_run/'config.json') != manifest['e02_config_sha256']:
        raise ValueError('E02 configuration changed after E06 setup')
    for trait in config['traits']:
        if digest(run/'vectors'/f'{trait}.pt') != manifest['vectors'][trait]['sha256']:
            raise ValueError('E06 vector changed')
        metadata = json.loads((run/'vectors'/f'{trait}.json').read_text())
        if metadata['trait'] != trait or any(metadata['model'][k] != config['model'][k] for k in ('id','revision')):
            raise ValueError('E06 vector model/trait mismatch')
        if read_jsonl(run/'tasks'/f'{trait}.jsonl') != tasks_for(config, trait):
            raise ValueError('Frozen E06 tasks changed')


def selected_layers(run, config):
    parent = Path(config['monitoring']['e02_run'])
    job = config['monitoring']['e02_final_job']
    marker = parent/'logs'/f'test-score_{job}.done.json'
    if not marker.exists() or json.loads(marker.read_text())['status'] != 'complete':
        raise ValueError('E02 final stage has not completed successfully')
    selection = json.loads((parent/'selection.json').read_text())
    layers, skipped = {}, {}
    for trait in config['traits']:
        best = selection['selected'][trait]
        if best is None:
            skipped[trait] = 'no_acceptable_E02_development_setting'
        else:
            layer = best['layer']
            if not isinstance(layer, int) or not 1 <= layer <= 32:
                raise ValueError('Invalid E02 selected layer')
            layers[trait] = layer
    result = {'layers': layers, 'skipped': skipped,
              'e02_selection_sha256': digest(parent/'selection.json'),
              'e02_final_summary_sha256': digest(parent/'heldout-summary.json')}
    frozen = run/'layer-selection.json'
    if frozen.exists() and json.loads(frozen.read_text()) != result:
        raise ValueError('E02 selection changed after E06 began')
    write_json(frozen, result)
    return result


def prompt_projections(run, config, trait, runtime):
    """Compute all 32 projections once per exact prompt, before any decoding."""
    import torch
    from .operations import load_vector
    runtime.load()
    vector_path = run/'vectors'/f'{trait}.pt'
    # Validate all raw directions, then use exactly the saved unit directions.
    load_vector(vector_path, 1)
    unit = torch.load(vector_path, map_location='cpu', weights_only=True)['unit'].float()
    if unit.shape != (32,2560) or not torch.isfinite(unit).all() or not torch.allclose(
            unit.norm(dim=-1), torch.ones(32), atol=1e-5):
        raise ValueError('Invalid E01 unit vectors')
    vector_hash = digest(vector_path)
    output = run/'projections'/f'{trait}.jsonl'
    cached = {}
    if output.exists():
        for row in read_jsonl(output):
            key = (row['prompt_id'], row['question_id'])
            if key in cached:
                raise ValueError('Duplicate cached prompt projection')
            cached[key] = row
    output.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    with output.open('a') as handle:
        for task in tasks_for(config, trait):
            key = (task['prompt_id'], task['question_id'])
            if key in seen:
                continue
            seen.add(key)
            ids = runtime.encode_conversation(task['messages'])['input_ids']
            if key in cached:
                row = cached[key]
                if row['prompt_token_ids'] != ids or row['messages'] != task['messages'] or row['vector_id'] != vector_hash:
                    raise ValueError('Cached projection prompt/vector changed')
                continue
            captured = runtime.activations(task['messages'])  # No answer, tokens or future response.
            values = torch.stack([captured[layer]['prompt_last'] for layer in range(1,33)])
            projections = (values * unit).sum(-1).tolist()
            if not all(math.isfinite(value) for value in projections):
                raise ValueError('Nonfinite prompt projection')
            row = {'trait': trait, 'prompt_id': task['prompt_id'], 'question_id': task['question_id'],
                   'messages': task['messages'], 'prompt_token_ids': ids,
                   'all_layer_projections': projections, 'vector_id': vector_hash,
                   'projection_model_id': config['model']['id'], 'projection_revision': config['model']['revision'],
                   'projection_checkpoint_id': 'base', 'projection_mode': 'prompt_last'}
            handle.write(json.dumps(row, ensure_ascii=False)+'\n'); handle.flush()
            cached[key] = row
    if set(cached) != seen:
        raise ValueError('Cached projection set differs from frozen prompts')
    return cached


def validate_responses(run, config, trait, folder='responses'):
    from .common import generation_fingerprint
    rows = read_jsonl(run/folder/f'{trait}.jsonl')
    tasks = {r['sample_id']: r for r in tasks_for(config, trait)}
    if len(rows) != len(tasks) or {r['sample_id'] for r in rows} != set(tasks):
        raise ValueError('E06 responses have missing/duplicate/extra samples')
    for row in rows:
        if row.get('generation_fingerprint') != generation_fingerprint(config):
            raise ValueError('E06 generation protocol/fingerprint mismatch')
        task = tasks[row['sample_id']]
        if any(row[k] != task[k] for k in ('messages','question_id','prompt_id','trait','rollout','sampling_seed_id')):
            raise ValueError('E06 response/task mismatch')
        seed = (config['generation']['seed'] + int(hashlib.sha256(task['sampling_seed_id'].encode()).hexdigest()[:8],16)) % 2**32
        if row['seed'] != seed or row['coefficient'] != 0 or row['layer'] is not None or row['checkpoint_id'] != 'base':
            raise ValueError('E06 requires paired seeds and unsteered base generation')
        if row['model_id'] != config['model']['id'] or row['model_revision'] != config['model']['revision']:
            raise ValueError('E06 response model mismatch')
    if folder == 'scored':
        original = {row['sample_id']:row for row in validate_responses(run,config,trait)}
        for row in rows:
            if any(row.get(k) != original[row['sample_id']].get(k) for k in
                   ('answer','prompt_token_ids','answer_token_ids','seed','generation_fingerprint')):
                raise ValueError('E06 scored response differs from original generation')
    return rows


def merge_rows(rows, projections, layer):
    merged = []
    for row in rows:
        p = projections[(row['prompt_id'], row['question_id'])]
        if row['prompt_token_ids'] != p['prompt_token_ids'] or row['messages'] != p['messages']:
            raise ValueError('Projection and generation tokenized prompts differ')
        # Raw response files preserve steering layer=None; this layer is the monitoring layer.
        value = dict(row, steering_layer=row['layer'], layer=layer,
                     projection=p['all_layer_projections'][layer-1])
        for field in ('vector_id','projection_model_id','projection_revision','projection_checkpoint_id','projection_mode'):
            value[field] = p[field]
        merged.append(value)
    return merged


def bootstrap_overall(means, repetitions=1000):
    groups = defaultdict(list)
    for row in means:
        groups[row['question_id']].append(row)
    if len(groups) < 2:
        return None
    rng = random.Random(0)
    groups = list(groups.values())
    correlations = []
    for _ in range(repetitions):
        sampled = [r for group in rng.choices(groups, k=len(groups)) for r in group]
        value = pearson_correlation([r['projection'] for r in sampled], [r['score'] for r in sampled])
        if value is not None:
            correlations.append(value)
    if not correlations:
        return None
    correlations.sort()
    return [correlations[int(.025*(len(correlations)-1))], correlations[int(.975*(len(correlations)-1))]]


def analyze_trait(rows, projections, layer, trait):
    merged = merge_rows(rows, projections, layer)
    counts = Counter(row['scores'][trait]['status'] for row in merged)
    numeric = [row for row in merged if row['scores'][trait]['status'] == 'ok']
    if not numeric:
        return {'status': 'no_numeric_trait_scores', 'score_status_counts': dict(counts)}, merged
    report = report_e06(numeric)  # Per trait: vector/layer identity can differ across traits.
    report['score_status_counts'] = dict(counts)
    report['excluded_non_numeric'] = len(merged)-len(numeric)
    report['total_responses'] = len(merged)
    report['truncated_responses'] = sum(row['truncated'] for row in merged)
    report['overall_question_bootstrap_95'] = bootstrap_overall(report['condition_question_means'])
    report['missing_numeric_conditions'] = sorted(set(row['prompt_id'] for row in merged)-set(row['prompt_id'] for row in numeric))
    report['rollout_count_by_prompt_question'] = [
        {'prompt_id': prompt, 'question_id': question, 'numeric_rollouts': count}
        for (prompt,question),count in sorted(Counter((r['prompt_id'],r['question_id']) for r in numeric).items())]
    report['exploratory_all_layer_correlations'] = []
    for other_layer in range(1,33):
        other_rows = merge_rows(rows, projections, other_layer)
        other_numeric = [r for r in other_rows if r['scores'][trait]['status']=='ok']
        other_report = report_e06(other_numeric)['trait_reports'][0]
        report['exploratory_all_layer_correlations'].append(dict(layer=other_layer, **other_report))
    return report, merged


def smoke(run, config):
    from .operations import runtime_from_config
    runtime = runtime_from_config(config)
    # The check is separate from experiment responses; it never reads E02 selection early.
    task = tasks_for(config, config['traits'][0])[0]
    ids = runtime.encode_conversation(task['messages'])['input_ids']
    captured = runtime.activations(task['messages'])
    response = runtime.generate(task['messages'], seed=42, max_new_tokens=8)
    if ids != response['prompt_token_ids'] or len(captured) != 32 or any(
            value['response_avg'] is not None for value in captured.values()):
        raise ValueError('Prompt-only projection/template check failed')
    write_json(run/'smoke.json', {'status':'passed','all_layers':32,'prompt_only':True,
                                 'prompt_token_ids_equal':True,'backend':runtime.backend_info})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['smoke','generate','score'])
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require_compute()
    run = args.run
    config = load_config(run/'config.json')
    verify_run(run, config)
    if args.stage == 'smoke':
        smoke(run, config)
        return
    selection = selected_layers(run, config)
    if args.stage == 'generate':
        from .model import ModelRuntime
        from .operations import generate_file
        runtime = ModelRuntime(config['model']['id'],config['model']['revision'],
            attention_implementation=config['model']['attn_implementation'],
            require_fast_kernels=config['model']['require_fast_kernels'])
        for trait, layer in selection['layers'].items():
            prompt_projections(run, config, trait, runtime)
            generate_file(run/'tasks'/f'{trait}.jsonl',run/'responses'/f'{trait}.jsonl',config,runtime=runtime)
            validate_responses(run, config, trait)
    else:
        from .judge import score_file
        summary = {'skipped': selection['skipped'], 'traits': {}}
        for trait, layer in selection['layers'].items():
            validate_responses(run, config, trait)
            score_file(run/'responses'/f'{trait}.jsonl',run/'scored'/f'{trait}.jsonl',config,metrics=('trait',))
            rows = validate_responses(run, config, trait, 'scored')
            projections = {(r['prompt_id'],r['question_id']):r for r in read_jsonl(run/'projections'/f'{trait}.jsonl')}
            result, merged = analyze_trait(rows, projections, layer, trait)
            write_jsonl(run/'merged'/f'{trait}.jsonl',merged)
            write_json(run/'results'/f'{trait}.json',result)
            summary['traits'][trait] = result
        write_json(run/'summary.json',summary)
    print(json.dumps({'stage':args.stage,'status':'complete','skipped':selection['skipped']}),flush=True)


if __name__ == '__main__':
    main()
