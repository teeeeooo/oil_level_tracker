from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe


def glass(initial=InitialObservationState.AUTO):
    value = InspectionRecipe.default_glass(320, 240)
    value.id = "glass-oil"
    value.geometry.zero_line_y = 150.0
    value.initial_state = initial
    value.detector_settings.minimum_final_confidence = 0.35
    value.detector_settings.oil_tracker_update_confidence = 0.45
    value.detector_settings.oil_path_min_margin = 0.04
    value.detector_settings.oil_reacquire_frames = 2
    return value


def oil_frame(y: int = 130, *, above=175, below=70):
    frame = np.full((240, 320, 3), 55, dtype=np.uint8)
    frame[78:186, 122:198] = above
    frame[y:186, 122:198] = below
    frame[y - 1 : y + 2, 122:198] = 225
    return frame


def uniform_frame(value: int):
    frame = np.full((240, 320, 3), 55, dtype=np.uint8)
    frame[78:186, 122:198] = value
    return frame


def test_detector_version_and_canonical_coordinates_and_debug_evidence():
    detector = OpenCvPhaseDetector()
    frame = oil_frame(130)
    before = frame.copy()
    detection, artifacts = detector.detect(frame, glass(), 1, 0.0, debug=True)
    assert detector.version == "opencv-phase-detector-s5b-oil-v3"
    assert np.array_equal(frame, before)
    assert detection.raw_oil_air_level_y is not None
    assert abs(detection.raw_oil_air_level_y - 130.0) <= 4.0
    assert detection.smoothed_oil_air_level_y == detection.raw_oil_air_level_y
    assert detection.oil_air_level_px_from_zero == 150.0 - detection.smoothed_oil_air_level_y
    assert artifacts is not None
    assert {
        "oil_signed_sobel_profile",
        "oil_signed_contrast_profile",
        "oil_horizontal_coverage_profile",
        "oil_consensus_support_profile",
        "oil_static_overlap_profile",
    } <= set(artifacts.profiles)
    assert detection.debug_metrics["oil_decision_status"] == "accepted_boundary"
    consensus = [item for item in detection.candidates if item.source == "oil_consensus"]
    assert consensus
    assert all("local_y" in item.features and "source_y" in item.features for item in consensus)


def test_no_interface_never_returns_numeric_boundary():
    detector = OpenCvPhaseDetector()
    config = glass(InitialObservationState.FULL_NO_INTERFACE)
    first, artifacts = detector.detect(uniform_frame(75), config, 1, 0.0, debug=True)
    second, _ = detector.detect(uniform_frame(75), config, 2, 0.5, debug=False)
    assert first.raw_oil_air_level_y is None
    assert first.smoothed_oil_air_level_y is None
    assert second.raw_oil_air_level_y is None
    assert second.smoothed_oil_air_level_y is None
    assert second.fill_state in {FillState.FULL_NO_INTERFACE, FillState.UNKNOWN_REVIEW}
    assert artifacts is not None
    assert first.debug_metrics["oil_no_interface_score"] >= 0.0


def test_one_frame_dropout_has_no_stale_numeric_output_and_recovers():
    detector = OpenCvPhaseDetector()
    config = glass()
    accepted, _ = detector.detect(oil_frame(130), config, 1, 0.0)
    assert accepted.raw_oil_air_level_y is not None
    missing, _ = detector.detect(uniform_frame(115), config, 2, 0.5)
    assert missing.raw_oil_air_level_y is None
    assert missing.smoothed_oil_air_level_y is None
    recovered, _ = detector.detect(oil_frame(132), config, 3, 1.0)
    assert recovered.raw_oil_air_level_y is not None
    assert abs(recovered.raw_oil_air_level_y - 132.0) <= 4.0


def test_per_glass_and_full_reset_clear_path_and_smoothing_state():
    detector = OpenCvPhaseDetector()
    first = glass()
    second = glass()
    second.id = "glass-two"
    detector.detect(oil_frame(130), first, 1, 0.0)
    detector.detect(oil_frame(140), second, 1, 0.0)
    assert detector.oil_temporal_state_count == 2
    assert detector.oil_path_for(first.id).accepted_y is not None
    detector.reset(first.id)
    assert detector.oil_temporal_state_count == 1
    assert detector.oil_path_for(first.id) is None
    assert detector.oil_path_for(second.id) is not None
    detector.reset()
    assert detector.oil_temporal_state_count == 0
    assert detector.foam_temporal_state_count == 0


def test_static_map_input_frames_are_not_mutated_and_dynamic_boundary_can_reappear():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = uniform_frame(80)
    static[150:154, 122:198] = 205
    before = static.copy()
    detector.learn_static_artifact([static], config)
    assert np.array_equal(static, before)
    detection, _ = detector.detect(oil_frame(130), config, 1, 0.0, debug=True)
    assert detection.raw_oil_air_level_y is not None
    assert abs(detection.raw_oil_air_level_y - 130.0) <= 4.0
    consensus = [item for item in detection.candidates if item.source == "oil_consensus"]
    assert any("static_overlap" in item.features for item in consensus)
