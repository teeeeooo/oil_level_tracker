from __future__ import annotations

import math

import cv2
import numpy as np

from foam_benchmark_fixtures import controlled_scenes
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import InspectionRecipe


def _glass():
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "integration-glass"
    return glass


def _scene(case_id: str):
    return next(scene for scene in controlled_scenes() if scene.case_id == case_id)


def test_detector_identity_input_immutability_and_debug_false_fast_path():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    before = frame.copy()
    detection, artifacts = detector.detect(frame, glass, 1, 1.0, debug=False)
    assert OpenCvPhaseDetector.version == "opencv-phase-detector-s5b-typed-production-v1"
    assert artifacts is None
    assert np.array_equal(frame, before)
    assert detection.raw_foam_front_y is not None
    assert detection.smoothed_foam_front_y is not None
    assert detection.foam_front_px_from_zero is not None


def test_detector_uses_canonical_source_coordinates_and_exposes_finite_evidence():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    bundle = build_mask_bundle(frame, glass)
    detection, artifacts = detector.detect(frame, glass, 1, 1.0, debug=True)
    assert artifacts is not None
    foam_rows = [candidate for candidate in detection.candidates if candidate.kind is BoundaryKind.FOAM_FRONT]
    assert foam_rows
    foam = foam_rows[0]
    assert math.isclose(foam.y, float(foam.features["local_y"]) + bundle.crop_origin[1])
    assert detection.raw_foam_front_y == foam.y
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
    assert detection.debug_metrics["foam_decision_status"] in {
        "accepted_strong",
        "accepted_moderate",
    }


def test_debug_images_are_additive_crop_sized_evidence_artifacts():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame
    bundle = build_mask_bundle(frame, glass)
    _detection, artifacts = detector.detect(frame, glass, 1, 1.0, debug=True)
    assert artifacts is not None
    crop_shape = bundle.crop.shape[:2]
    for key in (
        "foam_whiteness",
        "foam_texture_evidence",
        "foam_glare_excluded_mask",
        "foam_combined_evidence",
        "foam_accepted_component",
    ):
        assert key in artifacts.images
        assert artifacts.images[key].shape[:2] == crop_shape
        assert artifacts.images[key].dtype == np.uint8


def test_accepted_low_light_foam_does_not_invent_an_oil_boundary_below_texture():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    scene = _scene("low-light-foam")
    detection, _artifacts = detector.detect(
        scene.frame,
        glass,
        1,
        scene.timestamp,
        debug=False,
    )
    assert detection.raw_foam_front_y is not None
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None


def test_accepted_white_foam_plus_structural_band_does_not_create_false_oil():
    detector = OpenCvPhaseDetector()
    glass = _glass()
    frame = _scene("white-foam").frame.copy()
    cv2.rectangle(frame, (122, 125), (197, 127), (120, 120, 120), -1)

    detection, _artifacts = detector.detect(frame, glass, 1, 1.0, debug=False)

    assert detection.raw_foam_front_y is not None
    assert detection.debug_metrics["foam_decision_status"] in {
        "accepted_strong",
        "accepted_moderate",
    }
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None
    assert detection.fill_state.value != "FOAMING_VISIBLE"


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
