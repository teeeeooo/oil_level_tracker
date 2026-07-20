from __future__ import annotations

import pytest

from oil_tracker.application.services.debug_capture_policy import DebugCapturePolicy
from oil_tracker.domain.debug_trace import DebugCaptureReason
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.session import DebugTraceLevel


def _candidate(score=0.8, *, selected=False, rejected=False, kind=BoundaryKind.OIL_AIR):
    return BoundaryCandidate(
        source="test",
        kind=kind,
        y=100.0,
        final_score=score,
        feature_score=score,
        selected=selected,
        rejected=rejected,
        reject_reason="bad" if rejected else "",
    )


def _detection(
    *,
    state=FillState.PARTIAL_VISIBLE,
    confidence=0.9,
    flags=None,
    oil=100.0,
    foam=None,
    candidates=None,
):
    return PhaseDetection(
        glass_id="g1",
        frame_index=1,
        time_sec=1.0,
        fill_state=state,
        oil_air_level_y=oil,
        oil_air_level_px_from_zero=0.0 if oil is not None else None,
        oil_air_level_mm_from_zero=None,
        foam_front_y=foam,
        foam_front_px_from_zero=None,
        foam_front_mm_from_zero=None,
        oil_air_confidence=confidence,
        foam_confidence=0.5 if foam is not None else 0.0,
        visibility_confidence=0.9,
        overall_confidence=confidence,
        raw_oil_air_level_y=oil,
        raw_foam_front_y=foam,
        smoothed_oil_air_level_y=oil,
        smoothed_foam_front_y=foam,
        candidates=list(candidates if candidates is not None else [_candidate(selected=True)]),
        flags=list(flags or []),
    )


def _reasons(**kwargs):
    decision = DebugCapturePolicy().decide(
        DebugTraceLevel.BASIC,
        kwargs.pop("detection", _detection()),
        is_valid=kwargs.pop("is_valid", True),
        minimum_confidence=kwargs.pop("minimum_confidence", 0.5),
        effective_height=kwargs.pop("effective_height", 100.0),
        **kwargs,
    )
    return set(decision.reasons)


@pytest.mark.parametrize(
    ("argument", "reason"),
    [
        ("first_sample", DebugCaptureReason.FIRST_SAMPLE),
        ("last_sample", DebugCaptureReason.LAST_SAMPLE),
        ("compressor_nearest", DebugCaptureReason.COMPRESSOR_NEAREST),
    ],
)
def test_semantic_markers_are_captured(argument, reason):
    assert reason in _reasons(**{argument: True})


def test_invalid_and_low_confidence_are_captured():
    reasons = _reasons(detection=_detection(confidence=0.2), is_valid=False)
    assert {DebugCaptureReason.INVALID, DebugCaptureReason.LOW_CONFIDENCE} <= reasons


def test_unknown_review_and_detection_lost_are_captured():
    reasons = _reasons(detection=_detection(state=FillState.UNKNOWN_REVIEW, flags=["DETECTION_LOST"]))
    assert {DebugCaptureReason.UNKNOWN_REVIEW, DebugCaptureReason.DETECTION_LOST} <= reasons


def test_glare_and_foam_are_captured():
    reasons = _reasons(detection=_detection(flags=["FOGGED_OR_GLARE", "FOAM_PRESENT"], foam=140.0))
    assert {DebugCaptureReason.GLARE_OR_FOG, DebugCaptureReason.FOAM} <= reasons


def test_oil_and_foam_jump_are_normalized_by_effective_height():
    previous = _detection(oil=100.0, foam=120.0)
    current = _detection(oil=130.0, foam=150.0)
    reasons = _reasons(detection=current, previous_detection=previous, effective_height=100.0)
    assert {DebugCaptureReason.OIL_POSITION_JUMP, DebugCaptureReason.FOAM_POSITION_JUMP} <= reasons


def test_missing_position_does_not_create_jump():
    previous = _detection(oil=None, foam=None)
    current = _detection(oil=130.0, foam=150.0)
    reasons = _reasons(detection=current, previous_detection=previous)
    assert DebugCaptureReason.OIL_POSITION_JUMP not in reasons
    assert DebugCaptureReason.FOAM_POSITION_JUMP not in reasons


def test_state_transition_is_captured():
    reasons = _reasons(
        detection=_detection(state=FillState.FULL_NO_INTERFACE),
        previous_detection=_detection(state=FillState.PARTIAL_VISIBLE),
    )
    assert DebugCaptureReason.STATE_TRANSITION in reasons


def test_candidate_ambiguity_only_compares_eligible_oil_candidates():
    candidates = [
        _candidate(0.80, selected=True),
        _candidate(0.76),
        _candidate(0.79, kind=BoundaryKind.FOAM_FRONT),
        _candidate(0.795, rejected=True),
    ]
    reasons = _reasons(detection=_detection(candidates=candidates))
    assert DebugCaptureReason.CANDIDATE_AMBIGUITY in reasons


def test_rejected_and_foam_candidates_do_not_create_oil_ambiguity():
    candidates = [
        _candidate(0.80, selected=True),
        _candidate(0.79, rejected=True),
        _candidate(0.795, kind=BoundaryKind.FOAM_FRONT),
    ]
    reasons = _reasons(detection=_detection(candidates=candidates))
    assert DebugCaptureReason.CANDIDATE_AMBIGUITY not in reasons


def test_no_selected_and_rejected_only_have_distinct_reasons():
    reasons = _reasons(detection=_detection(candidates=[_candidate(0.2, rejected=True)]))
    assert {DebugCaptureReason.NO_SELECTED_CANDIDATE, DebugCaptureReason.REJECTED_ONLY} <= reasons


def test_normal_sample_is_not_captured_in_basic():
    decision = DebugCapturePolicy().decide(
        DebugTraceLevel.BASIC,
        _detection(),
        is_valid=True,
        minimum_confidence=0.5,
        effective_height=100.0,
    )
    assert decision.capture is False
    assert decision.reasons == ()


def test_full_always_captures_and_none_never_captures():
    policy = DebugCapturePolicy()
    detection = _detection()
    full = policy.decide(DebugTraceLevel.FULL, detection, is_valid=True, minimum_confidence=0.5, effective_height=100.0)
    none = policy.decide(DebugTraceLevel.NONE, detection, is_valid=False, minimum_confidence=0.5, effective_height=100.0, first_sample=True)
    assert full.capture and DebugCaptureReason.FULL_TRACE in full.reasons
    assert not none.capture and none.reasons == ()


def test_multiple_reasons_are_deduplicated_and_ordered():
    decision = DebugCapturePolicy().decide(
        DebugTraceLevel.BASIC,
        _detection(confidence=0.1, flags=["LOW_CONFIDENCE", "LOW_CONFIDENCE"]),
        is_valid=False,
        minimum_confidence=0.5,
        effective_height=100.0,
        first_sample=True,
    )
    assert len(decision.reasons) == len(set(decision.reasons))
    assert decision.reasons[0] is DebugCaptureReason.FIRST_SAMPLE
