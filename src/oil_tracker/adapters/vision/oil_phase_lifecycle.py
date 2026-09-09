from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
import math
from statistics import median

from oil_tracker.domain.enums import InitialObservationState

from .oil_candidate_authority import OilCandidateAuthority
from .oil_phase_identity import OilPhaseIdentity
from .oil_phase_identity import OilIdentityContradiction
from .oil_sequence_types import (
    OilCandidateRef,
    OilSequenceNode,
    TrackletConfirmationProfile,
    TrackletLifecycle,
)


class OilMaterialPhase(str, Enum):
    OPEN = "open"
    FILLING = "filling"
    FILLED_BARRIER = "filled_barrier"
    DRAINING = "draining"


class OilFillConfirmationProfile(str, Enum):
    NONE = "none"
    UNKNOWN_FILL_ANCHORED = "unknown_fill_anchored"
    EMPTY_ENTRANCE_MOTION = "empty_entrance_motion"


@dataclass(frozen=True)
class OilMaterialPhasePolicy:
    geometry_top_y: float
    geometry_height: float
    maximum_jump_px: float
    maximum_lost_frames: int
    handoff_ambiguity_margin: float
    handoff_direction_reversal_tolerance_px: float
    fill_onset_intent_frames: int
    fill_evidence_window_frames: int
    entrance_band_ratio: float
    fill_minimum_span_ratio: float
    minimum_directional_agreement: float
    confirmed_initial_state: InitialObservationState | None
    fill_minimum_motion_support: float
    fill_minimum_motion_coverage: float
    drain_entrance_ratio: float
    drain_minimum_progress_ratio: float
    drain_minimum_directional_agreement: float
    material_conflict_limit: float

    @property
    def initial_empty(self) -> bool:
        return (
            self.confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE
        )

    @property
    def initial_full(self) -> bool:
        return self.confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE


@dataclass(frozen=True)
class OilMaterialPhaseResult:
    phases: tuple[OilMaterialPhase, ...]
    reasons: tuple[str, ...]
    owner_chains: tuple[tuple[str, ...], ...]
    fill_confirmation_profiles: tuple[OilFillConfirmationProfile, ...]
    allowed_tracklet_ids: tuple[frozenset[str] | None, ...]
    ambiguous_frames: frozenset[int]
    diagnostics: tuple[dict[str, object], ...]
    frame_decisions: tuple[OilFrameDecision, ...] = ()


@dataclass(frozen=True)
class OilReleasePredicateEvaluation:
    stage: str
    tracklet_id: str
    row_hypothesis_id: str
    row_y: float
    entrance_y: float
    entrance_relative: float | None
    established_fill_last_y: float | None
    minimum_progress_px: float
    maximum_jump_px: float
    tracklet_progress_px: float
    directional_agreement: float
    current_material_veto: bool
    tracklet_material_conflict: float
    current_material_conflict: float
    predicates: tuple[tuple[str, bool], ...]

    @property
    def passed(self) -> bool:
        return all(passed for _name, passed in self.predicates)

    @property
    def first_failed_predicate(self) -> str | None:
        return next(
            (name for name, passed in self.predicates if not passed),
            None,
        )

    def as_debug_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "tracklet_id": self.tracklet_id,
            "row_hypothesis_id": self.row_hypothesis_id,
            "row_y": self.row_y,
            "entrance_y": self.entrance_y,
            "entrance_relative": self.entrance_relative,
            "established_fill_last_y": self.established_fill_last_y,
            "minimum_progress_px": self.minimum_progress_px,
            "maximum_jump_px": self.maximum_jump_px,
            "tracklet_progress_px": self.tracklet_progress_px,
            "directional_agreement": self.directional_agreement,
            "current_material_veto": self.current_material_veto,
            "tracklet_material_conflict": self.tracklet_material_conflict,
            "current_material_conflict": self.current_material_conflict,
            "predicates": {name: passed for name, passed in self.predicates},
            "passed": self.passed,
            "first_failed_predicate": self.first_failed_predicate,
        }


@dataclass(frozen=True)
class _ObservedRow:
    tracklet_id: str
    row_hypothesis_id: str
    y: float
    entrance_y: float
    ref: OilCandidateRef
    nodes: tuple[OilSequenceNode, ...]
    current_material_conflict: float
    current_material_veto: bool


@dataclass(frozen=True)
class _FillObservation:
    frame: int
    y: float
    material_veto: bool
    independent_anchor: bool
    confirmation_profile: TrackletConfirmationProfile
    net_progress_px: float
    directional_agreement: float
    motion_support: float
    motion_coverage: float


@dataclass(frozen=True)
class _FillChain:
    owner: str
    owners: tuple[str, ...]
    origin_y: float
    observations: tuple[_FillObservation, ...]

    @property
    def last(self) -> _FillObservation:
        return self.observations[-1]


@dataclass(frozen=True)
class _DrainChain:
    owner: str
    owners: tuple[str, ...]
    last_y: float
    last_frame: int


@dataclass(frozen=True)
class _RecoveryDrainChain:
    """Constant-size phase evidence for a fragmented drain release."""

    stage: str
    context_key: tuple[str, ...]
    owner: str
    owners: tuple[str, ...]
    seed_y: float
    current_y: float
    first_frame: int
    last_frame: int
    last_forward_progress_frame: int
    observation_count: int
    transition_count: int
    nonnegative_transition_count: int
    negative_transition_count: int
    net_progress_px: float
    # Initial-FULL release evidence has one explicitly bounded renewal.  The
    # original seed frame remains the lease origin so the horizon cannot grow
    # through repeated resets or a moving origin.
    lease_origin_frame: int
    lease_expiry_frame: int
    renewal_used: bool = False
    certified_anchor_frame: int | None = None
    certified_anchor_y: float | None = None

    @property
    def directional_agreement(self) -> float:
        if not self.transition_count:
            return 0.0
        return self.nonnegative_transition_count / self.transition_count

    @property
    def owner_key(self) -> str:
        return self.owner


@dataclass(frozen=True)
class _PartialFillOwnerlessBarrier:
    """Coordinate-free context for an established fill owner that was lost."""

    context_key: tuple[str, ...]
    owner_chain: tuple[str, ...]
    snapshot_frame: int
    snapshot_y: float
    loss_frame: int
    grace_limit: int


@dataclass(frozen=True)
class OilFrameDecision:
    """Immutable per-frame phase decision used by diagnostics and projection."""

    frame: int
    phase: OilMaterialPhase
    reason: str
    allowed_tracklet_ids: frozenset[str] | None
    owner_chain: tuple[str, ...]


@dataclass
class OilPhaseRuntimeState:
    """Mutable orchestration state owned by the lifecycle transition loop."""

    phase: OilMaterialPhase
    filled_chain: tuple[str, ...] = ()
    filled_frame: int | None = None
    fill_terminal_owner: str | None = None
    fill_owner_open: bool = False
    established_fill_chain: _FillChain | None = None
    drain_chain: _DrainChain | None = None
    recovery_chains: dict[str, _RecoveryDrainChain] = field(default_factory=dict)
    delayed_recovery_chains: dict[str, _RecoveryDrainChain] = field(
        default_factory=dict
    )
    ownerless_barrier: _PartialFillOwnerlessBarrier | None = None
    delayed_attempt: _DelayedDrainReacquisitionAttempt | None = None
    delayed_episode_blocked: bool = False

    chains: dict[str, _FillChain] = field(default_factory=dict)
    fill_confirmation_profile: OilFillConfirmationProfile = (
        OilFillConfirmationProfile.NONE
    )


@dataclass
class _OilFrameRecord:
    identity_contradictions: frozenset[str] = frozenset()
    established_fill_snapshot: _FillChain | None = None
    dynamic_fill_owner_snapshot: frozenset[str] = frozenset()
    release_stage: str = "not_evaluated"
    release_evaluation: tuple[OilReleasePredicateEvaluation, ...] = ()
    release_qualifying_ids: tuple[str, ...] = ()
    release_selected_id: str | None = None
    release_ambiguous: bool = False
    recovery_stage: str = "not_evaluated"
    recovery_evaluated: bool = False
    recovery_active: tuple[dict[str, object], ...] = ()
    recovery_predicates: tuple[dict[str, object], ...] = ()
    recovery_qualifying_ids: tuple[str, ...] = ()
    recovery_selected_id: str | None = None
    recovery_ambiguous: bool = False
    recovery_ambiguous_seed_owner_ids: tuple[str, ...] = ()
    recovery_reset_reason: str | None = None
    release_source: str = "none"
    release_source_detail: str = "none"
    ownerless_barrier_state: str = "inactive"
    ownerless_barrier_loss_epoch: int | None = None
    ownerless_barrier_loss_age: int | None = None
    ownerless_barrier_grace_limit: int = 0
    ownerless_barrier_attempt_consumed: bool = False
    delayed_reacquisition_evaluated: bool = False
    delayed_reacquisition_seed_predicates: tuple[dict[str, object], ...] = ()
    delayed_reacquisition_active: tuple[dict[str, object], ...] = ()
    delayed_reacquisition_qualifying_ids: tuple[str, ...] = ()
    delayed_reacquisition_selected_id: str | None = None
    delayed_reacquisition_ambiguous: bool = False
    delayed_reacquisition_reset_reason: str | None = None
    delayed_reacquisition_snapshot_distance: float | None = None
    delayed_reacquisition_seed_frame: int | None = None
    phase: OilMaterialPhase = OilMaterialPhase.OPEN
    reason: str = "OPEN"
    allowed_tracklet_ids: frozenset[str] | None = None
    owner_chain: tuple[str, ...] | None = None
    fill_confirmation_profile: OilFillConfirmationProfile = (
        OilFillConfirmationProfile.NONE
    )
    transient_owner_chain: tuple[str, ...] = ()
    barrier_state_override: str | None = None


@dataclass(frozen=True)
class _DelayedDrainReacquisitionAttempt:
    """One fresh-anchor attempt owned by one established-fill episode."""

    context_key: tuple[str, ...]
    seed_frame: int | None = None
    consumed: bool = False


