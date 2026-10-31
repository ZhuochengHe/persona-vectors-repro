"""Frozen Qwen3.5 altruism extraction, constrained layer sweep, and Figure 3."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import statistics

from persona_repro.common import generation_fingerprint, read_jsonl, require_compute, write_json
from persona_repro.e02 import summarize_pair
from persona_repro.extraction import audit_pairs
from persona_repro.gaming import select_layer
from persona_repro.judge import score_files
from persona_repro.model import Steering, generation_stop_ids
from persona_repro.operations import extract_vectors, generate_file, load_vector, runtime_from_config, vector_shape


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def profile(config, extraction=False):
    current = deepcopy(config)
    if extraction:
        current['model']['attn_implementation'] = 'eager'
    return current


def scan_cells(config):
    return [{'id': 'baseline', 'layer': None, 'coefficient': 0.0}] + [
        {'id': f'l{layer:02d}-a{alpha:g}'.replace('.', 'p'),
         'layer': layer, 'coefficient': alpha}
        for layer in config['gaming']['layers'] for alpha in config['gaming']['scan_coefficients']]


def fixed_cells(config, pilot=False):
    values = config['gaming']['pilot_coefficients' if pilot else 'evaluation_coefficients']
    return [{'id': 'a' + f'{alpha:g}'.replace('-', 'm').replace('.', 'p'),
             'layer': None if alpha == 0 else 'selected', 'coefficient': alpha} for alpha in values]


def vector_ready(run, config):
    frozen = json.loads((run / 'vector-provenance.json').read_text())
    assert digest(run / 'vectors/altruism.pt') == frozen['sha256']
    metadata = json.loads((run / 'vectors/altruism.json').read_text())
    assert metadata['model']['id'] == config['model']['id']
    assert metadata['model']['revision'] == config['model']['revision']
    assert metadata['source_commit'] == config['upstream_commit']


def selected_layer(run):
    provenance = json.loads((run / 'selection-provenance.json').read_text())
    assert digest(run / 'selection.json') == provenance['sha256']
    selection = json.loads((run / 'selection.json').read_text())
    chosen = selection['selected_by_coherence_floor']['75']
    if chosen is None:
        raise ValueError('No positive-gain layer meets development coherence>=75 and coverage constraints')
    return chosen['layer']


def checked(run, config, folder, cell, task_file, scored=False, extraction=False):
    current = profile(config, extraction)
    path = run / folder / ('scored' if scored else 'responses') / (cell['id'] + '.jsonl')
    tasks = {r['sample_id']: r for r in read_jsonl(run / task_file)}
    rows = read_jsonl(path)
    assert len(rows) == len(tasks) and len({r['sample_id'] for r in rows}) == len(rows)
    assert {r['sample_id'] for r in rows} == set(tasks)
    layer = selected_layer(run) if cell['layer'] == 'selected' else cell['layer']
    fp = generation_fingerprint(current, vector_digest=digest(run / 'vectors/altruism.pt') if layer else None,
                                layer=layer, coefficient=cell['coefficient'])
    for row in rows:
        assert row['generation_fingerprint'] == fp
        assert row['model_id'] == config['model']['id'] and row['model_revision'] == config['model']['revision']
        assert row['messages'] == tasks[row['sample_id']]['messages']
    if scored:
        originals = {r['sample_id']: r for r in checked(run, config, folder, cell, task_file, extraction=extraction)}
        for row in rows:
            assert all(row[k] == originals[row['sample_id']][k] for k in
                       ['answer', 'answer_token_ids', 'prompt_token_ids', 'seed', 'generation_fingerprint'])
    return rows


def generate_cells(run, config, folder, cells, task_file):
    vector_ready(run, config)
    runtime = runtime_from_config(config)
    for cell in cells:
        layer = selected_layer(run) if cell['layer'] == 'selected' else cell['layer']
        generate_file(run / task_file, run / folder / 'responses' / (cell['id'] + '.jsonl'), config,
                      vector_path=run / 'vectors/altruism.pt' if layer else None,
                      layer=layer, coefficient=cell['coefficient'], runtime=runtime)
        checked(run, config, folder, cell, task_file)
    assert not any(block._forward_hooks for block in runtime.layers)


def score_cells(run, config, folder, cells, task_file):
    vector_ready(run, config)
    for cell in cells:
        checked(run, config, folder, cell, task_file)
    score_files([(run / folder / 'responses' / (c['id'] + '.jsonl'),
                  run / folder / 'scored' / (c['id'] + '.jsonl'), None) for c in cells], config)


def summarize(run, config, folder, cells, task_file):
    from random_direction_control import repetition
    baseline_cell = next(c for c in cells if c['coefficient'] == 0)
    base = checked(run, config, folder, baseline_cell, task_file, scored=True)
    result = []
    for cell in cells:
        rows = checked(run, config, folder, cell, task_file, scored=True)
        item = summarize_pair(rows, base, 'altruism')
        item.update(cell)
        if item['layer'] == 'selected':
            item['layer'] = selected_layer(run)
        item['split'] = 'development' if folder == 'scan' else folder
        stops = set(config['gaming']['stop_ids'])
        values = []
        for row in rows:
            ids = row['answer_token_ids']
            end = next((i for i, token in enumerate(ids) if token in stops), len(ids))
            values.append(repetition(ids[:end]))
        item['repetition_4gram_mean'] = statistics.mean(values)
        if folder == 'evaluation':
            item['by_game'] = {}
            for game in sorted({r['game'] for r in rows}):
                item['by_game'][game] = summarize_pair([r for r in rows if r['game'] == game],
                                                     [r for r in base if r['game'] == game], 'altruism')
        result.append(item)
    write_json(run / folder / 'summary.json', result)
    return result


def preflight(run, config):
    import torch
    runtime = runtime_from_config(config)
    assert len(runtime.layers) == 32
    assert all(p.device.type == 'cuda' and p.dtype == torch.bfloat16 for p in runtime.model.parameters())
    messages = [{'role': 'user', 'content': 'What is 2 + 2? Answer briefly.'}]
    base = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=32)
    assert base['answer'].strip()
    direction = torch.randn(2560, generator=torch.Generator().manual_seed(73))
    direction /= direction.norm()
    with Steering(runtime.layers, 20, direction, 0, 'all'):
        zero = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=32)
    assert zero['answer_token_ids'] == base['answer_token_ids']
    source = Path(config['paths']['upstream']) / 'activation_steer.py'
    spec = importlib.util.spec_from_file_location('gaming_upstream_hook', source)
    module = importlib.util.module_from_spec(spec)
    old_hf_home = os.environ.get('HF_HOME')
    try:
        spec.loader.exec_module(module)
    finally:
        if old_hf_home is None:
            os.environ.pop('HF_HOME', None)
        else:
            os.environ['HF_HOME'] = old_hf_home
    # The upstream layer locator knows model.layers but not Qwen3.5's wrapper.
    text_model = runtime.model.model.language_model
    assert text_model.layers is runtime.layers
    with Steering(runtime.layers, 20, direction, 1, 'all'):
        own = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=32)
    from types import SimpleNamespace
    proxy = SimpleNamespace(model=SimpleNamespace(layers=runtime.layers),
                            config=text_model.config, parameters=runtime.model.parameters)
    with module.ActivationSteerer(proxy, direction, coeff=1, layer_idx=19, positions='all'):
        upstream = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=32)
    assert own['answer_token_ids'] == upstream['answer_token_ids']
    assert not any(block._forward_hooks for block in runtime.layers)
    write_json(run / 'preflight.json', {'status': 'passed', 'zero_matches': True,
               'gaming_upstream_all_hook_matches': True, 'sample': base,
               'backend': runtime.backend_info, 'stop_ids': generation_stop_ids(runtime.tokenizer, runtime.model)})


def plot(run, config, result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # These intervals are across rollouts for one fixed game, not across games.
    import random
    games = [r['game'] for r in read_jsonl(run / 'tasks/evaluation.jsonl') if r['rollout'] == 0]
    points = []
    for metric, label in [('altruism', 'Altruism'), ('coherence', 'Coherence')]:
        fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
        for ax, game in zip(axes.flat, games):
            xs, means, lows, highs = [], [], [], []
            for cell in sorted(fixed_cells(config), key=lambda c: c['coefficient']):
                rows = read_jsonl(run / 'evaluation/scored' / (cell['id'] + '.jsonl'))
                values = [r['scores'][metric]['score'] for r in rows
                          if r['game'] == game and r['scores'][metric]['status'] == 'ok']
                if not values:
                    continue
                rng = random.Random(20261030)
                boots = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(2000))
                xs.append(cell['coefficient']);means.append(statistics.mean(values))
                lows.append(boots[49]);highs.append(boots[1949])
                points.append({'metric': metric, 'game': game, 'coefficient': cell['coefficient'],
                               'numeric_count': len(values), 'mean': statistics.mean(values),
                               'rollout_bootstrap_95': [boots[49], boots[1949]]})
            ax.plot(xs, means, 'o-')
            ax.fill_between(xs, lows, highs, alpha=0.2)
            ax.set_title(game);ax.set_ylim(-3, 103);ax.set_xlabel('Steering coefficient')
            ax.set_ylabel(label)
        fig.suptitle(f'Qwen3.5-4B | selected layer {selected_layer(run)} | Luna direct score')
        fig.tight_layout()
        fig.savefig(run / f'evaluation/{metric}.png', dpi=180)
        fig.savefig(run / f'evaluation/{metric}.pdf')
        plt.close(fig)
    write_json(run / 'evaluation/figure-points.json', {'points': points,
               'interval_unit': 'rollouts of one fixed game prompt; not independent questions'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['preflight', 'extract-generate', 'extract-score', 'vectors',
                        'scan-generate', 'scan-score', 'pilot-generate', 'pilot-score',
                        'evaluation-generate', 'evaluation-score'])
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--shard', type=int, default=0)
    args = parser.parse_args();require_compute();run = args.run
    config = json.loads((run / 'config.json').read_text())
    manifest = json.loads((run / 'manifest.json').read_text())
    for path, sha in manifest['sha256'].items():
        if digest(run / path) != sha:
            raise ValueError(f'Frozen gaming input changed: {path}')
    stage = args.stage
    if stage == 'preflight':
        preflight(run, config)
    elif stage == 'extract-generate':
        generate_file(run / 'tasks/extraction.jsonl', run / 'extraction/responses/baseline.jsonl', profile(config, True))
    elif stage == 'extract-score':
        cell = {'id': 'baseline', 'layer': None, 'coefficient': 0.0}
        checked(run, config, 'extraction', cell, 'tasks/extraction.jsonl', extraction=True)
        score_files([(run / 'extraction/responses/baseline.jsonl', run / 'extraction/scored/baseline.jsonl', None)], config)
        checked(run, config, 'extraction', cell, 'tasks/extraction.jsonl', extraction=True, scored=True)
    elif stage == 'vectors':
        rows = checked(run, config, 'extraction', {'id': 'baseline', 'layer': None, 'coefficient': 0.0},
                       'tasks/extraction.jsonl', extraction=True, scored=True)
        accepted, audit = audit_pairs(rows, config['extraction'])
        write_json(run / 'extraction/filter-statistics.json', audit)
        assert audit['retained_pairs'] >= 20, 'Fewer than 20 retained extraction pairs'
        assert len({r['question_id'] for r in accepted}) >= 10, 'Insufficient question coverage'
        assert len({r['instruction_id'] for r in accepted}) >= 3, 'Insufficient prefix coverage'
        extract_vectors(run / 'extraction/scored/baseline.jsonl', run / 'vectors/altruism.pt', profile(config, True))
        write_json(run / 'vector-provenance.json', {'sha256': digest(run / 'vectors/altruism.pt')})
    else:
        folder = stage.split('-')[0]
        folder = 'evaluation' if folder == 'evaluation' else folder
        task_file = f'tasks/{folder}.jsonl'
        cells = scan_cells(config) if folder == 'scan' else fixed_cells(config, pilot=folder == 'pilot')
        if stage.endswith('generate'):
            shards = config['gaming']['generation_shards'] if folder in ('scan', 'evaluation') else 1
            assert 0 <= args.shard < shards
            generate_cells(run, config, folder, [c for i, c in enumerate(cells) if i % shards == args.shard], task_file)
        else:
            score_cells(run, config, folder, cells, task_file)
            result = summarize(run, config, folder, cells, task_file)
            if folder == 'scan':
                selection = select_layer(result)
                write_json(run / 'selection.json', selection)
                write_json(run / 'selection-provenance.json', {'sha256': digest(run / 'selection.json')})
                selected_layer(run)  # Fail closed before pilot/formal if no valid primary layer.
            elif folder == 'evaluation':
                plot(run, config, result)
    write_json(run / 'logs' / f'{stage}-{args.shard}.done.json', {'status': 'complete', 'stage': stage})


if __name__ == '__main__':
    main()
