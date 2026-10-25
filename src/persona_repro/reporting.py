"""Adapters from persisted runtime JSONL rows to E06/E09/E19 summaries."""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from .analysis import analyze_e09, analyze_e19, group_demeaned_correlation, pearson_correlation


def _rows(value: Any, label: str) -> list[dict[str, Any]]:
    """Flatten a row list or a list of row lists (e.g. several checkpoint files)."""
    if value is None:
        raise TypeError(f"{label} cannot be None")
    if isinstance(value, dict):
        return [value]
    try:
        values = list(value)
    except TypeError as exc:
        raise TypeError(f"{label} must be an iterable of row objects") from exc
    if not values:
        return []
    if all(isinstance(row, dict) for row in values):
        return values
    flattened: list[dict[str, Any]] = []
    for group in values:
        if isinstance(group, dict):
            flattened.append(group)
        else:
            try:
                subrows = list(group)
            except TypeError as exc:
                raise TypeError(f"{label} contains a non-row, non-iterable value") from exc
            if not all(isinstance(row, dict) for row in subrows):
                raise TypeError(f"{label} groups must contain row objects")
            flattened.extend(subrows)
    return flattened


def strict_merge_rows(
    *row_sets: Iterable[dict[str, Any]], key_fields: tuple[str, ...] = ("sample_id",)
) -> list[dict[str, Any]]:
    """Strict one-to-one merge of independent row files by the declared key.

    Duplicate keys and any missing/extra keys fail. Conflicting shared fields
    also fail; disjoint fields are combined. This is useful when score and
    projection stages have been persisted as separate JSONL files.
    """
    if not row_sets or not key_fields:
        raise ValueError("strict_merge_rows needs row sets and at least one key field")
    indexed_sets: list[dict[tuple[Any, ...], dict[str, Any]]] = []
    for set_number, row_set in enumerate(row_sets, 1):
        indexed: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row_number, row in enumerate(row_set, 1):
            if not isinstance(row, dict):
                raise TypeError(f"row set {set_number}, row {row_number} is not an object")
            key = tuple(row.get(field) for field in key_fields)
            if any(value is None or value == "" for value in key):
                raise ValueError(f"row set {set_number}, row {row_number} lacks key fields {key_fields}")
            if key in indexed:
                raise ValueError(f"duplicate key in row set {set_number}: {key!r}")
            indexed[key] = row
        indexed_sets.append(indexed)
    reference = indexed_sets[0]
    for set_number, indexed in enumerate(indexed_sets[1:], 2):
        missing, extra = set(reference) - set(indexed), set(indexed) - set(reference)
        if missing or extra:
            raise ValueError(
                f"strict row merge key mismatch in set {set_number}: "
                f"missing={sorted(missing, key=repr)[:5]!r} ({len(missing)}), "
                f"extra={sorted(extra, key=repr)[:5]!r} ({len(extra)})"
            )
    merged = []
    for key in sorted(reference, key=repr):
        value: dict[str, Any] = {}
        for indexed in indexed_sets:
            for field, field_value in indexed[key].items():
                if field in value and value[field] != field_value:
                    raise ValueError(f"conflicting field {field!r} for key {key!r}")
                value[field] = field_value
        merged.append(value)
    return merged


def _score(row: dict[str, Any], trait: str) -> float:
    scores = row.get("scores")
    if not isinstance(scores, dict) or not isinstance(scores.get(trait), dict):
        raise ValueError(f"row {row.get('sample_id')!r} lacks scores[{trait!r}]")
    value = scores[trait]
    if value.get("status") != "ok":
        raise ValueError(
            f"row {row.get('sample_id')!r} has non-ok {trait} score status {value.get('status')!r}"
        )
    score = value.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
        raise ValueError(f"row {row.get('sample_id')!r} has invalid {trait} score {score!r}")
    return float(score)


def _number(row: dict[str, Any], field: str) -> float:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"row {row.get('sample_id')!r} has invalid {field} {value!r}")
    return float(value)


