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
from .oil_candidate_evidence import OilCandidateEvidence, candidate_is_eligible
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


OIL_OBSERVATION_RESOLVER_VERSION = "r14-phase-component-replacement-v1"

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
    continuation_edge_frames: int = 2
    completed_fill_min_span_ratio: float = 0.20
    completed_fill_gap_frames: int = 6
    completed_fill_release_ratio: float = 0.40
    completed_fill_release_lookahead_frames: int = 6
    completed_fill_release_min_downward_ratio: float = 0.025
    completed_fill_release_directional_ratio: float = 0.60
    trajectory_spike_min_px: float = 8.0
    trajectory_spike_tolerance_ratio: float = 0.25
    trajectory_spike_lookaround_frames: int = 3
    high_recall_candidate_ref_limit: int = 8
    empty_entry_lookahead_frames: int = 6
    empty_entry_min_upward_ratio: float = 0.025
    empty_entry_directional_ratio: float = 0.60


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


@dataclass(frozen=True)
class OilObservationResolution:
    detections: tuple[PhaseDetection, ...]
    diagnostics: OilObservationDiagnostics


class OilObservationResolver:
    """Resolve one image-supported Oil/state observation per sampled frame.

    Initial state is used only in the first-layer prior. FULL/EMPTY emissions
    come only from raw typed no-interface metrics, and every numeric output is
    copied from an explicitly eligible candidate in that same frame.
    """

    version = OIL_OBSERVATION_RESOLVER_VERSION

    def __init__(self, config: OilObservationResolverConfig | None = None) -> None:
        self.config = config or OilObservationResolverConfig()

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
        refs_by_frame, ineligible_count, foam_material_identity = self._candidate_refs(
            source,
            glass,
        )
        refs_by_frame, track_count, maximum_track_opposition = (
            self._apply_track_opposition(refs_by_frame, glass)
        )
        refs_by_frame = self._apply_cluster_and_trajectory_support(
            refs_by_frame,
            glass,
        )
        layers = tuple(
            self._nodes_for_frame(detection, refs_by_frame[index])
            for index, detection in enumerate(source)
        )
        layers = self._admit_initial_empty_entry(
            layers,
            glass,
            confirmed_initial_state,
        )
        best_path = self._best_path(
            layers,
            source,
            glass,
            confirmed_initial_state,
        )
        bounded_path = self._bound_continuation_runs(best_path, layers, glass)
        spike_suppressed_path = self._suppress_trajectory_spikes(
            bounded_path,
            layers,
            glass,
        )
        path = self._suppress_completed_fill_reacquisition(
            spike_suppressed_path,
            layers,
            glass,
        )
        resolved = tuple(
            self._project_detection(
                detection,
                node,
                refs_by_frame[index],
                path,
                (
                    best_path[index],
                    bounded_path[index],
                    spike_suppressed_path[index],
                    path[index],
                ),
                index,
                glass,
                confirmed_initial_state,
            )
            for index, (detection, node) in enumerate(zip(source, path, strict=True))
        )
        counts = {
            kind: sum(node.kind == kind for node in path)
            for kind in ("oil", "full", "empty", "unknown")
        }
        return OilObservationResolution(
            resolved,
            OilObservationDiagnostics(
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
            ),
        )

    def _candidate_refs(
        self,
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
    ) -> tuple[
        tuple[tuple[_CandidateRef, ...], ...],
        int,
        FoamMaterialIdentity,
    ]:
        limit = max(1, int(glass.detector_settings.candidate_top_k))
        rows: list[tuple[_CandidateRef, ...]] = []
        ineligible = 0
        foam_material_identity = track_foam_material_identity(detections, glass)
        semantic_anchor_keys = _qualified_ordinary_semantic_keys(
            detections,
            glass,
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
                representation_support = _cross_representation_support(
                    candidate,
                    oil_candidates,
                    glass,
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
                        local_quality=_candidate_quality(
                            candidate,
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
                if not _candidate_is_calibrated_high_recall(ref.candidate)
            )[:limit]
            if not any(
                _candidate_is_supplemental(ref.candidate)
                and not _candidate_is_calibrated_high_recall(ref.candidate)
                for ref in selected_refs
            ):
                supplemental = next(
                    (
                        ref
                        for ref in refs
                        if _candidate_is_supplemental(ref.candidate)
                        and not _candidate_is_calibrated_high_recall(ref.candidate)
                        and ref not in selected_refs
                    ),
                    None,
                )
                if supplemental is not None:
                    selected_refs.append(supplemental)
            high_recall = [
                ref
                for ref in refs
                if _candidate_is_calibrated_high_recall(ref.candidate)
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

    def _apply_cluster_and_trajectory_support(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[_CandidateRef, ...], ...]:
        anchors = tuple(
            ref
            for refs in refs_by_frame
            for ref in refs
            if ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
        )
        horizon = max(2, min(3, int(glass.detector_settings.oil_path_window)))
        maximum_jump = max(
            1.0,
            float(glass.detector_settings.temporal_max_jump_px),
        )
        # Frame offsets do not encode the sampling rate, so the caller's
        # terminal-fallback bit is the stable bounded-window signal here.
        short_observation = bool(
            refs_by_frame
            and any(ref.terminal_fallback for refs in refs_by_frame for ref in refs)
        )
        minimum_anchor_frames = 1 if short_observation else 2
        qualified = _qualified_anchor_keys(
            anchors,
            frame_count=len(refs_by_frame),
            horizon=horizon,
            maximum_jump=maximum_jump,
            minimum_anchor_frames=minimum_anchor_frames,
        )
        trajectory, component_ids = _trajectory_supported_keys(
            refs_by_frame,
            qualified,
            maximum_jump=maximum_jump,
            minimum_anchor_frames=minimum_anchor_frames,
        )
        output: list[tuple[_CandidateRef, ...]] = []
        for refs in refs_by_frame:
            row: list[_CandidateRef] = []
            for ref in refs:
                key = (ref.frame_offset, ref.candidate_offset)
                row.append(
                    replace(
                        ref,
                        cluster_support=1.0 if key in qualified else 0.0,
                        trajectory_support=1.0 if key in trajectory else 0.0,
                        component_id=component_ids.get(key),
                    )
                )
            output.append(tuple(row))
        return tuple(output)

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
                _candidate_artifact_signature(item.candidate)
                for item in ordered
            ) / len(ordered)
            optics = sum(
                _candidate_optics_opposition(item.candidate)
                for item in ordered
            ) / len(ordered)
            material = sum(
                _candidate_material_support(item.candidate)
                for item in ordered
            ) / len(ordered)
            supplemental_ratio = sum(
                _candidate_is_material_path(item.candidate) for item in ordered
            ) / len(ordered)
            semantic_support = sum(
                item.semantic_corridor_support for item in ordered
            ) / len(ordered)
            semantic_mode_ratio = sum(
                not item.terminal_fallback for item in ordered
            ) / len(ordered)
            registered_motion = sum(
                _candidate_registered_motion(item.candidate)
                for item in ordered
            ) / len(ordered)
            registered_coverage = sum(
                _unit(
                    item.candidate.features.get(
                        "registered_oil_band_motion_coverage",
                        0.0,
                    )
                )
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
                material_path = _candidate_is_material_path(ref.candidate)
                opposed_peer = next(
                    (
                        peer
                        for peer in refs
                        if not material_path
                        and _candidate_is_material_path(peer.candidate)
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
                terminal = _candidate_terminal_support(ref.candidate)
                superior_partition = next(
                    (
                        peer
                        for peer in refs
                        if peer is not ref
                        and _candidate_terminal_support(peer.candidate) >= 0.60
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

    def _nodes_for_frame(
        self,
        detection: PhaseDetection,
        refs: tuple[_CandidateRef, ...],
    ) -> tuple[_Node, ...]:
        if _hard_unavailable(detection, self.config):
            return (_Node("unknown", 1.25, "unknown"),)

        nodes: list[_Node] = [
            _Node(
                "oil",
                _oil_emission(ref),
                f"oil:{ref.candidate.source}:{ref.candidate.y:.6f}",
                ref,
            )
            for ref in refs
            if ref.authority >= OilCandidateAuthority.CONTINUATION_ELIGIBLE
            and (
                not _candidate_is_calibrated_high_recall(ref.candidate)
                or ref.trajectory_support >= 0.99
            )
        ]
        full = _raw_state_evidence(detection, FillState.FULL_NO_INTERFACE)
        empty = _raw_state_evidence(detection, FillState.EMPTY_NO_INTERFACE)
        if full >= self.config.state_min_evidence:
            nodes.append(
                _Node(
                    "full",
                    -0.10 + 1.05 * full,
                    "full",
                    state_evidence=full,
                )
            )
        if empty >= self.config.state_min_evidence:
            nodes.append(
                _Node(
                    "empty",
                    -0.10 + 1.05 * empty,
                    "empty",
                    state_evidence=empty,
                )
            )
        best_quality = max((ref.local_quality for ref in refs), default=0.0)
        ambiguity = _unit(detection.debug_metrics.get("oil_ambiguity_score", 0.0))
        no_interface = _unit(
            detection.debug_metrics.get("oil_no_interface_score", 0.0)
        )
        unknown = 0.12 + 0.34 * ambiguity + 0.08 * no_interface - 0.10 * best_quality
        nodes.append(_Node("unknown", unknown, "unknown"))
        return tuple(nodes)

    def _best_path(
        self,
        layers: tuple[tuple[_Node, ...], ...],
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> tuple[_Node, ...]:
        scores: list[list[float]] = []
        backpointers: list[list[int]] = []
        first_scores = [
            node.emission
            + _initial_score(node, glass, confirmed_initial_state)
            for node in layers[0]
        ]
        scores.append(first_scores)
        backpointers.append([-1] * len(first_scores))
        for frame_offset in range(1, len(layers)):
            prior_layer = layers[frame_offset - 1]
            current_layer = layers[frame_offset]
            dt = max(
                1e-6,
                float(detections[frame_offset].time_sec)
                - float(detections[frame_offset - 1].time_sec),
            )
            current_scores: list[float] = []
            current_backpointers: list[int] = []
            for node in current_layer:
                choices = tuple(
                    (
                        scores[-1][prior_offset]
                        + self._transition_score(prior, node, glass, dt),
                        prior_offset,
                    )
                    for prior_offset, prior in enumerate(prior_layer)
                )
                best_score, best_offset = max(
                    choices,
                    key=lambda item: (
                        item[0],
                        -_node_order(prior_layer[item[1]]),
                    ),
                )
                current_scores.append(best_score + node.emission)
                current_backpointers.append(best_offset)
            scores.append(current_scores)
            backpointers.append(current_backpointers)

        last_offset = max(
            range(len(layers[-1])),
            key=lambda index: (
                scores[-1][index],
                -_node_order(layers[-1][index]),
            ),
        )
        offsets = [last_offset]
        for frame_offset in range(len(layers) - 1, 0, -1):
            offsets.append(backpointers[frame_offset][offsets[-1]])
        offsets.reverse()
        return tuple(
            layers[index][offset]
            for index, offset in enumerate(offsets)
        )

    def _admit_initial_empty_entry(
        self,
        layers: tuple[tuple[_Node, ...], ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> tuple[tuple[_Node, ...], ...]:
        """Keep initial EMPTY Oil provisional until a physical rise enters.

        This is completed-window candidate admission, not a post-publication
        censor.  Position only identifies the lower entrance; bounded upward
        progress distinguishes arriving Oil from a stationary lower structure.
        """

        if confirmed_initial_state is not InitialObservationState.EMPTY_NO_INTERFACE:
            return layers
        entry = _initial_empty_entry_start(layers, glass, self.config)
        output: list[tuple[_Node, ...]] = []
        for index, layer in enumerate(layers):
            if entry is not None and index >= entry:
                output.append(layer)
                continue
            filtered = tuple(node for node in layer if node.kind != "oil")
            output.append(filtered or (_unknown_node(layer),))
        return tuple(output)

    def _bound_continuation_runs(
        self,
        path: tuple[_Node, ...],
        layers: tuple[tuple[_Node, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[_Node, ...]:
        """Keep same-frame observations only inside an anchor-backed run.

        Unlike R6's universal 2--3 frame censor, a continuous candidate path
        may span an arbitrarily long interval *between* qualified anchors.  A
        one-sided tail remains bounded so repetition alone cannot establish or
        reacquire the interface.
        """

        bounded = list(path)
        edge = max(0, int(self.config.continuation_edge_frames))
        minimum_confidence = float(
            glass.detector_settings.minimum_final_confidence
        )
        offset = 0
        while offset < len(path):
            if path[offset].kind != "oil":
                offset += 1
                continue
            start = offset
            component_id = _node_component_id(path[offset])
            while (
                offset + 1 < len(path)
                and path[offset + 1].kind == "oil"
                and _node_component_id(path[offset + 1]) == component_id
            ):
                offset += 1
            end = offset
            qualified = [
                index
                for index in range(start, end + 1)
                if path[index].candidate_ref is not None
                and _independent_anchor(path[index].candidate_ref)
            ]
            if not qualified:
                for index in range(start, end + 1):
                    bounded[index] = _unknown_node(layers[index])
                offset += 1
                continue
            keep_start = max(start, qualified[0] - edge)
            keep_end = min(end, qualified[-1] + edge)
            for index in range(start, end + 1):
                ref = path[index].candidate_ref
                dynamic_extension = _continuous_registered_motion_extension(
                    path,
                    index,
                    qualified,
                    minimum_support=self.config.dynamic_anchor_min_support,
                    minimum_coverage=self.config.dynamic_anchor_min_coverage,
                )
                if (
                    ((index < keep_start or index > keep_end) and not dynamic_extension)
                    or ref is None
                    or ref.trajectory_support < 0.99
                    or _oil_confidence(ref) + 1e-9 < minimum_confidence
                ):
                    bounded[index] = _unknown_node(layers[index])
            offset += 1
        return tuple(bounded)

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
            if abs(following.y - prior.y) > tolerance * 1.5:
                continue
            fraction = (index - prior_index) / (following_index - prior_index)
            expected = prior.y + fraction * (following.y - prior.y)
            if abs(current.y - expected) <= tolerance:
                continue
            neighboring_partition = min(
                _candidate_terminal_support(prior.candidate_ref.candidate),
                _candidate_terminal_support(following.candidate_ref.candidate),
            )
            current_partition = _candidate_terminal_support(
                current.candidate_ref.candidate
            )
            if current_partition + 0.20 >= neighboring_partition:
                continue
            output[index] = _unknown_node(layers[index])
        return tuple(output)

    def _suppress_completed_fill_reacquisition(
        self,
        path: tuple[_Node, ...],
        layers: tuple[tuple[_Node, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[_Node, ...]:
        """Do not reacquire an upper internal texture after a completed fill.

        A same-frame candidate is still required everywhere.  This barrier only
        removes authority after an observed lower-to-upper trajectory reaches
        the entrance and then disappears; it never creates a numeric value or
        a categorical FULL observation. A later boundary well inside the Glass
        releases the barrier and can establish a draining trajectory.
        """

        output = list(path)
        highest_relative = -1.0
        oil_count = 0
        fill_armed = False
        missing = 0
        blocked = False
        release_armed = False
        for index, node in enumerate(path):
            if node.kind == "oil" and node.y is not None:
                relative = _relative_y(node.y, glass)
                if blocked:
                    if (
                        release_armed
                        and self._is_confirmed_downward_reacquisition(
                            path,
                            index,
                            glass,
                        )
                    ):
                        blocked = False
                        highest_relative = relative
                        oil_count = 1
                        fill_armed = False
                        missing = 0
                        release_armed = False
                    else:
                        output[index] = _unknown_node(layers[index])
                        if not release_armed:
                            missing = 0
                    continue
                if fill_armed and relative > self.config.entrance_band_ratio:
                    # Once the observed interface has reached the entrance, a
                    # lower material cap is not a new free interface. Require
                    # a real observation gap before a later drain may reopen
                    # the phase track.
                    blocked = True
                    missing = 0
                    output[index] = _unknown_node(layers[index])
                    continue
                highest_relative = max(highest_relative, relative)
                oil_count += 1
                missing = 0
                if (
                    oil_count >= 3
                    and relative <= self.config.entrance_band_ratio
                    and highest_relative - relative
                    >= self.config.completed_fill_min_span_ratio
                ):
                    fill_armed = True
                continue
            if not fill_armed and not blocked:
                continue
            missing += 1
            if missing >= self.config.completed_fill_gap_frames:
                blocked = True
                release_armed = True
        return tuple(output)

    def _is_confirmed_downward_reacquisition(
        self,
        path: tuple[_Node, ...],
        start: int,
        glass: GlassInspectionConfig,
    ) -> bool:
        """Release a completed-fill barrier only for an emerging drain path.

        A turbulent cap can form a strong, moving upper boundary after the real
        free interface has left the Glass.  Position alone cannot distinguish
        that cap from a missed drain entrance.  A real drain must progress
        downward (increasing image Y) within a small bounded lookahead; this
        check neither creates coordinates nor applies before a completed fill.
        """

        first = path[start]
        if first.y is None:
            return False
        if _relative_y(first.y, glass) > self.config.completed_fill_release_ratio:
            # A drain must re-enter through the physical top of the sight
            # glass. An internal cap that first appears deep in the vessel is
            # not a missed entrance and cannot release the completed-fill
            # barrier merely by wobbling downward for a few frames.
            return False
        stop = min(
            len(path),
            start + max(2, self.config.completed_fill_release_lookahead_frames) + 1,
        )
        observed = [
            float(path[index].y)
            for index in range(start, stop)
            if path[index].kind == "oil" and path[index].y is not None
        ]
        if len(observed) < 3:
            return False
        height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
        minimum_progress = max(
            4.0,
            height * self.config.completed_fill_release_min_downward_ratio,
        )
        deltas = [
            following - prior
            for prior, following in zip(observed, observed[1:])
        ]
        downward_ratio = sum(delta >= 0.0 for delta in deltas) / max(
            1,
            len(deltas),
        )
        return bool(
            observed[-1] - observed[0] >= minimum_progress
            and downward_ratio
            >= self.config.completed_fill_release_directional_ratio
        )

    def _transition_score(
        self,
        prior: _Node,
        current: _Node,
        glass: GlassInspectionConfig,
        dt: float,
    ) -> float:
        if prior.kind == current.kind:
            if current.kind == "oil":
                assert prior.y is not None and current.y is not None
                if _node_component_id(prior) != _node_component_id(current):
                    return float("-inf")
                maximum = max(
                    1.0,
                    float(glass.detector_settings.temporal_max_jump_px),
                )
                time_scale = max(1.0, dt / 0.5)
                normalized = abs(current.y - prior.y) / (maximum * time_scale)
                current_ref = current.candidate_ref
                if (
                    normalized > 1.0
                    and current_ref is not None
                    and _independent_anchor(current_ref)
                ):
                    # A cross-represented phase anchor may reacquire after a
                    # real rapid interface move. Motion/persistence alone never
                    # activates this bounded jump route.
                    return -min(0.30, 0.04 + 0.08 * normalized)
                return 0.22 - (0.12 * normalized + 0.30 * normalized * normalized)
            if current.kind in {"full", "empty"}:
                return 0.10 + 0.14 * current.state_evidence
            return 0.02

        if prior.kind == "unknown" or current.kind == "unknown":
            return -self.config.unknown_transition_cost
        if prior.kind in {"full", "empty"} and current.kind in {"full", "empty"}:
            return -self.config.incompatible_state_transition_cost
        if prior.kind == "oil" and current.kind in {"full", "empty"}:
            if current.state_evidence < self.config.state_min_evidence:
                return -self.config.incompatible_state_transition_cost
            return -_edge_transition_cost(prior, current.kind, glass, self.config)
        if current.kind == "oil" and prior.kind in {"full", "empty"}:
            assert current.candidate_ref is not None
            edge_cost = _edge_transition_cost(
                current,
                prior.kind,
                glass,
                self.config,
            )
            if current.candidate_ref.cluster_support >= 0.99:
                # A missed edge entrance must not lock a confirmed prior for the
                # rest of the video. Independent material anchors can release it
                # from any visible location, with edge proximity still preferred.
                return 0.08 - min(0.45, edge_cost * 0.18)
            return -max(0.35, edge_cost)
        return -0.10

    def _project_detection(
        self,
        detection: PhaseDetection,
        node: _Node,
        refs: tuple[_CandidateRef, ...],
        path: tuple[_Node, ...],
        stage_nodes: tuple[_Node, _Node, _Node, _Node],
        frame_offset: int,
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> PhaseDetection:
        flags = [flag for flag in detection.flags if flag not in _OIL_REPLACED_FLAGS]
        candidates = _project_candidates(
            detection.candidates,
            node.candidate_ref,
            refs,
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
                    else _candidate_terminal_support(node.candidate_ref.candidate)
                ),
                "sequence_terminal_fallback_mode": float(
                    node.candidate_ref is not None
                    and node.candidate_ref.terminal_fallback
                ),
                "sequence_registered_candidate_motion_support": (
                    0.0
                    if node.candidate_ref is None
                    else _candidate_registered_motion(node.candidate_ref.candidate)
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
                "sequence_selected_component_id": (
                    ""
                    if node.candidate_ref is None
                    else node.candidate_ref.component_id or ""
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
                    "R7_RESOLVED_OIL",
                    (
                        "R7_OIL_ANCHOR"
                        if node.candidate_ref.cluster_support >= 0.99
                        else "R7_OIL_CONTINUATION"
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
            flags.extend(("R7_IMAGE_SUPPORTED_STATE", "SEQUENCE_RESOLVED_STATE"))
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
        flags.extend(("R7_OBSERVATION_UNAVAILABLE", "SEQUENCE_UNAVAILABLE"))
        if confirmed_initial_state is not None:
            flags.append("R7_INITIAL_STATE_CONTEXT_ONLY")
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


def _candidate_eligible(candidate: BoundaryCandidate) -> bool:
    return candidate_is_eligible(candidate)


def _cross_representation_support(
    candidate: BoundaryCandidate,
    candidates: tuple[BoundaryCandidate, ...],
    glass: GlassInspectionConfig,
) -> float:
    """Measure same-frame agreement between independent proposal families.

    Material-path rows are deliberately broad.  They gain anchor eligibility
    only when an ordinary phase hypothesis at the same row supplies its own
    material/coverage evidence.  The old selected bit and Foam raster motion
    are not consulted.
    """

    candidate_family = _candidate_representation_family(candidate)
    tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.375,
    )
    support = 0.0
    for peer in candidates:
        if peer is candidate:
            continue
        peer_family = _candidate_representation_family(peer)
        if peer_family == candidate_family or not _candidate_eligible(peer):
            continue
        peer_evidence = OilCandidateEvidence.from_candidate(peer)
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
            0.55 * _candidate_material_support(peer)
            + 0.25 * peer_coverage
            + 0.20 * advantage
        )
        proximity = 0.75 + 0.25 * _unit(1.0 - distance / tolerance)
        support = max(support, evidence * proximity)
    return _unit(support)


def _candidate_material_support(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).material_support


def _candidate_terminal_support(candidate: BoundaryCandidate) -> float:
    evidence = OilCandidateEvidence.from_candidate(candidate)
    return evidence.terminal_support if evidence.material_path else 0.0


def _candidate_static_contradiction(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).static_contradiction


def _candidate_registered_motion(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).registered_motion


def _candidate_registered_motion_coverage(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).registered_motion_coverage


def _candidate_is_material_path(candidate: BoundaryCandidate) -> bool:
    return OilCandidateEvidence.from_candidate(candidate).material_path


def _candidate_is_supplemental(candidate: BoundaryCandidate) -> bool:
    return OilCandidateEvidence.from_candidate(candidate).supplemental


def _candidate_is_calibrated_high_recall(candidate: BoundaryCandidate) -> bool:
    return OilCandidateEvidence.from_candidate(candidate).calibrated_high_recall


def _candidate_representation_family(candidate: BoundaryCandidate) -> str:
    evidence = OilCandidateEvidence.from_candidate(candidate)
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


def _candidate_optics_opposition(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).optics_opposition


def _candidate_artifact_signature(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).artifact_signature


def _candidate_ambiguity(candidate: BoundaryCandidate) -> float:
    return OilCandidateEvidence.from_candidate(candidate).ambiguity


def _candidate_quality(
    candidate: BoundaryCandidate,
    *,
    terminal_fallback: bool = False,
) -> float:
    features = candidate.features
    material = _candidate_material_support(candidate)
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    return (
        0.64 * material
        + 0.18 * availability
        - 0.14 * _candidate_ambiguity(candidate)
        - 0.24 * _candidate_artifact_signature(candidate)
        - 0.18 * _candidate_static_contradiction(candidate)
        + (
            0.18 * _candidate_terminal_support(candidate)
            if terminal_fallback
            else 0.0
        )
        + 0.12 * _candidate_registered_motion(candidate)
    )


def _recurrence_hard_contradiction(ref: _CandidateRef) -> bool:
    """Return whether recurrence may revoke candidate authority.

    Persistence is not physical contradiction: a real interface can remain at
    one level. Hard demotion therefore needs independent candidate-local
    evidence that the row is material, optical or structural noise.
    """

    evidence = OilCandidateEvidence.from_candidate(ref.candidate)
    return bool(
        ref.phase_identity is OilPhaseIdentity.OPPOSED_MATERIAL
        or evidence.material_texture_conflict >= 0.60
        or evidence.artifact_signature >= 0.44
        or evidence.optics_opposition >= 0.46
    )


def _effective_track_opposition(ref: _CandidateRef) -> float:
    """Keep recurrence comparative when no physical contradiction exists."""

    if (
        ref.phase_identity is OilPhaseIdentity.DIRECT_INTERFACE
        and not _recurrence_hard_contradiction(ref)
    ):
        return 0.25 * ref.track_opposition
    return ref.track_opposition


def _independent_anchor(ref: _CandidateRef) -> bool:
    """Return anchors backed by an independent same-frame identity proof.

    A clustered anchor is independently supported by the bounded anchor graph.
    A semantic anchor may also stand alone when a second representation agrees
    strongly in the same frame.  This is deliberately narrower than accepting
    motion or persistence as identity, and lets a real rapid interface move
    reacquire without requiring several pre-existing anchors at its new row.
    """

    if ref.authority is not OilCandidateAuthority.ANCHOR_ELIGIBLE:
        return False
    if ref.cluster_support >= 0.99:
        return True
    evidence = OilCandidateEvidence.from_candidate(ref.candidate)
    return bool(
        evidence.availability.phase
        and ref.representation_support >= 0.50
        and ref.semantic_corridor_support >= 0.99
    )


def _oil_emission(ref: _CandidateRef) -> float:
    candidate = ref.candidate
    features = candidate.features
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    return (
        -0.18
        + 0.62 * _candidate_material_support(candidate)
        + 0.08 * availability
        + (
            0.18
            if ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
            else 0.0
        )
        + 0.34 * ref.cluster_support
        + 0.30 * ref.trajectory_support
        + 0.14 * ref.representation_support
        + 0.24 * ref.semantic_corridor_support
        - 0.65 * _candidate_artifact_signature(candidate)
        - 0.34 * _candidate_static_contradiction(candidate)
        - 0.28 * _candidate_ambiguity(candidate)
        - 0.72 * _effective_track_opposition(ref)
        - ref.foam_alias_penalty
        + (
            0.22 * _candidate_terminal_support(candidate)
            if ref.terminal_fallback
            else 0.0
        )
        + 0.24 * _candidate_registered_motion(candidate)
    )


def _oil_confidence(ref: _CandidateRef) -> float:
    return _unit(
        0.28
        + 0.50 * _candidate_material_support(ref.candidate)
        + 0.16 * ref.cluster_support
        + 0.10 * ref.trajectory_support
        + 0.08 * ref.representation_support
        + 0.08 * ref.semantic_corridor_support
        - 0.20 * _candidate_artifact_signature(ref.candidate)
        - 0.10 * _candidate_static_contradiction(ref.candidate)
        - 0.12 * _candidate_ambiguity(ref.candidate)
        - 0.22 * _effective_track_opposition(ref)
        + (
            0.08 * _candidate_terminal_support(ref.candidate)
            if ref.terminal_fallback
            else 0.0
        )
        + 0.08 * _candidate_registered_motion(ref.candidate)
    )


def _raw_state_evidence(detection: PhaseDetection, state: FillState) -> float:
    key = (
        "oil_no_interface_full_likelihood"
        if state is FillState.FULL_NO_INTERFACE
        else "oil_no_interface_empty_likelihood"
    )
    return _unit(detection.debug_metrics.get(key, 0.0))


def _initial_score(
    node: _Node,
    glass: GlassInspectionConfig,
    confirmed_initial_state: InitialObservationState | None,
) -> float:
    if confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE:
        if node.kind == "full":
            return 0.55
        if node.kind == "empty":
            return -1.0
        if node.kind == "oil" and node.y is not None:
            return 0.18 if _relative_y(node.y, glass) <= 0.27 else -0.18
    if confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE:
        if node.kind == "empty":
            return 0.55
        if node.kind == "full":
            return -1.0
        if node.kind == "oil" and node.y is not None:
            return 0.18 if _relative_y(node.y, glass) >= 0.73 else -0.18
    return 0.06 if node.kind == "unknown" else 0.0


def _initial_empty_entry_start(
    layers: tuple[tuple[_Node, ...], ...],
    glass: GlassInspectionConfig,
    config: OilObservationResolverConfig,
) -> int | None:
    lookahead = max(2, int(config.empty_entry_lookahead_frames))
    height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    minimum_progress = max(4.0, height * config.empty_entry_min_upward_ratio)
    lower_entrance = 1.0 - config.entrance_band_ratio
    for start, layer in enumerate(layers):
        anchors = tuple(
            node
            for node in layer
            if node.kind == "oil"
            and node.y is not None
            and node.candidate_ref is not None
            and _independent_anchor(node.candidate_ref)
            and _relative_y(node.y, glass) >= lower_entrance
        )
        for anchor in anchors:
            component_id = _node_component_id(anchor)
            observed: list[tuple[int, float]] = []
            for frame in range(start, min(len(layers), start + lookahead + 1)):
                compatible = tuple(
                    node
                    for node in layers[frame]
                    if node.kind == "oil"
                    and node.y is not None
                    and _node_component_id(node) == component_id
                )
                if not compatible:
                    continue
                best = max(compatible, key=lambda node: node.emission)
                observed.append((frame, float(best.y)))
            if len(observed) < 3:
                continue
            deltas = [
                following[1] - prior[1]
                for prior, following in zip(observed, observed[1:])
            ]
            upward_ratio = sum(delta <= 0.0 for delta in deltas) / len(deltas)
            if (
                observed[0][1] - observed[-1][1] >= minimum_progress
                and upward_ratio >= config.empty_entry_directional_ratio
            ):
                return start
    return None


def _continuous_registered_motion_extension(
    path: tuple[_Node, ...],
    index: int,
    qualified: list[int],
    *,
    minimum_support: float,
    minimum_coverage: float,
) -> bool:
    if not qualified or qualified[0] <= index <= qualified[-1]:
        return False
    anchor = qualified[0] if index < qualified[0] else qualified[-1]
    start, end = sorted((anchor, index))
    continuation = (
        path[start:end]
        if index < anchor
        else path[start + 1 : end + 1]
    )
    for node in continuation:
        ref = node.candidate_ref
        if (
            node.kind != "oil"
            or ref is None
            or ref.trajectory_support < 0.99
            or _candidate_registered_motion(ref.candidate) < minimum_support
            or _candidate_registered_motion_coverage(ref.candidate) < minimum_coverage
        ):
            return False
    return True


def _edge_transition_cost(
    oil_node: _Node,
    state_kind: str,
    glass: GlassInspectionConfig,
    config: OilObservationResolverConfig,
) -> float:
    assert oil_node.y is not None
    relative = _relative_y(oil_node.y, glass)
    band = config.entrance_band_ratio
    if state_kind == "full":
        overflow = max(0.0, relative - band)
    else:
        overflow = max(0.0, (1.0 - band) - relative)
    if overflow <= 0.0:
        return 0.05
    return 0.35 + 1.8 * overflow


def _visible_state(path: tuple[_Node, ...], index: int) -> FillState:
    prior_y = next(
        (
            path[offset].y
            for offset in range(index - 1, max(-1, index - 4), -1)
            if path[offset].kind == "oil"
        ),
        None,
    )
    next_y = next(
        (
            path[offset].y
            for offset in range(index + 1, min(len(path), index + 4))
            if path[offset].kind == "oil"
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
                    "sequence_component_id": ref.component_id or "",
                    **OilCandidateEvidence.from_candidate(
                        ref.candidate
                    ).availability.as_features(),
                },
            )
        eligible = _candidate_eligible(candidate)
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
            if not _ordinary_semantic_candidate(candidate):
                continue
            ranked.append(
                (
                    candidate_offset,
                    candidate,
                    _ordinary_semantic_rank(candidate),
                    _ordinary_terminal_peer_support(
                        candidate,
                        detection.candidates,
                        glass,
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
                                _ordinary_semantic_seed(candidate)
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
) -> float:
    tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.375,
    )
    return max(
        (
            _candidate_terminal_support(peer)
            for peer in candidates
            if peer is not candidate
            and _candidate_eligible(peer)
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


def _ordinary_semantic_candidate(candidate: BoundaryCandidate) -> bool:
    if (
        candidate.kind is not BoundaryKind.OIL_AIR
        or not _finite(candidate.y)
        or _candidate_is_material_path(candidate)
        or _candidate_is_supplemental(candidate)
        or not _candidate_eligible(candidate)
    ):
        return False
    features = candidate.features
    evidence = OilCandidateEvidence.from_candidate(candidate)
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
        _candidate_material_support(candidate) >= 0.30
        and boundary >= 0.26
        and artifact <= 0.76
        and _candidate_ambiguity(candidate) <= 0.68
        and _candidate_optics_opposition(candidate) <= 0.38
        and coverage >= 0.02
    )


def _ordinary_semantic_seed(candidate: BoundaryCandidate) -> bool:
    """Return localized interface evidence within the ordinary family.

    A broad moving brightness field is common inside a full, turbulent Glass.
    It is not a meniscus seed unless a localized narrow response or a genuinely
    wide cross-ROI boundary accompanies the semantic advantage.
    """

    if not _ordinary_semantic_candidate(candidate):
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


def _ordinary_semantic_rank(candidate: BoundaryCandidate) -> float:
    """Rank ordinary rows using image evidence, never legacy selection."""

    features = candidate.features
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
        - 0.15 * _candidate_ambiguity(candidate)
        - 0.10 * _candidate_static_contradiction(candidate)
    )


def _qualified_anchor_keys(
    anchors: tuple[_CandidateRef, ...],
    *,
    frame_count: int,
    horizon: int,
    maximum_jump: float,
    minimum_anchor_frames: int = 2,
) -> set[tuple[int, int]]:
    """Return anchors that belong to a bounded multi-frame path.

    Candidate order inside a frame is not temporal order.  The R5-style greedy
    grouping treated a second candidate from the same frame as a path break, so
    common top-k rasters fragmented every otherwise valid track.  R7 computes
    forward/backward path support across *different* frames and never connects
    candidates merely because they are adjacent in the flattened list.
    """

    if not anchors:
        return set()
    requested_minimum = max(1, int(minimum_anchor_frames))
    minimum = (
        1
        if requested_minimum == 1
        else 2
        if frame_count <= max(6, horizon * 2)
        else max(3, requested_minimum)
    )
    by_frame: dict[int, tuple[_CandidateRef, ...]] = {}
    for frame_offset in sorted({item.frame_offset for item in anchors}):
        by_frame[frame_offset] = tuple(
            item for item in anchors if item.frame_offset == frame_offset
        )

    forward: dict[tuple[int, int], int] = {}
    for anchor in sorted(
        anchors,
        key=lambda item: (item.frame_offset, float(item.candidate.y)),
    ):
        best = 0
        first = max(0, anchor.frame_offset - horizon * 2)
        for prior_frame in range(first, anchor.frame_offset):
            gap = anchor.frame_offset - prior_frame
            for prior in by_frame.get(prior_frame, ()):
                if (
                    _phase_component_class(anchor)
                    == _phase_component_class(prior)
                    and
                    abs(float(anchor.candidate.y) - float(prior.candidate.y))
                    <= maximum_jump * gap * 0.90
                ):
                    best = max(
                        best,
                        forward.get(
                            (prior.frame_offset, prior.candidate_offset),
                            1,
                        ),
                    )
        forward[(anchor.frame_offset, anchor.candidate_offset)] = best + 1

    backward: dict[tuple[int, int], int] = {}
    for anchor in sorted(
        anchors,
        key=lambda item: (-item.frame_offset, float(item.candidate.y)),
    ):
        best = 0
        last = min(frame_count - 1, anchor.frame_offset + horizon * 2)
        for next_frame in range(anchor.frame_offset + 1, last + 1):
            gap = next_frame - anchor.frame_offset
            for following in by_frame.get(next_frame, ()):
                if (
                    _phase_component_class(anchor)
                    == _phase_component_class(following)
                    and
                    abs(float(anchor.candidate.y) - float(following.candidate.y))
                    <= maximum_jump * gap * 0.90
                ):
                    best = max(
                        best,
                        backward.get(
                            (following.frame_offset, following.candidate_offset),
                            1,
                        ),
                    )
        backward[(anchor.frame_offset, anchor.candidate_offset)] = best + 1

    return {
        key
        for key in forward
        if forward[key] + backward.get(key, 1) - 1 >= minimum
    }


def _trajectory_supported_keys(
    refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
    qualified_anchors: set[tuple[int, int]],
    *,
    maximum_jump: float,
    minimum_anchor_frames: int = 2,
) -> tuple[set[tuple[int, int]], dict[tuple[int, int], str]]:
    """Return candidate keys in a consecutive, anchor-backed graph component.

    Edges cross exactly one sampled frame.  A frame with no candidate therefore
    remains a real gap and cannot be crossed by carried or interpolated state.
    Multiple compatible rows are retained until the global path chooses one.
    """

    eligible_by_frame = tuple(
        tuple(
            ref
            for ref in refs
            if ref.authority >= OilCandidateAuthority.CONTINUATION_ELIGIBLE
        )
        for refs in refs_by_frame
    )
    neighbors: dict[tuple[int, int], set[tuple[int, int]]] = {}
    refs_by_key: dict[tuple[int, int], _CandidateRef] = {}
    for refs in eligible_by_frame:
        for ref in refs:
            key = (ref.frame_offset, ref.candidate_offset)
            refs_by_key[key] = ref
            neighbors.setdefault(key, set())
    for frame_offset in range(1, len(eligible_by_frame)):
        prior_refs = eligible_by_frame[frame_offset - 1]
        current_refs = eligible_by_frame[frame_offset]
        for prior in prior_refs:
            prior_key = (prior.frame_offset, prior.candidate_offset)
            for current in current_refs:
                if (
                    abs(float(current.candidate.y) - float(prior.candidate.y))
                    > maximum_jump
                    or _phase_component_class(current)
                    != _phase_component_class(prior)
                ):
                    continue
                current_key = (current.frame_offset, current.candidate_offset)
                neighbors[prior_key].add(current_key)
                neighbors[current_key].add(prior_key)

    supported: set[tuple[int, int]] = set()
    component_ids: dict[tuple[int, int], str] = {}
    unseen = set(refs_by_key)
    while unseen:
        seed = min(unseen)
        component: set[tuple[int, int]] = set()
        pending = [seed]
        while pending:
            key = pending.pop()
            if key in component:
                continue
            component.add(key)
            unseen.discard(key)
            pending.extend(neighbors.get(key, ()))
        anchor_frames = {
            key[0] for key in component if key in qualified_anchors
        }
        if len(anchor_frames) >= max(1, int(minimum_anchor_frames)):
            supported.update(component)
            owner = min(component)
            component_id = f"oil-component:{owner[0]}:{owner[1]}"
            component_ids.update({key: component_id for key in component})
    return supported, component_ids


def _phase_component_class(ref: _CandidateRef) -> str:
    """Return the physical side of the tracked phase component."""

    return "ordered_lower" if ref.ordered_lower else "direct"


def _node_component_id(node: _Node) -> str | None:
    if node.candidate_ref is None:
        return None
    return node.candidate_ref.component_id


def _node_order(node: _Node) -> int:
    base = {"oil": 0, "full": 1, "empty": 2, "unknown": 3}[node.kind]
    if node.y is None:
        return base * 1_000_000
    return base * 1_000_000 + int(round(node.y * 100.0))


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
