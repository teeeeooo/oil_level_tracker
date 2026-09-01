from __future__ import annotations

from types import SimpleNamespace

from oil_tracker.adapters.vision.oil_candidate_authority import (
    OilCandidateAuthority,
)
from oil_tracker.adapters.vision.oil_candidate_evidence import (
    OilCandidateEvidence,
)
from oil_tracker.adapters.vision.oil_interface_selector import (
    BoundedOilInterfaceSelector,
    OilInterfaceSelectorPolicy,
)
from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilFillConfirmationProfile,
    OilMaterialPhase,
    OilMaterialPhaseLifecycleOwner,
    OilMaterialPhasePolicy,
)
from oil_tracker.adapters.vision.oil_phase_identity import OilPhaseIdentity
from oil_tracker.adapters.vision.oil_sequence_types import (
    OilCandidateRef,
    OilSequenceNode,
    TrackletConfirmationProfile,
    TrackletLifecycle,
)
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import (
    BoundaryKind,
    FillState,
    InitialObservationState,
)


def _policy(
    *,
    confirmed_initial_state: InitialObservationState | None = None,
) -> OilMaterialPhasePolicy:
    return OilMaterialPhasePolicy(
        geometry_top_y=0.0,
        geometry_height=200.0,
        maximum_jump_px=32.0,
        maximum_lost_frames=2,
        handoff_ambiguity_margin=0.08,
        handoff_direction_reversal_tolerance_px=3.0,
        fill_onset_intent_frames=6,
        fill_evidence_window_frames=10,
        entrance_band_ratio=0.27,
        fill_minimum_span_ratio=0.20,
        minimum_directional_agreement=0.60,
        confirmed_initial_state=confirmed_initial_state,
        fill_minimum_motion_support=0.50,
        fill_minimum_motion_coverage=0.50,
        drain_entrance_ratio=0.40,
        drain_minimum_progress_ratio=0.025,
        drain_minimum_directional_agreement=0.60,
        material_conflict_limit=0.45,
    )


def _node(
    frame: int,
    tracklet: str,
    y: float,
    *,
    direction: int,
    progress: float,
    material_conflict: float = 0.0,
    tracklet_material_conflict: float | None = None,
    lifecycle: TrackletLifecycle = TrackletLifecycle.CONTINUING,
    emission: float = 0.8,
    authority: OilCandidateAuthority = OilCandidateAuthority.ANCHOR_ELIGIBLE,
    confirmation_profile: TrackletConfirmationProfile = (
        TrackletConfirmationProfile.ANCHOR_TRAJECTORY
    ),
    motion_support: float = 0.0,
    motion_coverage: float = 0.0,
    material_path: bool = False,
    candidate_offset: int = 0,
    row_hypothesis_id: str | None = None,
    tracklet_incompatible: bool = False,
    phase_identity: OilPhaseIdentity = OilPhaseIdentity.CONTINUATION_ONLY,
) -> OilSequenceNode:
    candidate = BoundaryCandidate(
        source=f"source-{tracklet}",
        kind=BoundaryKind.OIL_AIR,
        y=y,
        features={
            "boundary_likelihood": 0.8,
            "artifact_likelihood": 0.05,
            "ambiguity_likelihood": 0.10,
            "broad_strength": 0.8,
            "narrow_peak_strength": 0.8,
            "narrow_horizontal_coverage": 0.8,
            "broad_scale_consistency": 0.8,
            "polarity_confidence": 0.8,
            "material_texture_conflict": material_conflict,
            "material_path": float(material_path),
        },
        penalties={"material_texture_conflict": material_conflict},
        feature_score=0.8,
        final_score=0.8,
    )
    ref = OilCandidateRef(
        frame_offset=frame,
        candidate_offset=candidate_offset,
        candidate=candidate,
        evidence=OilCandidateEvidence.from_candidate(candidate),
        local_quality=0.8,
        authority=authority,
        initial_authority=authority,
        post_track_authority=authority,
        tracklet_id=tracklet,
        row_hypothesis_id=(
            f"row-{frame}-{tracklet}"
            if row_hypothesis_id is None
            else row_hypothesis_id
        ),
        tracklet_lifecycle=lifecycle,
        tracklet_admitted=True,
        tracklet_confirmation_profile=confirmation_profile,
        tracklet_net_progress_px=progress,
        tracklet_direction=direction,
        tracklet_directional_agreement=1.0,
        tracklet_motion_support=motion_support,
        tracklet_motion_coverage=motion_coverage,
        tracklet_material_conflict=(
            material_conflict
            if tracklet_material_conflict is None
            else tracklet_material_conflict
        ),
        tracklet_incompatible=tracklet_incompatible,
        phase_identity=phase_identity,
    )
    return OilSequenceNode(
        "oil",
        emission,
        f"oil-{frame}-{tracklet}-{candidate_offset}-{y}",
        ref,
    )


def _material_veto_row(
    frame: int,
    tracklet: str,
    y: float,
) -> tuple[OilSequenceNode, OilSequenceNode]:
    return (
        _node(
            frame,
            tracklet,
            y,
            direction=1,
            progress=20.0,
            material_conflict=0.10,
            emission=0.90,
        ),
        _node(
            frame,
            tracklet,
            y + 1.0,
            direction=1,
            progress=20.0,
            material_conflict=0.80,
            material_path=True,
            candidate_offset=1,
            emission=0.70,
        ),
    )


def _unknown(frame: int) -> OilSequenceNode:
    return OilSequenceNode("unknown", 0.1, f"unknown-{frame}")


def _detections(count: int) -> tuple[PhaseDetection, ...]:
    return tuple(
        PhaseDetection(
            glass_id="glass",
            frame_index=frame,
            time_sec=frame * 0.5,
            fill_state=FillState.UNKNOWN_REVIEW,
        )
        for frame in range(count)
    )


def _selector_policy() -> OilInterfaceSelectorPolicy:
    return OilInterfaceSelectorPolicy(
        geometry_top_y=0.0,
        geometry_height=200.0,
        maximum_jump_px=32.0,
        lookahead_frames=6,
        ambiguity_margin=0.08,
        unknown_transition_cost=0.20,
        incompatible_state_transition_cost=2.5,
        state_min_evidence=0.58,
        entrance_band_ratio=0.27,
    )


def _resolve(
    layers: tuple[tuple[OilSequenceNode, ...], ...],
    *,
    confirmed_initial_state: InitialObservationState | None = None,
):
    path = tuple(
        next((node for node in layer if node.kind == "oil"), layer[-1])
        for layer in layers
    )
    phase = OilMaterialPhaseLifecycleOwner(
        _policy(
            confirmed_initial_state=confirmed_initial_state,
        )
    ).resolve(layers)
    selected = tuple(
        original
        if allowed is None
        else (
            next(
                (
                    node
                    for node in layer
                    if node.kind == "oil"
                    and node.candidate_ref is not None
                    and node.candidate_ref.tracklet_id in allowed
                ),
                _unknown(frame),
            )
            if allowed
            else _unknown(frame)
        )
        for frame, (original, layer, allowed) in enumerate(
            zip(path, layers, phase.allowed_tracklet_ids, strict=True)
        )
    )
    return SimpleNamespace(**phase.__dict__, path=selected)


def test_two_confirmed_tracklets_form_a_phase_only_fill_chain() -> None:
    a0 = _node(0, "a", 180.0, direction=-1, progress=20.0)
    a1 = _node(1, "a", 150.0, direction=-1, progress=20.0)
    b2 = _node(2, "b", 130.0, direction=-1, progress=20.0)
    b3 = _node(3, "b", 95.0, direction=-1, progress=20.0)
    b4 = _node(4, "b", 50.0, direction=-1, progress=20.0)
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate((a0, a1, b2, b3, b4))
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1] is b4
    assert result.owner_chains[-1] == ("a", "b")
    assert result.reasons[2] == "FILL_EVIDENCE_ACCUMULATING"
    assert result.reasons[-1] == "FILL_SPAN_CONFIRMED"
    assert (
        result.fill_confirmation_profiles[-1]
        is OilFillConfirmationProfile.UNKNOWN_FILL_ANCHORED
    )
    assert result.path[:4] == tuple(layer[0] for layer in layers[:4])


