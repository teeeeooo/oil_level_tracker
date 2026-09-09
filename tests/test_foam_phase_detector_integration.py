from __future__ import annotations

import math

import cv2
import numpy as np
import pytest

from foam_benchmark_fixtures import controlled_scenes
from oil_tracker.adapters.vision.artifact_calibration import template_from_candidate
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.opencv_phase_detector import (
    OpenCvPhaseDetector,
    _foam_static_match,
)
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import InspectionRecipe


def _glass():
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "integration-glass"
    return glass


def _scene(case_id: str):
    return next(scene for scene in controlled_scenes() if scene.case_id == case_id)


def _confirmed_detection(
    detector: OpenCvPhaseDetector,
    glass,
    frame: np.ndarray,
    *,
    time_sec: float = 1.0,
    debug: bool = False,
):
    detector.detect(frame, glass, 0, time_sec - 0.5, debug=False)
    return detector.detect(frame, glass, 1, time_sec, debug=debug)


def _resolve_repeated_static_frame(
    frame: np.ndarray,
    *,
    count: int = 8,
):
    detector = OpenCvPhaseDetector()
    glass = _glass()
    raw = [
        detector.detect(
            frame.copy(),
            glass,
            index,
            index * 0.5,
            debug=False,
        )[0]
        for index in range(count)
    ]
    return raw, detector.resolve_sequence(raw, glass)


def _detached_droplet_frame(center_x: int, center_y: int) -> np.ndarray:
    frame = np.full((240, 320, 3), 45, dtype=np.uint8)
    cv2.ellipse(
        frame,
        (center_x, center_y),
        (14, 25),
        0,
        0,
        360,
        (210, 210, 210),
        -1,
    )
    for y in range(center_y - 18, center_y + 19, 6):
        cv2.circle(
            frame,
            (center_x + (y % 3) - 1, y),
            2,
            (240, 240, 240),
            1,
        )
    return frame


def test_detector_identity_input_immutability_and_debug_false_fast_path():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    before = frame.copy()
    detection, artifacts = _confirmed_detection(
        detector,
        glass,
        frame,
        debug=False,
    )
    assert OpenCvPhaseDetector.version == "opencv-phase-detector-r22-oil-ownership-evidence-replacement-v1"
    assert artifacts is None
    assert np.array_equal(frame, before)
    assert any(
        candidate.kind is BoundaryKind.FOAM_FRONT
        for candidate in detection.candidates
    )


def test_detector_uses_canonical_source_coordinates_and_exposes_finite_evidence():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    bundle = build_mask_bundle(frame, glass)
    detection, artifacts = _confirmed_detection(
        detector,
        glass,
        frame,
        debug=True,
    )
    assert artifacts is not None
    foam_rows = [candidate for candidate in detection.candidates if candidate.kind is BoundaryKind.FOAM_FRONT]
    assert foam_rows
    foam = foam_rows[0]
    assert math.isclose(foam.y, float(foam.features["local_y"]) + bundle.crop_origin[1])
    assert foam.features["sequence_foam_eligible"] == 1.0
    assert all(
        foam.features["sequence_foam_eligibility_predicates"].values()
    )
    assert foam.features["sequence_foam_eligibility_failed_gates"] == ""
    for key in (
        "foam_evidence_score",
        "foam_whiteness_ratio",
        "foam_texture_support_ratio",
        "foam_glare_overlap_ratio",
        "foam_component_height_ratio",
        "foam_component_width_ratio",
        "foam_bounding_box_fill_ratio",
        "foam_temporal_pending_count",
        "foam_temporal_required_count",
        "foam_min_evidence_score",
        "foam_strong_evidence_score",
    ):
        value = detection.debug_metrics[key]
        assert isinstance(value, (int, float))
        assert math.isfinite(float(value))
    assert detection.debug_metrics["foam_registered_internal_motion_support"] >= 0.0


def test_static_detached_droplet_remains_sequence_ineligible() -> None:
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _detached_droplet_frame(158, 130)

    detection, _artifacts = _confirmed_detection(detector, glass, frame)

    foam = next(
        candidate
        for candidate in detection.candidates
        if candidate.kind is BoundaryKind.FOAM_FRONT
    )
    assert foam.features["foam_detached_droplet"] == 1.0
    assert foam.features["foam_dynamic_detached_droplet"] == 0.0
    assert foam.features["sequence_foam_eligible"] == 0.0
    assert (
        foam.features["sequence_foam_eligibility_predicates"][
            "supported_layer_shape"
        ]
        is False
    )
    assert "supported_layer_shape" in foam.features[
        "sequence_foam_eligibility_failed_gates"
    ]


