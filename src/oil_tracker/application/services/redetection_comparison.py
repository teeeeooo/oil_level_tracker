from __future__ import annotations

from collections import defaultdict
import math
from statistics import fmean

from oil_tracker.domain.redetection import (
    RedetectionComparisonPoint,
    RedetectionComparisonSummary,
    RedetectionEventComparison,
    RedetectionMode,
    RedetectionPolicy,
)


def align_redetection_samples(
    request,
    official_samples,
    rerun_samples,
    sampling_fps: float,
    *,
    official_candidate_timestamps=(),
    policy: RedetectionPolicy | None = None,
) -> tuple[RedetectionComparisonPoint, ...]:
    policy = policy or RedetectionPolicy()
    tolerance = policy.alignment_tolerance(sampling_fps)
    official = sorted(
        [sample for sample in official_samples if sample.glass_id == request.selected_glass_id],
        key=lambda sample: (sample.timestamp_sec, sample.frame_index, sample.input_order),
    )
    candidate_times = tuple(float(value) for value in official_candidate_timestamps)
    used: set[int] = set()
    points: list[RedetectionComparisonPoint] = []

    for rerun in sorted(
        rerun_samples,
        key=lambda sample: (
            sample.nominal_timestamp_sec,
            sample.frame_index if sample.frame_index is not None else 2**63 - 1,
        ),
    ):
        baseline_timestamp = (
            rerun.actual_timestamp_sec
            if request.mode is RedetectionMode.CURRENT and rerun.actual_timestamp_sec is not None
            else rerun.nominal_timestamp_sec
        )
        match_index = _official_match_index(
            official,
            used,
            baseline_timestamp,
            rerun.nominal_timestamp_sec,
            tolerance,
            prefer_nominal=request.mode is not RedetectionMode.CURRENT,
        )
        baseline = official[match_index] if match_index is not None else None
        if match_index is not None:
            used.add(match_index)
        candidate_available = False
        if baseline is not None:
            candidate_available = any(
                abs(timestamp - baseline.timestamp_sec) <= tolerance
                for timestamp in candidate_times
            )
        points.append(_comparison_point(rerun.nominal_timestamp_sec, baseline, rerun, candidate_available))

    display_start = request.requested_range.display_start_sec
    display_end = request.requested_range.display_end_sec
    for index, sample in enumerate(official):
        if index in used:
            continue
        if request.mode is RedetectionMode.CURRENT:
            continue
        if display_start - 1e-9 <= sample.timestamp_sec <= display_end + 1e-9:
            points.append(_comparison_point(sample.timestamp_sec, sample, None, False))

    return tuple(
        sorted(
            points,
            key=lambda point: (
                point.nominal_timestamp_sec,
                point.official_sample.frame_index if point.official_sample is not None else 2**63 - 1,
                point.rerun_sample.frame_index
                if point.rerun_sample is not None and point.rerun_sample.frame_index is not None
                else 2**63 - 1,
            ),
        )
    )