class OilMaterialPhaseLifecycleOwner:
    """Own causal fill/barrier/drain state without merging track identities."""

    def __init__(self, policy: OilMaterialPhasePolicy) -> None:
        self.policy = policy
        self.release_evidence = BoundedOilReleaseEvidenceEngine(policy)

    def resolve(
        self,
        layers: tuple[tuple[OilSequenceNode, ...], ...],
        *,
        identity_contradictions: tuple[frozenset[str], ...] = (),
    ) -> OilMaterialPhaseResult:
        if identity_contradictions and len(identity_contradictions) != len(layers):
            raise ValueError("Identity contradictions must align with frame layers")
        rows_by_frame = tuple((self._rows(layer) for layer in layers))
        first_frame = {
            row.tracklet_id: frame
            for frame, rows in reversed(tuple(enumerate(rows_by_frame)))
            for row in rows
        }
        records = [
            _OilFrameRecord(
                ownerless_barrier_grace_limit=self.policy.maximum_lost_frames + 1
            )
            for _ in layers
        ]
        state = OilPhaseRuntimeState(
            phase=OilMaterialPhase.FILLED_BARRIER
            if self.policy.initial_full
            else OilMaterialPhase.OPEN,
            filled_frame=0 if self.policy.initial_full else None,
        )
        ambiguous_frames: set[int] = set()
        for frame, record in enumerate(records):
            record.identity_contradictions = (
                identity_contradictions[frame]
                if identity_contradictions
                else frozenset()
            )
            if state.phase in {OilMaterialPhase.OPEN, OilMaterialPhase.FILLING}:
                self._transition_open(
                    state, records, rows_by_frame, first_frame, frame, ambiguous_frames
                )
            elif state.phase is OilMaterialPhase.FILLED_BARRIER:
                self._transition_barrier(
                    state, records, rows_by_frame, first_frame, frame, ambiguous_frames
                )
            else:
                self._transition_draining(
                    state, records, rows_by_frame, first_frame, frame, ambiguous_frames
                )
            record.phase = state.phase
            record.fill_confirmation_profile = state.fill_confirmation_profile
            if record.owner_chain is None:
                record.owner_chain = (
                    state.drain_chain.owners
                    if state.phase is OilMaterialPhase.DRAINING
                    and state.drain_chain is not None
                    else state.filled_chain
                    if state.phase is OilMaterialPhase.FILLED_BARRIER
                    else record.transient_owner_chain
                    or _selected_owner_chain(state.chains, record.allowed_tracklet_ids)
                )
            self._capture_frame_runtime(record, state, frame)
        decisions = tuple(
            (
                OilFrameDecision(
                    frame=i,
                    phase=r.phase,
                    reason=r.reason,
                    allowed_tracklet_ids=r.allowed_tracklet_ids,
                    owner_chain=r.owner_chain or (),
                )
                for i, r in enumerate(records)
            )
        )
        return OilMaterialPhaseResult(
            phases=tuple((d.phase for d in decisions)),
            reasons=tuple((d.reason for d in decisions)),
            owner_chains=tuple((d.owner_chain for d in decisions)),
            fill_confirmation_profiles=tuple(
                (r.fill_confirmation_profile for r in records)
            ),
            allowed_tracklet_ids=tuple((d.allowed_tracklet_ids for d in decisions)),
            ambiguous_frames=frozenset(ambiguous_frames),
            diagnostics=tuple((self._serialize_frame(r) for r in records)),
            frame_decisions=decisions,
        )

    def _transition_open(
        self,
        state: OilPhaseRuntimeState,
        records: list[_OilFrameRecord],
        rows_by_frame: tuple[tuple[_ObservedRow, ...], ...],
        first_frame: dict[str, int],
        frame: int,
        ambiguous_frames: set[int],
    ) -> None:
        record = records[frame]
        rows = rows_by_frame[frame]
        prior_phase = state.phase
        fill_phase_reentered = False
        recovery_released = False
        state.chains, chain_ambiguity, chain_reason = self._advance_fill_chains(
            state.chains, rows, frame
        )
        if chain_ambiguity:
            ambiguous_frames.add(frame)
            record.reason = "FILL_CHAIN_AMBIGUOUS"
        elif chain_reason:
            record.reason = chain_reason
        qualified = tuple(
            (
                (chain, profile)
                for chain in state.chains.values()
                if (profile := self._fill_confirmation_profile(chain))
                is not OilFillConfirmationProfile.NONE
            )
        )
        record.dynamic_fill_owner_snapshot = frozenset(
            (
                owner
                for owner, chain in state.chains.items()
                if self._chain_is_dynamic_fill_owner(chain)
                or (
                    state.established_fill_chain is not None
                    and chain.owners[: len(state.established_fill_chain.owners)]
                    == state.established_fill_chain.owners
                )
            )
        )
        if record.dynamic_fill_owner_snapshot and state.recovery_chains:
            state.recovery_chains = {}
            records[frame].recovery_reset_reason = "release_context_changed"
        if state.established_fill_chain is not None and (
            not record.dynamic_fill_owner_snapshot
        ):
            reentries = tuple(
                (
                    row
                    for row in rows
                    if self._fill_phase_reentry(
                        state.established_fill_chain, row, frame
                    )
                )
            )
            ranked_reentries = tuple(
                sorted(
                    (
                        (
                            abs(row.y - state.established_fill_chain.last.y)
                            / self.policy.maximum_jump_px,
                            row.tracklet_id,
                            row,
                        )
                        for row in reentries
                    )
                )
            )
            chosen = _clear_choice(
                tuple(((cost, owner) for cost, owner, _row in ranked_reentries)),
                self.policy.handoff_ambiguity_margin,
            )
            if chosen is None and ranked_reentries:
                state.chains = {}
                ambiguous_frames.add(frame)
                record.reason = "FILL_PHASE_REENTRY_AMBIGUOUS"
            elif chosen is not None:
                successor = next(
                    (row for _cost, owner, row in ranked_reentries if owner == chosen)
                )
                reentry_chain = _handoff_chain(
                    state.established_fill_chain,
                    successor,
                    frame,
                    self.policy.fill_evidence_window_frames,
                )
                state.chains = {chosen: reentry_chain}
                record.dynamic_fill_owner_snapshot = frozenset({chosen})
                fill_phase_reentered = True
                record.reason = "FILL_PHASE_REENTRY"
        if record.dynamic_fill_owner_snapshot or fill_phase_reentered:
            if (
                state.ownerless_barrier is not None
                or state.delayed_attempt is not None
                or state.delayed_recovery_chains
            ):
                state.delayed_episode_blocked = True
                state.ownerless_barrier = None
                state.delayed_attempt = None
                state.delayed_recovery_chains = {}
                record.barrier_state_override = "reset"
        elif (
            self.policy.initial_empty
            and state.established_fill_chain is not None
            and (not state.delayed_episode_blocked)
        ):
            ownerless_context = _recovery_context_key(
                "partial_fill", state.established_fill_chain
            )
            if (
                state.ownerless_barrier is None
                or state.ownerless_barrier.context_key != ownerless_context
            ):
                if state.ownerless_barrier is not None:
                    record.barrier_state_override = "reset"
                state.ownerless_barrier = _PartialFillOwnerlessBarrier(
                    context_key=ownerless_context,
                    owner_chain=state.established_fill_chain.owners,
                    snapshot_frame=state.established_fill_chain.last.frame,
                    snapshot_y=state.established_fill_chain.last.y,
                    loss_frame=frame,
                    grace_limit=self.policy.maximum_lost_frames + 1,
                )
                state.delayed_attempt = None
                state.delayed_recovery_chains = {}
        elif (
            self.policy.initial_empty
            and state.established_fill_chain is not None
            and state.delayed_episode_blocked
        ):
            record.barrier_state_override = "reset"
        if (
            self.policy.initial_empty
            and state.established_fill_chain is not None
            and (not record.dynamic_fill_owner_snapshot)
        ):
            records[frame].release_stage = "partial_fill_drain_release"
            records[frame].release_evaluation = tuple(
                (
                    self._partial_fill_drain_release_evaluation(
                        state.established_fill_chain, row
                    )
                    for row in rows
                )
            )
            partial_release, release_ambiguous = (
                self._partial_fill_drain_release_choice(
                    state.established_fill_chain, rows
                )
            )
            if release_ambiguous:
                state.recovery_chains = {}
                records[frame].recovery_reset_reason = "direct_ambiguity"
                records[frame].release_qualifying_ids = tuple(
                    sorted(
                        {
                            item.tracklet_id
                            for item in records[frame].release_evaluation
                            if item.passed
                        }
                    )
                )
                records[frame].release_ambiguous = True
                state.phase = OilMaterialPhase.OPEN
                record.allowed_tracklet_ids = frozenset()
                ambiguous_frames.add(frame)
                record.reason = "PARTIAL_FILL_DRAIN_RELEASE_AMBIGUOUS"
                record.owner_chain = state.established_fill_chain.owners
                return
            if partial_release is not None:
                records[frame].release_qualifying_ids = tuple(
                    sorted(
                        {
                            item.tracklet_id
                            for item in records[frame].release_evaluation
                            if item.passed
                        }
                    )
                )
                records[frame].release_selected_id = partial_release.tracklet_id
                state.drain_chain = _DrainChain(
                    owner=partial_release.tracklet_id,
                    owners=_append_unique_owner(
                        state.established_fill_chain.owners, partial_release.tracklet_id
                    ),
                    last_y=partial_release.y,
                    last_frame=frame,
                )
                state.phase = OilMaterialPhase.DRAINING
                record.allowed_tracklet_ids = frozenset({partial_release.tracklet_id})
                record.reason = "PARTIAL_FILL_DRAIN_RELEASE_CONFIRMED"
                records[frame].release_source = "direct"
                records[frame].release_source_detail = "direct"
                state.ownerless_barrier = None
                state.delayed_attempt = None
                state.delayed_recovery_chains = {}
                record.barrier_state_override = "released"
                record.owner_chain = state.drain_chain.owners
                return
            records[frame].recovery_stage = "partial_fill"
            records[frame].recovery_evaluated = True
            state.recovery_chains, recovery_result = self.release_evidence.advance(
                state.recovery_chains,
                rows,
                frame,
                stage="partial_fill",
                seed_rows=rows,
                established_fill=state.established_fill_chain,
                contradicted_owner_ids=record.identity_contradictions,
            )
            records[frame].recovery_active = recovery_result["active"]
            records[frame].recovery_predicates = recovery_result["predicates"]
            records[frame].recovery_reset_reason = recovery_result["reset_reason"]
            records[frame].recovery_ambiguous = recovery_result["ambiguous"]
            records[frame].recovery_ambiguous_seed_owner_ids = recovery_result[
                "ambiguous_seed_owner_ids"
            ]
            qualifying = tuple(
                sorted(
                    recovery_result["qualifying"],
                    key=lambda item: (item[0], item[1].tracklet_id),
                )
            )
            records[frame].recovery_qualifying_ids = tuple(
                (row.tracklet_id for _key, row in qualifying)
            )
            if recovery_result["ambiguous"]:
                state.phase = OilMaterialPhase.OPEN
                record.allowed_tracklet_ids = frozenset()
                ambiguous_frames.add(frame)
                record.reason = "PARTIAL_FILL_DRAIN_RECOVERY_AMBIGUOUS"
                record.owner_chain = state.established_fill_chain.owners
                return
            if len(qualifying) == 1:
                _key, selected = qualifying[0]
                recovery_owners = state.established_fill_chain.owners
                for recovery_owner in state.recovery_chains[_key].owners:
                    recovery_owners = _append_unique_owner(
                        recovery_owners, recovery_owner
                    )
                state.drain_chain = _DrainChain(
                    owner=selected.tracklet_id,
                    owners=recovery_owners,
                    last_y=selected.y,
                    last_frame=frame,
                )
                state.phase = OilMaterialPhase.DRAINING
                record.allowed_tracklet_ids = frozenset({selected.tracklet_id})
                record.reason = "PARTIAL_FILL_DRAIN_RECOVERY_CONFIRMED"
                records[frame].recovery_selected_id = selected.tracklet_id
                records[frame].release_source = "recovery"
                records[frame].release_source_detail = "recovery_near_snapshot"
                state.recovery_chains = {}
                state.ownerless_barrier = None
                state.delayed_attempt = None
                state.delayed_recovery_chains = {}
                record.barrier_state_override = "released"
                recovery_released = True
            elif len(qualifying) > 1:
                state.recovery_chains = {}
                records[frame].recovery_ambiguous = True
                ambiguous_frames.add(frame)
                record.allowed_tracklet_ids = frozenset()
                record.reason = "PARTIAL_FILL_DRAIN_RECOVERY_AMBIGUOUS"
            if recovery_released:
                record.owner_chain = state.drain_chain.owners
                return
            records[frame].delayed_reacquisition_snapshot_distance = (
                abs(rows[0].y - state.established_fill_chain.last.y) if rows else None
            )
            near_chain_active = bool(state.recovery_chains)
            grace_elapsed = bool(
                state.ownerless_barrier is not None
                and frame - state.ownerless_barrier.loss_frame
                >= state.ownerless_barrier.grace_limit
            )
            attempt_available = bool(
                state.ownerless_barrier is not None
                and (
                    state.delayed_attempt is None or not state.delayed_attempt.consumed
                )
            )
            records[frame].delayed_reacquisition_evaluated = bool(
                state.ownerless_barrier is not None and (not near_chain_active)
            )
            records[frame].delayed_reacquisition_seed_predicates = tuple(
                (
                    self.release_evidence._delayed_seed_admission_record(
                        row,
                        grace_elapsed=grace_elapsed,
                        attempt_available=attempt_available,
                        snapshot_y=state.established_fill_chain.last.y,
                    )
                    for row in rows
                )
            )
            delayed_released = False
            delayed_result: dict[str, object] = {
                "active": (),
                "predicates": (),
                "qualifying": (),
                "ambiguous": False,
                "reset_reason": None,
            }
            if (
                state.ownerless_barrier is not None
                and (not near_chain_active)
                and (state.delayed_attempt is not None)
                and state.delayed_attempt.consumed
                and state.delayed_recovery_chains
            ):
                state.delayed_recovery_chains, delayed_result = (
                    self.release_evidence.advance(
                        state.delayed_recovery_chains,
                        rows,
                        frame,
                        stage="delayed_reacquisition",
                        seed_rows=(),
                        established_fill=state.established_fill_chain,
                        allow_seeding=False,
                        contradicted_owner_ids=record.identity_contradictions,
                    )
                )
            elif (
                state.ownerless_barrier is not None
                and (not near_chain_active)
                and grace_elapsed
                and attempt_available
            ):
                delayed_seed_rows = tuple(
                    (
                        row
                        for row in rows
                        if self.release_evidence._delayed_seed_allowed(
                            row, established_fill=state.established_fill_chain
                        )
                    )
                )
                if delayed_seed_rows:
                    state.delayed_attempt = _DelayedDrainReacquisitionAttempt(
                        context_key=state.ownerless_barrier.context_key,
                        seed_frame=frame,
                        consumed=True,
                    )
                    records[frame].delayed_reacquisition_seed_frame = frame
                    if len(delayed_seed_rows) > 1:
                        records[frame].delayed_reacquisition_ambiguous = True
                        records[
                            frame
                        ].delayed_reacquisition_reset_reason = (
                            "duplicate_delayed_seed_anchors"
                        )
                        delayed_result = {
                            "active": (),
                            "predicates": (),
                            "qualifying": (),
                            "ambiguous": True,
                            "reset_reason": "duplicate_delayed_seed_anchors",
                        }
                    else:
                        state.delayed_recovery_chains, delayed_result = (
                            self.release_evidence.advance(
                                state.delayed_recovery_chains,
                                rows,
                                frame,
                                stage="delayed_reacquisition",
                                seed_rows=delayed_seed_rows,
                                established_fill=state.established_fill_chain,
                                contradicted_owner_ids=record.identity_contradictions,
                            )
                        )
            records[frame].delayed_reacquisition_active = tuple(
                delayed_result.get("active", ())
            )
            active_delayed = records[frame].delayed_reacquisition_active
            if active_delayed:
                current_y = active_delayed[0].get("current_y")
                if current_y is not None:
                    records[frame].delayed_reacquisition_snapshot_distance = abs(
                        float(current_y) - state.established_fill_chain.last.y
                    )
            records[frame].delayed_reacquisition_qualifying_ids = tuple(
                (row.tracklet_id for _key, row in delayed_result.get("qualifying", ()))
            )
            records[frame].delayed_reacquisition_ambiguous = bool(
                delayed_result.get("ambiguous", False)
            )
            records[frame].delayed_reacquisition_reset_reason = delayed_result.get(
                "reset_reason"
            )
            delayed_qualifying = tuple(
                sorted(
                    delayed_result.get("qualifying", ()),
                    key=lambda item: (item[0], item[1].tracklet_id),
                )
            )
            if delayed_result.get("ambiguous"):
                state.phase = OilMaterialPhase.OPEN
                record.allowed_tracklet_ids = frozenset()
                ambiguous_frames.add(frame)
                record.reason = "PARTIAL_FILL_DRAIN_DELAYED_REACQUISITION_AMBIGUOUS"
            elif len(delayed_qualifying) == 1:
                _key, selected = delayed_qualifying[0]
                recovery_owners = state.established_fill_chain.owners
                for recovery_owner in state.delayed_recovery_chains[_key].owners:
                    recovery_owners = _append_unique_owner(
                        recovery_owners, recovery_owner
                    )
                state.drain_chain = _DrainChain(
                    owner=selected.tracklet_id,
                    owners=recovery_owners,
                    last_y=selected.y,
                    last_frame=frame,
                )
                state.phase = OilMaterialPhase.DRAINING
                record.allowed_tracklet_ids = frozenset({selected.tracklet_id})
                record.reason = "PARTIAL_FILL_DRAIN_DELAYED_REACQUISITION_CONFIRMED"
                records[frame].delayed_reacquisition_selected_id = selected.tracklet_id
                records[frame].release_source = "delayed_reacquisition"
                records[frame].release_source_detail = "delayed_reacquisition"
                state.delayed_recovery_chains = {}
                state.ownerless_barrier = None
                record.barrier_state_override = "released"
                delayed_released = True
            if delayed_released:
                record.owner_chain = state.drain_chain.owners
                return
        established_interface_blocker = bool(
            not self.policy.initial_empty
            and any(
                (
                    owner not in record.dynamic_fill_owner_snapshot
                    and self._chain_is_strong_anchor_interface(chain)
                    for owner, chain in state.chains.items()
                )
            )
        )
        if established_interface_blocker:
            record.dynamic_fill_owner_snapshot = frozenset()
        if chain_ambiguity:
            state.phase = (
                OilMaterialPhase.FILLING
                if record.dynamic_fill_owner_snapshot
                else OilMaterialPhase.OPEN
            )
            record.allowed_tracklet_ids = (
                record.dynamic_fill_owner_snapshot
                if len(record.dynamic_fill_owner_snapshot) == 1
                else frozenset()
                if record.dynamic_fill_owner_snapshot
                else None
            )
        elif len(qualified) == 1:
            confirmed_chain, state.fill_confirmation_profile = qualified[0]
            state.delayed_episode_blocked = False
            if state.ownerless_barrier is not None:
                record.barrier_state_override = "reset"
            state.phase = OilMaterialPhase.FILLED_BARRIER
            state.filled_chain = confirmed_chain.owners
            state.filled_frame = frame
            state.fill_terminal_owner = confirmed_chain.owner
            state.fill_owner_open = True
            state.chains = {}
            state.ownerless_barrier = None
            state.delayed_attempt = None
            state.delayed_recovery_chains = {}
            if confirmed_chain.last.material_veto:
                state.fill_owner_open = False
                record.allowed_tracklet_ids = frozenset()
                record.reason = "FILL_SPAN_MATERIAL_VETO"
            else:
                record.allowed_tracklet_ids = frozenset({confirmed_chain.owner})
                record.reason = "FILL_SPAN_CONFIRMED"
        elif len(qualified) > 1:
            state.chains = {}
            state.phase = OilMaterialPhase.OPEN
            record.allowed_tracklet_ids = frozenset()
            ambiguous_frames.add(frame)
            record.reason = "FILL_COMPLETION_AMBIGUOUS"
        elif not record.dynamic_fill_owner_snapshot:
            state.phase = OilMaterialPhase.OPEN
            record.allowed_tracklet_ids = (
                frozenset() if self.policy.initial_empty else None
            )
            if state.chains:
                record.reason = (
                    "FILL_ESTABLISHED_INTERFACE"
                    if established_interface_blocker
                    else "FILL_EVIDENCE_ACCUMULATING"
                )
            elif self.policy.initial_empty:
                record.reason = "INITIAL_EMPTY_ENTRY_PENDING"
        elif len(record.dynamic_fill_owner_snapshot) == 1:
            state.phase = OilMaterialPhase.FILLING
            record.allowed_tracklet_ids = record.dynamic_fill_owner_snapshot
            record.reason = (
                "FILL_PHASE_REENTRY" if fill_phase_reentered else "FILL_MOTION_OWNER"
            )
            dynamic_owner = next(iter(record.dynamic_fill_owner_snapshot))
            if state.established_fill_chain is not None and (
                not any((row.tracklet_id == dynamic_owner for row in rows))
            ):
                current_anchor, anchor_ambiguous = self._current_fill_anchor_choice(
                    state.established_fill_chain, rows, frame
                )
                if anchor_ambiguous:
                    record.allowed_tracklet_ids = frozenset()
                    ambiguous_frames.add(frame)
                    record.reason = "FILL_CURRENT_ANCHOR_AMBIGUOUS"
                elif current_anchor is not None:
                    record.allowed_tracklet_ids = frozenset({current_anchor})
                    record.transient_owner_chain = _append_unique_owner(
                        state.established_fill_chain.owners, current_anchor
                    )
                    record.reason = "FILL_CURRENT_ANCHOR_HANDOFF"
            if prior_phase is OilMaterialPhase.OPEN and (not fill_phase_reentered):
                chain = state.chains[dynamic_owner]
                predecessor, predecessor_ambiguous = self._fill_onset_predecessor(
                    chain, rows_by_frame, frame
                )
                if predecessor is not None:
                    chain = _prepend_owner(chain, predecessor)
                    state.chains[dynamic_owner] = chain
                self._apply_fill_onset_intent(
                    chain=chain,
                    predecessor=predecessor,
                    predecessor_ambiguous=predecessor_ambiguous,
                    frame=frame,
                    rows_by_frame=rows_by_frame,
                    ambiguous_frames=ambiguous_frames,
                    records=records,
                )
            state.established_fill_chain = state.chains[dynamic_owner]
        else:
            state.phase = OilMaterialPhase.FILLING
            record.allowed_tracklet_ids = frozenset()
            ambiguous_frames.add(frame)
            record.reason = "FILL_OWNER_AMBIGUOUS"

    def _transition_barrier(
        self,
        state: OilPhaseRuntimeState,
        records: list[_OilFrameRecord],
        rows_by_frame: tuple[tuple[_ObservedRow, ...], ...],
        first_frame: dict[str, int],
        frame: int,
        ambiguous_frames: set[int],
    ) -> None:
        record = records[frame]
        rows = rows_by_frame[frame]
        terminal = (
            None
            if state.fill_terminal_owner is None
            else next(
                (row for row in rows if row.tracklet_id == state.fill_terminal_owner),
                None,
            )
        )
        if (
            state.fill_owner_open
            and terminal is not None
            and (not terminal.current_material_veto)
        ):
            state.recovery_chains = {}
            records[frame].recovery_reset_reason = "release_context_changed"
            record.allowed_tracklet_ids = frozenset({state.fill_terminal_owner})
            record.reason = "FILL_OWNER_AT_ENTRANCE"
            record.owner_chain = state.filled_chain
            return
        state.fill_owner_open = False
        records[frame].release_stage = "initial_full_drain_release"
        records[frame].release_evaluation = tuple(
            (self._drain_release_evaluation(row) for row in rows)
        )
        releases = tuple(
            (
                row
                for row in rows
                if state.filled_frame is not None
                and first_frame.get(row.tracklet_id, -1) >= state.filled_frame
                and self._drain_release(row)
            )
        )
        release_ids = tuple(sorted({row.tracklet_id for row in releases}))
        records[frame].release_qualifying_ids = release_ids
        if len(release_ids) == 1:
            release = next(
                (row for row in releases if row.tracklet_id == release_ids[0])
            )
            state.drain_chain = _DrainChain(
                owner=release.tracklet_id,
                owners=(release.tracklet_id,),
                last_y=release.y,
                last_frame=frame,
            )
            state.phase = OilMaterialPhase.DRAINING
            record.allowed_tracklet_ids = frozenset({state.drain_chain.owner})
            record.reason = "DRAIN_RELEASE_CONFIRMED"
            records[frame].release_selected_id = release.tracklet_id
            records[frame].release_source = "direct"
            records[frame].release_source_detail = "direct"
            state.recovery_chains = {}
        elif len(release_ids) > 1:
            state.recovery_chains = {}
            records[frame].recovery_reset_reason = "direct_ambiguity"
            record.allowed_tracklet_ids = frozenset()
            record.reason = "DRAIN_RELEASE_AMBIGUOUS"
            ambiguous_frames.add(frame)
            records[frame].release_ambiguous = True
        else:
            record.allowed_tracklet_ids = frozenset()
            record.reason = (
                "DRAIN_RELEASE_AMBIGUOUS"
                if len(release_ids) > 1
                else "INITIAL_FULL_BARRIER"
                if self.policy.initial_full and (not state.filled_chain)
                else "FILLED_CAP_VETO"
            )
            if len(release_ids) > 1:
                ambiguous_frames.add(frame)
                records[frame].release_ambiguous = True
            records[frame].recovery_stage = (
                "initial_full" if self.policy.initial_full else "not_evaluated"
            )
            records[frame].recovery_evaluated = self.policy.initial_full
            state.recovery_chains, recovery_result = self.release_evidence.advance(
                state.recovery_chains,
                rows if self.policy.initial_full else (),
                frame,
                stage="initial_full",
                seed_rows=tuple(
                    (
                        row
                        for row in rows
                        if self.policy.initial_full
                        and state.filled_frame is not None
                        and (first_frame.get(row.tracklet_id, -1) >= state.filled_frame)
                    )
                ),
                established_fill=None,
                contradicted_owner_ids=record.identity_contradictions,
            )
            records[frame].recovery_active = recovery_result["active"]
            records[frame].recovery_predicates = recovery_result["predicates"]
            records[frame].recovery_reset_reason = recovery_result["reset_reason"]
            records[frame].recovery_ambiguous = recovery_result["ambiguous"]
            records[frame].recovery_ambiguous_seed_owner_ids = recovery_result[
                "ambiguous_seed_owner_ids"
            ]
            qualifying = tuple(
                sorted(
                    recovery_result["qualifying"],
                    key=lambda item: (item[0], item[1].tracklet_id),
                )
            )
            records[frame].recovery_qualifying_ids = tuple(
                (row.tracklet_id for _key, row in qualifying)
            )
            if recovery_result["ambiguous"]:
                record.allowed_tracklet_ids = frozenset()
                ambiguous_frames.add(frame)
                record.reason = "DRAIN_RELEASE_RECOVERY_AMBIGUOUS"
            elif len(qualifying) == 1:
                _key, selected = qualifying[0]
                state.drain_chain = _DrainChain(
                    owner=selected.tracklet_id,
                    owners=state.recovery_chains[_key].owners,
                    last_y=selected.y,
                    last_frame=frame,
                )
                state.phase = OilMaterialPhase.DRAINING
                record.allowed_tracklet_ids = frozenset({selected.tracklet_id})
                record.reason = "DRAIN_RELEASE_RECOVERY_CONFIRMED"
                records[frame].recovery_selected_id = selected.tracklet_id
                records[frame].release_source = "recovery"
                records[frame].release_source_detail = "recovery_near_snapshot"
                state.recovery_chains = {}
            elif len(qualifying) > 1:
                state.recovery_chains = {}
                records[frame].recovery_ambiguous = True
                ambiguous_frames.add(frame)
                record.allowed_tracklet_ids = frozenset()
                record.reason = "DRAIN_RELEASE_RECOVERY_AMBIGUOUS"

    def _transition_draining(
        self,
        state: OilPhaseRuntimeState,
        records: list[_OilFrameRecord],
        rows_by_frame: tuple[tuple[_ObservedRow, ...], ...],
        first_frame: dict[str, int],
        frame: int,
        ambiguous_frames: set[int],
    ) -> None:
        record = records[frame]
        rows = rows_by_frame[frame]
        assert state.phase is OilMaterialPhase.DRAINING
        if state.drain_chain is None:
            record.allowed_tracklet_ids = frozenset()
            record.reason = "DRAIN_CHAIN_RESET"
        else:
            direct = next(
                (row for row in rows if row.tracklet_id == state.drain_chain.owner),
                None,
            )
            if direct is not None and self._drain_refill_closure(
                state.drain_chain, direct
            ):
                state.filled_chain = state.drain_chain.owners
                state.filled_frame = frame
                state.fill_terminal_owner = direct.tracklet_id
                state.fill_owner_open = True
                state.phase = OilMaterialPhase.FILLED_BARRIER
                record.allowed_tracklet_ids = frozenset({direct.tracklet_id})
                record.reason = "DRAIN_REFILL_CLOSURE_CONFIRMED"
                state.drain_chain = None
                state.recovery_chains = {}
            elif direct is not None and self._drain_continuation(
                state.drain_chain, direct, frame
            ):
                state.drain_chain = _DrainChain(
                    owner=state.drain_chain.owner,
                    owners=state.drain_chain.owners,
                    last_y=direct.y,
                    last_frame=frame,
                )
                record.allowed_tracklet_ids = frozenset({state.drain_chain.owner})
                record.reason = "DRAIN_OWNER_CONTINUING"
            else:
                successors = tuple(
                    (
                        row
                        for row in rows
                        if row.tracklet_id != state.drain_chain.owner
                        and self._drain_successor(state.drain_chain, row, frame)
                    )
                )
                if successors:
                    maturity = max((_tracklet_maturity(row.ref) for row in successors))
                    successors = tuple(
                        (
                            row
                            for row in successors
                            if _tracklet_maturity(row.ref) == maturity
                        )
                    )
                ranked = tuple(
                    sorted(
                        (
                            (
                                self._drain_handoff_cost(state.drain_chain, row, frame),
                                row.tracklet_id,
                                row,
                            )
                            for row in successors
                        )
                    )
                )
                chosen_id = _clear_choice(
                    tuple(((cost, tracklet_id) for cost, tracklet_id, _row in ranked)),
                    self.policy.handoff_ambiguity_margin,
                )
                if chosen_id is None and ranked:
                    record.allowed_tracklet_ids = frozenset()
                    ambiguous_frames.add(frame)
                    record.reason = "DRAIN_HANDOFF_AMBIGUOUS"
                elif chosen_id is not None:
                    successor = next(
                        (
                            row
                            for _cost, tracklet_id, row in ranked
                            if tracklet_id == chosen_id
                        )
                    )
                    state.drain_chain = _DrainChain(
                        owner=successor.tracklet_id,
                        owners=state.drain_chain.owners + (successor.tracklet_id,),
                        last_y=successor.y,
                        last_frame=frame,
                    )
                    record.allowed_tracklet_ids = frozenset({state.drain_chain.owner})
                    record.reason = "DRAIN_CHAIN_HANDOFF"
                else:
                    owner_terminated = (
                        frame - state.drain_chain.last_frame - 1
                        > self.policy.maximum_lost_frames
                    )
                    refill_reentries = (
                        tuple(
                            (
                                row
                                for row in rows
                                if row.tracklet_id != state.drain_chain.owner
                                and self._drain_refill_handoff(state.drain_chain, row)
                            )
                        )
                        if direct is None
                        else ()
                    )
                    refill_ids = tuple(
                        sorted({row.tracklet_id for row in refill_reentries})
                    )
                    if len(refill_ids) == 1:
                        refill = next(
                            (
                                row
                                for row in refill_reentries
                                if row.tracklet_id == refill_ids[0]
                            )
                        )
                        state.filled_chain = _append_unique_owner(
                            state.drain_chain.owners, refill.tracklet_id
                        )
                        state.filled_frame = frame
                        state.fill_terminal_owner = refill.tracklet_id
                        state.fill_owner_open = True
                        state.phase = OilMaterialPhase.FILLED_BARRIER
                        record.allowed_tracklet_ids = frozenset({refill.tracklet_id})
                        record.reason = "DRAIN_REFILL_HANDOFF_CONFIRMED"
                        state.drain_chain = None
                        state.recovery_chains = {}
                        reentries = ()
                    elif len(refill_ids) > 1:
                        record.allowed_tracklet_ids = frozenset()
                        ambiguous_frames.add(frame)
                        record.reason = "DRAIN_REFILL_HANDOFF_AMBIGUOUS"
                        reentries = ()
                    else:
                        reentries = (
                            tuple(
                                (
                                    row
                                    for row in rows
                                    if self._drain_phase_reentry(state.drain_chain, row)
                                )
                            )
                            if owner_terminated
                            else ()
                        )
                    if state.phase is OilMaterialPhase.FILLED_BARRIER:
                        pass
                    elif len(refill_ids) > 1:
                        pass
                    elif reentries:
                        maturity = max(
                            (_tracklet_maturity(row.ref) for row in reentries)
                        )
                        reentries = tuple(
                            (
                                row
                                for row in reentries
                                if _tracklet_maturity(row.ref) == maturity
                            )
                        )
                    reentry_ranked = tuple(
                        sorted(
                            (
                                (
                                    self._drain_phase_reentry_cost(
                                        state.drain_chain, row
                                    ),
                                    row.tracklet_id,
                                    row,
                                )
                                for row in reentries
                            )
                        )
                    )
                    reentry_id = _clear_choice(
                        tuple(
                            (
                                (cost, tracklet_id)
                                for cost, tracklet_id, _row in reentry_ranked
                            )
                        ),
                        self.policy.handoff_ambiguity_margin,
                    )
                    if state.phase is OilMaterialPhase.FILLED_BARRIER:
                        pass
                    elif len(refill_ids) > 1:
                        pass
                    elif reentry_id is None and reentry_ranked:
                        record.allowed_tracklet_ids = frozenset()
                        ambiguous_frames.add(frame)
                        record.reason = "DRAIN_REENTRY_AMBIGUOUS"
                    elif reentry_id is not None:
                        reentry = next(
                            (
                                row
                                for _cost, tracklet_id, row in reentry_ranked
                                if tracklet_id == reentry_id
                            )
                        )
                        state.drain_chain = _DrainChain(
                            owner=reentry.tracklet_id,
                            owners=_append_unique_owner(
                                state.drain_chain.owners, reentry.tracklet_id
                            ),
                            last_y=reentry.y,
                            last_frame=frame,
                        )
                        record.allowed_tracklet_ids = frozenset(
                            {state.drain_chain.owner}
                        )
                        record.reason = "DRAIN_PHASE_REENTRY"
                    else:
                        record.allowed_tracklet_ids = frozenset()
                        record.reason = (
                            "DRAIN_OWNER_TERMINATED"
                            if owner_terminated
                            else "DRAIN_OWNER_LOST"
                        )

    def _capture_frame_runtime(
        self, record: _OilFrameRecord, runtime: OilPhaseRuntimeState, frame: int
    ) -> None:
        record.established_fill_snapshot = runtime.established_fill_chain
        record.dynamic_fill_owner_snapshot = record.dynamic_fill_owner_snapshot
        barrier = runtime.ownerless_barrier
        attempt_consumed = bool(
            runtime.delayed_attempt is not None and runtime.delayed_attempt.consumed
        )
        record.ownerless_barrier_attempt_consumed = attempt_consumed
        if barrier is None:
            record.ownerless_barrier_state = record.barrier_state_override or "inactive"
            record.ownerless_barrier_loss_epoch = None
            record.ownerless_barrier_loss_age = None
            return
        record.ownerless_barrier_loss_epoch = barrier.loss_frame
        record.ownerless_barrier_loss_age = frame - barrier.loss_frame
        if record.barrier_state_override is not None:
            record.ownerless_barrier_state = record.barrier_state_override
        elif attempt_consumed:
            record.ownerless_barrier_state = (
                "attempt_active"
                if runtime.delayed_recovery_chains
                else "attempt_consumed"
            )
        elif frame - barrier.loss_frame < barrier.grace_limit:
            record.ownerless_barrier_state = "grace"
        else:
            record.ownerless_barrier_state = "available"

    def _serialize_frame(self, record: _OilFrameRecord) -> dict[str, object]:
        allowed = record.allowed_tracklet_ids
        established = record.established_fill_snapshot
        return {
            "schema_version": "r21-truth-preserving-detector-repair-v1",
            "legacy_schema_version": "r20-delayed-drain-reacquisition-v1",
            "initial_state": None
            if self.policy.confirmed_initial_state is None
            else self.policy.confirmed_initial_state.value,
            "initial_empty": self.policy.initial_empty,
            "initial_full": self.policy.initial_full,
            "allowed_mode": "unconstrained"
            if allowed is None
            else "hard_gate"
            if not allowed
            else "owner_bounded",
            "allowed_tracklet_ids": None if allowed is None else sorted(allowed),
            "dynamic_fill_owner_ids": sorted(record.dynamic_fill_owner_snapshot),
            "established_fill_present": established is not None,
            "established_fill_owner": None
            if established is None
            else established.owner,
            "established_fill_owner_chain": []
            if established is None
            else list(established.owners),
            "established_fill_last_y": None
            if established is None
            else established.last.y,
            "established_fill_last_frame": None
            if established is None
            else established.last.frame,
            "release_stage": record.release_stage,
            "release_evaluated": bool(record.release_evaluation),
            "release_qualifying_tracklet_ids": list(record.release_qualifying_ids),
            "release_selected_tracklet_id": record.release_selected_id,
            "release_ambiguous": record.release_ambiguous,
            "release_evaluations": [
                item.as_debug_dict() for item in record.release_evaluation
            ],
            "recovery_stage": record.recovery_stage,
            "recovery_evaluated": record.recovery_evaluated,
            "recovery_active_chains": list(record.recovery_active),
            "recovery_ordered_predicates": list(record.recovery_predicates),
            "recovery_qualifying_tracklet_ids": list(record.recovery_qualifying_ids),
            "recovery_selected_tracklet_id": record.recovery_selected_id,
            "recovery_ambiguous": record.recovery_ambiguous,
            "recovery_ambiguous_seed_owner_ids": list(
                record.recovery_ambiguous_seed_owner_ids
            ),
            "recovery_reset_reason": record.recovery_reset_reason,
            "release_source": record.release_source,
            "release_source_detail": record.release_source_detail,
            "release_evaluation_order": [
                "direct",
                "recovery_near_snapshot",
                "delayed_reacquisition",
            ],
            "ownerless_barrier_state": record.ownerless_barrier_state,
            "ownerless_barrier_loss_epoch": record.ownerless_barrier_loss_epoch,
            "ownerless_barrier_loss_age": record.ownerless_barrier_loss_age,
            "ownerless_barrier_grace_limit": record.ownerless_barrier_grace_limit,
            "ownerless_barrier_attempt_consumed": record.ownerless_barrier_attempt_consumed,
            "delayed_reacquisition_evaluated": record.delayed_reacquisition_evaluated,
            "delayed_reacquisition_seed_predicates": list(
                record.delayed_reacquisition_seed_predicates
            ),
            "delayed_reacquisition_active_chains": list(
                record.delayed_reacquisition_active
            ),
            "delayed_reacquisition_qualifying_tracklet_ids": list(
                record.delayed_reacquisition_qualifying_ids
            ),
            "delayed_reacquisition_selected_tracklet_id": record.delayed_reacquisition_selected_id,
            "delayed_reacquisition_ambiguous": record.delayed_reacquisition_ambiguous,
            "delayed_reacquisition_reset_reason": record.delayed_reacquisition_reset_reason,
            "delayed_reacquisition_snapshot_distance_px": record.delayed_reacquisition_snapshot_distance,
            "delayed_reacquisition_snapshot_distance_used_for_identity": False,
            "delayed_reacquisition_seed_frame": record.delayed_reacquisition_seed_frame,
            "policy": {
                "geometry_top_y": self.policy.geometry_top_y,
                "geometry_height": self.policy.geometry_height,
                "maximum_jump_px": self.policy.maximum_jump_px,
                "drain_entrance_ratio": self.policy.drain_entrance_ratio,
                "drain_minimum_progress_ratio": self.policy.drain_minimum_progress_ratio,
                "drain_minimum_directional_agreement": self.policy.drain_minimum_directional_agreement,
                "material_conflict_limit": self.policy.material_conflict_limit,
            },
        }

    def _fill_onset_predecessor(
        self,
        chain: _FillChain,
        rows_by_frame: tuple[tuple[_ObservedRow, ...], ...],
        frame: int,
    ) -> tuple[str | None, bool]:
        if frame <= 0:
            return (None, False)
        origin_y = chain.observations[0].y
        candidates = tuple(
            (
                row
                for row in rows_by_frame[frame - 1]
                if row.ref.tracklet_admitted
                and (not row.ref.tracklet_incompatible)
                and (abs(row.y - origin_y) <= self.policy.maximum_jump_px)
            )
        )
        if not candidates:
            return (None, False)
        maturity = max((_tracklet_maturity(row.ref) for row in candidates))
        candidates = tuple(
            (row for row in candidates if _tracklet_maturity(row.ref) == maturity)
        )
        best_cost_by_tracklet: dict[str, float] = {}
        for row in candidates:
            cost = abs(row.y - origin_y) / self.policy.maximum_jump_px
            best_cost_by_tracklet[row.tracklet_id] = min(
                best_cost_by_tracklet.get(row.tracklet_id, math.inf), cost
            )
        ranked = tuple(
            ((cost, tracklet_id) for tracklet_id, cost in best_cost_by_tracklet.items())
        )
        chosen = _clear_choice(ranked, self.policy.handoff_ambiguity_margin)
        return (chosen, chosen is None)

    def _apply_fill_onset_intent(
        self,
        *,
        chain: _FillChain,
        predecessor: str | None,
        predecessor_ambiguous: bool,
        frame: int,
        rows_by_frame: tuple[tuple[_ObservedRow, ...], ...],
        ambiguous_frames: set[int],
        records: list[_OilFrameRecord],
    ) -> None:
        if frame <= 0:
            return
        first = max(0, frame - self.policy.fill_onset_intent_frames)
        if predecessor is None:
            target = frame - 1
            if records[target].phase is not OilMaterialPhase.OPEN:
                return
            records[target].allowed_tracklet_ids = frozenset()
            records[target].owner_chain = chain.owners
            records[target].reason = (
                "FILL_ONSET_INTENT_AMBIGUOUS"
                if predecessor_ambiguous
                else "FILL_ONSET_INTENT_NO_PREDECESSOR"
            )
            if predecessor_ambiguous:
                ambiguous_frames.add(target)
            return
        observed = tuple(
            (
                prior_frame
                for prior_frame in range(first, frame)
                if any(
                    (
                        row.tracklet_id == predecessor
                        for row in rows_by_frame[prior_frame]
                    )
                )
            )
        )
        if not observed:
            return
        for prior_frame in range(observed[0], frame):
            if records[prior_frame].phase is not OilMaterialPhase.OPEN:
                continue
            is_observed = any(
                (row.tracklet_id == predecessor for row in rows_by_frame[prior_frame])
            )
            records[prior_frame].allowed_tracklet_ids = (
                frozenset({predecessor}) if is_observed else frozenset()
            )
            records[prior_frame].owner_chain = chain.owners
            records[prior_frame].reason = (
                "FILL_ONSET_INTENT_PREDECESSOR"
                if is_observed
                else "FILL_ONSET_INTENT_GAP"
            )

    def _chain_is_dynamic_fill_owner(self, chain: _FillChain) -> bool:
        origin_relative = (
            chain.origin_y - self.policy.geometry_top_y
        ) / self.policy.geometry_height
        lower_entrance = origin_relative >= 1.0 - self.policy.entrance_band_ratio
        central_origin = (
            self.policy.entrance_band_ratio
            <= origin_relative
            <= 1.0 - self.policy.entrance_band_ratio
        )
        for observation in chain.observations:
            strong_motion = bool(
                observation.motion_support >= self.policy.fill_minimum_motion_support
                and observation.motion_coverage
                >= self.policy.fill_minimum_motion_coverage
            )
            if self.policy.initial_empty:
                if (
                    lower_entrance
                    and observation.confirmation_profile
                    in {
                        TrackletConfirmationProfile.ANCHOR_CORRIDOR,
                        TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
                        TrackletConfirmationProfile.MOTION_TRAJECTORY,
                    }
                    and (
                        observation.net_progress_px
                        >= max(
                            4.0,
                            self.policy.geometry_height
                            * self.policy.drain_minimum_progress_ratio,
                        )
                    )
                    and (
                        observation.directional_agreement
                        >= self.policy.minimum_directional_agreement
                    )
                    and (strong_motion or observation.independent_anchor)
                ):
                    return True
            elif strong_motion and (
                central_origin
                and observation.confirmation_profile
                is TrackletConfirmationProfile.MOTION_TRAJECTORY
            ):
                return True
        return False

    def _chain_is_strong_anchor_interface(self, chain: _FillChain) -> bool:
        anchor_profiles = {
            TrackletConfirmationProfile.ANCHOR_CORRIDOR,
            TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
        }
        return any(
            (
                observation.confirmation_profile in anchor_profiles
                and observation.motion_support
                >= self.policy.fill_minimum_motion_support
                and (
                    observation.motion_coverage
                    >= self.policy.fill_minimum_motion_coverage
                )
                for observation in chain.observations
            )
        )

    def _advance_fill_chains(
        self, prior: dict[str, _FillChain], rows: tuple[_ObservedRow, ...], frame: int
    ) -> tuple[dict[str, _FillChain], bool, str]:
        upward = {
            row.tracklet_id: row
            for row in rows
            if row.ref.tracklet_admitted
            and (not row.ref.tracklet_incompatible)
            and (row.ref.tracklet_direction < 0)
            and (
                row.ref.tracklet_directional_agreement
                >= self.policy.minimum_directional_agreement
            )
        }
        retained = {
            owner: chain
            for owner, chain in prior.items()
            if frame - chain.last.frame - 1 <= self.policy.maximum_lost_frames
        }
        current: dict[str, _FillChain] = {
            owner: chain for owner, chain in retained.items() if owner not in upward
        }
        for owner, row in upward.items():
            if owner not in retained:
                continue
            current[owner] = _extend_chain(
                retained[owner], row, frame, self.policy.fill_evidence_window_frames
            )
        successors = {
            owner: row for owner, row in upward.items() if owner not in current
        }
        predecessors: dict[str, tuple[tuple[float, _FillChain], ...]] = {}
        for owner, row in successors.items():
            matches = tuple(
                (
                    (self._handoff_cost(chain, row, frame), chain)
                    for prior_owner, chain in retained.items()
                    if prior_owner not in upward
                    and self._compatible_handoff(chain, row, frame)
                )
            )
            predecessors[owner] = tuple(
                sorted(matches, key=lambda item: (item[0], item[1].owner))
            )
        by_predecessor: dict[str, list[tuple[float, str]]] = {}
        for successor, matches in predecessors.items():
            for cost, chain in matches:
                by_predecessor.setdefault(chain.owner, []).append((cost, successor))
        successor_choices = {
            owner: _clear_choice(
                tuple(((cost, chain.owner) for cost, chain in matches)),
                self.policy.handoff_ambiguity_margin,
            )
            for owner, matches in predecessors.items()
            if matches
        }
        predecessor_choices = {
            owner: _clear_choice(
                tuple(sorted(options)), self.policy.handoff_ambiguity_margin
            )
            for owner, options in by_predecessor.items()
        }
        ambiguous_successors = {
            owner for owner, choice in successor_choices.items() if choice is None
        }
        ambiguous_predecessors = {
            owner for owner, choice in predecessor_choices.items() if choice is None
        }
        for owner, row in successors.items():
            matches = predecessors[owner]
            chosen_predecessor = successor_choices.get(owner)
            if (
                chosen_predecessor is not None
                and predecessor_choices.get(chosen_predecessor) == owner
            ):
                predecessor = next(
                    (
                        chain
                        for _cost, chain in matches
                        if chain.owner == chosen_predecessor
                    )
                )
                current.pop(predecessor.owner, None)
                current[owner] = _handoff_chain(
                    predecessor, row, frame, self.policy.fill_evidence_window_frames
                )
                continue
            if not matches:
                current[owner] = _new_chain(row, frame)
                continue
            if (
                owner not in ambiguous_successors
                and chosen_predecessor not in ambiguous_predecessors
            ):
                current[owner] = _new_chain(row, frame)
        ambiguous = bool(ambiguous_successors or ambiguous_predecessors)
        if ambiguous:
            involved = set(ambiguous_predecessors) | set(ambiguous_successors)
            for successor in ambiguous_successors:
                involved.update(
                    (chain.owner for _cost, chain in predecessors[successor])
                )
            for owner in involved:
                current.pop(owner, None)
            return (current, True, "FILL_CHAIN_AMBIGUOUS")
        if any((len(chain.owners) > 1 for chain in current.values())):
            return (current, False, "FILL_CHAIN_HANDOFF")
        return (current, False, "FILLING_TRACKLET")

    def _compatible_handoff(
        self, chain: _FillChain, row: _ObservedRow, frame: int
    ) -> bool:
        gap = frame - chain.last.frame
        return bool(
            1 <= gap <= self.policy.maximum_lost_frames + 1
            and row.y <= chain.last.y + self.policy.maximum_jump_px * gap
            and (abs(row.y - chain.last.y) <= self.policy.maximum_jump_px * gap)
        )

    def _fill_phase_reentry(
        self, chain: _FillChain, row: _ObservedRow, frame: int
    ) -> bool:
        gap = frame - chain.last.frame
        return bool(
            1 <= gap <= self.policy.fill_evidence_window_frames * 2
            and _bounded_confirmed_observation(row.ref)
            and (not row.ref.tracklet_incompatible)
            and (not row.current_material_veto)
            and (row.ref.tracklet_direction < 0)
            and (
                row.ref.tracklet_directional_agreement
                >= self.policy.minimum_directional_agreement
            )
            and (
                row.ref.tracklet_material_conflict < self.policy.material_conflict_limit
            )
            and (row.current_material_conflict < self.policy.material_conflict_limit)
            and (
                row.y
                <= chain.last.y + self.policy.handoff_direction_reversal_tolerance_px
            )
            and (abs(row.y - chain.last.y) <= self.policy.maximum_jump_px)
        )

    def _current_fill_anchor_choice(
        self, chain: _FillChain, rows: tuple[_ObservedRow, ...], frame: int
    ) -> tuple[str | None, bool]:
        ranked = tuple(
            sorted(
                (
                    (
                        abs(row.y - chain.last.y) / self.policy.maximum_jump_px,
                        row.tracklet_id,
                    )
                    for row in rows
                    if self._is_current_fill_anchor_handoff(chain, row, frame)
                )
            )
        )
        chosen = _clear_choice(ranked, self.policy.handoff_ambiguity_margin)
        return (chosen, bool(ranked and chosen is None))

    def _is_current_fill_anchor_handoff(
        self, chain: _FillChain, row: _ObservedRow, frame: int
    ) -> bool:
        """Authorize one current observation without changing phase history.

        A strong same-frame material anchor can inherit stale direction from a
        different physical track history.  It may temporarily own the current
        observation when it remains geometrically connected to an established
        fill owner.  The phase chain itself is intentionally left untouched so
        one anchor cannot reopen a completed-material barrier.
        """
        gap = frame - chain.last.frame
        if (
            not 1 <= gap <= self.policy.maximum_lost_frames + 1
            or not _bounded_confirmed_observation(row.ref)
            or row.ref.tracklet_incompatible
            or (
                row.ref.tracklet_confirmation_profile
                not in {
                    TrackletConfirmationProfile.ANCHOR_CORRIDOR,
                    TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
                }
            )
            or (
                row.ref.tracklet_motion_support
                < self.policy.fill_minimum_motion_support
            )
            or (
                row.ref.tracklet_motion_coverage
                < self.policy.fill_minimum_motion_coverage
            )
            or (
                row.y
                > chain.last.y + self.policy.handoff_direction_reversal_tolerance_px
            )
            or (abs(row.y - chain.last.y) > self.policy.maximum_jump_px * gap)
        ):
            return False
        material_refs = tuple(
            (
                node.candidate_ref
                for node in row.nodes
                if node.candidate_ref is not None
                and node.candidate_ref.evidence.material_path
            )
        )
        return bool(
            material_refs
            and any(
                (
                    ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                    for ref in material_refs
                )
            )
        )

    def _handoff_cost(self, chain: _FillChain, row: _ObservedRow, frame: int) -> float:
        gap = max(1, frame - chain.last.frame)
        return abs(row.y - chain.last.y) / (self.policy.maximum_jump_px * gap)

    def _fill_confirmation_profile(
        self, chain: _FillChain
    ) -> OilFillConfirmationProfile:
        observations = chain.observations
        if len(observations) < 3:
            return OilFillConfirmationProfile.NONE
        first = observations[0]
        last = observations[-1]
        relative = (last.y - self.policy.geometry_top_y) / self.policy.geometry_height
        deltas = tuple(
            (
                following.y - prior.y
                for prior, following in zip(observations, observations[1:])
            )
        )
        directional_agreement = sum((delta <= 0.0 for delta in deltas)) / len(deltas)
        geometry_confirmed = bool(
            relative <= self.policy.entrance_band_ratio
            and (chain.origin_y if self.policy.initial_empty else first.y) - last.y
            >= self.policy.geometry_height * self.policy.fill_minimum_span_ratio
            and (directional_agreement >= self.policy.minimum_directional_agreement)
        )
        if not geometry_confirmed:
            return OilFillConfirmationProfile.NONE
        if any((item.independent_anchor for item in observations)):
            return OilFillConfirmationProfile.UNKNOWN_FILL_ANCHORED
        lower_entrance = (
            (chain.origin_y if self.policy.initial_empty else first.y)
            - self.policy.geometry_top_y
        ) / self.policy.geometry_height >= 1.0 - self.policy.entrance_band_ratio
        strong_entrance_motion = any(
            (
                item.confirmation_profile
                in {
                    TrackletConfirmationProfile.ANCHOR_CORRIDOR,
                    TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
                    TrackletConfirmationProfile.MOTION_TRAJECTORY,
                }
                and item.net_progress_px
                >= max(
                    4.0,
                    self.policy.geometry_height
                    * self.policy.drain_minimum_progress_ratio,
                )
                and (
                    item.directional_agreement
                    >= self.policy.minimum_directional_agreement
                )
                and (
                    item.independent_anchor
                    or (
                        item.motion_support >= self.policy.fill_minimum_motion_support
                        and item.motion_coverage
                        >= self.policy.fill_minimum_motion_coverage
                    )
                )
                for item in observations
            )
        )
        if self.policy.initial_empty and lower_entrance and strong_entrance_motion:
            return OilFillConfirmationProfile.EMPTY_ENTRANCE_MOTION
        return OilFillConfirmationProfile.NONE

    def _partial_fill_drain_release_choice(
        self, established_fill: _FillChain, rows: tuple[_ObservedRow, ...]
    ) -> tuple[_ObservedRow | None, bool]:
        releases = tuple(
            (
                row
                for row in rows
                if self._partial_fill_drain_release(established_fill, row)
            )
        )
        ranked = tuple(
            sorted(
                (
                    (
                        abs(row.y - established_fill.last.y)
                        / self.policy.maximum_jump_px,
                        row.tracklet_id,
                        row,
                    )
                    for row in releases
                )
            )
        )
        selected_id = _clear_choice(
            tuple(((cost, tracklet_id) for cost, tracklet_id, _row in ranked)),
            self.policy.handoff_ambiguity_margin,
        )
        if selected_id is None:
            return (None, bool(ranked))
        return (
            next(
                (
                    row
                    for _cost, tracklet_id, row in ranked
                    if tracklet_id == selected_id
                )
            ),
            False,
        )

    def _partial_fill_drain_release(
        self, established_fill: _FillChain, row: _ObservedRow
    ) -> bool:
        return self._partial_fill_drain_release_evaluation(established_fill, row).passed

    def _partial_fill_drain_release_evaluation(
        self, established_fill: _FillChain, row: _ObservedRow
    ) -> OilReleasePredicateEvaluation:
        minimum_progress = max(
            4.0, self.policy.geometry_height * self.policy.drain_minimum_progress_ratio
        )
        predicates = (
            ("bounded_confirmed", _bounded_confirmed_observation(row.ref)),
            ("compatible", not row.ref.tracklet_incompatible),
            ("downward_direction", row.ref.tracklet_direction > 0),
            ("minimum_progress", row.ref.tracklet_net_progress_px >= minimum_progress),
            (
                "directional_agreement",
                row.ref.tracklet_directional_agreement
                >= self.policy.drain_minimum_directional_agreement,
            ),
            (
                "reversal_lower_bound",
                row.y
                >= established_fill.last.y
                - self.policy.handoff_direction_reversal_tolerance_px,
            ),
            (
                "maximum_jump",
                abs(row.y - established_fill.last.y) <= self.policy.maximum_jump_px,
            ),
            ("current_material_veto_clear", not row.current_material_veto),
            (
                "tracklet_material_conflict",
                row.ref.tracklet_material_conflict
                < self.policy.material_conflict_limit,
            ),
            (
                "current_material_conflict",
                row.current_material_conflict < self.policy.material_conflict_limit,
            ),
        )
        return self._release_evaluation(
            stage="partial_fill_drain_release",
            row=row,
            predicates=predicates,
            minimum_progress=minimum_progress,
            entrance_relative=None,
            established_fill_last_y=established_fill.last.y,
        )

    def _drain_release(self, row: _ObservedRow) -> bool:
        return self._drain_release_evaluation(row).passed

    def _drain_release_evaluation(
        self, row: _ObservedRow
    ) -> OilReleasePredicateEvaluation:
        relative = (
            row.entrance_y - self.policy.geometry_top_y
        ) / self.policy.geometry_height
        minimum_progress = max(
            4.0, self.policy.geometry_height * self.policy.drain_minimum_progress_ratio
        )
        if self.policy.initial_full:
            direction = row.ref.tracklet_recent_direction
            progress = row.ref.tracklet_recent_net_progress_px
            directional_agreement = row.ref.tracklet_recent_directional_agreement
        else:
            direction = row.ref.tracklet_direction
            progress = row.ref.tracklet_net_progress_px
            directional_agreement = row.ref.tracklet_directional_agreement
        predicates = (
            ("bounded_confirmed", _bounded_confirmed_observation(row.ref)),
            ("compatible", not row.ref.tracklet_incompatible),
            ("downward_direction", direction > 0),
            ("minimum_progress", progress >= minimum_progress),
            (
                "directional_agreement",
                directional_agreement
                >= self.policy.drain_minimum_directional_agreement,
            ),
            ("entrance_relative", relative <= self.policy.drain_entrance_ratio),
            ("current_material_veto_clear", not row.current_material_veto),
            (
                "tracklet_material_conflict",
                row.ref.tracklet_material_conflict
                < self.policy.material_conflict_limit,
            ),
            (
                "current_material_conflict",
                row.current_material_conflict < self.policy.material_conflict_limit,
            ),
        )
        return self._release_evaluation(
            stage="initial_full_drain_release",
            row=row,
            predicates=predicates,
            minimum_progress=minimum_progress,
            entrance_relative=relative,
            established_fill_last_y=None,
            tracklet_progress_px=progress,
            directional_agreement=directional_agreement,
        )

    def _release_evaluation(
        self,
        *,
        stage: str,
        row: _ObservedRow,
        predicates: tuple[tuple[str, bool], ...],
        minimum_progress: float,
        entrance_relative: float | None,
        established_fill_last_y: float | None,
        tracklet_progress_px: float | None = None,
        directional_agreement: float | None = None,
    ) -> OilReleasePredicateEvaluation:
        return OilReleasePredicateEvaluation(
            stage=stage,
            tracklet_id=row.tracklet_id,
            row_hypothesis_id=row.row_hypothesis_id,
            row_y=row.y,
            entrance_y=row.entrance_y,
            entrance_relative=entrance_relative,
            established_fill_last_y=established_fill_last_y,
            minimum_progress_px=minimum_progress,
            maximum_jump_px=self.policy.maximum_jump_px,
            tracklet_progress_px=row.ref.tracklet_net_progress_px
            if tracklet_progress_px is None
            else tracklet_progress_px,
            directional_agreement=row.ref.tracklet_directional_agreement
            if directional_agreement is None
            else directional_agreement,
            current_material_veto=row.current_material_veto,
            tracklet_material_conflict=row.ref.tracklet_material_conflict,
            current_material_conflict=row.current_material_conflict,
            predicates=predicates,
        )

    def _drain_successor(
        self, chain: _DrainChain, row: _ObservedRow, frame: int
    ) -> bool:
        gap = frame - chain.last_frame
        return bool(
            1 <= gap <= self.policy.maximum_lost_frames + 1
            and self._drain_observation_supported(row)
            and (
                row.y
                >= chain.last_y - self.policy.handoff_direction_reversal_tolerance_px
            )
            and (abs(row.y - chain.last_y) <= self.policy.maximum_jump_px * gap)
        )

    def _drain_refill_closure(self, chain: _DrainChain, row: _ObservedRow) -> bool:
        relative = (row.y - self.policy.geometry_top_y) / self.policy.geometry_height
        minimum_refill_span = max(
            4.0, self.policy.geometry_height * self.policy.fill_minimum_span_ratio
        )
        minimum_recent_progress = max(
            4.0, self.policy.geometry_height * self.policy.drain_minimum_progress_ratio
        )
        bounded_refill_witness = bool(
            row.ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
            or (
                row.ref.tracklet_motion_support
                >= self.policy.fill_minimum_motion_support
                and row.ref.tracklet_motion_coverage
                >= self.policy.fill_minimum_motion_coverage
            )
        )
        return bool(
            row.tracklet_id == chain.owner
            and _bounded_confirmed_observation(row.ref)
            and (not row.ref.tracklet_incompatible)
            and (row.ref.tracklet_recent_direction < 0)
            and (
                row.ref.tracklet_recent_directional_agreement
                >= self.policy.minimum_directional_agreement
            )
            and (row.ref.tracklet_recent_net_progress_px >= minimum_recent_progress)
            and (chain.last_y - row.y >= minimum_refill_span)
            and (relative <= self.policy.entrance_band_ratio)
            and bounded_refill_witness
            and self.release_evidence._strict_material_support(row)
        )

    def _drain_refill_handoff(self, chain: _DrainChain, row: _ObservedRow) -> bool:
        """Close a rapid refill through a fresh independently proven owner.

        This is phase ownership transfer, not tracklet continuation.  The old
        drain identity may be inside bounded loss or already terminated after
        a high-speed reversal; a distinct confirmed upward owner may close only
        after proving its own bounded trajectory, top entrance, span and
        material support.  No prior row or coordinate is copied into the new
        owner.
        """
        relative = (row.y - self.policy.geometry_top_y) / self.policy.geometry_height
        minimum_refill_span = max(
            4.0, self.policy.geometry_height * self.policy.fill_minimum_span_ratio
        )
        minimum_recent_progress = max(
            4.0, self.policy.geometry_height * self.policy.drain_minimum_progress_ratio
        )
        bounded_refill_witness = bool(
            row.ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
            and row.ref.tracklet_motion_support
            >= self.policy.fill_minimum_motion_support
            and (
                row.ref.tracklet_motion_coverage
                >= self.policy.fill_minimum_motion_coverage
            )
        )
        return bool(
            _bounded_confirmed_observation(row.ref)
            and (not row.ref.tracklet_incompatible)
            and (row.ref.tracklet_recent_direction < 0)
            and (
                row.ref.tracklet_recent_directional_agreement
                >= self.policy.minimum_directional_agreement
            )
            and (row.ref.tracklet_recent_net_progress_px >= minimum_recent_progress)
            and (chain.last_y - row.y >= minimum_refill_span)
            and (relative <= self.policy.entrance_band_ratio)
            and bounded_refill_witness
            and self.release_evidence._strict_material_support(row)
        )

    def _drain_continuation(
        self, chain: _DrainChain, row: _ObservedRow, frame: int
    ) -> bool:
        gap = frame - chain.last_frame
        return bool(
            1 <= gap <= self.policy.maximum_lost_frames + 1
            and self._drain_observation_supported(row)
            and (
                row.y
                >= chain.last_y - self.policy.handoff_direction_reversal_tolerance_px
            )
            and (abs(row.y - chain.last_y) <= self.policy.maximum_jump_px * gap)
        )

    def _drain_handoff_cost(
        self, chain: _DrainChain, row: _ObservedRow, frame: int
    ) -> float:
        gap = max(1, frame - chain.last_frame)
        return abs(row.y - chain.last_y) / (self.policy.maximum_jump_px * gap)

    def _drain_phase_reentry(self, chain: _DrainChain, row: _ObservedRow) -> bool:
        """Reobserve an established drain phase without joining track IDs.

        A physical tracklet terminates after its bounded loss interval.  The
        material phase does not: after a longer occlusion, a newly confirmed
        downward row may become the phase owner only when its own evidence is
        valid and it remains within one ordinary physical jump of the last
        observed drain row.  This transfers phase ownership while preserving
        both tracklet identities in the owner chain.
        """
        return bool(
            self._drain_observation_supported(row)
            and row.y
            >= chain.last_y - self.policy.handoff_direction_reversal_tolerance_px
            and (abs(row.y - chain.last_y) <= self.policy.maximum_jump_px)
        )

    def _drain_observation_supported(self, row: _ObservedRow) -> bool:
        return bool(
            _bounded_confirmed_observation(row.ref)
            and (not row.ref.tracklet_incompatible)
            and (row.ref.tracklet_direction > 0)
            and (
                row.ref.tracklet_directional_agreement
                >= self.policy.drain_minimum_directional_agreement
            )
            and (
                self.release_evidence._strict_material_support(row)
                or self._strong_drain_motion_support(row)
            )
        )

    def _strong_drain_motion_support(self, row: _ObservedRow) -> bool:
        """Separate current drain motion from accumulated texture conflict.

        This is deliberately unavailable to initial drain release.  Once the
        drain phase exists, a confirmed anchor trajectory with registered
        motion may survive a stale/high texture average.  A material-path row
        still needs one low-conflict anchor-authoritative material witness, so
        a clean direct candidate cannot mask a conflicting material sibling.
        """
        if (
            row.ref.tracklet_confirmation_profile
            is not TrackletConfirmationProfile.ANCHOR_TRAJECTORY
            or row.ref.tracklet_motion_support < self.policy.fill_minimum_motion_support
            or row.ref.tracklet_motion_coverage
            < self.policy.fill_minimum_motion_coverage
        ):
            return False
        material_refs = tuple(
            (
                node.candidate_ref
                for node in row.nodes
                if node.candidate_ref is not None
                and node.candidate_ref.evidence.material_path
            )
        )
        if not material_refs:
            return True
        return any(
            (
                ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                and ref.evidence.material_texture_conflict
                < self.policy.material_conflict_limit
                for ref in material_refs
            )
        )

    def _drain_phase_reentry_cost(self, chain: _DrainChain, row: _ObservedRow) -> float:
        return abs(row.y - chain.last_y) / self.policy.maximum_jump_px

    def _rows(self, layer: tuple[OilSequenceNode, ...]) -> tuple[_ObservedRow, ...]:
        grouped: dict[tuple[str, str], list[OilSequenceNode]] = {}
        for node in layer:
            ref = node.candidate_ref
            if node.kind != "oil" or ref is None or (not ref.tracklet_id):
                continue
            grouped.setdefault(
                (ref.tracklet_id, ref.row_hypothesis_id or ""), []
            ).append(node)
        rows = []
        for (tracklet_id, row_id), members in grouped.items():
            ordered = tuple(
                sorted(
                    members,
                    key=lambda node: (
                        -float(node.emission),
                        float(node.y or math.inf),
                        node.identity,
                    ),
                )
            )
            ys = tuple((float(node.y) for node in ordered if node.y is not None))
            if not ys:
                continue
            assert ordered[0].candidate_ref is not None
            rows.append(
                _ObservedRow(
                    tracklet_id=tracklet_id,
                    row_hypothesis_id=row_id,
                    y=float(median(ys)),
                    entrance_y=min(ys),
                    ref=ordered[0].candidate_ref,
                    nodes=ordered,
                    current_material_conflict=min(
                        (
                            node.candidate_ref.evidence.material_texture_conflict
                            for node in ordered
                            if node.candidate_ref is not None
                            and node.candidate_ref.evidence.availability.material_texture
                        ),
                        default=1.0,
                    ),
                    current_material_veto=any(
                        (
                            node.candidate_ref is not None
                            and node.candidate_ref.evidence.material_path
                            and (
                                node.candidate_ref.evidence.material_texture_conflict
                                >= self.policy.material_conflict_limit
                            )
                            for node in ordered
                        )
                    ),
                )
            )
        return tuple(
            sorted(
                rows, key=lambda row: (row.y, row.tracklet_id, row.row_hypothesis_id)
            )
        )


