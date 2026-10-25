"""Compute-node preflight, kept separate from dry planning and unit tests."""
from __future__ import annotations
import importlib.metadata
import platform
from pathlib import Path
from .common import require_compute, write_json


def run_preflight(config):
    require_compute()
    import torch
    from .model import Steering
    from .operations import runtime_from_config
    from .training import _assistant_only_item, _find_text_linear_targets
    runtime = runtime_from_config(config)
    messages=[{'role':'user','content':'Reply with one short greeting.'}]
    before=runtime.generate(messages,temperature=0,max_new_tokens=8)
    vector=torch.ones(2560)
    with Steering(runtime.layers,16,vector,0.0,'last'):
        zero=runtime.generate(messages,temperature=0,max_new_tokens=8)
    if before['answer_token_ids'] != zero['answer_token_ids']:
        raise RuntimeError('Zero steering changed greedy generation')
    captured=runtime.activations(messages,answer='Hello.')
    if any(v['prompt_last'].shape != (2560,) or v['response_avg'].shape != (2560,) for v in captured.values()):
        raise RuntimeError('Incorrect block activation shape')
    labels=_assistant_only_item(runtime,messages+[{'role':'assistant','content':'Hello.'}],2048)
    if not any(label!=-100 for label in labels['labels']) or labels['labels'][0]!=-100:
        raise RuntimeError('Assistant loss mask is invalid')
    targets,_=_find_text_linear_targets(runtime.model,list(runtime.layers))
    if not targets:
        raise RuntimeError('No text LoRA target modules')
    result={'status':'passed','model':config['model'],'python':platform.python_version(),
            'versions':{name:importlib.metadata.version(name) for name in ('torch','transformers','peft')},
            'checks':['nonthinking_template_prefix','32_block_shapes','zero_steering_generation','assistant_loss_mask','text_lora_targets'],
            'lora_target_modules':targets,'greeting':before['answer']}
    write_json(Path(config['paths']['work'])/'preflight.json',result)
    print(result)
