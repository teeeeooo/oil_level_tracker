from __future__ import annotations

from dataclasses import replace

import pytest

from oil_tracker.adapters.vision.oil_candidate_authority import OilCandidateAuthority
from oil_tracker.adapters.vision.oil_interface_selector import BoundedOilInterfaceSelector
from oil_tracker.adapters.vision.oil_phase_identity import OilPhaseIdentity
from oil_tracker.adapters.vision.oil_phase_lifecycle import OilMaterialPhase, OilMaterialPhaseLifecycleOwner
from oil_tracker.adapters.vision.oil_sequence_types import OilSequenceNode, TrackletConfirmationProfile, TrackletLifecycle
from oil_tracker.domain.enums import InitialObservationState
from tests.unit.test_oil_phase_lifecycle import _detections, _node, _policy, _selector_policy, _unknown

FULL = InitialObservationState.FULL_NO_INTERFACE


def _owner(enabled=True, initial=FULL):
    return OilMaterialPhaseLifecycleOwner(replace(
        _policy(confirmed_initial_state=initial), initial_full_observation_enabled=enabled,
    ))


def _interface(frame=0, tracklet="a", y=55., **changes):
    return _node(frame, tracklet, y, **{
        "direction": -1, "progress": 20.,
        "phase_identity": OilPhaseIdentity.DIRECT_INTERFACE, **changes,
    })


def _select(layers, phase):
    return BoundedOilInterfaceSelector(_selector_policy()).resolve(
        layers, _detections(len(layers)), FULL, phase.allowed_tracklet_ids, phase.owner_chains,
    )


@pytest.mark.parametrize("direction,progress", [(0, 0.), (-1, 20.)])
def test_current_interface_can_be_observed_without_certifying_drain(direction, progress):
    row = _interface(direction=direction, progress=progress)
    layers = ((row, _unknown(0)),)
    baseline, trial = (_owner(enabled).resolve(layers) for enabled in (False, True))
    assert baseline.allowed_tracklet_ids == (frozenset(),)
    assert trial.phases == (OilMaterialPhase.OBSERVED_INTERFACE,)
    assert _select(layers, trial)[0].candidate_ref is row.candidate_ref
    assert trial.diagnostics[0]["release_evaluations"] == baseline.diagnostics[0]["release_evaluations"]
    assert trial.diagnostics[0]["release_source"] == "none"
    assert trial.diagnostics[0]["initial_full_observation"]["motion_phase"] == "filled_barrier"


@pytest.mark.parametrize("changes", [
    {"authority": OilCandidateAuthority.CANDIDATE_ONLY},
    {"authority": OilCandidateAuthority.HARD_INVALID},
    {"tracklet_incompatible": True},
    {"material_conflict": .9},
    {"tracklet_material_conflict": .9},
    {"confirmation_profile": TrackletConfirmationProfile.NONE},
    {"lifecycle": TrackletLifecycle.PROVISIONAL,
     "confirmation_profile": TrackletConfirmationProfile.NONE},
    {"lifecycle": TrackletLifecycle.LOST},
    {"lifecycle": TrackletLifecycle.TERMINATED},
])
def test_observation_does_not_promote_unsupported_current_rows(changes):
    layers = ((_interface(**changes), _unknown(0)),)
    trial = _owner().resolve(layers)
    assert trial.allowed_tracklet_ids == (frozenset(),)
    assert _select(layers, trial)[0].y is None


@pytest.mark.parametrize("identity,lifecycle", [
    (OilPhaseIdentity.CONTINUATION_ONLY, TrackletLifecycle.CONTINUING),
    (OilPhaseIdentity.DIRECT_INTERFACE, TrackletLifecycle.CONTINUING),
    (OilPhaseIdentity.DIRECT_INTERFACE, TrackletLifecycle.PROVISIONAL),
])
def test_bounded_admitted_observation_does_not_need_a_fresh_anchor(identity, lifecycle):
    # The three transferred Windows losses have these distinct evidence shapes.
    # The helper tests admission/provenance, not the physical identity of that video.
    row = _interface(authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                     phase_identity=identity, lifecycle=lifecycle)
    layers = ((row, _unknown(0)),)
    baseline, trial = (_owner(enabled).resolve(layers) for enabled in (False, True))
    assert baseline.allowed_tracklet_ids == (frozenset(),)
    assert trial.phases == (OilMaterialPhase.OBSERVED_INTERFACE,)
    assert _select(layers, trial)[0].candidate_ref is row.candidate_ref
    evaluation = trial.diagnostics[0]["initial_full_observation"]["evaluations"][0]
    assert evaluation["passed"]
    assert evaluation["observation_evidence"]["authority"] == "CONTINUATION_ELIGIBLE"


def test_unadmitted_provisional_row_cannot_borrow_confirmation():
    row = _interface(lifecycle=TrackletLifecycle.PROVISIONAL)
    row = replace(row, candidate_ref=replace(row.candidate_ref, tracklet_admitted=False))
    layers = ((row, _unknown(0)),)
    trial = _owner().resolve(layers)
    assert trial.allowed_tracklet_ids == (frozenset(),)
    assert _select(layers, trial)[0].y is None


