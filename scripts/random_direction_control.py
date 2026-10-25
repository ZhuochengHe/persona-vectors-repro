"""Paired evil steering versus three norm-matched Gaussian directions."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

from persona_repro.common import require_compute, read_jsonl, write_json, write_jsonl, generation_fingerprint


def repetition(ids, n=4):
    """Fraction of n-gram occurrences beyond the first occurrence (token IDs)."""
    count = max(0, len(ids) - n + 1)
    return 1 - len({tuple(ids[i:i+n]) for i in range(count)}) / count if count else 0.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['generate', 'score'])
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--arm', type=int, choices=range(4))
    args = p.parse_args()
    require_compute()
    run = args.run
    config = json.loads((run / 'config.json').read_text())
    manifest = json.loads((run / 'manifest.json').read_text())
    for path, digest in manifest['sha256'].items():
        if hashlib.sha256((run / path).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Frozen input/source changed: {path}')
    design = config['diagnostic']
    tasks = read_jsonl(run / 'tasks/evil.jsonl')
    assert len(tasks) == 40 and len({r['sample_id'] for r in tasks}) == 40
    assert repetition([1, 2, 3, 4, 5]) == 0
    assert repetition([1] * 8) == 0.8
    arms = ['persona'] + [f'random-{s}' for s in design['random_seeds']]
    if args.stage == 'generate':
        import torch
        from persona_repro.operations import generate_file, runtime_from_config
        assert args.arm is not None
        arm = arms[args.arm]
        payload = torch.load(run / 'vectors/persona.pt', map_location='cpu', weights_only=True)
        raw = payload['raw'].float().clone()
        ref = raw[18].clone()
        if args.arm:
            seed = design['random_seeds'][args.arm-1]
            generator = torch.Generator(device='cpu').manual_seed(seed)
            direction = torch.randn(ref.shape, generator=generator, dtype=torch.float32)
            raw[18] = direction / direction.norm() * ref.norm()
        assert torch.isfinite(raw).all()
        assert torch.isclose(raw[18].norm(), ref.norm(), rtol=1e-6)
        path = run / f'vectors/{arm}.pt'
        if args.arm:
            torch.save({'raw': raw, 'unit': raw / raw.norm(dim=-1, keepdim=True)}, path)
        write_json(run / f'vectors/{arm}.json', {
            'layer': 19, 'random_seed': None if not args.arm else seed,
            'raw_vector_l2': float(raw[18].norm()), 'reference_l2': float(ref.norm()),
            'cosine_with_persona': float(torch.nn.functional.cosine_similarity(raw[18], ref, dim=0)),
            'distribution': 'persona' if not args.arm else 'isotropic Gaussian; scaled once to persona L2; not orthogonalized',
            'injection': 'raw alpha * vector into block output, final prefill and each decode position'})
        runtime = runtime_from_config(config)
        for alpha in design['coefficients']:
            label = str(alpha).replace('.', 'p')
            generate_file(run / 'tasks/evil.jsonl', run / f'responses/{arm}-a{label}.jsonl',
                          config, vector_path=path, layer=19, coefficient=alpha, runtime=runtime)
        assert not any(block._forward_hooks for block in runtime.layers)
        write_json(run / f'logs/{arm}.done.json', {'status': 'complete', 'responses': 160})
    else:
        from persona_repro.judge import score_files
        from persona_repro.e02 import summarize_pair
        expected = ['baseline'] + [f'{arm}-a{str(a).replace(".", "p")}' for arm in arms for a in design['coefficients']]
        base = read_jsonl(run / 'responses/baseline.jsonl')
        for name in expected:
            rows = read_jsonl(run / f'responses/{name}.jsonl')
            assert len(rows) == 40 and {r['sample_id'] for r in rows} == {r['sample_id'] for r in tasks}
            if name == 'baseline':
                fingerprint = generation_fingerprint(config)
            else:
                arm, alpha_label = name.rsplit('-a', 1)
                vector_digest = hashlib.sha256((run / f'vectors/{arm}.pt').read_bytes()).hexdigest()
                fingerprint = generation_fingerprint(config, vector_digest=vector_digest, layer=19,
                                                     coefficient=float(alpha_label.replace('p', '.')))
            assert all(r['generation_fingerprint'] == fingerprint for r in rows)
        score_files([(run / f'responses/{n}.jsonl', run / f'scored/{n}.jsonl', None) for n in expected], config)
        baseline = read_jsonl(run / 'scored/baseline.jsonl')
        summary = {'design': design, 'conditions': {}, 'repetition_definition':
                   'Repeated token 4-gram occurrences / all token 4-gram occurrences; content before first EOS only'}
        stops = set(design['stop_ids'])
        for name in expected:
            rows = read_jsonl(run / f'scored/{name}.jsonl')
            metrics = summarize_pair(rows, baseline, 'evil')
            details = []
            for row in rows:
                ids = row['answer_token_ids']
                end = next((i for i, token in enumerate(ids) if token in stops), len(ids))
                details.append({'sample_id': row['sample_id'], 'question_id': row['question_id'],
                    'content_tokens': end, 'repeated_4gram_fraction': repetition(ids[:end]),
                    'hit_token_limit_without_eos': end == len(ids) == config['generation']['max_new_tokens']})
            metrics.update(repeated_4gram_fraction_mean=statistics.mean(r['repeated_4gram_fraction'] for r in details),
                           hit_token_limit_without_eos=sum(r['hit_token_limit_without_eos'] for r in details),
                           content_tokens_mean=statistics.mean(r['content_tokens'] for r in details))
            write_jsonl(run / f'metrics/{name}.jsonl', details)
            summary['conditions'][name] = metrics
        write_json(run / 'summary.json', summary)
        write_json(run / 'logs/score.done.json', {'status': 'complete', 'responses': 680})


if __name__ == '__main__':
    main()
