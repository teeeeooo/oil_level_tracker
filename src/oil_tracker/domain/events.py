from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable

from .enums import EventType, FillState
from .results import EventMarker, TrackingSample


@dataclass(frozen=True)
class DebounceConfig:
    minimum_duration_sec: float = 0.5
    low_confidence_threshold: float = 0.35
    movement_threshold_px: float = 1.0
    stable_recovery_sec: float = 1.0
    oil_drop_confirmation_sec: float = 1.5
    oil_drop_minimum_delta_px: float = 10.0
    oil_drop_baseline_sec: float = 1.5


def detect_events_for_glass(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    config: DebounceConfig | None = None,
) -> list[EventMarker]:
    """Convert a tracking time-series into debounced domain events.

    Image interpretation intentionally remains outside this module. Vision adapters
    provide semantic flags such as FOGGED_OR_GLARE and FOAM_REACH_TOP; this module
    applies duration/debounce rules and derives motion/crossing events from samples.
    """
    config = config or DebounceConfig()
    if not samples:
        return []
    events: list[EventMarker] = [
        EventMarker(
            run_id,
            glass_id,
            EventType.ANALYSIS_START,
            samples[0].timestamp_sec,
            representative_frame_index=samples[0].frame_index,
            confidence=1.0,
        ),
    ]

    _state_start_events(
        run_id,
        glass_id,
        samples,
        events,
        FillState.FULL_NO_INTERFACE,
        EventType.FULL_NO_INTERFACE_START,
        config.minimum_duration_sec,
    )
    _state_start_events(
        run_id,
        glass_id,
        samples,
        events,
        FillState.EMPTY_NO_INTERFACE,
        EventType.EMPTY_NO_INTERFACE_START,
        config.minimum_duration_sec,
    )
    _foam_events(run_id, glass_id, samples, events, config)
    _confidence_events(run_id, glass_id, samples, events, config)
    _flag_events(run_id, glass_id, samples, events, config)
    _crossing_events(run_id, glass_id, samples, events, config)
    _appearance_events(run_id, glass_id, samples, events)
    _oil_drop_event(run_id, glass_id, samples, events, config)

    r7_stream = _is_r7_stream(samples)
    numeric = [
        (sample, _oil_level(sample))
        for sample in samples
        if _oil_level(sample) is not None
        and (not r7_stream or _r7_anchor(sample))
    ]
    if numeric:
        maximum = max(numeric, key=lambda item: (float(item[1]), -item[0].timestamp_sec))[0]
        minimum = min(numeric, key=lambda item: (float(item[1]), item[0].timestamp_sec))[0]
        events.append(_event_from_sample(run_id, glass_id, EventType.MAXIMUM_OIL_LEVEL, maximum))
        events.append(_event_from_sample(run_id, glass_id, EventType.MINIMUM_OIL_LEVEL, minimum))

    events.append(
        EventMarker(
            run_id,
            glass_id,
            EventType.ANALYSIS_END,
            samples[-1].timestamp_sec,
            representative_frame_index=samples[-1].frame_index,
            confidence=1.0,
        )
    )
    return _deduplicate_and_sort(events)


def _state_start_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    state: FillState,
    event_type: EventType,
    minimum_duration: float,
) -> None:
    for start, end in _runs(samples, lambda s: s.fill_state == state):
        if _duration(start, end) >= minimum_duration or start is end:
            events.append(_event_from_sample(run_id, glass_id, event_type, start, end.timestamp_sec))