def _row_has_identity_contradiction(row: _ObservedRow) -> bool:
    """Return the typed current identity contradiction for an observed row."""

    return any(
        node.candidate_ref is not None
        and node.candidate_ref.identity_contradiction
        is OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER
        for node in row.nodes
    )


class BoundedOilReleaseEvidenceEngine:
    """Single owner for bounded release evidence advancement.

    The lifecycle owner decides which phase transition is being attempted;
    this engine owns the shared recovery context, lease, handoff, expiry and
    ambiguity contract.  It deliberately returns immutable summaries and
    never emits a coordinate or mutates a candidate row.
    """

    def __init__(self, policy: OilMaterialPhasePolicy) -> None:
        self.policy = policy

    def advance(
        self,
        prior: dict[str, _RecoveryDrainChain],
        rows: tuple[_ObservedRow, ...],
        frame: int,
        *,
        stage: str,
        seed_rows: tuple[_ObservedRow, ...],
        established_fill: _FillChain | None,
        allow_seeding: bool = True,
        contradicted_owner_ids: frozenset[str] = frozenset(),
    ) -> tuple[dict[str, _RecoveryDrainChain], dict[str, object]]:
        """Advance bounded release evidence without changing physical rows."""
        ordered_rows = tuple(
            sorted(
                rows, key=lambda row: (row.tracklet_id, row.row_hypothesis_id, row.y)
            )
        )
        row_keys = {
            (row.tracklet_id, row.row_hypothesis_id): row for row in ordered_rows
        }
        predicates = tuple(
            (self._recovery_admission_record(row, stage=stage) for row in ordered_rows)
        )
        reset_reasons: list[str] = []
        # Contradiction is positive evidence, not a missing/admission-filtered
        # row. Preserve it independently of the pool allowed to publish Oil.
        contradictions = (
            contradicted_owner_ids
            | frozenset(
                row.tracklet_id
                for row in ordered_rows
                if _row_has_identity_contradiction(row)
            )
            if stage in {"initial_full", "delayed_reacquisition"}
            else frozenset()
        )
        context_key = _recovery_context_key(stage, established_fill)
        retained: dict[str, _RecoveryDrainChain] = {}
        for key, chain in sorted(prior.items()):
            if chain.owner in contradictions:
                reset_reasons.append("identity_contradiction")
                continue
            if chain.stage != stage or chain.context_key != context_key:
                reset_reasons.append("release_context_changed")
                continue
            if stage == "initial_full":
                renewal = self._initial_full_renewal_candidate(
                    chain, ordered_rows, frame
                )
                if (
                    renewal is not None
                    and (not chain.renewal_used)
                    and (frame <= chain.lease_expiry_frame)
                ):
                    chain = replace(
                        chain,
                        lease_expiry_frame=chain.lease_origin_frame
                        + 2 * self.policy.fill_evidence_window_frames,
                        renewal_used=True,
                        certified_anchor_frame=frame,
                        certified_anchor_y=renewal.y,
                    )
                    reset_reasons.append("evidence_lease_renewed")
                if frame > chain.lease_expiry_frame:
                    reset_reasons.append("evidence_window_expired")
                    continue
            elif frame - chain.first_frame > self.policy.fill_evidence_window_frames:
                reset_reasons.append("evidence_window_expired")
                continue
            if frame - chain.last_frame > self.policy.maximum_lost_frames + 1:
                reset_reasons.append("loss_window_expired")
                continue
            if (
                frame - chain.last_forward_progress_frame
                >= self.policy.fill_evidence_window_frames
            ):
                reset_reasons.append("stagnation")
                continue
            retained[key] = chain
        current: dict[str, _RecoveryDrainChain] = {}
        current_rows: dict[str, _ObservedRow] = {}
        used_rows: set[tuple[str, str]] = set()
        ambiguous = False
        ambiguous_chain_keys: set[str] = set()
        blocked_chain_keys: set[str] = set()
        blocked_seed_owner_ids: set[str] = set(contradictions)
        reset_chain_keys: set[str] = set()
        blocked_rows: set[tuple[str, str]] = set()
        eligible_seed_keys_by_owner: dict[str, list[tuple[str, str]]] = {}
        for row in seed_rows:
            key = (row.tracklet_id, row.row_hypothesis_id)
            if self._recovery_seed_allowed(
                row, stage=stage, established_fill=established_fill
            ):
                eligible_seed_keys_by_owner.setdefault(row.tracklet_id, []).append(key)
        ambiguous_seed_owner_ids = tuple(
            sorted(
                (
                    owner
                    for owner, keys in eligible_seed_keys_by_owner.items()
                    if len(keys) > 1
                )
            )
        )
        if ambiguous_seed_owner_ids:
            ambiguous = True
            reset_reasons.append("duplicate_seed_hypotheses")
            for owner in ambiguous_seed_owner_ids:
                blocked_seed_owner_ids.add(owner)
                blocked_rows.update(eligible_seed_keys_by_owner[owner])
                ambiguous_chain_keys.update(
                    (
                        key
                        for key, chain in retained.items()
                        if key == owner or chain.owner == owner
                    )
                )

        def row_matches(chain: _RecoveryDrainChain, row: _ObservedRow) -> bool:
            gap = frame - chain.last_frame
            return bool(
                1 <= gap <= self.policy.maximum_lost_frames + 1
                and row.tracklet_id not in contradictions
                and (
                    not (
                        stage == "delayed_reacquisition"
                        and _row_has_identity_contradiction(row)
                    )
                )
                and self._recovery_common_admission(row)
                and (
                    row.y
                    >= chain.current_y
                    - self.policy.handoff_direction_reversal_tolerance_px
                )
                and (abs(row.y - chain.current_y) <= self.policy.maximum_jump_px * gap)
            )

        for key, chain in sorted(retained.items()):
            if chain.owner in ambiguous_seed_owner_ids:
                continue
            candidates = tuple(
                (
                    row
                    for row in ordered_rows
                    if row.tracklet_id == chain.owner
                    and self._recovery_row_has_authority(row)
                    and row_matches(chain, row)
                )
            )
            if len(candidates) > 1:
                ranked = tuple(
                    sorted(
                        (
                            (
                                self._recovery_step_cost(chain, row, frame),
                                row.row_hypothesis_id,
                                row,
                            )
                            for row in candidates
                        )
                    )
                )
                chosen = _clear_choice(
                    tuple(((cost, row_id) for cost, row_id, _row in ranked)),
                    self.policy.handoff_ambiguity_margin,
                )
                if chosen is None:
                    ambiguous = True
                    reset_reasons.append("same_owner_ambiguity")
                    ambiguous_chain_keys.add(key)
                    blocked_seed_owner_ids.add(chain.owner)
                    continue
                candidates = tuple(
                    (row for _cost, row_id, row in ranked if row_id == chosen)
                )
            if candidates:
                row = candidates[0]
                current[key] = _extend_recovery_chain(chain, row, frame)
                current_rows[key] = row
                used_rows.add((row.tracklet_id, row.row_hypothesis_id))
            else:
                same_owner_rows = tuple(
                    (row for row in ordered_rows if row.tracklet_id == chain.owner)
                )
                if same_owner_rows and (
                    not any(
                        (
                            self._recovery_common_admission(row)
                            for row in same_owner_rows
                        )
                    )
                ):
                    reset_reasons.append(
                        "identity_contradiction"
                        if stage == "delayed_reacquisition"
                        and any(
                            (
                                _row_has_identity_contradiction(row)
                                for row in same_owner_rows
                            )
                        )
                        else "material_or_incompatible"
                    )
                    blocked_chain_keys.add(key)
                    blocked_seed_owner_ids.add(chain.owner)
                    reset_chain_keys.add(key)
                elif same_owner_rows:
                    blocked_chain_keys.add(key)
                    blocked_seed_owner_ids.add(chain.owner)
                    reset_chain_keys.add(key)
                    reset_reasons.append("step_bound")
        successors = tuple(
            (
                row
                for row in ordered_rows
                if (row.tracklet_id, row.row_hypothesis_id) not in used_rows
                and self._recovery_row_has_authority(row, anchor_required=True)
                and (
                    stage != "delayed_reacquisition"
                    or self._delayed_phase_identity_valid(row)
                )
                and self._recovery_common_admission(row)
            )
        )
        matches_by_successor: dict[
            tuple[str, str], tuple[tuple[float, str, _RecoveryDrainChain], ...]
        ] = {}
        for row in successors:
            if row.tracklet_id in contradictions:
                continue
            matches_by_successor[row.tracklet_id, row.row_hypothesis_id] = tuple(
                sorted(
                    (
                        (self._recovery_step_cost(chain, row, frame), key, chain)
                        for key, chain in retained.items()
                        if key not in current
                        and key not in blocked_chain_keys
                        # A renewed lease certifies this physical owner only.
                        # A fresh identity must start its own bounded evidence.
                        and not chain.renewal_used
                        and row_matches(chain, row)
                    )
                )
            )
        matches_by_chain: dict[str, list[tuple[float, tuple[str, str]]]] = {}
        for successor_key, matches in matches_by_successor.items():
            for cost, chain_key, _chain in matches:
                matches_by_chain.setdefault(chain_key, []).append((cost, successor_key))
        successor_choices = {
            successor_key: _clear_choice(
                tuple(((cost, chain_key) for cost, chain_key, _chain in matches)),
                self.policy.handoff_ambiguity_margin,
            )
            for successor_key, matches in matches_by_successor.items()
            if matches
        }
        chain_choices = {
            chain_key: _clear_choice(
                tuple(sorted(options)), self.policy.handoff_ambiguity_margin
            )
            for chain_key, options in matches_by_chain.items()
        }
        for successor_key, matches in matches_by_successor.items():
            if not matches:
                continue
            chosen_chain = successor_choices.get(successor_key)
            if chosen_chain is None:
                ambiguous = True
                blocked_rows.add(successor_key)
                if matches:
                    reset_reasons.append("handoff_ambiguity")
                    ambiguous_chain_keys.update(
                        (chain_key for _cost, chain_key, _chain in matches)
                    )
                continue
            if chain_choices.get(chosen_chain) != successor_key:
                if chain_choices.get(chosen_chain) is None:
                    ambiguous = True
                    reset_reasons.append("handoff_ambiguity")
                    blocked_rows.add(successor_key)
                    ambiguous_chain_keys.add(chosen_chain)
                    ambiguous_chain_keys.update(
                        (chain_key for _cost, chain_key, _chain in matches)
                    )
                continue
            if chosen_chain not in current:
                chain = retained[chosen_chain]
                row = row_keys[successor_key]
                current[chosen_chain] = _extend_recovery_chain(chain, row, frame)
                current_rows[chosen_chain] = row
                used_rows.add(successor_key)
        for key, chain in sorted(retained.items()):
            if key not in current and key not in reset_chain_keys:
                current[key] = chain
        seed_keys = (
            {
                (row.tracklet_id, row.row_hypothesis_id)
                for row in seed_rows
                if self._recovery_seed_allowed(
                    row, stage=stage, established_fill=established_fill
                )
            }
            if allow_seeding
            else set()
        )
        for key in sorted(seed_keys):
            if key in used_rows or key in blocked_rows:
                continue
            row = row_keys[key]
            chain_key = row.tracklet_id
            if chain_key in current or chain_key in blocked_seed_owner_ids:
                continue
            chain = _new_recovery_chain(row, frame, stage, context_key)
            if stage == "initial_full":
                chain = replace(
                    chain,
                    lease_expiry_frame=frame + self.policy.fill_evidence_window_frames,
                    certified_anchor_frame=frame,
                    certified_anchor_y=row.y,
                )
            current[chain_key] = chain
            current_rows[chain_key] = row
            used_rows.add(key)
        if ambiguous:
            current = {
                key: chain
                for key, chain in current.items()
                if key not in ambiguous_chain_keys
            }
            current_rows = {
                key: row for key, row in current_rows.items() if key in current
            }
        qualifying: list[tuple[str, _ObservedRow]] = []
        minimum_progress = max(
            4.0, self.policy.geometry_height * self.policy.drain_minimum_progress_ratio
        )
        for key, chain in sorted(current.items()):
            row = current_rows.get(key)
            if row is None:
                continue
            chain_predicates = (
                ("positive_progress", chain.net_progress_px > 0.0),
                ("minimum_progress", chain.net_progress_px >= minimum_progress),
                (
                    "directional_agreement",
                    chain.directional_agreement
                    >= self.policy.drain_minimum_directional_agreement,
                ),
                ("current_admission", self._recovery_common_admission(row)),
            )
            if all((passed for _name, passed in chain_predicates)):
                qualifying.append((key, row))
        if len(qualifying) > 1:
            ambiguous = True
            reset_reasons.append("multiple_qualifying_chains")
            ambiguous_chain_keys.update((key for key, _row in qualifying))
            current = {
                key: chain
                for key, chain in current.items()
                if key not in ambiguous_chain_keys
            }
            current_rows = {
                key: row for key, row in current_rows.items() if key in current
            }
        active = tuple(
            (
                self._recovery_chain_summary(
                    key, chain, current_rows.get(key), minimum_progress=minimum_progress
                )
                for key, chain in sorted(current.items())
            )
        )
        if ambiguous:
            reset_reasons.append("ambiguity")
        return (
            current,
            {
                "active": active,
                "predicates": predicates
                + tuple(
                    (
                        self._recovery_chain_summary(
                            key,
                            chain,
                            current_rows.get(key),
                            minimum_progress=minimum_progress,
                        )
                        for key, chain in sorted(current.items())
                    )
                ),
                "qualifying": tuple(qualifying),
                "ambiguous": ambiguous,
                "ambiguous_seed_owner_ids": ambiguous_seed_owner_ids,
                "reset_reason": ";".join(dict.fromkeys(reset_reasons))
                if reset_reasons
                else None,
            },
        )

    def _recovery_admission_record(
        self, row: _ObservedRow, *, stage: str
    ) -> dict[str, object]:
        ordered = self._recovery_admission_predicates(row)
        return {
            "stage": stage,
            "tracklet_id": row.tracklet_id,
            "row_hypothesis_id": row.row_hypothesis_id,
            "ordered_predicates": [
                {"name": name, "passed": passed} for name, passed in ordered
            ],
            "first_failed_predicate": next(
                (name for name, passed in ordered if not passed), None
            ),
        }

    def _initial_full_renewal_candidate(
        self, chain: _RecoveryDrainChain, rows: tuple[_ObservedRow, ...], frame: int
    ) -> _ObservedRow | None:
        """Return one same-owner anchor that can renew an initial-FULL lease.

        Renewal is deliberately stricter than ordinary recovery continuation:
        it is same-owner, current-frame, material-clean, independently
        identified, and backed by a currently admitted confirmed witness.  A
        missing/late anchor therefore cannot revive an expired chain.
        """
        anchor_y = (
            chain.certified_anchor_y
            if chain.certified_anchor_y is not None
            else chain.seed_y
        )
        candidates = tuple(
            (
                row
                for row in rows
                if len(chain.owners) == 1
                and row.tracklet_id == chain.owner
                and (row.ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE)
                and (
                    row.ref.phase_identity
                    in {
                        OilPhaseIdentity.DIRECT_INTERFACE,
                        OilPhaseIdentity.ORDERED_LOWER_INTERFACE,
                    }
                )
                and (
                    row.ref.tracklet_lifecycle
                    in {TrackletLifecycle.CONFIRMED, TrackletLifecycle.CONTINUING}
                )
                and row.ref.tracklet_admitted
                and _bounded_confirmed_observation(row.ref)
                and self._strict_material_support(row)
                and (not row.ref.tracklet_incompatible)
                and (row.y > anchor_y)
                and (
                    row.y
                    >= chain.current_y
                    - self.policy.handoff_direction_reversal_tolerance_px
                )
                and (
                    abs(row.y - chain.current_y)
                    <= self.policy.maximum_jump_px * max(1, frame - chain.last_frame)
                )
                and self._recovery_common_admission(row)
            )
        )
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda row: (
                abs(row.y - chain.current_y),
                row.tracklet_id,
                row.row_hypothesis_id,
            ),
        )

    def _recovery_admission_predicates(
        self, row: _ObservedRow
    ) -> tuple[tuple[str, bool], ...]:
        authorities = tuple(
            (
                node.candidate_ref.authority
                for node in row.nodes
                if node.kind == "oil" and node.candidate_ref is not None
            )
        )
        return (
            ("bounded_confirmed", _bounded_confirmed_observation(row.ref)),
            ("compatible", not row.ref.tracklet_incompatible),
            ("strict_material_support", self._strict_material_support(row)),
            ("real_same_frame_oil_candidate", bool(authorities)),
            (
                "authority",
                any(
                    (
                        authority
                        in {
                            OilCandidateAuthority.ANCHOR_ELIGIBLE,
                            OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                        }
                        for authority in authorities
                    )
                ),
            ),
        )

    def _recovery_common_admission(self, row: _ObservedRow) -> bool:
        return all(
            (passed for _name, passed in self._recovery_admission_predicates(row))
        )

    def _recovery_row_has_authority(
        self, row: _ObservedRow, *, anchor_required: bool = False
    ) -> bool:
        authorities = tuple(
            (
                node.candidate_ref.authority
                for node in row.nodes
                if node.kind == "oil" and node.candidate_ref is not None
            )
        )
        if anchor_required:
            return OilCandidateAuthority.ANCHOR_ELIGIBLE in authorities
        return any(
            (
                authority
                in {
                    OilCandidateAuthority.ANCHOR_ELIGIBLE,
                    OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                }
                for authority in authorities
            )
        )

    def _recovery_seed_allowed(
        self, row: _ObservedRow, *, stage: str, established_fill: _FillChain | None
    ) -> bool:
        if not self._recovery_common_admission(
            row
        ) or not self._recovery_row_has_authority(row, anchor_required=True):
            return False
        if stage == "delayed_reacquisition":
            return bool(
                self._delayed_phase_identity_valid(row)
                and all(
                    (
                        passed
                        for _name, passed in self._delayed_seed_direction_predicates(
                            row
                        )
                    )
                )
            )
        if stage == "initial_full":
            relative = (
                row.entrance_y - self.policy.geometry_top_y
            ) / self.policy.geometry_height
            return relative <= self.policy.drain_entrance_ratio
        if established_fill is None:
            return False
        return bool(
            row.y
            >= established_fill.last.y
            - self.policy.handoff_direction_reversal_tolerance_px
            and abs(row.y - established_fill.last.y) <= self.policy.maximum_jump_px
        )

    def _delayed_phase_identity_valid(self, row: _ObservedRow) -> bool:
        """Require the existing independent phase identity for delayed seeds.

        This gate is intentionally local to R20 delayed reacquisition.  R19
        near-snapshot recovery keeps its established contract, while a fresh
        delayed owner must prove that it is a direct or ordered-lower
        interface before it can bootstrap a new phase-evidence chain.
        """
        if _row_has_identity_contradiction(row):
            return False
        return any(
            (
                node.candidate_ref is not None
                and node.candidate_ref.phase_identity
                in {
                    OilPhaseIdentity.DIRECT_INTERFACE,
                    OilPhaseIdentity.ORDERED_LOWER_INTERFACE,
                }
                for node in row.nodes
            )
        )

    def _delayed_seed_direction_predicates(
        self, row: _ObservedRow
    ) -> tuple[tuple[str, bool], ...]:
        """Return the shared drain-readiness test for a delayed seed.

        Delayed admission is the only release path that must decide whether
        to consume the episode's one fresh-anchor attempt.  The existing
        tracklet's direction, agreement and positive progress are therefore
        required before that irreversible decision.  The same predicate is
        used by the admission record below so diagnostics cannot describe a
        different eligibility rule than the lifecycle.
        """
        return (
            ("drain_direction_ready", row.ref.tracklet_direction > 0),
            (
                "drain_directional_agreement",
                row.ref.tracklet_directional_agreement
                >= self.policy.drain_minimum_directional_agreement,
            ),
            ("drain_positive_progress", row.ref.tracklet_net_progress_px > 0.0),
        )

    def _delayed_seed_allowed(
        self, row: _ObservedRow, *, established_fill: _FillChain | None
    ) -> bool:
        return bool(
            established_fill is not None
            and self._recovery_common_admission(row)
            and self._recovery_row_has_authority(row, anchor_required=True)
            and self._delayed_phase_identity_valid(row)
            and (
                row.ref.tracklet_lifecycle
                in {TrackletLifecycle.CONFIRMED, TrackletLifecycle.CONTINUING}
            )
            and _bounded_confirmed_observation(row.ref)
            and self._strict_material_support(row)
            and all(
                (
                    passed
                    for _name, passed in self._delayed_seed_direction_predicates(row)
                )
            )
        )

    def _delayed_seed_admission_record(
        self,
        row: _ObservedRow,
        *,
        grace_elapsed: bool,
        attempt_available: bool,
        snapshot_y: float,
    ) -> dict[str, object]:
        common_admission = self._recovery_common_admission(row)
        phase_identity = self._delayed_phase_identity_valid(row)
        identity_contradiction = _row_has_identity_contradiction(row)
        seed_authority = self._recovery_row_has_authority(row, anchor_required=True)
        bounded_tracklet = bool(
            row.ref.tracklet_lifecycle
            in {TrackletLifecycle.CONFIRMED, TrackletLifecycle.CONTINUING}
            and _bounded_confirmed_observation(row.ref)
        )
        predicates = (
            ("common_admission", common_admission),
            ("phase_identity", phase_identity),
            ("identity_contradiction_absent", not identity_contradiction),
            ("seed_authority", seed_authority),
            ("bounded_confirmed_tracklet", bounded_tracklet),
            ("strict_material_support", self._strict_material_support(row)),
            *self._delayed_seed_direction_predicates(row),
            ("ordinary_loss_grace_elapsed", grace_elapsed),
            ("attempt_available", attempt_available),
        )
        return {
            "stage": "delayed_reacquisition",
            "tracklet_id": row.tracklet_id,
            "row_hypothesis_id": row.row_hypothesis_id,
            "snapshot_distance_px": abs(row.y - snapshot_y),
            "snapshot_distance_used_for_identity": False,
            "drain_direction_ready": all(
                (
                    passed
                    for _name, passed in self._delayed_seed_direction_predicates(row)
                )
            ),
            "ordered_predicates": [
                {"name": name, "passed": passed} for name, passed in predicates
            ],
            "first_failed_predicate": next(
                (name for name, passed in predicates if not passed), None
            ),
            "eligible": all((passed for _name, passed in predicates)),
        }

    def _recovery_step_cost(
        self, chain: _RecoveryDrainChain, row: _ObservedRow, frame: int
    ) -> float:
        gap = max(1, frame - chain.last_frame)
        return abs(row.y - chain.current_y) / (self.policy.maximum_jump_px * gap)

    def _recovery_chain_summary(
        self,
        key: str,
        chain: _RecoveryDrainChain,
        row: _ObservedRow | None,
        *,
        minimum_progress: float,
    ) -> dict[str, object]:
        predicates = (
            ("positive_progress", chain.net_progress_px > 0.0),
            ("minimum_progress", chain.net_progress_px >= minimum_progress),
            (
                "directional_agreement",
                chain.directional_agreement
                >= self.policy.drain_minimum_directional_agreement,
            ),
            (
                "current_admission",
                row is not None and self._recovery_common_admission(row),
            ),
        )
        return {
            "chain_key": key,
            "stage": chain.stage,
            "context_key": list(chain.context_key),
            "current_tracklet_id": chain.owner,
            "seed_y": chain.seed_y,
            "current_y": chain.current_y,
            "first_frame": chain.first_frame,
            "last_frame": chain.last_frame,
            "lease_origin_frame": chain.lease_origin_frame,
            "lease_expiry_frame": chain.lease_expiry_frame,
            "lease_renewal_used": chain.renewal_used,
            "certified_anchor_frame": chain.certified_anchor_frame,
            "certified_anchor_y": chain.certified_anchor_y,
            "last_forward_progress_frame": chain.last_forward_progress_frame,
            "owner_ids": list(chain.owners),
            "observation_count": chain.observation_count,
            "transition_count": chain.transition_count,
            "nonnegative_transition_count": chain.nonnegative_transition_count,
            "negative_transition_count": chain.negative_transition_count,
            "net_progress_px": chain.net_progress_px,
            "directional_agreement": chain.directional_agreement,
            "ordered_predicates": [
                {"name": name, "passed": passed} for name, passed in predicates
            ],
            "first_failed_predicate": next(
                (name for name, passed in predicates if not passed), None
            ),
        }

    def _strict_material_support(self, row: _ObservedRow) -> bool:
        return bool(
            not row.current_material_veto
            and row.ref.tracklet_material_conflict < self.policy.material_conflict_limit
            and (row.current_material_conflict < self.policy.material_conflict_limit)
        )


