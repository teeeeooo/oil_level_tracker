from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from statistics import median

from .oil_candidate_authority import OilCandidateAuthority
from .oil_sequence_types import (
    OilCandidateRef,
    TrackletConfirmationProfile,
    TrackletLifecycle,
)


@dataclass(frozen=True)
class DirectedTrackletPolicy:
    geometry_top_y: float
    geometry_height: float
    maximum_jump_px: float
    row_hypothesis_tolerance_px: float
    maximum_lost_frames: int
    confirmation_window_frames: int
    confirmation_min_observations: int
    confirmation_min_anchor_frames: int
    confirmation_min_progress_px: float
    confirmation_min_directional_agreement: float
    confirmation_min_motion_support: float
    confirmation_min_motion_coverage: float
    continuation_grace_frames: int
    continuation_min_motion_energy: float
    continuation_min_motion_coverage: float
    ambiguity_margin: float = 0.08

    def __post_init__(self) -> None:
        if not math.isfinite(self.geometry_top_y):
            raise ValueError("Tracklet geometry top must be finite.")
        if not math.isfinite(self.geometry_height) or self.geometry_height <= 0.0:
            raise ValueError("Tracklet geometry height must be finite and positive.")
        if self.maximum_jump_px <= 0.0:
            raise ValueError("Tracklet maximum jump must be positive.")
        if self.row_hypothesis_tolerance_px <= 0.0:
            raise ValueError("Tracklet row tolerance must be positive.")
        if self.maximum_lost_frames < 0:
            raise ValueError("Tracklet lost-frame bound cannot be negative.")
        if self.confirmation_window_frames < 2:
            raise ValueError("Tracklet confirmation window must contain two frames.")
        if self.confirmation_min_observations < 2:
            raise ValueError("Tracklet confirmation needs two observations.")
        if self.confirmation_min_observations > self.confirmation_window_frames:
            raise ValueError("Tracklet observations must fit the confirmation window.")
        if self.confirmation_min_anchor_frames < 1:
            raise ValueError("Tracklet confirmation needs a positive anchor count.")
        for name, value in (
            (
                "directional agreement",
                self.confirmation_min_directional_agreement,
            ),
            ("motion coverage", self.confirmation_min_motion_coverage),
            ("continuation coverage", self.continuation_min_motion_coverage),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Tracklet {name} must be in [0, 1].")
        for name, value in (
            ("confirmation progress", self.confirmation_min_progress_px),
            ("confirmation motion", self.confirmation_min_motion_support),
            ("continuation motion", self.continuation_min_motion_energy),
            ("ambiguity margin", self.ambiguity_margin),
        ):
            if value < 0.0 or not math.isfinite(value):
                raise ValueError(f"Tracklet {name} must be finite and non-negative.")
        if self.continuation_grace_frames < 0:
            raise ValueError("Tracklet continuation grace cannot be negative.")


@dataclass(frozen=True)
class TrackletSummary:
    tracklet_id: str
    phase_class: str
    start_frame: int
    last_observed_frame: int
    observation_count: int
    confirmed_frame: int | None
    confirmation_profile: TrackletConfirmationProfile
    final_lifecycle: TrackletLifecycle
    lifecycle_history: tuple[TrackletLifecycle, ...]
    lost_event_count: int
    termination_reason: str


@dataclass(frozen=True)
class DirectedTrackletResult:
    refs_by_frame: tuple[tuple[OilCandidateRef, ...], ...]
    summaries: tuple[TrackletSummary, ...]
    incompatible_frames: frozenset[int]
    hypothesis_count: int
    comparison_count: int
    maximum_active_tracklets: int
    maximum_eligible_refs_per_frame: int
    maximum_hypotheses_per_frame: int
    lost_event_count: int
    terminated_tracklet_count: int

    @property
    def confirmed_tracklet_count(self) -> int:
        return sum(item.confirmed_frame is not None for item in self.summaries)

    @property
    def provisional_tracklet_count(self) -> int:
        return sum(item.confirmed_frame is None for item in self.summaries)


@dataclass(frozen=True)
class _RowHypothesis:
    identity: str
    frame_offset: int
    representation_classes: frozenset[str]
    source_families: frozenset[str]
    y: float
    members: tuple[OilCandidateRef, ...]
    local_quality: float
    anchor_signal: bool
    has_physical_proposal: bool
    motion_support: float
    motion_coverage: float
    material_conflict: float


@dataclass
class _TrackObservation:
    hypothesis: _RowHypothesis
    incompatible: bool = False
    lifecycle: TrackletLifecycle = TrackletLifecycle.PROVISIONAL
    admitted: bool = False
    confirmation_profile: TrackletConfirmationProfile = (
        TrackletConfirmationProfile.NONE
    )
    confirmation_support: float = 0.0
    net_progress_px: float = 0.0
    direction: int = 0
    directional_agreement: float = 0.0
    motion_support: float = 0.0
    motion_energy: float = 0.0
    motion_coverage: float = 0.0
    material_conflict: float = 0.0
    failure_reason: str = "PROVISIONAL_TRACKLET"
    confirmation_start_frame: int | None = None
    confirmation_end_frame: int | None = None
    confirmation_observation_count: int = 0


@dataclass(eq=False)
class _TrackState:
    identity: str
    representation_classes: frozenset[str]
    observations: list[_TrackObservation]
    lost_event_count: int = 0
    confirmed: bool = False
    terminated: bool = False
    termination_reason: str = ""
    # Each bounded end offset is evaluated once after the track observations
    # for that offset are known.  The cache keeps confirmation/recent witness
    # consumers from replaying the same window during finalization,
    # diagnostics and projection.
    window_evidence_cache: dict[int, _WindowEvidence] = field(
        default_factory=dict
    )

    @property
    def last(self) -> _TrackObservation:
        return self.observations[-1]


@dataclass(frozen=True)
class _WindowEvidence:
    start_observation: int
    end_observation: int
    observation_count: int
    net_progress_px: float
    direction: int
    directional_agreement: float
    motion_support: float
    motion_energy: float
    motion_coverage: float
    material_conflict: float
    anchor_frames: int
    profile: TrackletConfirmationProfile
    confirmation_support: float


_AssignmentPair = tuple[float, str, str, _TrackState, _RowHypothesis]


class DirectedInterfaceTrackletBuilder:
    """Build bounded directed identities without merge/split inheritance.

    Candidate connectivity is not physical identity. This owner first groups
    same-frame alternatives that describe one row, then performs deterministic
    one-to-one matching against only the bounded active tracklet set. Ambiguous
    many-to-one or one-to-many matches terminate the affected identity and mark
    the branch frame incompatible instead of silently hopping branches.
    """

    def __init__(self, policy: DirectedTrackletPolicy) -> None:
        self.policy = policy

    def resolve(
        self,
        refs_by_frame: tuple[tuple[OilCandidateRef, ...], ...],
    ) -> DirectedTrackletResult:
        tracks: list[_TrackState] = []
        active: list[_TrackState] = []
        incompatible_frames: set[int] = set()
        hypothesis_count = 0
        comparison_count = 0
        maximum_active = 0
        maximum_eligible_refs = 0
        maximum_hypotheses = 0
        next_tracklet = 0

        for frame_offset, refs in enumerate(refs_by_frame):
            hypotheses = self._row_hypotheses(frame_offset, refs)
            hypothesis_count += len(hypotheses)
            maximum_eligible_refs = max(
                maximum_eligible_refs,
                sum(
                    ref.authority
                    >= OilCandidateAuthority.CONTINUATION_ELIGIBLE
                    for ref in refs
                ),
            )
            maximum_hypotheses = max(maximum_hypotheses, len(hypotheses))
            retained = [
                track
                for track in active
                if not track.terminated
                and frame_offset
                - track.last.hypothesis.frame_offset
                - 1
                <= self.policy.maximum_lost_frames
            ]
            for track in active:
                if track not in retained and not track.terminated:
                    track.terminated = True
                    track.termination_reason = "LOST_BOUND_EXCEEDED"
            active = retained
            maximum_active = max(maximum_active, len(active))

            pairs: list[tuple[float, str, str, _TrackState, _RowHypothesis]] = []
            for track in active:
                for hypothesis in hypotheses:
                    comparison_count += 1
                    cost = self._match_cost(track, hypothesis)
                    if cost is None:
                        continue
                    pairs.append(
                        (
                            cost,
                            track.identity,
                            hypothesis.identity,
                            track,
                            hypothesis,
                        )
                    )

            conflicted_tracks, conflicted_hypotheses = self._ambiguities(pairs)
            if conflicted_tracks or conflicted_hypotheses:
                incompatible_frames.add(frame_offset)
            for track in conflicted_tracks:
                track.terminated = True
                track.termination_reason = "AMBIGUOUS_BRANCH"

            assigned_tracks: set[str] = set()
            assigned_hypotheses: set[str] = set()
            ordered_pairs = self._ordered_assignment_pairs(
                pairs,
                conflicted_hypotheses,
            )
            for _cost, _track_id, _hypothesis_id, track, hypothesis in ordered_pairs:
                if (
                    track.terminated
                    or track.identity in assigned_tracks
                    or hypothesis.identity in assigned_hypotheses
                    or hypothesis.identity in conflicted_hypotheses
                ):
                    continue
                track.observations.append(_TrackObservation(hypothesis))
                track.representation_classes = (
                    track.representation_classes
                    | hypothesis.representation_classes
                )
                self._refresh_confirmation(track)
                assigned_tracks.add(track.identity)
                assigned_hypotheses.add(hypothesis.identity)

            for track in active:
                if track.terminated or track.identity in assigned_tracks:
                    continue
                track.lost_event_count += 1

            for hypothesis in hypotheses:
                if hypothesis.identity in assigned_hypotheses:
                    continue
                identity = (
                    f"oil-tracklet:{frame_offset:06d}:{next_tracklet:04d}"
                )
                next_tracklet += 1
                track = _TrackState(
                    identity=identity,
                    representation_classes=(
                        hypothesis.representation_classes
                    ),
                    observations=[
                        _TrackObservation(
                            hypothesis,
                            incompatible=(
                                hypothesis.identity in conflicted_hypotheses
                            ),
                            failure_reason=(
                                "INCOMPATIBLE_BRANCH"
                                if hypothesis.identity in conflicted_hypotheses
                                else "PROVISIONAL_TRACKLET"
                            ),
                        )
                    ],
                )
                tracks.append(track)
                active.append(track)
            active = [track for track in active if not track.terminated]
            maximum_active = max(maximum_active, len(active))

        for track in active:
            if not track.terminated:
                track.terminated = True
                track.termination_reason = "WINDOW_END"
        for track in tracks:
            self._finalize_track(track)

        updates: dict[tuple[int, int], OilCandidateRef] = {}
        for track in tracks:
            for observation_offset, observation in enumerate(track.observations):
                hypothesis = observation.hypothesis
                recent_evidence = self._cached_confirmation_evidence(
                    track,
                    observation_offset,
                )
                recent_window_ready = (
                    recent_evidence.observation_count
                    >= self.policy.confirmation_min_observations
                )
                for member in hypothesis.members:
                    key = (member.frame_offset, member.candidate_offset)
                    updates[key] = replace(
                        member,
                        cluster_support=float(
                            observation.admitted
                            and member.authority
                            is OilCandidateAuthority.ANCHOR_ELIGIBLE
                        ),
                        trajectory_support=float(observation.admitted),
                        tracklet_id=track.identity,
                        row_hypothesis_id=hypothesis.identity,
                        tracklet_lifecycle=observation.lifecycle,
                        tracklet_admitted=observation.admitted,
                        tracklet_confirmation_profile=(
                            observation.confirmation_profile
                        ),
                        tracklet_confirmation_support=(
                            observation.confirmation_support
                        ),
                        tracklet_net_progress_px=observation.net_progress_px,
                        tracklet_direction=observation.direction,
                        tracklet_directional_agreement=(
                            observation.directional_agreement
                        ),
                        tracklet_recent_net_progress_px=(
                            recent_evidence.net_progress_px
                            if recent_window_ready
                            else observation.net_progress_px
                        ),
                        tracklet_recent_direction=(
                            recent_evidence.direction
                            if recent_window_ready
                            else observation.direction
                        ),
                        tracklet_recent_directional_agreement=(
                            recent_evidence.directional_agreement
                            if recent_window_ready
                            else observation.directional_agreement
                        ),
                        tracklet_confirmation_start_frame=(
                            observation.confirmation_start_frame
                        ),
                        tracklet_confirmation_end_frame=(
                            observation.confirmation_end_frame
                        ),
                        tracklet_confirmation_observation_count=(
                            observation.confirmation_observation_count
                        ),
                        tracklet_recent_window_end_frame=hypothesis.frame_offset,
                        tracklet_motion_support=observation.motion_support,
                        tracklet_motion_coverage=observation.motion_coverage,
                        tracklet_material_conflict=(
                            observation.material_conflict
                        ),
                        tracklet_incompatible=observation.incompatible,
                        tracklet_failure_reason=observation.failure_reason,
                    )

        output = tuple(
            tuple(
                updates.get(
                    (ref.frame_offset, ref.candidate_offset),
                    replace(
                        ref,
                        tracklet_failure_reason="INSUFFICIENT_AUTHORITY",
                    ),
                )
                for ref in refs
            )
            for refs in refs_by_frame
        )
        summaries = tuple(
            TrackletSummary(
                tracklet_id=track.identity,
                phase_class="+".join(sorted(track.representation_classes)),
                start_frame=track.observations[0].hypothesis.frame_offset,
                last_observed_frame=track.last.hypothesis.frame_offset,
                observation_count=len(track.observations),
                confirmed_frame=next(
                    (
                        item.hypothesis.frame_offset
                        for item in track.observations
                        if item.lifecycle is TrackletLifecycle.CONFIRMED
                    ),
                    None,
                ),
                confirmation_profile=next(
                    (
                        item.confirmation_profile
                        for item in track.observations
                        if item.confirmation_profile
                        is not TrackletConfirmationProfile.NONE
                    ),
                    TrackletConfirmationProfile.NONE,
                ),
                final_lifecycle=TrackletLifecycle.TERMINATED,
                lifecycle_history=_lifecycle_history(track),
                lost_event_count=track.lost_event_count,
                termination_reason=track.termination_reason,
            )
            for track in tracks
        )
        return DirectedTrackletResult(
            refs_by_frame=output,
            summaries=summaries,
            incompatible_frames=frozenset(incompatible_frames),
            hypothesis_count=hypothesis_count,
            comparison_count=comparison_count,
            maximum_active_tracklets=maximum_active,
            maximum_eligible_refs_per_frame=maximum_eligible_refs,
            maximum_hypotheses_per_frame=maximum_hypotheses,
            lost_event_count=sum(item.lost_event_count for item in tracks),
            terminated_tracklet_count=len(tracks),
        )

    def _row_hypotheses(
        self,
        frame_offset: int,
        refs: tuple[OilCandidateRef, ...],
    ) -> tuple[_RowHypothesis, ...]:
        eligible = sorted(
            (
                ref
                for ref in refs
                if ref.authority
                >= OilCandidateAuthority.CONTINUATION_ELIGIBLE
            ),
            key=lambda ref: (
                float(ref.candidate.y),
                ref.candidate.source,
                -ref.local_quality,
                ref.candidate_offset,
            ),
        )
        groups: list[list[OilCandidateRef]] = []
        for ref in eligible:
            if not groups:
                groups.append([ref])
                continue
            group = groups[-1]
            rows = tuple(float(item.candidate.y) for item in group)
            span = max(max(rows), float(ref.candidate.y)) - min(
                min(rows),
                float(ref.candidate.y),
            )
            if span <= self.policy.row_hypothesis_tolerance_px:
                group.append(ref)
            else:
                groups.append([ref])

        hypotheses: list[_RowHypothesis] = []
        for ordinal, members in enumerate(groups):
            ordered = tuple(
                sorted(
                    members,
                    key=lambda ref: (
                        -int(ref.authority),
                        -ref.local_quality,
                        float(ref.candidate.y),
                        ref.candidate.source,
                        ref.candidate_offset,
                    ),
                )
            )
            hypotheses.append(
                _RowHypothesis(
                    identity=f"oil-row:{frame_offset:06d}:{ordinal:03d}",
                    frame_offset=frame_offset,
                    representation_classes=frozenset(
                        _phase_class(ref) for ref in ordered
                    ),
                    source_families=frozenset(
                        _source_family(ref.candidate.source)
                        for ref in ordered
                    ),
                    y=float(median(float(ref.candidate.y) for ref in ordered)),
                    members=ordered,
                    local_quality=max(ref.local_quality for ref in ordered),
                    anchor_signal=any(
                        ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                        for ref in ordered
                    ),
                    has_physical_proposal=any(
                        not ref.evidence.calibrated_high_recall
                        for ref in ordered
                    ),
                    motion_support=max(
                        ref.evidence.registered_motion for ref in ordered
                    ),
                    motion_coverage=max(
                        ref.evidence.registered_motion_coverage
                        for ref in ordered
                    ),
                    material_conflict=min(
                        (
                            ref.evidence.material_texture_conflict
                            for ref in ordered
                            if ref.evidence.availability.material_texture
                        ),
                        default=0.0,
                    ),
                )
            )
        return tuple(hypotheses)

    def _match_cost(
        self,
        track: _TrackState,
        hypothesis: _RowHypothesis,
    ) -> float | None:
        last = track.last.hypothesis
        gap = hypothesis.frame_offset - last.frame_offset
        if gap < 1 or gap - 1 > self.policy.maximum_lost_frames:
            return None
        maximum = self.policy.maximum_jump_px * gap
        position_delta = hypothesis.y - last.y
        if abs(position_delta) > maximum:
            return None
        velocity = _track_velocity(track)
        expected = last.y + velocity * gap
        absolute_prediction_error = abs(hypothesis.y - expected)
        if absolute_prediction_error > self.policy.maximum_jump_px:
            return None
        representation_overlap = bool(
            last.representation_classes
            & hypothesis.representation_classes
        )
        if (
            not representation_overlap
            and not self._representation_bridge(
                track,
                hypothesis,
                absolute_prediction_error=absolute_prediction_error,
            )
        ):
            return None
        prediction_error = absolute_prediction_error / maximum
        position_error = abs(position_delta) / maximum
        reversal = 0.0
        if (
            abs(velocity) >= self.policy.row_hypothesis_tolerance_px / 2.0
            and abs(position_delta) >= self.policy.row_hypothesis_tolerance_px
            and velocity * position_delta < 0.0
        ):
            reversal = 0.30
        quality_relief = 0.04 * max(0.0, hypothesis.local_quality)
        representation_penalty = 0.0 if representation_overlap else 0.05
        return (
            0.72 * prediction_error
            + 0.28 * position_error
            + reversal
            + representation_penalty
            - quality_relief
        )

    def _representation_bridge(
        self,
        track: _TrackState,
        hypothesis: _RowHypothesis,
        *,
        absolute_prediction_error: float,
    ) -> bool:
        last_classes = track.last.hypothesis.representation_classes
        current_classes = hypothesis.representation_classes
        required = last_classes | current_classes
        _start, recent = _bounded_observation_window(
            track.observations,
            len(track.observations) - 1,
            self.policy.confirmation_window_frames,
        )
        if any(
            required <= item.hypothesis.representation_classes
            for item in recent
        ):
            return True
        strict_geometry = absolute_prediction_error <= max(
            1.0,
            self.policy.row_hypothesis_tolerance_px / 3.0,
        )
        independent_witness = bool(
            hypothesis.anchor_signal
            and hypothesis.has_physical_proposal
            and hypothesis.motion_support
            >= self.policy.confirmation_min_motion_support
            and hypothesis.motion_coverage
            >= self.policy.confirmation_min_motion_coverage
        )
        shared_provenance = bool(
            track.last.hypothesis.source_families
            & hypothesis.source_families
        )
        bounded_anchor_correction = bool(
            independent_witness
            and shared_provenance
            and abs(hypothesis.y - track.last.hypothesis.y)
            <= self.policy.maximum_jump_px
            * max(1, hypothesis.frame_offset - track.last.hypothesis.frame_offset)
        )
        return bool(
            (strict_geometry or bounded_anchor_correction)
            and independent_witness
            and shared_provenance
        )

    def _ambiguities(
        self,
        pairs: list[tuple[float, str, str, _TrackState, _RowHypothesis]],
    ) -> tuple[set[_TrackState], set[str]]:
        by_hypothesis: dict[str, list[tuple[float, _TrackState, _RowHypothesis]]] = {}
        by_track: dict[str, list[tuple[float, _TrackState, _RowHypothesis]]] = {}
        for cost, _track_id, _hypothesis_id, track, hypothesis in pairs:
            by_hypothesis.setdefault(hypothesis.identity, []).append(
                (cost, track, hypothesis)
            )
            by_track.setdefault(track.identity, []).append(
                (cost, track, hypothesis)
            )
        conflicted_track_ids: set[str] = set()
        conflicted_hypotheses: set[str] = set()
        for values in by_hypothesis.values():
            established = tuple(
                item for item in values if self._established(item[1])
            )
            ordered = sorted(
                established,
                key=lambda item: (item[0], item[1].identity),
            )
            if len(ordered) < 2:
                continue
            first, second = ordered[:2]
            if second[0] - first[0] <= self.policy.ambiguity_margin:
                conflicted_track_ids.update((first[1].identity, second[1].identity))
                conflicted_hypotheses.add(first[2].identity)
        # Apply the same ambiguity contract in the opposite direction.  A row
        # that has another clear predecessor is not a child of this parent;
        # without that reciprocal check, two nearby physical tracks look like
        # a false split and both are unnecessarily terminated.
        for values in by_track.values():
            track = values[0][1]
            if not self._established(track):
                continue
            preferred = tuple(
                item
                for item in values
                if self._clear_hypothesis_predecessor(
                    track,
                    by_hypothesis[item[2].identity],
                )
            )
            ordered = sorted(
                preferred,
                key=lambda item: (item[0], item[2].identity),
            )
            if len(ordered) < 2:
                continue
            first, second = ordered[:2]
            if second[0] - first[0] > self.policy.ambiguity_margin:
                continue
            conflicted_track_ids.add(track.identity)
            conflicted_hypotheses.update(
                hypothesis.identity
                for cost, _track, hypothesis in ordered
                if cost - first[0] <= self.policy.ambiguity_margin
            )
        tracks = {
            track
            for values in (*by_hypothesis.values(), *by_track.values())
            for _cost, track, _hypothesis in values
            if track.identity in conflicted_track_ids
        }
        return tracks, conflicted_hypotheses

    def _ordered_assignment_pairs(
        self,
        pairs: list[_AssignmentPair],
        conflicted_hypotheses: set[str],
    ) -> tuple[_AssignmentPair, ...]:
        established_first = self._established_first_pairs(pairs)
        assignments = self._greedy_assignments(
            established_first,
            conflicted_hypotheses,
        )
        by_hypothesis = self._pairs_by_hypothesis(pairs)
        reserved_predecessor = self._reciprocal_exchange_reservations(
            assignments,
            by_hypothesis,
        )
        if not reserved_predecessor:
            return established_first
        eligible = tuple(
            pair
            for pair in pairs
            if reserved_predecessor.get(pair[2], pair[1]) == pair[1]
        )
        return tuple(
            sorted(
                eligible,
                key=lambda item: (
                    -int(reserved_predecessor.get(item[2]) == item[1]),
                    -int(self._established(item[3])),
                    item[0],
                    item[1],
                    item[2],
                ),
            )
        )

    def _established_first_pairs(
        self,
        pairs: list[_AssignmentPair],
    ) -> tuple[_AssignmentPair, ...]:
        return tuple(
            sorted(
                pairs,
                key=lambda item: (
                    -int(self._established(item[3])),
                    item[0],
                    item[1],
                    item[2],
                ),
            )
        )

    def _pairs_by_hypothesis(
        self,
        pairs: list[_AssignmentPair],
    ) -> dict[str, list[tuple[float, _TrackState, _RowHypothesis]]]:
        indexed: dict[
            str,
            list[tuple[float, _TrackState, _RowHypothesis]],
        ] = {}
        for cost, _track_id, _hypothesis_id, track, hypothesis in pairs:
            indexed.setdefault(hypothesis.identity, []).append(
                (cost, track, hypothesis)
            )
        return indexed

    def _reciprocal_exchange_reservations(
        self,
        assignments: tuple[_AssignmentPair, ...],
        by_hypothesis: dict[
            str,
            list[tuple[float, _TrackState, _RowHypothesis]],
        ],
    ) -> dict[str, str]:
        reserved_predecessor: dict[str, str] = {}
        assignment_by_track = {pair[1]: pair for pair in assignments}
        for established_pair in assignments:
            established = established_pair[3]
            if not self._established(established):
                continue
            claimed_hypothesis = established_pair[4]
            for _cost, predecessor, _hypothesis in by_hypothesis[
                claimed_hypothesis.identity
            ]:
                residual = assignment_by_track.get(predecessor.identity)
                if (
                    self._established(predecessor)
                    or residual is None
                    or residual[2] == claimed_hypothesis.identity
                    or not claimed_hypothesis.has_physical_proposal
                    or not residual[4].has_physical_proposal
                    or not self._clear_hypothesis_predecessor(
                        predecessor,
                        by_hypothesis[claimed_hypothesis.identity],
                    )
                    or not self._clear_hypothesis_predecessor(
                        established,
                        by_hypothesis[residual[2]],
                    )
                ):
                    continue
                # The established-first assignment crossed two independently
                # clear child-to-predecessor edges. Reserve the complete swap;
                # a lone provisional best edge may not evict an established
                # identity or create an unmatched residual branch.
                if (
                    claimed_hypothesis.identity in reserved_predecessor
                    or residual[2] in reserved_predecessor
                    or predecessor.identity in reserved_predecessor.values()
                    or established.identity in reserved_predecessor.values()
                ):
                    continue
                reserved_predecessor[claimed_hypothesis.identity] = (
                    predecessor.identity
                )
                reserved_predecessor[residual[2]] = established.identity
        return reserved_predecessor

    def _greedy_assignments(
        self,
        ordered_pairs: tuple[_AssignmentPair, ...],
        conflicted_hypotheses: set[str],
    ) -> tuple[_AssignmentPair, ...]:
        assigned_tracks: set[str] = set()
        assigned_hypotheses: set[str] = set()
        assignments = []
        for pair in ordered_pairs:
            _cost, track_id, hypothesis_id, track, _hypothesis = pair
            if (
                track.terminated
                or track_id in assigned_tracks
                or hypothesis_id in assigned_hypotheses
                or hypothesis_id in conflicted_hypotheses
            ):
                continue
            assignments.append(pair)
            assigned_tracks.add(track_id)
            assigned_hypotheses.add(hypothesis_id)
        return tuple(assignments)

    def _clear_hypothesis_predecessor(
        self,
        track: _TrackState,
        predecessors: list[tuple[float, _TrackState, _RowHypothesis]],
    ) -> bool:
        ordered = sorted(
            predecessors,
            key=lambda item: (item[0], item[1].identity),
        )
        if ordered[0][1] is not track:
            return False
        return bool(
            len(ordered) == 1
            or ordered[1][0] - ordered[0][0]
            > self.policy.ambiguity_margin
        )

    def _established(self, track: _TrackState) -> bool:
        return track.confirmed

    def _refresh_confirmation(self, track: _TrackState) -> None:
        if track.confirmed:
            return
        evidence = self._cached_confirmation_evidence(
            track,
            len(track.observations) - 1,
        )
        track.confirmed = (
            evidence.profile is not TrackletConfirmationProfile.NONE
        )

    def _finalize_track(self, track: _TrackState) -> None:
        confirmation_offset: int | None = None
        witness: _WindowEvidence | None = None
        for offset in range(len(track.observations)):
            evidence = self._cached_confirmation_evidence(track, offset)
            if evidence.profile is TrackletConfirmationProfile.NONE:
                continue
            confirmation_offset = offset
            witness = evidence
            break

        if confirmation_offset is None or witness is None:
            reason = self._track_failure_reason(track)
            measured = self._best_failure_evidence(track)
            for observation in track.observations:
                if not observation.incompatible:
                    observation.failure_reason = reason
                    observation.confirmation_support = (
                        measured.confirmation_support
                    )
                    observation.net_progress_px = measured.net_progress_px
                    observation.direction = measured.direction
                    observation.directional_agreement = (
                        measured.directional_agreement
                    )
                    observation.motion_support = measured.motion_support
                    observation.motion_energy = measured.motion_energy
                    observation.motion_coverage = measured.motion_coverage
                    observation.material_conflict = measured.material_conflict
            return

        witness_offsets = range(
            witness.start_observation,
            confirmation_offset + 1,
        )
        for offset in witness_offsets:
            observation = track.observations[offset]
            observation.admitted = not observation.incompatible
            observation.confirmation_profile = witness.profile
            observation.confirmation_support = witness.confirmation_support
            observation.net_progress_px = witness.net_progress_px
            observation.direction = witness.direction
            observation.directional_agreement = witness.directional_agreement
            observation.motion_support = witness.motion_support
            observation.motion_energy = witness.motion_energy
            observation.motion_coverage = witness.motion_coverage
            observation.material_conflict = witness.material_conflict
            observation.confirmation_start_frame = (
                track.observations[witness.start_observation]
                .hypothesis.frame_offset
            )
            observation.confirmation_end_frame = (
                track.observations[confirmation_offset]
                .hypothesis.frame_offset
            )
            observation.confirmation_observation_count = witness.observation_count
            observation.failure_reason = (
                "INCOMPATIBLE_BRANCH"
                if observation.incompatible
                else ""
            )
        track.observations[confirmation_offset].lifecycle = (
            TrackletLifecycle.CONFIRMED
        )

        last_anchor_frame = max(
            (
                item.hypothesis.frame_offset
                for item in track.observations[: confirmation_offset + 1]
                if item.hypothesis.anchor_signal
            ),
            default=track.observations[confirmation_offset].hypothesis.frame_offset,
        )
        anchor_frames = tuple(
            item.hypothesis.frame_offset
            for item in track.observations[confirmation_offset + 1 :]
            if item.hypothesis.anchor_signal
        )
        for offset in range(confirmation_offset + 1, len(track.observations)):
            observation = track.observations[offset]
            observation.lifecycle = TrackletLifecycle.CONTINUING
            if observation.incompatible:
                observation.failure_reason = "INCOMPATIBLE_BRANCH"
                continue
            if observation.hypothesis.anchor_signal:
                last_anchor_frame = observation.hypothesis.frame_offset
            # Continuation aggregates the entire bounded window; confirmation
            # excludes incompatible observations and may have fewer than its
            # minimum count. Reusing its filtered motion values changes admission.
            _start, recent = _bounded_observation_window(
                track.observations, offset, self.policy.confirmation_window_frames
            )
            motion_energy = _motion_energy(recent)
            motion_support = _motion_support(recent)
            motion_coverage = _motion_coverage(recent)
            within_anchor_grace = (
                observation.hypothesis.frame_offset - last_anchor_frame
                <= self.policy.continuation_grace_frames
            )
            following_anchor = next(
                (
                    frame
                    for frame in anchor_frames
                    if frame >= observation.hypothesis.frame_offset
                ),
                None,
            )
            bounded_anchor_corridor = bool(
                following_anchor is not None
                and observation.hypothesis.frame_offset - last_anchor_frame
                < self.policy.confirmation_window_frames
                and following_anchor - observation.hypothesis.frame_offset
                < self.policy.confirmation_window_frames
            )
            aggregate_motion = (
                motion_energy
                >= self.policy.continuation_min_motion_energy
                and motion_coverage
                >= self.policy.continuation_min_motion_coverage
            )
            observation.admitted = (
                within_anchor_grace
                or bounded_anchor_corridor
                or aggregate_motion
            )
            observation.confirmation_profile = witness.profile
            observation.confirmation_support = witness.confirmation_support
            observation.net_progress_px = witness.net_progress_px
            observation.direction = witness.direction
            observation.directional_agreement = witness.directional_agreement
            observation.motion_support = motion_support
            observation.motion_energy = motion_energy
            observation.motion_coverage = motion_coverage
            observation.material_conflict = witness.material_conflict
            observation.confirmation_start_frame = (
                track.observations[witness.start_observation]
                .hypothesis.frame_offset
            )
            observation.confirmation_end_frame = (
                track.observations[confirmation_offset]
                .hypothesis.frame_offset
            )
            observation.confirmation_observation_count = witness.observation_count
            observation.failure_reason = (
                "" if observation.admitted else "CONTINUATION_EVIDENCE_EXPIRED"
            )

    def _confirmation_evidence(
        self,
        observations: list[_TrackObservation],
        end_offset: int,
    ) -> _WindowEvidence:
        start_offset, bounded = _bounded_observation_window(
            observations,
            end_offset,
            self.policy.confirmation_window_frames,
        )
        valid = tuple(item for item in bounded if not item.incompatible)
        if len(valid) < self.policy.confirmation_min_observations:
            return _empty_window(start_offset, len(valid), end_offset)
        first = valid[0].hypothesis
        last = valid[-1].hypothesis
        deltas = tuple(
            following.hypothesis.y - prior.hypothesis.y
            for prior, following in zip(valid, valid[1:])
        )
        motion_energy = _motion_energy(valid)
        motion_support = _motion_support(valid)
        motion_coverage = _motion_coverage(valid)
        material_conflict = _material_conflict(valid)
        anchor_frames = sum(item.hypothesis.anchor_signal for item in valid)
        physical_proposal = any(
            item.hypothesis.has_physical_proposal for item in valid
        )
        signed = last.y - first.y
        net_progress = abs(signed)
        observed_direction = -1 if signed < 0.0 else (1 if signed > 0.0 else 0)
        directional = max(
            sum(delta <= 0.0 for delta in deltas),
            sum(delta >= 0.0 for delta in deltas),
        ) / len(deltas)
        motion_witness = (
            motion_support >= self.policy.confirmation_min_motion_support
            and motion_coverage >= self.policy.confirmation_min_motion_coverage
        )
        anchor_witness = (
            anchor_frames >= self.policy.confirmation_min_anchor_frames
        )

        profile = TrackletConfirmationProfile.NONE
        if anchor_witness:
            profile = TrackletConfirmationProfile.ANCHOR_CORRIDOR
        elif (
            net_progress >= self.policy.confirmation_min_progress_px
            and directional >= self.policy.confirmation_min_directional_agreement
            and anchor_frames >= 1
            and physical_proposal
        ):
            profile = TrackletConfirmationProfile.ANCHOR_TRAJECTORY
        elif (
            net_progress >= self.policy.confirmation_min_progress_px
            and directional >= self.policy.confirmation_min_directional_agreement
            and motion_witness
            and physical_proposal
        ):
            profile = TrackletConfirmationProfile.MOTION_TRAJECTORY

        progress_score = min(
            1.0,
            net_progress / max(1e-9, self.policy.confirmation_min_progress_px),
        )
        motion_score = min(
            1.0,
            motion_support
            / max(1e-9, self.policy.confirmation_min_motion_support),
        )
        anchor_score = min(
            1.0,
            anchor_frames / max(1, self.policy.confirmation_min_anchor_frames),
        )
        support = min(
            1.0,
            0.32 * progress_score
            + 0.28 * directional
            + 0.22 * motion_score
            + 0.18 * anchor_score,
        )
        return _WindowEvidence(
            start_observation=start_offset,
            end_observation=end_offset,
            observation_count=len(valid),
            net_progress_px=net_progress,
            direction=observed_direction,
            directional_agreement=directional,
            motion_support=motion_support,
            motion_energy=motion_energy,
            motion_coverage=motion_coverage,
            material_conflict=material_conflict,
            anchor_frames=anchor_frames,
            profile=profile,
            confirmation_support=support,
        )

    def _cached_confirmation_evidence(
        self,
        track: _TrackState,
        end_offset: int,
    ) -> _WindowEvidence:
        """Return the bounded witness for one observation endpoint once."""

        cached = track.window_evidence_cache.get(end_offset)
        if cached is None:
            cached = self._confirmation_evidence(track.observations, end_offset)
            track.window_evidence_cache[end_offset] = cached
        return cached

    def _track_failure_reason(
        self,
        track: _TrackState,
    ) -> str:
        observations = track.observations
        if any(item.incompatible for item in observations):
            return "INCOMPATIBLE_BRANCH"
        maximum_progress = 0.0
        maximum_directional = 0.0
        maximum_motion = 0.0
        maximum_coverage = 0.0
        maximum_anchors = 0
        for offset in range(len(observations)):
            evidence = self._cached_confirmation_evidence(track, offset)
            maximum_progress = max(maximum_progress, evidence.net_progress_px)
            maximum_directional = max(
                maximum_directional,
                evidence.directional_agreement,
            )
            maximum_motion = max(maximum_motion, evidence.motion_support)
            maximum_coverage = max(maximum_coverage, evidence.motion_coverage)
            maximum_anchors = max(maximum_anchors, evidence.anchor_frames)
        if maximum_progress < self.policy.confirmation_min_progress_px:
            return "INSUFFICIENT_NET_PROGRESS"
        if (
            maximum_directional
            < self.policy.confirmation_min_directional_agreement
        ):
            return "INSUFFICIENT_DIRECTIONAL_AGREEMENT"
        if (
            maximum_motion < self.policy.confirmation_min_motion_support
            or maximum_coverage < self.policy.confirmation_min_motion_coverage
        ) and maximum_anchors < self.policy.confirmation_min_anchor_frames:
            return "INSUFFICIENT_MOTION_OR_ANCHOR_EVIDENCE"
        return "PROVISIONAL_TRACKLET"

    def _best_failure_evidence(
        self,
        track: _TrackState,
    ) -> _WindowEvidence:
        observations = track.observations
        evidence = tuple(
            self._cached_confirmation_evidence(track, offset)
            for offset in range(len(observations))
        )
        return max(
            evidence,
            key=lambda item: (
                item.observation_count,
                item.net_progress_px,
                item.directional_agreement,
                item.anchor_frames,
                item.motion_support,
                item.motion_coverage,
            ),
            default=_empty_window(0, 0),
        )


def _phase_class(ref: OilCandidateRef) -> str:
    return "ordered_lower" if ref.ordered_lower else "direct"


def _source_family(source: str) -> str:
    return str(source).split(":", 1)[0]


def _track_velocity(track: _TrackState) -> float:
    observations = track.observations[-4:]
    velocities = []
    for prior, following in zip(observations, observations[1:]):
        gap = (
            following.hypothesis.frame_offset
            - prior.hypothesis.frame_offset
        )
        if gap > 0:
            velocities.append(
                (following.hypothesis.y - prior.hypothesis.y) / gap
            )
    return 0.0 if not velocities else float(median(velocities))


def _bounded_observation_window(
    observations: list[_TrackObservation],
    end_offset: int,
    window_frames: int,
) -> tuple[int, tuple[_TrackObservation, ...]]:
    end_frame = observations[end_offset].hypothesis.frame_offset
    first_frame = end_frame - max(2, window_frames) + 1
    start_offset = end_offset
    while (
        start_offset > 0
        and observations[start_offset - 1].hypothesis.frame_offset
        >= first_frame
    ):
        start_offset -= 1
    return start_offset, tuple(observations[start_offset : end_offset + 1])


def _lifecycle_history(track: _TrackState) -> tuple[TrackletLifecycle, ...]:
    history: list[TrackletLifecycle] = [TrackletLifecycle.PROVISIONAL]
    if any(
        item.lifecycle is TrackletLifecycle.CONFIRMED
        for item in track.observations
    ):
        history.append(TrackletLifecycle.CONFIRMED)
    if any(
        item.lifecycle is TrackletLifecycle.CONTINUING
        for item in track.observations
    ):
        history.append(TrackletLifecycle.CONTINUING)
    if track.lost_event_count:
        history.append(TrackletLifecycle.LOST)
    history.append(TrackletLifecycle.TERMINATED)
    return tuple(history)


def _motion_energy(observations) -> float:
    values = tuple(
        item.hypothesis.motion_support * item.hypothesis.motion_coverage
        for item in observations
    )
    return 0.0 if not values else sum(values) / len(values)


def _motion_support(observations) -> float:
    values = tuple(item.hypothesis.motion_support for item in observations)
    return 0.0 if not values else sum(values) / len(values)


def _motion_coverage(observations) -> float:
    values = tuple(item.hypothesis.motion_coverage for item in observations)
    return 0.0 if not values else sum(values) / len(values)


def _material_conflict(observations) -> float:
    values = tuple(item.hypothesis.material_conflict for item in observations)
    return 0.0 if not values else sum(values) / len(values)


def _empty_window(
    start: int,
    count: int,
    end: int | None = None,
) -> _WindowEvidence:
    return _WindowEvidence(
        start_observation=start,
        end_observation=(
            start + max(0, count - 1) if end is None else end
        ),
        observation_count=count,
        net_progress_px=0.0,
        direction=0,
        directional_agreement=0.0,
        motion_support=0.0,
        motion_energy=0.0,
        motion_coverage=0.0,
        material_conflict=0.0,
        anchor_frames=0,
        profile=TrackletConfirmationProfile.NONE,
        confirmation_support=0.0,
    )
