from __future__ import annotations

from dataclasses import dataclass

import pytest

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidenceIndex
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_layer_bottom_qualified_authority as lbq

GLASS = InspectionRecipe.default_glass(320, 240, 1)


def _candidate(source, y, *, conflict=0.75, unit=None, material_path=False):
    features = {
        "sequence_eligible": 1.0,
        "boundary_likelihood": 0.8,
        "artifact_likelihood": 0.1,
        "narrow_horizontal_coverage": 0.8,
        "raw_material_row_support": 0.9,
        "material_texture_conflict": conflict,
        "material_terminal_partition_support": 1.0,
        "material_texture_evidence_available": 1.0,
    }
    if material_path:
        features["material_path"] = 1.0
    if unit is not None:
        features[lbq.FEATURE] = float(unit)
    return BoundaryCandidate(source, BoundaryKind.OIL_AIR, y, features=features, feature_score=0.8)


def _support(candidate, peers, *, qualified):
    candidates = (candidate, *peers)
    index = OilCandidateEvidenceIndex()
    for item in candidates:
        index.register(item)
    original = resolver._cross_representation_support(candidate, candidates, GLASS, evidence_index=index)
    copy_off = lbq.support(candidate, candidates, GLASS, evidence_index=index, qualified=False)
    trial = lbq.support(candidate, candidates, GLASS, evidence_index=index, qualified=qualified)
    return original, copy_off, trial


def test_support_copy_equals_original_when_off():
    for conflict in (0.2, 0.75):
        for unit in (None, False, True):
            candidate = _candidate("phase_transition_scan", 833.0, conflict=conflict, unit=unit)
            peer = _candidate("material_path", 834.0, conflict=conflict, unit=unit, material_path=True)
            original, copy_off, _ = _support(candidate, (peer,), qualified=False)
            assert copy_off == original


def test_unit_pair_counts_despite_texture_conflict():
    candidate = _candidate("phase_transition_scan", 833.0, unit=True)
    peer = _candidate("material_path", 833.0, unit=True, material_path=True)
    original, _, trial = _support(candidate, (peer,), qualified=True)
    assert original == 0.0
    assert trial > 0.12


@pytest.mark.parametrize("candidate_unit, peer_unit", [(True, False), (False, True), (None, True)])
def test_texture_peer_stays_excluded_unless_both_are_in_the_unit(candidate_unit, peer_unit):
    candidate = _candidate("phase_transition_scan", 833.0, unit=candidate_unit)
    peer = _candidate("material_path", 833.0, unit=peer_unit, material_path=True)
    assert _support(candidate, (peer,), qualified=True)[2] == 0.0


@dataclass(frozen=True)
class _Ref:
    candidate: BoundaryCandidate
    authority: object = resolver.OilCandidateAuthority.ANCHOR_ELIGIBLE
    initial_authority: object = resolver.OilCandidateAuthority.ANCHOR_ELIGIBLE
    post_track_authority: object = resolver.OilCandidateAuthority.ANCHOR_ELIGIBLE
    authority_reason: object = None
    authority_failed_gates: tuple = ()
    phase_identity: object = resolver.OilPhaseIdentity.ORDERED_LOWER_INTERFACE
    phase_identity_failed_gates: tuple = ()
    identity_contradiction: object = resolver.OilIdentityContradiction.NONE


def _refs(*rows):
    return [_Ref(_candidate("material_path", y, unit=unit)) for y, unit in rows]


def _anchor_ys(refs):
    return [ref.candidate.y for ref in refs if ref.authority is resolver.OilCandidateAuthority.ANCHOR_ELIGIBLE]


def test_demote_copy_equals_original_when_off():
    for rows in ([(235.0, False), (449.0, True), (453.0, True)], [(235.0, None), (300.0, None)],
                 [(449.0, True)], []):
        refs = _refs(*rows)
        assert lbq.demote(refs, GLASS, qualified=False) == resolver._demote_non_nearest_ordered_lower_anchors(refs, GLASS)


def test_upper_non_unit_anchor_is_demoted_below_a_unit_anchor():
    # Windows 677 s shape: the air-Foam top anchor above the supported layer bottom.
    changes = []
    refs = lbq.demote(_refs((235.0, False), (449.0, True), (453.0, True), (480.0, False)), GLASS,
                      qualified=True, changes=changes)
    assert _anchor_ys(refs) == [449.0, 453.0]
    assert [c["y"] for c in changes] == [235.0]
    demoted = next(ref for ref in refs if ref.candidate.y == 235.0)
    assert demoted.authority_failed_gates == (lbq.ABOVE_GATE,)
    assert demoted.identity_contradiction is resolver.OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER


def test_empty_unit_keeps_the_existing_rule():
    # Windows 678.5 s shape: the boundary is UNRESOLVED, so the upper anchor stays first.
    rows = [(229.0, False), (392.0, False), (403.0, False)]
    refs = _refs(*rows)
    assert lbq.demote(refs, GLASS, qualified=True) == resolver._demote_non_nearest_ordered_lower_anchors(refs, GLASS)
    assert _anchor_ys(lbq.demote(refs, GLASS, qualified=True)) == [229.0]


def test_patch_verifies_copies_and_is_removed():
    original_support = resolver._cross_representation_support
    original_demote = resolver._demote_non_nearest_ordered_lower_anchors
    candidate = _candidate("phase_transition_scan", 833.0, unit=True)
    peer = _candidate("material_path", 833.0, unit=True, material_path=True)
    index = OilCandidateEvidenceIndex()
    index.register(candidate)
    index.register(peer)
    with lbq.qualified_authority() as operations:
        value = resolver._cross_representation_support(candidate, (candidate, peer), GLASS, evidence_index=index)
        resolver._demote_non_nearest_ordered_lower_anchors(_refs((235.0, False), (449.0, True)), GLASS)
    assert value > 0.12
    assert [op["consumer"] for op in operations] == ["support", "demote"]
    assert resolver._cross_representation_support is original_support
    assert resolver._demote_non_nearest_ordered_lower_anchors is original_demote


def test_attach_marks_only_oil_candidates_and_does_not_mutate_raw():
    raw = [dict(frame_index=0, candidates=[dict(kind="oil_air", features={}), dict(kind="foam_front", features={}),
                                            dict(kind="oil_air", features={})])]
    attached = lbq.attach(raw, {0: [2]})
    assert [c["features"].get(lbq.FEATURE) for c in attached[0]["candidates"]] == [0.0, None, 1.0]
    assert raw[0]["candidates"][0]["features"] == {}


def test_bind_units_requires_identical_candidates():
    raw = [dict(frame_index=15, candidates=[dict(kind="oil_air", source="material_path", y=835.0)])]
    frames = {("g", 15): dict(unit=[0], candidates=[("oil_air", "material_path", 835.0)])}
    assert lbq.bind_units(raw, frames) == {15: [0]}
    frames[("g", 15)]["candidates"] = [("oil_air", "material_path", 836.0)]
    with pytest.raises(Exception):
        lbq.bind_units(raw, frames)