def test_continuation_uses_current_measurement_and_loss_cannot_create_full():
    layers = (
        (_interface(0, y=55.), _unknown(0)),
        (_interface(1, y=35., authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                    phase_identity=OilPhaseIdentity.CONTINUATION_ONLY), _unknown(1)),
        (_interface(2, y=5., authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE), _unknown(2)),
        (_unknown(3),),
    )
    trial = _owner().resolve(layers)
    selected = _select(layers, trial)
    assert [node.y for node in selected] == [55., 35., 5., None]
    assert selected[-1].kind == "unknown"
    assert all(d["initial_full_observation"]["motion_phase"] == "filled_barrier"
               for d in trial.diagnostics)


def test_incompatible_anchor_cannot_supply_identity_to_another_owner():
    observed = _interface(tracklet="observed", authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                          lifecycle=TrackletLifecycle.PROVISIONAL)
    incompatible = _interface(tracklet="incompatible", y=56., tracklet_incompatible=True)
    layers = ((observed, incompatible, _unknown(0)),)
    trial = _owner().resolve(layers)
    assert trial.allowed_tracklet_ids == (frozenset({"observed"}),)
    assert trial.owner_chains == (("observed",),)
    assert _select(layers, trial)[0].candidate_ref is observed.candidate_ref


@pytest.mark.parametrize("kind", ["full", "empty"])
def test_current_no_interface_state_blocks_observation(kind):
    trial = _owner().resolve(((_interface(), OilSequenceNode(kind, 1., kind, state_evidence=.9), _unknown(0)),))
    assert trial.allowed_tracklet_ids == (frozenset(),)
    assert trial.diagnostics[0]["initial_full_observation"]["blocked_by_current_state"]


def test_typed_current_identity_contradiction_blocks_observation():
    trial = _owner().resolve(((_interface(), _unknown(0)),), identity_contradictions=(frozenset({"a"}),))
    assert trial.allowed_tracklet_ids == (frozenset(),)


@pytest.mark.parametrize("initial", [None, InitialObservationState.EMPTY_NO_INTERFACE])
def test_other_initial_contexts_keep_original_phase_constraints(initial):
    layers = tuple((_interface(i), _unknown(i)) for i in range(5))
    baseline, trial = (_owner(enabled, initial).resolve(layers) for enabled in (False, True))
    assert trial.phases == baseline.phases
    assert trial.allowed_tracklet_ids == baseline.allowed_tracklet_ids
    assert all(not d["initial_full_observation"]["evaluated"] for d in trial.diagnostics)


def test_competing_observation_owners_remain_ambiguous_under_permutation():
    a, b = _interface(tracklet="a", y=55.), _interface(tracklet="b", y=65.)
    for layer in ((a, b, _unknown(0)), (b, a, _unknown(0))):
        trial = _owner().resolve((layer,))
        assert trial.allowed_tracklet_ids == (frozenset({"a", "b"}),)
        assert trial.owner_chains == ((),)
        assert _select((layer,), trial)[0].kind == "unknown"


def test_missing_current_row_has_no_carry_and_fresh_owner_can_be_observed():
    layers = (
        (_interface(0), _unknown(0)), (_unknown(1),), (_unknown(2),),
        (_interface(3, tracklet="fresh"), _unknown(3)),
    )
    baseline, trial = (_owner(enabled).resolve(layers) for enabled in (False, True))
    assert trial.allowed_tracklet_ids == (frozenset({"a"}), frozenset(), frozenset(), frozenset({"fresh"}))
    assert trial.owner_chains[-1] == ("fresh",)
    assert [n.y for n in _select(layers, trial)] == [55., None, None, 55.]
    for original, actual in zip(baseline.diagnostics, trial.diagnostics, strict=True):
        assert {k: v for k, v in actual.items() if k not in {"initial_full_observation", "allowed_mode", "allowed_tracklet_ids"}} == {
            k: v for k, v in original.items() if k not in {"allowed_mode", "allowed_tracklet_ids"}
        }


def test_existing_downward_release_and_ambiguity_take_precedence():
    a = _interface(tracklet="a", direction=1)
    b = _interface(tracklet="b", y=65., direction=1)
    for layers in (((a, _unknown(0)),), ((a, b, _unknown(0)),)):
        baseline, trial = (_owner(enabled).resolve(layers) for enabled in (False, True))
        assert trial.phases == baseline.phases
        assert trial.allowed_tracklet_ids == baseline.allowed_tracklet_ids
        assert not trial.diagnostics[0]["initial_full_observation"]["evaluated"]


def test_refill_closure_does_not_reopen_via_initial_observation_route():
    rows = tuple(_interface(i, "drain", y, direction=1) for i, y in enumerate((50., 70., 90.)))
    refill = _interface(5, "refill", 35., progress=60., motion_support=.9, motion_coverage=.9)
    layers = tuple((row, _unknown(i)) for i, row in enumerate(rows)) + (
        (_unknown(3),), (_unknown(4),), (refill, _unknown(5)),
        (_unknown(6),), (_interface(7, "new", 100.), _unknown(7)),
    )
    baseline, trial = (_owner(enabled).resolve(layers) for enabled in (False, True))
    assert trial.phases == baseline.phases
    assert trial.allowed_tracklet_ids == baseline.allowed_tracklet_ids
    assert trial.phases[5] is OilMaterialPhase.FILLED_BARRIER
    assert all(not d["initial_full_observation"]["evaluated"] for d in trial.diagnostics[5:])