def test_ambiguous_fill_successor_resets_instead_of_picking_a_branch() -> None:
    layers = (
        (_node(0, "a", 180.0, direction=-1, progress=20.0), _unknown(0)),
        (
            _node(1, "b", 160.0, direction=-1, progress=20.0),
            _node(1, "c", 162.0, direction=-1, progress=20.0),
            _unknown(1),
        ),
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.OPEN
    assert result.reasons[-1] == "FILL_CHAIN_AMBIGUOUS"
    assert result.allowed_tracklet_ids[-1] is None
    assert result.ambiguous_frames == frozenset({1})


def test_distant_fill_tracklet_does_not_inherit_phase_progress() -> None:
    layers = (
        (_node(0, "a", 180.0, direction=-1, progress=30.0), _unknown(0)),
        (_node(1, "b", 50.0, direction=-1, progress=5.0), _unknown(1)),
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.OPEN
    # The unmatched predecessor remains a separate bounded phase hypothesis;
    # no physical identity or extrema are inherited by b. Neither chain has
    # dynamic-fill proof, so ordinary OPEN selection remains unconstrained.
    assert result.owner_chains[-1] == ()
    assert result.allowed_tracklet_ids[-1] is None
    assert result.reasons[-1] == "FILL_EVIDENCE_ACCUMULATING"
    assert result.path[-1].kind == "oil"


def test_zero_strong_singleton_accumulates_without_constraining_selector() -> None:
    owner = _node(0, "upward-owner", 180.0, direction=-1, progress=20.0)
    competing = _node(
        0,
        "downward-competitor",
        80.0,
        direction=1,
        progress=30.0,
        emission=4.0,
    )
    layer = (competing, owner, _unknown(0))

    phase = OilMaterialPhaseLifecycleOwner(_policy()).resolve((layer,))
    selected = BoundedOilInterfaceSelector(_selector_policy()).resolve(
        (layer,),
        _detections(1),
        None,
        phase.allowed_tracklet_ids,
        phase.owner_chains,
    )

    assert phase.phases == (OilMaterialPhase.OPEN,)
    assert phase.allowed_tracklet_ids == (None,)
    assert phase.reasons == ("FILL_EVIDENCE_ACCUMULATING",)
    assert selected[0].candidate_ref is competing.candidate_ref


def test_unique_dynamic_fill_owner_ignores_weak_anchor_competitor() -> None:
    weak = _node(
        0,
        "weak-upward",
        120.0,
        direction=-1,
        progress=30.0,
        emission=4.0,
        motion_support=0.30,
        motion_coverage=0.40,
    )
    strong = _node(
        0,
        "strong-upward",
        100.0,
        direction=-1,
        progress=30.0,
        emission=1.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    layer = (weak, strong, _unknown(0))

    result = _resolve((layer,))

    assert result.allowed_tracklet_ids == (
        frozenset({"strong-upward"}),
    )
    assert result.reasons == ("FILL_MOTION_OWNER",)
    assert result.path[0].candidate_ref is strong.candidate_ref


def test_current_material_anchor_handoff_does_not_mutate_fill_phase_owner() -> None:
    owner0 = _node(
        0,
        "fill-owner",
        130.0,
        direction=-1,
        progress=20.0,
        motion_support=0.8,
        motion_coverage=0.8,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    owner1 = _node(
        1,
        "fill-owner",
        110.0,
        direction=-1,
        progress=20.0,
        motion_support=0.8,
        motion_coverage=0.8,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    current_anchor = _node(
        3,
        "current-anchor",
        60.0,
        direction=1,
        progress=18.0,
        material_conflict=1.0,
        tracklet_material_conflict=0.65,
        motion_support=0.9,
        motion_coverage=0.8,
        material_path=True,
        confirmation_profile=TrackletConfirmationProfile.ANCHOR_CORRIDOR,
    )
    layers = (
        (owner0, _unknown(0)),
        (owner1, _unknown(1)),
        (_unknown(2),),
        (current_anchor, _unknown(3)),
        (_unknown(4),),
    )

    result = _resolve(layers)

    assert result.phases[3] is OilMaterialPhase.FILLING
    assert result.reasons[3] == "FILL_CURRENT_ANCHOR_HANDOFF"
    assert result.allowed_tracklet_ids[3] == frozenset({"current-anchor"})
    assert result.owner_chains[3] == ("fill-owner", "current-anchor")
    assert result.path[3].candidate_ref is current_anchor.candidate_ref
    assert "current-anchor" not in result.owner_chains[4]


def test_dynamic_fill_links_unique_immediate_predecessor_without_extrema() -> None:
    predecessor = (
        _node(0, "visible-interface", 89.0, direction=1, progress=2.0),
        _node(1, "visible-interface", 87.0, direction=1, progress=2.0),
    )
    unrelated = _node(
        1,
        "unrelated-upper",
        30.0,
        direction=1,
        progress=8.0,
        emission=4.0,
    )
    dynamic = _node(
        2,
        "dynamic-fill",
        100.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    layers = (
        (predecessor[0], _unknown(0)),
        (unrelated, predecessor[1], _unknown(1)),
        (dynamic, _unknown(2)),
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)
    selected = BoundedOilInterfaceSelector(_selector_policy()).resolve(
        layers,
        _detections(len(layers)),
        None,
        result.allowed_tracklet_ids,
        result.owner_chains,
    )

    assert result.phases == (
        OilMaterialPhase.OPEN,
        OilMaterialPhase.OPEN,
        OilMaterialPhase.FILLING,
    )
    assert result.allowed_tracklet_ids == (
        frozenset({"visible-interface"}),
        frozenset({"visible-interface"}),
        frozenset({"dynamic-fill"}),
    )
    assert result.reasons[:2] == (
        "FILL_ONSET_INTENT_PREDECESSOR",
        "FILL_ONSET_INTENT_PREDECESSOR",
    )
    assert result.owner_chains == (
        ("visible-interface", "dynamic-fill"),
        ("visible-interface", "dynamic-fill"),
        ("visible-interface", "dynamic-fill"),
    )
    assert tuple(
        node.candidate_ref.tracklet_id
        for node in selected
        if node.candidate_ref is not None
    ) == (
        "visible-interface",
        "visible-interface",
        "dynamic-fill",
    )
    # The predecessor contributes identity continuity only.  Its 89px origin
    # must not help a one-observation dynamic chain satisfy fill-span geometry.
    assert OilMaterialPhase.FILLED_BARRIER not in result.phases


def test_dynamic_fill_activation_reuses_same_physical_predecessor() -> None:
    weak = _node(
        0,
        "dynamic-fill",
        105.0,
        direction=-1,
        progress=30.0,
        motion_support=0.30,
        motion_coverage=0.40,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    strong = _node(
        1,
        "dynamic-fill",
        100.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    layers = ((weak, _unknown(0)), (strong, _unknown(1)))

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)

    assert result.allowed_tracklet_ids == (
        frozenset({"dynamic-fill"}),
        frozenset({"dynamic-fill"}),
    )
    assert result.reasons[0] == "FILL_ONSET_INTENT_PREDECESSOR"
    assert result.owner_chains == (
        ("dynamic-fill",),
        ("dynamic-fill",),
    )


def test_dynamic_fill_ambiguous_predecessor_censors_only_onset_intent() -> None:
    dynamic = _node(
        2,
        "dynamic-fill",
        100.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    layers = (
        (_unknown(0),),
        (
            _node(1, "candidate-a", 85.0, direction=1, progress=2.0),
            _node(1, "candidate-b", 87.0, direction=1, progress=2.0),
            _unknown(1),
        ),
        (dynamic, _unknown(2)),
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)
    selected = BoundedOilInterfaceSelector(_selector_policy()).resolve(
        layers,
        _detections(len(layers)),
        None,
        result.allowed_tracklet_ids,
        result.owner_chains,
    )

    assert result.allowed_tracklet_ids[0] is None
    assert result.allowed_tracklet_ids[1] == frozenset()
    assert result.reasons[1] == "FILL_ONSET_INTENT_AMBIGUOUS"
    assert result.owner_chains[1:] == (
        ("dynamic-fill",),
        ("dynamic-fill",),
    )
    assert 1 in result.ambiguous_frames
    assert selected[1].kind == "unknown"


def test_dynamic_fill_without_compatible_predecessor_censors_prior_frame() -> None:
    distant = _node(0, "distant", 30.0, direction=1, progress=2.0)
    dynamic = _node(
        1,
        "dynamic-fill",
        100.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )

    layers = ((distant, _unknown(0)), (dynamic, _unknown(1)))
    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)
    selected = BoundedOilInterfaceSelector(_selector_policy()).resolve(
        layers,
        _detections(len(layers)),
        None,
        result.allowed_tracklet_ids,
        result.owner_chains,
    )

    assert result.allowed_tracklet_ids == (
        frozenset(),
        frozenset({"dynamic-fill"}),
    )
    assert result.reasons[0] == "FILL_ONSET_INTENT_NO_PREDECESSOR"
    assert result.owner_chains == (
        ("dynamic-fill",),
        ("dynamic-fill",),
    )
    assert selected[0].kind == "unknown"


def test_open_interface_without_future_fill_remains_unconstrained() -> None:
    layers = tuple(
        (
            _node(
                frame,
                "visible-interface",
                90.0 + frame,
                direction=1,
                progress=2.0,
            ),
            _unknown(frame),
        )
        for frame in range(4)
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)

    assert result.phases == (OilMaterialPhase.OPEN,) * 4
    assert result.allowed_tracklet_ids == (None,) * 4
    assert all("ONSET_INTENT" not in reason for reason in result.reasons)


def test_initial_drain_motion_does_not_create_fill_onset_intent() -> None:
    drain = tuple(
        _node(
            frame,
            "initial-drain",
            90.0 + 10.0 * frame,
            direction=1,
            progress=30.0,
            motion_support=0.90,
            motion_coverage=0.80,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        )
        for frame in range(3)
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(drain))
    )

    assert result.phases == (OilMaterialPhase.OPEN,) * 3
    assert result.allowed_tracklet_ids == (None,) * 3
    assert all("ONSET_INTENT" not in reason for reason in result.reasons)


def test_fill_onset_intent_cannot_rewrite_past_fixed_lag_boundary() -> None:
    target = 6
    stable = tuple(
        (
            _node(
                frame,
                "stable-interface",
                30.0,
                direction=1,
                progress=2.0,
            ),
            _unknown(frame),
        )
        for frame in range(13)
    )
    dynamic = _node(
        13,
        "late-dynamic-fill",
        100.0,
        direction=-1,
        progress=30.0,
        motion_support=0.90,
        motion_coverage=0.80,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    owner = OilMaterialPhaseLifecycleOwner(_policy())

    prefix = owner.resolve(stable[: target + 1])
    extended = owner.resolve(stable + ((dynamic, _unknown(13)),))

    assert extended.phases[target] is prefix.phases[target]
    assert extended.reasons[target] == prefix.reasons[target]
    assert extended.owner_chains[target] == prefix.owner_chains[target]
    assert (
        extended.allowed_tracklet_ids[target]
        == prefix.allowed_tracklet_ids[target]
    )


def test_current_strong_anchor_interface_blocks_dynamic_fill_activation() -> None:
    dynamic = _node(
        0,
        "dynamic-fill",
        90.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    established = _node(
        0,
        "established-interface",
        130.0,
        direction=-1,
        progress=8.0,
        motion_support=0.90,
        motion_coverage=0.80,
        confirmation_profile=TrackletConfirmationProfile.ANCHOR_CORRIDOR,
    )

    result = _resolve(((dynamic, established, _unknown(0)),))

    assert result.phases == (OilMaterialPhase.OPEN,)
    assert result.allowed_tracklet_ids == (None,)
    assert result.reasons == ("FILL_ESTABLISHED_INTERFACE",)


def test_retained_strong_anchor_interface_blocks_dynamic_fill_activation() -> None:
    established = _node(
        0,
        "retained-interface",
        130.0,
        direction=-1,
        progress=8.0,
        motion_support=0.90,
        motion_coverage=0.80,
        confirmation_profile=TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
    )
    dynamic = _node(
        1,
        "dynamic-fill",
        90.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    layers = (
        (established, _unknown(0)),
        (dynamic, _unknown(1)),
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.OPEN
    assert result.allowed_tracklet_ids[-1] is None
    assert result.reasons[-1] == "FILL_ESTABLISHED_INTERFACE"


def test_zero_strong_multiple_chains_accumulate_without_constraint() -> None:
    first = _node(
        0,
        "first-weak",
        150.0,
        direction=-1,
        progress=30.0,
        motion_support=0.30,
        motion_coverage=0.40,
    )
    second = _node(
        0,
        "second-weak",
        170.0,
        direction=-1,
        progress=30.0,
        motion_support=0.45,
        motion_coverage=0.40,
    )

    result = _resolve(((first, second, _unknown(0)),))

    assert result.phases == (OilMaterialPhase.OPEN,)
    assert result.allowed_tracklet_ids == (None,)
    assert result.reasons == ("FILL_EVIDENCE_ACCUMULATING",)
    assert result.path[0].candidate_ref is first.candidate_ref
    assert result.ambiguous_frames == frozenset()


def test_two_strong_motion_fill_chains_remain_ambiguous() -> None:
    first = _node(
        0,
        "first-strong",
        90.0,
        direction=-1,
        progress=30.0,
        motion_support=0.80,
        motion_coverage=0.70,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )
    second = _node(
        0,
        "second-strong",
        110.0,
        direction=-1,
        progress=30.0,
        motion_support=0.75,
        motion_coverage=0.80,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )

    result = _resolve(((first, second, _unknown(0)),))

    assert result.allowed_tracklet_ids == (frozenset(),)
    assert result.reasons == ("FILL_OWNER_AMBIGUOUS",)
    assert result.path[0].kind == "unknown"
    assert result.ambiguous_frames == frozenset({0})


def test_strong_anchor_profile_does_not_activate_speculative_fill() -> None:
    stationary = _node(
        0,
        "stationary-anchor",
        100.0,
        direction=-1,
        progress=18.0,
        motion_support=0.95,
        motion_coverage=0.90,
        confirmation_profile=TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
    )

    result = _resolve(((stationary, _unknown(0)),))

    assert result.phases == (OilMaterialPhase.OPEN,)
    assert result.allowed_tracklet_ids == (None,)
    assert result.reasons == ("FILL_ESTABLISHED_INTERFACE",)


def test_unknown_motion_track_outside_central_corridor_does_not_activate_fill() -> None:
    lower = _node(
        0,
        "lower-motion",
        180.0,
        direction=-1,
        progress=18.0,
        motion_support=0.95,
        motion_coverage=0.90,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )

    result = _resolve(((lower, _unknown(0)),))

    assert result.phases == (OilMaterialPhase.OPEN,)
    assert result.allowed_tracklet_ids == (None,)


def test_unknown_motion_track_on_central_boundary_activates_fill() -> None:
    boundary = _node(
        0,
        "central-boundary",
        54.0,
        direction=-1,
        progress=18.0,
        motion_support=0.95,
        motion_coverage=0.90,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )

    result = _resolve(((boundary, _unknown(0)),))

    assert result.phases == (OilMaterialPhase.FILLING,)
    assert result.allowed_tracklet_ids == (
        frozenset({"central-boundary"}),
    )


def test_confirmed_empty_lower_entrance_motion_activates_fill() -> None:
    entrance = _node(
        0,
        "empty-entrance",
        180.0,
        direction=-1,
        progress=18.0,
        motion_support=0.95,
        motion_coverage=0.90,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )

    result = _resolve(
        ((entrance, _unknown(0)),),
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases == (OilMaterialPhase.FILLING,)
    assert result.allowed_tracklet_ids == (
        frozenset({"empty-entrance"}),
    )


def test_established_slow_empty_fill_reenters_with_distinct_physical_id() -> None:
    layers = (
        (
            _node(
                0,
                "fill-a",
                180.0,
                direction=-1,
                progress=30.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(0),
        ),
        (
            _node(
                1,
                "fill-a",
                165.0,
                direction=-1,
                progress=30.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(1),
        ),
        (
            _node(
                2,
                "fill-a",
                150.0,
                direction=-1,
                progress=30.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(2),
        ),
        *((_unknown(frame),) for frame in range(3, 8)),
        (
            _node(
                8,
                "fill-b",
                140.0,
                direction=-1,
                progress=20.0,
                motion_support=0.85,
                motion_coverage=0.80,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(8),
        ),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[8] is OilMaterialPhase.FILLING
    assert result.reasons[8] == "FILL_PHASE_REENTRY"
    assert result.allowed_tracklet_ids[8] == frozenset({"fill-b"})
    assert result.owner_chains[8] == ("fill-a", "fill-b")


def test_established_partial_fill_reverses_into_unique_drain_owner() -> None:
    layers = (
        (
            _node(
                0,
                "fill-a",
                180.0,
                direction=-1,
                progress=25.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(0),
        ),
        (
            _node(
                1,
                "fill-a",
                155.0,
                direction=-1,
                progress=25.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(1),
        ),
        *((_unknown(frame),) for frame in range(2, 7)),
        (
            _node(
                7,
                "reversed",
                170.0,
                direction=1,
                progress=20.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _node(
                7,
                "distant",
                80.0,
                direction=-1,
                progress=20.0,
                motion_support=0.90,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(7),
        ),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[7] is OilMaterialPhase.DRAINING
    assert result.allowed_tracklet_ids[7] == frozenset({"reversed"})
    assert result.owner_chains[7] == ("fill-a", "reversed")
    assert result.reasons[7] == "PARTIAL_FILL_DRAIN_RELEASE_CONFIRMED"
    diagnostic = result.diagnostics[7]
    assert diagnostic["established_fill_present"] is True
    assert diagnostic["established_fill_last_y"] == 155.0
    assert diagnostic["release_stage"] == "partial_fill_drain_release"
    assert diagnostic["release_selected_tracklet_id"] == "reversed"
    reversed_evaluation = next(
        item
        for item in diagnostic["release_evaluations"]
        if item["tracklet_id"] == "reversed"
    )
    assert reversed_evaluation["passed"] is True
    assert reversed_evaluation["first_failed_predicate"] is None


def test_initial_empty_downward_tracklet_cannot_start_without_fill_owner() -> None:
    downward = _node(
        0,
        "downward",
        170.0,
        direction=1,
        progress=20.0,
        motion_support=0.90,
        motion_coverage=0.85,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
    )

    result = _resolve(
        ((downward, _unknown(0)),),
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases == (OilMaterialPhase.OPEN,)
    assert result.allowed_tracklet_ids == (frozenset(),)
    assert result.path[0].kind == "unknown"


def test_partial_fill_drain_release_rejects_distant_or_material_opposed_rows() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=30.0,
            motion_support=0.90,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=30.0,
            motion_support=0.90,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    distant = _node(5, "distant", 90.0, direction=1, progress=30.0)
    opposed = _node(
        6,
        "opposed",
        165.0,
        direction=1,
        progress=30.0,
        material_conflict=0.80,
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(fill)
    ) + tuple((_unknown(frame),) for frame in range(2, 5)) + (
        (distant, _unknown(5)),
        (opposed, _unknown(6)),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[5:] == (
        OilMaterialPhase.OPEN,
        OilMaterialPhase.OPEN,
    )
    assert result.allowed_tracklet_ids[5:] == (
        frozenset(),
        frozenset(),
    )
    distant_evaluation = next(
        item
        for item in result.diagnostics[5]["release_evaluations"]
        if item["tracklet_id"] == "distant"
    )
    opposed_evaluation = next(
        item
        for item in result.diagnostics[6]["release_evaluations"]
        if item["tracklet_id"] == "opposed"
    )
    assert (
        distant_evaluation["first_failed_predicate"]
        == "reversal_lower_bound"
    )
    assert (
        opposed_evaluation["first_failed_predicate"]
        == "tracklet_material_conflict"
    )


def test_ambiguous_partial_fill_drain_release_stays_unknown() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=30.0,
            motion_support=0.90,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=30.0,
            motion_support=0.90,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(fill)
    ) + tuple((_unknown(frame),) for frame in range(2, 5)) + (
        (
            _node(5, "drain-a", 162.0, direction=1, progress=25.0),
            _node(5, "drain-b", 164.0, direction=1, progress=25.0),
            _unknown(5),
        ),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[-1] is OilMaterialPhase.OPEN
    assert result.reasons[-1] == "PARTIAL_FILL_DRAIN_RELEASE_AMBIGUOUS"
    assert result.allowed_tracklet_ids[-1] == frozenset()
    assert result.owner_chains[-1] == ("fill",)
    assert result.diagnostics[-1]["release_ambiguous"] is True
    assert result.diagnostics[-1]["release_qualifying_tracklet_ids"] == [
        "drain-a",
        "drain-b",
    ]


def test_confirmed_full_starts_behind_fail_closed_material_barrier() -> None:
    stationary = _node(
        0,
        "stationary",
        55.0,
        direction=1,
        progress=2.0,
    )

    result = _resolve(
        ((stationary, _unknown(0)),),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases == (OilMaterialPhase.FILLED_BARRIER,)
    assert result.reasons == ("INITIAL_FULL_BARRIER",)
    assert result.allowed_tracklet_ids == (frozenset(),)
    assert result.path[0].kind == "unknown"


def test_initial_full_drain_diagnostic_records_first_failed_predicate() -> None:
    missed_entrance = _node(
        0,
        "missed-entrance",
        130.0,
        direction=1,
        progress=30.0,
    )

    result = _resolve(
        ((missed_entrance, _unknown(0)),),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    diagnostic = result.diagnostics[0]
    evaluation = diagnostic["release_evaluations"][0]
    assert diagnostic["release_stage"] == "initial_full_drain_release"
    assert diagnostic["allowed_mode"] == "hard_gate"
    assert evaluation["entrance_relative"] == 0.65
    assert evaluation["first_failed_predicate"] == "entrance_relative"
    assert evaluation["predicates"]["minimum_progress"] is True


def test_confirmed_full_releases_unique_downward_top_origin_owner() -> None:
    drain = _node(
        0,
        "drain",
        65.0,
        direction=1,
        progress=20.0,
        material_conflict=0.10,
    )

    result = _resolve(
        ((drain, _unknown(0)),),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases == (OilMaterialPhase.DRAINING,)
    assert result.reasons == ("DRAIN_RELEASE_CONFIRMED",)
    assert result.allowed_tracklet_ids == (frozenset({"drain"}),)
    assert result.owner_chains == (("drain",),)
    assert result.path[0].candidate_ref is drain.candidate_ref


def test_initial_full_fragmented_release_chain_uses_unique_current_row() -> None:
    rows = (
        _node(0, "drain-a", 65.0, direction=1, progress=2.0),
        _node(
            1,
            "drain-a",
            68.0,
            direction=1,
            progress=2.0,
            authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        ),
        _node(2, "drain-b", 72.0, direction=1, progress=2.0),
        _node(3, "drain-c", 92.0, direction=1, progress=2.0),
    )
    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(rows)),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases[:2] == (
        OilMaterialPhase.FILLED_BARRIER,
        OilMaterialPhase.FILLED_BARRIER,
    )
    assert result.phases[2] is OilMaterialPhase.DRAINING
    assert result.reasons[2] == "DRAIN_RELEASE_RECOVERY_CONFIRMED"
    assert result.allowed_tracklet_ids[2] == frozenset({"drain-b"})
    assert result.owner_chains[2] == ("drain-a", "drain-b")
    assert result.path[2].candidate_ref is rows[2].candidate_ref
    diagnostic = result.diagnostics[2]
    assert diagnostic["schema_version"] == "r20-delayed-drain-reacquisition-v1"
    assert diagnostic["release_source"] == "recovery"
    assert diagnostic["recovery_selected_tracklet_id"] == "drain-b"
    assert diagnostic["recovery_qualifying_tracklet_ids"] == ["drain-b"]
    assert result.path[0].candidate_ref is None


def test_partial_fill_fragmented_release_chain_uses_retained_fill_anchor() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    release = (
        _node(5, "drain-a", 160.0, direction=1, progress=2.0),
        _node(
            6,
            "drain-a",
            163.0,
            direction=1,
            progress=2.0,
            authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        ),
        _node(7, "drain-b", 190.0, direction=1, progress=2.0),
    )
    layers = tuple((node, _unknown(frame)) for frame, node in enumerate(fill))
    layers += tuple((_unknown(frame),) for frame in range(2, 5))
    layers += tuple((node, _unknown(frame)) for frame, node in enumerate(release, 5))

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[5] is OilMaterialPhase.OPEN
    assert result.phases[7] is OilMaterialPhase.DRAINING
    assert result.reasons[7] == "PARTIAL_FILL_DRAIN_RECOVERY_CONFIRMED"
    assert result.allowed_tracklet_ids[7] == frozenset({"drain-b"})
    assert result.owner_chains[7] == ("fill", "drain-a", "drain-b")
    assert result.path[7].candidate_ref is release[2].candidate_ref
    diagnostic = result.diagnostics[7]
    assert diagnostic["release_source"] == "recovery"
    assert diagnostic["established_fill_last_y"] == 150.0
    assert diagnostic["recovery_selected_tracklet_id"] == "drain-b"


def test_recovery_chain_expires_at_absolute_evidence_window() -> None:
    rows = tuple(
        _node(
            frame,
            "slow-drain",
            65.0 + frame * 0.3,
            direction=1,
            progress=2.0,
            authority=(
                OilCandidateAuthority.ANCHOR_ELIGIBLE
                if frame == 0
                else OilCandidateAuthority.CONTINUATION_ELIGIBLE
            ),
        )
        for frame in range(12)
    )
    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(rows)),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert OilMaterialPhase.DRAINING not in result.phases
    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.diagnostics[11]["recovery_reset_reason"] == (
        "evidence_window_expired"
    )


def test_recovery_one_to_many_handoff_resets_involved_chain() -> None:
    layers = (
        (_node(0, "drain-a", 65.0, direction=1, progress=2.0), _unknown(0)),
        (
            _node(1, "drain-b", 70.0, direction=1, progress=2.0),
            _node(1, "drain-c", 70.0, direction=1, progress=2.0),
            _unknown(1),
        ),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.allowed_tracklet_ids[-1] == frozenset()
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[-1]["recovery_ambiguous"] is True
    assert result.diagnostics[-1]["recovery_reset_reason"] == (
        "handoff_ambiguity;ambiguity"
    )


def test_recovery_many_to_one_handoff_resets_both_predecessors() -> None:
    layers = (
        (
            _node(0, "drain-a", 65.0, direction=1, progress=2.0),
            _node(0, "drain-c", 67.0, direction=1, progress=2.0),
            _unknown(0),
        ),
        (_node(1, "drain-b", 75.0, direction=1, progress=2.0), _unknown(1)),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.allowed_tracklet_ids[-1] == frozenset()
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[-1]["recovery_ambiguous"] is True
    assert result.diagnostics[-1]["recovery_reset_reason"] == (
        "handoff_ambiguity;ambiguity"
    )


def test_two_qualifying_recovery_chains_fail_closed() -> None:
    layers = (
        (
            _node(0, "drain-a", 65.0, direction=1, progress=2.0),
            _node(0, "drain-b", 70.0, direction=1, progress=2.0),
            _unknown(0),
        ),
        (
            _node(
                1,
                "drain-a",
                72.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _node(
                1,
                "drain-b",
                77.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(1),
        ),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.allowed_tracklet_ids[-1] == frozenset()
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[-1]["recovery_qualifying_tracklet_ids"] == [
        "drain-a",
        "drain-b",
    ]
    assert result.diagnostics[-1]["recovery_ambiguous"] is True


def test_recovery_ambiguity_blocks_unrelated_qualifier_until_later_frame() -> None:
    layers = (
        (
            _node(0, "ambiguous-a", 65.0, direction=1, progress=2.0),
            _node(0, "unrelated", 10.0, direction=1, progress=2.0),
            _unknown(0),
        ),
        (
            _node(1, "ambiguous-b", 70.0, direction=1, progress=2.0),
            _node(1, "ambiguous-c", 70.0, direction=1, progress=2.0),
            _node(
                1,
                "unrelated",
                20.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(1),
        ),
        (
            _node(
                2,
                "unrelated",
                30.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(2),
        ),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases[1] is OilMaterialPhase.FILLED_BARRIER
    assert result.allowed_tracklet_ids[1] == frozenset()
    assert result.path[1].kind == "unknown"
    assert result.diagnostics[1]["recovery_ambiguous"] is True
    assert "handoff_ambiguity" in result.diagnostics[1]["recovery_reset_reason"]
    assert result.phases[2] is OilMaterialPhase.DRAINING
    assert result.path[2].candidate_ref is layers[2][0].candidate_ref


def test_duplicate_eligible_seed_hypotheses_same_owner_fail_closed() -> None:
    duplicate_a = _node(
        0,
        "duplicate",
        65.0,
        direction=1,
        progress=2.0,
        row_hypothesis_id="hypothesis-a",
    )
    duplicate_b = _node(
        0,
        "duplicate",
        66.0,
        direction=1,
        progress=2.0,
        row_hypothesis_id="hypothesis-b",
    )

    result = _resolve(
        ((duplicate_a, duplicate_b, _unknown(0)),),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    diagnostic = result.diagnostics[0]
    assert result.phases == (OilMaterialPhase.FILLED_BARRIER,)
    assert result.allowed_tracklet_ids == (frozenset(),)
    assert result.path[0].kind == "unknown"
    assert diagnostic["recovery_ambiguous"] is True
    assert diagnostic["recovery_ambiguous_seed_owner_ids"] == ["duplicate"]
    assert diagnostic["recovery_reset_reason"] == (
        "duplicate_seed_hypotheses;ambiguity"
    )
    assert diagnostic["recovery_selected_tracklet_id"] is None


def test_multiple_qualifying_recovery_chains_record_explicit_reset_reason() -> None:
    layers = (
        (
            _node(0, "drain-a", 65.0, direction=1, progress=2.0),
            _node(0, "drain-b", 70.0, direction=1, progress=2.0),
            _unknown(0),
        ),
        (
            _node(
                1,
                "drain-a",
                72.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _node(
                1,
                "drain-b",
                77.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(1),
        ),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    diagnostic = result.diagnostics[-1]
    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert diagnostic["recovery_qualifying_tracklet_ids"] == [
        "drain-a",
        "drain-b",
    ]
    assert diagnostic["recovery_selected_tracklet_id"] is None
    assert diagnostic["recovery_reset_reason"] == (
        "multiple_qualifying_chains;ambiguity"
    )


def test_initial_full_missed_entrance_rows_never_seed_recovery_later() -> None:
    rows = (
        _node(0, "lower", 130.0, direction=1, progress=2.0),
        _node(
            1,
            "lower",
            140.0,
            direction=1,
            progress=2.0,
            authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        ),
    )
    result = _resolve(
        tuple((row, _unknown(frame)) for frame, row in enumerate(rows)),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert all(phase is OilMaterialPhase.FILLED_BARRIER for phase in result.phases)
    assert all(node.kind == "unknown" for node in result.path)
    assert result.diagnostics[1]["recovery_active_chains"] == []


def test_recovery_rejects_non_anchor_seed_and_continuation_only_cross_id_handoff() -> None:
    layers = (
        (
            _node(
                0,
                "continuation-only",
                65.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(0),
        ),
        (
            _node(
                1,
                "new-continuation-only",
                70.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(1),
        ),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert all(phase is OilMaterialPhase.FILLED_BARRIER for phase in result.phases)
    assert all(node.kind == "unknown" for node in result.path)
    assert result.diagnostics[-1]["recovery_active_chains"] == []


def test_recovery_material_opposition_and_incompatible_rows_reset_chain() -> None:
    layers = (
        (_node(0, "drain", 65.0, direction=1, progress=2.0), _unknown(0)),
        (
            _node(
                1,
                "drain",
                70.0,
                direction=1,
                progress=2.0,
                material_conflict=0.80,
                material_path=True,
            ),
            _unknown(1),
        ),
        (
            _node(
                2,
                "incompatible",
                75.0,
                direction=1,
                progress=2.0,
                tracklet_incompatible=True,
            ),
            _unknown(2),
        ),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert all(phase is OilMaterialPhase.FILLED_BARRIER for phase in result.phases)
    assert all(node.kind == "unknown" for node in result.path)
    assert result.diagnostics[1]["recovery_reset_reason"] == "material_or_incompatible"


def test_recovery_rejects_upward_reversal_beyond_tolerance() -> None:
    layers = (
        (_node(0, "drain", 65.0, direction=1, progress=2.0), _unknown(0)),
        (
            _node(
                1,
                "drain",
                59.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(1),
        ),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[-1]["recovery_reset_reason"] == "step_bound"


def test_recovery_gap_beyond_maximum_lost_frames_plus_one_cannot_confirm() -> None:
    layers = [(_node(0, "drain", 65.0, direction=1, progress=2.0), _unknown(0))]
    layers.extend((_unknown(frame),) for frame in range(1, 4))
    layers.append(
        (
            _node(
                4,
                "drain",
                75.0,
                direction=1,
                progress=2.0,
            ),
            _unknown(4),
        )
    )
    result = _resolve(
        tuple(layers),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert OilMaterialPhase.DRAINING not in result.phases
    assert result.path[-1].kind == "unknown"
    assert "loss_window_expired" in result.diagnostics[-1]["recovery_reset_reason"]


def test_recovery_stationary_chain_resets_without_confirmation() -> None:
    rows = tuple(
        _node(
            frame,
            "stationary",
            65.0,
            direction=1,
            progress=2.0,
            authority=(
                OilCandidateAuthority.ANCHOR_ELIGIBLE
                if frame == 0
                else OilCandidateAuthority.CONTINUATION_ELIGIBLE
            ),
        )
        for frame in range(11)
    )
    result = _resolve(
        tuple((row, _unknown(frame)) for frame, row in enumerate(rows)),
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert OilMaterialPhase.DRAINING not in result.phases
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[-1]["recovery_reset_reason"] == "stagnation"


def test_partial_fill_recovery_seed_beyond_one_jump_is_rejected() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    layers = tuple((row, _unknown(frame)) for frame, row in enumerate(fill))
    layers += ((_unknown(2),),)
    layers += (
        (_node(3, "far-drain", 100.0, direction=1, progress=2.0), _unknown(3)),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert OilMaterialPhase.DRAINING not in result.phases
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[-1]["recovery_qualifying_tracklet_ids"] == []


def test_partial_recovery_resets_when_fill_anchor_context_changes() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    layers = tuple((node, _unknown(frame)) for frame, node in enumerate(fill))
    layers += tuple((_unknown(frame),) for frame in range(2, 5))
    layers += (
        (_node(5, "old-drain", 160.0, direction=1, progress=2.0), _unknown(5)),
        (
            _node(
                6,
                "new-fill",
                160.0,
                direction=-1,
                progress=20.0,
                motion_support=0.9,
                motion_coverage=0.85,
                confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            ),
            _unknown(6),
        ),
    )
    layers += tuple((_unknown(frame),) for frame in range(7, 10))
    layers += tuple(
        (
            _node(frame, tracklet, y, direction=1, progress=2.0),
            _unknown(frame),
        )
        for frame, tracklet, y in (
            (10, "new-drain-a", 160.0),
            (11, "new-drain-a", 163.0),
            (12, "new-drain-b", 190.0),
        )
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.owner_chains[12] == (
        "old-drain",
        "new-fill",
        "new-drain-a",
        "new-drain-b",
    )
    recovery_chain = result.diagnostics[12]["recovery_active_chains"][0]
    assert recovery_chain["owner_ids"] == ["new-drain-a", "new-drain-b"]
    assert result.diagnostics[6]["recovery_reset_reason"] == (
        "release_context_changed"
    )


def test_recovery_large_same_owner_jump_cannot_reseed_or_handoff() -> None:
    layers = (
        (_node(0, "drain-a", 65.0, direction=1, progress=2.0), _unknown(0)),
        (_node(1, "drain-a", 110.0, direction=1, progress=2.0), _unknown(1)),
        (_node(2, "drain-b", 140.0, direction=1, progress=2.0), _unknown(2)),
    )
    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert OilMaterialPhase.DRAINING not in result.phases
    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.diagnostics[1]["recovery_reset_reason"] == "step_bound"
    assert result.diagnostics[1]["recovery_active_chains"] == []


def test_delayed_partial_fill_reacquisition_waits_for_grace_and_uses_fresh_anchor() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    layers = tuple((node, _unknown(frame)) for frame, node in enumerate(fill))
    layers += tuple((_unknown(frame),) for frame in range(2, 8))
    delayed_anchor = _node(
        8,
        "delayed-a",
        90.0,
        direction=1,
        progress=2.0,
        phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
    )
    delayed_success = _node(
        9,
        "delayed-a",
        110.0,
        direction=1,
        progress=2.0,
        authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
    )
    layers += (
        (delayed_anchor, _unknown(8)),
        (delayed_success, _unknown(9)),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[5:8] == (
        OilMaterialPhase.OPEN,
        OilMaterialPhase.OPEN,
        OilMaterialPhase.OPEN,
    )
    assert result.allowed_tracklet_ids[5:8] == (
        frozenset(),
        frozenset(),
        frozenset(),
    )
    assert result.phases[8] is OilMaterialPhase.OPEN
    assert result.diagnostics[5]["ownerless_barrier_state"] == "grace"
    assert result.diagnostics[7]["ownerless_barrier_state"] == "grace"
    assert result.diagnostics[8]["ownerless_barrier_state"] == "attempt_active"
    assert result.diagnostics[8]["delayed_reacquisition_snapshot_distance_px"] == 60.0
    assert result.diagnostics[8][
        "delayed_reacquisition_snapshot_distance_used_for_identity"
    ] is False
    assert result.diagnostics[8]["delayed_reacquisition_active_chains"][0][
        "seed_y"
    ] == 90.0
    assert result.phases[9] is OilMaterialPhase.DRAINING
    assert result.reasons[9] == (
        "PARTIAL_FILL_DRAIN_DELAYED_REACQUISITION_CONFIRMED"
    )
    assert result.allowed_tracklet_ids[9] == frozenset({"delayed-a"})
    assert result.owner_chains[9] == ("fill", "delayed-a")
    assert result.path[9].candidate_ref is delayed_success.candidate_ref
    assert result.diagnostics[9]["release_source"] == "delayed_reacquisition"
    assert result.diagnostics[9]["ownerless_barrier_state"] == "released"


def test_delayed_attempt_is_consumed_by_ambiguous_first_anchor_set() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    layers = tuple((node, _unknown(frame)) for frame, node in enumerate(fill))
    layers += tuple((_unknown(frame),) for frame in range(2, 8))
    layers += (
        (
            _node(
                8,
                "delayed-a",
                90.0,
                direction=1,
                progress=2.0,
                phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
            ),
            _node(
                8,
                "delayed-b",
                140.0,
                direction=1,
                progress=2.0,
                phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
            ),
            _unknown(8),
        ),
        (
            _node(
                9,
                "delayed-a",
                110.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(9),
        ),
        (
            _node(
                10,
                "delayed-b",
                160.0,
                direction=1,
                progress=2.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            ),
            _unknown(10),
        ),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert all(phase is OilMaterialPhase.OPEN for phase in result.phases[8:])
    assert result.diagnostics[8]["ownerless_barrier_state"] == "attempt_consumed"
    assert result.diagnostics[8]["ownerless_barrier_attempt_consumed"] is True
    assert result.diagnostics[8]["delayed_reacquisition_ambiguous"] is True
    assert result.diagnostics[8]["delayed_reacquisition_reset_reason"] == (
        "duplicate_delayed_seed_anchors"
    )
    assert result.diagnostics[9]["delayed_reacquisition_active_chains"] == []
    assert result.diagnostics[9]["ownerless_barrier_state"] == "attempt_consumed"
    assert result.diagnostics[10]["delayed_reacquisition_active_chains"] == []


def test_delayed_seed_requires_phase_identity_and_non_provisional_tracklet() -> None:
    fill = (
        _node(
            0,
            "fill",
            180.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
        _node(
            1,
            "fill",
            150.0,
            direction=-1,
            progress=25.0,
            motion_support=0.9,
            motion_coverage=0.85,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        ),
    )
    layers = tuple((node, _unknown(frame)) for frame, node in enumerate(fill))
    layers += tuple((_unknown(frame),) for frame in range(2, 8))
    invalid_phase = _node(
        8,
        "invalid-phase",
        90.0,
        direction=1,
        progress=2.0,
        phase_identity=OilPhaseIdentity.CONTINUATION_ONLY,
    )
    invalid_lifecycle = _node(
        9,
        "invalid-lifecycle",
        90.0,
        direction=1,
        progress=2.0,
        lifecycle=TrackletLifecycle.PROVISIONAL,
        phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
    )
    valid = _node(
        10,
        "valid-delayed",
        90.0,
        direction=1,
        progress=2.0,
        phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
    )
    layers += (
        (invalid_phase, _unknown(8)),
        (invalid_lifecycle, _unknown(9)),
        (valid, _unknown(10)),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[8] is OilMaterialPhase.OPEN
    assert result.phases[9] is OilMaterialPhase.OPEN
    assert result.phases[10] is OilMaterialPhase.OPEN
    assert result.diagnostics[8]["delayed_reacquisition_seed_predicates"][0][
        "first_failed_predicate"
    ] == "phase_identity"
    assert result.diagnostics[9]["delayed_reacquisition_seed_predicates"][0][
        "first_failed_predicate"
    ] == "bounded_confirmed_tracklet"
    assert result.diagnostics[10]["delayed_reacquisition_seed_predicates"][0][
        "first_failed_predicate"
    ] is None
    assert result.diagnostics[10]["ownerless_barrier_state"] == "attempt_active"


def test_confirmed_full_rejects_internal_or_ambiguous_drain_release() -> None:
    internal = _node(0, "internal", 110.0, direction=1, progress=30.0)
    ambiguous = (
        _node(1, "drain-a", 65.0, direction=1, progress=20.0),
        _node(1, "drain-b", 67.0, direction=1, progress=20.0),
    )
    layers = (
        (internal, _unknown(0)),
        (*ambiguous, _unknown(1)),
    )

    result = _resolve(
        layers,
        confirmed_initial_state=InitialObservationState.FULL_NO_INTERFACE,
    )

    assert result.phases == (
        OilMaterialPhase.FILLED_BARRIER,
        OilMaterialPhase.FILLED_BARRIER,
    )
    assert result.reasons == (
        "INITIAL_FULL_BARRIER",
        "DRAIN_RELEASE_AMBIGUOUS",
    )
    assert result.allowed_tracklet_ids == (frozenset(), frozenset())


def test_filled_barrier_ignores_cap_rows_and_gaps() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    cap = _node(
        3,
        "cap",
        55.0,
        direction=1,
        progress=20.0,
        material_conflict=0.80,
    )
    layers = (
        *((node, _unknown(frame)) for frame, node in enumerate(fill)),
        (cap, _unknown(3)),
        (_unknown(4),),
        (_unknown(5),),
        (
            _node(
                6,
                "cap-two",
                60.0,
                direction=1,
                progress=25.0,
                material_conflict=0.75,
            ),
            _unknown(6),
        ),
    )

    result = _resolve(tuple(layers))

    assert all(
        phase is OilMaterialPhase.FILLED_BARRIER
        for phase in result.phases[2:]
    )
    assert result.path[2].kind == "oil"
    assert all(node.kind == "unknown" for node in result.path[3:])


def test_independent_low_conflict_drain_releases_with_same_frame_provenance() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    drain3 = _node(
        3,
        "drain",
        70.0,
        direction=1,
        progress=18.0,
        material_conflict=0.20,
    )
    drain4 = _node(
        4,
        "drain",
        90.0,
        direction=1,
        progress=18.0,
        material_conflict=0.20,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate((*fill, drain3, drain4))
    )

    result = _resolve(layers)

    assert result.phases[2] is OilMaterialPhase.FILLED_BARRIER
    assert result.phases[3:] == (
        OilMaterialPhase.DRAINING,
        OilMaterialPhase.DRAINING,
    )
    assert result.path[3].candidate_ref is drain3.candidate_ref
    assert result.path[4].candidate_ref is drain4.candidate_ref
    assert result.reasons[3] == "DRAIN_RELEASE_CONFIRMED"


def test_internal_downward_row_cannot_release_filled_barrier() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    internal = _node(
        3,
        "internal",
        110.0,
        direction=1,
        progress=30.0,
        material_conflict=0.10,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate((*fill, internal))
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "FILLED_CAP_VETO"


def test_current_material_conflict_cannot_borrow_a_low_historic_average() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    false_drain = _node(
        3,
        "false-drain",
        70.0,
        direction=1,
        progress=18.0,
        material_conflict=0.60,
        tracklet_material_conflict=0.20,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate((*fill, false_drain))
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "FILLED_CAP_VETO"


def test_drain_release_rejects_conflicting_same_row_material_sibling() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    clean, material_path = _material_veto_row(3, "false-drain", 70.0)
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(fill)
    ) + ((clean, material_path, _unknown(3)),)

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "FILLED_CAP_VETO"


def test_drain_continuation_rejects_conflicting_same_row_material_sibling() -> None:
    fill_and_release = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain", 70.0, direction=1, progress=20.0),
    )
    clean, material_path = _material_veto_row(4, "drain", 90.0)
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_release)
    ) + ((clean, material_path, _unknown(4)),)

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.DRAINING
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "DRAIN_OWNER_LOST"


def test_drain_continuation_uses_strong_motion_not_stale_texture_average() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain", 70.0, direction=1, progress=20.0),
        _node(
            4,
            "drain",
            90.0,
            direction=1,
            progress=20.0,
            material_conflict=0.70,
            tracklet_material_conflict=0.60,
            motion_support=0.90,
            motion_coverage=0.80,
        ),
    )

    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(nodes))
    )

    assert result.path[-1].candidate_ref is nodes[-1].candidate_ref
    assert result.reasons[-1] == "DRAIN_OWNER_CONTINUING"


def test_drain_successor_rejects_conflicting_same_row_material_sibling() -> None:
    fill_and_release = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
    )
    clean, material_path = _material_veto_row(4, "drain-b", 90.0)
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_release)
    ) + ((clean, material_path, _unknown(4)),)

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.DRAINING
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "DRAIN_OWNER_LOST"
    assert result.owner_chains[-1] == ("drain-a",)


def test_drain_successor_accepts_strong_clean_material_anchor_witness() -> None:
    fill_and_release = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
    )
    clean_anchor = _node(
        4,
        "drain-b",
        89.0,
        direction=1,
        progress=20.0,
        material_conflict=0.10,
        tracklet_material_conflict=0.60,
        material_path=True,
        motion_support=0.90,
        motion_coverage=0.80,
        candidate_offset=0,
    )
    conflicting_sibling = _node(
        4,
        "drain-b",
        91.0,
        direction=1,
        progress=20.0,
        material_conflict=0.80,
        tracklet_material_conflict=0.60,
        material_path=True,
        motion_support=0.90,
        motion_coverage=0.80,
        authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        candidate_offset=1,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_release)
    ) + ((clean_anchor, conflicting_sibling, _unknown(4)),)

    result = _resolve(layers)

    assert result.reasons[-1] == "DRAIN_CHAIN_HANDOFF"
    assert result.allowed_tracklet_ids[-1] == frozenset({"drain-b"})
    assert result.owner_chains[-1] == ("drain-a", "drain-b")


def test_strong_motion_override_cannot_release_filled_barrier() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    clean_anchor = _node(
        3,
        "false-release",
        69.0,
        direction=1,
        progress=20.0,
        material_conflict=0.10,
        tracklet_material_conflict=0.60,
        material_path=True,
        motion_support=0.90,
        motion_coverage=0.80,
        candidate_offset=0,
    )
    conflicting_sibling = _node(
        3,
        "false-release",
        71.0,
        direction=1,
        progress=20.0,
        material_conflict=0.80,
        tracklet_material_conflict=0.60,
        material_path=True,
        motion_support=0.90,
        motion_coverage=0.80,
        authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        candidate_offset=1,
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(fill)
    ) + ((clean_anchor, conflicting_sibling, _unknown(3)),)

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "FILLED_CAP_VETO"


def test_drain_reentry_rejects_conflicting_same_row_material_sibling() -> None:
    fill_and_drain = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
    )
    clean, material_path = _material_veto_row(8, "late-drain", 105.0)
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_drain)
    ) + tuple((_unknown(frame),) for frame in range(5, 8)) + (
        (clean, material_path, _unknown(8)),
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.DRAINING
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "DRAIN_OWNER_TERMINATED"
    assert result.owner_chains[-1] == ("drain-a",)


def test_unique_drain_release_constrains_selector_before_competing_row() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    selected_internal = _node(
        3,
        "selected-internal",
        115.0,
        direction=-1,
        progress=12.0,
    )
    alternate_drain = _node(
        3,
        "alternate-drain",
        70.0,
        direction=1,
        progress=18.0,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill)
    ) + ((selected_internal, alternate_drain, _unknown(3)),)

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.DRAINING
    assert result.path[-1].candidate_ref is alternate_drain.candidate_ref
    assert result.reasons[-1] == "DRAIN_RELEASE_CONFIRMED"
    assert result.allowed_tracklet_ids[-1] == frozenset({"alternate-drain"})


def test_provisional_downward_tracklet_waits_for_explicit_confirmation() -> None:
    fill = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
    )
    provisional = _node(
        3,
        "provisional-drain",
        70.0,
        direction=1,
        progress=18.0,
        lifecycle=TrackletLifecycle.PROVISIONAL,
        confirmation_profile=TrackletConfirmationProfile.NONE,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate((*fill, provisional))
    )

    result = _resolve(layers)

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].kind == "unknown"
    assert result.reasons[-1] == "FILLED_CAP_VETO"


def test_drain_phase_handoff_keeps_physical_tracklet_ids_separate() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
        _node(5, "drain-b", 110.0, direction=1, progress=20.0),
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(nodes)
    )

    result = _resolve(layers)

    assert result.reasons[-1] == "DRAIN_CHAIN_HANDOFF"
    assert result.owner_chains[-1] == ("drain-a", "drain-b")
    assert result.path[-1].candidate_ref is nodes[-1].candidate_ref
    assert nodes[-2].candidate_ref.tracklet_id == "drain-a"
    assert nodes[-1].candidate_ref.tracklet_id == "drain-b"


def test_ambiguous_drain_handoff_resets_without_branch_choice() -> None:
    fill_and_drain = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_drain)
    ) + (
        (
            _node(5, "drain-b", 110.0, direction=1, progress=20.0),
            _node(5, "drain-c", 112.0, direction=1, progress=20.0),
            _unknown(5),
        ),
    )

    result = _resolve(layers)

    assert result.reasons[-1] == "DRAIN_HANDOFF_AMBIGUOUS"
    assert result.path[-1].kind == "unknown"
    assert result.owner_chains[-1] == ("drain-a",)
    assert 5 in result.ambiguous_frames


def test_distant_drain_tracklet_does_not_inherit_phase_owner() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
        _node(5, "distant", 180.0, direction=1, progress=20.0),
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(nodes)
    )

    result = _resolve(layers)

    assert result.reasons[-1] == "DRAIN_OWNER_LOST"
    assert result.path[-1].kind == "unknown"
    assert result.owner_chains[-1] == ("drain-a",)


def test_terminated_drain_phase_reenters_unique_lower_tracklet_before_scoring() -> None:
    fill_and_drain = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
    )
    upper = _node(
        8,
        "unrelated-upper",
        50.0,
        direction=-1,
        progress=30.0,
        emission=4.0,
    )
    lower = _node(
        8,
        "late-drain",
        105.0,
        direction=1,
        progress=30.0,
        emission=1.0,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_drain)
    ) + tuple((_unknown(frame),) for frame in range(5, 8)) + (
        (upper, lower, _unknown(8)),
    )

    phase = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)
    selected = BoundedOilInterfaceSelector(_selector_policy()).resolve(
        layers,
        _detections(len(layers)),
        None,
        phase.allowed_tracklet_ids,
        phase.owner_chains,
    )

    assert phase.reasons[-1] == "DRAIN_PHASE_REENTRY"
    assert phase.allowed_tracklet_ids[-1] == frozenset({"late-drain"})
    assert phase.owner_chains[-1] == ("drain-a", "late-drain")
    assert selected[-1].candidate_ref is lower.candidate_ref
    assert selected[-1].y == 105.0


def test_upward_reversing_drain_reentry_stays_unknown_within_jump_bound() -> None:
    fill_and_drain = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
    )
    reversed_reentry = _node(
        8,
        "reversed-reentry",
        65.0,
        direction=1,
        progress=30.0,
    )
    layers = tuple(
        (node, _unknown(frame))
        for frame, node in enumerate(fill_and_drain)
    ) + tuple((_unknown(frame),) for frame in range(5, 8)) + (
        (reversed_reentry, _unknown(8)),
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)

    assert result.reasons[-1] == "DRAIN_OWNER_TERMINATED"
    assert result.allowed_tracklet_ids[-1] == frozenset()
    assert result.owner_chains[-1] == ("drain-a",)


def test_same_drain_tracklet_reauthorization_keeps_owner_chain_unique() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
    )
    reobserved = _node(
        8,
        "drain-a",
        105.0,
        direction=1,
        progress=30.0,
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(nodes)
    ) + tuple((_unknown(frame),) for frame in range(5, 8)) + (
        (reobserved, _unknown(8)),
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)

    assert result.reasons[-1] == "DRAIN_PHASE_REENTRY"
    assert result.allowed_tracklet_ids[-1] == frozenset({"drain-a"})
    assert result.owner_chains[-1] == ("drain-a",)


def test_ambiguous_drain_reentry_is_unknown_without_killing_phase_owner() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(nodes)
    ) + tuple((_unknown(frame),) for frame in range(5, 8)) + (
        (
            _node(8, "candidate-b", 103.0, direction=1, progress=20.0),
            _node(8, "candidate-c", 105.0, direction=1, progress=20.0),
            _unknown(8),
        ),
        (
            _node(9, "candidate-b", 106.0, direction=1, progress=20.0),
            _unknown(9),
        ),
    )

    result = OilMaterialPhaseLifecycleOwner(_policy()).resolve(layers)

    assert result.reasons[8] == "DRAIN_REENTRY_AMBIGUOUS"
    assert result.allowed_tracklet_ids[8] == frozenset()
    assert result.owner_chains[8] == ("drain-a",)
    assert result.reasons[9] == "DRAIN_PHASE_REENTRY"
    assert result.allowed_tracklet_ids[9] == frozenset({"candidate-b"})
    assert result.owner_chains[9] == ("drain-a", "candidate-b")


def test_upward_reversing_drain_successor_cannot_inherit_phase_owner() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
        _node(5, "reversed", 80.0, direction=1, progress=20.0),
    )
    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(nodes))
    )

    assert result.reasons[-1] == "DRAIN_OWNER_LOST"
    assert result.path[-1].kind == "unknown"
    assert result.owner_chains[-1] == ("drain-a",)


def test_material_conflicting_drain_successor_cannot_inherit_phase_owner() -> None:
    nodes = (
        _node(0, "fill", 180.0, direction=-1, progress=50.0),
        _node(1, "fill", 120.0, direction=-1, progress=50.0),
        _node(2, "fill", 50.0, direction=-1, progress=50.0),
        _node(3, "drain-a", 70.0, direction=1, progress=20.0),
        _node(4, "drain-a", 90.0, direction=1, progress=20.0),
        _node(
            5,
            "cap-successor",
            110.0,
            direction=1,
            progress=20.0,
            material_conflict=0.80,
        ),
    )
    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(nodes))
    )

    assert result.reasons[-1] == "DRAIN_OWNER_LOST"
    assert result.path[-1].kind == "unknown"
    assert result.owner_chains[-1] == ("drain-a",)


def test_long_steady_drift_cannot_accumulate_lifetime_fill_extrema() -> None:
    nodes = tuple(
        _node(
            frame,
            "steady-interface",
            100.0 - frame,
            direction=-1,
            progress=5.0,
        )
        for frame in range(70)
    )
    layers = tuple(
        (node, _unknown(frame)) for frame, node in enumerate(nodes)
    )

    result = _resolve(layers)

    assert OilMaterialPhase.FILLED_BARRIER not in result.phases
    assert result.phases[-1] is OilMaterialPhase.OPEN
    assert result.path[-1].candidate_ref is nodes[-1].candidate_ref


def test_unknown_motion_only_fill_cannot_arm_without_independent_anchor() -> None:
    nodes = tuple(
        _node(
            frame,
            "motion-only",
            y,
            direction=-1,
            progress=130.0,
            authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            motion_support=0.90,
            motion_coverage=0.80,
        )
        for frame, y in enumerate((180.0, 155.0, 130.0, 100.0, 75.0, 50.0))
    )

    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(nodes))
    )

    assert OilMaterialPhase.FILLED_BARRIER not in result.phases
    assert result.fill_confirmation_profiles[-1] is OilFillConfirmationProfile.NONE


def test_initial_empty_continuation_only_bottom_rise_can_arm_fill() -> None:
    nodes = tuple(
        _node(
            frame,
            "bottom-rising",
            y,
            direction=-1,
            progress=130.0,
            authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            motion_support=0.89,
            motion_coverage=0.80,
        )
        for frame, y in enumerate((180.0, 155.0, 130.0, 100.0, 75.0, 50.0))
    )

    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(nodes)),
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1].candidate_ref is nodes[-1].candidate_ref
    assert (
        result.fill_confirmation_profiles[-1]
        is OilFillConfirmationProfile.EMPTY_ENTRANCE_MOTION
    )


def test_initial_empty_weak_motion_bottom_drift_stays_open() -> None:
    nodes = tuple(
        _node(
            frame,
            "weak-bottom-drift",
            y,
            direction=-1,
            progress=130.0,
            authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
            motion_support=0.26,
            motion_coverage=0.80,
        )
        for frame, y in enumerate((180.0, 155.0, 130.0, 100.0, 75.0, 50.0))
    )

    result = _resolve(
        tuple((node, _unknown(frame)) for frame, node in enumerate(nodes)),
        confirmed_initial_state=InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert OilMaterialPhase.FILLED_BARRIER not in result.phases
    assert result.fill_confirmation_profiles[-1] is OilFillConfirmationProfile.NONE
