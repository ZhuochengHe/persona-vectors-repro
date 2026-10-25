"""Focused CPU-only tests for training preprocessing and target discovery."""

from pathlib import Path

import pytest
import torch
from torch import nn

from src.persona_repro.training import (
    _assistant_only_item,
    _ensure_output_is_empty,
    _find_text_linear_targets,
    _validate_disjoint_question_groups,
)


class ToyRuntime:
    def encode_conversation(self, messages, answer=None):
        prefix = [10, 11]
        if answer is None:
            return {"input_ids": prefix, "attention_mask": [1, 1], "response_start": 2}
        target = [20, 21]
        return {
            "input_ids": prefix + target,
            "attention_mask": [1, 1, 1, 1],
            "response_start": len(prefix),
        }


def test_assistant_only_mask_excludes_prompt_and_keeps_assistant_tokens():
    item = _assistant_only_item(
        ToyRuntime(),
        [
            {"role": "user", "content": "question"},
            {"role": "assistant", "content": "answer"},
        ],
        max_length=16,
    )

    assert item["input_ids"] == [10, 11, 20, 21]
    assert item["labels"] == [-100, -100, 20, 21]
    assert item["attention_mask"] == [1, 1, 1, 1]


def test_target_discovery_uses_exact_text_layer_names_with_vision_collision():
    class Block(nn.Module):
        def __init__(self):
            super().__init__()
            self.q_proj = nn.Linear(4, 4)
            self.delta_proj = nn.Linear(4, 4)

    class ToyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = nn.ModuleList([Block()])
            self.vision = nn.Module()
            self.vision.q_proj = nn.Linear(4, 4)

    model = ToyModel()
    exact_targets, suffixes = _find_text_linear_targets(model, list(model.layers))

    assert exact_targets == ["layers.0.delta_proj", "layers.0.q_proj"]
    assert suffixes == ["delta_proj", "q_proj"]
    assert "vision.q_proj" not in exact_targets


def test_question_group_leakage_is_rejected():
    with pytest.raises(ValueError, match="leakage"):
        _validate_disjoint_question_groups(
            [{"question_group_id": "group-a"}], [{"question_group_id": "group-a"}]
        )


def test_question_group_ids_may_be_omitted_or_disjoint():
    _validate_disjoint_question_groups([{"messages": []}], [{"messages": []}])
    _validate_disjoint_question_groups(
        [{"question_group_id": 1}], [{"question_group_id": 2}]
    )


def test_output_directory_must_be_new_or_empty(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    _ensure_output_is_empty(empty)

    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "old_adapter.bin").touch()
    with pytest.raises(FileExistsError, match="new or empty"):
        _ensure_output_is_empty(occupied)
