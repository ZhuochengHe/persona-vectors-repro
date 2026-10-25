"""Measure raw steering magnitude relative to unsteered block activations."""
import json
import statistics
import sys
from pathlib import Path

from persona_repro.common import require_compute, read_jsonl, write_json
from persona_repro.model import ModelRuntime, generation_stop_ids, response_content_ids


def main():
    require_compute()
    import torch
    run, parent = map(Path, sys.argv[1:3])
    config = json.loads((parent / 'config.json').read_text())
    model = config['model']
    runtime = ModelRuntime(model['id'], revision=model['revision'], attention_implementation='sdpa').load()
    layers = (18, 19, 20, 24)
    pooled = {layer: [] for layer in layers}
    means = {layer: [] for layer in layers}
    rows = read_jsonl(parent / 'responses/baseline.jsonl')
    stop_ids = generation_stop_ids(runtime.tokenizer, runtime.model)
    for index, row in enumerate(rows):
        prompt = row['prompt_token_ids']
        response = response_content_ids(row['answer_token_ids'], stop_ids)
        assert runtime.encode_conversation(row['messages'])['input_ids'] == prompt
        handles = []
        for layer in layers:
            def capture(_module, _inputs, output, layer=layer):
                value = output[0] if isinstance(output, (tuple, list)) else output
                # These are the positions that predict the first response token
                # and subsequent tokens, excluding a generated EOS as model input.
                norms = value[0, len(prompt)-1:].detach().float().norm(dim=-1).cpu().tolist()
                pooled[layer].extend(norms)
                means[layer].append(statistics.mean(norms))
            handles.append(runtime.layers[layer-1].register_forward_hook(capture))
        try:
            ids = torch.tensor([prompt + response], device=runtime.model.device)
            with torch.inference_mode():
                runtime.model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, logits_to_keep=1)
        finally:
            for handle in handles:
                handle.remove()
        print('activation norm samples', index + 1, '/', len(rows), flush=True)
    vector_paths = {'original': parent / 'original_vectors/evil.pt', 'boundary_corrected': parent / 'vectors/evil.pt'}
    fresh_pointer = Path(config['paths']['work']) / 'active_e01_fresh.txt'
    if fresh_pointer.exists():
        fresh = Path(fresh_pointer.read_text().strip()) / 'vectors/evil.pt'
        if fresh.exists():
            vector_paths['fresh_e01'] = fresh
    vectors = {name: torch.load(path, map_location='cpu', weights_only=True)['raw'].float().norm(dim=-1)
               for name, path in vector_paths.items()}
    result = {'model': model, 'baseline_samples': len(rows), 'runtime_backend': runtime.backend_info,
              'definition': 'unsteered teacher-forced block output; prompt-last plus response content positions; each response weighted equally for primary denominator; also report token-weighted denominator',
              'layers': {}}
    for layer in layers:
        denominator = statistics.mean(means[layer])
        result['layers'][str(layer)] = {'one_based_layer': layer,
            'layer_type': runtime.model.config.text_config.layer_types[layer-1],
            'mean_activation_l2_equal_response_weight': denominator,
            'mean_activation_l2_token_weight': statistics.mean(pooled[layer]),
            'positions': len(pooled[layer]), 'vectors': {}}
        for name, norms in vectors.items():
            norm = float(norms[layer-1])
            result['layers'][str(layer)]['vectors'][name] = {'raw_vector_l2': norm,
                'coefficients': {str(a): {'perturbation_l2': a * norm, 'relative_perturbation': a * norm / denominator}
                                 for a in (0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 5.0)}}
    write_json(run / 'result.json', result)


if __name__ == '__main__':
    main()
