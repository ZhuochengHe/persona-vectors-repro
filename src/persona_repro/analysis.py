"""Strict, dependency-free analysis helpers for E09 and E19 result tables.

The functions consume tidy dictionaries so the runtime can persist JSONL/CSV
without binding these calculations to one storage layer.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable, Sequence


def pearson_correlation(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Return Pearson r, or None for fewer than two points or zero variance."""
    if len(x) != len(y):
        raise ValueError(f"correlation inputs differ in length ({len(x)} != {len(y)})")
    if len(x) < 2:
        return None
    xs, ys = [float(value) for value in x], [float(value) for value in y]
    if not all(math.isfinite(value) for value in xs + ys):
        raise ValueError("correlation inputs must be finite")
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    dx, dy = [value - mean_x for value in xs], [value - mean_y for value in ys]
    sum_x, sum_y = sum(value * value for value in dx), sum(value * value for value in dy)
    if sum_x == 0.0 or sum_y == 0.0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / math.sqrt(sum_x * sum_y)


def group_demeaned_correlation(
    x: Sequence[float], y: Sequence[float], groups: Sequence[Any]
) -> float | None:
    """Pearson r after subtracting each group's mean from both variables."""
    if not (len(x) == len(y) == len(groups)):
        raise ValueError("x, y, and groups must have equal lengths")
    if not x:
        return None
    xs, ys = [float(value) for value in x], [float(value) for value in y]
    if not all(math.isfinite(value) for value in xs + ys):
        raise ValueError("correlation inputs must be finite")
    grouped_x: dict[Any, list[int]] = defaultdict(list)
    for index, group in enumerate(groups):
        grouped_x[group].append(index)
    demeaned_x = [0.0] * len(xs)
    demeaned_y = [0.0] * len(ys)
    for indices in grouped_x.values():
        mean_x = sum(xs[index] for index in indices) / len(indices)
        mean_y = sum(ys[index] for index in indices) / len(indices)
        for index in indices:
            demeaned_x[index] = xs[index] - mean_x
            demeaned_y[index] = ys[index] - mean_y
    return pearson_correlation(demeaned_x, demeaned_y)


def _finite_number(row: dict[str, Any], field: str) -> float:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number; got {value!r}")
    return float(value)


def _unique_index(
    rows: Iterable[dict[str, Any]], keys: tuple[str, ...], label: str
) -> dict[tuple[Any, ...], dict[str, Any]]:
    indexed: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row_number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise TypeError(f"{label} row {row_number} must be an object")
        key = tuple(row.get(field) for field in keys)
        if any(value is None or value == "" for value in key):
            raise ValueError(f"{label} row {row_number} lacks one of keys {keys}")
        if key in indexed:
            raise ValueError(f"duplicate {label} key {key!r}")
        indexed[key] = row
    return indexed


def _require_same_keys(
    left: dict[tuple[Any, ...], Any], right: dict[tuple[Any, ...], Any], left_label: str, right_label: str
) -> None:
    missing = sorted(set(left) - set(right), key=repr)
    extra = sorted(set(right) - set(left), key=repr)
    if missing or extra:
        raise ValueError(
            f"strict join mismatch for {left_label} and {right_label}: "
            f"missing={missing[:5]!r} (count={len(missing)}), "
            f"extra={extra[:5]!r} (count={len(extra)})"
        )


def analyze_e09(
    projection_rows: Iterable[dict[str, Any]], behavior_rows: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    """Join E09 activation and score tables, then summarize by trait/checkpoint.

    Projection rows require ``trait``, ``checkpoint_id``, ``prompt_id``,
    ``base_projection`` and ``finetuned_projection``. Behavior rows require the
    same join keys plus ``base_score`` and ``finetuned_score``. Every key must
    match exactly; changes are finetuned minus base. Correlations are computed
    across checkpoint summaries independently per trait.
    """
    keys = ("trait", "checkpoint_id", "prompt_id")
    projections = _unique_index(projection_rows, keys, "E09 projection")
    behaviors = _unique_index(behavior_rows, keys, "E09 behavior")
    _require_same_keys(projections, behaviors, "E09 projection", "E09 behavior")
    grouped: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"projection_shift": [], "behavior_change": []}
    )
    joined = []
    for key in sorted(projections, key=repr):
        trait, checkpoint_id, prompt_id = key
        activation, behavior = projections[key], behaviors[key]
        projection_shift = _finite_number(activation, "finetuned_projection") - _finite_number(activation, "base_projection")
        behavior_change = _finite_number(behavior, "finetuned_score") - _finite_number(behavior, "base_score")
        grouped[(trait, checkpoint_id)]["projection_shift"].append(projection_shift)
        grouped[(trait, checkpoint_id)]["behavior_change"].append(behavior_change)
        joined.append({
            "trait": trait,
            "checkpoint_id": checkpoint_id,
            "prompt_id": prompt_id,
            "projection_shift": projection_shift,
            "behavior_change": behavior_change,
        })
    summaries = []
    for (trait, checkpoint_id), values in sorted(grouped.items()):
        count = len(values["projection_shift"])
        summaries.append({
            "trait": trait,
            "checkpoint_id": checkpoint_id,
            "prompt_count": count,
            "mean_projection_shift": sum(values["projection_shift"]) / count,
            "mean_behavior_change": sum(values["behavior_change"]) / count,
        })
    correlations = []
    by_trait: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in summaries:
        by_trait[row["trait"]].append(row)
    for trait, rows in sorted(by_trait.items()):
        correlations.append({
            "trait": trait,
            "checkpoint_count": len(rows),
            "pearson_r": pearson_correlation(
                [row["mean_projection_shift"] for row in rows],
                [row["mean_behavior_change"] for row in rows],
            ),
        })
    return {"joined_rows": joined, "checkpoint_summaries": summaries, "correlations": correlations}