def _foam_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    config: DebounceConfig,
) -> None:
    foam_states = {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE}
    for start, end in _runs(
        samples,
        lambda s: s.fill_state in foam_states or s.smoothed_foam_front_px_from_zero is not None,
    ):
        if _duration(start, end) >= config.minimum_duration_sec or start is end:
            events.append(_event_from_sample(run_id, glass_id, EventType.FOAM_START, start, end.timestamp_sec))
            events.append(_event_from_sample(run_id, glass_id, EventType.FOAM_END, end))

    previous: TrackingSample | None = None
    rising_start: TrackingSample | None = None
    rising_last: TrackingSample | None = None
    for sample in samples:
        foam = sample.smoothed_foam_front_px_from_zero
        previous_foam = previous.smoothed_foam_front_px_from_zero if previous else None
        if foam is None or previous_foam is None:
            if rising_start is not None and rising_last is not None and _duration(rising_start, rising_last) >= config.minimum_duration_sec:
                events.append(_event_from_sample(run_id, glass_id, EventType.FOAM_FRONT_RISING, rising_start, rising_last.timestamp_sec))
            rising_start = rising_last = None
            previous = sample
            continue
        if foam > previous_foam + config.movement_threshold_px:
            rising_start = rising_start or sample
            rising_last = sample
        else:
            if rising_start is not None and rising_last is not None and _duration(rising_start, rising_last) >= config.minimum_duration_sec:
                events.append(_event_from_sample(run_id, glass_id, EventType.FOAM_FRONT_RISING, rising_start, rising_last.timestamp_sec))
            rising_start = rising_last = None
        if previous_foam < 0 <= foam:
            events.append(_event_from_sample(run_id, glass_id, EventType.FOAM_REACH_ZERO, sample))
        previous = sample
    if rising_start is not None and rising_last is not None and _duration(rising_start, rising_last) >= config.minimum_duration_sec:
        events.append(_event_from_sample(run_id, glass_id, EventType.FOAM_FRONT_RISING, rising_start, rising_last.timestamp_sec))


def _confidence_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    config: DebounceConfig,
) -> None:
    for start, end in _runs(samples, lambda s: s.overall_confidence < config.low_confidence_threshold):
        if _duration(start, end) >= config.minimum_duration_sec:
            events.append(_event_from_sample(run_id, glass_id, EventType.LOW_CONFIDENCE_START, start, end.timestamp_sec))
            events.append(_event_from_sample(run_id, glass_id, EventType.LOW_CONFIDENCE_END, end))
    for start, end in _runs(samples, lambda s: s.fill_state == FillState.UNKNOWN_REVIEW):
        if _duration(start, end) >= config.minimum_duration_sec:
            events.append(_event_from_sample(run_id, glass_id, EventType.REVIEW_REQUIRED, start, end.timestamp_sec))


def _flag_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    config: DebounceConfig,
) -> None:
    mappings = {
        "DETECTION_LOST": EventType.DETECTION_LOST,
        "FOGGED_OR_GLARE": EventType.FOGGED_OR_GLARE,
        "FOAM_REACH_TOP": EventType.FOAM_REACH_TOP,
    }
    for flag, event_type in mappings.items():
        for start, end in _runs(samples, lambda s, marker=flag: marker in s.flags):
            if _duration(start, end) >= config.minimum_duration_sec or start is end:
                events.append(_event_from_sample(run_id, glass_id, event_type, start, end.timestamp_sec))


def _crossing_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    config: DebounceConfig,
) -> None:
    previous: TrackingSample | None = None
    for index, current in enumerate(samples):
        curr = current.smoothed_oil_air_level_px_from_zero
        prev = previous.smoothed_oil_air_level_px_from_zero if previous else None
        if (
            curr is not None
            and prev is not None
            and _crossing_has_anchor_authority(samples, index)
        ):
            if prev < 0 <= curr:
                recovery_end = _continuous_condition_end(
                    samples,
                    index,
                    lambda s: s.smoothed_oil_air_level_px_from_zero is not None
                    and _numeric(s.smoothed_oil_air_level_px_from_zero) >= 0
                    and s.fill_state != FillState.UNKNOWN_REVIEW,
                )
                if _duration(current, recovery_end) >= config.minimum_duration_sec:
                    events.append(
                        _event_from_sample(
                            run_id,
                            glass_id,
                            EventType.ZERO_CROSS_UP,
                            current,
                        )
                    )
                if _duration(current, recovery_end) >= config.stable_recovery_sec:
                    events.append(
                        _event_from_sample(
                            run_id,
                            glass_id,
                            EventType.ZERO_STABLE_RECOVERY,
                            current,
                            recovery_end.timestamp_sec,
                        )
                    )
            elif prev >= 0 > curr:
                below_end = _continuous_condition_end(
                    samples,
                    index,
                    lambda s: s.smoothed_oil_air_level_px_from_zero is not None
                    and _numeric(s.smoothed_oil_air_level_px_from_zero) < 0
                    and s.fill_state != FillState.UNKNOWN_REVIEW,
                )
                if _duration(current, below_end) >= config.minimum_duration_sec:
                    events.append(
                        _event_from_sample(
                            run_id,
                            glass_id,
                            EventType.ZERO_CROSS_DOWN,
                            current,
                        )
                    )
        previous = current


