from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np

from foam_benchmark_fixtures import controlled_scenes as controlled_foam_scenes
from oil_observability_fixtures import single_frame_observability_collisions
from oil_tracker.adapters.vision import oil_shadow_observations as observations
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics.s11_evidence_probe import (
    ProbeCase,
    TRANSFORMS,
    _p2_no_interface,
    _relative_signed_profile,
    decode_frame,
    load_cases,
    repository_root,
    run_variant,
    transform_frame,
)


def _diagnostic_case(frame: np.ndarray, glass, case_id: str, truth_oil_y: float = 0.0, *, foam=False):
    return ProbeCase(
        sample=case_id,
        frame_index=0,
        time_sec=0.0,
        truth_oil_y=truth_oil_y,
        truth_foam_present=foam,
        truth_foam_y=None,
        glass=glass,
        video_path=Path("."),
    )


def test_p0_probe_matches_production_and_p1_native_delta_is_bounded() -> None:
    root = repository_root()
    rows = []
    for case in load_cases(root):
        frame = decode_frame(case)
        production, _ = OpenCvPhaseDetector().detect(
            frame.copy(), case.glass, case.frame_index, case.time_sec, debug=False
        )
        p0 = run_variant(frame.copy(), case, "P0")
        p1 = run_variant(frame.copy(), case, "P1")
        p2 = run_variant(frame.copy(), case, "P2")
        assert p0.oil_y == production.raw_oil_air_level_y, case.case_id
        assert p0.foam_y == production.raw_foam_front_y, case.case_id
        assert p2.oil_y == p0.oil_y, case.case_id
        if p0.oil_y is not None:
            assert p1.oil_y == p0.oil_y, case.case_id
        rows.append((case.case_id, p0, p1, p2))

    p0_rows = [row[1] for row in rows]
    p1_rows = [row[2] for row in rows]
    assert sum(item.oil_y is not None for item in p0_rows) == 7
    assert np.mean([item.oil_error_px for item in p0_rows if item.oil_error_px is not None]) == 31.0 / 7.0
    assert sum(item.oil_y is not None for item in p1_rows) == 9
    recovered = {
        case_id: p1.oil_y
        for case_id, p0, p1, _p2 in rows
        if p0.oil_y is None and p1.oil_y is not None
    }
    assert recovered == {"sample2:30": 599.0, "sample2:60": 598.0}


def test_relative_local_contrast_is_multiplicative_scale_invariant() -> None:
    full = SimpleNamespace(
        above=np.array([200.0]), below=np.array([100.0]),
        signed_difference=np.array([100.0]), available=np.array([True]),
    )
    dim = SimpleNamespace(
        above=np.array([100.0]), below=np.array([50.0]),
        signed_difference=np.array([50.0]), available=np.array([True]),
    )
    assert np.allclose(_relative_signed_profile(full), _relative_signed_profile(dim))
    assert abs(full.signed_difference[0] / 255.0) > abs(dim.signed_difference[0] / 255.0)


def test_production_p2_returns_known_low_exposure_false_no_interface_cases_to_ambiguity() -> None:
    root = repository_root()
    cases = {case.case_id: case for case in load_cases(root)}
    transforms = {item.name: item for item in TRANSFORMS}
    expectations = (
        ("base_sample_1:144", "brightness_0.45"),
        ("sample3:900", "brightness_0.45"),
        ("sample3:1035", "brightness_0.45"),
        ("sample3:900", "brightness_0.60"),
    )
    for case_id, transform_id in expectations:
        case = cases[case_id]
        frame = transform_frame(decode_frame(case), transforms[transform_id])
        production, _ = OpenCvPhaseDetector().detect(
            frame.copy(), case.glass, case.frame_index, case.time_sec, debug=False
        )
        p2 = run_variant(frame.copy(), case, "P2")
        assert production.debug_metrics["oil_decision_status"] == "ambiguous", (
            case_id,
            transform_id,
        )
        assert production.raw_oil_air_level_y is None, (case_id, transform_id)
        assert production.smoothed_oil_air_level_y is None, (case_id, transform_id)
        assert production.fill_state.value == "UNKNOWN_REVIEW", (case_id, transform_id)
        assert "OIL_EVIDENCE_AMBIGUOUS" in production.flags, (case_id, transform_id)
        assert production.debug_metrics["oil_no_interface_score"] == p2.no_interface_likelihood
        assert p2.current_kind == "ambiguous", (case_id, transform_id)
        assert p2.oil_y is None, (case_id, transform_id)


