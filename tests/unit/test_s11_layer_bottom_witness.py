from __future__ import annotations

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_material_path import material_layer_context_features
from tests.diagnostics import s11_layer_bottom_witness as lbw

H, W = 200, 100


def _rasters(*textured, mask_columns=None):
    material = np.zeros((H, W))
    for start, stop in textured:
        material[start:stop, :] = 0.9
    effective = np.full((H, W), 255, dtype=np.uint8)
    if mask_columns is not None:
        effective[:, mask_columns[0]:mask_columns[1]] = 0
    return material, effective, np.zeros((H, W), dtype=np.uint8)


def test_bottom_of_textured_layer_is_supported():
    material, effective, glare = _rasters((20, 100))
    assert lbw.witness(material, effective, glare, 100)["decision"] == "INTERFACE_SUPPORTED"


def test_row_inside_the_layer_is_interior():
    material, effective, glare = _rasters((20, 100))
    assert lbw.witness(material, effective, glare, 60)["decision"] == "INTERNAL_OR_ARTIFACT"


def test_lower_structure_below_clean_oil_is_not_supported():
    material, effective, glare = _rasters((20, 100), (150, 190))
    assert lbw.witness(material, effective, glare, 150)["decision"] != "INTERFACE_SUPPORTED"


def test_upper_sublayer_with_texture_within_depth_below_is_interior():
    # depth = round(0.16 * 200) = 32; a 10-row gap leaves texture within reach.
    material, effective, glare = _rasters((20, 60), (70, 120))
    assert lbw.witness(material, effective, glare, 60)["decision"] == "INTERNAL_OR_ARTIFACT"
    assert lbw.witness(material, effective, glare, 120)["decision"] == "INTERFACE_SUPPORTED"


def test_masked_sectors_leave_the_witness_unresolved():
    material, effective, glare = _rasters((20, 100))
    effective[:, 10:90] = 0
    result = lbw.witness(material, effective, glare, 100)
    assert result["decision"] == "UNRESOLVED"
    assert len(result["states"]) < lbw.MIN_SECTORS or result["counts"]["TERMINAL"] < lbw.MIN_SECTORS


def test_self_check_uses_the_existing_feature_function():
    material, effective, glare = _rasters((20, 100))
    stored = material_layer_context_features(material, effective, glare, local_y=100.0)
    assert lbw.self_check(material, effective, glare, 100.0, stored) is True
    shifted = dict(stored, material_terminal_partition_support=stored["material_terminal_partition_support"] - 0.2)
    assert lbw.self_check(material, effective, glare, 100.0, shifted) is False
    assert lbw.self_check(material, effective, glare, 100.0, {}) is None


def test_crop_origin_prefers_state_and_rejects_inconsistent_candidates():
    record = {"state": {"foam_component_diagnostics": {"crop_origin": [5, 40]}}, "candidates": []}
    assert lbw.origin_from_record(record) == (40.0, "state")
    record = {"state": {}, "candidates": [{"canonical_y": 140.0, "local_y": 100.0},
                                          {"canonical_y": 150.0, "local_y": 110.0}]}
    assert lbw.origin_from_record(record) == (40.0, "candidate_local_y")
    record["candidates"].append({"canonical_y": 150.0, "local_y": 100.0})
    with pytest.raises(ValueError):
        lbw.origin_from_record(record)


def test_saved_trace_pngs_round_trip_through_the_real_writer(tmp_path):
    import json
    import shutil
    from pathlib import Path
    from types import SimpleNamespace

    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
    from oil_tracker.adapters.vision.phase_frame_detection import unit_image
    from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
    from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
    from oil_tracker.domain.enums import BoundaryKind, FillState
    from oil_tracker.domain.recipe import InspectionRecipe
    from oil_tracker.domain.session import DebugTraceLevel

    material, effective, glare = _rasters((20, 100))
    origin = 40.0
    features = {**material_layer_context_features(material, effective, glare, local_y=100.0), "local_y": 100.0}
    candidate = BoundaryCandidate("material_path", BoundaryKind.OIL_AIR, 100.0 + origin, features=features)
    detection = PhaseDetection(glass_id="g", frame_index=3, time_sec=1.5, fill_state=FillState.PARTIAL_VISIBLE,
                               candidates=[candidate])
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.id = "g"
    images = {"foam_combined_evidence": unit_image(material), "effective_mask": effective, "glare_mask": glare}
    writer = JsonlDebugTraceWriter("run", DebugTraceLevel.BASIC, staging_parent=tmp_path)
    writer.write(glass, detection, SimpleNamespace(images=images, state={}),
                 DebugCaptureDecision(True, (DebugCaptureReason.FOAM,)))
    staging = Path(writer.finalize().staging_directory)
    root = tmp_path / "bundle"
    shutil.copytree(staging, root / "debug")
    record = json.loads((root / "debug" / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert lbw.origin_from_record(record) == (origin, "candidate_local_y")
    rows = lbw.evaluate(lbw.rasters_from_bundle(root, record), record["candidates"], origin)
    assert [(row["decision"], row["check"]) for row in rows] == [("INTERFACE_SUPPORTED", True)]


def test_lbw2_supports_a_thin_oil_band_over_structure_that_lbw1_rejects():
    material, effective, glare = _rasters((20, 100), (112, 150))
    assert lbw.witness(material, effective, glare, 100)["decision"] == "INTERNAL_OR_ARTIFACT"
    assert lbw.witness(material, effective, glare, 100, tolerance=12)["decision"] == "INTERFACE_SUPPORTED"


def test_lbw2_localizes_within_the_same_boundary_tolerance_only():
    material, effective, glare = _rasters((20, 100))
    assert lbw.witness(material, effective, glare, 92, tolerance=12)["decision"] == "INTERFACE_SUPPORTED"
    assert lbw.witness(material, effective, glare, 70, tolerance=12)["decision"] == "INTERNAL_OR_ARTIFACT"


def test_lbw2_short_gap_inside_the_layer_stays_interior():
    material, effective, glare = _rasters((20, 60), (63, 120))
    assert lbw.witness(material, effective, glare, 60, tolerance=12)["decision"] == "INTERNAL_OR_ARTIFACT"
    assert lbw.witness(material, effective, glare, 120, tolerance=12)["decision"] == "INTERFACE_SUPPORTED"


def test_lbw2_lower_structure_below_clean_oil_is_not_supported():
    material, effective, glare = _rasters((20, 100), (130, 170))
    assert lbw.witness(material, effective, glare, 130, tolerance=12)["decision"] != "INTERFACE_SUPPORTED"
