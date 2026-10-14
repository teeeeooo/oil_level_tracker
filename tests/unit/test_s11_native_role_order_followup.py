"""Saved-weight followup must retain unknowns and never acquire new truth."""
import copy

import numpy as np
import pytest

from tests.diagnostics import s11_native_role_order_followup as follow


def roster():
    packet = dict(source_recording=dict(sha256="new-source"), frame=1063, fragments=[])
    units = []
    for fid in [444, 453, 687, 900, 901]:
        f = dict(id=f"s7/fragment-{fid}", fragment_id=fid, source_path_xy=[[2, fid]],
                 context_support=dict(status=follow.order.READY if fid != 901 else "UNAVAILABLE"))
        packet["fragments"].append(f)
        units.append(dict(id=f["id"], native_fragment_id=fid, source_recording=packet["source_recording"],
                          frame=1063, context=copy.deepcopy(f["context_support"]),
                          path_sha256=follow.o2.fingerprint_json(f["source_path_xy"]),
                          review_role=follow.ROLES.get(fid), partition="followup", availability=f["context_support"]["status"]))
    return units, packet


def test_only_explicit_upper_and_structures_enter_two_constraints():
    units, packet = roster(); follow.validate_roster(units, packet, {"fit"})
    assert follow.order.pairs_by_source(units, "followup") == {
        "new-source": [["s7/fragment-687", "s7/fragment-444"], ["s7/fragment-687", "s7/fragment-453"]]}


@pytest.mark.parametrize("change,match", [("drop", "population"), ("duplicate", "duplicate"),
    ("label_unknown", "role changed"), ("swap_truth", "role changed"),
    ("support", "support changed"), ("unavailable_truth", "support unavailable"),
    ("source", "source leakage"), ("metadata", "availability/partition")])
def test_wrong_source_truth_support_or_population_is_rejected(change, match):
    units, packet = roster(); fit = {"fit"}
    if change == "drop": units.pop()
    if change == "duplicate": units.append(copy.deepcopy(units[0]))
    if change == "label_unknown": units[-1]["review_role"] = "STRUCTURE_BOUNDARY"
    if change == "swap_truth": units[2]["review_role"] = "STRUCTURE_BOUNDARY"
    if change == "support": units[0]["context"]["status"] = "UNAVAILABLE"
    if change == "unavailable_truth":
        units[0]["context"]["status"] = packet["fragments"][0]["context_support"]["status"] = "UNAVAILABLE"
        units[0]["availability"] = "UNAVAILABLE"
    if change == "source": fit.add("new-source")
    if change == "metadata": units[-1]["availability"] = follow.order.READY
    with pytest.raises(ValueError, match=match): follow.validate_roster(units, packet, fit)


def test_saved_weight_archive_is_exact_finite_float32_and_copied():
    original = {"w": np.arange(4, dtype=np.float32)}
    hashes = {"w": follow.old.array_hash(original["w"])}
    result = follow.checked_weights(original, hashes)
    result["w"][0] = 99
    assert original["w"][0] == 0
    for bad in [{}, {"extra": original["w"]}]:
        with pytest.raises(ValueError, match="keys"): follow.checked_weights(bad, hashes)
    for value in [original["w"]+1, original["w"].astype(np.float64), np.full(4, np.nan, np.float32)]:
        with pytest.raises(ValueError, match="bytes"): follow.checked_weights({"w": value}, hashes)
