"""Scoring/attribution contracts, not physical detector qualification."""
from copy import deepcopy
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from tests.diagnostics.s11_corroboration_peer_screen import audit_frame
from tests.unit.test_oil_candidate_authority import _candidate


def glass():
    return SimpleNamespace(detector_settings=SimpleNamespace(temporal_max_jump_px=32.0))


def inputs():
    target = _candidate(material_path=True)
    target.source = "material"
    peer = _candidate()
    peer.source = "phase"
    return [asdict(target), asdict(peer)]


def test_pair_attribution_keeps_all_maximum_ties_without_counting_votes():
    raw = inputs()
    raw.append(deepcopy(raw[1]))
    raw[2]["source"] = "second_phase"
    before = deepcopy(raw)
    row = audit_frame(raw, glass())[0]
    assert row["winning_peer_indexes"] == [1, 2]
    assert row["legacy_support"] == row["contributors"][0]["support"]
    assert row["legacy_support"] == row["nonrecursive_support"]
    assert raw == before


def test_duplicate_same_family_does_not_increase_support():
    raw = inputs()
    original = audit_frame(raw, glass())[0]
    raw.append(deepcopy(raw[0]))
    raw[2]["source"] = "renamed_material_descendant"
    current = audit_frame(raw, glass())[0]
    assert current["legacy_support"] == original["legacy_support"]
    assert current["winning_peer_indexes"] == [1]


@pytest.mark.parametrize("mapping,key,value", [
    ("features", "sequence_eligible", 0.0),
    ("features", "material_texture_conflict", 0.61),
    ("features", "artifact_likelihood", 1.0),
    ("penalties", "optics_conflict", 0.47),
])
def test_ineligible_or_opposed_peer_cannot_corroborate(mapping, key, value):
    raw = inputs()
    raw[1][mapping][key] = value
    if key == "artifact_likelihood":
        raw[1]["features"]["static_prior_contribution"] = 1.0
    row = audit_frame(raw, glass())[0]
    assert row["legacy_support"] == 0.0
    assert row["contributors"] == []


def test_missing_peer_primitives_are_reported_not_invented_as_measured_zero():
    raw = inputs()
    raw[1]["features"] = {"boundary_likelihood": 0.8}
    raw[1]["penalties"] = {}
    row = audit_frame(raw, glass())[0]
    assert row["legacy_support_pass"]  # characterization of existing scalar route
    assert not row["nonrecursive_support_pass"]
    evidence = row["contributors"][0]["evidence"]["availability"]
    assert not evidence["phase"]
    assert not evidence["material_texture"]
    assert not evidence["optics"]
    assert not evidence["artifact"]


def test_material_candidate_cannot_recursively_supply_its_own_seed():
    raw = inputs()
    rows = audit_frame(raw, glass())
    assert rows[0]["standalone_seed"]["eligible_seed"] is False
    assert rows[1]["standalone_seed"]["eligible_seed"] is True
    assert rows[1]["legacy_support_pass"]
    assert rows[1]["nonrecursive_support"] == 0
    assert not rows[1]["material_support_removed"]  # not a proposed gate consumer


def test_permutation_preserves_scores_and_semantic_peer_identity():
    raw = inputs()
    a = audit_frame(raw, glass())
    b = audit_frame(list(reversed(raw)), glass())
    def semantic(rows):
        return {r["source"]: (r["source_y"], r["legacy_support"], r["nonrecursive_support"],
                sorted((p["source"], p["source_y"], p["support"])
                       for p in r["contributors"])) for r in rows}
    assert semantic(a) == semantic(b)


def test_wrong_source_type_or_nonfinite_y_is_not_an_oil_peer():
    raw = inputs()
    raw[1]["kind"] = "foam_front"
    assert audit_frame(raw, glass())[0]["legacy_support"] == 0
    raw[1]["kind"] = "oil_air"
    raw[1]["y"] = float("nan")
    assert audit_frame(raw, glass())[0]["legacy_support"] == 0