def _new_chain(row: _ObservedRow, frame: int) -> _FillChain:
    return _FillChain(
        owner=row.tracklet_id,
        owners=(row.tracklet_id,),
        origin_y=row.y,
        observations=(_fill_observation(row, frame),),
    )


def _recovery_context_key(
    stage: str,
    established_fill: _FillChain | None,
) -> tuple[str, ...]:
    if stage == "initial_full":
        return (stage,)
    if established_fill is None:
        return (stage, "no_established_fill")
    return (
        stage,
        established_fill.owner,
        ",".join(established_fill.owners),
        str(established_fill.last.frame),
        repr(established_fill.last.y),
    )


def _new_recovery_chain(
    row: _ObservedRow,
    frame: int,
    stage: str,
    context_key: tuple[str, ...],
) -> _RecoveryDrainChain:
    return _RecoveryDrainChain(
        stage=stage,
        context_key=context_key,
        owner=row.tracklet_id,
        owners=(row.tracklet_id,),
        seed_y=row.y,
        current_y=row.y,
        first_frame=frame,
        last_frame=frame,
        last_forward_progress_frame=frame,
        observation_count=1,
        transition_count=0,
        nonnegative_transition_count=0,
        negative_transition_count=0,
        net_progress_px=0.0,
        lease_origin_frame=frame,
        lease_expiry_frame=frame,
    )


