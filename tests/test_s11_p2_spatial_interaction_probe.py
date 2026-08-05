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
from tests.diagnostics import s11_evidence_probe as evidence_probe
from tests.diagnostics.s11_p2_spatial_interaction_probe import (
    build_manifest,
    run_experiment,
    run_interaction_variant,
)
from tests.s11_local_corpus import require_s11_local_corpus


def _run_corpus_experiment():
    return run_experiment(require_s11_local_corpus())


def _diagnostic_case(frame, glass, case_id: str, *, foam=False):
    return evidence_probe.ProbeCase(
        sample=case_id,
        frame_index=0,
        time_sec=0.0,
        truth_oil_y=0.0,
        truth_foam_present=foam,
        truth_foam_y=None,
        glass=glass,
        video_path=Path("."),
    )


def test_native_p0_p2_spatial_combined_matrix_is_consistent() -> None:
    rows = [row for row in _run_corpus_experiment() if row.transform == "brightness_1.00"]
    assert len(rows) == 13
    assert sum(row.p0_oil_y is not None for row in rows) == 7
    assert sum(row.p2_oil_y is not None for row in rows) == 7
    assert sum(row.spatial_oil_y is not None for row in rows) == 9
    assert sum(row.combined_oil_y is not None for row in rows) == 9
    assert np.mean([abs(row.p0_oil_y - row.truth_oil_y) for row in rows if row.p0_oil_y is not None]) == 31.0 / 7.0
    assert np.mean([row.combined_error_px for row in rows if row.combined_error_px is not None]) == 44.0 / 9.0
    assert all(row.p0_oil_y == row.p2_oil_y for row in rows)
    assert all(row.spatial_oil_y == row.combined_oil_y for row in rows)
    assert not any(row.spatial_oil_y is None and row.combined_oil_y is not None for row in rows)


def test_known_p2_false_no_interface_transitions_do_not_gain_combined_numeric_oil() -> None:
    rows = {(row.transform, row.case_id): row for row in _run_corpus_experiment()}
    expected = (
        ("brightness_0.60", "sample3:900"),
        ("brightness_0.45", "base_sample_1:144"),
        ("brightness_0.45", "sample3:900"),
        ("brightness_0.45", "sample3:1035"),
    )
    for key in expected:
        row = rows[key]
        assert row.p0_current_kind == "no_interface"
        assert row.p2_current_kind == "ambiguous"
        assert row.p2_oil_y is None
        assert row.combined_candidate_oil_y is None
        assert row.combined_oil_y is None
        assert row.combined_route == "P2_AMBIGUOUS_NO_SPATIAL_CANDIDATE"


def test_combined_keeps_existing_spatial_low_light_recovery_but_adds_no_interaction_recovery() -> None:
    rows = {(row.transform, row.case_id): row for row in _run_corpus_experiment()}
    row = rows[("brightness_0.60", "sample3:1035")]
    assert row.p0_current_kind == "ambiguous"
    assert row.p2_current_kind == "ambiguous"
    assert row.spatial_oil_y == 245.0
    assert row.combined_oil_y == 245.0
    assert row.combined_route == "COMBINED_ACCEPTED"
    assert row.combined_error_px == 2.0
    assert not any(
        item.spatial_oil_y is None and item.combined_oil_y is not None
        for item in rows.values()
    )


def test_low_light_false_boundary_candidate_stays_spatially_rejected() -> None:
    rows = {(row.transform, row.case_id): row for row in _run_corpus_experiment()}
    for transform_id in ("brightness_0.60", "brightness_0.45"):
        row = rows[(transform_id, "sample4:450")]
        assert row.combined_candidate_oil_y == 804.0
        assert row.combined_oil_y is None
        assert row.combined_route == "COMBINED_REJECTED"
        assert row.path is not None
        assert row.path.reason == "candidate_lacks_symmetric_phase_window"


def test_observational_equivalence_collisions_stay_fail_closed_under_combination() -> None:
    grouped = defaultdict(list)
    candidate_count = 0
    for scene in single_frame_observability_collisions():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-interaction-{scene.case_id}"
        glass.geometry.ellipse = scene.ellipse
        case = _diagnostic_case(scene.frame, glass, scene.case_id)
        row = run_interaction_variant(scene.frame.copy(), case)
        candidate_count += row.combined_candidate_oil_y is not None
        assert row.combined_oil_y is None, scene.case_id
        grouped[scene.collision_id].append(row)
    assert candidate_count == 14
    for pair in grouped.values():
        assert len(pair) == 2
        left, right = pair
        assert (left.combined_oil_y, left.combined_route) == (right.combined_oil_y, right.combined_route)
        assert (None if left.path is None else left.path.reason) == (None if right.path is None else right.path.reason)
        if left.combined_candidate_oil_y is not None:
            assert left.path is not None and left.path.reason == "degenerate_scalar_row"


def test_retained_glare_negatives_remain_non_numeric_under_combination() -> None:
    for scene in historical_glare_negatives():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-interaction-glare-{scene.case_id}"
        case = _diagnostic_case(scene.frame, glass, scene.case_id)
        row = run_interaction_variant(scene.frame.copy(), case)
        assert row.combined_oil_y is None, scene.case_id


def _structural_foam_frames():
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
        cv2.rectangle(frame, (122, band_y), (197, band_y + band_height - 1), (band_value,) * 3, -1)
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
        glass.id = f"s11-interaction-foam-{index}"
        case = _diagnostic_case(frame, glass, f"foam-{index}", foam=True)
        p0 = evidence_probe.run_variant(frame.copy(), case, "P0")
        row = run_interaction_variant(frame.copy(), case)
        assert p0.foam_y is not None, index
        assert row.foam_y == p0.foam_y, index
        assert row.combined_oil_y is None, index


def test_manifest_declares_no_material_interaction_and_bounded_resources() -> None:
    manifest = build_manifest(_run_corpus_experiment())
    assert manifest["baseline_main_sha"] == "fd3c7baa6cc6f6095343a1da2cdba4375914c799"
    native = manifest["aggregate"]["brightness_1.00"]
    assert native["p0"]["oil_coverage"] == 7
    assert native["p2"]["oil_coverage"] == 7
    assert native["spatial"]["oil_coverage"] == 9
    assert native["combined"]["oil_coverage"] == 9
    assert native["combined_only_recovery"] == []
    assert manifest["resource_bound"] == {
        "maximum_path_sector_row_evaluations": 125,
        "retained_temporal_state": 0,
        "new_dependencies": 0,
    }