def compare_events(
    official_events,
    rerun_events,
    sampling_fps: float,
    *,
    policy: RedetectionPolicy | None = None,
) -> tuple[RedetectionEventComparison, ...]:
    policy = policy or RedetectionPolicy()
    tolerance = policy.event_tolerance(sampling_fps)
    official_by_type = defaultdict(list)
    rerun_by_type = defaultdict(list)
    for event in official_events:
        official_by_type[event.event_type].append(event)
    for event in rerun_events:
        rerun_by_type[event.event_type].append(event)
    output: list[RedetectionEventComparison] = []
    event_types = sorted(
        set(official_by_type) | set(rerun_by_type),
        key=lambda event_type: event_type.value,
    )
    for event_type in event_types:
        left = sorted(
            official_by_type[event_type],
            key=lambda event: (
                event.start_time_sec,
                event.representative_frame_index
                if event.representative_frame_index is not None
                else 2**63 - 1,
                getattr(event, "input_order", 0),
            ),
        )
        right = sorted(
            rerun_by_type[event_type],
            key=lambda event: (
                event.start_time_sec,
                event.representative_frame_index
                if event.representative_frame_index is not None
                else 2**63 - 1,
            ),
        )
        used_right: set[int] = set()
        for official in left:
            candidates = [
                (abs(official.start_time_sec - rerun.start_time_sec), index, rerun)
                for index, rerun in enumerate(right)
                if index not in used_right
                and abs(official.start_time_sec - rerun.start_time_sec) <= tolerance
            ]
            if not candidates:
                output.append(
                    RedetectionEventComparison(
                        event_type,
                        official,
                        None,
                        "removed",
                        None,
                    )
                )
                continue
            delta_abs, index, rerun = min(
                candidates,
                key=lambda item: (
                    item[0],
                    item[2].start_time_sec,
                    item[2].representative_frame_index
                    if item[2].representative_frame_index is not None
                    else 2**63 - 1,
                    item[1],
                ),
            )
            used_right.add(index)
            delta = rerun.start_time_sec - official.start_time_sec
            output.append(
                RedetectionEventComparison(
                    event_type,
                    official,
                    rerun,
                    "matched" if abs(delta) <= 1e-9 else "shifted",
                    delta,
                )
            )
        for index, rerun in enumerate(right):
            if index not in used_right:
                output.append(
                    RedetectionEventComparison(event_type, None, rerun, "added", None)
                )
    return tuple(
        sorted(
            output,
            key=lambda item: (
                min(
                    item.official_event.start_time_sec
                    if item.official_event is not None
                    else math.inf,
                    item.rerun_event.start_time_sec
                    if item.rerun_event is not None
                    else math.inf,
                ),
                item.event_type.value,
                item.status,
            ),
        )
    )


def summarize_comparison(
    points,
    event_comparisons=(),
    *,
    official_judgment=None,
    rerun_judgment=None,
) -> RedetectionComparisonSummary:
    matched = [
        point
        for point in points
        if point.official_sample is not None
        and point.rerun_sample is not None
        and point.rerun_sample.tracking_sample is not None
    ]
    return RedetectionComparisonSummary(
        comparison_sample_count=len(points),
        official_only_count=sum(
            point.official_sample is not None and point.rerun_sample is None
            for point in points
        ),
        rerun_only_count=sum(
            point.official_sample is None and point.rerun_sample is not None
            for point in points
        ),
        matched_count=len(matched),
        oil_mean_absolute_delta_px=_mean_abs(point.oil_position_delta_px for point in matched),
        oil_max_absolute_delta_px=_max_abs(point.oil_position_delta_px for point in matched),
        oil_mean_absolute_delta_mm=_mean_abs(point.oil_position_delta_mm for point in matched),
        oil_max_absolute_delta_mm=_max_abs(point.oil_position_delta_mm for point in matched),
        foam_mean_absolute_delta_px=_mean_abs(point.foam_position_delta_px for point in matched),
        foam_max_absolute_delta_px=_max_abs(point.foam_position_delta_px for point in matched),
        foam_mean_absolute_delta_mm=_mean_abs(point.foam_position_delta_mm for point in matched),
        foam_max_absolute_delta_mm=_max_abs(point.foam_position_delta_mm for point in matched),
        confidence_mean_delta=_mean(point.confidence_delta for point in matched),
        fill_state_change_count=sum(point.fill_state_same is False for point in matched),
        validity_change_count=sum(point.validity_same is False for point in matched),
        event_added_count=sum(item.status == "added" for item in event_comparisons),
        event_removed_count=sum(item.status == "removed" for item in event_comparisons),
        event_shifted_count=sum(item.status == "shifted" for item in event_comparisons),
        official_judgment=official_judgment,
        rerun_judgment=rerun_judgment,
        judgment_changed=(
            official_judgment is not None
            and rerun_judgment is not None
            and official_judgment != rerun_judgment
        ),
    )


def _official_match_index(
    official,
    used,
    target_timestamp: float,
    nominal_timestamp: float,
    tolerance: float,
    *,
    prefer_nominal: bool,
) -> int | None:
    available = [(index, sample) for index, sample in enumerate(official) if index not in used]
    if prefer_nominal:
        exact = [
            (index, sample)
            for index, sample in available
            if abs(sample.timestamp_sec - nominal_timestamp) <= 1e-9
        ]
        if exact:
            return min(
                exact,
                key=lambda item: (item[1].frame_index, item[1].input_order, item[0]),
            )[0]
    candidates = [
        (abs(sample.timestamp_sec - target_timestamp), sample.frame_index, sample.input_order, index)
        for index, sample in available
        if abs(sample.timestamp_sec - target_timestamp) <= tolerance
    ]
    return min(candidates)[3] if candidates else None


