from copy import deepcopy

import numpy as np
import pytest

from tests.diagnostics.s11_corroboration_geometry_screen import (
    bind_packet, compare_native, native_sectors, verify_band,
)
from oil_tracker.adapters.vision.oil_interface_diagnostics import (
    _measure_sector, _sector_profile,
)


def packet():
    candidates = [{"source": "a", "y": 20.0, "kind": "oil_air"},
                  {"source": "foam", "y": 5.0, "kind": "foam_front"},
                  {"source": "b", "y": 22.0, "kind": "oil_air"}]
    raw = {"frame_index": 42, "candidates": candidates}
    witness = {"source_frame_index": 42, "coordinate_space": "source_frame_y",
        "candidate_index_space": "detection.candidates_before_trace_score_sort",
        "candidates": [{"candidate_input_index": i, "source": candidates[i]["source"],
                        "canonical_y": candidates[i]["y"]} for i in (0, 2)]}
    return raw, witness


def test_bind_uses_original_offsets_not_sorted_or_oil_only_indexes():
    raw, witness = packet()
    witness["candidates"].reverse()
    assert list(bind_packet(raw, witness)) == [2, 0]


@pytest.mark.parametrize("field,value", [
    ("source_frame_index", 43), ("coordinate_space", "crop_y"),
    ("candidate_index_space", "sorted"),
])
def test_packet_metadata_mismatch_is_rejected(field, value):
    raw, witness = packet()
    witness[field] = value
    with pytest.raises(ValueError):
        bind_packet(raw, witness)


@pytest.mark.parametrize("field,value", [
    ("candidate_input_index", 1), ("source", "other"), ("canonical_y", 21.0),
])
def test_candidate_identity_mismatch_is_rejected(field, value):
    raw, witness = packet()
    witness["candidates"][0][field] = value
    with pytest.raises(ValueError):
        bind_packet(raw, witness)


@pytest.mark.parametrize("mode", ["duplicate", "missing", "wrong-kind"])
def test_population_mismatch_is_rejected(mode):
    raw, witness = packet()
    if mode == "duplicate":
        witness["candidates"].append(deepcopy(witness["candidates"][0]))
    elif mode == "missing":
        witness["candidates"].pop()
    else:
        raw["candidates"][0]["kind"] = "foam_front"
    with pytest.raises(ValueError):
        bind_packet(raw, witness)


def native(y=20.0, x0=10, x1=20):
    return {"path_aligned": {"reason": "native_generator_path",
        "shared_derivation": ["current_frame_gray"], "sectors": [
            {"sector": 0, "source_x_range": [x0, x1], "path_source_y": y,
             "near_signed_contrast": -0.2}]}}


def test_equal_native_geometry_never_becomes_physical_identity():
    row = native()
    before = deepcopy(row)
    result = compare_native(row, row)
    assert result["cells"][0]["absolute_delta_y"] == 0.0
    assert result["physical_same_interface"] == "NOT_EVALUATED"
    assert result["measurement_independence"] == "NOT_ESTABLISHED"
    assert row == before


def test_center_only_never_becomes_native_and_absence_is_not_zero_distance():
    center = {"path_aligned": {"reason": "no_captured_native_path", "sectors": []},
              "sectors": [{"peak_source_y": 20.0}]}
    result = compare_native(native(), center)
    assert result["status"] == "NATIVE_UNAVAILABLE"
    assert result["cells"] == []


def test_common_x_support_and_symmetric_distances():
    a, b = native(20.0, 10, 20), native(23.0, 15, 25)
    ab, ba = compare_native(a, b), compare_native(b, a)
    assert ab["cells"][0]["source_x_range"] == [15, 20]
    assert ab["cells"][0]["absolute_delta_y"] == ba["cells"][0]["absolute_delta_y"] == 3.0
    assert compare_native(a, native(20, 30, 40))["cells"] == []


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_invalid_native_coordinate_is_not_usable(value):
    with pytest.raises(ValueError):
        native_sectors(native(value))


def test_duplicate_sector_rejected():
    row = native()
    row["path_aligned"]["sectors"] *= 2
    with pytest.raises(ValueError):
        native_sectors(row)


@pytest.mark.parametrize("center", [-4, 0, 2, 10, 20, 34, 40])
@pytest.mark.parametrize("mask_mode", ["full", "partial", "empty"])
def test_direct_raster_moments_match_existing_prefix_sum_measurements(center, mask_mode):
    rng = np.random.default_rng(42)
    gray = rng.integers(0, 256, size=(37, 41), dtype=np.uint8)
    visible = np.ones_like(gray, dtype=bool)
    if mask_mode == "partial":
        visible = rng.random(gray.shape) > 0.4
    elif mask_mode == "empty":
        visible[:] = False
    profile = _sector_profile(gray, visible, np.zeros_like(gray, dtype=float),
                              None, np.zeros_like(visible), 3, 17)
    sector = _measure_sector(profile, sector=0, center=center, band=3,
                             local_y=center, crop_origin=(100, 200), height=37)
    for band in sector["bands"].values():
        result = verify_band(gray, visible, [100, 200], sector, band)
        assert result["mismatches"] == []


def test_corrupt_saved_moment_does_not_pass_as_missing_zero():
    gray = np.ones((20, 20), dtype=np.uint8)*128
    visible = np.ones_like(gray, dtype=bool)
    sector = {"source_x_range": [0, 20]}
    band = {"local_y_range": [2, 5], "available": True,
            "valid_pixel_count": 60, "valid_fraction": 1.0,
            "gray_mean": None, "gray_std": 0.0}
    result = verify_band(gray, visible, [0, 0], sector, band)
    assert "gray_mean_missing_or_nonfinite" in result["mismatches"]
