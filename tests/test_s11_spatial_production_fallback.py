from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import pytest

from foam_benchmark_fixtures import controlled_scenes as controlled_foam_scenes
from oil_observability_fixtures import (
    historical_glare_negatives,
    single_frame_observability_collisions,
)
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.foam_front_detector import detect_bottom_connected_foam
from oil_tracker.adapters.vision.foam_temporal_gate import FoamTemporalGate
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_shadow_observations import extract_raw_observations
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousOutcome,
    OilShadowBounds,
    ShadowSourceFamily,
)
from oil_tracker.adapters.vision.oil_spatial_fallback import (
    _evaluate_spatial_path,
    build_spatial_positive_fallback_frame,
)
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics.s11_evidence_probe import (
    ProbeCase,
    TRANSFORMS,
    decode_frame,
    load_cases,
    run_variant,
    transform_frame,
)
from tests.s11_local_corpus import require_s11_local_corpus


def _production_raw_oil(frame: np.ndarray, glass, *, frame_index: int = 0) -> float | None:
    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        glass,
        frame_index=frame_index,
        time_sec=0.0,
        debug=False,
    )
    return detection.raw_oil_air_level_y


def _diagnostic_case(frame, glass, case_id: str, *, foam=False) -> ProbeCase:
    return ProbeCase(
        sample=case_id,
        frame_index=0,
        time_sec=0.0,
        truth_oil_y=0.0,
        truth_foam_present=foam,
        truth_foam_y=None,
        glass=glass,
        video_path=Path("."),
    )


def _decode_local_video_frame(root: Path, sample: str, frame_index: int) -> np.ndarray:
    capture = cv2.VideoCapture(str(root / "sample" / f"{sample}.mp4"))
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = capture.read()
    capture.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not decode {sample}:{frame_index}")
    return frame


def test_production_native_recovery_preserves_d2_anchors_with_d4_foam_routing() -> None:
    expected_numeric = {
        "base_sample_1:144": 395.0,
        "sample2:30": 599.0,
        "sample2:60": 598.0,
        "sample3:1035": 245.0,
        "sample4:900": 848.0,
        "sample4:1470": 866.0,
        "sample4:1680": 866.0,
    }
    expected_non_numeric = {
        "base_sample_1:156",
        "base_sample_1:240",
        "sample2:0",
        "sample3:900",
        "sample4:0",
        "sample4:450",
    }
    rows = []
    root = require_s11_local_corpus()
    for case in load_cases(root):
        detection, _artifacts = OpenCvPhaseDetector().detect(
            decode_frame(case),
            case.glass,
            frame_index=case.frame_index,
            time_sec=case.time_sec,
            debug=False,
        )
        rows.append(
            (
                case.case_id,
                case.truth_oil_y,
                detection.raw_oil_air_level_y,
                detection.raw_foam_front_y,
                bool(detection.debug_metrics["foam_oil_context_authoritative"]),
            )
        )

    numeric = [row for row in rows if row[2] is not None]
    assert len(rows) == 13
    assert {case_id: oil_y for case_id, _truth, oil_y, _foam, _auth in numeric} == expected_numeric
    assert np.mean(
        [abs(oil_y - truth) for _case_id, truth, oil_y, _foam, _auth in numeric]
    ) == pytest.approx(6.142857142857143)
    assert {case_id for case_id, _truth, oil_y, _foam, _auth in rows if oil_y is None} == expected_non_numeric

    # D4 must not inflate already valid white-Foam support and erase the accepted
    # D2 sample2 Oil anchors.
    assert {
        case_id: oil_y
        for case_id, _truth, oil_y, _foam, _auth in rows
        if case_id in {"sample2:30", "sample2:60"}
    } == {"sample2:30": 599.0, "sample2:60": 598.0}

    # Authoritative Foam now constrains the existing Oil authority instead of
    # selecting a separate stricter semantic stack. The native sample3:1035
    # boundary therefore remains available below Foam; sample3:900 still fails
    # closed because its Foam-aware residual Spatial proof is insufficient.
    sample3_900 = next(item for item in rows if item[0] == "sample3:900")
    assert sample3_900[2] is None
    assert sample3_900[3] is not None
    assert sample3_900[4] is True
    sample3_1035 = next(item for item in rows if item[0] == "sample3:1035")
    assert sample3_1035[2] == 245.0
    assert sample3_1035[3] == 226.0
    assert sample3_1035[4] is True
    assert sample3_1035[2] > sample3_1035[3]


