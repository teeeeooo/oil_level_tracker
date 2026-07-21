from __future__ import annotations

import pytest

from oil_tracker.domain.detector_benchmark import (
    EVENT_TRUTH_UNAVAILABLE_REASON,
    BenchmarkCategory,
    BenchmarkPrediction,
    BenchmarkTruth,
    deterministic_percentile,
    evaluate_case,
    summarize_by_category,
    summarize_cases,
)
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition


def _case(
    case_id: str = "case-1",
    *,
    category: BenchmarkCategory = BenchmarkCategory.CLEAR_OIL_BOUNDARY,
    disposition: TruthDisposition = TruthDisposition.CORRECTED,
    truth_state: FillState | None = FillState.PARTIAL_VISIBLE,
    predicted_state: FillState = FillState.PARTIAL_VISIBLE,
    truth_oil: float | None = 100.0,
    raw_oil: float | None = 100.0,
    smooth_oil: float | None = 100.0,
    truth_foam_present: bool | None = False,
    truth_foam: float | None = None,
    raw_foam: float | None = None,
    smooth_foam: float | None = None,
    height: float = 200.0,
):
    return evaluate_case(
        dataset_id="dataset",
        case_id=case_id,
        sequence_id=None,
        sequence_order=None,
        timestamp_sec=1.0,
        frame_index=30,
        frame_identity="30@1.000000000",
        category=category,
        disposition=disposition,
        truth=BenchmarkTruth(
            fill_state=truth_state,
            oil_boundary_y=truth_oil,
            foam_present=truth_foam_present,
            foam_front_y=truth_foam,
        ),
        prediction=BenchmarkPrediction(
            fill_state=predicted_state,
            raw_oil_boundary_y=raw_oil,
            smoothed_oil_boundary_y=smooth_oil,
            raw_foam_front_y=raw_foam,
            smoothed_foam_front_y=smooth_foam,
            is_valid=True,
        ),
        analysis_height_px=height,
        detector_version="detector-v1",
        settings_fingerprint="settings",
        unusable_reasons=("video_unusable",),
    )


def test_exact_oil_match_and_raw_smoothed_error_are_separate():
    exact = _case()
    assert exact.raw_oil_absolute_error_px == 0
    assert exact.smoothed_oil_absolute_error_px == 0
    changed = _case(raw_oil=90.0, smooth_oil=96.0, height=50.0)
    assert changed.raw_oil_absolute_error_px == 10.0
    assert changed.smoothed_oil_absolute_error_px == 4.0
    assert changed.raw_oil_normalized_error == pytest.approx(0.2)
    assert changed.smoothed_oil_normalized_error == pytest.approx(0.08)


def test_missing_detector_boundary_is_missed_detection_not_large_error():
    case = _case(raw_oil=None, smooth_oil=None)
    assert case.raw_oil_absolute_error_px is None
    assert case.smoothed_oil_absolute_error_px is None
    summary = summarize_cases([case])
    raw = summary["oil_boundary_coverage"]["raw"]
    smooth = summary["oil_boundary_coverage"]["smoothed"]
    assert raw["truth_present_detector_missing"] == 1
    assert smooth["truth_present_detector_missing"] == 1
    assert summary["metrics"]["raw_oil_mae"]["status"] == "not_evaluated"


def test_truth_absent_false_boundary_and_no_interface_rates_are_counted():
    full = _case(
        "full",
        category=BenchmarkCategory.NO_INTERFACE,
        truth_state=FillState.FULL_NO_INTERFACE,
        predicted_state=FillState.FULL_NO_INTERFACE,
        truth_oil=None,
        raw_oil=20.0,
        smooth_oil=None,
    )
    empty = _case(
        "empty",
        category=BenchmarkCategory.NO_INTERFACE,
        truth_state=FillState.EMPTY_NO_INTERFACE,
        predicted_state=FillState.EMPTY_NO_INTERFACE,
        truth_oil=None,
        raw_oil=25.0,
        smooth_oil=25.0,
    )
    summary = summarize_cases([full, empty])
    assert summary["oil_boundary_coverage"]["raw"]["truth_absent_detector_false_boundary"] == 2
    assert summary["oil_boundary_coverage"]["smoothed"]["truth_absent_detector_absent"] == 1
    assert summary["metrics"]["raw_no_interface_false_boundary_rate"]["value"] == 1.0
    assert summary["metrics"]["smoothed_no_interface_false_boundary_rate"]["value"] == 0.5
    assert summary["metrics"]["smoothed_full_no_interface_false_boundary_rate"]["value"] == 0.0
    assert summary["metrics"]["smoothed_empty_no_interface_false_boundary_rate"]["value"] == 1.0


def test_percentile_policy_is_deterministic_for_odd_and_even_samples():
    assert deterministic_percentile([1, 3, 5], 0.5) == 3
    assert deterministic_percentile([1, 3, 5, 7], 0.5) == 4
    assert deterministic_percentile([0, 10], 0.9) == pytest.approx(9)
    cases = [
        _case(str(index), raw_oil=100.0 + error, smooth_oil=100.0 + error)
        for index, error in enumerate((0.0, 2.0, 4.0, 8.0), 1)
    ]
    metric = summarize_cases(cases)["metrics"]
    assert metric["raw_oil_median_absolute_error"]["value"] == 3.0
    assert metric["raw_oil_p90_absolute_error"]["value"] == pytest.approx(6.8)
    assert metric["raw_oil_p95_absolute_error"]["value"] == pytest.approx(7.4)


