from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe


DETECTOR_VERSION = "opencv-phase-detector-r21-truth-preserving-detector-repair-v1"


def glass(initial=InitialObservationState.AUTO, glass_id="glass-oil"):
    value = InspectionRecipe.default_glass(320, 240)
    value.id = glass_id
    value.geometry.zero_line_y = 150.0
    value.initial_state = initial
    value.detector_settings.minimum_final_confidence = 0.35
    return value


def oil_frame(y: int = 130, *, above=175, below=70):
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


def _oil_candidates(detection):
    return [item for item in detection.candidates if item.kind.value == "oil_air"]


def test_detector_version_canonical_coordinates_and_typed_debug_evidence():
    detector = OpenCvPhaseDetector()
    frame = oil_frame(130)
    before = frame.copy()
    detection, artifacts = detector.detect(frame, glass(), 1, 0.0, debug=True)

    assert detector.version == DETECTOR_VERSION
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
    assert detection.debug_metrics["oil_decision_status"] == "boundary_accepted"
    candidates = _oil_candidates(detection)
    semantic = [
        item for item in candidates if item.source.startswith("oil_hypothesis:")
    ]
    supplemental = [
        item for item in candidates if item.source == "material_path"
    ]
    assert candidates
    assert semantic
    assert supplemental
    assert all(
        "local_y" in item.features and "source_y" in item.features
        for item in candidates
    )
    assert all(
        {
            "registered_oil_motion_available",
            "registered_oil_band_motion_support",
            "sequence_material_layer_topology",
        }
        <= set(item.features)
        for item in candidates
    )
    selected = [item for item in candidates if item.selected]
    assert len(selected) == 1
    assert selected == [item for item in semantic if item.selected]
    assert not any(item.source == "oil_consensus" for item in detection.candidates)


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
    assert not any(item.selected for item in _oil_candidates(first))


def test_one_frame_dropout_has_no_stale_numeric_output_and_recovers():
    detector = OpenCvPhaseDetector()
    config = glass()
    accepted, _ = detector.detect(oil_frame(130), config, 1, 0.0)
    assert accepted.raw_oil_air_level_y is not None
    missing, _ = detector.detect(uniform_frame(135), config, 2, 0.5)
    assert missing.raw_oil_air_level_y is None
    assert missing.smoothed_oil_air_level_y is None
    recovered, _ = detector.detect(oil_frame(132), config, 3, 1.0)
    assert recovered.raw_oil_air_level_y is not None
    assert abs(recovered.raw_oil_air_level_y - 132.0) <= 4.0


def test_per_glass_and_full_reset_clear_typed_and_smoothing_state():
    detector = OpenCvPhaseDetector()
    first = glass(glass_id="glass-one")
    second = glass(glass_id="glass-two")
    detector.detect(oil_frame(130), first, 1, 0.0)
    detector.detect(oil_frame(140), second, 1, 0.0)
    assert detector.oil_temporal_state_count == 2
    detector.reset(first.id)
    assert detector.oil_temporal_state_count == 1
    detector.reset()
    assert detector.oil_temporal_state_count == 0
    assert detector.foam_temporal_state_count == 0


def test_static_structure_is_not_false_boundary_and_real_boundary_reappears():
    detector = OpenCvPhaseDetector()
    config = glass()
    static = multi_edge_static_band()
    before = static.copy()
    detector.learn_static_artifact([static.copy()] * 3, config)
    assert np.array_equal(static, before)

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
        candidates = _oil_candidates(detection)
        semantic = [
            item for item in candidates if item.source.startswith("oil_hypothesis:")
        ]
        supplemental = [
            item for item in candidates if item.source == "material_path"
        ]
        assert candidates
        assert semantic
        assert supplemental
        assert all(not item.selected for item in candidates)
        assert any(
            item.features["static_prior_contribution"] > 0.0
            for item in semantic
        )
        assert all(
            "sequence_eligible" in item.features for item in supplemental
        )

    reappeared, _ = detector.detect(oil_frame(130), config, 4, 1.5, debug=True)
    assert reappeared.raw_oil_air_level_y is not None
    assert abs(reappeared.raw_oil_air_level_y - 130.0) <= 4.0
    selected = [item for item in _oil_candidates(reappeared) if item.selected]
    assert len(selected) == 1
    assert selected[0].y == reappeared.raw_oil_air_level_y


def test_partial_static_prior_remains_soft_and_provenance_is_exposed():
    detector = OpenCvPhaseDetector()
    config = glass()
    partial_static = multi_edge_static_band(x_start=150, x_stop=170)
    detector.learn_static_artifact(
        [partial_static.copy(), partial_static.copy(), partial_static.copy()],
        config,
    )
    detection, _ = detector.detect(multi_edge_static_band(), config, 1, 0.0, debug=True)
    assert detection.raw_oil_air_level_y is None
    candidates = _oil_candidates(detection)
    semantic = [
        item for item in candidates if item.source.startswith("oil_hypothesis:")
    ]
    assert candidates
    assert semantic
    assert all(not item.selected for item in candidates)
    assert all(item.features["provenance_count"] > 0.0 for item in semantic)
    assert all(
        0.0 <= item.features["static_prior_contribution"] <= 1.0
        for item in semantic
    )
