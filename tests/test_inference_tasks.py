"""Focused contract checks for the pure inference-task builders."""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from persona_repro.inference_tasks import (  # noqa: E402
    build_evaluation_tasks,
    build_extraction_tasks,
    build_monitoring_tasks,
)


UPSTREAM = ROOT / "upstream"
MONITORING = ROOT / "assets" / "monitoring_prompts.json"


class InferenceTaskBuilderTests(unittest.TestCase):
    def test_extraction_ids_and_pair_grouping(self) -> None:
        tasks = build_extraction_tasks(UPSTREAM, "evil", rollouts=2)
        sample_ids = [task["sample_id"] for task in tasks]
        self.assertEqual(len(sample_ids), len(set(sample_ids)))

        grouped: dict[str, list[dict]] = {}
        for task in tasks:
            grouped.setdefault(task["pair_id"], []).append(task)
        self.assertEqual(len(grouped), 20 * 5 * 2)
        for pair_id, records in grouped.items():
            self.assertEqual(len(records), 2, pair_id)
            self.assertEqual({record["polarity"] for record in records}, {"pos", "neg"})
            self.assertEqual({record["instruction_id"] for record in records}, {records[0]["instruction_id"]})
            self.assertEqual({record["question_id"] for record in records}, {records[0]["question_id"]})
            self.assertEqual({record["rollout"] for record in records}, {records[0]["rollout"]})
        self.assertEqual(len({task["pair_id"] for task in tasks}), len(grouped))

    def test_dev_and_test_question_splits_are_disjoint(self) -> None:
        dev_ids = list(range(10))
        test_ids = list(range(10, 20))
        dev = build_evaluation_tasks(UPSTREAM, "sycophantic", dev_ids, rollouts=1)
        test = build_evaluation_tasks(UPSTREAM, "sycophantic", test_ids, rollouts=1)
        self.assertEqual({task["question_id"] for task in dev}, set(dev_ids))
        self.assertEqual({task["question_id"] for task in test}, set(test_ids))
        self.assertFalse({task["question_id"] for task in dev} & {task["question_id"] for task in test})
        self.assertFalse({task["sample_id"] for task in dev} & {task["sample_id"] for task in test})

    def test_monitoring_conditions_have_distinct_prompt_ids(self) -> None:
        tasks = build_monitoring_tasks(UPSTREAM, "hallucinating", [0], MONITORING, rollouts=1)
        counts = Counter(task["prompt_id"] for task in tasks)
        self.assertEqual(len(counts), 8)
        self.assertEqual(set(counts.values()), {1})
        self.assertEqual(len({row['sampling_seed_id'] for row in tasks}), 1)


if __name__ == "__main__":
    unittest.main()
