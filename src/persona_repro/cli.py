"""Explicit stage CLI. Imports do not load models or require credentials."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .common import REPO, TRAITS, load_config, read_jsonl, write_json, write_jsonl, question_splits, require_compute


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=REPO/'configs/reproduction.json')
    sub = parser.add_subparsers(dest='command',required=True)
    plan = sub.add_parser('plan',help='Print manifest without compute, network or writing')
    plan.add_argument('--output',type=Path)
    tasks = sub.add_parser('tasks',help='Materialize extraction/evaluation/monitoring task JSONL')
    tasks.add_argument('kind',choices=['extract','eval','monitor'])
    tasks.add_argument('--trait',choices=TRAITS,required=True)
    tasks.add_argument('--split',choices=['dev','test'],default='test')
    tasks.add_argument('--rollouts',type=int)
    tasks.add_argument('--output',type=Path,required=True)
    data = sub.add_parser('prepare-data')
    data.add_argument('--dataset-root',type=Path,required=True)
    data.add_argument('--output',type=Path,required=True)
    data.add_argument('--train-size',type=int)
    download = sub.add_parser('fetch-data',help='Download fixed upstream archive and extract selected categories to scratch')
    download.add_argument('--output',type=Path,required=True)
    dataset_tasks = sub.add_parser('dataset-tasks',help='Annotate teacher-forced training answers for E19 projections')
    dataset_tasks.add_argument('--input',type=Path,required=True)
    dataset_tasks.add_argument('--trait',choices=TRAITS,required=True)
    dataset_tasks.add_argument('--category',required=True)
    dataset_tasks.add_argument('--version',required=True)
    dataset_tasks.add_argument('--output',type=Path,required=True)
    natural = sub.add_parser('natural-tasks',help='Build base natural-response tasks from one selected training subset')
    natural.add_argument('--input',type=Path,required=True)
    natural.add_argument('--trait',choices=TRAITS,required=True)
    natural.add_argument('--output',type=Path,required=True)
    analyze = sub.add_parser('analyze')
    analyze.add_argument('experiment',choices=['E06','E09','E19'])
    analyze.add_argument('--input',type=Path,nargs='+',required=True,help='E06 merged rows; E09 fine merged rows; E19 dataset projections')
    analyze.add_argument('--base',type=Path,nargs='+',help='Merged base score and projection rows for E09; scored base rows for E19')
    analyze.add_argument('--natural',type=Path,nargs='+')
    analyze.add_argument('--finetuned',type=Path,nargs='+',help='E19 finetuned behavior rows')
    analyze.add_argument('--checkpoint-map',type=Path,help='Map checkpoint_id to category/version for E19')
    analyze.add_argument('--output',type=Path,required=True)
    sub.add_parser('preflight',help='Load model on compute node and check template, hooks, zero steering and labels')
    mprep = sub.add_parser('prepare-mmlu')
    mprep.add_argument('--output',type=Path,required=True)
    for command in ('generate','score','vectors','project','mmlu'):
        child = sub.add_parser(command)
        child.add_argument('--input',type=Path,required=True)
        child.add_argument('--output',type=Path,required=True)
        if command in ('generate','project','mmlu'):
            child.add_argument('--adapter',type=Path)
            child.add_argument('--vector',type=Path)
            child.add_argument('--layer',type=int)
            child.add_argument('--coefficient',type=float,default=0.0)
        if command=='project':
            child.add_argument('--mode',choices=['prompt_last','response_avg'],default='response_avg')
    train = sub.add_parser('train')
    train.add_argument('--train-file',type=Path,required=True)
    train.add_argument('--dev-file',type=Path,required=True)
    train.add_argument('--output',type=Path,required=True)
    train.add_argument('--vector',type=Path)
    train.add_argument('--layer',type=int)
    train.add_argument('--coefficient',type=float,default=0.0)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    upstream = Path(config['paths']['upstream'])
    if args.command=='plan':
        from .planning import build_plan
        plan = build_plan(config)
        if args.output: write_json(args.output,plan)
        else: print(json.dumps(plan,ensure_ascii=False,indent=2))
    elif args.command=='tasks':
        from .inference_tasks import build_extraction_tasks,build_evaluation_tasks,build_monitoring_tasks
        default_rollouts = config['extraction']['rollouts'] if args.kind=='extract' else config['generation']['rollouts']
        rollouts = args.rollouts if args.rollouts is not None else default_rollouts
        indices = question_splits(upstream,config['data']['seed'])[args.trait][args.split]
        if args.kind=='eval':
            indices = config.get('evaluation', {}).get('question_splits', {}).get(args.trait, {}).get(args.split, indices)
        if args.kind=='extract':
            rows=build_extraction_tasks(upstream,args.trait,rollouts,
                question_ids=config['extraction']['question_ids'],
                instruction_ids=config['extraction']['instruction_ids'])
        elif args.kind=='eval': rows=build_evaluation_tasks(upstream,args.trait,indices,rollouts)
        else: rows=build_monitoring_tasks(upstream,args.trait,indices,Path(config['paths']['monitoring_prompts']),rollouts)
        write_jsonl(args.output,rows)
        print(json.dumps({'output':str(args.output),'records':len(rows)}))
    elif args.command=='dataset-tasks':
        rows=[]
        for row in read_jsonl(args.input):
            messages=row['messages']
            if messages[-1]['role']!='assistant': raise ValueError('Training row must end with assistant')
            rows.append(dict(row,trait=args.trait,category=args.category,version=args.version,question=next(m['content'] for m in reversed(messages[:-1]) if m['role']=='user')))
        write_jsonl(args.output,rows)
    elif args.command=='natural-tasks':
        rows=[]
        for row in read_jsonl(args.input):
            messages=row['messages']
            if messages[-1]['role']=='assistant': messages=messages[:-1]
            value=dict(row, messages=messages,trait=args.trait,question=next(m['content'] for m in reversed(messages) if m['role']=='user'))
            value['sample_id']=f"natural:{args.trait}:{row['question_group_id']}"
            rows.append(value)
        # Reuse only exact prompt matches, not merely normalized question groups.
        unique={}
        for row in rows:
            key=row['sample_id']
            if key in unique and unique[key]['messages'] != row['messages']: raise ValueError('Changed prompt under one question group')
            unique[key]=row
        write_jsonl(args.output,unique.values())
    elif args.command=='analyze':
        from .reporting import report_e06,report_e09,report_e19
        def read_many(paths):
            return [row for path in (paths or []) for row in read_jsonl(path)]
        rows=read_many(args.input)
        if args.experiment=='E06': result=report_e06(rows)
        elif args.experiment=='E09':
            if not args.base: parser.error('E09 requires --base')
            result=report_e09(read_many(args.base),rows)
        else:
            if not args.base or not args.natural or not args.finetuned or not args.checkpoint_map: parser.error('E19 requires --base --natural --finetuned --checkpoint-map')
            mapping=json.loads(args.checkpoint_map.read_text())
            fine=read_many(args.finetuned)
            for row in fine:
                if row['checkpoint_id'] not in mapping: raise ValueError('Unmapped checkpoint_id')
                row.update(mapping[row['checkpoint_id']])
            result=report_e19(rows,read_many(args.natural),read_many(args.base),fine)
        write_json(args.output,result)
    elif args.command=='prepare-data':
        require_compute()
        from .data import prepare_subsets
        print(json.dumps(prepare_subsets(args.dataset_root,args.output,train_size=args.train_size or config['data']['train_size'],dev_size=config['data']['dev_size'],seed=config['data']['seed'],categories=config['data']['categories']),indent=2))
    elif args.command=='fetch-data':
        from .setup import fetch_data
        fetch_data(config,args.output)
    elif args.command=='preflight':
        from .preflight import run_preflight
        run_preflight(config)
    elif args.command=='prepare-mmlu':
        from .mmlu import prepare_mmlu
        print(json.dumps(prepare_mmlu(config,args.output),indent=2))
    elif args.command=='generate':
        from .operations import generate_file
        generate_file(args.input,args.output,config,adapter_path=args.adapter,vector_path=args.vector,layer=args.layer,coefficient=args.coefficient)
    elif args.command=='score':
        from .judge import score_file
        score_file(args.input,args.output,config)
    elif args.command=='vectors':
        from .operations import extract_vectors
        extract_vectors(args.input,args.output,config)
    elif args.command=='project':
        from .operations import project_file
        if not args.vector or not args.layer: parser.error('project requires --vector and --layer')
        project_file(args.input,args.output,config,args.vector,args.layer,adapter_path=args.adapter,mode=args.mode)
    elif args.command=='mmlu':
        from .mmlu import evaluate_mmlu
        evaluate_mmlu(config,args.input,args.output,adapter_path=args.adapter,vector_path=args.vector,layer=args.layer,coefficient=args.coefficient)
    elif args.command=='train':
        from .training import train_adapter
        train_adapter(config,args.train_file,args.dev_file,args.output,vector_path=args.vector,layer=args.layer,coefficient=args.coefficient)

if __name__=='__main__':
    main()
