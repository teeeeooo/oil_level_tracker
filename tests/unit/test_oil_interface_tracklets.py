from __future__ import annotations

from dataclasses import replace

from oil_tracker.adapters.vision.oil_candidate_authority import (
    OilCandidateAuthority,
)
from oil_tracker.adapters.vision.oil_candidate_evidence import (
    OilCandidateEvidence,
)
from oil_tracker.adapters.vision.oil_interface_tracklets import (
    DirectedInterfaceTrackletBuilder,
    DirectedTrackletPolicy,
)
from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilObservationResolverConfig,
)
from oil_tracker.adapters.vision.oil_interface_selector import (
    BoundedOilInterfaceSelector,
    OilInterfaceSelectorPolicy,
    build_interface_layers,
)
from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilMaterialPhaseLifecycleOwner,
    OilMaterialPhasePolicy,
)
from oil_tracker.adapters.vision.oil_sequence_types import (
    OilCandidateRef,
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
    initial_state: InitialObservationState | None = None,
) -> DirectedTrackletPolicy:
    return DirectedTrackletPolicy(
        geometry_top_y=0.0,
        geometry_height=200.0,
        maximum_jump_px=32.0,
        row_hypothesis_tolerance_px=4.0,
        maximum_lost_frames=2,
        confirmation_window_frames=6,
        confirmation_min_observations=3,
        confirmation_min_anchor_frames=2,
        confirmation_min_progress_px=5.0,
        confirmation_min_directional_agreement=0.60,
        confirmation_min_motion_support=0.50,
        confirmation_min_motion_coverage=0.50,
        continuation_grace_frames=2,
        continuation_min_motion_energy=0.08,
        continuation_min_motion_coverage=0.12,
        entrance_band_ratio=0.27,
        initial_state=initial_state,
    )


def _ref(
    frame: int,
    offset: int,
    y: float,
    *,
    authority: OilCandidateAuthority,
    source: str,
    motion: float = 0.0,
    coverage: float = 0.0,
    ordered_lower: bool = False,
) -> OilCandidateRef:
    candidate = BoundaryCandidate(
        source=source,
        kind=BoundaryKind.OIL_AIR,
        y=y,
        features={
            "boundary_likelihood": 0.72,
            "artifact_likelihood": 0.08,
            "ambiguity_likelihood": 0.16,
            "broad_strength": 0.62,
            "narrow_peak_strength": 0.70,
            "narrow_horizontal_coverage": 0.65,
            "broad_scale_consistency": 0.75,
            "polarity_confidence": 0.65,
            "evidence_availability": 1.0,
            "visibility": 1.0,
            "sequence_eligible": 1.0,
            "registered_oil_band_motion_support": motion,
            "registered_oil_band_motion_coverage": coverage,
        },
        penalties={
            "artifact_likelihood": 0.08,
            "ambiguity_likelihood": 0.16,
        },
        feature_score=0.72,
        final_score=0.72,
    )
    return OilCandidateRef(
        frame_offset=frame,
        candidate_offset=offset,
        candidate=candidate,
        evidence=OilCandidateEvidence.from_candidate(candidate),
        local_quality=0.80,
        authority=authority,
        initial_authority=authority,
        post_track_authority=authority,
        ordered_lower=ordered_lower,
    )


def _by_source(result, source: str) -> list[OilCandidateRef]:
    return [
        ref
        for refs in result.refs_by_frame
        for ref in refs
        if ref.candidate.source == source
    ]


def test_same_frame_row_hypothesis_retains_every_candidate_provenance() -> None:
    frames = tuple(
        (
            _ref(
                frame,
                0,
                100.0 + frame,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source=f"phase-{frame}",
            ),
            _ref(
                frame,
                1,
                102.0 + frame,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source=f"material-{frame}",
            ),
        )
        for frame in range(3)
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)

    for original, resolved in zip(frames, result.refs_by_frame, strict=True):
        assert [item.candidate for item in resolved] == [
            item.candidate for item in original
        ]
        assert len({item.row_hypothesis_id for item in resolved}) == 1
        assert len({item.tracklet_id for item in resolved}) == 1
        assert all(item.tracklet_admitted for item in resolved)
    assert result.hypothesis_count == 3


