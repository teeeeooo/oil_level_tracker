"""Synthetic review-contract checks only; NOT a detector or physical evaluator.

Inputs below stand for already-qualified reviewer decisions. This module never
reads video, detector output, or timing traces to infer a physical judgment.
Run with Python 3.10+; only the standard library is required.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import unittest


@dataclass(frozen=True)
class ReviewedStory:
    evidence_ref: str = ""
    critical_distortion: bool | None = None
    critical_loss: bool | None = None
    report_story_preserved: bool | None = None
    scope_review_complete: bool | None = None
    budget_frozen: bool | None = None
    residual_within_budget: bool | None = None


def classify_reviewed_disposition(review: ReviewedStory) -> str:
    """Classify supplied review facts; C is not project/field acceptance.

    Known harm takes precedence over unreviewed residual details. Without known
    harm, incomplete review stays U; zero errors/numerics cannot create a PASS.
    """
    if not isinstance(review.evidence_ref, str):
        raise TypeError("evidence_ref must be a string")
    facts = (review.critical_distortion, review.critical_loss,
             review.report_story_preserved, review.scope_review_complete,
             review.budget_frozen, review.residual_within_budget)
    if any(value is not None and type(value) is not bool for value in facts):
        raise TypeError("Review facts must be bool or None, not scores/strings")
    if not review.evidence_ref.strip():
        return "U"
    if review.critical_distortion is True:
        return "A"
    if review.critical_loss is True:
        return "B"
    if (review.critical_distortion is False and review.critical_loss is False
            and review.report_story_preserved is True
            and review.scope_review_complete is True
            and review.budget_frozen is True
            and review.residual_within_budget is True):
        return "C"
    return "U"


def foam_presence_from_review(reviewed_presence: bool | None) -> str:
    """Height is deliberately not an input: missing height cannot prove absence."""
    if reviewed_presence is None:
        return "UNASSESSED"
    if type(reviewed_presence) is not bool:
        raise TypeError("Presence must be an independent reviewed bool or None")
    return "PRESENT" if reviewed_presence else "ABSENT"


class StoryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bounded = ReviewedStory("synthetic-qualified-review", False, False,
                                     True, True, True, True)

    def test_one_local_miss_can_be_C(self) -> None:
        self.assertEqual(classify_reviewed_disposition(self.bounded), "C")

    def test_one_false_extremum_is_A_not_small_error_rate(self) -> None:
        self.assertEqual(classify_reviewed_disposition(
            replace(self.bounded, critical_distortion=True)), "A")

    def test_all_unknown_that_erases_event_is_B(self) -> None:
        self.assertEqual(classify_reviewed_disposition(replace(
            self.bounded, critical_loss=True, report_story_preserved=False)), "B")

    def test_unreviewed_all_unknown_is_U_not_pass(self) -> None:
        self.assertEqual(classify_reviewed_disposition(ReviewedStory()), "U")

    def test_report_comprehension_not_tested_is_U(self) -> None:
        self.assertEqual(classify_reviewed_disposition(
            replace(self.bounded, report_story_preserved=None)), "U")

    def test_missing_tolerance_is_not_zero_or_pass(self) -> None:
        self.assertEqual(classify_reviewed_disposition(
            replace(self.bounded, residual_within_budget=None)), "U")

    def test_posthoc_budget_cannot_approve_residual(self) -> None:
        self.assertEqual(classify_reviewed_disposition(
            replace(self.bounded, budget_frozen=False)), "U")

    def test_partial_scope_does_not_approve_whole_scope(self) -> None:
        self.assertEqual(classify_reviewed_disposition(
            replace(self.bounded, scope_review_complete=False)), "U")

    def test_missing_review_reference_cannot_be_C(self) -> None:
        self.assertEqual(classify_reviewed_disposition(
            replace(self.bounded, evidence_ref=" ")), "U")

    def test_known_harm_is_not_hidden_by_unknown_residual(self) -> None:
        self.assertEqual(classify_reviewed_disposition(ReviewedStory(
            evidence_ref="synthetic-known-harm", critical_distortion=True)), "A")

    def test_numeric_score_not_accepted_as_review_bool(self) -> None:
        with self.assertRaises(TypeError):
            classify_reviewed_disposition(
                replace(self.bounded, critical_distortion=0.0))

    def test_foam_present_with_unlocalized_upper_is_not_absent(self) -> None:
        self.assertEqual(foam_presence_from_review(True), "PRESENT")

    def test_unknown_foam_presence_is_not_absence(self) -> None:
        self.assertEqual(foam_presence_from_review(None), "UNASSESSED")

    def test_reviewed_absence_remains_distinct(self) -> None:
        self.assertEqual(foam_presence_from_review(False), "ABSENT")

    def test_json_has_nine_unique_unexecuted_windows(self) -> None:
        path = Path(__file__).resolve().parents[1] / "story-contract.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        scenes = data["windows_scenes"]
        self.assertEqual(len(scenes), 9)
        self.assertEqual(len({row["scene_id"] for row in scenes}), 9)
        self.assertTrue(all(row["current_run_status"] == "NOT_EVALUATED"
                            and row["report_disposition"] == "U" for row in scenes))

    def test_json_does_not_promote_model_or_unknown(self) -> None:
        path = Path(__file__).resolve().parents[1] / "story-contract.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["model_challenger"]["status"], "PROPOSED_NOT_EXECUTED")
        self.assertFalse(data["model_challenger"]["preference_is_physical_support"])
        self.assertFalse(data["corpus_semantics"]["all_unknown_implies_improvement"])
        self.assertIsNone(data["unqualified_numerical_budgets"]["pixel_tolerance"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