def test_d2_class_a_authority_continues_but_foam_component_exclusion_can_fail_closed() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", 899)
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    detector = OpenCvPhaseDetector()

    # D2 remains unchanged in its own owner: without accepted Foam context the
    # same current frame still has the four-sector positive-evidence recovery.
    direct = detector._evaluate_oil_pipeline(
        glass.id,
        pre,
        bundle,
        None,
        accepted_foam_front_local_y=None,
        accepted_foam_component_mask=None,
    )
    assert isinstance(direct, AcceptedBoundaryOutcome)
    assert direct.raw_source_y == 320.0
    path = _evaluate_spatial_path(
        pre,
        bundle.effective_mask,
        candidate_local_y=320.0 - float(bundle.crop_origin[1]),
        accepted_foam_component_mask=None,
        bounds=OilShadowBounds(),
    )
    assert path.accepted
    assert path.sector_count == 4
    assert path.rows == (119, 128, 124, 128)
    assert path.span_px == 9
    assert path.maximum_jump_px == 9

    # D4 supplies genuine S5-A Foam on this blind-positive frame. D5 keeps D2
    # available, but accepted Foam pixels remain excluded from its x-resolved
    # proof. Here that exclusion removes the four-sector evidence, so the frame
    # legitimately remains fail-closed rather than recovering Oil by bypassing Foam.
    foam = detect_bottom_connected_foam(
        bundle.crop,
        pre.gray,
        pre.canny,
        pre.glare_mask,
        bundle.effective_mask,
        glass.detector_settings,
    )
    assert foam.candidate is not None
    assert 320.0 > foam.candidate.y + float(bundle.crop_origin[1])
    foam_aware_path = _evaluate_spatial_path(
        pre,
        bundle.effective_mask,
        candidate_local_y=320.0 - float(bundle.crop_origin[1]),
        accepted_foam_component_mask=foam.mask,
        bounds=OilShadowBounds(),
    )
    assert not foam_aware_path.accepted
    assert foam_aware_path.sector_count == 1

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame.copy(),
        glass,
        frame_index=899,
        time_sec=29.996633333333335,
        debug=False,
    )
    assert detection.raw_foam_front_y == 272.0
    assert detection.debug_metrics["foam_oil_context_authoritative"] is True
    assert detection.raw_oil_air_level_y is None
    assert detection.debug_metrics["oil_decision_status"] == "ambiguous"


@pytest.mark.parametrize(
    ("frame_index", "expected_oil_y", "expected_foam_y"),
    (
        (929, 300.0, 260.0),
        (1034, 245.0, 228.0),
        (1094, 244.0, 233.0),
        (1124, 250.0, 226.0),
    ),
)
def test_d5_authoritative_foam_preserves_compatible_current_frame_oil_authority(
    frame_index: int,
    expected_oil_y: float,
    expected_foam_y: float,
) -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", frame_index)

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        glass,
        frame_index=frame_index,
        time_sec=frame_index / 29.97,
        debug=False,
    )

    assert detection.raw_foam_front_y == expected_foam_y
    assert detection.debug_metrics["foam_oil_context_authoritative"] is True
    assert detection.raw_oil_air_level_y == expected_oil_y
    assert detection.debug_metrics["oil_decision_status"] == "boundary_accepted"
    assert expected_oil_y > expected_foam_y