def test_same_physical_row_aggregates_cross_representation_members() -> None:
    frames = tuple(
        (
            _ref(
                frame,
                0,
                100.0 + frame,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="direct-material",
            ),
            _ref(
                frame,
                1,
                102.0 + frame,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source="ordered-phase",
                ordered_lower=True,
            ),
        )
        for frame in range(3)
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)

    assert result.hypothesis_count == 3
    assert all(
        len({item.row_hypothesis_id for item in refs}) == 1
        for refs in result.refs_by_frame
    )
    assert all(
        len({item.tracklet_id for item in refs}) == 1
        for refs in result.refs_by_frame
    )
    assert all(
        item.tracklet_admitted
        for refs in result.refs_by_frame
        for item in refs
    )


def test_row_hypothesis_span_does_not_chain_distinct_nearby_rows() -> None:
    frames = tuple(
        (
            _ref(
                frame,
                0,
                100.0 + frame,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="upper",
            ),
            _ref(
                frame,
                1,
                103.0 + frame,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="middle",
                ordered_lower=True,
            ),
            _ref(
                frame,
                2,
                106.0 + frame,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="lower",
            ),
        )
        for frame in range(3)
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)

    assert result.hypothesis_count == 6
    assert all(
        len({item.row_hypothesis_id for item in refs}) == 2
        for refs in result.refs_by_frame
    )


def test_dual_representation_row_bridges_a_bounded_family_transition() -> None:
    frames = (
        (
            _ref(
                0,
                0,
                100.0,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="material",
            ),
        ),
        (
            _ref(
                1,
                0,
                101.0,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="material",
            ),
        ),
        (
            _ref(
                2,
                0,
                102.0,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="material",
            ),
            _ref(
                2,
                1,
                103.0,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source="phase",
                ordered_lower=True,
            ),
        ),
        *tuple(
            (
                _ref(
                    frame,
                    0,
                    101.0 + frame,
                    authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                    source="phase",
                    ordered_lower=True,
                ),
            )
            for frame in range(3, 6)
        ),
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)

    assert len(
        {
            item.tracklet_id
            for refs in result.refs_by_frame
            for item in refs
        }
    ) == 1
    assert all(
        item.tracklet_admitted
        for refs in result.refs_by_frame
        for item in refs
    )


def test_abrupt_representation_change_starts_a_new_provisional_identity() -> None:
    frames = tuple(
        (
            _ref(
                frame,
                0,
                100.0 + frame,
                authority=(
                    OilCandidateAuthority.ANCHOR_ELIGIBLE
                    if frame < 3
                    else OilCandidateAuthority.CONTINUATION_ELIGIBLE
                ),
                source="direct-before" if frame < 3 else "ordered-after",
                ordered_lower=frame >= 3,
            ),
        )
        for frame in range(6)
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)
    before = {
        item.tracklet_id
        for refs in result.refs_by_frame[:3]
        for item in refs
    }
    after = {
        item.tracklet_id
        for refs in result.refs_by_frame[3:]
        for item in refs
    }

    assert before.isdisjoint(after)
    assert not any(
        item.tracklet_admitted
        for refs in result.refs_by_frame[3:]
        for item in refs
    )


