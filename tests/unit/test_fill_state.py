from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.enums import FillState, InitialObservationState
from tests.fixtures.synthetic import empty_frame, full_frame, glare_frame, glass_config, partial_frame


def test_full_does_not_force_numeric_interface():
    glass = glass_config(); glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    detection, _ = OpenCvPhaseDetector().detect(full_frame(), glass, 0, 0)
    assert detection.fill_state == FillState.FULL_NO_INTERFACE
    assert detection.oil_air_level_y is None


def test_empty_does_not_force_numeric_interface():
    glass = glass_config(); glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
    detection, _ = OpenCvPhaseDetector().detect(empty_frame(), glass, 0, 0)
    assert detection.fill_state == FillState.EMPTY_NO_INTERFACE
    assert detection.oil_air_level_y is None


def test_partial_boundary_is_selected():
    glass = glass_config(); detection, _ = OpenCvPhaseDetector().detect(partial_frame(130), glass, 0, 0)
    assert detection.oil_air_level_y is not None
    assert abs(detection.oil_air_level_y - 130) < 8


def test_glare_becomes_unknown_review():
    glass = glass_config(); detection, _ = OpenCvPhaseDetector().detect(glare_frame(), glass, 0, 0)
    assert detection.fill_state == FillState.UNKNOWN_REVIEW


def test_full_prior_keeps_mid_glass_reflection_ambiguous_without_numeric_output():
    import cv2

    frame = full_frame()
    cv2.line(frame, (100, 120), (220, 120), (150, 150, 150), 2)
    glass = glass_config()
    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    detection, _ = OpenCvPhaseDetector().detect(frame, glass, 0, 0)
    assert detection.fill_state == FillState.UNKNOWN_REVIEW
    assert detection.oil_air_level_y is None
    assert "OIL_EVIDENCE_AMBIGUOUS" in detection.flags
    assert all(
        not candidate.selected
        for candidate in detection.candidates
        if candidate.kind.value == "oil_air"
    )


def test_boundary_appearing_from_top_is_draining_visible():
    glass = glass_config(); glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    detection, _ = OpenCvPhaseDetector().detect(partial_frame(45), glass, 0, 0)
    assert detection.fill_state == FillState.DRAINING_VISIBLE
    assert detection.oil_air_level_y is not None


def test_near_bottom_boundary_ambiguity_does_not_become_oil_or_foam():
    glass = glass_config()
    glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
    detection, _ = OpenCvPhaseDetector().detect(partial_frame(200), glass, 0, 0)
    assert detection.fill_state == FillState.UNKNOWN_REVIEW
    assert detection.oil_air_level_y is None
    assert detection.foam_front_y is None
    assert "OIL_EVIDENCE_AMBIGUOUS" in detection.flags
