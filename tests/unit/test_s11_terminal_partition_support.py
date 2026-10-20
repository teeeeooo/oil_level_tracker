from __future__ import annotations

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidenceIndex
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics.s11_terminal_partition_support import support, terminal_support


def _candidate(source, y, *, conflict, terminal, material_path=False, glare=0.0):
    features = {
        "sequence_eligible": 1.0,
        "boundary_likelihood": 0.8,
        "artifact_likelihood": 0.1,
        "narrow_horizontal_coverage": 0.8,
        "raw_material_row_support": 0.9,
        "material_texture_conflict": conflict,
        "material_terminal_partition_support": terminal,
        "material_texture_evidence_available": 1.0,
    }
    if material_path:
        features["material_path"] = 1.0
    penalties = {"glare_conflict": glare} if glare else {}
    return BoundaryCandidate(source, BoundaryKind.OIL_AIR, y, features=features, penalties=penalties,
                             feature_score=0.8)


def _support(candidate, peers, *, exempt):
    candidates = (candidate, *peers)
    index = OilCandidateEvidenceIndex()
    for item in candidates:
        index.register(item)
    glass = InspectionRecipe.default_glass(320, 240, 1)
    original = resolver._cross_representation_support(candidate, candidates, glass, evidence_index=index)
    copy_off = support(candidate, candidates, glass, evidence_index=index, exempt_terminal_pairs=False)
    trial = support(candidate, candidates, glass, evidence_index=index, exempt_terminal_pairs=exempt)
    return original, copy_off, trial


def test_copy_equals_original_with_exemption_off():
    for conflict in (0.2, 0.75):
        for terminal in (0.0, 1.0):
            candidate = _candidate("phase_transition_scan", 833.0, conflict=conflict, terminal=terminal)
            peer = _candidate("material_path", 834.0, conflict=conflict, terminal=terminal, material_path=True)
            original, copy_off, _ = _support(candidate, (peer,), exempt=False)
            assert copy_off == original


def test_terminal_boundary_pair_supports_each_other_despite_texture_conflict():
    candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75, terminal=1.0)
    peer = _candidate("material_path", 833.0, conflict=0.75, terminal=1.0, material_path=True)
    original, _, trial = _support(candidate, (peer,), exempt=True)
    assert original == 0.0
    assert trial > 0.12


def test_non_terminal_candidate_or_peer_stays_excluded():
    terminal_peer = _candidate("material_path", 833.0, conflict=0.75, terminal=1.0, material_path=True)
    inner_peer = _candidate("material_path", 833.0, conflict=0.75, terminal=0.0, material_path=True)
    inner_candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75, terminal=0.0)
    terminal_candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75, terminal=1.0)
    assert _support(inner_candidate, (terminal_peer,), exempt=True)[2] == 0.0
    assert _support(terminal_candidate, (inner_peer,), exempt=True)[2] == 0.0


def test_optics_exclusion_is_unchanged():
    candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75, terminal=1.0)
    peer = _candidate("material_path", 833.0, conflict=0.75, terminal=1.0, material_path=True, glare=0.5)
    original, copy_off, trial = _support(candidate, (peer,), exempt=True)
    assert original == copy_off == trial == 0.0


def test_patch_verifies_copy_and_is_removed():
    original = resolver._cross_representation_support
    with terminal_support() as operations:
        assert resolver._cross_representation_support is not original
        candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75, terminal=1.0)
        peer = _candidate("material_path", 833.0, conflict=0.75, terminal=1.0, material_path=True)
        index = OilCandidateEvidenceIndex()
        index.register(candidate)
        index.register(peer)
        glass = InspectionRecipe.default_glass(320, 240, 1)
        value = resolver._cross_representation_support(candidate, (candidate, peer), glass, evidence_index=index)
    assert value > 0.12
    assert len(operations) == 1 and operations[0]["ordinary"] == 0.0
    assert resolver._cross_representation_support is original