def _extend_recovery_chain(
    chain: _RecoveryDrainChain,
    row: _ObservedRow,
    frame: int,
) -> _RecoveryDrainChain:
    delta = row.y - chain.current_y
    owners = _append_unique_owner(chain.owners, row.tracklet_id)
    return _RecoveryDrainChain(
        stage=chain.stage,
        context_key=chain.context_key,
        owner=row.tracklet_id,
        owners=owners,
        seed_y=chain.seed_y,
        current_y=row.y,
        first_frame=chain.first_frame,
        last_frame=frame,
        last_forward_progress_frame=(
            frame if delta > 0.0 else chain.last_forward_progress_frame
        ),
        observation_count=chain.observation_count + 1,
        transition_count=chain.transition_count + 1,
        nonnegative_transition_count=(
            chain.nonnegative_transition_count + int(delta >= 0.0)
        ),
        negative_transition_count=(chain.negative_transition_count + int(delta < 0.0)),
        net_progress_px=row.y - chain.seed_y,
        lease_origin_frame=chain.lease_origin_frame,
        lease_expiry_frame=chain.lease_expiry_frame,
        renewal_used=chain.renewal_used,
        certified_anchor_frame=chain.certified_anchor_frame,
        certified_anchor_y=chain.certified_anchor_y,
    )