def test_d5_foam_owned_current_frame_evidence_remains_fail_closed() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", 1079)
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)

    direct = OpenCvPhaseDetector()._evaluate_oil_pipeline(
        glass.id,
        pre,
        bundle,
        None,
        accepted_foam_front_local_y=None,
        accepted_foam_component_mask=None,
    )
    assert isinstance(direct, AcceptedBoundaryOutcome)
    assert direct.raw_source_y == 231.0

    foam = detect_bottom_connected_foam(
        bundle.crop,
        pre.gray,
        pre.canny,
        pre.glare_mask,
        bundle.effective_mask,
        glass.detector_settings,
    )
    assert foam.candidate is not None
    candidate_row = int(round(231.0 - float(bundle.crop_origin[1])))
    visible_row = bundle.effective_mask[candidate_row] > 0
    assert np.any(visible_row)
    assert np.all(foam.mask[candidate_row][visible_row] > 0)

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        glass,
        frame_index=1079,
        time_sec=1079 / 29.97,
        debug=False,
    )
    assert detection.raw_foam_front_y == 219.0
    assert detection.debug_metrics["foam_oil_context_authoritative"] is True
    assert detection.raw_oil_air_level_y is None
    assert detection.debug_metrics["oil_decision_status"] == "ambiguous"


def test_d3_near_tie_remains_ambiguous_until_foam_residual_evidence_separates_it() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", 914)
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    bounds = OilShadowBounds()
    raw = extract_raw_observations(
        pre,
        bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )

    fallback = build_spatial_positive_fallback_frame(
        pre=pre,
        effective_mask=bundle.effective_mask,
        ellipse_mask=bundle.ellipse_mask,
        exclusion_mask=bundle.exclusion_mask,
        static_artifact_map=None,
        base_raw_observations=raw,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
        accepted_foam_front_local_y=None,
        accepted_foam_component_mask=None,
    )
    assert fallback is None

    detector = OpenCvPhaseDetector()
    without_foam = detector._evaluate_oil_pipeline(
        glass.id,
        pre,
        bundle,
        None,
        accepted_foam_front_local_y=None,
        accepted_foam_component_mask=None,
    )
    assert isinstance(without_foam, AmbiguousOutcome)

    detection, _artifacts = detector.detect(
        frame.copy(),
        glass,
        frame_index=914,
        time_sec=30.497133,
        debug=False,
    )
    assert detection.raw_foam_front_y == 255.0
    assert detection.debug_metrics["foam_oil_context_authoritative"] is True
    assert detection.raw_oil_air_level_y == 301.0
    assert detection.debug_metrics["oil_decision_status"] == "boundary_accepted"
    assert detection.raw_oil_air_level_y > detection.raw_foam_front_y


def test_d2_spatial_recovery_respects_authoritative_foam_front() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", 899)
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    accepted_foam_mask = np.zeros_like(bundle.effective_mask)

    path = _evaluate_spatial_path(
        pre,
        bundle.effective_mask,
        candidate_local_y=125.0,
        accepted_foam_component_mask=accepted_foam_mask,
        bounds=OilShadowBounds(),
    )
    assert path.accepted
    assert path.sector_count == 4

    def evaluate(front_local_y: float):
        return OpenCvPhaseDetector()._evaluate_oil_pipeline(
            glass.id,
            pre,
            bundle,
            None,
            accepted_foam_front_local_y=front_local_y,
            accepted_foam_component_mask=accepted_foam_mask,
        )

    below_front = evaluate(124.0)
    assert isinstance(below_front, AcceptedBoundaryOutcome)
    assert below_front.raw_source_y == 320.0

    for front_local_y in (125.0, 145.0, 150.0, 155.0):
        blocked = evaluate(front_local_y)
        assert isinstance(blocked, AmbiguousOutcome)
        assert blocked.tracker_action.value == "NO_UPDATE"
        assert blocked.projected_source_y == 321.0


def test_slice_a_removes_distributed_supplemental_authority_without_forced_promotion() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", 2697)

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        glass,
        frame_index=2697,
        time_sec=89.9899,
        debug=False,
    )
    assert detection.raw_oil_air_level_y is None
    assert detection.debug_metrics["oil_decision_status"] == "ambiguous"

    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    raw = extract_raw_observations(
        pre,
        bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=OilShadowBounds(),
    )
    assert raw
    assert ShadowSourceFamily.REGION_STEP in {item.source_family for item in raw}
    assert not any(
        item.source_family is ShadowSourceFamily.SOBEL_DISTRIBUTED
        for item in raw
    )


