from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Iterable, Sequence

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig

from .oil_candidate_authority import (
    AuthorityContext,
    AuthorityReason,
    OilCandidateAuthority,
    evaluate_candidate_authority,
)
from .oil_candidate_evidence import (
    OilCandidateEvidence,
    OilCandidateEvidenceIndex,
    candidate_is_eligible,
)
from .oil_interface_tracklets import (
    DirectedInterfaceTrackletBuilder,
    DirectedTrackletPolicy,
    DirectedTrackletResult,
)
from .oil_interface_selector import (
    BoundedOilInterfaceSelector,
    OilInterfaceSelectorPolicy,
    assert_publishable_path as _assert_publishable_path,
    build_interface_layers,
    effective_track_opposition as _effective_track_opposition,
    oil_candidate_confidence as _oil_confidence,
    oil_candidate_emission as _oil_emission,
    recurrence_hard_contradiction as _recurrence_hard_contradiction,
)
from .oil_phase_lifecycle import (
    OilFillConfirmationProfile,
    OilMaterialPhase,
    OilMaterialPhaseLifecycleOwner,
    OilMaterialPhasePolicy,
)
from .foam_material_identity import (
    FoamMaterialIdentity,
    foam_material_identity_tolerance,
    track_foam_material_identity,
)
from .oil_sequence_types import (
    OilCandidateRef as _CandidateRef,
    OilSequenceNode as _Node,
)
from .oil_phase_identity import (
    OilPhaseIdentity,
    PhaseIdentityContext,
    evaluate_phase_identity,
)


OIL_OBSERVATION_RESOLVER_VERSION = "r16-directed-interface-tracklets-v1"

_OIL_REPLACED_FLAGS = {
    "LOW_CONFIDENCE",
    "OIL_EVIDENCE_AMBIGUOUS",
    "OIL_PIPELINE_UNAVAILABLE",
    "OIL_REACQUISITION_PENDING",
    "R6_IMAGE_SUPPORTED_STATE",
    "R6_INITIAL_STATE_CONTEXT_ONLY",
    "R6_OBSERVATION_UNAVAILABLE",
    "R6_RESOLVED_OIL",
    "R7_IMAGE_SUPPORTED_STATE",
    "R7_INITIAL_STATE_CONTEXT_ONLY",
    "R7_OBSERVATION_UNAVAILABLE",
    "R7_OIL_ANCHOR",
    "R7_OIL_CONTINUATION",
    "R7_RESOLVED_OIL",
    "R16_IMAGE_SUPPORTED_STATE",
    "R16_INITIAL_STATE_CONTEXT_ONLY",
    "R16_MATERIAL_PHASE_BARRIER",
    "R16_OBSERVATION_UNAVAILABLE",
    "R16_RESOLVED_OIL",
    "R16_TRACKLET_CONFIRMED",
    "R16_TRACKLET_CONTINUING",
    "R16_TRACKLET_WITNESS",
    "SEQUENCE_INITIAL_STATE_PRIOR",
    "SEQUENCE_RESOLVED_OIL",
    "SEQUENCE_RESOLVED_STATE",
    "SEQUENCE_SAME_FRAME_CANDIDATE",
    "SEQUENCE_UNAVAILABLE",
}
_HARD_UNAVAILABLE_FLAGS = {
    "DETECTION_FAILED",
    "DETECTION_LOST",
    "FOGGED_OR_GLARE",
    "FRAME_UNAVAILABLE",
    "OIL_PIPELINE_FAILURE",
    "OIL_PIPELINE_UNAVAILABLE",
    "REDETECTION_SAMPLE_FAILED",
    "UNAVAILABLE",
}


@dataclass(frozen=True)
class OilObservationResolverConfig:
    entrance_band_ratio: float = 0.27
    recurring_track_min_frames: int = 6
    recurring_track_min_ratio: float = 0.18
    recurring_track_tolerance_ratio: float = 0.018
    recurring_track_reject_opposition: float = 0.60
    anchor_min_material: float = 0.32
    anchor_min_boundary: float = 0.34
    anchor_min_boundary_advantage: float = 0.08
    anchor_max_artifact: float = 0.34
    anchor_max_ambiguity: float = 0.64
    continuation_min_material: float = 0.23
    continuation_min_boundary: float = 0.18
    continuation_max_artifact: float = 0.46
    continuation_max_ambiguity: float = 0.84
    terminal_anchor_min_support: float = 0.55
    terminal_anchor_min_sector_fraction: float = 0.78
    dynamic_anchor_min_support: float = 0.18
    dynamic_anchor_min_coverage: float = 0.60
    state_min_evidence: float = 0.58
    black_frame_max_mean: float = 2.0
    black_frame_max_std: float = 2.0
    black_frame_max_dynamic_range: float = 4.0
    unknown_transition_cost: float = 0.20
    incompatible_state_transition_cost: float = 2.5
    completed_fill_min_span_ratio: float = 0.20
    completed_fill_gap_frames: int = 6
    completed_fill_release_ratio: float = 0.40
    completed_fill_release_lookahead_frames: int = 6
    completed_fill_release_min_downward_ratio: float = 0.025
    completed_fill_release_directional_ratio: float = 0.60
    completed_fill_material_conflict_min: float = 0.45
    trajectory_spike_min_px: float = 8.0
    trajectory_spike_tolerance_ratio: float = 0.25
    trajectory_spike_lookaround_frames: int = 3
    high_recall_candidate_ref_limit: int = 8
    tracklet_row_hypothesis_ratio: float = 0.012
    tracklet_maximum_lost_frames: int = 2
    tracklet_confirmation_window_frames: int = 6
    tracklet_confirmation_min_observations: int = 3
    tracklet_confirmation_min_progress_ratio: float = 0.05
    tracklet_confirmation_min_directional_agreement: float = 0.60
    tracklet_confirmation_min_motion_support: float = 0.50
    tracklet_confirmation_min_motion_coverage: float = 0.50
    tracklet_continuation_grace_frames: int = 2
    tracklet_continuation_min_motion_energy: float = 0.08
    tracklet_continuation_min_motion_coverage: float = 0.12
    tracklet_ambiguity_margin: float = 0.08

    @property
    def end_to_end_commit_lag_frames(self) -> int:
        """Bound suffix influence across confirmation and fixed-lag stages."""

        stage_lag = max(0, int(self.tracklet_confirmation_window_frames))
        confirmation_future = max(0, stage_lag - 1)
        return stage_lag + confirmation_future


@dataclass(frozen=True)
class OilObservationDiagnostics:
    version: str
    frame_count: int
    oil_frame_count: int
    full_frame_count: int
    empty_frame_count: int
    unknown_frame_count: int
    eligible_candidate_count: int
    ineligible_candidate_count: int
    recurring_track_count: int
    maximum_track_opposition: float
    candidate_only_count: int = 0
    continuation_eligible_count: int = 0
    anchor_eligible_count: int = 0
    qualified_anchor_count: int = 0
    foam_material_seeded_frame_count: int = 0
    foam_material_continued_frame_count: int = 0
    foam_material_opposed_candidate_count: int = 0
    tracklet_count: int = 0
    confirmed_tracklet_count: int = 0
    provisional_tracklet_count: int = 0
    incompatible_tracklet_frame_count: int = 0
    tracklet_lost_event_count: int = 0
    terminated_tracklet_count: int = 0
    tracklet_hypothesis_count: int = 0
    tracklet_comparison_count: int = 0
    maximum_active_tracklets: int = 0
    maximum_tracklet_eligible_refs_per_frame: int = 0
    maximum_tracklet_hypotheses_per_frame: int = 0


@dataclass(frozen=True)
class OilObservationResolution:
    detections: tuple[PhaseDetection, ...]
    diagnostics: OilObservationDiagnostics


@dataclass(frozen=True)
class OilPathLifecycleResult:
    layers: tuple[tuple[_Node, ...], ...]
    best_path: tuple[_Node, ...]
    bounded_path: tuple[_Node, ...]
    spike_suppressed_path: tuple[_Node, ...]
    path: tuple[_Node, ...]
    material_phases: tuple[OilMaterialPhase, ...]
    material_phase_reasons: tuple[str, ...]
    material_phase_owner_chains: tuple[tuple[str, ...], ...]
    material_phase_fill_confirmation_profiles: tuple[
        OilFillConfirmationProfile, ...
    ]
    material_phase_ambiguous_frames: frozenset[int]


