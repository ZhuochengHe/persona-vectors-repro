"""Development-only layer/alpha selection subject to absolute coherence floors."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .common import load_config, require_compute, write_json
from .e02 import (checked_rows, condition, development_summary, generate_cells,
                  score_cells, smoke, summarize_pair, verify_run)
from .e02_paper import sweep_conditions, write_curves


def select_coherent(summaries, config):
    thresholds = config['steering']['coherence_thresholds']
    selections, tests = {}, []
    for threshold in thresholds:
        choices = {}
        for trait in config['traits']:
            eligible = [r for r in summaries if r['trait'] == trait and r['coefficient'] > 0
                        and all(isinstance(r.get(k), (float, int)) and math.isfinite(r[k])
                                for k in ('coherence_mean', 'trait_gain'))
                        and r['coherence_mean'] >= threshold and r['trait_gain'] > 0]
            ranked = sorted(eligible, key=lambda r: (-r['trait_gain'], -r['coherence_mean'],
                                                     r['coefficient'], r['layer']))
            choices[trait] = ranked[0] if ranked else None
        selections[f'{threshold:g}'] = choices
    for trait in config['traits']:
        settings = [choices[trait] for choices in selections.values() if choices[trait] is not None]
        if settings:
            tests.append(condition(trait, config['steering']['layers'][0], 0, 'test'))
        for setting in settings:
            cell = condition(trait, setting['layer'], setting['coefficient'], 'test')
            if cell not in tests:
                tests.append(cell)
    top_layers = {}
    for trait in config['traits']:
        by_layer = {}
        for row in summaries:
            if (row['trait'] != trait or row['coefficient'] <= 0 or row.get('trait_gain') is None
                    or not math.isfinite(row['trait_gain'])):
                continue
            key = (-row['trait_gain'], -(row.get('coherence_mean') or 0), row['coefficient'])
            previous = by_layer.get(row['layer'])
            if previous is None or key < previous[0]:
                by_layer[row['layer']] = (key, row)
        top_layers[trait] = [item[1] for item in sorted(by_layer.values(), key=lambda x: (x[0], x[1]['layer']))[:5]]
    return {'selected_by_coherence_floor': selections, 'test_conditions': tests,
            'top_five_distinct_layers_by_trait_gain_without_coherence_gate': top_layers,
            'primary_coherence_floor': config['steering']['primary_coherence_floor'],
            'rule': 'joint development layer/positive-alpha selection: mean numeric coherence >= floor; maximize positive paired trait gain; ties: higher coherence, lower alpha, lower layer',
            'non_numeric_policy': 'exclude refusal/invalid from numeric means; report all counts; never impute zero',
            'scope': 'coherence-constrained adaptation; paper B.4 fixed-alpha selection is retained separately'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['preflight', 'generate', 'score', 'test-generate', 'test-score'])
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--shard', type=int)
    args = parser.parse_args()
    require_compute()
    run = args.run
    config = load_config(run / 'config.json', allow_trait_subset=True)
    verify_run(run, config)
    cells = sweep_conditions(config)
    if args.stage == 'preflight':
        smoke(run, config)
    elif args.stage == 'generate':
        assert args.shard is not None and 0 <= args.shard < config['steering']['generation_shards']
        cells = [cell for index, cell in enumerate(cells)
                 if index % config['steering']['generation_shards'] == args.shard]
        generate_cells(run, config, cells)
    elif args.stage == 'score':
        score_cells(run, config, cells)
        summaries = development_summary(run, config, cells)
        write_json(run / 'development-summary.json', summaries)
        write_curves(run, summaries)
        write_json(run / 'selection.json', select_coherent(summaries, config))
    else:
        selection = json.loads((run / 'selection.json').read_text())
        cells = selection['test_conditions']
        if args.stage == 'test-generate':
            generate_cells(run, config, cells)
        else:
            score_cells(run, config, cells)
            result = {'selection': selection, 'by_coherence_floor': {}}
            for floor, choices in selection['selected_by_coherence_floor'].items():
                result['by_coherence_floor'][floor] = {}
                for trait, setting in choices.items():
                    if setting is None:
                        item = {'status': 'no_eligible_development_setting'}
                    else:
                        base = condition(trait, config['steering']['layers'][0], 0, 'test')
                        cell = condition(trait, setting['layer'], setting['coefficient'], 'test')
                        item = dict(cell, **summarize_pair(checked_rows(run, config, cell, 'scored'),
                                                         checked_rows(run, config, base, 'scored'), trait))
                    result['by_coherence_floor'][floor][trait] = item
            write_json(run / 'heldout-summary.json', result)
    write_json(run / f'logs/{args.stage}-{args.shard if args.shard is not None else "single"}.done.json',
               {'status': 'complete', 'stage': args.stage})


if __name__ == '__main__':
    main()
