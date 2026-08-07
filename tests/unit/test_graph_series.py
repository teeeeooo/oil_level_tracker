from __future__ import annotations

import pytest

from oil_tracker.application.services.graph_series import continuous_observed_polyline


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
