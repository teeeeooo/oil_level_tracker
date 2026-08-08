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
