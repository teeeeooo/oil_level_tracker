from __future__ import annotations

from collections.abc import Iterable, MutableMapping, Sequence
from typing import Any

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import GlassInspectionConfig
from oil_tracker.domain.results import TrackingSample


DecodedFrame = tuple[Any, int, float]


def static_artifact_sample_timestamps(schedule: Sequence[float]) -> tuple[float, ...]:
    """Return the official start/middle/end preparation timestamps deterministically."""
    if len(schedule) < 2:
        return ()
    indices = sorted({0, len(schedule) // 2, len(schedule) - 1})
    return tuple(float(schedule[index]) for index in indices)


def learn_static_artifacts(
    reader,
    detector,
    glasses: Iterable[GlassInspectionConfig],
    schedule: Sequence[float],
    *,
    decoded_frame_cache: MutableMapping[float, DecodedFrame] | None = None,
) -> tuple[float, ...]:
    """Prepare a detector using the official representative-frame policy.

    Decode failures are intentionally skipped. Re-detection may provide a bounded
    cache so representative timestamps that also belong to its processing schedule
    are decoded only once. The official pipeline leaves the cache unset and retains
    its established behavior.
    """
    learn = getattr(detector, "learn_static_artifact", None)
    targets = static_artifact_sample_timestamps(schedule)
    if learn is None or not targets:
        return ()
    frames = []
    decoded_targets: list[float] = []
    for target in targets:
        try:
            decoded = reader.read_at(target)
        except Exception:
            continue
        frame, _frame_index, _actual_timestamp = decoded
        frames.append(frame)
        decoded_targets.append(target)
        if decoded_frame_cache is not None:
            decoded_frame_cache[target] = decoded
    if not frames:
        return ()
    for glass in tuple(glasses):
        learn(frames, glass)
    return tuple(decoded_targets)


def tracking_sample_from_detection(
    run_id: str,
    glass: GlassInspectionConfig,
    detection,
) -> TrackingSample:
    """Convert a detector result without changing the official analysis semantics."""
    zero = glass.geometry.zero_line_y
    mm_per_pixel = glass.mm_per_pixel
    raw_oil_px = (
        None
        if detection.raw_oil_air_level_y is None or zero is None
        else zero - detection.raw_oil_air_level_y
    )
    raw_foam_px = (
        None
        if detection.raw_foam_front_y is None or zero is None
        else zero - detection.raw_foam_front_y
    )
    oil_px = detection.oil_air_level_px_from_zero
    foam_px = detection.foam_front_px_from_zero
    explicit_state = detection.fill_state in {
        FillState.FULL_NO_INTERFACE,
        FillState.EMPTY_NO_INTERFACE,
    }
    flags = {str(flag).strip().upper() for flag in detection.flags}
    sequence_state = "SEQUENCE_RESOLVED_STATE" in flags
    image_supported_state = explicit_state and (
        not sequence_state or "R6_IMAGE_SUPPORTED_STATE" in flags
    )
    visible_valid = detection.fill_state is not FillState.UNKNOWN_REVIEW and (
        oil_px is not None or detection.fill_state is FillState.FULL_WITH_FOAM
    )
    valid = (
        detection.overall_confidence >= glass.detector_settings.minimum_final_confidence
        and (image_supported_state or visible_valid)
    )
    return TrackingSample(
        run_id=run_id,
        glass_id=glass.id,
        frame_index=detection.frame_index,
        timestamp_sec=detection.time_sec,
        fill_state=detection.fill_state,
        raw_oil_air_level_y=detection.raw_oil_air_level_y,
        raw_oil_air_level_px_from_zero=raw_oil_px,
        raw_oil_air_level_mm_from_zero=(
            None if raw_oil_px is None or mm_per_pixel is None else raw_oil_px * mm_per_pixel
        ),
        smoothed_oil_air_level_px_from_zero=oil_px,
        smoothed_oil_air_level_mm_from_zero=detection.oil_air_level_mm_from_zero,
        oil_air_confidence=detection.oil_air_confidence,
        raw_foam_front_y=detection.raw_foam_front_y,
        raw_foam_front_px_from_zero=raw_foam_px,
        raw_foam_front_mm_from_zero=(
            None if raw_foam_px is None or mm_per_pixel is None else raw_foam_px * mm_per_pixel
        ),
        smoothed_foam_front_px_from_zero=foam_px,
        smoothed_foam_front_mm_from_zero=detection.foam_front_mm_from_zero,
        foam_confidence=detection.foam_confidence,
        visibility_confidence=detection.visibility_confidence,
        overall_confidence=detection.overall_confidence,
        is_valid=valid,
        flags=list(detection.flags),
    )


def effective_observation_height(glass: GlassInspectionConfig) -> float:
    full_height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    return max(
        1.0,
        full_height * max(0.05, 1.0 - float(glass.geometry.margin_ratio) * 2.0),
    )