class OilAdmissionEvidenceOwner:
    """Normalize candidates and establish same-frame admission evidence."""

    def __init__(self, config: OilObservationResolverConfig) -> None:
        self.config = config

    def prepare(
        self,
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
        evidence_index: OilCandidateEvidenceIndex,
    ) -> tuple[
        tuple[tuple[_CandidateRef, ...], ...],
        int,
        FoamMaterialIdentity,
    ]:
        return self._candidate_refs(detections, glass, evidence_index)

    def _candidate_refs(
        self,
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
        evidence_index: OilCandidateEvidenceIndex,
    ) -> tuple[
        tuple[tuple[_CandidateRef, ...], ...],
        int,
        FoamMaterialIdentity,
    ]:
        limit = max(1, int(glass.detector_settings.candidate_top_k))
        rows: list[tuple[_CandidateRef, ...]] = []
        ineligible = 0
        foam_material_identity = track_foam_material_identity(
            detections,
            glass,
            evidence_index=evidence_index,
        )
        semantic_anchor_keys = _qualified_ordinary_semantic_keys(
            detections,
            glass,
            evidence_index=evidence_index,
        )
        semantic_anchor_rows = tuple(
            (frame_offset, float(detections[frame_offset].candidates[candidate_offset].y))
            for frame_offset, candidate_offset in sorted(semantic_anchor_keys)
        )
        # Terminal anchoring is only a bounded single-observation fallback.
        # Absence of a semantic corridor in a long sequence is not positive
        # physical evidence and must not manufacture anchor authority.
        sequence_span_sec = (
            0.0
            if len(detections) <= 1
            else float(detections[-1].time_sec) - float(detections[0].time_sec)
        )
        terminal_fallback_mode = len(detections) <= 6 or sequence_span_sec <= 3.0
        lower_separation = foam_material_identity_tolerance(glass) + 2.0
        for frame_offset, detection in enumerate(detections):
            refs: list[_CandidateRef] = []
            oil_candidates = tuple(
                candidate
                for candidate in detection.candidates
                if candidate.kind is BoundaryKind.OIL_AIR
                and _finite(candidate.y)
            )
            foam_rows = tuple(
                float(candidate.y)
                for candidate in detection.candidates
                if candidate.kind is BoundaryKind.FOAM_FRONT
                and _finite(candidate.y)
                and _unit(candidate.features.get("sequence_foam_eligible", 0.0))
                >= 0.5
            )
            for candidate_offset, candidate in enumerate(detection.candidates):
                if candidate.kind is not BoundaryKind.OIL_AIR or not _finite(candidate.y):
                    continue
                evidence = evidence_index.evidence(candidate)
                material_identity_opposition = foam_material_identity.opposition(
                    frame_offset,
                    candidate_offset,
                )
                material_identity_row = foam_material_identity.row(frame_offset)
                foam_seed_age_seconds = foam_material_identity.seed_age_seconds(
                    frame_offset
                )
                ordered_lower = bool(
                    material_identity_row is not None
                    and float(candidate.y)
                    >= material_identity_row + lower_separation
                    and material_identity_opposition < 0.20
                )
                candidate = replace(
                    candidate,
                    features={
                        **candidate.features,
                        "foam_material_identity": material_identity_opposition,
                        "composition_lower_reserve": float(ordered_lower),
                    },
                )
                evidence_index.register(candidate, evidence)
                representation_support = _cross_representation_support(
                    candidate,
                    oil_candidates,
                    glass,
                    evidence_index=evidence_index,
                )
                semantic_corridor_support = _semantic_corridor_support(
                    frame_offset,
                    float(candidate.y),
                    semantic_anchor_rows,
                    glass,
                )
                allow_terminal_anchor = terminal_fallback_mode
                phase_identity = evaluate_phase_identity(
                    candidate,
                    self.config,
                    PhaseIdentityContext(
                        representation_support=representation_support,
                        foam_material_identity=material_identity_opposition,
                        foam_material_row=material_identity_row,
                        foam_seed_age_seconds=foam_seed_age_seconds,
                        lower_separation_px=lower_separation,
                    ),
                    evidence=evidence,
                )
                authority_decision = evaluate_candidate_authority(
                    candidate,
                    self.config,
                    AuthorityContext(
                        representation_support=representation_support,
                        semantic_corridor_support=semantic_corridor_support,
                        semantic_sequence_available=bool(semantic_anchor_keys),
                        allow_terminal_anchor=allow_terminal_anchor,
                        allow_material_layer_terminal=len(detections) <= 6,
                        foam_material_identity=material_identity_opposition,
                        foam_material_row=material_identity_row,
                        foam_seed_age_seconds=foam_seed_age_seconds,
                        lower_separation_px=lower_separation,
                        phase_identity=phase_identity,
                    ),
                    evidence=evidence,
                )
                authority = authority_decision.tier
                if authority is OilCandidateAuthority.HARD_INVALID:
                    ineligible += 1
                    continue
                foam_alias_penalty = _foam_front_alias_penalty(
                    candidate,
                    foam_rows,
                    glass,
                )
                refs.append(
                    _CandidateRef(
                        frame_offset=frame_offset,
                        candidate_offset=candidate_offset,
                        candidate=candidate,
                        evidence=evidence,
                        local_quality=_candidate_quality(
                            candidate,
                            evidence=evidence,
                            terminal_fallback=allow_terminal_anchor,
                        )
                        + 0.14 * representation_support
                        + 0.18 * semantic_corridor_support
                        - foam_alias_penalty
                        - 0.40 * material_identity_opposition
                        + (
                            0.16
                            if authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                            else 0.0
                        ),
                        authority=authority,
                        initial_authority=authority,
                        post_track_authority=authority,
                        representation_support=representation_support,
                        semantic_corridor_support=semantic_corridor_support,
                        terminal_fallback=allow_terminal_anchor,
                        foam_alias_penalty=foam_alias_penalty,
                        authority_reason=authority_decision.reason,
                        authority_failed_gates=authority_decision.failed_gates,
                        foam_material_identity=material_identity_opposition,
                        phase_identity=phase_identity.identity,
                        phase_identity_failed_gates=phase_identity.failed_gates,
                        ordered_lower=phase_identity.ordered_lower,
                    )
                )
            refs = _demote_non_nearest_ordered_lower_anchors(refs, glass)
            refs.sort(
                key=lambda item: (
                    -int(item.authority),
                    -item.local_quality,
                    float(item.candidate.y),
                    item.candidate.source,
                )
            )
            selected_refs = list(
                ref
                for ref in refs
                if not ref.evidence.calibrated_high_recall
            )[:limit]
            if not any(
                ref.evidence.supplemental
                and not ref.evidence.calibrated_high_recall
                for ref in selected_refs
            ):
                supplemental = next(
                    (
                        ref
                        for ref in refs
                        if ref.evidence.supplemental
                        and not ref.evidence.calibrated_high_recall
                        and ref not in selected_refs
                    ),
                    None,
                )
                if supplemental is not None:
                    selected_refs.append(supplemental)
            high_recall = [
                ref
                for ref in refs
                if ref.evidence.calibrated_high_recall
            ][: min(
                12,
                max(
                    4,
                    min(limit, int(self.config.high_recall_candidate_ref_limit)),
                ),
            )]
            selected_refs.extend(high_recall)
            lower_reserve = next(
                (
                    ref
                    for ref in refs
                    if _unit(
                        ref.candidate.features.get(
                            "composition_lower_reserve",
                            0.0,
                        )
                    )
                    >= 0.5
                    and ref not in selected_refs
                ),
                None,
            )
            if lower_reserve is not None:
                selected_refs.append(lower_reserve)
            rows.append(tuple(selected_refs))
        return tuple(rows), ineligible, foam_material_identity