def test_registered_dynamic_detached_droplet_becomes_sequence_eligible() -> None:
    detector = OpenCvPhaseDetector()
    glass = _glass()
    detection = None
    for index, (center_x, center_y) in enumerate(
        ((154, 140), (158, 130), (162, 120), (166, 110))
    ):
        detection, _artifacts = detector.detect(
            _detached_droplet_frame(center_x, center_y),
            glass,
            index,
            index * 0.5,
            debug=False,
        )

    assert detection is not None
    foam = next(
        candidate
        for candidate in detection.candidates
        if candidate.kind is BoundaryKind.FOAM_FRONT
    )
    assert foam.features["foam_detached_droplet"] == 1.0
    assert foam.features["foam_dynamic_detached_droplet"] == 1.0
    assert foam.features["sequence_foam_eligible"] == 1.0


def test_user_calibrated_boundary_is_removed_from_live_preview_authority():
    frame = _scene("clear-boundary").frame
    source_glass = _glass()
    source, _ = _confirmed_detection(
        OpenCvPhaseDetector(),
        source_glass,
        frame,
    )
    selected = next(
        candidate
        for candidate in source.candidates
        if candidate.kind is BoundaryKind.OIL_AIR and candidate.selected
    )
    template = template_from_candidate(selected, name="사용자 지정 반사선")
    assert template is not None

    calibrated_glass = _glass()
    calibrated_glass.geometry.artifact_templates.append(template)
    calibrated, _ = _confirmed_detection(
        OpenCvPhaseDetector(),
        calibrated_glass,
        frame,
    )

    assert calibrated.raw_oil_air_level_y is None
    assert calibrated.oil_air_level_y is None
    assert "R8_CALIBRATED_ARTIFACT_REJECTED" in calibrated.flags
    assert any(
        candidate.reject_reason == f"calibrated_artifact:{template.id}"
        for candidate in calibrated.candidates
    )


def test_debug_images_are_additive_crop_sized_evidence_artifacts():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    bundle = build_mask_bundle(frame, glass)
    _detection, artifacts = _confirmed_detection(
        detector,
        glass,
        frame,
        debug=True,
    )
    assert artifacts is not None
    crop_shape = bundle.crop.shape[:2]
    for key in (
        "foam_whiteness",
        "foam_texture_evidence",
        "foam_glare_excluded_mask",
        "foam_combined_evidence",
        "foam_accepted_component",
        "static_foam_artifact_map",
    ):
        assert key in artifacts.images
        assert artifacts.images[key].shape[:2] == crop_shape
        assert artifacts.images[key].dtype == np.uint8


def test_representative_static_foam_is_explained_without_losing_debug_evidence():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    detector.learn_static_artifact([frame.copy() for _ in range(3)], glass)

    detection, artifacts = detector.detect(frame, glass, 1, 1.0, debug=True)

    assert artifacts is not None
    assert detection.raw_foam_front_y is None
    assert detection.smoothed_foam_front_y is None
    assert detection.debug_metrics["foam_decision_status"] == "static_rejected"
    assert detection.debug_metrics["foam_static_artifact_overlap"] >= 0.80
    assert detection.debug_metrics["foam_static_artifact_tolerant_overlap"] >= 0.80
    assert detection.debug_metrics["foam_static_artifact_reciprocal_overlap"] >= 0.80
    assert detection.debug_metrics["foam_static_artifact_dominant"] is True
    assert detection.debug_metrics["foam_oil_context_authoritative"] is False
    assert detection.debug_metrics["foam_oil_context_publication_accepted"] is False
    assert detection.debug_metrics["foam_static_artifact_pixel_count"] > 0
    assert "FOAM_STATIC_ARTIFACT_REJECTED" in detection.flags
    assert np.count_nonzero(artifacts.images["foam_mask"]) > 0
    assert np.count_nonzero(artifacts.images["static_foam_artifact_map"]) > 0
    assert np.count_nonzero(artifacts.images["foam_accepted_component"]) == 0

    detector.reset(glass.id)
    reset_detection, reset_artifacts = detector.detect(
        frame,
        glass,
        2,
        2.0,
        debug=True,
    )
    assert reset_artifacts is not None
    assert reset_detection.raw_foam_front_y is None
    assert reset_detection.debug_metrics["foam_decision_status"] == "persistence_pending"
    assert reset_detection.debug_metrics["foam_oil_context_authoritative"] is False
    assert reset_detection.debug_metrics["foam_oil_context_publication_accepted"] is False
    assert reset_detection.debug_metrics["foam_static_artifact_pixel_count"] == 0
    raw, resolution = _resolve_repeated_static_frame(frame)
    assert all(
        any(candidate.kind is BoundaryKind.FOAM_FRONT for candidate in item.candidates)
        for item in raw
    )
    assert resolution.diagnostics.foam_episode_count == 0
    assert all(item.raw_foam_front_y is None for item in resolution.detections)


