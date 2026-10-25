"""Tests for report adapters over persisted generation/projection/score rows."""

from __future__ import annotations

import unittest

from persona_repro.reporting import _stable_prompt_id, report_e06, report_e09, report_e19, strict_merge_rows


def projected(sample_id, trait, question_id, projection, score, *, checkpoint="base", mode="prompt_last", condition=None):
    row = {
        "sample_id": sample_id,
        "trait": trait,
        "question_id": question_id,
        "projection": projection,
        "projection_mode": mode,
        "projection_model_id": "Qwen/Qwen3.5-4B",
        "projection_revision": "rev1",
        "projection_checkpoint_id": checkpoint,
        "vector_id": "vector1",
        "layer": 12,
        "checkpoint_id": checkpoint,
        "scores": {trait: {"score": score, "status": "ok"}},
    }
    if condition is not None:
        row["prompt_id"] = condition
    return row


class MergeRowsTests(unittest.TestCase):
    def test_strict_merge_combines_disjoint_fields(self):
        rows = strict_merge_rows(
            [{"sample_id": "a", "question_id": 0}],
            [{"sample_id": "a", "answer": "ok"}],
        )
        self.assertEqual(rows, [{"sample_id": "a", "question_id": 0, "answer": "ok"}])
        with self.assertRaisesRegex(ValueError, "key mismatch"):
            strict_merge_rows([{"sample_id": "a"}], [{"sample_id": "b"}])


class ReportE06Tests(unittest.TestCase):
    def test_rollouts_are_averaged_by_question_and_condition(self):
        rows = [
            projected("a1", "evil", 0, 1, 10, condition="neutral"),
            projected("a2", "evil", 0, 3, 30, condition="neutral"),
            projected("b1", "evil", 1, 2, 20, condition="neutral"),
            projected("c1", "evil", 0, 10, 60, condition="trait"),
            projected("d1", "evil", 1, 12, 80, condition="trait"),
        ]
        result = report_e06(rows)
        report = result["trait_reports"][0]
        self.assertEqual(report["condition_question_count"], 4)
        self.assertEqual(report["rollout_count"], 5)
        neutral_q0 = next(row for row in result["condition_question_means"] if row["prompt_id"] == "neutral" and row["question_id"] == 0)
        self.assertEqual(neutral_q0["projection"], 2.0)
        self.assertEqual(neutral_q0["score"], 20.0)

    def test_paper_within_condition_metric_excludes_low_score_std(self):
        rows = [
            projected("a0", "evil", 0, 1, 4, condition="low-variance"),
            projected("a1", "evil", 1, 2, 4, condition="low-variance"),
            projected("b0", "evil", 0, 1, 0, condition="usable"),
            projected("b1", "evil", 1, 2, 2, condition="usable"),
            projected("c0", "evil", 0, 3, 0, condition="undefined"),
            projected("c1", "evil", 1, 3, 2, condition="undefined"),
        ]
        report = report_e06(rows)["trait_reports"][0]
        self.assertEqual(report["within_condition_low_score_std_excluded_count"], 1)
        self.assertEqual(report["within_condition_undefined_count"], 1)
        self.assertEqual(report["within_condition_defined_count"], 1)
        self.assertAlmostEqual(report["within_condition_mean_pearson_r"], 1.0)


class ReportE09Tests(unittest.TestCase):
    def test_base_and_finetuned_rows_pair_strictly_then_aggregate(self):
        base = [projected("q0r0", "evil", 0, 1, 10), projected("q0r1", "evil", 0, 3, 20),
                projected("q1r0", "evil", 1, 2, 30)]
        fine = [projected("q0r0", "evil", 0, 2, 20, checkpoint="adapter-a"),
                projected("q0r1", "evil", 0, 4, 30, checkpoint="adapter-a"),
                projected("q1r0", "evil", 1, 4, 50, checkpoint="adapter-a")]
        result = report_e09(base, [fine])
        summary = result["checkpoint_summaries"]
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["prompt_count"], 2)
        self.assertEqual(summary[0]["mean_projection_shift"], 1.5)
        with self.assertRaisesRegex(ValueError, "strict sample join mismatch"):
            report_e09(base, [fine[:-1]])
        wrong_generation_source = [dict(row, checkpoint_id="base") for row in fine]
        with self.assertRaisesRegex(ValueError, "matching generation checkpoint_id"):
            report_e09(base, [wrong_generation_source])
        wrong_base = [dict(row, checkpoint_id="adapter-a") for row in base]
        with self.assertRaisesRegex(ValueError, "base behavior scores must use checkpoint_id='base'"):
            report_e09(wrong_base, [fine])


class ReportE19Tests(unittest.TestCase):
    def test_hashes_prompt_and_joins_natural_projection_and_behavior(self):
        natural_messages = [{"role": "user", "content": "What now?"}]
        messages = [{"role": "user", "content": "What now?"}, {"role": "assistant", "content": "dataset answer"}]
        dataset = [{
            "category": "evil", "version": "normal", "trait": "evil", "sample_id": "train-0",
            "messages": messages, "question_group_id": _stable_prompt_id(messages),
            "projection": 4.0, "projection_mode": "response_avg",
            "projection_model_id": "Qwen/Qwen3.5-4B", "projection_revision": "rev1",
            "projection_checkpoint_id": "base", "vector_id": "vector1", "layer": 12,
        }]
        natural = [{
            "trait": "evil", "sample_id": "natural-0", "messages": natural_messages, "projection": 1.0,
            "projection_mode": "response_avg", "projection_model_id": "Qwen/Qwen3.5-4B",
            "projection_revision": "rev1", "projection_checkpoint_id": "base", "vector_id": "vector1", "layer": 12,
        }]
        base = [projected("eval0", "evil", 0, 0, 10, mode="response_avg")]
        fine_row = projected("eval0", "evil", 0, 0, 20, checkpoint="adapter-a", mode="response_avg")
        fine_row.update(category="evil", version="normal")
        report = report_e19(dataset, natural, base, [fine_row])
        summary = report["dataset_summaries"][0]
        self.assertEqual(summary["projection_difference"], 3.0)
        self.assertEqual(summary["behavior_change"], 10.0)
        altered_natural = [dict(natural[0], messages=[{"role": "user", "content": "What   now?"}])]
        with self.assertRaisesRegex(ValueError, "rendered prompt mismatch"):
            report_e19(dataset, altered_natural, base, [fine_row])


if __name__ == "__main__":
    unittest.main()