def test_composed_confirmation_and_onset_lag_uses_end_to_end_commit_horizon() -> None:
    target = 0
    stage_lag = 6
    commit_lag = OilObservationResolverConfig().end_to_end_commit_lag_frames

    assert commit_lag == 11

    def frame_refs(frame: int) -> tuple[OilCandidateRef, ...]:
        refs = []
        if frame <= 2:
            refs.append(
                _ref(
                    frame,
                    0,
                    100.0 + frame,
                    authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                    source="visible-interface",
                )
            )
        if 3 <= frame <= commit_lag:
            dynamic_y = {
                3: 120.0,
                4: 119.0,
                5: 118.0,
                6: 117.0,
                7: 105.0,
                8: 94.0,
                9: 83.0,
                10: 72.0,
                11: 61.0,
            }[frame]
            refs.append(
                _ref(
                    frame,
                    1,
                    dynamic_y,
                    authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                    source="late-confirmed-dynamic",
                    motion=0.90,
                    coverage=0.80,
                    ordered_lower=True,
                )
            )
        if frame > commit_lag:
            refs.append(
                _ref(
                    frame,
                    2,
                    40.0 + 5.0 * (frame - commit_lag),
                    authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                    source="hostile-suffix",
                )
            )
        return tuple(refs)

    def resolve(frame_count: int):
        refs = tuple(frame_refs(frame) for frame in range(frame_count))
        tracklets = DirectedInterfaceTrackletBuilder(
            replace(
                _policy(),
                confirmation_min_anchor_frames=3,
                confirmation_min_progress_px=10.0,
            )
        ).resolve(refs)
        detections = tuple(
            PhaseDetection(
                glass_id="glass",
                frame_index=frame,
                time_sec=frame * 0.5,
                fill_state=FillState.UNKNOWN_REVIEW,
                candidates=[ref.candidate for ref in refs[frame]],
                visibility_confidence=1.0,
                overall_confidence=0.2,
                debug_metrics={"oil_ambiguity_score": 0.15},
            )
            for frame in range(frame_count)
        )
        layer_pairs = tuple(
            build_interface_layers(
                detection,
                tracklets.refs_by_frame[frame],
                hard_unavailable=False,
                minimum_confidence=0.28,
                state_min_evidence=0.58,
            )
            for frame, detection in enumerate(detections)
        )
        phase = OilMaterialPhaseLifecycleOwner(
            OilMaterialPhasePolicy(
                geometry_top_y=0.0,
                geometry_height=200.0,
                maximum_jump_px=32.0,
                maximum_lost_frames=3,
                handoff_ambiguity_margin=0.08,
                handoff_direction_reversal_tolerance_px=3.0,
                fill_onset_intent_frames=stage_lag,
                fill_evidence_window_frames=12,
                entrance_band_ratio=0.27,
                fill_minimum_span_ratio=0.20,
                minimum_directional_agreement=0.60,
                empty_entrance_motion_enabled=False,
                fill_minimum_motion_support=0.50,
                fill_minimum_motion_coverage=0.50,
                drain_entrance_ratio=0.40,
                drain_minimum_progress_ratio=0.025,
                drain_minimum_directional_agreement=0.60,
                material_conflict_limit=0.45,
            )
        ).resolve(tuple(pair[0] for pair in layer_pairs))
        selected = BoundedOilInterfaceSelector(
            OilInterfaceSelectorPolicy(
                geometry_top_y=0.0,
                geometry_height=200.0,
                maximum_jump_px=32.0,
                lookahead_frames=stage_lag,
                ambiguity_margin=0.08,
                unknown_transition_cost=0.20,
                incompatible_state_transition_cost=2.5,
                state_min_evidence=0.58,
                entrance_band_ratio=0.27,
            )
        ).resolve(
            tuple(pair[1] for pair in layer_pairs),
            detections,
            None,
            phase.allowed_tracklet_ids,
            phase.owner_chains,
        )
        return tracklets, phase, selected

    stage_prefix = resolve(target + stage_lag + 1)
    confirmation_suffix = resolve(8)
    prefix_tracklets, prefix_phase, prefix_selected = stage_prefix
    extended_tracklets, extended_phase, extended_selected = confirmation_suffix

    assert not any(
        ref.tracklet_admitted
        for refs in prefix_tracklets.refs_by_frame[3:]
        for ref in refs
        if ref.candidate.source == "late-confirmed-dynamic"
    )
    extended_dynamic = tuple(
        ref
        for refs in extended_tracklets.refs_by_frame[3:]
        for ref in refs
        if ref.candidate.source == "late-confirmed-dynamic"
    )
    assert all(
        ref.tracklet_confirmation_profile
        is TrackletConfirmationProfile.MOTION_TRAJECTORY
        for ref in extended_dynamic
    ), tuple(
        (
            ref.frame_offset,
            ref.candidate.y,
            ref.tracklet_id,
            ref.tracklet_admitted,
            ref.tracklet_confirmation_profile,
            ref.tracklet_failure_reason,
        )
        for ref in extended_dynamic
    )
    # t+6 is only the individual selector/onset window.  Confirmation at t+7
    # can still make the onset intent visible, so t is not committed yet.
    assert prefix_selected[target].y == extended_selected[target].y
    assert prefix_phase.reasons[target] == "FILLING_TRACKLET"
    assert (
        extended_phase.reasons[target]
        == "FILL_ONSET_INTENT_PREDECESSOR"
    )
    assert prefix_phase.owner_chains[target] != extended_phase.owner_chains[target]

    committed = resolve(target + commit_lag + 1)
    hostile_suffix = resolve(target + commit_lag + 7)
    _committed_tracklets, committed_phase, committed_selected = committed
    _suffix_tracklets, suffix_phase, suffix_selected = hostile_suffix

    assert committed_selected[target].y == suffix_selected[target].y
    assert (
        committed_selected[target].candidate_ref.tracklet_id
        == suffix_selected[target].candidate_ref.tracklet_id
    )
    assert committed_phase.phases[target] is suffix_phase.phases[target]
    assert committed_phase.reasons[target] == suffix_phase.reasons[target]
    assert committed_phase.owner_chains[target] == suffix_phase.owner_chains[target]