def test_registered_static_match_recovers_bounded_mask_shift():
    static = np.zeros((240, 320), dtype=np.uint8)
    current = np.zeros_like(static)
    static[100:120, 100:110] = 255
    current[100:120, 103:113] = 255

    match = _foam_static_match(current, static)

    assert match.tolerance_radius_px == 2
    assert match.exact_overlap == pytest.approx(0.70)
    assert match.tolerant_overlap == pytest.approx(0.90)
    assert match.reciprocal_overlap == pytest.approx(0.90)
    assert match.dominant


def test_registered_static_match_does_not_explain_materially_larger_new_support():
    static = np.zeros((240, 320), dtype=np.uint8)
    current = np.zeros_like(static)
    static[100:120, 100:110] = 255
    current[100:140, 103:123] = 255

    match = _foam_static_match(current, static)

    assert match.exact_overlap < 0.70
    assert not match.dominant


def test_registered_static_match_rejects_shape_mismatch():
    with pytest.raises(ValueError, match="share one raster shape"):
        _foam_static_match(
            np.zeros((20, 20), dtype=np.uint8),
            np.zeros((21, 20), dtype=np.uint8),
        )


def test_transient_foam_in_representative_frames_is_not_learned_as_static():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    foam = _scene("white-foam").frame
    clear = _scene("full-no-interface").frame
    detector.learn_static_artifact(
        [foam.copy(), clear.copy(), clear.copy()],
        glass,
    )

    detection, artifacts = _confirmed_detection(
        detector,
        glass,
        foam,
        debug=True,
    )

    assert artifacts is not None
    assert detection.raw_foam_front_y is not None
    assert detection.debug_metrics["foam_decision_status"] in {
        "accepted_strong",
        "accepted_moderate",
    }
    assert detection.debug_metrics["foam_static_artifact_pixel_count"] == 0
    assert np.count_nonzero(artifacts.images["static_foam_artifact_map"]) == 0


def test_accepted_low_light_foam_does_not_invent_an_oil_boundary_below_texture():
    scene = _scene("low-light-foam")
    raw, resolution = _resolve_repeated_static_frame(scene.frame)

    assert any(
        candidate.kind is BoundaryKind.FOAM_FRONT
        for candidate in raw[0].candidates
    )
    assert resolution.diagnostics.foam_episode_count == 0
    assert all(item.raw_oil_air_level_y is None for item in resolution.detections)
    assert all(item.raw_foam_front_y is None for item in resolution.detections)


def _assert_structural_foam_stays_fail_closed(frame: np.ndarray, timestamp: float) -> None:
    _raw, resolution = _resolve_repeated_static_frame(frame)

    assert resolution.diagnostics.foam_episode_count == 0
    assert all(item.raw_foam_front_y is None for item in resolution.detections)
    assert all(item.raw_oil_air_level_y is None for item in resolution.detections)
    assert all(item.fill_state.value != "FOAMING_VISIBLE" for item in resolution.detections)


def test_accepted_white_foam_plus_structural_band_does_not_create_false_oil():
    frame = _scene("white-foam").frame.copy()
    cv2.rectangle(frame, (122, 125), (197, 127), (120, 120, 120), -1)
    _assert_structural_foam_stays_fail_closed(frame, 1.0)


