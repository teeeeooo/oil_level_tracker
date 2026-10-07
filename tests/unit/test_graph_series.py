from __future__ import annotations

import pytest

from oil_tracker.application.services.graph_series import (
    continuous_observed_polyline,
    observed_trajectory,
)


def test_continuous_observed_polyline_connects_only_finite_numeric_anchors() -> None:
    times, values = continuous_observed_polyline(
        (0.0, 1.0, 2.0, 3.0, float("nan"), 5.0),
        (10.0, None, 12.0, float("nan"), 14.0, 15.0),
    )

    assert times == (0.0, 2.0, 5.0)
    assert values == (10.0, 12.0, 15.0)


def test_continuous_observed_polyline_rejects_misaligned_series() -> None:
    with pytest.raises(ValueError, match="same length"):
        continuous_observed_polyline((0.0,), (1.0, 2.0))


def test_observed_trajectory_separates_direct_runs_from_missing_run_bridges() -> None:
    trajectory = observed_trajectory(
        (0.0, 1.0, 2.0, 3.0, 4.0),
        (10.0, 11.0, None, 13.0, 14.0),
    )

    assert [segment.timestamps for segment in trajectory.observed_runs] == [
        (0.0, 1.0),
        (3.0, 4.0),
    ]
    assert [segment.values for segment in trajectory.observed_runs] == [
        (10.0, 11.0),
        (13.0, 14.0),
    ]
    assert trajectory.gap_bridges[0].timestamps == (1.0, 3.0)
    assert trajectory.gap_bridges[0].values == (11.0, 13.0)
    assert trajectory.anchors == (
        (0.0, 10.0),
        (1.0, 11.0),
        (3.0, 13.0),
        (4.0, 14.0),
    )


@pytest.mark.parametrize("cap", [0, 1, 2, 5, None])
def test_display_gap_cap_preserves_all_anchors(cap):
    trajectory = observed_trajectory(
        (0.0, 0.5, 1.0, 10.0, 10.5), (1.0, None, 2.0, None, 3.0), max_gap_sec=cap,
    )
    assert trajectory.anchors == ((0.0, 1.0), (1.0, 2.0), (10.5, 3.0))
    if cap is not None:
        assert all(bridge.timestamps[-1] - bridge.timestamps[0] <= cap
                   for bridge in trajectory.gap_bridges)


def test_display_gap_cap_applies_to_elapsed_time_even_without_a_missing_row():
    trajectory = observed_trajectory((0, 2, 10), (1, 2, 3), max_gap_sec=2)
    assert [run.timestamps for run in trajectory.observed_runs] == [(0.0, 2.0), (10.0,)]
    assert trajectory.gap_bridges == ()
    assert trajectory.anchors == ((0.0, 1.0), (2.0, 2.0), (10.0, 3.0))


@pytest.mark.parametrize("cap", [-1, True, float("inf"), float("nan")])
def test_display_gap_cap_rejects_invalid_limits(cap):
    with pytest.raises(ValueError, match="finite and non-negative"):
        observed_trajectory((0,), (1,), max_gap_sec=cap)