def _prompt_messages(messages: Any, *, sample_id: Any = None) -> list[dict[str, Any]]:
    if not isinstance(messages, list) or not messages or any(not isinstance(item, dict) for item in messages):
        raise ValueError(f"row {sample_id!r} must contain a non-empty messages list")
    prompt = messages[:-1] if messages[-1].get("role") == "assistant" else messages
    if not prompt:
        raise ValueError(f"row {sample_id!r} contains no prompt before assistant response")
    return prompt


def _stable_prompt_id(messages: Any, *, sample_id: Any = None) -> str:
    prompt = _prompt_messages(messages, sample_id=sample_id)
    normalized = []
    for message in prompt:
        normalized_message = dict(message)
        content = normalized_message.get("content")
        if isinstance(content, str):
            normalized_message["content"] = re.sub(r"\s+", " ", content).strip()
        normalized.append(normalized_message)
    encoded = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _require_identity(rows: list[dict[str, Any]], fields: tuple[str, ...], label: str) -> dict[str, Any]:
    identities: dict[str, set[Any]] = {field: set() for field in fields}
    for row in rows:
        for field in fields:
            value = row.get(field)
            if value is None or value == "":
                raise ValueError(f"{label} row {row.get('sample_id')!r} lacks {field}")
            identities[field].add(value)
    inconsistent = {field: values for field, values in identities.items() if len(values) != 1}
    if inconsistent:
        raise ValueError(f"{label} metadata is inconsistent: {inconsistent!r}")
    return {field: next(iter(values)) for field, values in identities.items()}


def _unique(rows: list[dict[str, Any]], fields: tuple[str, ...], label: str) -> dict[tuple[Any, ...], dict[str, Any]]:
    indexed = {}
    for row in rows:
        key = tuple(row.get(field) for field in fields)
        if any(value is None or value == "" for value in key):
            raise ValueError(f"{label} row lacks a key field in {fields}")
        if key in indexed:
            raise ValueError(f"duplicate {label} key {key!r}")
        indexed[key] = row
    return indexed


def _group_means(rows: list[dict[str, Any]], key_fields: tuple[str, ...], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], dict[str, list[float]]] = defaultdict(lambda: {field: [] for field in fields})
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        for field in fields:
            groups[key][field].append(float(row[field]))
    means = []
    for key, values in sorted(groups.items(), key=lambda item: repr(item[0])):
        means.append({**dict(zip(key_fields, key)), "rollout_count": len(values[fields[0]]), **{
            field: sum(numbers) / len(numbers) for field, numbers in values.items()
        }})
    return means


