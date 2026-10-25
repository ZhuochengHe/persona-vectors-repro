"""Pure task builders for the upstream persona extraction and evaluation assets.

This module deliberately has no model, network, or third-party dependencies. It
turns the checked-in upstream JSON assets into stable generation task records;
generation, judging, and activation capture belong to the shared runtime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TRAIT_FILES = {
    "evil": "evil",
    "sycophantic": "sycophantic",
    "hallucinating": "hallucinating",
}


def _validate_trait(trait: str) -> str:
    if trait not in TRAIT_FILES:
        raise ValueError(
            f"unsupported trait {trait!r}; choose one of {', '.join(TRAIT_FILES)}"
        )
    return trait


def _validate_rollouts(rollouts: int) -> int:
    if isinstance(rollouts, bool) or not isinstance(rollouts, int) or rollouts < 1:
        raise ValueError("rollouts must be a positive integer")
    return rollouts


def _load_trait_asset(upstream_dir: Path, kind: str, trait: str) -> dict[str, Any]:
    path = Path(upstream_dir) / "data_generation" / f"trait_data_{kind}" / f"{TRAIT_FILES[trait]}.json"
    try:
        with path.open(encoding="utf-8") as stream:
            asset = json.load(stream)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"missing upstream {kind} asset: {path}") from exc
    if not isinstance(asset, dict) or not isinstance(asset.get("questions"), list):
        raise ValueError(f"invalid upstream trait asset: {path}")
    if not all(isinstance(question, str) and question for question in asset["questions"]):
        raise ValueError(f"asset questions must be non-empty strings: {path}")
    return asset


def _question_indices(question_count: int, split_question_ids: list[int]) -> list[int]:
    if not isinstance(split_question_ids, list):
        raise TypeError("split_question_ids must be a list of zero-based question IDs")
    if any(isinstance(index, bool) or not isinstance(index, int) for index in split_question_ids):
        raise TypeError("question IDs must be integers")
    if len(set(split_question_ids)) != len(split_question_ids):
        raise ValueError("split_question_ids must not contain duplicates")
    if any(index < 0 or index >= question_count for index in split_question_ids):
        raise ValueError(f"question IDs must be in [0, {question_count})")
    return split_question_ids


def build_extraction_tasks(
    upstream_dir: Path, trait: str, rollouts: int = 10, *,
    question_ids: list[int] | None = None,
    instruction_ids: list[int] | None = None,
) -> list[dict[str, Any]]:
    """Build paired positive/negative extraction generations.

    ``question_id`` and ``instruction_id`` are zero-based indices into the
    original JSON asset. ``pair_id`` uniquely identifies one question,
    instruction pair, and rollout, and is shared by its positive and negative
    records. The returned records are ordered by question, pair, polarity, rollout.
    """
    trait = _validate_trait(trait)
    rollouts = _validate_rollouts(rollouts)
    asset = _load_trait_asset(upstream_dir, "extract", trait)
    instructions = asset.get("instruction")
    if not isinstance(instructions, list) or not instructions:
        raise ValueError(f"extract asset for {trait!r} has no instruction pairs")
    selected_questions = _question_indices(len(asset['questions']),
        list(range(len(asset['questions']))) if question_ids is None else question_ids)
    selected_instructions = _question_indices(len(instructions),
        list(range(len(instructions))) if instruction_ids is None else instruction_ids)
    if not selected_questions or not selected_instructions:
        raise ValueError('Extraction question and instruction selections cannot be empty')

    tasks: list[dict[str, Any]] = []
    for question_id in selected_questions:
        question = asset['questions'][question_id]
        for pair_id in selected_instructions:
            pair = instructions[pair_id]
            if not isinstance(pair, dict) or not all(
                isinstance(pair.get(polarity), str) and pair[polarity]
                for polarity in ("pos", "neg")
            ):
                raise ValueError(f"invalid instruction pair {pair_id} in {trait!r} asset")
            for polarity in ("pos", "neg"):
                instruction_id = pair_id
                instruction = pair[polarity]
                assistant_name = trait if polarity == "pos" else "helpful"
                article = "an" if assistant_name[0].lower() in "aeiou" else "a"
                system_prompt = f"You are {article} {assistant_name} assistant. {instruction}"
                for rollout in range(rollouts):
                    sample_id = f"extract:{trait}:q{question_id:03d}:i{instruction_id:02d}:{polarity}:r{rollout:03d}"
                    tasks.append(
                        {
                            "sample_id": sample_id,
                            "question_id": question_id,
                            "trait": trait,
                            "question": question,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": question},
                            ],
                            "rollout": rollout,
                            "pair_id": f"extract:{trait}:q{question_id}:i{instruction_id}:r{rollout}",
                            "polarity": polarity,
                            "instruction_id": instruction_id,
                        }
                    )
    return tasks


def build_evaluation_tasks(
    upstream_dir: Path,
    trait: str,
    split_question_ids: list[int],
    rollouts: int = 10,
    system_prompt: str | None = None,
) -> list[dict[str, Any]]:
    """Build generations from the upstream evaluation questions.

    ``system_prompt`` is an optional complete override used for conditions such
    as neutral prompting or steering; absent it, only the user question is sent.
    """
    trait = _validate_trait(trait)
    rollouts = _validate_rollouts(rollouts)
    if system_prompt is not None and not isinstance(system_prompt, str):
        raise TypeError("system_prompt must be a string or None")
    asset = _load_trait_asset(upstream_dir, "eval", trait)
    indices = _question_indices(len(asset["questions"]), split_question_ids)

    tasks: list[dict[str, Any]] = []
    for question_id in indices:
        question = asset["questions"][question_id]
        for rollout in range(rollouts):
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": question})
            tasks.append(
                {
                    "sample_id": f"eval:{trait}:q{question_id:03d}:r{rollout:03d}",
                    "question_id": question_id,
                    "trait": trait,
                    "question": question,
                    "messages": messages,
                    "rollout": rollout,
                }
            )
    return tasks


def build_monitoring_tasks(
    upstream_dir: Path,
    trait: str,
    split_question_ids: list[int],
    monitoring_path: Path,
    rollouts: int = 10,
) -> list[dict[str, Any]]:
    """Build the E06 8-condition system-prompt monitoring task matrix."""
    trait = _validate_trait(trait)
    rollouts = _validate_rollouts(rollouts)
    asset = _load_trait_asset(upstream_dir, "eval", trait)
    indices = _question_indices(len(asset["questions"]), split_question_ids)
    try:
        with Path(monitoring_path).open(encoding="utf-8") as stream:
            monitoring = json.load(stream)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"missing monitoring prompt asset: {monitoring_path}") from exc
    conditions = monitoring.get("traits", {}).get(trait) if isinstance(monitoring, dict) else None
    if not isinstance(conditions, list) or len(conditions) != 8:
        raise ValueError(f"monitoring asset must provide exactly 8 conditions for {trait!r}")

    tasks: list[dict[str, Any]] = []
    for condition in conditions:
        if not isinstance(condition, dict):
            raise ValueError(f"invalid monitoring condition for {trait!r}")
        prompt_id = condition.get("prompt_id")
        prompt = condition.get("system_prompt")
        if not isinstance(prompt_id, str) or not prompt_id or not isinstance(prompt, str) or not prompt:
            raise ValueError(f"monitoring conditions need prompt_id and system_prompt for {trait!r}")
        for question_id in indices:
            question = asset["questions"][question_id]
            for rollout in range(rollouts):
                tasks.append(
                    {
                        "sample_id": f"monitor:{trait}:{prompt_id}:q{question_id:03d}:r{rollout:03d}",
                        "sampling_seed_id": f"monitor:{trait}:q{question_id:03d}:r{rollout:03d}",
                        "question_id": question_id,
                        "trait": trait,
                        "question": question,
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": question},
                        ],
                        "rollout": rollout,
                        "prompt_id": prompt_id,
                    }
                )
    return tasks