def test_sample4_structural_foam_rejection_remains_independent_from_oil_boundary_authority() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    for case_id in ("sample4:0", "sample4:450", "sample4:900"):
        case = cases[case_id]
        detection, _artifacts = OpenCvPhaseDetector().detect(
            decode_frame(case),
            case.glass,
            frame_index=case.frame_index,
            time_sec=case.time_sec,
            debug=False,
        )
        assert detection.raw_foam_front_y is None, case_id
        assert detection.debug_metrics["foam_decision_status"] == "weak_rejected", case_id
        assert detection.debug_metrics["foam_component_width_ratio"] >= 0.70, case_id
        assert detection.debug_metrics["foam_bounding_box_fill_ratio"] < 0.30, case_id
        assert detection.debug_metrics["foam_oil_context_authoritative"] is False, case_id
        if case_id == "sample4:900":
            assert detection.raw_oil_air_level_y == 848.0
            assert detection.debug_metrics["oil_decision_status"] == "boundary_accepted"
        else:
            assert detection.raw_oil_air_level_y is None, case_id
            assert detection.debug_metrics["oil_decision_status"] == "ambiguous", case_id


def test_sample4_later_foam_separates_from_structural_substrate() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample4.oilrecipe").glasses[0]

    structural = OpenCvPhaseDetector().detect(
        _decode_local_video_frame(root, "sample4", 975),
        glass,
        frame_index=975,
        time_sec=32.5,
        debug=False,
    )[0]
    assert structural.raw_foam_front_y is None
    assert structural.debug_metrics["foam_decision_status"] == "weak_rejected"
    assert structural.debug_metrics["foam_oil_context_authoritative"] is False

    early_positive = OpenCvPhaseDetector().detect(
        _decode_local_video_frame(root, "sample4", 1050),
        glass,
        frame_index=1050,
        time_sec=35.0,
        debug=False,
    )[0]
    assert early_positive.raw_foam_front_y is None
    assert early_positive.debug_metrics["foam_decision_status"] == "weak_rejected"

    expected_fronts = {
        1125: 837.0,
        1200: 840.0,
        1275: 837.0,
        1350: 836.0,
        1425: 836.0,
    }
    for frame_index, expected_front in expected_fronts.items():
        time_sec = frame_index / 30.0
        detection, _artifacts = OpenCvPhaseDetector().detect(
            _decode_local_video_frame(root, "sample4", frame_index),
            glass,
            frame_index=frame_index,
            time_sec=time_sec,
            debug=False,
        )
        assert detection.raw_foam_front_y == expected_front, frame_index
        assert detection.debug_metrics["foam_decision_status"] == "accepted_strong", frame_index
        assert detection.debug_metrics["foam_oil_context_authoritative"] is True, frame_index
        assert detection.debug_metrics["foam_component_width_ratio"] < 0.70, frame_index


def test_recovered_native_rows_use_genuine_cross_roi_path_information() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    expected = {
        "sample2:30": (599.0, (277, 273, 267)),
        "sample2:60": (598.0, (283, 279, 272)),
    }
    for case_id, (source_y, path_rows) in expected.items():
        case = cases[case_id]
        frame = decode_frame(case)
        production, _artifacts = OpenCvPhaseDetector().detect(
            frame.copy(),
            case.glass,
            frame_index=case.frame_index,
            time_sec=case.time_sec,
            debug=False,
        )
        assert production.raw_oil_air_level_y == source_y
        assert production.debug_metrics["foam_oil_context_authoritative"] is True
        bundle = build_mask_bundle(frame, case.glass)
        pre = preprocess(
            bundle.crop,
            bundle.effective_mask,
            case.glass.detector_settings,
        )
        foam = detect_bottom_connected_foam(
            bundle.crop,
            pre.gray,
            pre.canny,
            pre.glare_mask,
            bundle.effective_mask,
            case.glass.detector_settings,
        )
        foam_temporal = FoamTemporalGate().evaluate(
            case.glass.id,
            foam,
            case.glass.detector_settings,
        )
        accepted_foam_mask = None if foam_temporal.candidate is None else foam.mask
        path = _evaluate_spatial_path(
            pre,
            bundle.effective_mask,
            candidate_local_y=source_y - float(bundle.crop_origin[1]),
            accepted_foam_component_mask=accepted_foam_mask,
            bounds=OilShadowBounds(),
        )
        assert path.accepted
        assert path.sector_count == 3
        assert path.rows == path_rows
        assert path.span_px > 1
        assert path.maximum_jump_px <= 12