def _append_unique_owner(
    owners: tuple[str, ...],
    owner: str,
) -> tuple[str, ...]:
    if owner in owners:
        return owners
    return owners + (owner,)


def _prepend_owner(chain: _FillChain, owner: str) -> _FillChain:
    if owner in chain.owners:
        return chain
    return _FillChain(
        owner=chain.owner,
        owners=(owner,) + chain.owners,
        origin_y=chain.origin_y,
        observations=chain.observations,
    )


def _extend_chain(
    chain: _FillChain,
    row: _ObservedRow,
    frame: int,
    window_frames: int,
) -> _FillChain:
    return _FillChain(
        owner=chain.owner,
        owners=chain.owners,
        origin_y=chain.origin_y,
        observations=_bounded_fill_observations(
            chain.observations + (_fill_observation(row, frame),),
            frame,
            window_frames,
        ),
    )


def _handoff_chain(
    chain: _FillChain,
    row: _ObservedRow,
    frame: int,
    window_frames: int,
) -> _FillChain:
    return _FillChain(
        owner=row.tracklet_id,
        owners=_append_unique_owner(chain.owners, row.tracklet_id),
        origin_y=chain.origin_y,
        observations=_bounded_fill_observations(
            chain.observations + (_fill_observation(row, frame),),
            frame,
            window_frames,
        ),
    )