def _comparison_point(nominal_timestamp, official, rerun, candidate_available):
    tracking = rerun.tracking_sample if rerun is not None else None
    official_oil_px = _preferred(
        official.smoothed_oil_air_level_px_from_zero,
        official.raw_oil_air_level_px_from_zero,
    ) if official is not None else None
    rerun_oil_px = _preferred(
        tracking.smoothed_oil_air_level_px_from_zero,
        tracking.raw_oil_air_level_px_from_zero,
    ) if tracking is not None else None
    official_oil_mm = _preferred(
        official.smoothed_oil_air_level_mm_from_zero,
        official.raw_oil_air_level_mm_from_zero,
    ) if official is not None else None
    rerun_oil_mm = _preferred(
        tracking.smoothed_oil_air_level_mm_from_zero,
        tracking.raw_oil_air_level_mm_from_zero,
    ) if tracking is not None else None
    official_foam_px = _preferred(
        official.smoothed_foam_front_px_from_zero,
        official.raw_foam_front_px_from_zero,
    ) if official is not None else None
    rerun_foam_px = _preferred(
        tracking.smoothed_foam_front_px_from_zero,
        tracking.raw_foam_front_px_from_zero,
    ) if tracking is not None else None
    official_foam_mm = _preferred(
        official.smoothed_foam_front_mm_from_zero,
        official.raw_foam_front_mm_from_zero,
    ) if official is not None else None
    rerun_foam_mm = _preferred(
        tracking.smoothed_foam_front_mm_from_zero,
        tracking.raw_foam_front_mm_from_zero,
    ) if tracking is not None else None
    left_flags = set(official.flags) if official is not None else set()
    right_flags = set(tracking.flags) if tracking is not None else set()
    if official is None:
        status = "rerun_only"
    elif rerun is None:
        status = "official_only"
    elif tracking is None:
        status = "rerun_failed"
    else:
        status = "matched"
    return RedetectionComparisonPoint(
        nominal_timestamp_sec=float(nominal_timestamp),
        official_sample=official,
        rerun_sample=rerun,
        official_timestamp_sec=official.timestamp_sec if official is not None else None,
        rerun_actual_timestamp_sec=rerun.actual_timestamp_sec if rerun is not None else None,
        oil_position_delta_px=_delta(rerun_oil_px, official_oil_px),
        oil_position_delta_mm=_delta(rerun_oil_mm, official_oil_mm),
        foam_position_delta_px=_delta(rerun_foam_px, official_foam_px),
        foam_position_delta_mm=_delta(rerun_foam_mm, official_foam_mm),
        confidence_delta=_delta(
            tracking.overall_confidence if tracking is not None else None,
            official.overall_confidence if official is not None else None,
        ),
        fill_state_same=(
            tracking.fill_state == official.fill_state
            if tracking is not None and official is not None
            else None
        ),
        validity_same=(
            tracking.is_valid == official.is_valid
            if tracking is not None and official is not None
            else None
        ),
        flags_added=tuple(sorted(right_flags - left_flags)),
        flags_removed=tuple(sorted(left_flags - right_flags)),
        candidate_comparison_available=bool(candidate_available),
        match_status=status,
    )


def _preferred(preferred, fallback):
    return _finite(preferred) if _finite(preferred) is not None else _finite(fallback)


def _finite(value):
    if value is None:
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return None
    return converted if math.isfinite(converted) else None


def _delta(right, left):
    right_value = _finite(right)
    left_value = _finite(left)
    return None if right_value is None or left_value is None else right_value - left_value


def _mean(values):
    finite = [value for value in (_finite(value) for value in values) if value is not None]
    return fmean(finite) if finite else None


def _mean_abs(values):
    finite = [abs(value) for value in (_finite(value) for value in values) if value is not None]
    return fmean(finite) if finite else None


def _max_abs(values):
    finite = [abs(value) for value in (_finite(value) for value in values) if value is not None]
    return max(finite) if finite else None