def test_scalar_relative_collision_candidates_cannot_publish_numeric_oil() -> None:
    grouped = defaultdict(list)
    relative_numeric = 0
    production_numeric = 0
    for scene in single_frame_observability_collisions():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-production-collision-{scene.case_id}"
        glass.geometry.ellipse = scene.ellipse
        case = _diagnostic_case(scene.frame, glass, scene.case_id)
        relative = run_variant(scene.frame.copy(), case, "P1")
        oil_y = _production_raw_oil(scene.frame.copy(), glass)
        relative_numeric += relative.oil_y is not None
        production_numeric += oil_y is not None
        grouped[scene.collision_id].append(oil_y)
    assert relative_numeric == 16
    assert production_numeric == 0
    assert all(pair == [None, None] for pair in grouped.values())


def test_retained_glare_negatives_remain_non_numeric_in_production() -> None:
    for scene in historical_glare_negatives():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-production-glare-{scene.case_id}"
        assert _production_raw_oil(scene.frame.copy(), glass) is None, scene.case_id


def _structural_foam_frames() -> tuple[np.ndarray, ...]:
    scenes = {scene.case_id: scene for scene in controlled_foam_scenes()}
    frames = []
    frame = scenes["white-foam"].frame.copy()
    cv2.rectangle(frame, (122, 125), (197, 127), (120, 120, 120), -1)
    frames.append(frame)
    for band_y, band_height, band_value in (
        (123, 2, 150),
        (132, 4, 180),
        (138, 5, 180),
        (150, 6, 180),
        (156, 4, 180),
        (165, 5, 180),
    ):
        frame = scenes["partial-foam"].frame.copy()
        cv2.rectangle(
            frame,
            (122, band_y),
            (197, band_y + band_height - 1),
            (band_value, band_value, band_value),
            -1,
        )
        frames.append(frame)
    for foam_width in (16, 20):
        frame = scenes["white-foam"].frame.copy()
        frame[120:185, 122 + foam_width : 198] = 45
        cv2.rectangle(frame, (122, 132), (197, 135), (180, 180, 180), -1)
        frames.append(frame)
    return tuple(frames)


def test_structural_foam_protection_preserves_s5a_owner() -> None:
    for index, frame in enumerate(_structural_foam_frames()):
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-production-foam-{index}"
        detection, _artifacts = OpenCvPhaseDetector().detect(
            frame.copy(),
            glass,
            frame_index=0,
            time_sec=0.0,
            debug=False,
        )
        assert detection.raw_foam_front_y is not None, index
        assert detection.raw_oil_air_level_y is None, index
        assert detection.debug_metrics["foam_oil_context_authoritative"] is True, index


def test_p2_semantic_rescues_do_not_gain_spatial_numeric_oil() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    transforms = {item.name: item for item in TRANSFORMS}
    expected = (
        ("brightness_0.60", "sample3:900"),
        ("brightness_0.45", "base_sample_1:144"),
        ("brightness_0.45", "sample3:900"),
        ("brightness_0.45", "sample3:1035"),
    )
    for transform_id, case_id in expected:
        case = cases[case_id]
        frame = transform_frame(decode_frame(case), transforms[transform_id])
        detection, _artifacts = OpenCvPhaseDetector().detect(
            frame,
            case.glass,
            frame_index=case.frame_index,
            time_sec=case.time_sec,
            debug=False,
        )
        assert detection.raw_oil_air_level_y is None
        assert "OIL_EVIDENCE_AMBIGUOUS" in detection.flags


def test_low_exposure_known_false_boundary_warning_stays_fail_closed() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    transforms = {item.name: item for item in TRANSFORMS}
    case = cases["sample4:450"]
    for transform_id in ("brightness_0.60", "brightness_0.45"):
        frame = transform_frame(decode_frame(case), transforms[transform_id])
        assert _production_raw_oil(frame, case.glass, frame_index=case.frame_index) is None
