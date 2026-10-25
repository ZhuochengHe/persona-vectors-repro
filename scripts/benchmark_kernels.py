"""Compare isolated acceleration backends on compute, not an experiment rerun."""
import argparse
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import sys
import time
import types

from persona_repro.common import load_config,require_compute
from persona_repro.model import ModelRuntime, Steering


def bindings(function):
    seen=set();found=set()
    def visit(value):
        if not isinstance(value,types.FunctionType) or id(value) in seen:return
        seen.add(id(value))
        module=getattr(value,'__module__','')
        if module.startswith(('fla.','causal_conv1d.')):found.add(module+'.'+value.__name__)
        visit(getattr(value,'__wrapped__',None))
        for cell in value.__closure__ or ():
            try:visit(cell.cell_contents)
            except ValueError:pass
    visit(function)
    return sorted(found)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['reference','sdpa','accelerated']);parser.add_argument('--config',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    require_compute()
    config=load_config(args.config)
    os.environ.setdefault('XDG_CACHE_HOME',str(Path(config['paths']['work'])/'cache'))
    os.environ.setdefault('CUDA_CACHE_PATH',str(Path(config['paths']['work'])/'cache/cuda'))
    import torch
    if args.mode=='accelerated':
        from fla.ops.gated_delta_rule import chunk_gated_delta_rule, fused_recurrent_gated_delta_rule
    from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen
    attention='eager' if args.mode=='reference' else 'sdpa'
    runtime=ModelRuntime(config['model']['id'],config['model']['revision'],attention_implementation=attention,
        require_fast_kernels=args.mode=='accelerated').load()
    kernel_bindings={name:bindings(getattr(qwen,name)) for name in ['causal_conv1d_fn','causal_conv1d_update','torch_chunk_gated_delta_rule','torch_recurrent_gated_delta_rule']}
    if args.mode=='accelerated' and any(not values for values in kernel_bindings.values()):
        raise RuntimeError(f'Acceleration packages did not bind all four functions: {kernel_bindings}')
    messages=[{'role':'user','content':'Write a long numbered list counting upwards from one. Continue until you have written at least one hundred numbers.'}]
    runtime.generate(messages,temperature=0,min_new_tokens=16,max_new_tokens=16)
    timings=[];result=None
    for _ in range(2):
        torch.cuda.synchronize();start=time.perf_counter()
        result=runtime.generate(messages,temperature=0,min_new_tokens=64,max_new_tokens=64)
        torch.cuda.synchronize();timings.append(time.perf_counter()-start)
    activations=runtime.activations(messages,answer='1. One\n2. Two\n3. Three')
    encoded=runtime.encode_conversation(messages)
    ids=torch.tensor([encoded['input_ids']],device=runtime.model.device)
    with torch.inference_mode():logits=runtime.model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=1).logits[0,-1].float().cpu()
    tensors={'activations':torch.stack([activations[layer]['response_avg'] for layer in range(1,33)]),'logits':logits}
    args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/f'{args.mode}.pt';torch.save(tensors,target)
    metrics={'mode':args.mode,'attention_implementation':attention,'timings_seconds':timings,'tokens_per_second':64/min(timings),
             'generated_ids':result['answer_token_ids'],'bindings':kernel_bindings,'gpu':torch.cuda.get_device_name(),
             'versions':{name:importlib.metadata.version(name) for name in ['torch','transformers','triton','fla-core','flash-linear-attention','causal-conv1d'] if args.mode=='accelerated' or name in ['torch','transformers','triton']}}
    if args.mode!='reference':
        reference=torch.load(args.output/'reference.pt',weights_only=True)
        delta=(logits-reference['logits']).abs()
        cos=torch.nn.functional.cosine_similarity(tensors['activations'],reference['activations'],dim=-1)
        metrics.update(logit_max_absolute_difference=float(delta.max()),logit_mean_absolute_difference=float(delta.mean()),
                       min_layer_activation_cosine=float(cos.min()),same_next_token=int(logits.argmax())==int(reference['logits'].argmax()))
        refmetrics=json.loads((args.output/'reference.json').read_text())
        metrics['speedup']=metrics['tokens_per_second']/refmetrics['tokens_per_second']
        metrics['exact_greedy_sequence_match']=metrics['generated_ids']==refmetrics['generated_ids']
        # A small backward pass checks that function-level kernels still work
        # with residual hooks; it is not an E11 training experiment.
        runtime.model.requires_grad_(False)
        weight=runtime.layers[0].mlp.up_proj.weight
        weight.requires_grad_(True)
        runtime.model.train()
        with Steering(runtime.layers,16,torch.ones(2560),.01,'all'):
            loss=runtime.model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=1).logits[0,-1].float().square().mean()
            loss.backward()
        metrics['hook_backward_finite']=bool(weight.grad is not None and torch.isfinite(weight.grad).all() and weight.grad.abs().sum()>0)
        runtime.model.eval()
        # Numerical agreement is checked on identical forced inputs, not on
        # independently sampled sequences that may legitimately branch.
        metrics['numerical_check_passed']=bool(metrics['same_next_token'] and cos.min()>.999 and torch.allclose(logits,reference['logits'],atol=.15,rtol=.02) and metrics['hook_backward_finite'])
        import pytest
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        test_status=pytest.main(['-q',str(Path(__file__).resolve().parents[1]/'tests')])
        metrics['regression_tests_passed']=int(test_status)==0
    (args.output/f'{args.mode}.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps(metrics,indent=2),flush=True)
    if args.mode!='reference' and not (metrics['numerical_check_passed'] and metrics['regression_tests_passed']):
        raise RuntimeError('Accelerated backend failed numerical or regression checks')

if __name__=='__main__':main()
