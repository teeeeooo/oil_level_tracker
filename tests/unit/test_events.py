from oil_tracker.domain.enums import EventType, FillState
from oil_tracker.domain.events import DebounceConfig, detect_events_for_glass
from oil_tracker.domain.results import TrackingSample


def s(t, state=FillState.PARTIAL_VISIBLE, confidence=.9, level=1):
    return TrackingSample("r", "g", int(t*10), t, state, smoothed_oil_air_level_px_from_zero=level, overall_confidence=confidence, is_valid=True)


def test_single_frame_low_confidence_is_debounced():
    events = detect_events_for_glass("r", "g", [s(0), s(.1, confidence=.1), s(.2)], DebounceConfig(.5, .35))
    assert EventType.LOW_CONFIDENCE_START not in [e.event_type for e in events]


def test_zero_cross_events():
    events = detect_events_for_glass("r", "g", [s(0, level=-1), s(1, level=2), s(2, level=-1)])
    types = [e.event_type for e in events]
    assert EventType.ZERO_CROSS_UP in types
    assert EventType.ZERO_CROSS_DOWN in types


def test_oil_drop_and_stable_recovery_events():
    samples = [
        s(0.0, level=4),
        s(0.5, level=2),
        s(1.0, level=-2),
        s(1.5, level=1),
        s(2.0, level=2),
        s(2.5, level=2),
    ]
    events = detect_events_for_glass(
        "r", "g", samples,
        DebounceConfig(minimum_duration_sec=.5, movement_threshold_px=.5, stable_recovery_sec=1.0),
    )
    types = [e.event_type for e in events]
    assert EventType.OIL_DROP_START in types
    assert EventType.ZERO_STABLE_RECOVERY in types


def test_semantic_flag_events_are_emitted():
    samples = [s(0), s(.5), s(1.0)]
    for sample in samples:
        sample.flags = ["DETECTION_LOST", "FOGGED_OR_GLARE", "FOAM_REACH_TOP"]
    events = detect_events_for_glass("r", "g", samples, DebounceConfig(.5, .35))
    types = [e.event_type for e in events]
    assert EventType.DETECTION_LOST in types
    assert EventType.FOGGED_OR_GLARE in types
    assert EventType.FOAM_REACH_TOP in types