def test_bottom_motion_tracklet_confirms_without_borrowing_false_upper_anchor() -> None:
    upper = (82.0, 80.0, 79.0, 78.0, 77.0, 76.0)
    lower = (192.0, 180.0, 166.0, 151.0, 138.0, 126.0)
    frames = tuple(
        (
            _ref(
                frame,
                0,
                upper[frame],
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="false-upper-anchor",
            ),
            _ref(
                frame,
                1,
                lower[frame],
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source="bottom-rising-continuation",
                motion=0.90,
                coverage=0.80,
            ),
        )
        for frame in range(len(lower))
    )

    result = DirectedInterfaceTrackletBuilder(
        _policy(InitialObservationState.EMPTY_NO_INTERFACE)
    ).resolve(frames)
    upper_refs = _by_source(result, "false-upper-anchor")
    lower_refs = _by_source(result, "bottom-rising-continuation")

    assert {item.tracklet_id for item in upper_refs}.isdisjoint(
        {item.tracklet_id for item in lower_refs}
    )
    assert not any(item.tracklet_admitted for item in upper_refs)
    assert all(item.tracklet_admitted for item in lower_refs)
    assert all(
        item.tracklet_confirmation_profile
        is TrackletConfirmationProfile.ENTRANCE_MOTION
        for item in lower_refs
    )
    assert all(
        item.tracklet_failure_reason == "ENTRANCE_ORIGIN_MISSING"
        for item in upper_refs
    )


def test_stationary_lower_structure_stays_provisional_without_motion() -> None:
    ys = (190.0, 191.0, 190.0, 191.0, 190.0, 191.0)
    frames = tuple(
        (
            _ref(
                frame,
                0,
                y,
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source="static-lower",
            ),
        )
        for frame, y in enumerate(ys)
    )

    result = DirectedInterfaceTrackletBuilder(
        _policy(InitialObservationState.EMPTY_NO_INTERFACE)
    ).resolve(frames)
    refs = _by_source(result, "static-lower")

    assert not any(item.tracklet_admitted for item in refs)
    assert all(
        item.tracklet_lifecycle is TrackletLifecycle.PROVISIONAL
        for item in refs
    )
    assert all(
        item.tracklet_failure_reason == "INSUFFICIENT_NET_PROGRESS"
        for item in refs
    )


def test_anchor_trajectory_does_not_yield_to_weak_continuation_drift() -> None:
    true_upper = (145.0, 136.0, 126.0, 116.0, 106.0, 96.0)
    false_lower = (175.0, 176.0, 177.0, 178.0, 179.0, 180.0)
    frames = tuple(
        (
            _ref(
                frame,
                0,
                true_upper[frame],
                authority=(
                    OilCandidateAuthority.ANCHOR_ELIGIBLE
                    if frame == len(true_upper) - 1
                    else OilCandidateAuthority.CONTINUATION_ELIGIBLE
                ),
                source="true-upper-anchor-trajectory",
                motion=0.20,
                coverage=0.20,
            ),
            _ref(
                frame,
                1,
                false_lower[frame],
                authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source="false-lower-drift",
                motion=0.40,
                coverage=0.60,
            ),
        )
        for frame in range(len(true_upper))
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)
    true_refs = _by_source(result, "true-upper-anchor-trajectory")
    false_refs = _by_source(result, "false-lower-drift")

    assert all(item.tracklet_admitted for item in true_refs)
    assert all(
        item.tracklet_confirmation_profile
        is TrackletConfirmationProfile.ANCHOR_TRAJECTORY
        for item in true_refs
    )
    assert not any(item.tracklet_admitted for item in false_refs)
    assert all(
        item.tracklet_confirmation_profile is TrackletConfirmationProfile.NONE
        for item in false_refs
    )


