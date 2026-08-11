from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from oil_observability_fixtures import (
    historical_glare_negatives,
    single_frame_observability_collisions,
)
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_evidence_probe as evidence_probe
from tests.diagnostics.s11_p2_spatial_interaction_probe import (
    run_experiment,
    run_interaction_variant,
)
from tests.s11_local_corpus import require_s11_local_corpus


def _archived_interaction_manifest():
    path = (
        Path(__file__).resolve().parents[1]
        / "docs/50-diagnostics/s11/s11-a-p2-spatial-interaction-probe-manifest.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _archived_interaction_rows():
    return {
        (row["transform"], row["case_id"]): row
        for row in _archived_interaction_manifest()["rows"]
    }

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
    native = _archived_interaction_manifest()["aggregate"]["brightness_1.00"]
    assert native["p0"]["oil_coverage"] == 7
    assert native["p2"]["oil_coverage"] == 7
    assert native["spatial"]["oil_coverage"] == 9
    assert native["combined"]["oil_coverage"] == 9
    assert native["p0"]["oil_mae_px"] == 31.0 / 7.0
    assert native["combined"]["oil_mae_px"] == 44.0 / 9.0
    assert native["combined_only_recovery"] == []


def test_known_p2_false_no_interface_transitions_do_not_gain_combined_numeric_oil() -> None:
    rows = _archived_interaction_rows()
    expected = (
        ("brightness_0.60", "sample3:900"),
        ("brightness_0.45", "base_sample_1:144"),
        ("brightness_0.45", "sample3:900"),
        ("brightness_0.45", "sample3:1035"),
    )
    for key in expected:
        row = rows[key]
        assert row["p0_current_kind"] == "no_interface"
        assert row["p2_current_kind"] == "ambiguous"
        assert row["p2_oil_y"] is None
        assert row["combined_candidate_oil_y"] is None
        assert row["combined_oil_y"] is None
        assert row["combined_route"] == "P2_AMBIGUOUS_NO_SPATIAL_CANDIDATE"


def test_combined_keeps_existing_spatial_low_light_recovery_but_adds_no_interaction_recovery() -> None:
    rows = _archived_interaction_rows()
    row = rows[("brightness_0.60", "sample3:1035")]
    assert row["p0_current_kind"] == "ambiguous"
    assert row["p2_current_kind"] == "ambiguous"
    assert row["spatial_oil_y"] == 245.0
    assert row["combined_oil_y"] == 245.0
    assert row["combined_route"] == "COMBINED_ACCEPTED"
    assert row["combined_error_px"] == 2.0


def test_low_light_sample4_boundary_keeps_spatial_rejection_or_direct_same_interface_recovery() -> None:
    rows = {(row.transform, row.case_id): row for row in _run_corpus_experiment()}
    rejected = rows[("brightness_0.60", "sample4:450")]
    assert rejected.combined_candidate_oil_y == 804.0
    assert rejected.combined_oil_y is None
    assert rejected.combined_route == "COMBINED_REJECTED"
    assert rejected.path is not None
    assert rejected.path.reason == "candidate_lacks_symmetric_phase_window"

    recovered = rows[("brightness_0.45", "sample4:450")]
    assert recovered.combined_candidate_oil_y is None
    assert recovered.combined_oil_y == 853.0
    assert recovered.combined_error_px == 0.5
    assert recovered.combined_route == "P2_BASE"
    assert recovered.path is None


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
    assert candidate_count == 16
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


def test_manifest_declares_no_material_interaction_and_bounded_resources() -> None:
    manifest = _archived_interaction_manifest()
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