def test_production_no_interface_matches_p2_and_keeps_full_empty_as_diagnostics_only() -> None:
    mask = np.full((20, 20), 255, dtype=np.uint8)
    glare = np.zeros((20, 20), dtype=np.uint8)
    sobel = np.zeros((20, 20), dtype=np.float32)
    scores = []
    diagnostics = []
    production_scores = []
    production_diagnostics = []
    for level in (100, 180):
        gray = np.full((20, 20), level, dtype=np.uint8)
        normalized = np.full((20, 20), 128, dtype=np.uint8)
        pre = SimpleNamespace(gray=gray, normalized=normalized, sobel_y_abs=sobel, glare_mask=glare)
        p2 = _p2_no_interface(pre, mask, ())
        production = observations._no_interface_evidence(pre, mask, ())
        scores.append(p2.likelihood)
        diagnostics.append((p2.full_likelihood, p2.empty_likelihood))
        production_scores.append(production.likelihood)
        production_diagnostics.append(
            (production.full_likelihood, production.empty_likelihood)
        )
    assert scores[0] == scores[1]
    assert production_scores == scores
    assert diagnostics[0] != diagnostics[1]
    assert production_diagnostics == diagnostics


def test_p1_and_p3_collision_failure_is_explicit_while_p0_and_p2_preserve_observability() -> None:
    grouped = defaultdict(list)
    for scene in single_frame_observability_collisions():
        grouped[scene.collision_id].append(scene)
    counts = {variant: 0 for variant in ("P0", "P1", "P2", "P3")}
    pair_outputs = {variant: {} for variant in counts}
    for collision_id, pair in grouped.items():
        for variant in counts:
            outputs = []
            for scene in pair:
                glass = InspectionRecipe.default_glass(320, 240)
                glass.id = f"s11-{variant}-{scene.case_id}"
                glass.geometry.ellipse = scene.ellipse
                case = _diagnostic_case(scene.frame, glass, scene.case_id, 80.0)
                row = run_variant(scene.frame.copy(), case, variant)
                counts[variant] += row.oil_y is not None
                outputs.append((row.oil_y, row.current_kind))
            pair_outputs[variant][collision_id] = outputs
            assert outputs[0] == outputs[1], (variant, collision_id, outputs)
    assert counts == {"P0": 0, "P1": 14, "P2": 0, "P3": 14}


def test_all_probe_variants_keep_structural_foam_false_oil_closed() -> None:
    scenes = {scene.case_id: scene for scene in controlled_foam_scenes()}
    frames = []
    frame = scenes["white-foam"].frame.copy()
    cv2.rectangle(frame, (122, 125), (197, 127), (120, 120, 120), -1)
    frames.append(frame)
    for band_y, band_height, band_value in (
        (123, 2, 150), (132, 4, 180), (138, 5, 180),
        (150, 6, 180), (156, 4, 180), (165, 5, 180),
    ):
        frame = scenes["partial-foam"].frame.copy()
        cv2.rectangle(
            frame, (122, band_y), (197, band_y + band_height - 1),
            (band_value, band_value, band_value), -1,
        )
        frames.append(frame)
    for foam_width in (16, 20):
        frame = scenes["white-foam"].frame.copy()
        frame[120:185, 122 + foam_width : 198] = 45
        cv2.rectangle(frame, (122, 132), (197, 135), (180, 180, 180), -1)
        frames.append(frame)

    for variant in ("P0", "P1", "P2", "P3"):
        for index, frame in enumerate(frames):
            glass = InspectionRecipe.default_glass(320, 240)
            glass.id = f"s11-foam-{variant}-{index}"
            case = _diagnostic_case(frame, glass, f"foam-{index}", foam=True)
            row = run_variant(frame.copy(), case, variant)
            assert row.foam_y is not None, (variant, index)
            assert row.oil_y is None, (variant, index)