@pytest.mark.parametrize(
    ("band_y", "band_height", "band_value"),
    (
        (123, 2, 150),
        (132, 4, 180),
        (138, 5, 180),
        (150, 6, 180),
        (156, 4, 180),
        (165, 5, 180),
    ),
)
def test_accepted_partial_foam_structural_band_neighborhood_stays_fail_closed(
    band_y: int,
    band_height: int,
    band_value: int,
):
    scene = _scene("partial-foam")
    frame = scene.frame.copy()
    cv2.rectangle(
        frame,
        (122, band_y),
        (197, band_y + band_height - 1),
        (band_value, band_value, band_value),
        -1,
    )
    _assert_structural_foam_stays_fail_closed(frame, scene.timestamp)


@pytest.mark.parametrize("foam_width", (16, 20))
def test_narrow_partial_foam_structural_band_stays_fail_closed(foam_width: int):
    frame = _scene("white-foam").frame.copy()
    frame[120:185, 122 + foam_width : 198] = 45
    cv2.rectangle(frame, (122, 132), (197, 135), (180, 180, 180), -1)
    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        _glass(),
        frame_index=1,
        time_sec=1.0,
        debug=False,
    )

    assert detection.raw_foam_front_y is None
    assert detection.debug_metrics["foam_decision_status"] == "incoherent_rejected"
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None
    assert detection.fill_state.value not in {"FULL_WITH_FOAM", "FOAMING_VISIBLE"}


def test_transient_shimmer_does_not_create_raw_or_smoothed_foam_front():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    sequence = [
        _scene("transient-shimmer-0"),
        _scene("transient-shimmer-1"),
        _scene("transient-shimmer-2"),
    ]
    for index, scene in enumerate(sequence):
        detection, _artifacts = detector.detect(
            scene.frame, glass, index, scene.timestamp, debug=False
        )
        assert detection.raw_foam_front_y is None
        assert detection.smoothed_foam_front_y is None


def test_representative_detached_warm_grid_cannot_gain_foam_or_fill_state_authority():
    frame = np.full((240, 320, 3), 45, dtype=np.uint8)
    for x in range(110, 210, 10):
        frame[70:150, x : x + 3] = (60, 85, 105)
    for y in range(70, 150, 10):
        frame[y : y + 3, 110:210] = (60, 85, 105)

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        _glass(),
        frame_index=0,
        time_sec=0.0,
        debug=False,
    )

    assert detection.raw_foam_front_y is None
    assert detection.smoothed_foam_front_y is None
    assert detection.debug_metrics["foam_oil_context_authoritative"] is False
    assert detection.debug_metrics["foam_decision_status"] not in {
        "accepted_strong",
        "accepted_moderate",
    }
    assert detection.fill_state.value != "FOAMING_VISIBLE"


def test_representative_bottom_connected_warm_grid_cannot_gain_foam_or_fill_state_authority():
    frame = np.full((240, 320, 3), 45, dtype=np.uint8)
    for x in range(110, 210, 10):
        frame[120:240, x : x + 3] = (60, 85, 105)
    for y in range(120, 240, 10):
        frame[y : y + 3, 110:210] = (60, 85, 105)

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        _glass(),
        frame_index=0,
        time_sec=0.0,
        debug=False,
    )

    assert detection.raw_foam_front_y is None
    assert detection.smoothed_foam_front_y is None
    assert detection.debug_metrics["foam_oil_context_authoritative"] is False
    assert detection.debug_metrics["foam_decision_status"] not in {
        "accepted_strong",
        "accepted_moderate",
    }
    assert detection.fill_state.value not in {"FULL_WITH_FOAM", "FOAMING_VISIBLE"}


def test_detector_reset_clears_bounded_foam_state_per_glass_and_globally():
    detector = OpenCvPhaseDetector()
    first = _glass()
    second = _glass()
    second.id = "integration-glass-2"
    first.detector_settings.foam_strong_evidence_score = 1.0
    first.detector_settings.foam_min_evidence_score = 0.20
    second.detector_settings.foam_strong_evidence_score = 1.0
    second.detector_settings.foam_min_evidence_score = 0.20
    scene = _scene("partial-foam")
    detector.detect(scene.frame, first, 0, scene.timestamp, debug=False)
    detector.detect(scene.frame, second, 0, scene.timestamp, debug=False)
    assert detector.foam_temporal_state_count <= 2
    detector.reset(first.id)
    assert detector._foam_gate.state_for(first.id) is None
    detector.reset()
    assert detector.foam_temporal_state_count == 0