def _appearance_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
) -> None:
    previous_state: FillState | None = None
    for sample in samples:
        has_authority = not _is_r7_sample(sample) or _r7_anchor(sample)
        if has_authority and sample.fill_state == FillState.DRAINING_VISIBLE and previous_state in {
            FillState.FULL_NO_INTERFACE,
            FillState.FULL_WITH_FOAM,
        }:
            events.append(_event_from_sample(run_id, glass_id, EventType.OIL_BOUNDARY_APPEARED_FROM_TOP, sample))
        if has_authority and sample.fill_state == FillState.FILLING_VISIBLE and previous_state == FillState.EMPTY_NO_INTERFACE:
            events.append(_event_from_sample(run_id, glass_id, EventType.OIL_BOUNDARY_APPEARED_FROM_BOTTOM, sample))
        previous_state = sample.fill_state


def _oil_drop_event(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    config: DebounceConfig,
) -> None:
    """Emit the first multi-sample decrease in engineering oil height."""

    required_duration = max(
        config.minimum_duration_sec,
        config.oil_drop_confirmation_sec,
    )
    required_delta = max(
        config.oil_drop_minimum_delta_px,
        config.movement_threshold_px * 3.0,
    )
    for run in _numeric_sample_runs(samples):
        for start_offset, start in enumerate(run[:-1]):
            if _duration(run[0], start) < config.oil_drop_baseline_sec:
                continue
            start_level = _oil_level(start)
            assert start_level is not None
            for end_offset in range(start_offset + 1, len(run)):
                end = run[end_offset]
                if _duration(start, end) < required_duration:
                    continue
                if _duration(start, end) > required_duration * 2.0:
                    break
                segment = run[start_offset : end_offset + 1]
                end_level = _oil_level(end)
                assert end_level is not None
                deltas = [
                    float(_oil_level(current)) - float(_oil_level(previous))
                    for previous, current in zip(segment, segment[1:])
                ]
                decreasing_steps = sum(
                    delta < -config.movement_threshold_px
                    for delta in deltas
                )
                required_steps = max(2, math.ceil(len(deltas) * 0.60))
                if (
                    float(start_level) - float(end_level) >= required_delta
                    and decreasing_steps >= required_steps
                ):
                    event_sample = start
                    if _is_r7_stream(samples):
                        anchors = tuple(
                            item for item in segment if _r7_anchor(item)
                        )
                        if len(anchors) < 2:
                            continue
                        anchor_start = _oil_level(anchors[0])
                        anchor_end = _oil_level(anchors[-1])
                        if (
                            anchor_start is None
                            or anchor_end is None
                            or float(anchor_start) - float(anchor_end)
                            < required_delta
                        ):
                            continue
                        event_sample = anchors[0]
                    events.append(
                        _event_from_sample(
                            run_id,
                            glass_id,
                            EventType.OIL_DROP_START,
                            event_sample,
                            end.timestamp_sec,
                        )
                    )
                    return


def _numeric_sample_runs(
    samples: list[TrackingSample],
) -> tuple[tuple[TrackingSample, ...], ...]:
    runs: list[tuple[TrackingSample, ...]] = []
    current: list[TrackingSample] = []
    for sample in samples:
        if _oil_level(sample) is None or sample.fill_state is FillState.UNKNOWN_REVIEW:
            if current:
                runs.append(tuple(current))
                current = []
            continue
        current.append(sample)
    if current:
        runs.append(tuple(current))
    return tuple(runs)


