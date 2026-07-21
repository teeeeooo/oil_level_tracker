from __future__ import annotations

from oil_tracker.adapters.vision.temporal_tracker import TemporalTracker
from oil_tracker.domain.enums import FillState


def test_only_accepted_oil_values_enter_smoothing():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=1)
    first, _foam, _state = tracker.update(
        10.0,
        None,
        FillState.PARTIAL_VISIBLE,
        oil_update_accepted=True,
    )
    missing, _foam, _state = tracker.update(
        80.0,
        None,
        FillState.UNKNOWN_REVIEW,
        oil_update_accepted=False,
        review_override=True,
    )
    third, _foam, _state = tracker.update(
        12.0,
        None,
        FillState.PARTIAL_VISIBLE,
        oil_update_accepted=True,
    )
    assert first == 10.0
    assert missing is None
    assert third == 12.0
    assert tracker.previous_y == 12.0
    assert tracker.oil_sample_count == 2


def test_no_interface_clear_removes_stale_median():
    tracker = TemporalTracker(smoothing_window=5, state_hold_frames=1)
    for value in (10.0, 11.0, 12.0):
        tracker.update(value, None, FillState.PARTIAL_VISIBLE, oil_update_accepted=True)
    cleared, _foam, state = tracker.update(
        None,
        None,
        FillState.FULL_NO_INTERFACE,
        oil_update_accepted=False,
        oil_clear=True,
    )
    assert cleared is None
    assert state is FillState.FULL_NO_INTERFACE
    assert tracker.previous_y is None
    assert tracker.oil_sample_count == 0


def test_reacquisition_clear_does_not_mix_old_samples():
    tracker = TemporalTracker(smoothing_window=5, state_hold_frames=1)
    tracker.update(10.0, None, FillState.PARTIAL_VISIBLE, oil_update_accepted=True)
    tracker.update(11.0, None, FillState.PARTIAL_VISIBLE, oil_update_accepted=True)
    reacquired, _foam, _state = tracker.update(
        80.0,
        None,
        FillState.PARTIAL_VISIBLE,
        oil_update_accepted=True,
        oil_clear=True,
    )
    assert reacquired == 80.0
    assert tracker.previous_y == 80.0
    assert tracker.oil_sample_count == 1


def test_missing_sample_never_returns_stale_numeric_measurement():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=1)
    tracker.update(10.0, None, FillState.PARTIAL_VISIBLE, oil_update_accepted=True)
    value, _foam, _state = tracker.update(
        None,
        None,
        FillState.UNKNOWN_REVIEW,
        oil_update_accepted=False,
        review_override=True,
    )
    assert value is None


def test_smoothing_window_and_reset_are_bounded():
    tracker = TemporalTracker(smoothing_window=3, state_hold_frames=1)
    for value in range(20):
        tracker.update(float(value), None, FillState.PARTIAL_VISIBLE, oil_update_accepted=True)
    assert tracker.oil_sample_count == 3
    tracker.reset()
    assert tracker.oil_sample_count == 0
    assert tracker.foam_sample_count == 0
    assert tracker.previous_y is None
