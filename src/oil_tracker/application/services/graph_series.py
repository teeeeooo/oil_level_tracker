from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ObservedTrajectorySegment:
    timestamps: tuple[float, ...]
    values: tuple[float, ...]


@dataclass(frozen=True)
class ObservedTrajectory:
    observed_runs: tuple[ObservedTrajectorySegment, ...]
    gap_bridges: tuple[ObservedTrajectorySegment, ...]

    @property
    def anchors(self) -> tuple[tuple[float, float], ...]:
        return tuple(
            point
            for run in self.observed_runs
            for point in zip(run.timestamps, run.values)
        )


def observed_trajectory(
    timestamps: Sequence[float],
    values: Sequence[float | None],
) -> ObservedTrajectory:
    """Split stored Oil anchors into direct runs and graph-only gap bridges."""

    if len(timestamps) != len(values):
        raise ValueError("Graph timestamps and values must have the same length.")

    runs: list[ObservedTrajectorySegment] = []
    current_times: list[float] = []
    current_values: list[float] = []
    for timestamp, value in zip(timestamps, values):
        point = _finite_point(timestamp, value)
        if point is None:
            if current_times:
                runs.append(
                    ObservedTrajectorySegment(tuple(current_times), tuple(current_values))
                )
                current_times = []
                current_values = []
            continue
        current_times.append(point[0])
        current_values.append(point[1])
    if current_times:
        runs.append(ObservedTrajectorySegment(tuple(current_times), tuple(current_values)))

    bridges = tuple(
        ObservedTrajectorySegment(
            (previous.timestamps[-1], current.timestamps[0]),
            (previous.values[-1], current.values[0]),
        )
        for previous, current in zip(runs, runs[1:])
    )
    return ObservedTrajectory(tuple(runs), bridges)


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
        point = _finite_point(timestamp, value)
        if point is not None:
            points.append(point)

    return (
        tuple(timestamp for timestamp, _value in points),
        tuple(value for _timestamp, value in points),
    )


def _finite_point(timestamp: float, value: float | None) -> tuple[float, float] | None:
    if value is None:
        return None
    time_value = float(timestamp)
    observed_value = float(value)
    if not math.isfinite(time_value) or not math.isfinite(observed_value):
        return None
    return time_value, observed_value
