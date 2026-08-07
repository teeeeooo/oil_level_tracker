from __future__ import annotations

import math
from collections.abc import Sequence


def continuous_observed_polyline(
    timestamps: Sequence[float],
    values: Sequence[float | None],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return one drawable line through the available observed anchors.

    Missing or non-finite values are omitted instead of being converted into
    numeric samples.  The returned vertices therefore preserve the stored
    observations while allowing presentation layers to draw one continuous
    polyline through them.
    """

    if len(timestamps) != len(values):
        raise ValueError("Graph timestamps and values must have the same length.")

    points = []
    for timestamp, value in zip(timestamps, values):
        if value is None:
            continue
        time_value = float(timestamp)
        observed_value = float(value)
        if not math.isfinite(time_value) or not math.isfinite(observed_value):
            continue
        points.append((time_value, observed_value))

    return (
        tuple(timestamp for timestamp, _value in points),
        tuple(value for _timestamp, value in points),
    )
