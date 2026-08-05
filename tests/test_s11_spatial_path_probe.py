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
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics.s11_evidence_probe import (
    ProbeCase,
    TRANSFORMS,
    decode_frame,
    load_cases,
    run_variant,
    transform_frame,
)
from tests.diagnostics.s11_spatial_path_probe import (
    build_manifest,
    run_native_experiment,
    run_spatial_variant,
)
from tests.s11_local_corpus import require_s11_local_corpus


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


def test_native_spatial_path_recovers_two_residuals_without_regressing_p0_anchors() -> None:
    rows = run_native_experiment(require_s11_local_corpus())
    p0_numeric = [row for row in rows if row.p0_oil_y is not None]
    spatial_numeric = [row for row in rows if row.oil_y is not None]
    assert len(rows) == 13
    assert len(p0_numeric) == 7
    assert np.mean([abs(row.p0_oil_y - row.truth_oil_y) for row in p0_numeric]) == 31.0 / 7.0
    assert len(spatial_numeric) == 9
    assert np.mean([row.oil_error_px for row in spatial_numeric]) == 44.0 / 9.0
    recovered = {
        row.case_id: row.oil_y
        for row in rows
        if row.p0_oil_y is None and row.oil_y is not None
    }
    assert recovered == {"sample2:30": 599.0, "sample2:60": 598.0}
    for row in p0_numeric:
        assert row.oil_y == row.p0_oil_y
        assert row.route == "P0"


def test_native_spatial_recovery_uses_nondegenerate_cross_roi_paths() -> None:
    rows = {row.case_id: row for row in run_native_experiment(require_s11_local_corpus())}
    expected = {
        "sample2:30": (277, 273, 267),
        "sample2:60": (283, 279, 272),
    }
    for case_id, path_rows in expected.items():
        path = rows[case_id].path
        assert path is not None and path.accepted
        assert path.reason == "nondegenerate_cross_roi_phase_path"
        assert path.path_sector_indices == (0, 1, 2)
        assert path.path_rows == path_rows
        assert path.path_span_px > 1
        assert path.maximum_adjacent_jump_px <= 12


def test_observational_equivalence_collisions_stay_fail_closed() -> None:
    grouped = defaultdict(list)
    relative_numeric = 0
    spatial_numeric = 0
    for scene in single_frame_observability_collisions():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-spatial-{scene.case_id}"
        glass.geometry.ellipse = scene.ellipse
        case = _diagnostic_case(scene.frame, glass, scene.case_id)
        relative = run_variant(scene.frame.copy(), case, "P1")
        spatial = run_spatial_variant(scene.frame.copy(), case)
        relative_numeric += relative.oil_y is not None
        spatial_numeric += spatial.oil_y is not None
        grouped[scene.collision_id].append(spatial)
        if relative.oil_y is not None:
            assert spatial.path is not None
            assert spatial.path.reason == "degenerate_scalar_row"
            assert spatial.path.path_span_px <= 1
    assert relative_numeric == 14
    assert spatial_numeric == 0
    for pair in grouped.values():
        assert len(pair) == 2
        left, right = pair
        assert (left.oil_y, left.route) == (right.oil_y, right.route)
        assert (
            None if left.path is None else left.path.reason
        ) == (
            None if right.path is None else right.path.reason
        )


def test_retained_glare_negatives_remain_non_numeric() -> None:
    for scene in historical_glare_negatives():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-spatial-glare-{scene.case_id}"
        case = _diagnostic_case(scene.frame, glass, scene.case_id)
        result = run_spatial_variant(scene.frame.copy(), case)
        assert result.oil_y is None, scene.case_id


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


def test_structural_foam_protection_and_foam_owner_stay_independent() -> None:
    for index, frame in enumerate(_structural_foam_frames()):
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-spatial-foam-{index}"
        case = _diagnostic_case(frame, glass, f"foam-{index}", foam=True)
        p0 = run_variant(frame.copy(), case, "P0")
        result = run_spatial_variant(frame.copy(), case)
        assert p0.foam_y is not None, index
        assert result.foam_y == p0.foam_y, index
        assert result.oil_y is None, index


def test_low_light_p1_warning_is_rejected_for_missing_symmetric_path_window() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    transforms = {item.name: item for item in TRANSFORMS}
    case = cases["sample4:450"]
    for transform_id in ("brightness_0.60", "brightness_0.45"):
        frame = transform_frame(decode_frame(case), transforms[transform_id])
        p1 = run_variant(frame.copy(), case, "P1")
        result = run_spatial_variant(frame.copy(), case)
        assert p1.oil_y == 804.0
        assert result.oil_y is None
        assert result.path is not None
        assert result.path.reason == "candidate_lacks_symmetric_phase_window"


def test_spatial_manifest_declares_bounded_current_frame_resources() -> None:
    manifest = build_manifest(run_native_experiment(require_s11_local_corpus()))
    assert manifest["baseline_main_sha"] == "3305cb8268fd4e1612105cba6144c2083066ff8c"
    native = manifest["native"]
    assert native["oil_coverage"] == 9
    assert native["recovered_case_ids"] == ["sample2:30", "sample2:60"]
    assert native["maximum_path_sector_row_evaluations"] == 125
    assert native["retained_temporal_state"] == 0
