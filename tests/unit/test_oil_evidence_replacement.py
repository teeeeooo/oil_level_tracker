"""Generic replacement controls through physical layers and final selection."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from oil_tracker.adapters.vision.oil_candidate_authority import (
    OilCandidateAuthority as Authority,
)
from oil_tracker.adapters.vision.oil_interface_selector import (
    build_interface_layers,
    BoundedOilInterfaceSelector,
)
from oil_tracker.adapters.vision.oil_phase_identity import (
    OilIdentityContradiction,
    OilPhaseIdentity as Identity,
)
from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilMaterialPhaseLifecycleOwner,
    OilMaterialPhase,
)
from oil_tracker.adapters.vision.oil_observation_resolver import (
    _demote_non_nearest_ordered_lower_anchors,
)
from oil_tracker.adapters.vision.oil_interface_tracklets import (
    DirectedInterfaceTrackletBuilder,
)
from oil_tracker.adapters.vision.oil_sequence_types import TrackletConfirmationProfile
from oil_tracker.domain.enums import InitialObservationState
from tests.unit.test_oil_phase_lifecycle import (
    _node,
    _policy,
    _detections,
    _selector_policy,
)
from tests.unit.test_oil_interface_tracklets import _policy as tracking_policy, _ref


def _run(frames, initial):
    detections = _detections(len(frames))
    refs = tuple(
        tuple(
            replace(
                n.candidate_ref,
                trajectory_support=1.0,
                cluster_support=1.0,
                representation_support=1.0,
            )
            for n in nodes
        )
        for nodes in frames
    )
    pairs = tuple(
        build_interface_layers(
            d,
            r,
            hard_unavailable=False,
            minimum_confidence=0.4,
            state_min_evidence=0.58,
        )
        for d, r in zip(detections, refs, strict=True)
    )
    phase = OilMaterialPhaseLifecycleOwner(
        _policy(confirmed_initial_state=initial)
    ).resolve(
        tuple(p[0] for p in pairs),
        identity_contradictions=tuple(
            frozenset(
                r.tracklet_id
                for r in group
                if r.identity_contradiction
                is OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER
            )
            for group in refs
        ),
    )
    path = BoundedOilInterfaceSelector(_selector_policy()).resolve(
        tuple(p[1] for p in pairs),
        detections,
        initial,
        phase.allowed_tracklet_ids,
        phase.owner_chains,
    )
    return phase, path, refs


def _slow(ys=None, anchors=(0, 8), owner_change=None):
    ys = ys or tuple(65 + i * 0.3 for i in range(20))
    return tuple(
        (
            _node(
                i,
                "slow" if owner_change is None or i < owner_change else "different",
                y,
                direction=1,
                progress=2,
                authority=Authority.ANCHOR_ELIGIBLE
                if i in anchors
                else Authority.CONTINUATION_ELIGIBLE,
                phase_identity=Identity.DIRECT_INTERFACE
                if i in anchors
                else Identity.CONTINUATION_ONLY,
            ),
        )
        for i, y in enumerate(ys)
    )


def test_reaffirmed_slow_owner_releases_without_changing_direct_threshold_or_provenance():
    phase, path, refs = _run(_slow(), InitialObservationState.FULL_NO_INTERFACE)
    assert phase.phases[16] is OilMaterialPhase.FILLED_BARRIER
    assert phase.phases[17] is OilMaterialPhase.DRAINING
    assert phase.diagnostics[17]["release_source"] == "recovery"
    assert (
        phase.diagnostics[17]["release_evaluations"][0]["first_failed_predicate"]
        == "minimum_progress"
    )
    assert path[17].candidate_ref is refs[17][0]
    assert path[17].y == refs[17][0].candidate.y
    chain = phase.diagnostics[16]["recovery_active_chains"][0]
    assert chain["lease_renewal_used"] is True
    assert chain["lease_expiry_frame"] == 20


@pytest.mark.parametrize(
    "frames",
    [
        _slow(anchors=(0,)),
        _slow(anchors=(0, 11)),
        _slow(ys=(65.0,) * 20),
        _slow(ys=tuple(65 + 0.3 * (i % 2) for i in range(20))),
        _slow(ys=(65.0,) * 11 + (72.0,) * 9, anchors=(0, 11)),
        _slow(anchors=(0, 8), owner_change=7),
        _slow(anchors=(0, 7, 8, 9, 10), owner_change=7),
        _slow(anchors=(0, 8, 9), owner_change=9),
    ],
)
def test_renewal_does_not_rescue_unreaffirmed_static_oscillating_late_or_cross_owner_evidence(
    frames,
):
    phase, path, _ = _run(frames, InitialObservationState.FULL_NO_INTERFACE)
    assert OilMaterialPhase.DRAINING not in phase.phases
    assert all(n.kind != "oil" for n in path)


def test_repeated_anchors_do_not_extend_lease_past_total_horizon():
    phase, _, _ = _run(
        _slow(ys=tuple(65 + i * 0.1 for i in range(23)), anchors=tuple(range(23))),
        InitialObservationState.FULL_NO_INTERFACE,
    )
    assert OilMaterialPhase.DRAINING not in phase.phases
    assert phase.diagnostics[21]["recovery_reset_reason"] == "evidence_window_expired"


def _delayed():
    frames = [
        (
            _node(
                i,
                "fill",
                y,
                direction=-1,
                progress=25,
                motion_support=0.9,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
        )
        for i, y in enumerate((180, 150))
    ]
    frames += [()] * 6
    frames += [
        (
            _node(
                8,
                "delayed",
                90,
                direction=1,
                progress=2,
                phase_identity=Identity.ORDERED_LOWER_INTERFACE,
            ),
        ),
        (
            _node(
                9,
                "delayed",
                92,
                direction=1,
                progress=2,
                authority=Authority.CONTINUATION_ELIGIBLE,
            ),
        ),
        (),
        (
            _node(
                11,
                "delayed",
                110,
                direction=1,
                progress=2,
                authority=Authority.CONTINUATION_ELIGIBLE,
            ),
        ),
    ]
    return frames


def test_sparse_weak_continuation_without_contradiction_keeps_delayed_evidence():
    phase, path, refs = _run(_delayed(), InitialObservationState.EMPTY_NO_INTERFACE)
    assert phase.phases[11] is OilMaterialPhase.DRAINING
    assert path[11].candidate_ref is refs[11][0]


@pytest.mark.parametrize("unadmitted", [False, True])
def test_same_owner_identity_contradiction_resets_even_if_not_publishable(unadmitted):
    frames = _delayed()
    node = frames[9][0]
    contradiction = replace(
        node,
        candidate_ref=replace(
            node.candidate_ref,
            identity_contradiction=OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER,
            tracklet_admitted=not unadmitted,
        ),
    )
    # A stronger clean member in the same row cannot hide its sibling's contradiction.
    clean = replace(node, candidate_ref=replace(node.candidate_ref, candidate_offset=1))
    frames[9] = (clean, contradiction)
    phase, path, _ = _run(frames, InitialObservationState.EMPTY_NO_INTERFACE)
    assert (
        phase.diagnostics[9]["delayed_reacquisition_reset_reason"]
        == "identity_contradiction"
    )
    assert phase.diagnostics[9]["delayed_reacquisition_active_chains"] == []
    assert phase.phases[11] is OilMaterialPhase.OPEN
    assert path[11].kind != "oil"
    assert phase.diagnostics[11]["ownerless_barrier_attempt_consumed"] is True


def test_actual_authority_demotion_survives_physical_tracklet_assignment():
    glass = SimpleNamespace(detector_settings=SimpleNamespace(temporal_max_jump_px=32))
    frames = []
    for frame in range(5):
        far = replace(
            _ref(
                frame,
                0,
                140 + frame,
                authority=Authority.ANCHOR_ELIGIBLE,
                source="material_path",
                ordered_lower=True,
            ),
            phase_identity=Identity.ORDERED_LOWER_INTERFACE,
        )
        candidates = [far]
        if frame >= 3:
            candidates.append(
                replace(
                    _ref(
                        frame,
                        1,
                        100,
                        authority=Authority.ANCHOR_ELIGIBLE,
                        source="near",
                        ordered_lower=True,
                    ),
                    phase_identity=Identity.ORDERED_LOWER_INTERFACE,
                )
            )
        frames.append(
            tuple(_demote_non_nearest_ordered_lower_anchors(candidates, glass))
        )
    result = DirectedInterfaceTrackletBuilder(tracking_policy()).resolve(tuple(frames))
    far_refs = [
        next(r for r in group if r.candidate.source == "material_path")
        for group in result.refs_by_frame
    ]
    assert len({r.tracklet_id for r in far_refs}) == 1
    assert far_refs[2].identity_contradiction is OilIdentityContradiction.NONE
    assert (
        far_refs[3].identity_contradiction
        is OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER
    )
    assert far_refs[3].phase_identity is Identity.CONTINUATION_ONLY


def test_completed_frame_decisions_are_frozen_and_do_not_alias_final_runtime():
    from dataclasses import FrozenInstanceError

    phase, _, _ = _run(_slow(), InitialObservationState.FULL_NO_INTERFACE)
    assert phase.frame_decisions[0].phase is OilMaterialPhase.FILLED_BARRIER
    assert phase.frame_decisions[17].phase is OilMaterialPhase.DRAINING
    with pytest.raises(FrozenInstanceError):
        phase.frame_decisions[0].reason = "mutated"
    assert phase.diagnostics[0]["release_source"] == "none"
    assert phase.diagnostics[17]["release_source"] == "recovery"
