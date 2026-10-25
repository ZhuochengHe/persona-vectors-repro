import json
from types import SimpleNamespace

import pytest

from persona_repro.common import generation_fingerprint, read_jsonl
from persona_repro.operations import generate_file


def test_generation_routes_positions_and_cannot_reuse_other_mode(tmp_path, monkeypatch):
    import persona_repro.model as model
    import persona_repro.operations as ops
    called = []

    class Hook:
        def __init__(self, layers, layer, vector, coefficient, positions):
            called.append(positions)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(model, 'Steering', Hook)
    monkeypatch.setattr(ops, 'load_vector', lambda *args: object())
    monkeypatch.setattr(ops, 'require_compute', lambda: None)
    runtime = SimpleNamespace(load=lambda: None, layers=[], generate=lambda *args, **kwargs: {
        'answer': 'hello', 'answer_token_ids': [1], 'prompt_token_ids': [2]})
    config = {'model': {'id': 'test', 'revision': 'test'}, 'generation': {
        'seed': 0, 'temperature': 1, 'top_p': 1, 'top_k': 0, 'repetition_penalty': 1,
        'min_new_tokens': 1, 'num_beams': 1, 'max_new_tokens': 10}}
    task = tmp_path / 'task.jsonl'
    task.write_text(json.dumps({'sample_id': 'one', 'messages': [{'role': 'user', 'content': 'hello'}]}) + '\n')
    vector = tmp_path / 'vector.pt'
    vector.write_text('test fixture')
    response = tmp_path / 'response.jsonl'
    generate_file(task, response, config, vector_path=vector, layer=12, coefficient=1, runtime=runtime)
    old_fingerprint = generation_fingerprint(config)
    config['generation']['steering_positions'] = 'all'
    assert generation_fingerprint(config) != old_fingerprint
    with pytest.raises(ValueError, match='different generation configuration'):
        generate_file(task, response, config, vector_path=vector, layer=12, coefficient=1, runtime=runtime)
    generate_file(task, tmp_path / 'all.jsonl', config, vector_path=vector, layer=12, coefficient=1, runtime=runtime)
    assert called == ['last', 'all']
    assert read_jsonl(response)[0]['steering_positions'] == 'response'
    assert read_jsonl(tmp_path / 'all.jsonl')[0]['steering_positions'] == 'all'


def test_invalid_position_fails_before_loading_model(tmp_path, monkeypatch):
    import persona_repro.operations as ops
    monkeypatch.setattr(ops, 'require_compute', lambda: None)
    with pytest.raises(ValueError, match='steering_positions'):
        generate_file(tmp_path / 'none', tmp_path / 'out', {'generation': {'steering_positions': 'prompt'}})