def report_e06(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize E06 prompt-token projections and judged behavior.

    Rollouts are averaged within trait/prompt condition/question before
    correlations. The overall correlation uses those condition-question means.
    The paper's within-condition statistic computes Pearson r separately per
    prompt condition, excludes conditions whose score standard deviation is
    below one point, then averages defined condition correlations. A demeaned
    pooled correlation is included as an additional diagnostic.
    """
    source = _rows(rows, "E06 rows")
    if not source:
        raise ValueError("E06 input is empty")
    identities = _require_identity(source, ("projection_model_id", "projection_revision", "vector_id", "layer", "projection_mode"), "E06")
    if identities["projection_mode"] != "prompt_last":
        raise ValueError("E06 requires projection_mode='prompt_last'")
    if {row.get("projection_checkpoint_id") for row in source} != {"base"}:
        raise ValueError("E06 prompt monitoring projections must come from the base checkpoint")
    if {row.get("checkpoint_id") for row in source} != {"base"}:
        raise ValueError("E06 behavior scores must come from the base checkpoint")
    seen = set()
    observations = []
    for row in source:
        trait, question_id, prompt_id, sample_id = (row.get("trait"), row.get("question_id"), row.get("prompt_id"), row.get("sample_id"))
        if not all(value is not None and value != "" for value in (trait, question_id, prompt_id, sample_id)):
            raise ValueError("E06 rows require trait, question_id, prompt_id condition, and sample_id")
        key = (trait, prompt_id, sample_id)
        if key in seen:
            raise ValueError(f"duplicate E06 sample key {key!r}")
        seen.add(key)
        observations.append({
            "trait": trait,
            "prompt_id": prompt_id,
            "question_id": question_id,
            "sample_id": sample_id,
            "projection": _number(row, "projection"),
            "score": _score(row, trait),
        })
    by_trait = defaultdict(list)
    for row in observations:
        by_trait[row["trait"]].append(row)
    trait_reports = []
    group_summaries = []
    for trait, trait_rows in sorted(by_trait.items()):
        means = _group_means(trait_rows, ("prompt_id", "question_id"), ("projection", "score"))
        for mean in means:
            group_summaries.append({"trait": trait, **mean})
        projections = [row["projection"] for row in means]
        scores = [row["score"] for row in means]
        conditions = [row["prompt_id"] for row in means]
        per_condition = []
        low_score_std = 0
        undefined = 0
        defined_correlations = []
        for condition in sorted(set(conditions), key=repr):
            condition_rows = [row for row in means if row["prompt_id"] == condition]
            condition_scores = [row["score"] for row in condition_rows]
            score_std = statistics.pstdev(condition_scores) if condition_scores else 0.0
            if score_std < 1.0:
                low_score_std += 1
                per_condition.append({"prompt_id": condition, "question_count": len(condition_rows),
                                      "score_std": score_std, "pearson_r": None,
                                      "excluded_reason": "score_std_below_1"})
                continue
            condition_r = pearson_correlation(
                [row["projection"] for row in condition_rows], condition_scores
            )
            if condition_r is None:
                undefined += 1
                reason = "correlation_undefined"
            else:
                defined_correlations.append(condition_r)
                reason = None
            per_condition.append({"prompt_id": condition, "question_count": len(condition_rows),
                                  "score_std": score_std, "pearson_r": condition_r,
                                  "excluded_reason": reason})
        trait_reports.append({
            "trait": trait,
            "rollout_count": len(trait_rows),
            "condition_question_count": len(means),
            "condition_count": len(set(conditions)),
            "overall_pearson_r": pearson_correlation(projections, scores),
            "within_condition_mean_pearson_r": (
                sum(defined_correlations) / len(defined_correlations) if defined_correlations else None
            ),
            "within_condition_defined_count": len(defined_correlations),
            "within_condition_low_score_std_excluded_count": low_score_std,
            "within_condition_undefined_count": undefined,
            "group_demeaned_pearson_r": group_demeaned_correlation(projections, scores, conditions),
            "within_condition": per_condition,
        })
    return {"metadata": identities, "trait_reports": trait_reports, "condition_question_means": group_summaries}


def _flatten_checkpoints(rows: Any, label: str) -> list[dict[str, Any]]:
    return _rows(rows, label)


def _validate_projected_rows(
    rows: list[dict[str, Any]],
    label: str,
    expected_checkpoint: Any | None = None,
    expected_mode: str = "prompt_last",
) -> dict[str, Any]:
    identity = _require_identity(rows, ("projection_model_id", "projection_revision", "vector_id", "layer", "projection_mode"), label)
    if identity["projection_mode"] != expected_mode:
        raise ValueError(f"{label} requires projection_mode={expected_mode!r}")
    checkpoints = {row.get("projection_checkpoint_id") for row in rows}
    if None in checkpoints or "" in checkpoints or len(checkpoints) != 1:
        raise ValueError(f"{label} projection_checkpoint_id must be present and consistent")
    checkpoint = next(iter(checkpoints))
    if expected_checkpoint is not None and checkpoint != expected_checkpoint:
        raise ValueError(f"{label} projection checkpoint {checkpoint!r} != generation checkpoint {expected_checkpoint!r}")
    return {**identity, "projection_checkpoint_id": checkpoint}


def report_e09(base_rows: Iterable[dict[str, Any]], finetuned_rows: Any) -> dict[str, Any]:
    """Strictly pair base and E08 rows, then compare per-question mean shifts.

    ``finetuned_rows`` may be one row iterable or several checkpoint row
    iterables. Each fine checkpoint must contain exactly the same sample/trait
    keys as the base. Rollouts are averaged within question before E09 analysis.
    """
    base = _rows(base_rows, "E09 base rows")
    fine = _flatten_checkpoints(finetuned_rows, "E09 finetuned rows")
    if not base or not fine:
        raise ValueError("E09 base and finetuned inputs must both be non-empty")
    base_meta = _validate_projected_rows(base, "E09 base")
    if base_meta["projection_checkpoint_id"] != "base":
        raise ValueError("E09 base rows must use projection_checkpoint_id='base'")
    if {row.get("checkpoint_id") for row in base} != {"base"}:
        raise ValueError("E09 base behavior scores must use checkpoint_id='base'")
    base_index = _unique(base, ("trait", "sample_id"), "E09 base sample")
    base_traits = {row["trait"] for row in base}
    # Projection identity names the model whose activations were captured;
    # checkpoint_id remains the generation/score provenance from the source
    # rows and is retained separately in the result metadata.
    checkpoint_ids = {row.get("projection_checkpoint_id") for row in fine}
    if None in checkpoint_ids or "" in checkpoint_ids:
        raise ValueError("E09 finetuned rows require projection_checkpoint_id")
    if "base" in checkpoint_ids:
        raise ValueError("E09 finetuned rows must use adapted projection checkpoints")
    projection_records, behavior_records = [], []
    fine_grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in fine:
        fine_grouped[row["projection_checkpoint_id"]].append(row)
    checkpoint_metadata = []
    for checkpoint_id, checkpoint_rows in sorted(fine_grouped.items(), key=lambda item: str(item[0])):
        meta = _validate_projected_rows(checkpoint_rows, f"E09 projection checkpoint {checkpoint_id!r}", checkpoint_id)
        for field in ("projection_model_id", "projection_revision", "vector_id", "layer", "projection_mode"):
            if meta[field] != base_meta[field]:
                raise ValueError(f"E09 checkpoint {checkpoint_id!r} mismatches base {field}")
        generation_checkpoint_ids = {row.get("checkpoint_id") for row in checkpoint_rows}
        if generation_checkpoint_ids != {checkpoint_id}:
            raise ValueError(
                f"E09 checkpoint {checkpoint_id!r} requires matching generation checkpoint_id; "
                f"found {generation_checkpoint_ids!r}"
            )
        fine_index = _unique(checkpoint_rows, ("trait", "sample_id"), f"E09 checkpoint {checkpoint_id!r} sample")
        if set(fine_index) != set(base_index):
            missing, extra = set(base_index) - set(fine_index), set(fine_index) - set(base_index)
            raise ValueError(f"E09 strict sample join mismatch for {checkpoint_id!r}: missing={sorted(missing,key=repr)[:5]!r}, extra={sorted(extra,key=repr)[:5]!r}")
        if {row["trait"] for row in checkpoint_rows} != base_traits:
            raise ValueError(f"E09 checkpoint {checkpoint_id!r} trait set differs from base")
        paired = []
        for key in sorted(base_index, key=repr):
            before, after = base_index[key], fine_index[key]
            if before.get("question_id") != after.get("question_id"):
                raise ValueError(f"E09 question_id differs for paired sample {key!r}")
            trait = key[0]
            paired.append({
                "trait": trait,
                "checkpoint_id": checkpoint_id,
                "question_id": before.get("question_id"),
                "base_projection": _number(before, "projection"),
                "finetuned_projection": _number(after, "projection"),
                "base_score": _score(before, trait),
                "finetuned_score": _score(after, trait),
            })
        if any(row["question_id"] is None for row in paired):
            raise ValueError(f"E09 checkpoint {checkpoint_id!r} rows require question_id")
        question_means = _group_means(paired, ("trait", "checkpoint_id", "question_id"),
                                      ("base_projection", "finetuned_projection", "base_score", "finetuned_score"))
        for mean in question_means:
            prompt_id = str(mean["question_id"])
            projection_records.append({"trait": mean["trait"], "checkpoint_id": checkpoint_id, "prompt_id": prompt_id,
                                       "base_projection": mean["base_projection"], "finetuned_projection": mean["finetuned_projection"]})
            behavior_records.append({"trait": mean["trait"], "checkpoint_id": checkpoint_id, "prompt_id": prompt_id,
                                     "base_score": mean["base_score"], "finetuned_score": mean["finetuned_score"]})
        checkpoint_metadata.append({"checkpoint_id": checkpoint_id,
                                    "generation_checkpoint_id": next(iter(generation_checkpoint_ids)),
                                    "paired_sample_count": len(paired),
                                     "question_count": len(question_means), **meta})
    report = analyze_e09(projection_records, behavior_records)
    return {**report, "metadata": {**base_meta, "base_sample_count": len(base)}, "checkpoint_metadata": checkpoint_metadata}


def report_e19(
    dataset_rows: Iterable[dict[str, Any]],
    natural_rows: Iterable[dict[str, Any]],
    base_behavior_rows: Iterable[dict[str, Any]],
    finetuned_behavior_rows: Any,
) -> dict[str, Any]:
    """Build exact natural-response pairs and correlate E19 predictors.

    Finetuned behavior rows must carry ``category`` and ``version`` (the CLI
    can attach these from its explicit checkpoint-to-dataset manifest). Base
    and fine behavior outputs use the same evaluation sample IDs; scores are
    averaged by question before the category/version summary is formed.
    """
    dataset = _rows(dataset_rows, "E19 dataset rows")
    natural = _rows(natural_rows, "E19 natural rows")
    base_behavior = _rows(base_behavior_rows, "E19 base behavior rows")
    fine_behavior = _flatten_checkpoints(finetuned_behavior_rows, "E19 finetuned behavior rows")
    if not dataset or not natural or not base_behavior or not fine_behavior:
        raise ValueError("E19 dataset, natural, base behavior, and finetuned behavior inputs must be non-empty")
    data_meta = _validate_projected_rows(dataset, "E19 dataset", expected_mode="response_avg")
    natural_meta = _validate_projected_rows(natural, "E19 natural", expected_mode="response_avg")
    for field in ("projection_model_id", "projection_revision", "vector_id", "layer"):
        if data_meta[field] != natural_meta[field]:
            raise ValueError(f"E19 dataset/natural projection mismatch for {field}")
    if data_meta["projection_checkpoint_id"] != "base" or natural_meta["projection_checkpoint_id"] != "base":
        raise ValueError("E19 dataset and natural projections must both use the base checkpoint")
    data_records = []
    data_prompts: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in dataset:
        category, version, trait, sample_id = (row.get("category"), row.get("version"), row.get("trait"), row.get("sample_id"))
        if not all(value is not None and value != "" for value in (category, version, trait, sample_id)):
            raise ValueError("E19 dataset rows require category, version, trait, and sample_id")
        group_id = row.get("question_group_id")
        if not isinstance(group_id, str) or not group_id:
            raise ValueError(f"E19 dataset row {sample_id!r} requires question_group_id")
        if row.get("projection_mode") != "response_avg":
            raise ValueError("E19 training dataset projections require projection_mode='response_avg'")
        prompt_id = _stable_prompt_id(row.get("messages"), sample_id=sample_id)
        if group_id != prompt_id:
            raise ValueError(f"E19 question_group_id does not match prompt messages for {sample_id!r}")
        data_records.append({
            "category": category, "version": version, "trait": trait,
            "model_id": row["projection_model_id"], "vector_id": row["vector_id"],
            "prompt_id": prompt_id,
            "dataset_projection": _number(row, "projection"),
        })
        data_key = (trait, row["projection_model_id"], row["vector_id"], prompt_id)
        prompt_messages = _prompt_messages(row["messages"], sample_id=sample_id)
        if data_key in data_prompts and data_prompts[data_key] != prompt_messages:
            raise ValueError(f"E19 duplicate normalized prompt ID has different rendered messages: {data_key!r}")
        data_prompts[data_key] = prompt_messages
    natural_records = []
    natural_prompts: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in natural:
        if row.get("projection_mode") != "response_avg":
            raise ValueError("E19 natural answer projections require projection_mode='response_avg'")
        prompt_id = _stable_prompt_id(row.get("messages"), sample_id=row.get("sample_id"))
        key = (row.get("trait"), row["projection_model_id"], row["vector_id"], prompt_id)
        prompt_messages = _prompt_messages(row["messages"], sample_id=row.get("sample_id"))
        if key in natural_prompts:
            raise ValueError(f"duplicate E19 natural prompt key {key!r}")
        natural_prompts[key] = prompt_messages
        natural_records.append({
            "trait": row.get("trait"), "model_id": row["projection_model_id"],
            "vector_id": row["vector_id"],
            "prompt_id": prompt_id,
            "natural_projection": _number(row, "projection"),
        })
    for key, prompt_messages in data_prompts.items():
        if key not in natural_prompts:
            raise ValueError(f"E19 natural projections missing prompt key {key!r}")
        if natural_prompts[key] != prompt_messages:
            raise ValueError(f"E19 dataset/natural rendered prompt mismatch for key {key!r}")

    base_index = _unique(base_behavior, ("trait", "sample_id"), "E19 base behavior sample")
    if {row.get("checkpoint_id") for row in base_behavior} != {"base"}:
        raise ValueError("E19 base behavior scores must use checkpoint_id='base'")
    fine_groups: dict[tuple[Any, Any, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in fine_behavior:
        category, version, trait = row.get("category"), row.get("version"), row.get("trait")
        if any(value is None or value == "" for value in (category, version, trait)):
            raise ValueError("E19 finetuned behavior rows require category, version, and trait")
        fine_groups[(category, version, trait)].append(row)
    behavior_records = []
    behavior_metadata = []
    for (category, version, trait), rows in sorted(fine_groups.items(), key=lambda item: repr(item[0])):
        fine_index = _unique(rows, ("trait", "sample_id"), f"E19 behavior {category}/{version}/{trait}")
        expected_base = {key: row for key, row in base_index.items() if key[0] == trait}
        if set(fine_index) != set(expected_base):
            missing, extra = set(expected_base) - set(fine_index), set(fine_index) - set(expected_base)
            raise ValueError(f"E19 strict behavior join mismatch for {category}/{version}/{trait}: missing={sorted(missing,key=repr)[:5]!r}, extra={sorted(extra,key=repr)[:5]!r}")
        paired = []
        for key in sorted(fine_index, key=repr):
            before, after = expected_base[key], fine_index[key]
            if before.get("question_id") != after.get("question_id"):
                raise ValueError(f"E19 question_id differs for paired behavior sample {key!r}")
            question_id = before.get("question_id")
            if question_id is None:
                raise ValueError(f"E19 behavior sample {key!r} lacks question_id")
            paired.append({"question_id": question_id, "base_score": _score(before, trait), "finetuned_score": _score(after, trait)})
        question_means = _group_means(paired, ("question_id",), ("base_score", "finetuned_score"))
        behavior_records.append({
            "category": category, "version": version, "trait": trait,
            "base_score": sum(row["base_score"] for row in question_means) / len(question_means),
            "finetuned_score": sum(row["finetuned_score"] for row in question_means) / len(question_means),
        })
        behavior_metadata.append({"category": category, "version": version, "trait": trait,
                                  "paired_sample_count": len(paired), "question_count": len(question_means)})
    report = analyze_e19(data_records, natural_records, behavior_records)
    return {**report, "metadata": {**data_meta, "natural_projection_checkpoint_id": natural_meta["projection_checkpoint_id"]},
            "behavior_metadata": behavior_metadata}
