"""E01 stages reuse one model across traits without changing per-sample RNG."""
from __future__ import annotations
import argparse
from pathlib import Path
from .common import load_config,require_compute
from .model import ModelRuntime
from .operations import generate_file,extract_vectors


def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['generate','vectors']);parser.add_argument('--run',type=Path,required=True);args=parser.parse_args()
    require_compute()
    config=load_config(args.run/'config.json')
    runtime=ModelRuntime(config['model']['id'],config['model']['revision'],
        attention_implementation=config['model'].get('attn_implementation','eager'),
        require_fast_kernels=config['model'].get('require_fast_kernels',False))
    for trait in config['traits']:
        print(f'{args.stage}: {trait}',flush=True)
        if args.stage=='generate':
            generate_file(args.run/'tasks'/f'{trait}.jsonl',args.run/'responses'/f'{trait}.jsonl',config,runtime=runtime)
        else:
            extract_vectors(args.run/'scored'/f'{trait}.jsonl',args.run/'vectors'/f'{trait}.pt',config,runtime=runtime)

if __name__=='__main__':main()
