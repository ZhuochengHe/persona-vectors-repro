"""Read-only inventory of downloaded training records and sampled token lengths."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random

from .common import load_config, require_compute, write_json
from .data import VERSIONS, _canonical, _question_messages


def quantiles(values):
    values=sorted(values)
    return {str(q):values[round((len(values)-1)*q/100)] for q in (0,50,90,95,99,100)} if values else {}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('configs/reproduction.json'))
    parser.add_argument('--dataset-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--length-sample',type=int,default=200)
    args=parser.parse_args();require_compute();config=load_config(args.config)
    result={'dataset_root':str(args.dataset_root.resolve()),'categories':{},
            'length_sampling':'seed 0; at most 200 unique question groups per file; deterministic representative per group',
            'max_length_checked':2048,'model':config['model'],'format_errors':0}
    samples={}
    for category in config['data']['categories']:
        info={'versions':{}};sets={}
        for version in VERSIONS:
            path=args.dataset_root/category/f'{version}.jsonl'
            raw=path.read_bytes();groups=defaultdict(list);full_records=set();stats=Counter();patterns=Counter();keys=Counter();bad=[]
            lengths=[]
            for line_number,line in enumerate(raw.decode().splitlines(),1):
                if not line.strip():continue
                stats['rows']+=1
                try:
                    row=json.loads(line)
                    if not isinstance(row,dict):raise ValueError('record is not an object')
                    keys.update(row.keys());messages=row.get('messages')
                    if not isinstance(messages,list) or not messages:raise ValueError('missing messages')
                    if any(not isinstance(m,dict) or m.get('role') not in ('system','user','assistant') or not isinstance(m.get('content'),str) for m in messages):raise ValueError('invalid role/content')
                    if messages[-1]['role']!='assistant':raise ValueError('last message is not assistant')
                    if not any(m['role']=='user' for m in messages):raise ValueError('no user question')
                    if not messages[-1]['content'].strip():raise ValueError('empty final assistant answer')
                    prompt=_question_messages(messages,path,line_number)
                    group=hashlib.sha256(_canonical(prompt).encode()).hexdigest()
                    canonical=_canonical(row)
                    full_records.add(hashlib.sha256(canonical.encode()).hexdigest())
                    groups[group].append((canonical,row))
                    patterns['/'.join(m['role'] for m in messages)]+=1
                    lengths.append(len(messages[-1]['content']))
                except (ValueError,TypeError,KeyError) as exc:
                    stats['format_errors']+=1
                    if len(bad)<10:bad.append({'line':line_number,'reason':str(exc)})
            group_ids=set(groups);sets[version]=group_ids
            selected=random.Random(0).sample(sorted(group_ids),min(args.length_sample,len(group_ids)))
            samples[category,version]=[min(groups[g],key=lambda x:x[0])[1] for g in selected]
            valid=stats['rows']-stats['format_errors']
            info['versions'][version]={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                'rows':stats['rows'],'valid_rows':valid,'format_errors':stats['format_errors'],
                'unique_question_groups':len(groups),'extra_rows_in_question_groups':valid-len(groups),
                'exact_duplicate_records':valid-len(full_records),'question_multiplicity':dict(sorted(Counter(map(len,groups.values())).items())),
                'message_patterns':dict(patterns),'record_fields':dict(keys),'assistant_char_length_quantiles':quantiles(lengths),
                'format_error_examples':bad}
            result['format_errors']+=stats['format_errors']
            print(json.dumps({'category':category,'version':version,'rows':stats['rows'],'groups':len(groups),'errors':stats['format_errors']}),flush=True)
        shared=set.intersection(*sets.values());union=set.union(*sets.values())
        info.update(shared_question_groups=len(shared),union_question_groups=len(union),
                    missing_groups_by_version={v:len(union-s) for v,s in sets.items()},
                    supports_1000_train_100_dev=len(shared)>=1100)
        result['categories'][category]=info
    write_json(args.output,result)  # Structural results survive a tokenizer/environment failure.
    from transformers import AutoTokenizer
    from .model import ModelRuntime
    from .training import _assistant_only_item
    runtime=ModelRuntime(config['model']['id'],config['model']['revision'])
    runtime.tokenizer=AutoTokenizer.from_pretrained(config['model']['id'],revision=config['model']['revision'])
    runtime.tokenizer.padding_side='right'
    for (category,version),rows in samples.items():
        lengths=[];prompt_lengths=[];errors=[];truncated=0;lost_targets=0;target_tokens=[]
        for index,row in enumerate(rows):
            messages=row['messages']
            try:
                encoded=runtime.encode_conversation(messages[:-1],answer=messages[-1]['content'])
                lengths.append(len(encoded['input_ids']));prompt_lengths.append(encoded['response_start'])
                truncated+=len(encoded['input_ids'])>2048
                item=_assistant_only_item(runtime,messages,2048)
                target_tokens.append(sum(x!=-100 for x in item['labels']))
            except ValueError as exc:
                if 'no assistant target tokens' in str(exc):lost_targets+=1
                if len(errors)<10:errors.append({'sample_index':index,'reason':str(exc)})
        result['categories'][category]['versions'][version]['token_length_sample']={
            'sample_size':len(rows),'encoded_count':len(lengths),'sequence_length_quantiles':quantiles(lengths),
            'prompt_length_quantiles':quantiles(prompt_lengths),'assistant_target_tokens_after_truncation':quantiles(target_tokens),
            'sequences_over_2048':truncated,'fraction_over_2048':truncated/len(rows) if rows else None,
            'zero_assistant_targets_after_truncation':lost_targets,'encoding_error_examples':errors}
        write_json(args.output,result)
        print(json.dumps({'category':category,'version':version,'sample':len(rows),'over_2048':truncated,'lost_targets':lost_targets,'encoding_errors_shown':len(errors)}),flush=True)
    result['status']='complete';write_json(args.output,result)


if __name__=='__main__':main()