def _crossing_has_anchor_authority(
    samples: list[TrackingSample],
    index: int,
) -> bool:
    if not _is_r7_stream(samples):
        return True
    start = index - 1
    while (
        start > 0
        and _oil_level(samples[start - 1]) is not None
        and samples[start - 1].fill_state is not FillState.UNKNOWN_REVIEW
    ):
        start -= 1
    end = index
    while (
        end + 1 < len(samples)
        and _oil_level(samples[end + 1]) is not None
        and samples[end + 1].fill_state is not FillState.UNKNOWN_REVIEW
    ):
        end += 1
    return bool(
        any(_r7_anchor(sample) for sample in samples[start : index + 1])
        and any(_r7_anchor(sample) for sample in samples[index : end + 1])
    )


def _is_r7_stream(samples: Iterable[TrackingSample]) -> bool:
    return any(_is_r7_sample(sample) for sample in samples)


def _is_r7_sample(sample: TrackingSample) -> bool:
    return any(
        str(flag).strip().upper().startswith("R7_")
        for flag in sample.flags
    )


def _r7_anchor(sample: TrackingSample) -> bool:
    return "R7_OIL_ANCHOR" in {
        str(flag).strip().upper() for flag in sample.flags
    }


def _continuous_condition_end(
    samples: list[TrackingSample],
    start_index: int,
    predicate: Callable[[TrackingSample], bool],
) -> TrackingSample:
    end = samples[start_index]
    for sample in samples[start_index:]:
        if not predicate(sample):
            break
        end = sample
    return end


def _runs(
    samples: Iterable[TrackingSample],
    predicate: Callable[[TrackingSample], bool],
):
    start: TrackingSample | None = None
    last: TrackingSample | None = None
    for sample in samples:
        if predicate(sample):
            start = start or sample
            last = sample
        elif start is not None and last is not None:
            yield start, last
            start = last = None
    if start is not None and last is not None:
        yield start, last


def _duration(start: TrackingSample, end: TrackingSample) -> float:
    return max(0.0, end.timestamp_sec - start.timestamp_sec)


def _numeric(value: float | None) -> float:
    return float(value) if value is not None else 0.0


def _deduplicate_and_sort(events: list[EventMarker]) -> list[EventMarker]:
    seen: set[tuple[EventType, float, float | None]] = set()
    output: list[EventMarker] = []
    for event in sorted(events, key=lambda e: (e.start_time_sec, e.event_type.value)):
        key = (event.event_type, round(event.start_time_sec, 6), None if event.end_time_sec is None else round(event.end_time_sec, 6))
        if key not in seen:
            seen.add(key)
            output.append(event)
    return output


def _event_from_sample(
    run_id: str,
    glass_id: str,
    event_type: EventType,
    sample: TrackingSample,
    end_time: float | None = None,
) -> EventMarker:
    return EventMarker(
        run_id=run_id,
        glass_id=glass_id,
        event_type=event_type,
        start_time_sec=sample.timestamp_sec,
        end_time_sec=end_time,
        representative_frame_index=sample.frame_index,
        oil_level_px=_oil_level(sample),
        oil_level_mm=_finite_first(
            sample.smoothed_oil_air_level_mm_from_zero,
            sample.raw_oil_air_level_mm_from_zero,
        ),
        foam_front_px=_finite_first(
            sample.smoothed_foam_front_px_from_zero,
            sample.raw_foam_front_px_from_zero,
        ),
        foam_front_mm=_finite_first(
            sample.smoothed_foam_front_mm_from_zero,
            sample.raw_foam_front_mm_from_zero,
        ),
        confidence=sample.overall_confidence,
    )


def _oil_level(sample: TrackingSample) -> float | None:
    return _finite_first(
        sample.smoothed_oil_air_level_px_from_zero,
        sample.raw_oil_air_level_px_from_zero,
    )


def _finite_first(*values: float | None) -> float | None:
    for value in values:
        if value is None:
            continue
        number = float(value)
        if math.isfinite(number):
            return number
    return None