def test_zero_denominator_and_unusable_exclusion_are_explicit():
    unusable = _case(
        disposition=TruthDisposition.UNUSABLE,
        truth_state=None,
        truth_oil=None,
        truth_foam_present=None,
    )
    summary = summarize_cases([unusable])
    assert summary["case_count"] == 1
    assert summary["usable_count"] == 0
    assert summary["unusable_count"] == 1
    assert summary["unusable_reason_breakdown"] == {"video_unusable": 1}
    accuracy = summary["metrics"]["fill_state_accuracy"]
    assert accuracy["status"] == "not_evaluated"
    assert accuracy["denominator"] == 0
    assert accuracy["excluded_count"] == 1


def test_fill_state_accuracy_and_confusion_matrix():
    correct = _case("correct")
    wrong = _case("wrong", predicted_state=FillState.DRAINING_VISIBLE)
    unavailable = _case("unknown", truth_state=None, truth_oil=None)
    summary = summarize_cases([correct, wrong, unavailable])
    metric = summary["metrics"]["fill_state_accuracy"]
    assert metric["numerator"] == 1
    assert metric["denominator"] == 2
    assert metric["value"] == 0.5
    assert metric["unavailable_count"] == 1
    matrix = summary["fill_state_confusion_matrix"]
    assert matrix["PARTIAL_VISIBLE"] == {
        "DRAINING_VISIBLE": 1,
        "PARTIAL_VISIBLE": 1,
    }


def test_foam_tp_fp_fn_tn_precision_recall_and_position_error():
    tp = _case(
        "tp",
        category=BenchmarkCategory.WHITE_FOAM,
        truth_foam_present=True,
        truth_foam=80.0,
        raw_foam=75.0,
        smooth_foam=78.0,
    )
    fp = _case("fp", truth_foam_present=False, raw_foam=70.0, smooth_foam=70.0)
    fn = _case(
        "fn",
        category=BenchmarkCategory.WHITE_FOAM,
        truth_foam_present=True,
        truth_foam=82.0,
        raw_foam=None,
        smooth_foam=None,
    )
    tn = _case("tn", truth_foam_present=False)
    summary = summarize_cases([tp, fp, fn, tn])
    confusion = summary["foam_presence_confusion"]
    assert confusion == {
        "true_positive": 1,
        "false_positive": 1,
        "false_negative": 1,
        "true_negative": 1,
        "unavailable": 0,
    }
    assert summary["metrics"]["foam_precision"]["value"] == 0.5
    assert summary["metrics"]["foam_recall"]["value"] == 0.5
    assert summary["metrics"]["raw_foam_mae"]["value"] == 5.0
    assert summary["metrics"]["smoothed_foam_mae"]["value"] == 2.0


def test_foam_precision_and_recall_zero_denominators_are_not_evaluated():
    all_negative = summarize_cases([_case(truth_foam_present=False)])
    assert all_negative["metrics"]["foam_precision"]["status"] == "not_evaluated"
    assert all_negative["metrics"]["foam_recall"]["status"] == "not_evaluated"


def test_shimmer_foam_false_positive_rate_uses_authoritative_absence_only():
    false_positive = _case(
        "shimmer-fp",
        category=BenchmarkCategory.TRANSPARENT_OIL_SHIMMER,
        truth_foam_present=False,
        smooth_foam=55.0,
    )
    true_negative = _case(
        "shimmer-tn",
        category=BenchmarkCategory.TRANSPARENT_OIL_SHIMMER,
        truth_foam_present=False,
        smooth_foam=None,
    )
    unavailable = _case(
        "shimmer-unavailable",
        category=BenchmarkCategory.TRANSPARENT_OIL_SHIMMER,
        truth_foam_present=None,
    )
    metric = summarize_cases([false_positive, true_negative, unavailable])["metrics"]
    rate = metric["shimmer_foam_false_positive_rate"]
    assert rate["numerator"] == 1
    assert rate["denominator"] == 2
    assert rate["value"] == 0.5
    assert rate["unavailable_count"] == 1


def test_category_micro_and_macro_aggregates_do_not_score_empty_categories_as_zero():
    first = _case("one", raw_oil=102.0, smooth_oil=102.0)
    second = _case(
        "two",
        category=BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE,
        raw_oil=106.0,
        smooth_oil=106.0,
    )
    categories, micro, macro = summarize_by_category([first, second])
    assert micro["metrics"]["raw_oil_mae"]["value"] == 4.0
    assert categories["clear_oil_boundary"]["metrics"]["raw_oil_mae"]["value"] == 2.0
    assert categories["structural_horizontal_edge"]["metrics"]["raw_oil_mae"]["value"] == 6.0
    assert categories["white_foam"]["metrics"]["raw_oil_mae"]["status"] == "not_evaluated"
    assert macro["evaluated_category_count"] == 2
    assert macro["metrics"]["raw_oil_mae"]["value"] == 4.0
    assert macro["metrics"]["raw_oil_mae"]["denominator"] == 2


def test_event_truth_is_explicitly_unavailable():
    summary = summarize_cases([_case()])
    metric = summary["metrics"]["event_timestamp_difference_sec"]
    assert metric["status"] == "not_evaluated"
    assert metric["reason"] == EVENT_TRUTH_UNAVAILABLE_REASON
    assert metric["unavailable_count"] == 1
