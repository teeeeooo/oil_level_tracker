from __future__ import annotations

from collections import defaultdict

import cv2
import numpy as np
import pytest

from oil_benchmark_fixtures import controlled_oil_scenes
from oil_observability_fixtures import (
    DetectorObservability,
    ExpectedCanonicalFamily,
    LatentSceneCause,
    historical_glare_negatives,
    single_frame_observability_collisions,
)
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_shadow_observations import (
    build_bounded_proposals,
    evaluate_semantic_hypotheses,
    evaluate_typed_current_observation,
    extract_raw_observations,
)
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    AmbiguousOutcome,
    ShadowAmbiguousObservation,
)
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import InspectionRecipe


def _collision_pairs():
    grouped = defaultdict(list)
    for scene in single_frame_observability_collisions():
        grouped[scene.collision_id].append(scene)
    pairs = []
    for collision_id, scenes in sorted(grouped.items()):
        assert len(scenes) == 2
        pairs.append(pytest.param(tuple(scenes), id=collision_id))
    return pairs


def _glass(scene, suffix: str = ""):
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = f"observability-{scene.collision_id}{suffix}"
    glass.geometry.ellipse = scene.ellipse
    return glass


def _inputs(scene):
    glass = _glass(scene)
    bundle = build_mask_bundle(scene.frame, glass)
    prepared = preprocess(
        bundle.crop,
        bundle.effective_mask,
        glass.detector_settings,
    )
    return glass, bundle, prepared


def _typed_observation(scene):
    _glass_config, bundle, prepared = _inputs(scene)
    bounds = OilHypothesisPipeline().bounds
    raw = extract_raw_observations(
        prepared,
        bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )
    proposals = build_bounded_proposals(raw, bounds)
    hypotheses = evaluate_semantic_hypotheses(
        proposals,
        raw,
        prepared,
        bundle.effective_mask,
        bundle.ellipse_mask,
        bundle.exclusion_mask,
        None,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )
    return evaluate_typed_current_observation(
        prepared,
        bundle.effective_mask,
        hypotheses,
    )


def _canonical_outcome(scene):
    glass, bundle, prepared = _inputs(scene)
    return OilHypothesisPipeline().run(
        glass_id=glass.id,
        pre=prepared,
        effective_mask=bundle.effective_mask,
        ellipse_mask=bundle.ellipse_mask,
        exclusion_mask=bundle.exclusion_mask,
        static_artifact_map=None,
        crop_origin_y=float(bundle.crop_origin[1]),
    )


def _detection(scene, detector=None, frame_index: int = 0):
    owner = OpenCvPhaseDetector() if detector is None else detector
    detection, _artifacts = owner.detect(
        scene.frame.copy(),
        _glass(scene, "-detector"),
        frame_index,
        float(frame_index),
        debug=False,
    )
    return detection


def _effective_observation(scene):
    _glass_config, bundle, prepared = _inputs(scene)
    masked_bgr = np.where(
        bundle.effective_mask[:, :, None] > 0,
        bundle.crop,
        0,
    )
    return (
        masked_bgr,
        bundle.effective_mask,
        bundle.ellipse_mask,
        bundle.exclusion_mask,
        prepared.gray,
        prepared.normalized,
        prepared.blurred,
        prepared.sobel_y_signed,
        prepared.sobel_y_abs,
        prepared.canny,
        prepared.horizontal_mask,
        prepared.glare_mask,
    )


@pytest.mark.parametrize("pair", _collision_pairs())
def test_latent_truth_is_separate_from_identical_detector_expectation(pair):
    glare, oil = sorted(pair, key=lambda item: item.latent_cause.value)
    assert {glare.latent_cause, oil.latent_cause} == {
        LatentSceneCause.PARTIAL_GLARE,
        LatentSceneCause.LEGITIMATE_OIL_BOUNDARY,
    }
    assert {item.numeric_oil_geometry_present for item in pair} == {False, True}
    assert {item.latent_oil_y for item in pair} == {None, 80.0}
    assert all(
        item.detector_observability is DetectorObservability.UNIDENTIFIABLE
        for item in pair
    )
    assert all(
        item.expected_canonical_family is ExpectedCanonicalFamily.AMBIGUOUS
        for item in pair
    )
    left = _effective_observation(pair[0])
    right = _effective_observation(pair[1])
    assert len(left) == len(right)
    assert all(np.array_equal(a, b) for a, b in zip(left, right, strict=True))


