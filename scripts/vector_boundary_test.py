"""Controlled evil-vector boundary re-extraction and paired generation test."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

from persona_repro.common import read_jsonl, write_json, require_compute


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['extract', 'generate', 'score'])
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--arm', choices=['original', 'corrected'])
    args = parser.parse_args()
    require_compute()
    run = args.run
    manifest = json.loads((run / 'manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if hashlib.sha256((run / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Frozen input/source changed: {relative}')
    config = json.loads((run / 'config.json').read_text())
    diagnostic = config['diagnostic']
    if args.stage == 'extract':
        import torch
        from persona_repro.extraction import audit_pairs
        from persona_repro.operations import extract_vectors, runtime_from_config
        extraction_config = deepcopy(config)
        extraction_config['model']['attn_implementation'] = 'eager'
        write_json(run / 'extraction_config.json', extraction_config)
        runtime = runtime_from_config(extraction_config)
        extract_vectors(run / 'inputs/evil-scored.jsonl', run / 'vectors/evil.pt', extraction_config, runtime=runtime)
        # Replay the original implementation on the same loaded model and exact
        # accepted IDs: this checks that the original payload can be reproduced.
        spec = importlib.util.spec_from_file_location('persona_repro.legacy_model', run / 'inputs/legacy_model.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        legacy = module.ModelRuntime(config['model']['id'], revision=config['model']['revision'])
        legacy.model, legacy.tokenizer, legacy.layers = runtime.model, runtime.tokenizer, runtime.layers
        accepted, _ = audit_pairs(read_jsonl(run / 'inputs/evil-scored.jsonl'), config['extraction'])
        sums = {side: torch.zeros(32, 2560) for side in ('pos', 'neg')}
        counts = {'pos': 0, 'neg': 0}
        for index, row in enumerate(accepted):
            captured = legacy.activations(row['messages'], prompt_token_ids=row['prompt_token_ids'], answer_token_ids=row['answer_token_ids'])
            sums[row['polarity']] += torch.stack([captured[layer]['response_avg'] for layer in range(1, 33)])
            counts[row['polarity']] += 1
            if (index + 1) % 10 == 0:
                print('legacy extraction replay', index + 1, flush=True)
        reproduced = sums['pos'] / counts['pos'] - sums['neg'] / counts['neg']
        old = torch.load(run / 'original_vectors/evil.pt', weights_only=True)['raw'].float()
        new = torch.load(run / 'vectors/evil.pt', weights_only=True)['raw'].float()
        def compare(a, b):
            return {'cosine': torch.nn.functional.cosine_similarity(a, b, dim=-1).tolist(),
                    'max_absolute_difference': (a - b).abs().amax(-1).tolist(),
                    'norm_relative_difference': ((a.norm(dim=-1) - b.norm(dim=-1)) / b.norm(dim=-1)).tolist()}
        metrics = {'accepted_counts': counts, 'original_replay': compare(reproduced, old),
                   'corrected_vs_original': compare(new, old), 'old_norms': old.norm(dim=-1).tolist(),
                   'corrected_norms': new.norm(dim=-1).tolist(), 'fixed_layer': 19,
                   'scope': 'same legacy scored samples, same bf16 token mean and float32 polarity accumulation; response-boundary correction only'}
        write_json(run / 'vector-comparison.json', metrics)
        torch.save({'raw': reproduced, 'unit': reproduced / reproduced.norm(dim=-1, keepdim=True)}, run / 'original_reproduced.pt')
        assert metrics['original_replay']['cosine'][18] > 0.999, metrics['original_replay']
        assert abs(metrics['original_replay']['norm_relative_difference'][18]) < 0.01
        write_json(run / 'extract.done.json', {'status': 'complete', 'accepted_pairs': counts['pos']})
    elif args.stage == 'generate':
        from persona_repro.operations import generate_file, runtime_from_config
        assert (run / 'extract.done.json').exists()
        runtime = runtime_from_config(config)
        if args.arm == 'corrected':
            generate_file(run / 'tasks/evil.jsonl', run / 'responses/baseline.jsonl', config, runtime=runtime)
        vector = run / ('original_vectors' if args.arm == 'original' else 'vectors') / 'evil.pt'
        for alpha in diagnostic['coefficients']:
            label = str(alpha).replace('.', 'p')
            generate_file(run / 'tasks/evil.jsonl', run / f'responses/{args.arm}-a{label}.jsonl', config,
                          vector_path=vector, layer=19, coefficient=alpha, runtime=runtime)
    else:
        from persona_repro.judge import score_files
        from persona_repro.e02 import summarize_pair, numeric_score
        files = [(p, run / 'scored' / p.name, None) for p in sorted((run / 'responses').glob('*.jsonl'))]
        assert len(files) == 1 + 2 * len(diagnostic['coefficients'])
        score_files(files, config)
        baseline = read_jsonl(run / 'scored/baseline.jsonl')
        def mean_score(metric):
            values = [numeric_score(row, metric) for row in baseline]
            values = [value for value in values if value is not None]
            return sum(values) / len(values) if values else None
        summary = {'baseline': {'trait_mean': mean_score('evil'), 'coherence_mean': mean_score('coherence')},
                   'arms': {}, 'design': diagnostic}
        for arm in ('original', 'corrected'):
            summary['arms'][arm] = {}
            for alpha in diagnostic['coefficients']:
                label = str(alpha).replace('.', 'p')
                rows = read_jsonl(run / f'scored/{arm}-a{label}.jsonl')
                summary['arms'][arm][str(alpha)] = summarize_pair(rows, baseline, 'evil')
        write_json(run / 'diagnostic-summary.json', summary)


if __name__ == '__main__':
    main()