def test_crossing_branches_terminate_instead_of_hopping_or_merging() -> None:
    first = (80.0, 90.0, 100.0, 110.0, 120.0, 130.0)
    second = (140.0, 130.0, 120.0, 110.0, 100.0, 90.0)
    frames = tuple(
        (
            _ref(
                frame,
                0,
                first[frame],
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="branch-a",
            ),
            _ref(
                frame,
                1,
                second[frame],
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="branch-b",
            ),
        )
        for frame in range(len(first))
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)

    assert 3 in result.incompatible_frames
    assert not any(item.tracklet_admitted for item in result.refs_by_frame[3])
    before = {
        item.tracklet_id
        for refs in result.refs_by_frame[:3]
        for item in refs
    }
    after = {
        item.tracklet_id
        for refs in result.refs_by_frame[4:]
        for item in refs
    }
    assert before.isdisjoint(after)
    assert any(
        item.termination_reason == "AMBIGUOUS_BRANCH"
        for item in result.summaries
    )


def test_sparse_motion_supports_continuation_without_a_per_frame_gate() -> None:
    frames = []
    for frame in range(10):
        frames.append(
            (
                _ref(
                    frame,
                    0,
                    100.0 + frame,
                    authority=(
                        OilCandidateAuthority.ANCHOR_ELIGIBLE
                        if frame < 2
                        else OilCandidateAuthority.CONTINUATION_ELIGIBLE
                    ),
                    source="sparse-motion",
                    motion=0.90 if frame in {4, 7} else 0.0,
                    coverage=0.80 if frame in {4, 7} else 0.0,
                ),
            )
        )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(tuple(frames))
    refs = _by_source(result, "sparse-motion")

    assert all(item.tracklet_admitted for item in refs)
    assert refs[5].evidence.registered_motion == 0.0
    assert refs[5].tracklet_lifecycle is TrackletLifecycle.CONTINUING


def test_lost_frame_has_no_observation_and_reacquisition_retains_identity() -> None:
    frames = (
        (
            _ref(
                0,
                0,
                100.0,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="gap-track",
            ),
        ),
        (
            _ref(
                1,
                0,
                101.0,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="gap-track",
            ),
        ),
        (),
        (
            _ref(
                3,
                0,
                103.0,
                authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                source="gap-track",
            ),
        ),
    )

    result = DirectedInterfaceTrackletBuilder(_policy()).resolve(frames)
    refs = _by_source(result, "gap-track")

    assert result.refs_by_frame[2] == ()
    assert len({item.tracklet_id for item in refs}) == 1
    assert result.lost_event_count == 1
    assert TrackletLifecycle.LOST in result.summaries[0].lifecycle_history


def test_tracklet_assignment_is_permutation_stable_and_incrementally_bounded() -> None:
    def rows(reverse: bool):
        output = []
        for frame in range(100):
            refs = [
                _ref(
                    frame,
                    offset,
                    y + 0.5 * frame,
                    authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
                    source=source,
                )
                for offset, (source, y) in enumerate(
                    (("low", 60.0), ("middle", 110.0), ("high", 160.0))
                )
            ]
            if reverse:
                refs.reverse()
                refs = [
                    replace(item, candidate_offset=offset)
                    for offset, item in enumerate(refs)
                ]
            output.append(tuple(refs))
        return tuple(output)

    builder = DirectedInterfaceTrackletBuilder(_policy())
    forward = builder.resolve(rows(False))
    reverse = builder.resolve(rows(True))

    forward_ids = {
        item.candidate.source: item.tracklet_id
        for item in forward.refs_by_frame[-1]
    }
    reverse_ids = {
        item.candidate.source: item.tracklet_id
        for item in reverse.refs_by_frame[-1]
    }
    assert forward_ids == reverse_ids
    assert forward.maximum_active_tracklets <= 3
    assert forward.comparison_count <= 100 * 3 * 3
