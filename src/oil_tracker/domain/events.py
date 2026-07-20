from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .enums import EventType, FillState
from .results import EventMarker, TrackingSample


@dataclass(frozen=True)
class DebounceConfig:
    minimum_duration_sec: float = 0.5
    low_confidence_threshold: float = 0.35
    movement_threshold_px: float = 1.0
    stable_recovery_sec: float = 1.0


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

    numeric = [s for s in samples if s.smoothed_oil_air_level_px_from_zero is not None]
    if numeric:
        minimum = min(numeric, key=lambda s: _numeric(s.smoothed_oil_air_level_px_from_zero))
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
        if curr is not None and prev is not None:
            if prev < 0 <= curr:
                events.append(_event_from_sample(run_id, glass_id, EventType.ZERO_CROSS_UP, current))
                recovery_end = _continuous_condition_end(
                    samples,
                    index,
                    lambda s: s.smoothed_oil_air_level_px_from_zero is not None
                    and _numeric(s.smoothed_oil_air_level_px_from_zero) >= 0
                    and s.fill_state != FillState.UNKNOWN_REVIEW,
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
                events.append(_event_from_sample(run_id, glass_id, EventType.ZERO_CROSS_DOWN, current))
        previous = current


def _appearance_events(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
) -> None:
    previous_state: FillState | None = None
    for sample in samples:
        if sample.fill_state == FillState.DRAINING_VISIBLE and previous_state in {
            FillState.FULL_NO_INTERFACE,
            FillState.FULL_WITH_FOAM,
        }:
            events.append(_event_from_sample(run_id, glass_id, EventType.OIL_BOUNDARY_APPEARED_FROM_TOP, sample))
        if sample.fill_state == FillState.FILLING_VISIBLE and previous_state == FillState.EMPTY_NO_INTERFACE:
            events.append(_event_from_sample(run_id, glass_id, EventType.OIL_BOUNDARY_APPEARED_FROM_BOTTOM, sample))
        previous_state = sample.fill_state


def _oil_drop_event(
    run_id: str,
    glass_id: str,
    samples: list[TrackingSample],
    events: list[EventMarker],
    config: DebounceConfig,
) -> None:
    """Emit the first sustained decrease in engineering oil height."""
    start: TrackingSample | None = None
    last: TrackingSample | None = None
    previous: TrackingSample | None = None
    for sample in samples:
        level = sample.smoothed_oil_air_level_px_from_zero
        prior_level = previous.smoothed_oil_air_level_px_from_zero if previous else None
        decreasing = (
            level is not None
            and prior_level is not None
            and _numeric(level) < _numeric(prior_level) - config.movement_threshold_px
        )
        if decreasing:
            start = start or previous or sample
            last = sample
            if start is not None and last is not None and _duration(start, last) >= config.minimum_duration_sec:
                events.append(_event_from_sample(run_id, glass_id, EventType.OIL_DROP_START, start, last.timestamp_sec))
                return
        else:
            start = last = None
        previous = sample


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
        oil_level_px=sample.smoothed_oil_air_level_px_from_zero,
        oil_level_mm=sample.smoothed_oil_air_level_mm_from_zero,
        foam_front_px=sample.smoothed_foam_front_px_from_zero,
        foam_front_mm=sample.smoothed_foam_front_mm_from_zero,
        confidence=sample.overall_confidence,
    )