class OilTrackletOppositionOwner:
    """Apply recurring-row opposition, then build directed Oil tracklets."""

    def __init__(self, config: OilObservationResolverConfig) -> None:
        self.config = config

    def resolve(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> tuple[DirectedTrackletResult, int, float]:
        opposed, track_count, maximum = self._apply_track_opposition(
            refs_by_frame,
            glass,
        )
        tracklets = DirectedInterfaceTrackletBuilder(
            _tracklet_policy(
                opposed,
                glass,
                self.config,
                confirmed_initial_state,
            )
        ).resolve(opposed)
        return tracklets, track_count, maximum

    def _apply_track_opposition(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[tuple[_CandidateRef, ...], ...], int, float]:
        frame_count = len(refs_by_frame)
        height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
        tolerance = max(
            3.0,
            height * self.config.recurring_track_tolerance_ratio,
        )
        # Evaluate several shifted grids. A fixed row that jitters across one
        # quantization boundary must not escape the recurrence check.
        bucket_width = tolerance * 2.4
        buckets: dict[tuple[int, int], list[_CandidateRef]] = {}
        for phase, shift in enumerate((0.0, bucket_width / 3.0, 2.0 * bucket_width / 3.0)):
            for refs in refs_by_frame:
                for ref in refs:
                    bucket = int(math.floor((float(ref.candidate.y) + shift) / bucket_width))
                    buckets.setdefault((phase, bucket), []).append(ref)

        penalties: dict[tuple[int, int], float] = {}
        recurring_tracks: set[int] = set()
        maximum = 0.0
        for bucket_refs in buckets.values():
            best_by_frame: dict[int, _CandidateRef] = {}
            for ref in bucket_refs:
                prior = best_by_frame.get(ref.frame_offset)
                if prior is None or ref.local_quality > prior.local_quality:
                    best_by_frame[ref.frame_offset] = ref
            ordered = tuple(best_by_frame[index] for index in sorted(best_by_frame))
            presence_ratio = len(ordered) / max(1, frame_count)
            longest_run = _longest_consecutive(
                tuple(item.frame_offset for item in ordered)
            )
            if (
                len(ordered) < self.config.recurring_track_min_frames
                or presence_ratio < self.config.recurring_track_min_ratio
                or longest_run < self.config.recurring_track_min_frames
            ):
                continue
            ys = tuple(float(item.candidate.y) for item in ordered)
            mean_y = sum(ys) / len(ys)
            variance = sum((value - mean_y) ** 2 for value in ys) / len(ys)
            stability = max(
                0.0,
                1.0 - math.sqrt(variance) / max(1.0, tolerance * 1.5),
            )
            if stability <= 0.0:
                continue
            opposition = sum(
                item.evidence.artifact_signature
                for item in ordered
            ) / len(ordered)
            optics = sum(
                item.evidence.optics_opposition
                for item in ordered
            ) / len(ordered)
            material = sum(
                item.evidence.material_support
                for item in ordered
            ) / len(ordered)
            supplemental_ratio = sum(
                item.evidence.material_path for item in ordered
            ) / len(ordered)
            semantic_support = sum(
                item.semantic_corridor_support for item in ordered
            ) / len(ordered)
            semantic_mode_ratio = sum(
                not item.terminal_fallback for item in ordered
            ) / len(ordered)
            registered_motion = sum(
                item.evidence.registered_motion
                for item in ordered
            ) / len(ordered)
            registered_coverage = sum(
                item.evidence.registered_motion_coverage
                for item in ordered
            ) / len(ordered)
            contradiction = max(
                0.0,
                max(opposition, optics) - 0.35 * material - 0.04,
            )
            recurrence = _unit(
                (presence_ratio - self.config.recurring_track_min_ratio)
                / max(0.01, 0.70 - self.config.recurring_track_min_ratio)
            )
            semantic_penalty = _unit(
                recurrence * stability * contradiction * 2.6
            )
            # The supplemental path generator intentionally has broad recall.
            # A nearly fixed supplemental row therefore needs another semantic
            # anchor; continuity cannot turn it into truth by itself.
            supplemental_fixed_penalty = _unit(
                recurrence
                * stability
                * supplemental_ratio
                * max(
                    0.0,
                    max(opposition, optics) - 0.30 * material,
                )
                * 2.2
            )
            # In a stream that already has an ordinary semantic corridor, a
            # nearly fixed supplemental row must agree with that corridor on
            # more than isolated frames. This is the competing-track form of
            # static artifact rejection: it does not apply in terminal-only
            # fallback streams such as a real near-bottom material boundary.
            uncorroborated_fixed_penalty = _unit(
                recurrence
                * stability
                * supplemental_ratio
                * semantic_mode_ratio
                * _unit((0.30 - semantic_support) / 0.20)
                * 1.25
            )
            raw_track_penalty = max(
                semantic_penalty,
                supplemental_fixed_penalty,
                uncorroborated_fixed_penalty,
            )
            # A stable Y track is not automatically a fixed artifact. Real Oil
            # can remain at one level while the registered phase raster evolves
            # around the meniscus. Conversely, a lower rim/cap tends to remain
            # both position-stable and raster-static. Use candidate-local Oil
            # motion only as relief from recurrence opposition; it never grants
            # anchor authority by itself.
            dynamic_relief = _unit(
                0.75 * registered_motion + 0.25 * registered_coverage
            )
            track_penalty = _unit(
                raw_track_penalty * (1.0 - 0.80 * dynamic_relief)
            )
            if track_penalty <= 0.0:
                continue
            recurring_tracks.add(int(round(mean_y / tolerance)))
            maximum = max(maximum, track_penalty)
            for item in bucket_refs:
                key = (item.frame_offset, item.candidate_offset)
                penalties[key] = max(penalties.get(key, 0.0), track_penalty)

        output = tuple(
            tuple(
                replace(
                    ref,
                    authority=(
                        OilCandidateAuthority.CANDIDATE_ONLY
                        if penalties.get(
                            (ref.frame_offset, ref.candidate_offset),
                            0.0,
                        )
                        >= self.config.recurring_track_reject_opposition
                        and _recurrence_hard_contradiction(ref)
                        else ref.authority
                    ),
                    track_opposition=penalties.get(
                        (ref.frame_offset, ref.candidate_offset),
                        0.0,
                    ),
                )
                for ref in refs
            )
            for refs in refs_by_frame
        )
        reconciled: list[tuple[_CandidateRef, ...]] = []
        for refs in output:
            row: list[_CandidateRef] = []
            for ref in refs:
                material_path = ref.evidence.material_path
                opposed_peer = next(
                    (
                        peer
                        for peer in refs
                        if not material_path
                        and peer.evidence.material_path
                        and peer.track_opposition
                        >= self.config.recurring_track_reject_opposition
                        and abs(float(peer.candidate.y) - float(ref.candidate.y))
                        <= 8.0
                    ),
                    None,
                )
                if opposed_peer is not None and _recurrence_hard_contradiction(ref):
                    ref = replace(
                        ref,
                        authority=OilCandidateAuthority.CANDIDATE_ONLY,
                        track_opposition=max(
                            ref.track_opposition,
                            opposed_peer.track_opposition,
                        ),
                    )
                terminal = (
                    ref.evidence.terminal_support
                    if ref.evidence.material_path
                    else 0.0
                )
                superior_partition = next(
                    (
                        peer
                        for peer in refs
                        if peer is not ref
                        and peer.evidence.material_path
                        and peer.evidence.terminal_support >= 0.60
                        and _unit(
                            peer.candidate.features.get(
                                "sequence_material_layer_topology",
                                0.0,
                            )
                        )
                        < 0.50
                        and abs(float(peer.candidate.y) - float(ref.candidate.y))
                        >= 8.0
                        and (
                            (
                                terminal >= 0.60
                                and peer.local_quality
                                >= ref.local_quality + 0.03
                            )
                            or (
                                terminal < 0.60
                                and peer.local_quality + 0.05
                                >= ref.local_quality
                            )
                        )
                    ),
                    None,
                )
                if superior_partition is None or not _recurrence_hard_contradiction(ref):
                    row.append(ref)
                    continue
                row.append(
                    replace(
                        ref,
                        authority=OilCandidateAuthority.CANDIDATE_ONLY,
                        track_opposition=max(ref.track_opposition, 0.80),
                    )
                )
            reconciled.append(tuple(row))
        output = tuple(reconciled)
        output = tuple(
            tuple(
                replace(ref, post_track_authority=ref.authority)
                for ref in refs
            )
            for refs in output
        )
        return output, len(recurring_tracks), maximum


class OilPathLifecycleOwner:
    """Resolve path transitions and apply bounded compatibility lifecycle rules."""

    def __init__(self, config: OilObservationResolverConfig) -> None:
        self.config = config

    def resolve(
        self,
        detections: tuple[PhaseDetection, ...],
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> OilPathLifecycleResult:
        layer_pairs = tuple(
            build_interface_layers(
                detection,
                refs_by_frame[index],
                hard_unavailable=_hard_unavailable(
                    detection,
                    self.config,
                ),
                minimum_confidence=float(
                    glass.detector_settings.minimum_final_confidence
                ),
                state_min_evidence=self.config.state_min_evidence,
            )
            for index, detection in enumerate(detections)
        )
        phase_layers = tuple(pair[0] for pair in layer_pairs)
        layers = tuple(pair[1] for pair in layer_pairs)
        phase = OilMaterialPhaseLifecycleOwner(
            _material_phase_policy(
                glass,
                self.config,
                confirmed_initial_state,
            )
        ).resolve(phase_layers)
        selection_path = BoundedOilInterfaceSelector(
            _interface_selector_policy(glass, self.config)
        ).resolve(
            layers,
            detections,
            confirmed_initial_state,
            phase.allowed_tracklet_ids,
            phase.owner_chains,
        )
        bounded_path = _assert_publishable_path(
            selection_path,
            float(glass.detector_settings.minimum_final_confidence),
        )
        spike_suppressed_path = self._suppress_trajectory_spikes(
            bounded_path,
            layers,
            glass,
        )
        return OilPathLifecycleResult(
            layers=layers,
            best_path=selection_path,
            bounded_path=bounded_path,
            spike_suppressed_path=spike_suppressed_path,
            path=spike_suppressed_path,
            material_phases=phase.phases,
            material_phase_reasons=phase.reasons,
            material_phase_owner_chains=phase.owner_chains,
            material_phase_fill_confirmation_profiles=(
                phase.fill_confirmation_profiles
            ),
            material_phase_ambiguous_frames=phase.ambiguous_frames,
        )

    def _suppress_trajectory_spikes(
        self,
        path: tuple[_Node, ...],
        layers: tuple[tuple[_Node, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[_Node, ...]:
        """Remove a one-frame weaker partition that breaks a stable interface.

        This is a censor, not interpolation: the source frame becomes UNKNOWN
        and the report may only draw its normal display-only gap bridge. The
        rule is intentionally topology-backed so a genuinely strong terminal
        boundary is not erased merely because it changes direction quickly.
        """

        output = list(path)
        tolerance = max(
            self.config.trajectory_spike_min_px,
            float(glass.detector_settings.temporal_max_jump_px)
            * self.config.trajectory_spike_tolerance_ratio,
        )
        for index in range(1, len(path) - 1):
            current = path[index]
            lookaround = max(1, self.config.trajectory_spike_lookaround_frames)
            prior_index = next(
                (
                    offset
                    for offset in range(
                        index - 1,
                        max(-1, index - lookaround - 1),
                        -1,
                    )
                    if path[offset].kind == "oil"
                ),
                None,
            )
            following_index = next(
                (
                    offset
                    for offset in range(
                        index + 1,
                        min(len(path), index + lookaround + 1),
                    )
                    if path[offset].kind == "oil"
                ),
                None,
            )
            if prior_index is None or following_index is None:
                continue
            prior = path[prior_index]
            following = path[following_index]
            if (
                current.kind != "oil"
                or prior.y is None
                or current.y is None
                or following.y is None
                or prior.candidate_ref is None
                or current.candidate_ref is None
                or following.candidate_ref is None
            ):
                continue
            if len(
                {
                    _node_tracklet_id(prior),
                    _node_tracklet_id(current),
                    _node_tracklet_id(following),
                }
            ) != 1:
                continue
            if abs(following.y - prior.y) > tolerance * 1.5:
                continue
            fraction = (index - prior_index) / (following_index - prior_index)
            expected = prior.y + fraction * (following.y - prior.y)
            if abs(current.y - expected) <= tolerance:
                continue
            neighboring_partition = min(
                _candidate_terminal_support(
                    prior.candidate_ref.candidate,
                    prior.candidate_ref.evidence,
                ),
                _candidate_terminal_support(
                    following.candidate_ref.candidate,
                    following.candidate_ref.evidence,
                ),
            )
            current_partition = _candidate_terminal_support(
                current.candidate_ref.candidate,
                current.candidate_ref.evidence,
            )
            if current_partition + 0.20 >= neighboring_partition:
                continue
            output[index] = _unknown_node(layers[index])
        return tuple(output)

class OilResolutionProjectionOwner:
    """Project resolved nodes back to same-frame public candidates and metrics."""

    def __init__(self, version: str) -> None:
        self.version = version

    def project(
        self,
        detections: tuple[PhaseDetection, ...],
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        lifecycle: OilPathLifecycleResult,
        tracklets: DirectedTrackletResult,
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
        evidence_index: OilCandidateEvidenceIndex,
    ) -> tuple[PhaseDetection, ...]:
        return tuple(
            self._project_detection(
                detection,
                node,
                refs_by_frame[index],
                tracklets,
                lifecycle.path,
                (
                    lifecycle.best_path[index],
                    lifecycle.bounded_path[index],
                    lifecycle.spike_suppressed_path[index],
                    lifecycle.path[index],
                ),
                lifecycle.material_phases[index],
                lifecycle.material_phase_reasons[index],
                lifecycle.material_phase_owner_chains[index],
                lifecycle.material_phase_fill_confirmation_profiles[index],
                index in lifecycle.material_phase_ambiguous_frames,
                index,
                glass,
                confirmed_initial_state,
                evidence_index,
            )
            for index, (detection, node) in enumerate(
                zip(detections, lifecycle.path, strict=True)
            )
        )

    def diagnostics(
        self,
        resolved: tuple[PhaseDetection, ...],
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        lifecycle: OilPathLifecycleResult,
        tracklets: DirectedTrackletResult,
        *,
        ineligible_count: int,
        track_count: int,
        maximum_track_opposition: float,
        foam_material_identity: FoamMaterialIdentity,
    ) -> OilObservationDiagnostics:
        counts = {
            kind: sum(node.kind == kind for node in lifecycle.path)
            for kind in ("oil", "full", "empty", "unknown")
        }
        return OilObservationDiagnostics(
            version=self.version,
            frame_count=len(resolved),
            oil_frame_count=counts["oil"],
            full_frame_count=counts["full"],
            empty_frame_count=counts["empty"],
            unknown_frame_count=counts["unknown"],
            eligible_candidate_count=sum(map(len, refs_by_frame)),
            ineligible_candidate_count=ineligible_count,
            recurring_track_count=track_count,
            maximum_track_opposition=maximum_track_opposition,
            candidate_only_count=sum(
                ref.authority is OilCandidateAuthority.CANDIDATE_ONLY
                for refs in refs_by_frame
                for ref in refs
            ),
            continuation_eligible_count=sum(
                ref.authority is OilCandidateAuthority.CONTINUATION_ELIGIBLE
                for refs in refs_by_frame
                for ref in refs
            ),
            anchor_eligible_count=sum(
                ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                for refs in refs_by_frame
                for ref in refs
            ),
            qualified_anchor_count=sum(
                ref.cluster_support >= 0.99
                for refs in refs_by_frame
                for ref in refs
            ),
            foam_material_seeded_frame_count=(
                foam_material_identity.seeded_frame_count
            ),
            foam_material_continued_frame_count=(
                foam_material_identity.continued_frame_count
            ),
            foam_material_opposed_candidate_count=len(
                foam_material_identity.opposition_by_candidate
            ),
            tracklet_count=len(tracklets.summaries),
            confirmed_tracklet_count=tracklets.confirmed_tracklet_count,
            provisional_tracklet_count=tracklets.provisional_tracklet_count,
            incompatible_tracklet_frame_count=len(
                tracklets.incompatible_frames
            ),
            tracklet_lost_event_count=tracklets.lost_event_count,
            terminated_tracklet_count=tracklets.terminated_tracklet_count,
            tracklet_hypothesis_count=tracklets.hypothesis_count,
            tracklet_comparison_count=tracklets.comparison_count,
            maximum_active_tracklets=tracklets.maximum_active_tracklets,
            maximum_tracklet_eligible_refs_per_frame=(
                tracklets.maximum_eligible_refs_per_frame
            ),
            maximum_tracklet_hypotheses_per_frame=(
                tracklets.maximum_hypotheses_per_frame
            ),
        )

    def _project_detection(
        self,
        detection: PhaseDetection,
        node: _Node,
        refs: tuple[_CandidateRef, ...],
        tracklets: DirectedTrackletResult,
        path: tuple[_Node, ...],
        stage_nodes: tuple[_Node, _Node, _Node, _Node],
        material_phase: OilMaterialPhase,
        material_phase_reason: str,
        material_phase_owner_chain: tuple[str, ...],
        material_phase_fill_confirmation_profile: OilFillConfirmationProfile,
        material_phase_ambiguous: bool,
        frame_offset: int,
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
        evidence_index: OilCandidateEvidenceIndex,
    ) -> PhaseDetection:
        flags = [flag for flag in detection.flags if flag not in _OIL_REPLACED_FLAGS]
        material_ownership_barrier = (
            material_phase is OilMaterialPhase.FILLED_BARRIER
            and material_phase_reason
            not in {"FILL_SPAN_CONFIRMED", "FILL_OWNER_AT_ENTRANCE"}
        )
        candidates = _project_candidates(
            detection.candidates,
            node.candidate_ref,
            refs,
            evidence_index,
            material_ownership_barrier=material_ownership_barrier,
        )
        metrics = dict(detection.debug_metrics)
        metrics.update(
            {
                "sequence_resolver_version": self.version,
                "sequence_resolved_kind": node.kind,
                "sequence_resolved_source_y": node.y,
                "sequence_emission": float(node.emission),
                "sequence_stage_best_path_kind": stage_nodes[0].kind,
                "sequence_stage_best_path_y": stage_nodes[0].y,
                "sequence_stage_continuation_bound_kind": stage_nodes[1].kind,
                "sequence_stage_continuation_bound_y": stage_nodes[1].y,
                "sequence_stage_spike_suppressed_kind": stage_nodes[2].kind,
                "sequence_stage_spike_suppressed_y": stage_nodes[2].y,
                "sequence_stage_completed_fill_kind": stage_nodes[3].kind,
                "sequence_stage_completed_fill_y": stage_nodes[3].y,
                "sequence_material_phase": material_phase.value,
                "sequence_material_phase_reason": material_phase_reason,
                "sequence_material_phase_owner_chain": ";".join(
                    material_phase_owner_chain
                ),
                "sequence_material_phase_fill_confirmation_profile": (
                    material_phase_fill_confirmation_profile.value
                ),
                "sequence_material_phase_ambiguous": float(
                    material_phase_ambiguous
                ),
                "sequence_track_opposition": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.track_opposition)
                ),
                "sequence_effective_track_opposition": (
                    0.0
                    if node.candidate_ref is None
                    else float(_effective_track_opposition(node.candidate_ref))
                ),
                "sequence_anchor_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.cluster_support)
                ),
                "sequence_trajectory_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.trajectory_support)
                ),
                "sequence_cross_representation_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.representation_support)
                ),
                "sequence_semantic_corridor_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.semantic_corridor_support)
                ),
                "sequence_terminal_partition_support": (
                    0.0
                    if node.candidate_ref is None
                    else _candidate_terminal_support(
                        node.candidate_ref.candidate,
                        node.candidate_ref.evidence,
                    )
                ),
                "sequence_terminal_fallback_mode": float(
                    node.candidate_ref is not None
                    and node.candidate_ref.terminal_fallback
                ),
                "sequence_registered_candidate_motion_support": (
                    0.0
                    if node.candidate_ref is None
                    else node.candidate_ref.evidence.registered_motion
                ),
                "sequence_selected_authority_tier": (
                    OilCandidateAuthority.HARD_INVALID.name
                    if node.candidate_ref is None
                    else node.candidate_ref.authority.name
                ),
                "sequence_selected_authority_reason": (
                    None
                    if node.candidate_ref is None
                    else node.candidate_ref.authority_reason.value
                ),
                "sequence_selected_foam_material_identity": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.foam_material_identity)
                ),
                "sequence_selected_authority_failed_gates": (
                    ""
                    if node.candidate_ref is None
                    else ";".join(node.candidate_ref.authority_failed_gates)
                ),
                "sequence_selected_phase_identity": (
                    None
                    if node.candidate_ref is None
                    else node.candidate_ref.phase_identity.value
                ),
                "sequence_selected_phase_identity_failed_gates": (
                    ""
                    if node.candidate_ref is None
                    else ";".join(node.candidate_ref.phase_identity_failed_gates)
                ),
                "sequence_selected_tracklet_id": (
                    ""
                    if node.candidate_ref is None
                    else node.candidate_ref.tracklet_id or ""
                ),
                "sequence_selected_row_hypothesis_id": (
                    ""
                    if node.candidate_ref is None
                    else node.candidate_ref.row_hypothesis_id or ""
                ),
                "sequence_selected_tracklet_lifecycle": (
                    None
                    if node.candidate_ref is None
                    else node.candidate_ref.tracklet_lifecycle.value
                ),
                "sequence_selected_tracklet_confirmation_profile": (
                    None
                    if node.candidate_ref is None
                    else node.candidate_ref.tracklet_confirmation_profile.value
                ),
                "sequence_selected_tracklet_admitted": float(
                    node.candidate_ref is not None
                    and node.candidate_ref.tracklet_admitted
                ),
                "sequence_selected_tracklet_confirmation_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(
                        node.candidate_ref.tracklet_confirmation_support
                    )
                ),
                "sequence_selected_tracklet_net_progress_px": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.tracklet_net_progress_px)
                ),
                "sequence_selected_tracklet_direction": (
                    0
                    if node.candidate_ref is None
                    else int(node.candidate_ref.tracklet_direction)
                ),
                "sequence_selected_tracklet_directional_agreement": (
                    0.0
                    if node.candidate_ref is None
                    else float(
                        node.candidate_ref.tracklet_directional_agreement
                    )
                ),
                "sequence_selected_tracklet_motion_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.tracklet_motion_support)
                ),
                "sequence_selected_tracklet_motion_coverage": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.tracklet_motion_coverage)
                ),
                "sequence_selected_tracklet_material_conflict": (
                    0.0
                    if node.candidate_ref is None
                    else float(
                        node.candidate_ref.tracklet_material_conflict
                    )
                ),
                "sequence_tracklet_incompatible": float(
                    frame_offset in tracklets.incompatible_frames
                ),
                "sequence_tracklet_failure_reason": (
                    node.candidate_ref.tracklet_failure_reason
                    if node.candidate_ref is not None
                    else (
                        "MATERIAL_OWNERSHIP_BARRIER"
                        if material_ownership_barrier
                        else _frame_tracklet_failure(refs)
                    )
                ),
                "sequence_material_ownership_barrier": float(
                    material_ownership_barrier
                ),
                "sequence_tracklet_count": len(tracklets.summaries),
                "sequence_confirmed_tracklet_count": (
                    tracklets.confirmed_tracklet_count
                ),
                "sequence_provisional_tracklet_count": (
                    tracklets.provisional_tracklet_count
                ),
                "sequence_tracklet_comparison_count": (
                    tracklets.comparison_count
                ),
                "sequence_maximum_active_tracklets": (
                    tracklets.maximum_active_tracklets
                ),
                "sequence_maximum_tracklet_eligible_refs_per_frame": (
                    tracklets.maximum_eligible_refs_per_frame
                ),
                "sequence_maximum_tracklet_hypotheses_per_frame": (
                    tracklets.maximum_hypotheses_per_frame
                ),
                "sequence_state_image_evidence": float(node.state_evidence),
            }
        )
        if node.kind == "oil":
            assert node.y is not None and node.candidate_ref is not None
            y = float(node.y)
            zero = glass.geometry.zero_line_y
            px = None if zero is None else float(zero) - y
            mm = None if px is None or glass.mm_per_pixel is None else px * glass.mm_per_pixel
            confidence = _oil_confidence(node.candidate_ref)
            state = _visible_state(path, frame_offset)
            flags.extend(
                (
                    "R16_RESOLVED_OIL",
                    (
                        "R16_TRACKLET_CONFIRMED"
                        if node.candidate_ref.tracklet_lifecycle.value
                        == "confirmed"
                        else (
                            "R16_TRACKLET_CONTINUING"
                            if node.candidate_ref.tracklet_lifecycle.value
                            == "continuing"
                            else "R16_TRACKLET_WITNESS"
                        )
                    ),
                    "SEQUENCE_RESOLVED_OIL",
                    "SEQUENCE_SAME_FRAME_CANDIDATE",
                )
            )
            return replace(
                detection,
                fill_state=state,
                oil_air_level_y=y,
                oil_air_level_px_from_zero=px,
                oil_air_level_mm_from_zero=mm,
                oil_air_confidence=confidence,
                overall_confidence=confidence,
                raw_oil_air_level_y=y,
                smoothed_oil_air_level_y=y,
                candidates=candidates,
                flags=sorted(set(flags)),
                debug_metrics=metrics,
            )
        if node.kind in {"full", "empty"}:
            state = (
                FillState.FULL_NO_INTERFACE
                if node.kind == "full"
                else FillState.EMPTY_NO_INTERFACE
            )
            flags.extend(("R16_IMAGE_SUPPORTED_STATE", "SEQUENCE_RESOLVED_STATE"))
            confidence = min(0.95, 0.46 + 0.46 * node.state_evidence)
            return replace(
                detection,
                fill_state=state,
                oil_air_level_y=None,
                oil_air_level_px_from_zero=None,
                oil_air_level_mm_from_zero=None,
                oil_air_confidence=0.0,
                overall_confidence=confidence,
                raw_oil_air_level_y=None,
                smoothed_oil_air_level_y=None,
                candidates=candidates,
                flags=sorted(set(flags)),
                debug_metrics=metrics,
            )
        flags.extend(("R16_OBSERVATION_UNAVAILABLE", "SEQUENCE_UNAVAILABLE"))
        if material_ownership_barrier:
            flags.append("R16_MATERIAL_PHASE_BARRIER")
        if confirmed_initial_state is not None:
            flags.append("R16_INITIAL_STATE_CONTEXT_ONLY")
        return replace(
            detection,
            fill_state=FillState.UNKNOWN_REVIEW,
            oil_air_level_y=None,
            oil_air_level_px_from_zero=None,
            oil_air_level_mm_from_zero=None,
            oil_air_confidence=0.0,
            overall_confidence=min(detection.overall_confidence, 0.40),
            raw_oil_air_level_y=None,
            smoothed_oil_air_level_y=None,
            candidates=candidates,
            flags=sorted(set(flags)),
            debug_metrics=metrics,
        )


