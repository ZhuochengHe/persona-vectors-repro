"""Streaming experiment operations composed by the CLI."""
from __future__ import annotations
from contextlib import nullcontext
import hashlib
import json
import time
from pathlib import Path
from .common import read_jsonl, stable_id, write_json, write_jsonl, require_compute, generation_fingerprint, GENERATION_PROTOCOL


def runtime_from_config(config, adapter_path=None):
    from .model import ModelRuntime
    return ModelRuntime(config['model']['id'], config['model']['revision'], adapter_path,
        attention_implementation=config['model'].get('attn_implementation','eager'),
        require_fast_kernels=config['model'].get('require_fast_kernels',False)).load()


def vector_shape(config):
    model = config['model']
    shape = (model.get('expected_layers', 32), model.get('expected_hidden_size', 2560))
    if any(isinstance(x, bool) or not isinstance(x, int) or x <= 0 for x in shape):
        raise ValueError('Expected positive integer model geometry')
    return shape


def generate_file(input_path, output_path, config, *, adapter_path=None, vector_path=None, layer=None, coefficient=0.0, runtime=None):
    require_compute()
    from .model import Steering
    steering_positions = config['generation'].get('steering_positions', 'response')
    if steering_positions not in ('response', 'all'):
        raise ValueError('Inference steering_positions must be response or all')
    runtime = runtime if runtime is not None else runtime_from_config(config, adapter_path)
    vector = load_vector(vector_path, layer, vector_shape(config)) if vector_path else None
    if coefficient and vector is None:
        raise ValueError('Nonzero coefficient requires vector and layer')
    if vector is not None:
        runtime.load()  # Shared runtimes are lazy; hooks need initialized blocks.
    vector_digest = hashlib.sha256(Path(vector_path).read_bytes()).hexdigest() if vector_path else None
    fingerprint = generation_fingerprint(config, adapter_path, vector_digest, layer, coefficient)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    completed = {}
    if destination.exists():
        for row in read_jsonl(destination):
            if row['generation_fingerprint'] != fingerprint:
                raise ValueError('Existing output uses a different generation configuration')
            if row['sample_id'] in completed:
                raise ValueError('Duplicate completed sample_id')
            completed[row['sample_id']] = row
    settings = config['generation']
    with destination.open('a') as handle:
        seen = set()
        for row in read_jsonl(input_path):
            key = row['sample_id']
            if key in seen:
                raise ValueError('Duplicate input sample_id')
            seen.add(key)
            seed_key = row.get('sampling_seed_id', key)
            seed = (settings['seed'] + int(hashlib.sha256(seed_key.encode()).hexdigest()[:8], 16)) % 2**32
            if key in completed:
                if completed[key]['messages'] != row['messages']:
                    raise ValueError('Sample ID reused with changed messages')
                if completed[key].get('seed') != seed:
                    raise ValueError('Existing output uses a different per-sample random seed')
                continue
            positions = 'last' if steering_positions == 'response' else 'all'
            context = Steering(runtime.layers, layer, vector, coefficient, positions) if vector is not None else nullcontext()
            started = time.perf_counter()
            with context:
                generated = runtime.generate(row['messages'], seed=seed, temperature=settings['temperature'],
                                             top_p=settings['top_p'], top_k=settings['top_k'],
                                             repetition_penalty=settings['repetition_penalty'],
                                             min_new_tokens=settings['min_new_tokens'], num_beams=settings['num_beams'],
                                             max_new_tokens=settings['max_new_tokens'])
            value = dict(row, **generated, generation_seconds=time.perf_counter()-started,
                         generation_fingerprint=fingerprint, generation_protocol=GENERATION_PROTOCOL,
                         model_id=config['model']['id'], model_revision=config['model']['revision'],
                         checkpoint_id=str(adapter_path or 'base'), layer=layer, coefficient=coefficient,
                         steering_positions=steering_positions)
            value['seed'] = seed
            handle.write(json.dumps(value, ensure_ascii=False) + '\n')
            handle.flush()
            if len(seen) == 1 or len(seen) % 10 == 0:
                print(json.dumps({'completed':len(seen), 'sample_id':key,
                    'last_generation_seconds':value['generation_seconds'],
                    'last_response_tokens':len(value['answer_token_ids'])}), flush=True)


def load_vector(path, layer, expected_shape=(32, 2560)):
    import torch
    if layer is None or not 1 <= layer <= expected_shape[0]:
        raise ValueError(f'Vector layer must be 1..{expected_shape[0]}')
    payload = torch.load(path, map_location='cpu', weights_only=True)
    raw = payload['raw']
    if tuple(raw.shape) != tuple(expected_shape) or not torch.isfinite(raw).all():
        raise ValueError(f'Expected finite raw persona vectors with shape {expected_shape}')
    if (raw.norm(dim=-1) <= 0).any():
        raise ValueError('Persona vector contains a zero direction')
    return raw[layer - 1]  # Payload contains blocks only, no embedding row.


