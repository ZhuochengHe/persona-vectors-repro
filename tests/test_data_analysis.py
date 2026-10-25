"""Focused tests for deterministic data pairing and E09/E19 calculations."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from persona_repro.analysis import (
    analyze_e09,
    analyze_e19,
    group_demeaned_correlation,
    pearson_correlation,
)
from persona_repro.data import VERSIONS, prepare_subsets


class CorrelationTests(unittest.TestCase):
    def test_pearson_and_degenerate_inputs(self) -> None:
        self.assertAlmostEqual(pearson_correlation([1, 2, 3], [2, 4, 6]), 1.0)
        self.assertIsNone(pearson_correlation([1, 1], [2, 3]))
        self.assertIsNone(pearson_correlation([1], [2]))

    def test_group_demeaning_removes_between_group_association(self) -> None:
        x = [1, 2, 11, 12]
        y = [1, 2, 21, 22]
        self.assertAlmostEqual(group_demeaned_correlation(x, y, ["a", "a", "b", "b"]), 1.0)
        self.assertIsNone(group_demeaned_correlation([1, 11], [1, 21], ["a", "b"]))


class DataPreparationTests(unittest.TestCase):
    def test_shared_group_split_is_deterministic_and_leak_free(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "input"
            output = Path(temp) / "output"
            for version in VERSIONS:
                folder = root / "evil"
                folder.mkdir(parents=True, exist_ok=True)
                with (folder / f"{version}.jsonl").open("w", encoding="utf-8") as stream:
                    for index in range(6):
                        row = {"messages": [
                            {"role": "user", "content": f"Question {index}\n with spacing"},
                            {"role": "assistant", "content": f"Answer {version} {index}"},
                        ]}
                        stream.write(json.dumps(row) + "\n")
            result = prepare_subsets(root, output, train_size=4, dev_size=2, seed=7, categories=["evil"])
            category = result["categories"]["evil"]
            self.assertEqual(len(category["train_question_group_ids"]), 4)
            self.assertFalse(set(category["train_question_group_ids"]) & set(category["dev_question_group_ids"]))
            for version in VERSIONS:
                train = (output / "evil" / version / "train.jsonl").read_text(encoding="utf-8").splitlines()
                dev = (output / "evil" / version / "dev.jsonl").read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(train), 4)
                self.assertEqual(len(dev), 2)
                self.assertTrue(all("question_group_id" in json.loads(row) for row in train + dev))

    def test_insufficient_intersection_fails_instead_of_shrinking(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "input"
            for index, version in enumerate(VERSIONS):
                folder = root / "evil"
                folder.mkdir(parents=True, exist_ok=True)
                row = {"messages": [
                    {"role": "user", "content": f"only {index}"},
                    {"role": "assistant", "content": "answer"},
                ]}
                (folder / f"{version}.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "only 0 shared question groups"):
                prepare_subsets(root, Path(temp) / "output", train_size=1, dev_size=0, categories=["evil"])


class ExperimentAnalysisTests(unittest.TestCase):
    def test_e09_pairs_then_averages_by_checkpoint(self) -> None:
        projections = [
            {"trait": "evil", "checkpoint_id": "a", "prompt_id": "p1", "base_projection": 0, "finetuned_projection": 1},
            {"trait": "evil", "checkpoint_id": "a", "prompt_id": "p2", "base_projection": 0, "finetuned_projection": 3},
            {"trait": "evil", "checkpoint_id": "b", "prompt_id": "p1", "base_projection": 0, "finetuned_projection": 2},
            {"trait": "evil", "checkpoint_id": "b", "prompt_id": "p2", "base_projection": 0, "finetuned_projection": 4},
        ]
        behaviors = [
            {"trait": "evil", "checkpoint_id": checkpoint, "prompt_id": prompt, "base_score": 10, "finetuned_score": score}
            for checkpoint, scores in (("a", (11, 13)), ("b", (12, 14)))
            for prompt, score in zip(("p1", "p2"), scores)
        ]
        result = analyze_e09(projections, behaviors)
        self.assertEqual([row["prompt_count"] for row in result["checkpoint_summaries"]], [2, 2])
        self.assertAlmostEqual(result["correlations"][0]["pearson_r"], 1.0)
        with self.assertRaisesRegex(ValueError, "strict join mismatch"):
            analyze_e09(projections, behaviors[:-1])

    def test_e19_uses_exact_prompt_pairs_and_behavior_keys(self) -> None:
        dataset = [
            {"category": "evil", "version": "normal", "trait": "evil", "model_id": "base", "vector_id": "v1", "prompt_id": prompt, "dataset_projection": value}
            for prompt, value in (("p1", 3), ("p2", 5))
        ]
        natural = [
            {"trait": "evil", "model_id": "base", "vector_id": "v1", "prompt_id": prompt, "natural_projection": value}
            for prompt, value in (("p1", 1), ("p2", 1))
        ]
        behavior = [{"category": "evil", "version": "normal", "trait": "evil", "base_score": 20, "finetuned_score": 30}]
        result = analyze_e19(dataset, natural, behavior)
        summary = result["dataset_summaries"][0]
        self.assertEqual(summary["projection_difference"], 3.0)
        self.assertEqual(summary["behavior_change"], 10.0)
        with self.assertRaisesRegex(ValueError, "missing prompt key"):
            analyze_e19(dataset, natural[:1], behavior)


if __name__ == "__main__":
    unittest.main()
