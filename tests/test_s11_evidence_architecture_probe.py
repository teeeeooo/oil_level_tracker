from __future__ import annotations

from collections import defaultdict
import json
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
    run_variant,
    transform_frame,
)
from tests.s11_local_corpus import require_s11_local_corpus


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


def test_historical_p0_p1_p2_native_diagnostic_baseline_is_frozen() -> None:
    manifest_path = (
        Path(__file__).resolve().parents[1]
        / "docs/50-diagnostics/s11/s11-a-opencv-evidence-architecture-probe-manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["baseline_main_sha"] == "0fd8ca0d423a1f632ad9a026d8f396686870d633"
    native = manifest["aggregate"]["brightness_1.00"]
    assert native["P0"]["oil_coverage"] == 7
    assert native["P0"]["oil_mae_px"] == 31.0 / 7.0
    assert native["P1"]["oil_coverage"] == 9
    assert native["P2"]["oil_coverage"] == 7
    recovered = {
        (item["case_id"], item["variant"]): item["oil_y"]
        for item in manifest["key_cases"]
        if item["transform"] == "brightness_1.00"
        and item["case_id"] in {"sample2:30", "sample2:60"}
        and item["variant"] in {"P0", "P1"}
    }
    assert recovered == {
        ("sample2:30", "P0"): None,
        ("sample2:30", "P1"): 599.0,
        ("sample2:60", "P0"): None,
        ("sample2:60", "P1"): 598.0,
    }


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
    root = require_s11_local_corpus()
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
        assert production.debug_metrics["oil_decision_status"] == "ambiguous", (
            case_id,
            transform_id,
        )
        assert production.raw_oil_air_level_y is None, (case_id, transform_id)
        assert production.smoothed_oil_air_level_y is None, (case_id, transform_id)
        assert production.fill_state.value == "UNKNOWN_REVIEW", (case_id, transform_id)
        assert "OIL_EVIDENCE_AMBIGUOUS" in production.flags, (case_id, transform_id)
        assert production.debug_metrics["oil_no_interface_score"] < 0.58


def test_production_no_interface_reweights_normalized_uniformity_without_brightness_coupling() -> None:
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
    assert production_scores[0] == production_scores[1]
    assert production_scores[0] > scores[0]
    assert production_scores[0] >= 0.58
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
    current_scene_count = sum(len(pair) for pair in grouped.values())
    assert counts == {
        "P0": 0,
        "P1": current_scene_count,
        "P2": 0,
        "P3": current_scene_count,
    }


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
            # The probe receives one frame, so R4 keeps public Foam pending. Its
            # coherent raw mask still protects every Oil variant from the band.
            assert row.foam_y is None, (variant, index)
            assert row.oil_y is None, (variant, index)
