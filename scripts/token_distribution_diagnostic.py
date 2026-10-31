"""Replay saved answers with KV cache and measure next-token distributions."""
import argparse
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import statistics

from persona_repro.common import read_jsonl, require_compute, write_json
from persona_repro.model import Steering, generation_stop_ids
from persona_repro.operations import load_vector, runtime_from_config, vector_shape


def distribution(logits, chosen):
    import torch
    log_z = torch.logsumexp(logits, dim=-1)
    probabilities = torch.softmax(logits, dim=-1)
    safe = torch.where(torch.isfinite(logits), logits, torch.zeros_like(logits))
    entropy = log_z - (probabilities * safe).sum()
    values = torch.topk(logits, 20).values
    threshold = values[-1]
    mass = probabilities.topk(20).values.sum()
    # HF retains ties at the kth score, so its retained mass can exceed top20.
    retained_mass = probabilities[logits >= threshold].sum()
    rank = (logits > logits[chosen]).sum() + 1
    return {'entropy_nats': float(entropy), 'top20_mass': float(mass),
            'topk20_cutoff_retained_mass': float(retained_mass),
            'top1_probability': float(probabilities.max()),
            'chosen_rank': int(rank), 'chosen_probability': float(probabilities[chosen])}


def replay(runtime, row, vector, coefficient, output):
    import torch
    from transformers.generation.logits_process import RepetitionPenaltyLogitsProcessor
    prompt = row['prompt_token_ids']
    stop_ids = generation_stop_ids(runtime.tokenizer, runtime.model)
    answer = row['answer_token_ids']
    end = next((i + 1 for i, token in enumerate(answer) if token in stop_ids), len(answer))
    answer = answer[:end]
    settings = row['effective_generation_config']
    assert settings['temperature'] == 1 and settings['top_p'] == 1
    assert settings['num_beams'] == 1
    penalty = settings['repetition_penalty']
    processor = RepetitionPenaltyLogitsProcessor(penalty) if penalty != 1 else None
    prefix = torch.tensor([prompt], device=runtime.model.device)
    next_input = prefix
    cache = None
    records = []
    context = Steering(runtime.layers, 20, vector, coefficient, 'last') if coefficient else nullcontext()
    output.parent.mkdir(parents=True, exist_ok=True)
    with context, torch.inference_mode(), output.open('w') as stream:
        for index, chosen in enumerate(answer):
            result = runtime.model(input_ids=next_input, past_key_values=cache,
                                   use_cache=True, logits_to_keep=1)
            cache = result.past_key_values
            raw = result.logits[0, -1].float()
            assert torch.isfinite(raw).all()
            adjusted = processor(prefix, raw[None, :].clone())[0] if processor else raw.clone()
            if index < settings['min_new_tokens']:
                adjusted = adjusted.clone()
                adjusted[stop_ids] = -torch.inf
            raw_stats = distribution(raw, chosen)
            adjusted_stats = distribution(adjusted, chosen)
            # Also measure the final distribution actually used for sampling.
            final = adjusted.clone()
            k = settings['top_k']
            if k:
                final[final < torch.topk(final, k).values[-1]] = -torch.inf
            record = {'index': index, 'token_id': chosen,
                      'token': runtime.tokenizer.decode([chosen]),
                      'is_stop': chosen in stop_ids,
                      'raw': raw_stats, 'before_topk': adjusted_stats,
                      'after_sampling': distribution(final, chosen)}
            records.append(record)
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
            next_input = torch.tensor([[chosen]], device=runtime.model.device)
            prefix = torch.cat((prefix, next_input), dim=1)
            del result
    assert not any(block._forward_hooks for block in runtime.layers)
    content = [r for r in records if not r['is_stop']]
    assert content
    summary = {'content_tokens': len(content), 'all_predicted_tokens': len(records)}
    for stage in ['raw', 'before_topk', 'after_sampling']:
        summary[stage] = {metric: statistics.mean(r[stage][metric] for r in content)
                          for metric in ['entropy_nats', 'top20_mass', 'topk20_cutoff_retained_mass', 'top1_probability']}
        summary[stage]['chosen_outside_top20_fraction'] = statistics.mean(
            r[stage]['chosen_rank'] > 20 for r in content)
        summary[stage]['chosen_zero_probability_count'] = sum(
            r[stage]['chosen_probability'] == 0 for r in content)
    # Early positions are comparable before generated contexts diverge strongly.
    for window, selected in [('first_token', content[:1]), ('first_50', content[:50])]:
        summary[window] = {metric: statistics.mean(r['raw'][metric] for r in selected)
                           for metric in ['entropy_nats', 'top20_mass', 'top1_probability']}
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require_compute()
    import math
    import torch
    uniform = distribution(torch.zeros(100, device='cuda'), 0)
    assert abs(uniform['entropy_nats'] - math.log(100)) < 1e-4
    assert abs(uniform['top20_mass'] - 0.2) < 1e-5
    peaked = torch.full((100,), -100.0, device='cuda')
    peaked[0] = 0
    check = distribution(peaked, 1)
    assert check['entropy_nats'] < 1e-4 and check['top20_mass'] > 0.9999
    assert check['chosen_rank'] == 2
    run = args.run
    manifest = json.loads((run / 'manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        assert hashlib.sha256((run / path).read_bytes()).hexdigest() == expected, path
    config = json.loads((run / 'config.json').read_text())
    runtime = runtime_from_config(config)
    vector = load_vector(run / 'vectors/evil.pt', 20, vector_shape(config))
    summaries = []
    for source in config['distribution_diagnostic']['sources']:
        rows = read_jsonl(run / source['path'])
        rows = [r for r in rows if r['rollout'] == 0]
        assert len(rows) == 10 and len({r['question_id'] for r in rows}) == 10
        for row in rows:
            assert row['model_id'] == config['model']['id']
            assert row['model_revision'] == config['model']['revision']
            assert row.get('coefficient', 0) == source['alpha']
            assert row['effective_generation_config']['top_k'] == source['top_k']
            assert row['effective_generation_config']['repetition_penalty'] == 1
            modes = [('unsteered', 0.0)]
            if source['alpha']:
                assert row['layer'] == 20 and row['steering_positions'] == 'response'
                modes.append(('steered', source['alpha']))
            for mode, alpha in modes:
                stem = row['sample_id'].replace(':', '-')
                output = run / 'tokens' / source['name'] / mode / (stem + '.jsonl')
                marker = output.with_suffix('.summary.json')
                if marker.exists():
                    item = json.loads(marker.read_text())
                else:
                    item = replay(runtime, row, vector, alpha, output)
                    item.update(source=source['name'], mode=mode, sample_id=row['sample_id'],
                                question_id=row['question_id'], alpha=alpha,
                                original_scores=row['scores'])
                    write_json(marker, item)
                summaries.append(item)
                print(json.dumps({'completed_replays': len(summaries), 'source': source['name'],
                                  'sample_id': row['sample_id'], 'mode': mode}), flush=True)
    aggregate = {}
    for source in config['distribution_diagnostic']['sources']:
        aggregate[source['name']] = {}
        for mode in ['unsteered', 'steered']:
            selected = [r for r in summaries if r['source'] == source['name'] and r['mode'] == mode]
            if not selected:
                continue
            metrics = {'responses': len(selected)}
            for stage in ['raw', 'before_topk', 'after_sampling', 'first_token', 'first_50']:
                metrics[stage] = {key: statistics.mean(r[stage][key] for r in selected)
                                  for key in selected[0][stage]}
            aggregate[source['name']][mode] = metrics
    write_json(run / 'summary.json', {'aggregation': 'Equal weight per saved answer, then mean over its content tokens; n=10 questions per source',
               'conditions': aggregate, 'per_response': summaries,
               'scope': 'KV-cache replay on fixed saved prefixes; unsteered replay of steered text is counterfactual, not free generation'})
    write_json(run / 'logs/distribution.done.json', {'status': 'complete', 'replays': len(summaries)})


if __name__ == '__main__':
    main()
