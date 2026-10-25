"""Refresh E06 at paper-rule E02 layers, reusing unsteered monitoring data."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil

from .common import load_config, read_jsonl, require_compute, write_json, write_jsonl
from .e02 import digest
from .e06 import (analyze_trait, prompt_projections, selected_layers, smoke,
                  tasks_for, validate_responses, verify_run)


def layer_sets(run, config):
    primary=selected_layers(run,config)  # Checks successful E02 completion, then freezes its selection hash.
    parent=Path(config['monitoring']['e02_run'])
    choices=json.loads((parent/'selection.json').read_text())
    by_alpha={a:{trait:s['layer'] for trait,s in settings.items() if s is not None}
              for a,settings in choices['selected_by_alpha'].items()}
    return primary,by_alpha


def reuse_monitoring(run,config):
    source=Path(config['reuse']['e06_run']);old=load_config(source/'config.json')
    for field in ('model','generation'):
        if old[field]!=config[field]:raise ValueError(f'E06 reuse differs in {field}')
    if old['monitoring']['question_ids']!=config['monitoring']['question_ids']:
        raise ValueError('E06 monitoring question IDs changed')
    if old['judge']['model']!=config['judge']['model'] or digest(old['paths']['monitoring_prompts'])!=digest(config['paths']['monitoring_prompts']):
        raise ValueError('E06 judge or monitoring prompts changed')
    reused={}
    for trait in config['traits']:
        if digest(source/'vectors'/f'{trait}.pt')!=digest(run/'vectors'/f'{trait}.pt'):
            raise ValueError('E06 monitoring vector changed')
        for folder in ('responses','scored','projections'):
            origin=source/folder/f'{trait}.jsonl';target=run/folder/origin.name
            if origin.exists():
                if not target.exists():shutil.copy2(origin,target)
                reused[f'{folder}/{origin.name}']={'source':str(origin),'sha256':digest(origin)}
    write_json(run/'reuse.json',reused)


def checked_projections(run,config,trait):
    rows=read_jsonl(run/'projections'/f'{trait}.jsonl')
    values={(r['prompt_id'],r['question_id']):r for r in rows}
    expected={(r['prompt_id'],r['question_id']):r for r in tasks_for(config,trait)}
    if len(rows)!=len(values) or set(values)!=set(expected):
        raise ValueError('E06 reused projection coverage differs')
    for key,row in values.items():
        if row['messages']!=expected[key]['messages'] or row['vector_id']!=digest(run/'vectors'/f'{trait}.pt') or len(row['all_layer_projections'])!=32:
            raise ValueError('E06 reused projection identity differs')
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['smoke','generate','score'])
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();require_compute();run=args.run
    config=load_config(run/'config.json');verify_run(run,config)
    if args.stage=='smoke':smoke(run,config);return
    primary,by_alpha=layer_sets(run,config);reuse_monitoring(run,config)
    active={trait for settings in by_alpha.values() for trait in settings}
    if args.stage=='generate':
        from .model import ModelRuntime
        from .operations import generate_file
        runtime=ModelRuntime(config['model']['id'],config['model']['revision'],
            attention_implementation=config['model']['attn_implementation'],
            require_fast_kernels=config['model']['require_fast_kernels'])
        for trait in config['traits']:
            if trait not in active:continue
            response=run/'responses'/f'{trait}.jsonl'
            if response.exists() and len(read_jsonl(response))==len(tasks_for(config,trait)):
                validate_responses(run,config,trait);checked_projections(run,config,trait)
                print(json.dumps({'trait':trait,'responses':'reused'}),flush=True);continue
            prompt_projections(run,config,trait,runtime)
            generate_file(run/'tasks'/f'{trait}.jsonl',response,config,runtime=runtime)
            validate_responses(run,config,trait)
    else:
        from .judge import score_files
        files=[]
        for trait in config['traits']:
            if trait not in active:continue
            validate_responses(run,config,trait)
            if not (run/'scored'/f'{trait}.jsonl').exists():
                files.append((run/'responses'/f'{trait}.jsonl',run/'scored'/f'{trait}.jsonl',('trait',)))
        score_files(files,config)
        summary={'primary_alpha':1,'traits':{},'sensitivity_by_alpha':{},'skipped':primary['skipped']}
        for trait in config['traits']:
            if trait not in active:continue
            validate_responses(run,config,trait)
            rows=validate_responses(run,config,trait,'scored')
            projections=checked_projections(run,config,trait)
            reports={}
            for a,settings in by_alpha.items():
                if trait not in settings:continue
                layer=settings[trait]
                if layer not in reports:
                    result,merged=analyze_trait(rows,projections,layer,trait)
                    reports[layer]=result
                    write_jsonl(run/'merged'/f'{trait}-l{layer:02d}.jsonl',merged)
                    write_json(run/'results'/f'{trait}-l{layer:02d}.json',result)
                summary['sensitivity_by_alpha'].setdefault(a,{})[trait]=reports[layer]
                if a=='1':summary['traits'][trait]=reports[layer]
        write_json(run/'summary.json',summary)
    print(json.dumps({'stage':args.stage,'status':'complete'}),flush=True)


if __name__=='__main__':main()
