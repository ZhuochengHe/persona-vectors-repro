"""MMLU subset selection and full-option likelihood under shared steering hooks."""
from __future__ import annotations
from contextlib import nullcontext
import json
from pathlib import Path
import random
from .common import require_compute, read_jsonl, write_json, write_jsonl


def prepare_mmlu(config: dict, output_path: Path) -> dict:
    require_compute()
    from datasets import load_dataset
    options = config['mmlu']
    dataset = load_dataset(options['dataset'], 'all', split='test', revision=options['revision'])
    groups = {}
    for index, row in enumerate(dataset):
        groups.setdefault(row['subject'], []).append(dict(row, sample_id=f'mmlu:{row["subject"]}:{index}'))
    target = options['subset_size']
    if not 0 < target <= len(dataset):
        raise ValueError('Invalid MMLU subset size')
    rng = random.Random(options['seed'])
    for rows in groups.values():
        rng.shuffle(rows)
    # Round robin subjects for a balanced, deterministic fixed subset.
    selected = []
    while len(selected) < target:
        for subject in sorted(groups):
            if groups[subject] and len(selected) < target:
                selected.append(groups[subject].pop())
    write_jsonl(output_path, selected)
    metadata = dict(options, dataset_fingerprint=dataset._fingerprint, n=len(selected), subjects=len(groups))
    write_json(output_path.with_suffix('.manifest.json'), metadata)
    return metadata


def evaluate_mmlu(config, input_path, output_path, *, adapter_path=None, vector_path=None, layer=None, coefficient=0.0):
    require_compute()
    import torch
    from .model import Steering
    from .operations import runtime_from_config, load_vector
    runtime = runtime_from_config(config, adapter_path)
    vector = load_vector(vector_path, layer) if vector_path else None
    if coefficient and vector is None:
        raise ValueError('Nonzero MMLU steering requires vector and layer')
    records = []
    for row in read_jsonl(input_path):
        question = row['question'] + '\n' + '\n'.join(f'{chr(65+i)}. {choice}' for i,choice in enumerate(row['choices'])) + '\nAnswer with the correct letter only.'
        messages = [{'role':'user','content':question}]
        prompt = runtime.encode_conversation(messages)['input_ids']
        scores = []
        for option in 'ABCD':
            # Tokenize the complete option; never assume it is one token.
            completion = runtime.tokenizer.encode(option, add_special_tokens=False)
            if not completion:
                raise ValueError('Empty MMLU option tokenization')
            ids = torch.tensor([prompt + completion], device=runtime.model.device)
            # Match autoregressive response steering: final prompt position onward.
            if vector is not None:
                def suffix_hook(_module, _args, output):
                    value = output[0] if isinstance(output,(tuple,list)) else output
                    changed = value.clone()
                    changed[:,len(prompt)-1:,:] += coefficient*vector.to(value.device,value.dtype)
                    return (changed,*output[1:]) if isinstance(output,tuple) else [changed,*output[1:]] if isinstance(output,list) else changed
                handle = runtime.layers[layer-1].register_forward_hook(suffix_hook)
            else:
                handle = None
            try:
                with torch.inference_mode():
                    logits = runtime.model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False).logits
                    values = logits[0,len(prompt)-1:len(prompt)+len(completion)-1].float().log_softmax(-1)
                    likelihood = sum(float(values[i,token]) for i,token in enumerate(completion))
                    scores.append(likelihood)
            finally:
                if handle:
                    handle.remove()
        prediction = max(range(4), key=scores.__getitem__)
        records.append(dict(sample_id=row['sample_id'], subject=row['subject'], scores=scores,
                            prediction=prediction, answer=row['answer'], correct=prediction==row['answer'],
                            checkpoint_id=str(adapter_path or 'base'), coefficient=coefficient, layer=layer))
    if not records:
        raise ValueError('Empty MMLU subset')
    write_jsonl(output_path, records)
    write_json(Path(output_path).with_suffix('.summary.json'), {'n':len(records), 'accuracy':sum(x['correct'] for x in records)/len(records),
               'scope':'fixed MMLU subset, 0-shot, complete-letter likelihood', 'model':config['model']})