def _fill_observation(
    row: _ObservedRow,
    frame: int,
) -> _FillObservation:
    return _FillObservation(
        frame=frame,
        y=row.y,
        material_veto=row.current_material_veto,
        independent_anchor=any(
            node.candidate_ref is not None
            and node.candidate_ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
            for node in row.nodes
        ),
        confirmation_profile=row.ref.tracklet_confirmation_profile,
        net_progress_px=row.ref.tracklet_net_progress_px,
        directional_agreement=row.ref.tracklet_directional_agreement,
        motion_support=max(
            (
                node.candidate_ref.tracklet_motion_support
                for node in row.nodes
                if node.candidate_ref is not None
            ),
            default=0.0,
        ),
        motion_coverage=max(
            (
                node.candidate_ref.tracklet_motion_coverage
                for node in row.nodes
                if node.candidate_ref is not None
            ),
            default=0.0,
        ),
    )


def _bounded_fill_observations(
    observations: tuple[_FillObservation, ...],
    frame: int,
    window_frames: int,
) -> tuple[_FillObservation, ...]:
    first_frame = frame - max(3, window_frames) + 1
    return tuple(
        observation for observation in observations if observation.frame >= first_frame
    )


def _selected_owner_chain(
    chains: dict[str, _FillChain],
    allowed: frozenset[str] | None,
) -> tuple[str, ...]:
    if allowed is not None and len(allowed) == 1:
        owner = next(iter(allowed))
        if owner in chains:
            return chains[owner].owners
    if len(chains) == 1:
        return next(iter(chains.values())).owners
    return ()