class OilObservationResolver:
    """Coordinate completed-window Oil owners without inventing observations."""

    version = OIL_OBSERVATION_RESOLVER_VERSION

    def __init__(self, config: OilObservationResolverConfig | None = None) -> None:
        self.config = config or OilObservationResolverConfig()
        self.admission_evidence = OilAdmissionEvidenceOwner(self.config)
        self.tracklet_opposition = OilTrackletOppositionOwner(
            self.config
        )
        self.path_lifecycle = OilPathLifecycleOwner(self.config)
        self.projection = OilResolutionProjectionOwner(self.version)

    def resolve(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> OilObservationResolution:
        source = tuple(detections)
        if not source:
            return OilObservationResolution(
                (),
                OilObservationDiagnostics(
                    self.version,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0.0,
                ),
            )

        evidence_index = OilCandidateEvidenceIndex(source)
        refs_by_frame, ineligible_count, foam_material_identity = (
            self.admission_evidence.prepare(
                source,
                glass,
                evidence_index,
            )
        )
        tracklets, track_count, maximum_track_opposition = (
            self.tracklet_opposition.resolve(
                refs_by_frame,
                glass,
                confirmed_initial_state,
            )
        )
        refs_by_frame = tracklets.refs_by_frame
        lifecycle = self.path_lifecycle.resolve(
            source,
            refs_by_frame,
            glass,
            confirmed_initial_state,
        )
        resolved = self.projection.project(
            source,
            refs_by_frame,
            lifecycle,
            tracklets,
            glass,
            confirmed_initial_state,
            evidence_index,
        )
        diagnostics = self.projection.diagnostics(
            resolved,
            refs_by_frame,
            lifecycle,
            tracklets,
            ineligible_count=ineligible_count,
            track_count=track_count,
            maximum_track_opposition=maximum_track_opposition,
            foam_material_identity=foam_material_identity,
        )
        return OilObservationResolution(resolved, diagnostics)


def _candidate_eligible(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> bool:
    return candidate_is_eligible(candidate, evidence)


def _cross_representation_support(
    candidate: BoundaryCandidate,
    candidates: tuple[BoundaryCandidate, ...],
    glass: GlassInspectionConfig,
    *,
    evidence_index: OilCandidateEvidenceIndex,
) -> float:
    """Measure same-frame agreement between independent proposal families.

    Material-path rows are deliberately broad.  They gain anchor eligibility
    only when an ordinary phase hypothesis at the same row supplies its own
    material/coverage evidence.  The old selected bit and Foam raster motion
    are not consulted.
    """

    candidate_family = _candidate_representation_family(
        candidate,
        evidence_index.evidence(candidate),
    )
    tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.375,
    )
    support = 0.0
    for peer in candidates:
        if peer is candidate:
            continue
        peer_evidence = evidence_index.evidence(peer)
        peer_family = _candidate_representation_family(peer, peer_evidence)
        if peer_family == candidate_family or not _candidate_eligible(
            peer,
            peer_evidence,
        ):
            continue
        if (
            peer_evidence.material_texture_conflict >= 0.60
            or peer_evidence.artifact_signature >= 0.44
            or peer_evidence.optics_opposition >= 0.46
        ):
            # Two generators observing the same contradicted material/optical
            # structure are not independent phase corroboration.
            continue
        if "calibrated_raster" in {candidate_family, peer_family} and "material" not in {
            candidate_family,
            peer_family,
        }:
            continue
        distance = abs(float(peer.y) - float(candidate.y))
        if distance > tolerance:
            continue
        peer_features = peer.features
        peer_boundary = _unit(
            peer_features.get("boundary_likelihood", peer.feature_score)
        )
        peer_artifact = _unit(
            peer_features.get(
                "artifact_likelihood",
                peer.penalties.get("artifact_likelihood", 0.0),
            )
        )
        peer_coverage = _unit(
            peer_features.get(
                "narrow_horizontal_coverage",
                peer_features.get("horizontal_coverage", 0.0),
            )
        )
        advantage = _unit((peer_boundary - peer_artifact + 0.10) / 0.30)
        evidence = _unit(
            0.55 * peer_evidence.material_support
            + 0.25 * peer_coverage
            + 0.20 * advantage
        )
        proximity = 0.75 + 0.25 * _unit(1.0 - distance / tolerance)
        support = max(support, evidence * proximity)
    return _unit(support)


def _candidate_material_support(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).material_support


def _candidate_terminal_support(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    evidence = evidence or OilCandidateEvidence.from_candidate(candidate)
    return evidence.terminal_support if evidence.material_path else 0.0


def _candidate_static_contradiction(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).static_contradiction


def _candidate_registered_motion(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).registered_motion


def _candidate_registered_motion_coverage(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (
        evidence or OilCandidateEvidence.from_candidate(candidate)
    ).registered_motion_coverage


def _candidate_is_material_path(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> bool:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).material_path


def _candidate_is_supplemental(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> bool:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).supplemental


def _candidate_is_calibrated_high_recall(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> bool:
    return (
        evidence or OilCandidateEvidence.from_candidate(candidate)
    ).calibrated_high_recall


def _candidate_representation_family(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> str:
    evidence = evidence or OilCandidateEvidence.from_candidate(candidate)
    if evidence.material_path:
        return "material"
    if evidence.calibrated_high_recall or evidence.supplemental:
        return "calibrated_raster"
    return "phase_hypothesis"


def _demote_non_nearest_ordered_lower_anchors(
    refs: list[_CandidateRef],
    glass: GlassInspectionConfig,
) -> list[_CandidateRef]:
    """Only the first independently identified interface below Foam may anchor.

    Multiple proposal families may describe the same boundary within a small
    tolerance. Deeper rows remain continuation observations, but cannot create
    a competing Oil component from another bubble, residue or vessel edge.
    """

    anchors = tuple(
        ref
        for ref in refs
        if ref.phase_identity is OilPhaseIdentity.ORDERED_LOWER_INTERFACE
        and ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
    )
    if not anchors:
        return refs
    first_y = min(float(ref.candidate.y) for ref in anchors)
    tolerance = max(
        6.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.25,
    )
    output: list[_CandidateRef] = []
    for ref in refs:
        if (
            ref in anchors
            and float(ref.candidate.y) > first_y + tolerance
        ):
            output.append(
                replace(
                    ref,
                    authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                    initial_authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                    post_track_authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                    authority_reason=AuthorityReason.CONTINUATION,
                    authority_failed_gates=("nearest_ordered_lower_interface",),
                    phase_identity=OilPhaseIdentity.CONTINUATION_ONLY,
                    phase_identity_failed_gates=("nearest_ordered_lower_interface",),
                )
            )
        else:
            output.append(ref)
    return output


def _foam_front_alias_penalty(
    candidate: BoundaryCandidate,
    foam_rows: tuple[float, ...],
    glass: GlassInspectionConfig,
) -> float:
    if not foam_rows:
        return 0.0
    tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.35,
    )
    distance = min(abs(float(candidate.y) - y) for y in foam_rows)
    return 0.52 * _unit(1.0 - distance / tolerance)


def _candidate_optics_opposition(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).optics_opposition


def _candidate_artifact_signature(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).artifact_signature


def _candidate_ambiguity(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    return (evidence or OilCandidateEvidence.from_candidate(candidate)).ambiguity


def _candidate_quality(
    candidate: BoundaryCandidate,
    *,
    evidence: OilCandidateEvidence | None = None,
    terminal_fallback: bool = False,
) -> float:
    evidence = evidence or OilCandidateEvidence.from_candidate(candidate)
    features = candidate.features
    material = evidence.material_support
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    return (
        0.64 * material
        + 0.18 * availability
        - 0.14 * evidence.ambiguity
        - 0.24 * evidence.artifact_signature
        - 0.18 * evidence.static_contradiction
        + (
            0.18
            * (evidence.terminal_support if evidence.material_path else 0.0)
            if terminal_fallback
            else 0.0
        )
        + 0.12 * evidence.registered_motion
    )


def _visible_state(path: tuple[_Node, ...], index: int) -> FillState:
    tracklet_id = _node_tracklet_id(path[index])
    prior_y = next(
        (
            path[offset].y
            for offset in range(index - 1, max(-1, index - 4), -1)
            if path[offset].kind == "oil"
            and _node_tracklet_id(path[offset]) == tracklet_id
        ),
        None,
    )
    next_y = next(
        (
            path[offset].y
            for offset in range(index + 1, min(len(path), index + 4))
            if path[offset].kind == "oil"
            and _node_tracklet_id(path[offset]) == tracklet_id
        ),
        None,
    )
    current_y = path[index].y
    assert current_y is not None
    delta = 0.0
    if prior_y is not None and next_y is not None:
        delta = next_y - prior_y
    elif prior_y is not None:
        delta = current_y - prior_y
    elif next_y is not None:
        delta = next_y - current_y
    if delta < -2.0:
        return FillState.FILLING_VISIBLE
    if delta > 2.0:
        return FillState.DRAINING_VISIBLE
    return FillState.PARTIAL_VISIBLE


def _project_candidates(
    candidates: Iterable[BoundaryCandidate],
    selected_ref: _CandidateRef | None,
    refs: tuple[_CandidateRef, ...],
    evidence_index: OilCandidateEvidenceIndex,
    *,
    material_ownership_barrier: bool = False,
) -> list[BoundaryCandidate]:
    output: list[BoundaryCandidate] = []
    refs_by_offset = {ref.candidate_offset: ref for ref in refs}
    for offset, candidate in enumerate(candidates):
        if candidate.kind is not BoundaryKind.OIL_AIR:
            output.append(candidate)
            continue
        selected = selected_ref is not None and offset == selected_ref.candidate_offset
        ref = refs_by_offset.get(offset)
        if ref is not None:
            # Sequence stages may add evidence to their immutable candidate
            # refs. Preserve both the final evidence and the stage-specific
            # authority needed for exact post-run diagnostics.
            candidate = replace(
                ref.candidate,
                features={
                    **ref.candidate.features,
                    "sequence_top_k": 1.0,
                    "sequence_initial_authority_tier": float(ref.initial_authority),
                    "sequence_post_track_authority_tier": float(
                        ref.post_track_authority
                    ),
                    "sequence_final_authority_tier": float(ref.authority),
                    "sequence_cross_representation_support": float(
                        ref.representation_support
                    ),
                    "sequence_semantic_corridor_support": float(
                        ref.semantic_corridor_support
                    ),
                    "sequence_track_opposition": float(ref.track_opposition),
                    "sequence_effective_track_opposition": float(
                        _effective_track_opposition(ref)
                    ),
                    "sequence_cluster_support": float(ref.cluster_support),
                    "sequence_trajectory_support": float(ref.trajectory_support),
                    "sequence_foam_alias_penalty": float(ref.foam_alias_penalty),
                    "sequence_selected": float(selected),
                    "sequence_authority_reason": ref.authority_reason.value,
                    "sequence_authority_failed_gates": ";".join(
                        ref.authority_failed_gates
                    ),
                    "sequence_foam_material_identity": float(
                        ref.foam_material_identity
                    ),
                    "sequence_phase_identity": ref.phase_identity.value,
                    "sequence_phase_identity_failed_gates": ";".join(
                        ref.phase_identity_failed_gates
                    ),
                    "sequence_ordered_lower": float(ref.ordered_lower),
                    "sequence_tracklet_id": ref.tracklet_id or "",
                    "sequence_row_hypothesis_id": (
                        ref.row_hypothesis_id or ""
                    ),
                    "sequence_tracklet_lifecycle": (
                        ref.tracklet_lifecycle.value
                    ),
                    "sequence_tracklet_admitted": float(
                        ref.tracklet_admitted
                    ),
                    "sequence_tracklet_confirmation_profile": (
                        ref.tracklet_confirmation_profile.value
                    ),
                    "sequence_tracklet_confirmation_support": float(
                        ref.tracklet_confirmation_support
                    ),
                    "sequence_tracklet_net_progress_px": float(
                        ref.tracklet_net_progress_px
                    ),
                    "sequence_tracklet_direction": int(
                        ref.tracklet_direction
                    ),
                    "sequence_tracklet_directional_agreement": float(
                        ref.tracklet_directional_agreement
                    ),
                    "sequence_tracklet_motion_support": float(
                        ref.tracklet_motion_support
                    ),
                    "sequence_tracklet_motion_coverage": float(
                        ref.tracklet_motion_coverage
                    ),
                    "sequence_tracklet_material_conflict": float(
                        ref.tracklet_material_conflict
                    ),
                    "sequence_tracklet_incompatible": float(
                        ref.tracklet_incompatible
                    ),
                    "sequence_tracklet_failure_reason": (
                        ref.tracklet_failure_reason
                    ),
                    "sequence_material_ownership_barrier": float(
                        material_ownership_barrier
                    ),
                    **ref.evidence.availability.as_features(),
                },
            )
        evidence = (
            ref.evidence
            if ref is not None
            else evidence_index.evidence(candidate)
        )
        eligible = _candidate_eligible(candidate, evidence)
        output.append(
            replace(
                candidate,
                selected=selected,
                rejected=not selected,
                reject_reason=(
                    ""
                    if selected
                    else (
                        candidate.reject_reason
                        if candidate.reject_reason.startswith(
                            "calibrated_artifact:"
                        )
                        else (
                            "sequence_candidate_hard_invalid"
                            if not eligible
                            else "not_selected_by_observation_resolver"
                        )
                    )
                ),
            )
        )
    return output


def _frame_tracklet_failure(refs: tuple[_CandidateRef, ...]) -> str:
    tracked = tuple(ref for ref in refs if ref.tracklet_id is not None)
    if not tracked:
        return "NO_ELIGIBLE_ROW_HYPOTHESIS"
    if any(
        ref.tracklet_admitted and not ref.tracklet_incompatible
        for ref in tracked
    ):
        return "TRACKLET_NOT_SELECTED_BY_PATH"
    if any(ref.tracklet_incompatible for ref in tracked):
        return "INCOMPATIBLE_BRANCH"
    owner = max(
        tracked,
        key=lambda ref: (
            int(ref.authority),
            ref.local_quality,
            -float(ref.candidate.y),
            ref.candidate.source,
        ),
    )
    return owner.tracklet_failure_reason or "PROVISIONAL_TRACKLET"


def _hard_unavailable(
    detection: PhaseDetection,
    config: OilObservationResolverConfig,
) -> bool:
    flags = {str(flag).strip().upper() for flag in detection.flags}
    if flags.intersection(_HARD_UNAVAILABLE_FLAGS):
        return True
    mean = _optional_finite(detection.debug_metrics.get("effective_gray_mean"))
    standard_deviation = _optional_finite(
        detection.debug_metrics.get("effective_gray_std")
    )
    dynamic_range = _optional_finite(
        detection.debug_metrics.get("effective_gray_dynamic_range")
    )
    return bool(
        mean is not None
        and standard_deviation is not None
        and dynamic_range is not None
        and mean <= config.black_frame_max_mean
        and standard_deviation <= config.black_frame_max_std
        and dynamic_range <= config.black_frame_max_dynamic_range
    )


def _relative_y(y: float, glass: GlassInspectionConfig) -> float:
    ellipse = glass.geometry.ellipse
    top = float(ellipse.center_y - ellipse.radius_y)
    bottom = float(ellipse.center_y + ellipse.radius_y)
    return _unit((float(y) - top) / max(1.0, bottom - top))


def _tracklet_policy(
    refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
    glass: GlassInspectionConfig,
    config: OilObservationResolverConfig,
    confirmed_initial_state: InitialObservationState | None,
) -> DirectedTrackletPolicy:
    ellipse = glass.geometry.ellipse
    top = float(ellipse.center_y - ellipse.radius_y)
    height = max(1.0, float(ellipse.radius_y) * 2.0)
    maximum_jump = max(
        1.0,
        float(glass.detector_settings.temporal_max_jump_px),
    )
    row_tolerance = max(
        3.0,
        min(
            maximum_jump * 0.50,
            max(
                8.0,
                maximum_jump * 0.375,
                height * config.tracklet_row_hypothesis_ratio,
            ),
        ),
    )
    short_observation = bool(
        refs_by_frame
        and any(
            ref.terminal_fallback
            for refs in refs_by_frame
            for ref in refs
        )
    )
    return DirectedTrackletPolicy(
        geometry_top_y=top,
        geometry_height=height,
        maximum_jump_px=maximum_jump,
        row_hypothesis_tolerance_px=row_tolerance,
        maximum_lost_frames=config.tracklet_maximum_lost_frames,
        confirmation_window_frames=(
            config.tracklet_confirmation_window_frames
        ),
        confirmation_min_observations=(
            config.tracklet_confirmation_min_observations
        ),
        confirmation_min_anchor_frames=1 if short_observation else 3,
        confirmation_min_progress_px=max(
            4.0,
            height * config.tracklet_confirmation_min_progress_ratio,
        ),
        confirmation_min_directional_agreement=(
            config.tracklet_confirmation_min_directional_agreement
        ),
        confirmation_min_motion_support=(
            config.tracklet_confirmation_min_motion_support
        ),
        confirmation_min_motion_coverage=(
            config.tracklet_confirmation_min_motion_coverage
        ),
        continuation_grace_frames=(
            config.tracklet_continuation_grace_frames
        ),
        continuation_min_motion_energy=(
            config.tracklet_continuation_min_motion_energy
        ),
        continuation_min_motion_coverage=(
            config.tracklet_continuation_min_motion_coverage
        ),
        entrance_band_ratio=config.entrance_band_ratio,
        initial_state=confirmed_initial_state,
        ambiguity_margin=config.tracklet_ambiguity_margin,
    )


def _material_phase_policy(
    glass: GlassInspectionConfig,
    config: OilObservationResolverConfig,
    confirmed_initial_state: InitialObservationState | None,
) -> OilMaterialPhasePolicy:
    ellipse = glass.geometry.ellipse
    height = max(1.0, float(ellipse.radius_y) * 2.0)
    return OilMaterialPhasePolicy(
        geometry_top_y=float(ellipse.center_y - ellipse.radius_y),
        geometry_height=height,
        maximum_jump_px=max(
            1.0,
            float(glass.detector_settings.temporal_max_jump_px),
        ),
        maximum_lost_frames=max(
            config.tracklet_maximum_lost_frames,
            config.tracklet_confirmation_window_frames // 2,
        ),
        handoff_ambiguity_margin=config.tracklet_ambiguity_margin,
        handoff_direction_reversal_tolerance_px=max(
            1.0,
            height * config.tracklet_row_hypothesis_ratio,
        ),
        fill_onset_intent_frames=(
            config.tracklet_confirmation_window_frames
        ),
        fill_evidence_window_frames=(
            config.tracklet_confirmation_window_frames
            + config.completed_fill_gap_frames
        ),
        entrance_band_ratio=config.entrance_band_ratio,
        fill_minimum_span_ratio=config.completed_fill_min_span_ratio,
        minimum_directional_agreement=(
            config.tracklet_confirmation_min_directional_agreement
        ),
        empty_entrance_motion_enabled=(
            confirmed_initial_state
            is InitialObservationState.EMPTY_NO_INTERFACE
        ),
        fill_minimum_motion_support=(
            config.tracklet_confirmation_min_motion_support
        ),
        fill_minimum_motion_coverage=(
            config.tracklet_confirmation_min_motion_coverage
        ),
        drain_entrance_ratio=config.completed_fill_release_ratio,
        drain_minimum_progress_ratio=(
            config.completed_fill_release_min_downward_ratio
        ),
        drain_minimum_directional_agreement=(
            config.completed_fill_release_directional_ratio
        ),
        material_conflict_limit=(
            config.completed_fill_material_conflict_min
        ),
    )


def _interface_selector_policy(
    glass: GlassInspectionConfig,
    config: OilObservationResolverConfig,
) -> OilInterfaceSelectorPolicy:
    ellipse = glass.geometry.ellipse
    return OilInterfaceSelectorPolicy(
        geometry_top_y=float(ellipse.center_y - ellipse.radius_y),
        geometry_height=max(1.0, float(ellipse.radius_y) * 2.0),
        maximum_jump_px=max(
            1.0,
            float(glass.detector_settings.temporal_max_jump_px),
        ),
        lookahead_frames=config.tracklet_confirmation_window_frames,
        ambiguity_margin=config.tracklet_ambiguity_margin,
        unknown_transition_cost=config.unknown_transition_cost,
        incompatible_state_transition_cost=(
            config.incompatible_state_transition_cost
        ),
        state_min_evidence=config.state_min_evidence,
        entrance_band_ratio=config.entrance_band_ratio,
    )


def _longest_consecutive(indices: tuple[int, ...]) -> int:
    longest = 0
    current = 0
    prior: int | None = None
    for index in indices:
        current = current + 1 if prior is not None and index == prior + 1 else 1
        longest = max(longest, current)
        prior = index
    return longest


def _qualified_ordinary_semantic_keys(
    detections: tuple[PhaseDetection, ...],
    glass: GlassInspectionConfig,
    *,
    evidence_index: OilCandidateEvidenceIndex,
) -> set[tuple[int, int]]:
    """Find an evidence-seeded ordinary semantic corridor.

    This replaces R6's dependence on the old current-frame ``selected`` bit.
    A weak ordinary row is never authoritative merely because it repeats.
    Three bounded observations must include either two independent seeds or one
    seed plus coherent directional motion. A weak third member cannot inherit
    anchor authority when it contradicts the seeded trend.
    This preserves a faint entering meniscus while preventing a stationary
    glare/cap row from manufacturing authority through persistence alone.
    """

    by_frame: dict[int, tuple[tuple[int, BoundaryCandidate], ...]] = {}
    for frame_offset, detection in enumerate(detections):
        ranked: list[tuple[int, BoundaryCandidate, float, float]] = []
        for candidate_offset, candidate in enumerate(detection.candidates):
            evidence = evidence_index.evidence(candidate)
            if not _ordinary_semantic_candidate(candidate, evidence):
                continue
            ranked.append(
                (
                    candidate_offset,
                    candidate,
                    _ordinary_semantic_rank(candidate, evidence),
                    _ordinary_terminal_peer_support(
                        candidate,
                        detection.candidates,
                        glass,
                        evidence_index=evidence_index,
                    ),
                )
            )
        if ranked:
            backed_rank = max(
                (rank for _offset, _candidate, rank, peer in ranked if peer >= 0.75),
                default=-math.inf,
            )
            ranked = [
                item
                for item in ranked
                if not (
                    item[3] < 0.25
                    and backed_rank >= item[2] - 0.05
                )
            ]
            if not ranked:
                continue
            # Candidate generators intentionally have broad recall.  Building
            # triples from every weak row creates a combinatorial corridor in a
            # small Glass (rim, reflection and meniscus all become connected).
            # Keep a deterministic evidence beam before any temporal reasoning.
            ranked.sort(
                key=lambda item: (
                    -(item[2] + 0.12 * item[3]),
                    float(item[1].y),
                    item[1].source,
                )
            )
            by_frame[frame_offset] = tuple(
                (offset, candidate)
                for offset, candidate, _rank, _peer in ranked[:2]
            )
    if not by_frame:
        return set()

    horizon = max(1, min(2, int(glass.detector_settings.oil_path_window)))
    maximum_jump = max(
        4.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.75,
    )
    qualified: set[tuple[int, int]] = set()
    for first_frame in sorted(by_frame):
        for second_frame in range(
            first_frame + 1,
            min(len(detections), first_frame + horizon + 1),
        ):
            for third_frame in range(
                second_frame + 1,
                min(len(detections), second_frame + horizon + 1),
            ):
                for first_offset, first in by_frame.get(first_frame, ()):
                    for second_offset, second in by_frame.get(second_frame, ()):
                        first_delta = float(second.y) - float(first.y)
                        if abs(first_delta) > maximum_jump * (second_frame - first_frame):
                            continue
                        for third_offset, third in by_frame.get(third_frame, ()):
                            second_delta = float(third.y) - float(second.y)
                            if abs(second_delta) > maximum_jump * (third_frame - second_frame):
                                continue
                            candidates = (first, second, third)
                            frames = (first_frame, second_frame, third_frame)
                            seed_flags = tuple(
                                _ordinary_semantic_seed(
                                    candidate,
                                    evidence_index.evidence(candidate),
                                )
                                for candidate in candidates
                            )
                            seed_count = sum(
                                seed_flags
                            )
                            coherent_motion = bool(
                                seed_count >= 1
                                and abs(first_delta) >= 1.5
                                and abs(second_delta) >= 1.5
                                and first_delta * second_delta > 0.0
                                and abs(float(third.y) - float(first.y)) >= 8.0
                            )
                            weak_follows = bool(
                                seed_count == 2
                                and _weak_member_follows_seed_trend(
                                    candidates,
                                    frames,
                                    seed_flags,
                                    maximum_jump=maximum_jump,
                                )
                            )
                            if seed_count == 2 and not weak_follows:
                                qualified.update(
                                    key
                                    for key, seeded_here in zip(
                                        (
                                            (first_frame, first_offset),
                                            (second_frame, second_offset),
                                            (third_frame, third_offset),
                                        ),
                                        seed_flags,
                                        strict=True,
                                    )
                                    if seeded_here
                                )
                                continue
                            if seed_count < 2 and not coherent_motion:
                                continue
                            qualified.update(
                                (
                                    (first_frame, first_offset),
                                    (second_frame, second_offset),
                                    (third_frame, third_offset),
                                )
                            )

    # Nearby weak rows receive corridor proximity later, but they do not become
    # semantic anchors merely by sitting beside a qualified triple. That former
    # shoulder expansion let one ambiguous shadow inherit anchor authority from
    # two strong neighboring frames.
    return qualified


def _ordinary_terminal_peer_support(
    candidate: BoundaryCandidate,
    candidates: Sequence[BoundaryCandidate],
    glass: GlassInspectionConfig,
    *,
    evidence_index: OilCandidateEvidenceIndex,
) -> float:
    tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.375,
    )
    return max(
        (
            _candidate_terminal_support(
                peer,
                evidence_index.evidence(peer),
            )
            for peer in candidates
            if peer is not candidate
            and _candidate_eligible(peer, evidence_index.evidence(peer))
            and abs(float(peer.y) - float(candidate.y)) <= tolerance
        ),
        default=0.0,
    )


def _weak_member_follows_seed_trend(
    candidates: tuple[BoundaryCandidate, BoundaryCandidate, BoundaryCandidate],
    frames: tuple[int, int, int],
    seed_flags: tuple[bool, bool, bool],
    *,
    maximum_jump: float,
) -> bool:
    """Require the one weak member to agree with the two seeded observations."""

    seeded = tuple(
        (frame, float(candidate.y))
        for frame, candidate, seeded_here in zip(
            frames,
            candidates,
            seed_flags,
            strict=True,
        )
        if seeded_here
    )
    weak = next(
        (frame, float(candidate.y))
        for frame, candidate, seeded_here in zip(
            frames,
            candidates,
            seed_flags,
            strict=True,
        )
        if not seeded_here
    )
    first, second = seeded
    slope = (second[1] - first[1]) / max(1, second[0] - first[0])
    expected = first[1] + slope * (weak[0] - first[0])
    distance = min(abs(weak[0] - first[0]), abs(weak[0] - second[0]))
    tolerance = max(6.0, maximum_jump * 0.35 * max(1, distance))
    return abs(weak[1] - expected) <= tolerance


def _semantic_corridor_support(
    frame_offset: int,
    candidate_y: float,
    semantic_rows: tuple[tuple[int, float], ...],
    glass: GlassInspectionConfig,
) -> float:
    if not semantic_rows:
        return 0.0
    tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.42,
    )

    def proximity(expected: float) -> float:
        return _unit(1.0 - abs(candidate_y - expected) / tolerance)

    same_frame = tuple(y for offset, y in semantic_rows if offset == frame_offset)
    if same_frame:
        return max(proximity(y) for y in same_frame)

    maximum_gap = max(3, int(glass.detector_settings.oil_path_window) * 2)
    prior = next(
        (
            item
            for item in reversed(semantic_rows)
            if item[0] < frame_offset and frame_offset - item[0] <= maximum_gap
        ),
        None,
    )
    following = next(
        (
            item
            for item in semantic_rows
            if item[0] > frame_offset and item[0] - frame_offset <= maximum_gap
        ),
        None,
    )
    if prior is not None and following is not None:
        span = following[0] - prior[0]
        fraction = (frame_offset - prior[0]) / max(1, span)
        expected = prior[1] + fraction * (following[1] - prior[1])
        return proximity(expected)
    nearest = prior if following is None else following
    if nearest is None or abs(frame_offset - nearest[0]) > 2:
        return 0.0
    return proximity(nearest[1])


def _ordinary_semantic_candidate(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> bool:
    evidence = evidence or OilCandidateEvidence.from_candidate(candidate)
    if (
        candidate.kind is not BoundaryKind.OIL_AIR
        or not _finite(candidate.y)
        or evidence.material_path
        or evidence.supplemental
        or not _candidate_eligible(candidate, evidence)
    ):
        return False
    features = candidate.features
    if (
        not evidence.availability.material_texture
        or evidence.material_texture_conflict >= 0.60
    ):
        return False
    if (
        _unit(features.get("sequence_material_layer_topology", 0.0)) >= 0.5
        and _unit(features.get("material_terminal_partition_support", 0.0))
        >= 0.55
    ):
        return False
    boundary = _unit(features.get("boundary_likelihood", candidate.feature_score))
    artifact = _unit(
        features.get(
            "artifact_likelihood",
            candidate.penalties.get("artifact_likelihood", 0.0),
        )
    )
    coverage = _unit(
        features.get(
            "narrow_horizontal_coverage",
            features.get("horizontal_coverage", 0.0),
        )
    )
    return bool(
        evidence.material_support >= 0.30
        and boundary >= 0.26
        and artifact <= 0.76
        and evidence.ambiguity <= 0.68
        and evidence.optics_opposition <= 0.38
        and coverage >= 0.02
    )


def _ordinary_semantic_seed(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> bool:
    """Return localized interface evidence within the ordinary family.

    A broad moving brightness field is common inside a full, turbulent Glass.
    It is not a meniscus seed unless a localized narrow response or a genuinely
    wide cross-ROI boundary accompanies the semantic advantage.
    """

    evidence = evidence or OilCandidateEvidence.from_candidate(candidate)
    if not _ordinary_semantic_candidate(candidate, evidence):
        return False
    features = candidate.features
    boundary = _unit(features.get("boundary_likelihood", candidate.feature_score))
    artifact = _unit(
        features.get(
            "artifact_likelihood",
            candidate.penalties.get("artifact_likelihood", 0.0),
        )
    )
    coverage = _unit(
        features.get(
            "narrow_horizontal_coverage",
            features.get("horizontal_coverage", 0.0),
        )
    )
    broad = _unit(
        features.get("broad_strength", features.get("region_contrast", 0.0))
    )
    narrow = _unit(
        features.get("narrow_peak_strength", features.get("edge_strength", 0.0))
    )
    return bool(
        (
            boundary - artifact >= 0.04
            or (coverage >= 0.38 and broad >= 0.42)
        )
        and (
            narrow >= 0.58
            or (coverage >= 0.50 and broad >= 0.38)
        )
    )


def _ordinary_semantic_rank(
    candidate: BoundaryCandidate,
    evidence: OilCandidateEvidence | None = None,
) -> float:
    """Rank ordinary rows using image evidence, never legacy selection."""

    features = candidate.features
    evidence = evidence or OilCandidateEvidence.from_candidate(candidate)
    boundary = _unit(features.get("boundary_likelihood", candidate.feature_score))
    artifact = _unit(
        features.get(
            "artifact_likelihood",
            candidate.penalties.get("artifact_likelihood", 0.0),
        )
    )
    narrow = _unit(
        features.get("narrow_peak_strength", features.get("edge_strength", 0.0))
    )
    coverage = _unit(
        features.get(
            "narrow_horizontal_coverage",
            features.get("horizontal_coverage", 0.0),
        )
    )
    broad = _unit(
        features.get("broad_strength", features.get("region_contrast", 0.0))
    )
    scale = _unit(features.get("broad_scale_consistency", 0.0))
    terminal = _unit(features.get("material_terminal_partition_support", 0.0))
    return (
        0.40 * boundary
        + 0.16 * narrow
        + 0.12 * coverage
        + 0.12 * broad
        + 0.12 * terminal
        + 0.08 * scale
        - 0.30 * artifact
        - 0.15 * evidence.ambiguity
        - 0.10 * evidence.static_contradiction
    )


def _node_tracklet_id(node: _Node) -> str | None:
    if node.candidate_ref is None:
        return None
    return node.candidate_ref.tracklet_id


def _unknown_node(layer: tuple[_Node, ...]) -> _Node:
    return next(node for node in layer if node.kind == "unknown")


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _optional_finite(value: object) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _unit(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
