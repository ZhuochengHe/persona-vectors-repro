from types import SimpleNamespace

import pytest

from persona_repro.model import locate_layers
from persona_repro.operations import load_vector, vector_shape


def test_layer_lookup_uses_the_model_geometry():
    blocks = [object() for _ in range(28)]
    model = SimpleNamespace(config=SimpleNamespace(num_hidden_layers=28),
                            model=SimpleNamespace(layers=blocks))
    assert locate_layers(model) is blocks
    with pytest.raises(ValueError, match='32'):
        locate_layers(model, 32)


def test_qwen25_vector_cannot_be_loaded_as_qwen35(tmp_path):
    import torch
    raw = torch.full((28, 3584), 2.0)
    path = tmp_path / 'evil.pt'
    torch.save({'raw': raw}, path)
    vector = load_vector(path, 20, (28, 3584))
    assert torch.equal(vector, raw[19])
    assert float(vector.norm()) > 1  # Loading must preserve the raw magnitude.
    with pytest.raises(ValueError, match='shape'):
        load_vector(path, 20)
    with pytest.raises(ValueError, match='1..28'):
        load_vector(path, 29, (28, 3584))


def test_shape_validation_rejects_invalid_config():
    assert vector_shape({'model': {'expected_layers': 28, 'expected_hidden_size': 3584}}) == (28, 3584)
    with pytest.raises(ValueError, match='geometry'):
        vector_shape({'model': {'expected_layers': True}})
