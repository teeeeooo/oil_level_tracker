from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from foam_benchmark_fixtures import controlled_scenes as controlled_foam_scenes
from oil_observability_fixtures import (
    historical_glare_negatives,
    single_frame_observability_collisions,
)
from oil_tracker.adapters.vision.foam_front_detector import detect_bottom_connected_foam
from oil_tracker.adapters.vision.foam_temporal_gate import FoamTemporalGate
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_shadow_types import OilShadowBounds
from oil_tracker.adapters.vision.oil_spatial_fallback import _evaluate_spatial_path
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


def test_production_native_recovery_preserves_non_d1_anchors_and_withholds_unsafe_sample4() -> None:
    expected_preserved = {
        "base_sample_1:144": 395.0,
        "sample2:30": 599.0,
        "sample2:60": 598.0,
        "sample3:1035": 245.0,
    }
    unsafe_sample4 = {
        "sample4:0",
        "sample4:450",
        "sample4:900",
        "sample4:1470",
        "sample4:1680",
    }
    rows = []
    root = require_s11_local_corpus()
    for case in load_cases(root):
        oil_y = _production_raw_oil(
            decode_frame(case),
            case.glass,
            frame_index=case.frame_index,
        )
        rows.append((case.case_id, case.truth_oil_y, oil_y))

    numeric = [row for row in rows if row[2] is not None]
    assert len(rows) == 13
    assert len(numeric) == 4
    assert {
        case_id: oil_y
        for case_id, _truth, oil_y in rows
        if case_id in expected_preserved
    } == expected_preserved
    assert np.mean([abs(oil_y - truth) for _case_id, truth, oil_y in numeric]) == 6.0
    assert {
        case_id
        for case_id, _truth, oil_y in rows
        if oil_y is None
    } == {
        "base_sample_1:156",
        "base_sample_1:240",
        "sample2:0",
        "sample3:900",
        *unsafe_sample4,
    }


def test_sample4_structural_foam_is_published_without_oil_routing_authority() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    for case_id in (
        "sample4:0",
        "sample4:450",
        "sample4:900",
        "sample4:1470",
        "sample4:1680",
    ):
        case = cases[case_id]
        detection, _artifacts = OpenCvPhaseDetector().detect(
            decode_frame(case),
            case.glass,
            frame_index=case.frame_index,
            time_sec=case.time_sec,
            debug=False,
        )
        assert detection.raw_foam_front_y is not None, case_id
        assert detection.raw_oil_air_level_y is None, case_id
        assert detection.debug_metrics["foam_oil_context_authoritative"] is False
        assert (
            detection.debug_metrics["foam_oil_context_reason"]
            == "wide_hollow_structural_or_refractive_component"
        )
        assert detection.debug_metrics["foam_oil_context_wide_row_fraction"] >= 0.25
        assert detection.debug_metrics["foam_oil_context_wide_row_compactness_median"] < 0.65


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
    assert relative_numeric == 14
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