def extract_vectors(scored_path, output_path, config, *, runtime=None):
    require_compute()
    import torch
    rows = read_jsonl(scored_path)
    source_digest = hashlib.sha256(Path(scored_path).read_bytes()).hexdigest()
    legacy = config['extraction'].get('allow_legacy_reextract', False)
    if not isinstance(legacy, bool):
        raise ValueError('allow_legacy_reextract must be boolean')
    if legacy and config['extraction'].get('legacy_source_sha256') != source_digest:
        raise ValueError('Legacy re-extraction requires the exact pinned scored-source SHA256')
    from .extraction import audit_pairs
    accepted, audit = audit_pairs(rows, config['extraction'])
    trait = audit['trait']
    output_path = Path(output_path)
    audit_path = output_path.with_suffix('.audit.json')
    # Write the rejection evidence even when no valid pair survives.
    write_json(audit_path, audit)
    if not accepted:
        raise ValueError('No positive/negative pairs survived the fixed repository-style filter')
    for row in rows:
        if row.get('model_id') != config['model']['id'] or row.get('model_revision') != config['model']['revision']:
            raise ValueError('Extraction response model identity differs from configured base model')
        if row.get('checkpoint_id') != 'base' or row.get('coefficient') != 0:
            raise ValueError('E01 requires unsteered base-model responses')
        if not legacy and row.get('generation_fingerprint') != generation_fingerprint(config):
            raise ValueError('E01 response generation protocol differs; legacy reuse requires explicit pinned-source opt-in')
    runtime = runtime if runtime is not None else runtime_from_config(config)
    layers, hidden_size = vector_shape(config)
    sums = {side: torch.zeros(layers, hidden_size) for side in ('pos','neg')}
    counts = {side:0 for side in sums}
    for row in accepted:
        if runtime.encode_conversation(row['messages'])['input_ids'] != row['prompt_token_ids']:
            raise ValueError('Extraction tokenized prompt does not match the current chat template')
        if legacy:
            from .model import generation_stop_ids, response_content_ids
            content = response_content_ids(row['answer_token_ids'], generation_stop_ids(runtime.tokenizer, runtime.model))
            if runtime.tokenizer.decode(content, skip_special_tokens=True).strip() != row['answer'].strip():
                raise ValueError('Legacy score includes text outside the first assistant turn; re-score before extraction')
        captured = runtime.activations(row['messages'], prompt_token_ids=row['prompt_token_ids'], answer_token_ids=row['answer_token_ids'])
        vectors = torch.stack([captured[l]['response_avg'] for l in range(1, layers + 1)])
        if not torch.isfinite(vectors).all():
            raise ValueError('Non-finite activation means')
        sums[row['polarity']] += vectors
        counts[row['polarity']] += 1
    raw = sums['pos']/counts['pos'] - sums['neg']/counts['neg']
    norms = raw.norm(dim=-1, keepdim=True)
    if (norms <= 0).any():
        raise ValueError('Zero persona vector')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'raw':raw, 'unit':raw/norms}, output_path)
    asset = Path(config['paths']['upstream']) / f'data_generation/trait_data_extract/{trait}.json'
    audit['status'] = 'vectors_extracted_pending_setting_review'
    audit['vector_norms'] = norms.squeeze(-1).tolist()
    write_json(audit_path, audit)
    write_json(output_path.with_suffix('.json'), {'trait':trait, 'layers':list(range(1, layers + 1)),
               'hook':'block_output_pre_final_norm', 'counts':counts, 'filter':config['extraction'],
               'model':config['model'], 'input':str(scored_path), 'scoring_mode':'codex_direct_score',
               'judge_model': config['judge']['model'], 'audit_file': str(audit_path),
               'source_commit':config.get('upstream_commit', 'b8e0f044fe2410a6fad579f38324f03f13b4e917'),
               'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
               'scored_input_sha256':hashlib.sha256(Path(scored_path).read_bytes()).hexdigest(),
               'mask':'actual generated response IDs before first assistant-turn/model EOS; prompt, terminator and following tokens excluded',
               'extraction_protocol':'response-before-first-eos-v2',
               'source_generation_mode':'explicit_legacy_boundary_isolation' if legacy else GENERATION_PROTOCOL,
               'arithmetic':'response token mean in model dtype; polarity accumulation and difference in float32',
               'accepted_sample_ids':[row['sample_id'] for row in accepted],
               'runtime_backend':getattr(runtime,'backend_info',None),
               'weighting':'equal response means within polarity', 'raw_vector_norms':norms.squeeze(-1).tolist()})


def project_file(input_path, output_path, config, vector_path, layer, *, adapter_path=None, mode='response_avg'):
    require_compute()
    if mode not in ('prompt_last','response_avg'):
        raise ValueError('Invalid projection mode')
    runtime = runtime_from_config(config, adapter_path)
    vector = load_vector(vector_path, layer, vector_shape(config)).float()
    vector /= vector.norm()
    vector_id = hashlib.sha256(Path(vector_path).read_bytes()).hexdigest()
    def results():
        for row in read_jsonl(input_path):
            # Prompt-only monitoring intentionally never passes the future response.
            if mode == 'prompt_last':
                messages = row['messages']
                if messages[-1]['role'] == 'assistant':
                    messages = messages[:-1]
                captured = runtime.activations(messages, selected_layers=[layer])
            elif 'prompt_token_ids' in row and 'answer_token_ids' in row:
                captured = runtime.activations(row['messages'], prompt_token_ids=row['prompt_token_ids'], answer_token_ids=row['answer_token_ids'], selected_layers=[layer])
            else:
                messages = row['messages']
                answer = row.get('answer')
                if messages[-1]['role'] == 'assistant':
                    answer, messages = messages[-1]['content'], messages[:-1]
                if answer is None:
                    raise ValueError('Response projection requires an answer')
                captured = runtime.activations(messages, answer, selected_layers=[layer])
            value = captured[layer][mode]
            yield dict(row, projection=float((value*vector).sum()), projection_mode=mode,
                       projection_model_id=config['model']['id'], projection_revision=config['model']['revision'],
                       projection_checkpoint_id=str(adapter_path or 'base'), vector_id=vector_id, layer=layer)
    write_jsonl(output_path, results())