def _bounded_confirmed_observation(ref: OilCandidateRef) -> bool:
    """Accept a witness retro-admitted by one bounded confirmed tracklet.

    A witness frame remains lifecycle ``PROVISIONAL`` because confirmation
    happens later in the bounded window.  Its non-NONE confirmation profile is
    the explicit proof that the physical tracklet did subsequently confirm; a
    truly provisional observation has no such profile and cannot move material
    phase state.
    """

    return bool(
        ref.tracklet_admitted
        and ref.tracklet_confirmation_profile is not TrackletConfirmationProfile.NONE
    )


def _tracklet_maturity(ref: OilCandidateRef) -> int:
    return {
        TrackletLifecycle.PROVISIONAL: 0,
        TrackletLifecycle.CONFIRMED: 1,
        TrackletLifecycle.CONTINUING: 2,
        TrackletLifecycle.LOST: -1,
        TrackletLifecycle.TERMINATED: -1,
    }[ref.tracklet_lifecycle]


def _clear_choice(
    options: tuple[tuple[float, str], ...],
    ambiguity_margin: float,
) -> str | None:
    if not options:
        return None
    ordered = tuple(sorted(options, key=lambda item: (item[0], item[1])))
    if len(ordered) > 1 and (ordered[1][0] - ordered[0][0] <= ambiguity_margin):
        return None
    return ordered[0][1]
