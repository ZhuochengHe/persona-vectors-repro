"""Fixed-alpha E02 layer sweeps: maximize trait score, report coherence separately."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil

from .common import load_config, read_jsonl, require_compute, stable_id, write_json, generation_fingerprint
from .e02 import (checked_rows, condition, development_summary, digest, generate_cells,
                  score_cells, smoke, summarize_pair, tasks_for, verify_run)


def sweep_conditions(config):
    return [cell for trait in config['traits'] for cell in (
        [condition(trait, config['steering']['layers'][0], 0)] +
        [condition(trait, layer, alpha) for alpha in config['steering']['coefficients']
         for layer in config['steering']['layers']])]


def select_fixed_alpha(summaries, config):
    by_alpha = {}
    for alpha in config['steering']['coefficients']:
        by_alpha[f'{alpha:g}'] = {}
        for trait in config['traits']:
            candidates = [r for r in summaries if r['trait']==trait and
                          r['coefficient']==alpha and r['trait_mean'] is not None]
            # Paper B.4: same alpha, highest absolute trait score. No coherence/gain gate.
            ranked = sorted(candidates, key=lambda r: (-r['trait_mean'], r['layer']))
            by_alpha[f'{alpha:g}'][trait] = ranked[0] if ranked else None
    primary = by_alpha[f"{config['steering']['primary_alpha']:g}"]
    tests = []
    for trait in config['traits']:
        settings = [by_alpha[f'{alpha:g}'][trait] for alpha in config['steering']['coefficients']]
        if any(setting is not None for setting in settings):
            tests.append(condition(trait, config['steering']['layers'][0], 0, 'test'))
            tests.extend(condition(trait, s['layer'], s['coefficient'], 'test') for s in settings if s is not None)
    return {'selected':primary,'selected_by_alpha':by_alpha,'test_conditions':tests,
            'primary_alpha':config['steering']['primary_alpha'],
            'rule':'per fixed alpha, maximize development mean numeric trait score; tie: lower layer',
            'coherence_policy':'report only; never exclude layers',
            'primary_alpha_policy':'fixed at 1 before supplemental results; paper does not specify unique selection alpha',
            'non_numeric_policy':'refusal/invalid excluded explicitly; report numeric counts, no zero imputation'}


def reuse_conditions(run, config, cells):
    source = Path(config['reuse']['e02_run'])
    original = load_config(source/'config.json')
    for field in ('model','generation'):
        if original[field] != config[field]:
            raise ValueError(f'E02 reuse differs in {field}')
    if original['judge']['model'] != config['judge']['model']:
        raise ValueError('E02 reused judge differs')
    traits={cell['trait'] for cell in cells}
    label=next(iter(traits)) if len(traits)==1 else 'all'
    record=run/'reuse'/f'{label}.json'
    reused = json.loads(record.read_text()) if record.exists() else {}
    for cell in cells:
        for folder in ('responses','scored'):
            origin = source/folder/f"{cell['id']}.jsonl"
            target = run/folder/origin.name
            if target.exists() or not origin.exists():
                continue
            if digest(source/'vectors'/f"{cell['trait']}.pt") != digest(run/'vectors'/f"{cell['trait']}.pt"):
                raise ValueError('Reused E01 vector differs')
            expected = generation_fingerprint(config, vector_digest=digest(run/'vectors'/f"{cell['trait']}.pt"),
                                              layer=cell['layer'],coefficient=cell['coefficient'])
            rows = read_jsonl(origin)
            if any(row['generation_fingerprint'] != expected for row in rows):
                raise ValueError('Reused generation fingerprint differs')
            shutil.copy2(origin,target)
            checked_rows(run,config,cell,folder)
            reused[f'{folder}/{origin.name}']={'source':str(origin),'sha256':digest(origin),'rows':len(rows)}
    write_json(record,reused)


def generate_pending(run, config, cells):
    reuse_conditions(run,config,cells)
    pending=[]
    for cell in cells:
        path=run/'responses'/f"{cell['id']}.jsonl"
        if path.exists() and len(read_jsonl(path))==len(tasks_for(config,cell['trait'],cell['split'])):
            checked_rows(run,config,cell,'responses')
        else:
            pending.append(cell)
    generate_cells(run,config,pending)


def score_pending(run, config, cells):
    reuse_conditions(run,config,cells)
    pending=[]
    for cell in cells:
        if (run/'scored'/f"{cell['id']}.jsonl").exists():
            checked_rows(run,config,cell,'scored')
        else:
            pending.append(cell)
    score_cells(run,config,pending)


def write_curves(run, summaries):
    fields=['trait','layer','coefficient','responses','trait_mean','coherence_mean',
            'trait_gain','coherence_change','paired_numeric_trait_responses','truncated_responses']
    with (run/'layer-curves.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,extrasaction='ignore')
        writer.writeheader();writer.writerows(summaries)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['smoke','generate','score','test-generate','test-score'])
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--trait',choices=['evil','sycophantic','hallucinating'])
    args=parser.parse_args();require_compute();run=args.run
    config=load_config(run/'config.json');verify_run(run,config)
    cells=sweep_conditions(config)
    if args.trait:
        if args.stage!='generate':raise ValueError('Trait-sharded execution is only valid for generation')
        cells=[cell for cell in cells if cell['trait']==args.trait]
    if args.stage=='smoke':smoke(run,config)
    elif args.stage=='generate':generate_pending(run,config,cells)
    elif args.stage=='score':
        score_pending(run,config,cells)
        summaries=development_summary(run,config,cells)
        write_json(run/'development-summary.json',summaries);write_curves(run,summaries)
        write_json(run/'selection.json',select_fixed_alpha(summaries,config))
    else:
        selection=json.loads((run/'selection.json').read_text());cells=selection['test_conditions']
        if args.stage=='test-generate':generate_pending(run,config,cells)
        else:
            score_pending(run,config,cells);results={}
            for trait in config['traits']:
                subset=[c for c in cells if c['trait']==trait]
                if not subset:
                    results[trait]={'status':'no_numeric_development_trait_scores'};continue
                baseline=checked_rows(run,config,subset[0],'scored')
                results[trait]={'primary_alpha':selection['primary_alpha'],'by_alpha':{}}
                for cell in subset[1:]:
                    rows=checked_rows(run,config,cell,'scored')
                    results[trait]['by_alpha'][f"{cell['coefficient']:g}"]=dict(cell,**summarize_pair(rows,baseline,trait))
            write_json(run/'heldout-summary.json',results)
    print(json.dumps({'stage':args.stage,'status':'complete'}),flush=True)


if __name__=='__main__':main()