@pytest.mark.parametrize("pair", _collision_pairs())
def test_unidentifiable_collision_requires_canonical_ambiguity(pair):
    actual = []
    violations = []
    for scene in pair:
        typed = _typed_observation(scene)
        outcome = _canonical_outcome(scene)
        detection = _detection(scene)
        selected_oil = [
            item
            for item in detection.candidates
            if item.kind.value == "oil_air" and item.selected
        ]
        record = {
            "case_id": scene.case_id,
            "typed": type(typed).__name__,
            "canonical": type(outcome).__name__,
            "canonical_reason": outcome.reason,
            "canonical_tracker": outcome.tracker_action.value,
            "canonical_smoothing": outcome.smoothing_action.value,
            "raw": detection.raw_oil_air_level_y,
            "smoothed": detection.smoothed_oil_air_level_y,
            "current": detection.debug_metrics["oil_hypothesis_current_observation"],
            "decision": detection.debug_metrics["oil_decision_reason"],
            "tracker": detection.debug_metrics["oil_tracker_action"],
            "smoothing": detection.debug_metrics["oil_smoothing_action"],
            "flags": detection.flags,
        }
        actual.append(record)
        if not isinstance(typed, ShadowAmbiguousObservation):
            violations.append(f"{scene.case_id}: typed={type(typed).__name__}")
        if not isinstance(outcome, AmbiguousOutcome):
            violations.append(f"{scene.case_id}: canonical={type(outcome).__name__}")
        if detection.raw_oil_air_level_y is not None:
            violations.append(f"{scene.case_id}: raw={detection.raw_oil_air_level_y}")
        if detection.smoothed_oil_air_level_y is not None:
            violations.append(
                f"{scene.case_id}: smoothed={detection.smoothed_oil_air_level_y}"
            )
        if selected_oil:
            violations.append(f"{scene.case_id}: selected_oil={len(selected_oil)}")
        if detection.debug_metrics["oil_tracker_action"] != "NO_UPDATE":
            violations.append(f"{scene.case_id}: tracker action accepted")
        if detection.debug_metrics["oil_smoothing_action"] != "PRESERVE":
            violations.append(f"{scene.case_id}: smoothing was not preserved")
        if "REVIEW_REQUIRED" not in detection.flags:
            violations.append(f"{scene.case_id}: review flag absent")
    assert not violations, {
        "expected": "AmbiguousOutcome, no numeric oil, NO_UPDATE/PRESERVE, review",
        "violations": violations,
        "actual": actual,
    }


def test_repeated_identical_ambiguity_is_not_positive_temporal_evidence():
    scene = next(
        item
        for item in single_frame_observability_collisions()
        if item.case_id == "centered-partial-glare-72-latent-oil"
    )
    detector = OpenCvPhaseDetector()
    outputs = [
        _detection(scene, detector=detector, frame_index=index)
        for index in range(6)
    ]
    actual = [
        (
            item.raw_oil_air_level_y,
            item.smoothed_oil_air_level_y,
            item.debug_metrics["oil_hypothesis_current_observation"],
            item.debug_metrics["oil_tracker_action"],
            item.debug_metrics["oil_smoothing_action"],
        )
        for item in outputs
    ]
    assert all(
        raw is None
        and smoothed is None
        and current == "ambiguous"
        and tracker == "NO_UPDATE"
        and smoothing == "PRESERVE"
        for raw, smoothed, current, tracker, smoothing in actual
    ), actual


@pytest.mark.parametrize(
    "negative",
    [
        pytest.param(item, id=item.case_id)
        for item in historical_glare_negatives()
    ],
)
def test_historical_21_glare_negatives_remain_without_numeric_oil(negative):
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = f"historical-{negative.case_id}"
    detection, _artifacts = OpenCvPhaseDetector().detect(
        negative.frame.copy(),
        glass,
        0,
        0.0,
        debug=False,
    )
    assert detection.raw_oil_air_level_y is None, negative.case_id
    assert detection.smoothed_oil_air_level_y is None, negative.case_id


def test_retained_distinguishable_boundaries_stay_truth_near_numeric():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    for case_id in ("clear-upper", "rapid-filling-0", "structural-plus-real"):
        scene = scenes[case_id]
        assert scene.oil_y is not None
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"retained-{case_id}"
        detection, _artifacts = OpenCvPhaseDetector().detect(
            scene.frame.copy(),
            glass,
            0,
            scene.timestamp,
            debug=False,
        )
        assert detection.raw_oil_air_level_y is not None, case_id
        assert abs(detection.raw_oil_air_level_y - scene.oil_y) <= 4.0, case_id


def test_retained_bright_reversal_and_structural_separation_stay_distinguishable():
    reversed_boundary = np.full((240, 320, 3), 70, dtype=np.uint8)
    reversed_boundary[120:] = 230
    bright_glass = InspectionRecipe.default_glass(320, 240)
    bright_glass.id = "retained-bright-reversed"
    bright, _artifacts = OpenCvPhaseDetector().detect(
        reversed_boundary,
        bright_glass,
        0,
        0.0,
        debug=False,
    )
    assert bright.raw_oil_air_level_y is not None
    assert abs(bright.raw_oil_air_level_y - 120.0) <= 4.0

    thin_line = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.line(thin_line, (0, 120), (319, 120), (235, 235, 235), 1)
    structural_glass = InspectionRecipe.default_glass(320, 240)
    structural_glass.id = "retained-structural-only"
    structural, _artifacts = OpenCvPhaseDetector().detect(
        thin_line,
        structural_glass,
        0,
        0.0,
        debug=False,
    )
    assert structural.raw_oil_air_level_y is None
    assert structural.smoothed_oil_air_level_y is None
