from __future__ import annotations

import pytest

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.oil_candidate_authority import (
    AuthorityContext,
    OilCandidateAuthority,
    evaluate_candidate_authority,
)
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidenceIndex
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_layer_bottom_topology as lbt

GLASS = InspectionRecipe.default_glass(320, 240, 1)
CONFIG = resolver.OilObservationResolverConfig()


def _candidate(source, y, *, unit=None, top=None, lower=None, conflict=0.75, material_path=False):
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
        features[lbt.UNIT] = float(unit)
    if top is not None:
        features[lbt.TOP] = float(top)
    if lower is not None:
        features["composition_lower_reserve"] = float(lower)
    return BoundaryCandidate(source, BoundaryKind.OIL_AIR, y, features=features, feature_score=0.8)


def _context(row=210.0, age=1.0, separation=10.0):
    return AuthorityContext(foam_material_row=row, foam_seed_age_seconds=age, lower_separation_px=separation)


def _patched_tier(candidate, context):
    with lbt.topology() as operations:
        decision = resolver.evaluate_candidate_authority(candidate, CONFIG, context)
    return decision, operations


def test_row_above_the_unit_top_is_invalid_in_context():
    # Windows 677 s shape: air-Foam top Y235 above the layer bottom B = 449.
    decision, operations = _patched_tier(_candidate("material_path", 235.0, unit=False, top=449.0), _context())
    assert decision.tier is OilCandidateAuthority.HARD_INVALID
    assert decision.failed_gates == (lbt.GATE,)
    assert [op["consumer"] for op in operations] == ["E1"]


@pytest.mark.parametrize("y", [449.0, 453.0, 470.0])
def test_rows_at_or_below_the_unit_top_are_untouched(y):
    candidate = _candidate("material_path", y, unit=True, top=449.0)
    decision, operations = _patched_tier(candidate, _context())
    assert decision == evaluate_candidate_authority(candidate, CONFIG, _context())
    assert operations == []


@pytest.mark.parametrize("context, top", [
    (_context(row=None), 449.0),         # no Foam material row
    (_context(age=3.5), 449.0),          # old Foam seed
    (_context(age=None), 449.0),         # seed age unknown
    (_context(), None),                  # empty unit (Windows 678.5 s shape)
    (_context(row=445.0), 449.0),        # unit top not below the Foam row by the separation
])
def test_out_of_context_frames_are_unchanged(context, top):
    candidate = _candidate("material_path", 235.0, unit=False, top=top)
    decision, operations = _patched_tier(candidate, context)
    assert decision == evaluate_candidate_authority(candidate, CONFIG, context)
    assert operations == []


def test_disabled_patch_equals_original():
    candidate = _candidate("material_path", 235.0, unit=False, top=449.0)
    with lbt.topology(enabled=False) as operations:
        decision = resolver.evaluate_candidate_authority(candidate, CONFIG, _context())
    assert decision == evaluate_candidate_authority(candidate, CONFIG, _context())
    assert operations == []


def _support(candidate, peer):
    index = OilCandidateEvidenceIndex()
    index.register(candidate)
    index.register(peer)
    with lbt.topology() as _:
        return resolver._cross_representation_support(candidate, (candidate, peer), GLASS, evidence_index=index)


def test_unit_pair_support_requires_an_ordered_lower_candidate():
    peer = _candidate("material_path", 833.0, unit=True, material_path=True)
    assert _support(_candidate("phase_transition_scan", 833.0, unit=True, lower=1.0), peer) > 0.12
    assert _support(_candidate("phase_transition_scan", 833.0, unit=True, lower=0.0), peer) == 0.0
    assert _support(_candidate("phase_transition_scan", 833.0, unit=True), peer) == 0.0


def test_nearest_anchor_rule_is_not_patched_and_patches_are_removed():
    originals = (resolver.evaluate_candidate_authority, resolver._cross_representation_support,
                 resolver._demote_non_nearest_ordered_lower_anchors)
    with lbt.topology():
        assert resolver._demote_non_nearest_ordered_lower_anchors is originals[2]
        assert resolver.evaluate_candidate_authority is not originals[0]
    assert (resolver.evaluate_candidate_authority, resolver._cross_representation_support,
            resolver._demote_non_nearest_ordered_lower_anchors) == originals


def test_attach_sets_the_unit_top_only_for_non_empty_units():
    raw = [dict(frame_index=0, candidates=[dict(kind="oil_air", y=835.0, features={}),
                                            dict(kind="oil_air", y=844.0, features={}),
                                            dict(kind="foam_front", y=812.0, features={})]),
           dict(frame_index=15, candidates=[dict(kind="oil_air", y=830.0, features={})])]
    attached = lbt.attach(raw, {0: [0, 1], 15: []})
    assert [c["features"].get(lbt.TOP) for c in attached[0]["candidates"]] == [835.0, 835.0, None]
    assert attached[1]["candidates"][0]["features"] == {lbt.UNIT: 0.0}
    assert raw[0]["candidates"][0]["features"] == {}
