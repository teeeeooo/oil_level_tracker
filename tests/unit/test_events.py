from oil_tracker.domain.enums import EventType, FillState
from oil_tracker.domain.events import DebounceConfig, detect_events_for_glass
from oil_tracker.domain.results import TrackingSample


def s(t, state=FillState.PARTIAL_VISIBLE, confidence=.9, level=1, flags=()):
    return TrackingSample(
        "r",
        "g",
        int(t * 10),
        t,
        state,
        smoothed_oil_air_level_px_from_zero=level,
        overall_confidence=confidence,
        is_valid=True,
        flags=list(flags),
    )


def test_single_frame_low_confidence_is_debounced():
    events = detect_events_for_glass("r", "g", [s(0), s(.1, confidence=.1), s(.2)], DebounceConfig(.5, .35))
    assert EventType.LOW_CONFIDENCE_START not in [e.event_type for e in events]


def test_zero_cross_events():
    events = detect_events_for_glass(
        "r",
        "g",
        [
            s(0, level=-1),
            s(1, level=2),
            s(1.5, level=2),
            s(2, level=-1),
            s(2.5, level=-1),
        ],
    )
    types = [e.event_type for e in events]
    assert EventType.ZERO_CROSS_UP in types
    assert EventType.ZERO_CROSS_DOWN in types


def test_oil_drop_and_stable_recovery_events():
    samples = [
        s(0.0, level=8),
        s(0.5, level=8),
        s(1.0, level=8),
        s(1.5, level=8),
        s(2.0, level=4),
        s(2.5, level=-2),
        s(3.0, level=-3),
        s(3.5, level=1),
        s(4.0, level=2),
        s(4.5, level=2),
    ]
    events = detect_events_for_glass(
        "r", "g", samples,
        DebounceConfig(minimum_duration_sec=.5, movement_threshold_px=.5, stable_recovery_sec=1.0),
    )
    types = [e.event_type for e in events]
    assert EventType.OIL_DROP_START in types
    assert EventType.ZERO_STABLE_RECOVERY in types


def test_single_step_oil_jitter_does_not_start_drop_event():
    samples = [
        s(0.0, level=10),
        s(0.5, level=5),
        s(1.0, level=11),
        s(1.5, level=10),
        s(2.0, level=12),
    ]

    events = detect_events_for_glass("r", "g", samples)

    assert EventType.OIL_DROP_START not in [event.event_type for event in events]


def test_semantic_flag_events_are_emitted():
    samples = [s(0), s(.5), s(1.0)]
    for sample in samples:
        sample.flags = ["DETECTION_LOST", "FOGGED_OR_GLARE", "FOAM_REACH_TOP"]
    events = detect_events_for_glass("r", "g", samples, DebounceConfig(.5, .35))
    types = [e.event_type for e in events]
    assert EventType.DETECTION_LOST in types
    assert EventType.FOGGED_OR_GLARE in types
    assert EventType.FOAM_REACH_TOP in types


def test_observed_extrema_include_maximum_and_minimum_with_raw_fallback():
    samples = [s(0.0, level=2.0), s(1.0, level=-3.0), s(2.0, level=7.0)]
    samples[0].smoothed_oil_air_level_px_from_zero = None
    samples[0].raw_oil_air_level_px_from_zero = 2.0

    events = detect_events_for_glass("r", "g", samples)
    maximum = next(event for event in events if event.event_type is EventType.MAXIMUM_OIL_LEVEL)
    minimum = next(event for event in events if event.event_type is EventType.MINIMUM_OIL_LEVEL)

    assert (maximum.start_time_sec, maximum.oil_level_px) == (2.0, 7.0)
    assert (minimum.start_time_sec, minimum.oil_level_px) == (1.0, -3.0)


def test_r7_extrema_ignore_continuation_only_outliers() -> None:
    anchor = ("R7_RESOLVED_OIL", "R7_OIL_ANCHOR")
    continuation = ("R7_RESOLVED_OIL", "R7_OIL_CONTINUATION")
    samples = [
        s(0.0, level=5.0, flags=anchor),
        s(0.5, level=100.0, flags=continuation),
        s(1.0, level=-100.0, flags=continuation),
        s(1.5, level=0.0, flags=anchor),
    ]

    events = detect_events_for_glass("r", "g", samples)
    maximum = next(
        event for event in events if event.event_type is EventType.MAXIMUM_OIL_LEVEL
    )
    minimum = next(
        event for event in events if event.event_type is EventType.MINIMUM_OIL_LEVEL
    )

    assert (maximum.start_time_sec, maximum.oil_level_px) == (0.0, 5.0)
    assert (minimum.start_time_sec, minimum.oil_level_px) == (1.5, 0.0)


def test_r7_continuation_only_motion_cannot_create_drop_or_crossing() -> None:
    continuation = ("R7_RESOLVED_OIL", "R7_OIL_CONTINUATION")
    samples = [
        s(0.0, level=20.0, flags=continuation),
        s(0.5, level=15.0, flags=continuation),
        s(1.0, level=5.0, flags=continuation),
        s(1.5, level=-5.0, flags=continuation),
        s(2.0, level=-10.0, flags=continuation),
    ]

    events = detect_events_for_glass(
        "r",
        "g",
        samples,
        DebounceConfig(movement_threshold_px=0.5),
    )
    types = {event.event_type for event in events}

    assert EventType.OIL_DROP_START not in types
    assert EventType.ZERO_CROSS_DOWN not in types
