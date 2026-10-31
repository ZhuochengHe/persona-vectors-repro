"""Small-scale Qwen2.5-7B-Instruct evil extraction and fixed-layer control."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

from persona_repro.common import (generation_fingerprint, read_jsonl, require_compute,
                                  write_json, write_jsonl)
from persona_repro.operations import (extract_vectors, generate_file, load_vector,
                                     runtime_from_config, vector_shape)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_rows(run, config, name, scored=False):
    folder = 'scored' if scored else 'responses'
    rows = read_jsonl(run / folder / f'{name}.jsonl')
    tasks = {r['sample_id']: r for r in read_jsonl(run / 'tasks/eval.jsonl')}
    assert len(rows) == len(tasks) == 40 and {r['sample_id'] for r in rows} == set(tasks)
    if name == 'baseline':
        fingerprint = generation_fingerprint(config)
    else:
        alpha = float(name.removeprefix('a').replace('p', '.'))
        fingerprint = generation_fingerprint(config, vector_digest=digest(run / 'vectors/evil.pt'),
                                             layer=20, coefficient=alpha)
    for row in rows:
        assert row['generation_fingerprint'] == fingerprint
        assert row['model_id'] == config['model']['id'] and row['model_revision'] == config['model']['revision']
        assert row['messages'] == tasks[row['sample_id']]['messages']
    if scored:
        original = {r['sample_id']: r for r in checked_rows(run, config, name)}
        for row in rows:
            assert all(row[k] == original[row['sample_id']][k] for k in
                       ('answer', 'answer_token_ids', 'prompt_token_ids', 'seed', 'generation_fingerprint'))
    return rows


def preflight(run, config):
    import torch
    from persona_repro.model import Steering, generation_stop_ids, template_token_ids
    runtime = runtime_from_config(config)
    assert len(runtime.layers) == 28 and runtime.model.config.hidden_size == 3584
    assert runtime.model.config.model_type == 'qwen2'
    assert all(p.dtype == torch.bfloat16 for p in runtime.model.parameters())
    assert all(p.device.type == 'cuda' for p in runtime.model.parameters()), 'Model parameters must reside on GPU'
    assert all(b.device.type == 'cuda' for b in runtime.model.buffers()), 'Model buffers must reside on GPU'
    messages = [{'role': 'user', 'content': 'What is 2 + 2? Answer briefly.'}]
    generated = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=48)
    assert generated['answer'].strip()
    unmodified_template = template_token_ids(runtime.tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_dict=False))
    assert unmodified_template == generated['prompt_token_ids']
    vector = torch.randn(3584, generator=torch.Generator().manual_seed(123))
    vector /= vector.norm()
    for positions in ('last', 'all'):
        with Steering(runtime.layers, 20, vector, 0, positions):
            zero = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=48)
        assert generated['answer_token_ids'] == zero['answer_token_ids']
    spec = importlib.util.spec_from_file_location('upstream_control_hook', run / 'source/upstream/activation_steer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with Steering(runtime.layers, 20, vector, 1, 'last'):
        own = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=48)
    with module.ActivationSteerer(runtime.model, vector, coeff=1, layer_idx=19, positions='response'):
        upstream = runtime.generate(messages, seed=42, temperature=0, max_new_tokens=48)
    assert own['answer_token_ids'] == upstream['answer_token_ids']
    captured = runtime.activations(messages, prompt_token_ids=generated['prompt_token_ids'],
                                   answer_token_ids=generated['answer_token_ids'])
    assert len(captured) == 28
    assert all(v['response_avg'].shape == (3584,) and torch.isfinite(v['response_avg']).all()
               for v in captured.values())
    assert not any(block._forward_hooks for block in runtime.layers)
    write_json(run / 'preflight.json', {'status': 'passed', 'model': config['model'],
        'layers': 28, 'hidden_size': 3584, 'dtype': 'bfloat16', 'no_cpu_offload': True,
        'zero_hook_matches_baseline': True, 'upstream_hook_tokens_match': True,
        'chat_template_matches_without_thinking_kwarg': True,
        'stop_ids': generation_stop_ids(runtime.tokenizer, runtime.model),
        'peak_cuda_memory_allocated_bytes': torch.cuda.max_memory_allocated(),
        'sample': generated, 'backend': runtime.backend_info})


def activation_norm(run, runtime, config):
    import torch
    from persona_repro.model import generation_stop_ids, response_content_ids
    norms = []
    for row in checked_rows(run, config, 'baseline'):
        prompt = row['prompt_token_ids']
        response = response_content_ids(row['answer_token_ids'], generation_stop_ids(runtime.tokenizer, runtime.model))
        def capture(_module, _inputs, output):
            value = output[0] if isinstance(output, (tuple, list)) else output
            norms.append(float(value[0, len(prompt)-1:].detach().float().norm(dim=-1).mean()))
        handle = runtime.layers[19].register_forward_hook(capture)
        try:
            ids = torch.tensor([prompt + response], device=runtime.model.device)
            with torch.inference_mode():
                runtime.model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, logits_to_keep=1)
        finally:
            handle.remove()
    assert len(norms) == 40
    vector_norm = float(load_vector(run / 'vectors/evil.pt', 20, vector_shape(config)).float().norm())
    denominator = statistics.mean(norms)
    write_json(run / 'perturbation.json', {'layer': 20, 'raw_vector_l2': vector_norm,
        'unsteered_mean_activation_l2': denominator,
        'definition': 'Unsteered teacher-forced block output; prompt-last plus response content; each answer weighted equally',
        'by_alpha': {str(a): {'perturbation_l2': abs(a)*vector_norm,
                             'relative_perturbation': abs(a)*vector_norm/denominator}
                     for a in config['backup']['coefficients']}})


def report(run, config, summary):
    meta = json.loads((run / 'vectors/evil.json').read_text())
    norm = json.loads((run / 'perturbation.json').read_text())
    completed = ('复用既有向量，已完成200条固定第20层评估回答的生成与评分。'
                 if config['backup'].get('reused_vector_run') else
                 '已完成180条提取回答及200条固定第20层评估回答的生成与评分。')
    lines = ['\n' + completed,
             f"有效提取配对：{meta['counts']['pos']}对；第20层raw vector范数：{norm['raw_vector_l2']:.4f}。\n",
             '| α | evil均值 | coherence均值 | 重复4-gram比例 | 相对扰动 |',
             '|---:|---:|---:|---:|---:|']
    for name, item in summary['conditions'].items():
        alpha = 0 if name == 'baseline' else float(name[1:].replace('p', '.'))
        relative = norm['by_alpha'][str(float(alpha))]['relative_perturbation']
        trait = item['trait_mean']
        text = '无数值评分' if trait is None else f'{trait:.2f}'
        coherent = item['coherence_mean']
        coherence_text = '无数值评分' if coherent is None else f'{coherent:.2f}'
        lines.append(f"| {alpha:g} | {text} | {coherence_text} | {item['repetition_4gram_mean']:.1%} | {relative:.1%} |")
    eligible = [item for name,item in summary['conditions'].items() if name!='baseline'
                and item['coherence_mean'] is not None and item['coherence_mean']>=75
                and item['trait_gain'] is not None and item['trait_gain']>0]
    lines += ['\n'+('在已测系数中存在coherence≥75且trait正向提升的设置，需结合具体回答及不确定性解释。' if eligible else
              '在已测系数中没有发现coherence≥75且trait正向提升的设置；不能因此单独断言是pipeline问题。'),
              '\n这不是论文全量规模复现；Luna评分、提取有效样本数及运行设置仍是需要考虑的差异。\n']
    path = Path(config['backup']['document'])
    text = path.read_text()
    begin,end = '<!-- qwen25-results:start -->','<!-- qwen25-results:end -->'
    prefix,rest = text.split(begin);_,suffix = rest.split(end)
    path.write_text(prefix+begin+'\n'+'\n'.join(lines)+'\n'+end+suffix)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['preflight','generate-extraction','score-extraction','vectors','generate-steering','score-steering'])
    parser.add_argument('--run',type=Path,required=True)
    args = parser.parse_args();require_compute();run=args.run
    config=json.loads((run/'config.json').read_text())
    extraction=json.loads((run/'extraction-config.json').read_text())
    manifest=json.loads((run/'manifest.json').read_text())
    for path,expected in manifest['sha256'].items():
        if digest(run/path)!=expected:raise ValueError(f'Frozen backup input changed: {path}')
    if args.stage=='preflight':preflight(run,config)
    elif args.stage=='generate-extraction':
        generate_file(run/'tasks/extraction.jsonl',run/'extraction/responses.jsonl',extraction)
    elif args.stage=='score-extraction':
        from persona_repro.judge import score_files
        rows=read_jsonl(run/'extraction/responses.jsonl')
        assert len(rows)==180 and all(r['generation_fingerprint']==generation_fingerprint(extraction) for r in rows)
        score_files([(run/'extraction/responses.jsonl',run/'extraction/scored.jsonl',None)],extraction)
    elif args.stage=='vectors':
        extract_vectors(run/'extraction/scored.jsonl',run/'vectors/evil.pt',extraction)
    elif args.stage=='generate-steering':
        runtime=runtime_from_config(config)
        generate_file(run/'tasks/eval.jsonl',run/'responses/baseline.jsonl',config,runtime=runtime)
        activation_norm(run,runtime,config)
        for alpha in config['backup']['coefficients']:
            if not alpha:continue
            name='a'+str(alpha).replace('.','p')
            generate_file(run/'tasks/eval.jsonl',run/f'responses/{name}.jsonl',config,
                          vector_path=run/'vectors/evil.pt',layer=20,coefficient=alpha,runtime=runtime)
            checked_rows(run,config,name)
    else:
        from persona_repro.e02 import summarize_pair
        from persona_repro.judge import score_files
        from random_direction_control import repetition
        names=['baseline']+['a'+str(a).replace('.','p') for a in config['backup']['coefficients'] if a]
        for name in names:checked_rows(run,config,name)
        score_files([(run/f'responses/{n}.jsonl',run/f'scored/{n}.jsonl',None) for n in names],config)
        base=checked_rows(run,config,'baseline',scored=True)
        stops=set(json.loads((run/'preflight.json').read_text())['stop_ids'])
        summary={'design':config['backup'],'conditions':{}}
        for name in names:
            rows=checked_rows(run,config,name,scored=True)
            result=summarize_pair(rows,base,'evil');details=[]
            for row in rows:
                ids=row['answer_token_ids'];end=next((i for i,t in enumerate(ids) if t in stops),len(ids))
                details.append({'sample_id':row['sample_id'],'repetition_4gram':repetition(ids[:end])})
            result['repetition_4gram_mean']=statistics.mean(r['repetition_4gram'] for r in details)
            write_jsonl(run/f'metrics/{name}.jsonl',details);summary['conditions'][name]=result
        write_json(run/'summary.json',summary);report(run,config,summary)
    write_json(run/f'logs/{args.stage}.done.json',{'status':'complete','stage':args.stage})


if __name__=='__main__':main()
