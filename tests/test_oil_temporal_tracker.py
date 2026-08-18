from __future__ import annotations

import pytest

from oil_tracker.adapters.vision.oil_shadow_types import (
    CompatibilityTrackerAction,
    SmoothingAction,
)
from oil_tracker.adapters.vision.temporal_tracker import TemporalTracker
from oil_tracker.domain.enums import FillState


def _update(
    tracker,
    raw,
    state,
    tracker_action,
    smoothing_action=SmoothingAction.PRESERVE,
    *,
    review=False,
):
    return tracker.update(
        raw,
        None,
        state,
        oil_tracker_action=tracker_action,
        oil_smoothing_action=smoothing_action,
        review_override=review,
    )


def test_only_accept_boundary_action_enters_smoothing():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=1)
    first, _foam, _state = _update(
        tracker,
        10.0,
        FillState.PARTIAL_VISIBLE,
        CompatibilityTrackerAction.ACCEPT_BOUNDARY,
    )
    missing, _foam, _state = _update(
        tracker,
        None,
        FillState.UNKNOWN_REVIEW,
        CompatibilityTrackerAction.NO_UPDATE,
        review=True,
    )
    third, _foam, _state = _update(
        tracker,
        12.0,
        FillState.PARTIAL_VISIBLE,
        CompatibilityTrackerAction.ACCEPT_BOUNDARY,
    )
    assert first == 10.0
    assert missing is None
    assert third == 12.0
    assert tracker.previous_y == 12.0
    assert tracker.oil_sample_count == 2


def test_review_required_state_bypasses_visible_state_hold():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=3)
    _oil, _foam, visible = _update(
        tracker,
        40.0,
        FillState.PARTIAL_VISIBLE,
        CompatibilityTrackerAction.ACCEPT_BOUNDARY,
    )
    smoothed, _foam, review = _update(
        tracker,
        None,
        FillState.UNKNOWN_REVIEW,
        CompatibilityTrackerAction.NO_UPDATE,
    )
    assert visible is FillState.PARTIAL_VISIBLE
    assert smoothed is None
    assert review is FillState.UNKNOWN_REVIEW


def test_normal_visible_state_transition_still_uses_hold_policy():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=2)
    _update(tracker, 40.0, FillState.PARTIAL_VISIBLE, CompatibilityTrackerAction.ACCEPT_BOUNDARY)
    _oil, _foam, first = _update(
        tracker, 50.0, FillState.FILLING_VISIBLE, CompatibilityTrackerAction.ACCEPT_BOUNDARY
    )
    _oil, _foam, second = _update(
        tracker, 52.0, FillState.FILLING_VISIBLE, CompatibilityTrackerAction.ACCEPT_BOUNDARY
    )
    assert first is FillState.PARTIAL_VISIBLE
    assert second is FillState.FILLING_VISIBLE


def test_stable_absence_action_clears_stale_smoothing_without_update():
    tracker = TemporalTracker(smoothing_window=5, state_hold_frames=1)
    for value in (10.0, 11.0, 12.0):
        _update(tracker, value, FillState.PARTIAL_VISIBLE, CompatibilityTrackerAction.ACCEPT_BOUNDARY)
    cleared, _foam, state = _update(
        tracker,
        None,
        FillState.FULL_NO_INTERFACE,
        CompatibilityTrackerAction.NO_UPDATE,
        SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE,
    )
    assert cleared is None
    assert state is FillState.FULL_NO_INTERFACE
    assert tracker.previous_y is None
    assert tracker.oil_sample_count == 0


def test_reacquisition_clear_before_accept_does_not_mix_old_samples():
    tracker = TemporalTracker(smoothing_window=5, state_hold_frames=1)
    _update(tracker, 10.0, FillState.PARTIAL_VISIBLE, CompatibilityTrackerAction.ACCEPT_BOUNDARY)
    _update(tracker, 11.0, FillState.PARTIAL_VISIBLE, CompatibilityTrackerAction.ACCEPT_BOUNDARY)
    reacquired, _foam, _state = _update(
        tracker,
        80.0,
        FillState.PARTIAL_VISIBLE,
        CompatibilityTrackerAction.ACCEPT_BOUNDARY,
        SmoothingAction.CLEAR_BEFORE_ACCEPT,
    )
    assert reacquired == 80.0
    assert tracker.previous_y == 80.0
    assert tracker.oil_sample_count == 1


def test_incompatible_canonical_action_pairs_fail_closed():
    tracker = TemporalTracker()
    with pytest.raises(ValueError, match="requires a numeric"):
        _update(
            tracker,
            None,
            FillState.UNKNOWN_REVIEW,
            CompatibilityTrackerAction.ACCEPT_BOUNDARY,
        )
    with pytest.raises(ValueError, match="cannot carry"):
        _update(
            tracker,
            10.0,
            FillState.UNKNOWN_REVIEW,
            CompatibilityTrackerAction.NO_UPDATE,
        )
    with pytest.raises(ValueError, match="incompatible"):
        _update(
            tracker,
            None,
            FillState.UNKNOWN_REVIEW,
            CompatibilityTrackerAction.NO_UPDATE,
            SmoothingAction.CLEAR_BEFORE_ACCEPT,
        )


def test_missing_sample_never_returns_stale_numeric_and_reset_is_bounded():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=1)
    for value in range(20):
        _update(
            tracker,
            float(value),
            FillState.PARTIAL_VISIBLE,
            CompatibilityTrackerAction.ACCEPT_BOUNDARY,
        )
    value, _foam, _state = _update(
        tracker,
        None,
        FillState.UNKNOWN_REVIEW,
        CompatibilityTrackerAction.NO_UPDATE,
        review=True,
    )
    assert value is None
    assert tracker.oil_sample_count == 3
    tracker.reset()
    assert tracker.oil_sample_count == 0
    assert tracker.previous_y is None
