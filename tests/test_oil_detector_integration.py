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
    # Keep the entire effective ellipse uniform above the contract boundary. A
    # rectangular patch would add an unintended four-source structural line.
    frame = np.full((240, 320, 3), above, dtype=np.uint8)
    frame[y:] = below
    frame[y - 1 : y + 2] = 225
    return frame


def uniform_frame(value: int):
    return np.full((240, 320, 3), value, dtype=np.uint8)


def multi_edge_static_band(
    *,
    offset: int = 0,
    background: int = 95,
    x_start: int = 0,
    x_stop: int = 320,
):
    frame = uniform_frame(background)
    for y, value in (
        (108 + offset, 180),
        (112 + offset, 70),
        (116 + offset, 190),
        (120 + offset, 75),
    ):
        frame[y - 1 : y + 2, x_start:x_stop] = value
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
    missing, _ = detector.detect(uniform_frame(135), config, 2, 0.5)
    assert missing.raw_oil_air_level_y is None
    assert missing.smoothed_oil_air_level_y is None
    assert missing.fill_state is FillState.UNKNOWN_REVIEW
    assert "REVIEW_REQUIRED" in missing.flags
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


def test_static_map_structure_is_not_false_boundary_and_real_boundary_can_reappear():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = uniform_frame(80)
    static[150:154] = 205
    before = static.copy()
    detector.learn_static_artifact([static], config)
    assert np.array_equal(static, before)
    structure_only, _ = detector.detect(static, config, 1, 0.0, debug=True)
    assert structure_only.raw_oil_air_level_y is None
    assert structure_only.smoothed_oil_air_level_y is None
    detection, _ = detector.detect(oil_frame(130), config, 2, 0.5, debug=True)
    assert detection.raw_oil_air_level_y is not None
    assert abs(detection.raw_oil_air_level_y - 130.0) <= 4.0
    consensus = [item for item in detection.candidates if item.source == "oil_consensus"]
    assert any("static_overlap" in item.features for item in consensus)


def test_multi_edge_static_band_never_produces_numeric_oil_output():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = multi_edge_static_band()
    detector.learn_static_artifact([static, static.copy(), static.copy()], config)

    for index in range(3):
        detection, _ = detector.detect(
            static,
            config,
            index + 1,
            index * 0.5,
            debug=True,
        )
        assert detection.raw_oil_air_level_y is None
        assert detection.smoothed_oil_air_level_y is None
        consensus = [
            item for item in detection.candidates if item.source == "oil_consensus"
        ]
        assert consensus
        assert not [item for item in consensus if not item.rejected]
        if index == 0:
            assert any(
                item.reject_reason == "multi_edge_static_structure"
                for item in consensus
            )


def test_partial_static_learning_never_protects_multi_edge_false_survivor():
    detector = OpenCvPhaseDetector()
    config = glass()
    observed = multi_edge_static_band()
    partial_static = multi_edge_static_band(x_start=150, x_stop=170)
    detector.learn_static_artifact(
        [partial_static, partial_static.copy(), partial_static.copy()],
        config,
    )

    for index in range(3):
        detection, _ = detector.detect(
            observed,
            config,
            index + 1,
            index * 0.5,
            debug=True,
        )
        assert detection.raw_oil_air_level_y is None
        assert detection.smoothed_oil_air_level_y is None
        consensus = [
            item for item in detection.candidates if item.source == "oil_consensus"
        ]
        assert consensus
        assert not [item for item in consensus if not item.rejected]
        assert all(
            item.reject_reason == "multi_edge_static_structure"
            for item in consensus
        )
        assert any(
            0.0 < item.features["static_overlap"] < 0.06
            and item.features["observation_score"] > 0.90
            and item.features["unique_generator_support_count"] >= 4.0
            and item.features["consensus_score"] > 0.90
            for item in consensus
        )


def test_real_boundary_is_only_survivor_beside_multi_edge_static_band():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = multi_edge_static_band(offset=-2, background=115)
    combo = oil_frame(154, above=165, below=72)
    static_pixels = np.any(static != 115, axis=2)
    combo[static_pixels] = static[static_pixels]
    detector.learn_static_artifact([static, static.copy(), static.copy()], config)

    detection, _ = detector.detect(combo, config, 1, 0.0, debug=True)
    assert detection.raw_oil_air_level_y is not None
    assert abs(detection.raw_oil_air_level_y - 154.0) <= 4.0
    accepted = [
        item
        for item in detection.candidates
        if item.source == "oil_consensus" and not item.rejected
    ]
    assert accepted
    assert all(abs(item.y - 154.0) <= 4.0 for item in accepted)
    assert any(
        item.reject_reason == "multi_edge_static_structure"
        for item in detection.candidates
        if item.source == "oil_consensus"
    )


def test_nearby_real_boundary_survives_within_static_group_distance():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = multi_edge_static_band(offset=-2, background=115)
    combo = oil_frame(126, above=165, below=72)
    static_pixels = np.any(static != 115, axis=2)
    combo[static_pixels] = static[static_pixels]
    detector.learn_static_artifact([static, static.copy(), static.copy()], config)

    detection, _ = detector.detect(combo, config, 1, 0.0, debug=True)
    assert detection.raw_oil_air_level_y is not None
    assert detection.smoothed_oil_air_level_y is not None
    assert abs(detection.raw_oil_air_level_y - 126.0) <= 4.0
    accepted = [
        item
        for item in detection.candidates
        if item.source == "oil_consensus" and not item.rejected
    ]
    assert len(accepted) == 1
    assert abs(accepted[0].y - 126.0) <= 4.0
    assert (
        accepted[0].features[
            "multi_edge_static_protected_real_boundary"
        ]
        == 1.0
    )
    assert all(
        item.reject_reason == "multi_edge_static_structure"
        for item in detection.candidates
        if item.source == "oil_consensus"
        and abs(item.y - accepted[0].y) > 4.0
    )


def test_stationary_weak_boundary_survives_nonuniform_static_overlap():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = uniform_frame(112)
    static[138:142, 40:130] = 150
    static[138:142, 190:280] = 150
    weak = uniform_frame(125)
    weak[140:] = 103
    weak[139:142] = 145
    detector.learn_static_artifact([static, static.copy(), static.copy()], config)

    detection, _ = detector.detect(weak, config, 1, 0.0, debug=True)
    assert detection.raw_oil_air_level_y is not None
    assert abs(detection.raw_oil_air_level_y - 140.0) <= 4.0
    assert any(
        item.source == "oil_consensus" and not item.rejected
        for item in detection.candidates
    )