def analyze_e19(
    dataset_projection_rows: Iterable[dict[str, Any]],
    natural_projection_rows: Iterable[dict[str, Any]],
    behavior_rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Compute E19 training-vs-natural projection differences and behavior link.

    Dataset rows require ``category``, ``version``, ``trait``, ``model_id``,
    ``vector_id``, ``prompt_id``, ``dataset_projection``. Natural rows require
    the same model/vector/trait/prompt keys and ``natural_projection``; those
    natural prompts are reused across dataset versions. Behavior rows require
    ``category``, ``version``, ``trait``, ``base_score`` and
    ``finetuned_score``. The dataset/natural prompt-key sets must match for
    each model/vector/trait, with no duplicate prompt records. Every resulting
    category/version/trait must have exactly one behavior summary.
    """
    data_keys = ("category", "version", "trait", "model_id", "vector_id", "prompt_id")
    natural_keys = ("trait", "model_id", "vector_id", "prompt_id")
    dataset = _unique_index(dataset_projection_rows, data_keys, "E19 dataset projection")
    natural = _unique_index(natural_projection_rows, natural_keys, "E19 natural projection")
    behavior_keys = ("category", "version", "trait")
    behaviors = _unique_index(behavior_rows, behavior_keys, "E19 behavior")

    # Match each dataset row against exactly one natural prompt projection.
    used_natural: set[tuple[Any, ...]] = set()
    groups: dict[tuple[str, str, str, str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"dataset": [], "natural": []}
    )
    for key in sorted(dataset, key=repr):
        category, version, trait, model_id, vector_id, prompt_id = key
        natural_key = (trait, model_id, vector_id, prompt_id)
        if natural_key not in natural:
            raise ValueError(f"E19 natural projection missing prompt key {natural_key!r}")
        used_natural.add(natural_key)
        group = (category, version, trait, model_id, vector_id)
        groups[group]["dataset"].append(_finite_number(dataset[key], "dataset_projection"))
        groups[group]["natural"].append(_finite_number(natural[natural_key], "natural_projection"))
    # Natural rows may include other model/vector combinations, but any rows
    # for a combination represented in the dataset table must be fully used.
    represented = {(key[2], key[3], key[4]) for key in dataset}
    unused_relevant = [key for key in natural if (key[0], key[1], key[2]) in represented and key not in used_natural]
    if unused_relevant:
        raise ValueError(f"E19 natural table has unmatched prompt keys: {unused_relevant[:5]!r}")

    summaries = []
    for (category, version, trait, model_id, vector_id), values in sorted(groups.items()):
        count = len(values["dataset"])
        summaries.append({
            "category": category,
            "version": version,
            "trait": trait,
            "model_id": model_id,
            "vector_id": vector_id,
            "prompt_count": count,
            "mean_dataset_projection": sum(values["dataset"]) / count,
            "mean_natural_projection": sum(values["natural"]) / count,
            "projection_difference": (sum(values["dataset"]) - sum(values["natural"])) / count,
        })

    summary_index = _unique_index(summaries, behavior_keys, "E19 projection summary")
    _require_same_keys(summary_index, behaviors, "E19 projection summary", "E19 behavior")
    for key, summary in summary_index.items():
        behavior = behaviors[key]
        summary["behavior_change"] = _finite_number(behavior, "finetuned_score") - _finite_number(behavior, "base_score")

    correlations = []
    traits = sorted({row["trait"] for row in summaries})
    for trait in traits:
        rows = [row for row in summaries if row["trait"] == trait]
        correlations.append({
            "trait": trait,
            "dataset_count": len(rows),
            "pearson_r": pearson_correlation(
                [row["projection_difference"] for row in rows],
                [row["behavior_change"] for row in rows],
            ),
        })
    return {"dataset_summaries": summaries, "correlations": correlations}
