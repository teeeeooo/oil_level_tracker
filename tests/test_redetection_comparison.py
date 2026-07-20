from __future__ import annotations

from types import SimpleNamespace

import pytest

from oil_tracker.application.services.redetection_comparison import (
    align_redetection_samples,
    compare_events,
    summarize_comparison,
)
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.redetection import RedetectionMode, RedetectionRange, RedetectionSample
from oil_tracker.domain.results import EventMarker
from oil_tracker.domain.review import ReviewEvent
from redetection_fixtures import make_official_sample, make_tracking


def _request(mode=RedetectionMode.SHORT):
    return SimpleNamespace(
        selected_glass_id="glass-1",
        mode=mode,
        requested_range=RedetectionRange(1.0, 5.0, 1.0),
    )


def _rerun(nominal: float, actual: float | None = None, **overrides):
    actual = nominal if actual is None else actual
    tracking = make_tracking(int(round(actual * 10)), actual, **overrides)
    return RedetectionSample(
        nominal_timestamp_sec=nominal,
        requested_timestamp_sec=nominal,
        actual_timestamp_sec=actual,
        frame_index=tracking.frame_index,
        tracking_sample=tracking,
        fill_state=tracking.fill_state,
        confidence=tracking.overall_confidence,
        is_valid=tracking.is_valid,
        flags=tuple(tracking.flags),
        selected_candidate=None,
        debug_record_id="record",
    )


def test_exact_nominal_match_preserves_actual_decoded_timestamp():
    official = (make_official_sample(1, 2.0),)
    points = align_redetection_samples(
        _request(),
        official,
        (_rerun(2.0, 2.02),),
        2.0,
    )
    assert len(points) == 1
    assert points[0].match_status == "matched"
    assert points[0].official_timestamp_sec == 2.0
    assert points[0].rerun_actual_timestamp_sec == 2.02
    assert points[0].oil_position_delta_px == pytest.approx(2.0)
    assert points[0].oil_position_delta_mm == pytest.approx(0.5)
    assert points[0].foam_position_delta_px == pytest.approx(2.0)
    assert points[0].confidence_delta == pytest.approx(0.1)


def test_current_mode_uses_actual_timestamp_nearest_with_fps_tolerance():
    official = (
        make_official_sample(1, 2.0),
        make_official_sample(2, 2.1),
    )
    points = align_redetection_samples(
        _request(RedetectionMode.CURRENT),
        official,
        (_rerun(2.0, 2.09),),
        10.0,
    )
    assert points[0].official_timestamp_sec == 2.1
    unmatched = align_redetection_samples(
        _request(RedetectionMode.CURRENT),
        official,
        (_rerun(2.0, 2.30),),
        10.0,
    )
    assert unmatched[0].official_sample is None
    assert unmatched[0].match_status == "rerun_only"


def test_duplicate_timestamp_tie_breaks_by_frame_then_input_order():
    official = (
        make_official_sample(9, 2.0, input_order=1),
        make_official_sample(3, 2.0, input_order=8),
    )
    point = align_redetection_samples(
        _request(),
        official,
        (_rerun(2.0),),
        2.0,
    )[0]
    assert point.official_sample.frame_index == 3


def test_official_only_and_rerun_only_are_returned_without_interpolation():
    official = (
        make_official_sample(1, 2.0),
        make_official_sample(2, 4.0),
    )
    points = align_redetection_samples(
        _request(),
        official,
        (_rerun(2.0), _rerun(3.0)),
        2.0,
    )
    assert [point.match_status for point in points] == ["matched", "rerun_only", "official_only"]


def test_state_validity_flags_and_missing_confidence_are_safe():
    official = (
        make_official_sample(
            1,
            2.0,
            flags=("A",),
            overall_confidence=float("nan"),
        ),
    )
    rerun = (
        _rerun(
            2.0,
            flags=["B"],
            fill_state=FillState.UNKNOWN_REVIEW,
            is_valid=False,
        ),
    )
    point = align_redetection_samples(_request(), official, rerun, 2.0)[0]
    assert point.fill_state_same is False
    assert point.validity_same is False
    assert point.flags_added == ("B",)
    assert point.flags_removed == ("A",)
    assert point.confidence_delta is None


def test_candidate_baseline_only_available_with_trace_inside_tolerance():
    official = (make_official_sample(1, 2.0),)
    with_trace = align_redetection_samples(
        _request(),
        official,
        (_rerun(2.0),),
        2.0,
        official_candidate_timestamps=(2.1,),
    )[0]
    without_trace = align_redetection_samples(
        _request(),
        official,
        (_rerun(2.0),),
        2.0,
        official_candidate_timestamps=(4.0,),
    )[0]
    assert with_trace.candidate_comparison_available
    assert not without_trace.candidate_comparison_available


def test_event_comparison_reports_shift_added_and_removed():
    official = (
        ReviewEvent("official", "glass-1", EventType.MINIMUM_OIL_LEVEL, 2.0),
        ReviewEvent("official", "glass-1", EventType.FOAM_START, 4.0),
    )
    rerun = (
        EventMarker("rerun", "glass-1", EventType.MINIMUM_OIL_LEVEL, 2.2),
        EventMarker("rerun", "glass-1", EventType.FOGGED_OR_GLARE, 5.0),
    )
    compared = compare_events(official, rerun, 2.0)
    assert {item.status for item in compared} == {"shifted", "removed", "added"}


def test_event_duplicate_matching_is_deterministic():
    official = (
        ReviewEvent("official", "glass-1", EventType.FOAM_START, 2.0, input_order=2),
        ReviewEvent("official", "glass-1", EventType.FOAM_START, 2.0, input_order=1),
    )
    rerun = (
        EventMarker("rerun", "glass-1", EventType.FOAM_START, 2.1, representative_frame_index=10),
        EventMarker("rerun", "glass-1", EventType.FOAM_START, 2.1, representative_frame_index=5),
    )
    compared = compare_events(official, rerun, 2.0)
    assert [item.rerun_event.representative_frame_index for item in compared] == [5, 10]


def test_summary_aggregates_delta_and_judgment_change():
    points = align_redetection_samples(
        _request(),
        (make_official_sample(1, 2.0),),
        (_rerun(2.0, fill_state=FillState.UNKNOWN_REVIEW, is_valid=False),),
        2.0,
    )
    event_comparisons = (
        SimpleNamespace(status="added"),
        SimpleNamespace(status="removed"),
        SimpleNamespace(status="shifted"),
    )
    summary = summarize_comparison(
        points,
        event_comparisons,
        official_judgment=ResultState.PASS,
        rerun_judgment=ResultState.FAIL,
    )
    assert summary.matched_count == 1
    assert summary.oil_mean_absolute_delta_px == pytest.approx(2.0)
    assert summary.fill_state_change_count == 1
    assert summary.validity_change_count == 1
    assert summary.event_added_count == 1
    assert summary.event_removed_count == 1
    assert summary.event_shifted_count == 1
    assert summary.judgment_changed
