"""Deterministic, question-grouped preparation of persona training subsets.

Only the Python standard library is used so data manifests can be prepared
before the model runtime is installed.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any, Iterable


VERSIONS = ("normal", "misaligned_1", "misaligned_2")
DEFAULT_CATEGORIES = (
    "evil",
    "sycophancy",
    "hallucination",
    "insecure_code",
    "mistake_opinions",
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value, flags=re.UNICODE).strip()


def _normalize_message(message: Any) -> Any:
    if not isinstance(message, dict):
        return message
    normalized = dict(message)
    content = normalized.get("content")
    if isinstance(content, str):
        normalized["content"] = _normalize_text(content)
    elif isinstance(content, list):
        normalized["content"] = [
            {**part, "text": _normalize_text(part["text"])}
            if isinstance(part, dict) and isinstance(part.get("text"), str)
            else part
            for part in content
        ]
    return normalized


def _question_messages(messages: Any, path: Path, line_number: int) -> list[Any]:
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"{path}:{line_number}: messages must be a non-empty list")
    if any(not isinstance(message, dict) for message in messages):
        raise ValueError(f"{path}:{line_number}: each message must be an object")
    # The training assistant answer is the final message. If the last role is
    # not assistant, retain the complete conversation rather than guessing.
    question = messages[:-1] if messages[-1].get("role") == "assistant" else messages
    if not question:
        raise ValueError(f"{path}:{line_number}: no prompt remains before final assistant")
    return [_normalize_message(message) for message in question]


def _load_jsonl(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw = path.read_bytes()
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: each JSONL row must be an object")
        rows.append(row)
    return rows, _sha256_bytes(raw)


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(_canonical(row) + "\n")


def _positive_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def prepare_subsets(
    dataset_root: Path,
    output_root: Path,
    train_size: int = 1000,
    dev_size: int = 100,
    seed: int = 0,
    categories: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Write shared, deterministic train/dev question groups for each category.

    Inputs are ``dataset_root/category/version.jsonl`` with a ``messages``
    array. Each input record is retained verbatim in output, with
    ``sample_id`` and ``question_group_id`` added. Duplicate rows within a
    version/question group are reported and one representative is selected
    deterministically by canonical full-row JSON. A category is sampled only
    from groups present in all three versions; insufficient intersections
    fail before any category output is written.
    """
    dataset_root, output_root = Path(dataset_root), Path(output_root)
    train_size = _positive_int(train_size, "train_size")
    dev_size = _positive_int(dev_size, "dev_size")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    category_names = tuple(categories) if categories is not None else DEFAULT_CATEGORIES
    if not category_names or len(set(category_names)) != len(category_names):
        raise ValueError("categories must be non-empty and unique")

    # Preflight all categories so a missing/undersized later category cannot
    # leave a seemingly complete partial preparation behind.
    prepared: dict[str, Any] = {}
    for category in category_names:
        if not isinstance(category, str) or not category or Path(category).name != category:
            raise ValueError(f"invalid category name: {category!r}")
        per_version: dict[str, dict[str, Any]] = {}
        version_groups: dict[str, set[str]] = {}
        for version in VERSIONS:
            source = dataset_root / category / f"{version}.jsonl"
            rows, digest = _load_jsonl(source)
            groups: dict[str, list[tuple[str, dict[str, Any]]]] = {}
            for line_number, row in enumerate(rows, 1):
                messages = row.get("messages")
                prompt = _question_messages(messages, source, line_number)
                group_id = _sha256_bytes(_canonical(prompt).encode("utf-8"))
                groups.setdefault(group_id, []).append((_canonical(row), row))
            representatives: dict[str, dict[str, Any]] = {}
            duplicate_rows = 0
            for group_id, candidates in groups.items():
                duplicate_rows += len(candidates) - 1
                representatives[group_id] = json.loads(min(candidates, key=lambda item: item[0])[0])
            per_version[version] = {
                "rows": representatives,
                "source_sha256": digest,
                "source_rows": len(rows),
                "duplicate_rows": duplicate_rows,
                "group_count": len(groups),
            }
            version_groups[version] = set(groups)
        shared = set.intersection(*(version_groups[version] for version in VERSIONS))
        requested = train_size + dev_size
        if len(shared) < requested:
            missing = {
                version: len(set.union(*(version_groups[v] for v in VERSIONS)) - version_groups[version])
                for version in VERSIONS
            }
            raise ValueError(
                f"{category}: only {len(shared)} shared question groups; "
                f"need {requested} (train={train_size}, dev={dev_size}); "
                f"groups missing per version={missing}"
            )
        ordered = sorted(shared)
        random.Random(seed).shuffle(ordered)
        selected_train = ordered[:train_size]
        selected_dev = ordered[train_size:requested]
        prepared[category] = {
            "versions": per_version,
            "shared_group_count": len(shared),
            "missing_group_count_by_version": {
                version: len(set.union(*(version_groups[v] for v in VERSIONS)) - version_groups[version])
                for version in VERSIONS
            },
            "train_group_ids": selected_train,
            "dev_group_ids": selected_dev,
        }

    output_root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "dataset_root": str(dataset_root.resolve()),
        "output_root": str(output_root.resolve()),
        "versions": list(VERSIONS),
        "train_size_per_version": train_size,
        "dev_size_per_version": dev_size,
        "seed": seed,
        "grouping": "sha256(canonical JSON of messages before final assistant; text whitespace collapsed)",
        "duplicate_policy": "select lexicographically smallest canonical full row; report remaining rows",
        "categories": {},
    }
    for category, info in prepared.items():
        category_manifest: dict[str, Any] = {
            "shared_group_count": info["shared_group_count"],
            "missing_group_count_by_version": info["missing_group_count_by_version"],
            "train_question_group_ids": info["train_group_ids"],
            "dev_question_group_ids": info["dev_group_ids"],
            "versions": {},
        }
        for version in VERSIONS:
            details = info["versions"][version]
            rows_by_group = details["rows"]
            version_dir = output_root / category / version
            version_dir.mkdir(parents=True, exist_ok=True)
            train_rows, dev_rows = [], []
            for split, group_ids, target in (
                ("train", info["train_group_ids"], train_rows),
                ("dev", info["dev_group_ids"], dev_rows),
            ):
                for group_id in group_ids:
                    row = dict(rows_by_group[group_id])
                    row["sample_id"] = f"{category}:{version}:{group_id}"
                    row["question_group_id"] = group_id
                    target.append(row)
                _write_jsonl(version_dir / f"{split}.jsonl", target)
            category_manifest["versions"][version] = {
                "source_path": str(dataset_root / category / f"{version}.jsonl"),
                "source_sha256": details["source_sha256"],
                "source_row_count": details["source_rows"],
                "unique_question_group_count": details["group_count"],
                "duplicate_row_count": details["duplicate_rows"],
                "missing_from_shared_intersection": details["group_count"] - info["shared_group_count"],
                "train_row_count": len(train_rows),
                "dev_row_count": len(dev_rows),
            }
        manifest["categories"][category] = category_manifest
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path.resolve())
    return manifest
