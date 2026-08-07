from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum
import json
import math
from statistics import median
from threading import Condition, Lock, local
from typing import Any

import numpy as np

from .oil_shadow_observations import (
    build_bounded_proposals,
    evaluate_semantic_hypotheses,
    evaluate_typed_current_observation,
    extract_raw_observations,
)
from .oil_spatial_fallback import build_spatial_positive_fallback_frame
from .oil_shadow_temporal import (
    CanonicalTemporalReduction,
    GlassTemporalRecord,
    GlassTemporalState,
    TemporalAuditSnapshot,
    TemporalReentryError,
    TemporalStoreState,
    _BeamItem,
)
from .oil_shadow_types import (
    AbsenceStabilityMode,
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
    BoundaryAcceptanceMode,
    BoundaryAcceptedDecision,
    BoundedYProposal,
    CompatibilityTrackerAction,
    EvidenceUnavailableDecision,
    EvidenceUnavailableOutcome,
    NoInterfaceAcceptedDecision,
    NoInterfaceOutcome,
    OilCanonicalOutcome,
    OilShadowBounds,
    PipelineFailureOutcome,
    PipelineFailureStage,
    RawEdgeObservation,
    ReacquisitionPendingDecision,
    ReacquisitionPendingOutcome,
    SemanticHypothesis,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowCurrentObservation,
    ShadowHypothesisLabel,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowResourceSummary,
    ShadowSourceFamily,
    ShadowUnavailableObservation,
    SmoothingAction,
    SuccessfulPipelineFrame,
    TemporalResourceMetrics,
    stable_digest,
)
from .preprocessing import PreprocessResult


@dataclass(frozen=True)
class _PreparedPreprocessInputs:
    gray: np.ndarray
    normalized: np.ndarray
    blurred: np.ndarray
    sobel_y_signed: np.ndarray
    sobel_y_abs: np.ndarray
    canny: np.ndarray
    horizontal_mask: np.ndarray
    glare_mask: np.ndarray


@dataclass(frozen=True)
class _PreparedRunInputs:
    glass_id: str
    pre: _PreparedPreprocessInputs
    effective_mask: np.ndarray
    ellipse_mask: np.ndarray
    exclusion_mask: np.ndarray
    static_artifact_map: np.ndarray | None
    crop_origin_y: float
    accepted_foam_front_local_y: float | None
    accepted_foam_component_mask: np.ndarray | None

    def __post_init__(self) -> None:
        arrays = (
            self.pre.gray,
            self.pre.normalized,
            self.pre.blurred,
            self.pre.sobel_y_signed,
            self.pre.sobel_y_abs,
            self.pre.canny,
            self.pre.horizontal_mask,
            self.pre.glare_mask,
            self.effective_mask,
            self.ellipse_mask,
            self.exclusion_mask,
        )
        if self.static_artifact_map is not None:
            arrays += (self.static_artifact_map,)
        if self.accepted_foam_component_mask is not None:
            arrays += (self.accepted_foam_component_mask,)
        if type(self.glass_id) is not str or not self.glass_id:
            raise ValueError("Prepared oil command requires a Glass identity.")
        if not math.isfinite(self.crop_origin_y):
            raise ValueError("Prepared oil command crop origin must be finite.")
        if self.accepted_foam_front_local_y is not None:
            if not math.isfinite(self.accepted_foam_front_local_y):
                raise ValueError("Accepted Foam front must be finite.")
            if not 0.0 <= self.accepted_foam_front_local_y <= self.pre.gray.shape[0] - 1:
                raise ValueError("Accepted Foam front must stay inside the Oil raster.")
        if (
            self.accepted_foam_component_mask is not None
            and self.accepted_foam_front_local_y is None
        ):
            raise ValueError("Accepted Foam component context requires an accepted front.")
        if any(
            type(value) is not np.ndarray
            or value.flags.writeable
            or not value.flags.owndata
            or value.base is not None
            for value in arrays
        ):
            raise TypeError("Prepared oil command arrays must be owned read-only copies.")
        expected_shape = self.pre.gray.shape
        if any(value.shape != expected_shape for value in arrays):
            raise ValueError("Prepared oil command arrays must share one raster shape.")
        for index, left in enumerate(arrays):
            for right in arrays[index + 1 :]:
                if np.shares_memory(left, right):
                    raise ValueError("Prepared oil command arrays cannot retain aliases.")


@dataclass(frozen=True)
class _RunOilFrameCommand:
    payload: _PreparedRunInputs

    def __post_init__(self) -> None:
        if type(self.payload) is not _PreparedRunInputs:
            raise TypeError("Run command requires the closed prepared payload.")


@dataclass(frozen=True)
class _ResetGlassCommand:
    glass_id: str

    def __post_init__(self) -> None:
        if type(self.glass_id) is not str or not self.glass_id:
            raise ValueError("Glass reset command requires a Glass identity.")


@dataclass(frozen=True)
class _ResetAllCommand:
    pass


@dataclass(frozen=True)
class _ReadSnapshotCommand:
    glass_id: str

    def __post_init__(self) -> None:
        if type(self.glass_id) is not str or not self.glass_id:
            raise ValueError("Snapshot command requires a Glass identity.")


@dataclass(frozen=True)
class _ReadStateCountCommand:
    pass


class _FixedCanonicalReducer:
    """Fixed pure reducer; it has no owner-store reference or replaceable seams."""

    def __init__(self, bounds: OilShadowBounds) -> None:
        self.bounds = bounds

    @property
    def retained_scalar_limit(self) -> int:
        return self.bounds.temporal_beam_width * (
            self.bounds.temporal_history_window * 4 + 7
        ) + 12

    def reduce(
        self,
        prior_record: GlassTemporalRecord,
        frame: SuccessfulPipelineFrame,
    ) -> CanonicalTemporalReduction:
        decision, next_state, temporal = self._transition_record(
            prior_record, frame.current_observation
        )
        next_record = GlassTemporalRecord(
            glass_id=prior_record.glass_id,
            version=prior_record.version + 1,
            temporal_state=next_state,
        )
        resources = self._resource_summary(frame, temporal)
        outcome = self._prepare_outcome(frame, decision, resources)
        outcome = self._finalize_debug_resources(outcome)
        return CanonicalTemporalReduction(
            decision=decision,
            next_record=next_record,
            outcome=outcome,
            tracker_action=decision.tracker_action,
            smoothing_action=decision.smoothing_action,
            resource_metrics=outcome.resources,
        )

    def _transition_record(
        self,
        prior_record: GlassTemporalRecord,
        observation: ShadowCurrentObservation,
    ) -> tuple[object, GlassTemporalState, TemporalResourceMetrics]:
        prior = prior_record.temporal_state
        alternatives = self._alternatives(observation)
        beam = self._advance_beam(prior.beam, alternatives)
        provisional = replace(prior, beam=beam)
        best = beam[0] if beam else None
        second = beam[1] if len(beam) > 1 else None
        margin = (
            _unit(best.cumulative_score - second.cumulative_score)
            if best is not None and second is not None
            else (0.0 if best is None else _unit(best.observation_score))
        )
        provisional = self._record_static_state(provisional, observation)
        if isinstance(observation, ShadowBoundaryObservation):
            decision, next_state = self._boundary_decision(provisional, observation, margin)
        elif isinstance(observation, ShadowNoInterfaceObservation):
            decision, next_state = self._no_interface_decision(provisional, observation, margin)
        elif isinstance(observation, ShadowUnavailableObservation):
            decision, next_state = self._unavailable_decision(provisional, observation, margin)
        elif isinstance(observation, ShadowAmbiguousObservation):
            decision, next_state = self._ambiguous_decision(provisional, observation, margin)
        else:
            raise TypeError("Unsupported successful current-observation variant.")
        temporal = self._resources(next_state)
        decision = replace(decision, resources=temporal)
        return decision, next_state, temporal

    def _resource_summary(
        self,
        frame: SuccessfulPipelineFrame,
        temporal: TemporalResourceMetrics,
    ) -> ShadowResourceSummary:
        proposals = frame.proposals
        return ShadowResourceSummary(
            raw_observation_count=len(frame.raw_observations),
            raw_observation_limit=self.bounds.total_raw_observations,
            broad_scale_count=len(self.bounds.broad_band_scales),
            broad_scale_limit=len(self.bounds.broad_band_scales),
            narrow_scale_count=len(self.bounds.narrow_scales),
            narrow_scale_limit=len(self.bounds.narrow_scales),
            narrow_examined_rows_per_hypothesis=min(
                frame.frame_height,
                2 * self.bounds.narrow_lobe_search_radius_px + 1,
            ),
            narrow_examined_rows_per_hypothesis_limit=(
                2 * self.bounds.narrow_lobe_search_radius_px + 1
            ),
            proposal_count=len(proposals),
            proposal_limit=self.bounds.total_proposals,
            maximum_proposal_diameter_px=max(
                (item.diameter_px for item in proposals),
                default=0.0,
            ),
            proposal_diameter_limit_px=self.bounds.maximum_proposal_diameter_px,
            maximum_members_per_proposal=max(
                (item.member_count for item in proposals),
                default=0,
            ),
            members_per_proposal_limit=self.bounds.members_per_proposal,
            retained_member_count=sum(item.member_count for item in proposals),
            retained_member_limit=self.bounds.total_retained_members,
            semantic_hypothesis_count=len(frame.hypotheses),
            semantic_hypothesis_limit=self.bounds.semantic_hypotheses,
            temporal_beam_count=temporal.beam_count,
            temporal_beam_limit=self.bounds.temporal_beam_width,
            temporal_history_length=temporal.history_length,
            temporal_history_limit=self.bounds.temporal_history_window,
            retained_temporal_scalar_count=temporal.retained_scalar_count,
            retained_temporal_scalar_limit=self.retained_scalar_limit,
            static_prior_scalar_count=2,
            static_prior_scalar_limit=self.bounds.static_prior_scalars_per_glass,
            debug_scalar_count=0,
            debug_scalar_limit=self.bounds.maximum_debug_scalar_count,
        )

    def _prepare_outcome(
        self,
        frame: SuccessfulPipelineFrame,
        decision,
        resources: ShadowResourceSummary,
    ) -> OilCanonicalOutcome:
        current = frame.current_observation
        hypotheses = frame.hypotheses
        if isinstance(decision, BoundaryAcceptedDecision):
            return AcceptedBoundaryOutcome(
                selected_hypothesis=decision.selected_hypothesis,
                hypotheses=hypotheses,
                resources=resources,
                confidence=decision.confidence,
                decision_margin=decision.decision_margin,
                acceptance_mode=decision.acceptance_mode,
                reason=decision.reason,
            )
        if isinstance(decision, NoInterfaceAcceptedDecision):
            return NoInterfaceOutcome(
                evidence=decision.evidence,
                hypotheses=hypotheses,
                resources=resources,
                confidence=decision.confidence,
                decision_margin=decision.decision_margin,
                stability_mode=decision.stability_mode,
                reason=decision.reason,
            )
        if isinstance(decision, AmbiguousDecision):
            if not isinstance(current, ShadowAmbiguousObservation):
                raise ValueError("Ambiguous outcome preparation lacks canonical evidence.")
            return AmbiguousOutcome(
                hypotheses=hypotheses,
                hypothesis_ids=decision.hypothesis_ids,
                projected_source_y=decision.projected_source_y,
                boundary_likelihood=current.boundary_likelihood,
                artifact_likelihood=current.artifact_likelihood,
                ambiguity_likelihood=current.ambiguity_likelihood,
                no_interface_likelihood=current.no_interface_likelihood,
                visibility=current.visibility,
                resources=resources,
                confidence=decision.confidence,
                decision_margin=decision.decision_margin,
                reason=decision.reason,
            )
        if isinstance(decision, EvidenceUnavailableDecision):
            return EvidenceUnavailableOutcome(
                hypotheses=hypotheses,
                resources=resources,
                visibility=decision.visibility,
                confidence=decision.confidence,
                decision_margin=decision.decision_margin,
                stability_mode=decision.stability_mode,
                reason=decision.reason,
            )
        if isinstance(decision, ReacquisitionPendingDecision):
            return ReacquisitionPendingOutcome(
                pending_hypothesis=decision.pending_hypothesis,
                hypotheses=hypotheses,
                resources=resources,
                confidence=decision.confidence,
                decision_margin=decision.decision_margin,
                reason=decision.reason,
            )
        raise TypeError("Unsupported temporal decision during outcome preparation.")

    def _finalize_debug_resources(
        self,
        outcome: OilCanonicalOutcome,
    ) -> OilCanonicalOutcome:
        if isinstance(outcome, PipelineFailureOutcome):
            return outcome
        debug_count = _scalar_leaf_count(oil_runtime_metrics(outcome)) + _scalar_leaf_count(
            oil_debug_detail(outcome)
        )
        if debug_count > self.bounds.maximum_debug_scalar_count:
            raise ValueError("Oil canonical debug scalar bound exceeded.")
        resources = replace(outcome.resources, debug_scalar_count=debug_count)
        return replace(outcome, resources=resources)

    def _advance_beam(
        self,
        previous: tuple[_BeamItem, ...],
        alternatives: tuple[tuple[ShadowObservationKind, str | None, float | None, float], ...],
    ) -> tuple[_BeamItem, ...]:
        priors: tuple[_BeamItem | None, ...] = previous or (None,)
        expanded: list[_BeamItem] = []
        for prior in priors:
            for kind, identity, source_y, score in alternatives:
                transition, velocity = self._transition(prior, kind, source_y)
                history = () if prior is None else prior.history
                history = (history + ((kind.value, identity, source_y, score),))[
                    -self.bounds.temporal_history_window :
                ]
                prior_score = 0.0 if prior is None else prior.cumulative_score * 0.72
                expanded.append(
                    _BeamItem(
                        kind=kind,
                        identity=identity,
                        source_y=source_y,
                        observation_score=score,
                        cumulative_score=prior_score + score - transition,
                        transition_cost=transition,
                        velocity=velocity,
                        history=history,
                    )
                )
        collapsed: dict[tuple[ShadowObservationKind, str | None], _BeamItem] = {}
        for item in expanded:
            key = (item.kind, item.identity)
            current = collapsed.get(key)
            if current is None or _beam_order(item) < _beam_order(current):
                collapsed[key] = item
        return tuple(
            sorted(collapsed.values(), key=_beam_order)[: self.bounds.temporal_beam_width]
        )

    def _transition(
        self,
        prior: _BeamItem | None,
        kind: ShadowObservationKind,
        source_y: float | None,
    ) -> tuple[float, float | None]:
        if prior is None:
            return 0.0, None
        if kind is ShadowObservationKind.UNAVAILABLE:
            return 0.10, prior.velocity
        if kind is ShadowObservationKind.AMBIGUOUS:
            return 0.08, prior.velocity
        if kind is ShadowObservationKind.NO_INTERFACE:
            return (
                0.02 if prior.kind is ShadowObservationKind.NO_INTERFACE else 0.11,
                None,
            )
        if (
            source_y is None
            or prior.source_y is None
            or prior.kind is not ShadowObservationKind.BOUNDARY
        ):
            return 0.10, None
        velocity = source_y - prior.source_y
        continuity = self.bounds.maximum_proposal_diameter_px * 4.0
        jump_cost = min(0.62, 0.10 * (abs(velocity) / max(1.0, continuity)) ** 1.35)
        acceleration_cost = 0.0
        if prior.velocity is not None:
            acceleration_cost = min(
                0.24,
                0.08 * abs(velocity - prior.velocity) / max(1.0, continuity),
            )
        return min(0.90, jump_cost + acceleration_cost), velocity

    def _boundary_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowBoundaryObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        hypothesis = observation.hypothesis
        y = hypothesis.representative_source_y
        confidence = _unit(
            hypothesis.boundary_likelihood * (1.0 - 0.35 * hypothesis.ambiguity_likelihood)
        )
        state = replace(state, no_interface_count=0, unavailable_count=0)
        if state.accepted_y is None:
            return self._accept_boundary(
                state,
                hypothesis,
                y,
                confidence,
                margin,
                BoundaryAcceptanceMode.INITIAL,
                "initial_shadow_boundary",
            )

        continuity = self.bounds.maximum_proposal_diameter_px * 4.0
        predicted = state.accepted_y + (state.accepted_velocity or 0.0)
        if abs(y - state.accepted_y) <= continuity or abs(y - predicted) <= continuity:
            return self._accept_boundary(
                state,
                hypothesis,
                y,
                confidence,
                margin,
                BoundaryAcceptanceMode.CONTINUOUS,
                "continuous_shadow_boundary",
            )

        pending_continuous = _pending_path_compatible(self.bounds, state, y)
        if state.pending_y is None or not pending_continuous:
            pending_count = 1
            pending_velocity = None
        else:
            pending_count = state.pending_count + 1
            pending_velocity = y - state.pending_y
        state = replace(
            state,
            pending_y=y,
            pending_velocity=pending_velocity,
            pending_count=pending_count,
        )
        if pending_count >= self.bounds.reacquisition_frames:
            return self._accept_boundary(
                state,
                hypothesis,
                y,
                confidence,
                margin,
                BoundaryAcceptanceMode.REACQUIRED,
                "bounded_shadow_reacquisition",
            )
        resources = self._resources(state)
        decision = ReacquisitionPendingDecision(
            pending_hypothesis=hypothesis,
            confidence=confidence,
            decision_margin=margin,
            reason="large_shadow_motion_waiting_for_consistency",
            resources=resources,
        )
        return decision, state

    def _accept_boundary(
        self,
        state: GlassTemporalState,
        hypothesis,
        y: float,
        confidence: float,
        margin: float,
        mode: BoundaryAcceptanceMode,
        reason: str,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        prior = state.accepted_y
        velocity = (
            None
            if prior is None or mode is BoundaryAcceptanceMode.REACQUIRED
            else y - prior
        )
        next_state = replace(
            state,
            accepted_y=y,
            accepted_velocity=velocity,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
            smoothing_invalidated=False,
        )
        decision = BoundaryAcceptedDecision(
            selected_hypothesis=hypothesis,
            accepted_source_y=y,
            confidence=confidence,
            decision_margin=margin,
            acceptance_mode=mode,
            reason=reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _no_interface_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowNoInterfaceObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        count = min(
            self.bounds.no_interface_clear_frames,
            state.no_interface_count + 1,
        )
        stable = count >= self.bounds.no_interface_clear_frames
        next_state = replace(
            state,
            no_interface_count=count,
            unavailable_count=0,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
        )
        if stable:
            next_state = replace(
                next_state,
                accepted_y=None,
                accepted_velocity=None,
                smoothing_invalidated=True,
            )
        mode = AbsenceStabilityMode.STABLE if stable else AbsenceStabilityMode.PENDING
        decision = NoInterfaceAcceptedDecision(
            evidence=observation.evidence,
            confidence=observation.evidence.likelihood,
            decision_margin=margin,
            stability_mode=mode,
            reason=observation.evidence.reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _unavailable_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowUnavailableObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        count = min(
            self.bounds.unavailable_clear_frames,
            state.unavailable_count + 1,
        )
        stable = count >= self.bounds.unavailable_clear_frames
        next_state = replace(
            state,
            unavailable_count=count,
            no_interface_count=0,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
        )
        if stable:
            next_state = replace(
                next_state,
                accepted_y=None,
                accepted_velocity=None,
                smoothing_invalidated=True,
                beam=(),
            )
        mode = AbsenceStabilityMode.STABLE if stable else AbsenceStabilityMode.PENDING
        decision = EvidenceUnavailableDecision(
            visibility=observation.visibility,
            confidence=observation.visibility,
            decision_margin=margin,
            stability_mode=mode,
            reason=observation.reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _ambiguous_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowAmbiguousObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        retain_pending = _pending_path_compatible(
            self.bounds,
            state,
            observation.projected_source_y,
        )
        next_state = replace(
            state,
            no_interface_count=0,
            unavailable_count=0,
            pending_y=state.pending_y if retain_pending else None,
            pending_velocity=state.pending_velocity if retain_pending else None,
            pending_count=state.pending_count if retain_pending else 0,
        )
        confidence = _unit(
            max(
                observation.boundary_likelihood,
                observation.artifact_likelihood,
                observation.no_interface_likelihood,
            ) * (1.0 - 0.45 * observation.ambiguity_likelihood)
        )
        decision = AmbiguousDecision(
            hypothesis_ids=observation.hypothesis_ids,
            projected_source_y=observation.projected_source_y,
            confidence=confidence,
            decision_margin=margin,
            reason=observation.reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _alternatives(
        self,
        observation: ShadowCurrentObservation,
    ) -> tuple[tuple[ShadowObservationKind, str | None, float | None, float], ...]:
        if isinstance(observation, ShadowBoundaryObservation):
            item = observation.hypothesis
            return (
                (
                    ShadowObservationKind.BOUNDARY,
                    item.identity,
                    item.representative_source_y,
                    item.boundary_likelihood,
                ),
                (
                    ShadowObservationKind.AMBIGUOUS,
                    None,
                    item.representative_source_y,
                    item.ambiguity_likelihood * 0.55,
                ),
            )
        if isinstance(observation, ShadowNoInterfaceObservation):
            return ((
                ShadowObservationKind.NO_INTERFACE,
                None,
                None,
                observation.evidence.likelihood,
            ),)
        if isinstance(observation, ShadowUnavailableObservation):
            return ((
                ShadowObservationKind.UNAVAILABLE,
                None,
                None,
                0.20 * observation.visibility,
            ),)
        if not isinstance(observation, ShadowAmbiguousObservation):
            raise TypeError("Unsupported successful current-observation variant.")
        alternatives: list[tuple[ShadowObservationKind, str | None, float | None, float]] = [
            (
                ShadowObservationKind.AMBIGUOUS,
                None,
                observation.projected_source_y,
                observation.ambiguity_likelihood,
            )
        ]
        if observation.projected_source_y is not None:
            alternatives.append((
                ShadowObservationKind.BOUNDARY,
                observation.hypothesis_ids[0] if observation.hypothesis_ids else None,
                observation.projected_source_y,
                observation.boundary_likelihood * 0.55,
            ))
        if observation.no_interface_likelihood > 0.0:
            alternatives.append((
                ShadowObservationKind.NO_INTERFACE,
                None,
                None,
                observation.no_interface_likelihood * 0.55,
            ))
        return tuple(alternatives)

    def _record_static_state(
        self,
        state: GlassTemporalState,
        observation: ShadowCurrentObservation,
    ) -> GlassTemporalState:
        if isinstance(observation, ShadowBoundaryObservation):
            return replace(
                state,
                last_static_contribution=observation.hypothesis.static_prior.contribution,
                last_static_available=float(observation.hypothesis.static_prior.available),
            )
        return replace(
            state,
            last_static_contribution=0.0,
            last_static_available=0.0,
        )

    def _resources(self, state: GlassTemporalState) -> TemporalResourceMetrics:
        return TemporalResourceMetrics(
            beam_count=len(state.beam),
            history_length=max((len(item.history) for item in state.beam), default=0),
            retained_scalar_count=self._retained_scalar_count(state),
            reacquisition_count=state.pending_count,
        )

    def _retained_scalar_count(self, state: GlassTemporalState) -> int:
        beam_scalars = sum(len(item.history) * 4 + 7 for item in state.beam)
        return beam_scalars + 12


class OilHypothesisPipeline:
    """Single serialized S5-B temporal owner and sole validation authority."""

    def __init__(self, bounds: OilShadowBounds | None = None) -> None:
        self.bounds = bounds or OilShadowBounds()
        self.__reducer = _FixedCanonicalReducer(self.bounds)
        self.__store = TemporalStoreState({})
        self.__ingress = Condition(Lock())
        self.__owner_context = local()
        self.__next_sequence = 0
        self.__next_to_execute = 0
        self.__assigned_sequences: list[int] = []
        self.__execution_sequences: list[int] = []
        self.__replacement_count = 0

    @property
    def temporal_state_count(self) -> int:
        self._reject_reentry()
        return int(self._submit(_ReadStateCountCommand()))

    def temporal_snapshot(self, glass_id: str) -> TemporalAuditSnapshot:
        self._reject_reentry()
        key = str(glass_id)
        if not key:
            raise ValueError("Temporal audit snapshot requires a Glass identity.")
        result = self._submit(_ReadSnapshotCommand(key))
        if type(result) is not TemporalAuditSnapshot:
            raise TypeError("Temporal owner returned an invalid snapshot acknowledgment.")
        return result

    def reset(self, glass_id: str | None = None) -> None:
        self._reject_reentry()
        if glass_id is None:
            self._submit(_ResetAllCommand())
            return
        key = str(glass_id)
        if not key:
            raise ValueError("Temporal reset requires a Glass identity.")
        self._submit(_ResetGlassCommand(key))

    def run(
        self,
        *,
        glass_id: str,
        pre: PreprocessResult,
        effective_mask: np.ndarray,
        ellipse_mask: np.ndarray,
        exclusion_mask: np.ndarray,
        static_artifact_map: np.ndarray | None,
        crop_origin_y: float,
        accepted_foam_front_local_y: float | None = None,
        accepted_foam_component_mask: np.ndarray | None = None,
    ) -> OilCanonicalOutcome:
        if self._is_owner_active():
            return self._failure_outcome(
                "temporal_reentry_rejected",
                PipelineFailureStage.EXTERNAL_RUNNER,
            )
        try:
            command = self._prepare_run_command(
                glass_id=glass_id,
                pre=pre,
                effective_mask=effective_mask,
                ellipse_mask=ellipse_mask,
                exclusion_mask=exclusion_mask,
                static_artifact_map=static_artifact_map,
                crop_origin_y=crop_origin_y,
                accepted_foam_front_local_y=accepted_foam_front_local_y,
                accepted_foam_component_mask=accepted_foam_component_mask,
            )
        except Exception as exc:
            return self._failure_outcome(
                _failure_reason(exc),
                PipelineFailureStage.EXTERNAL_RUNNER,
            )
        return self._submit(command)

    def _prepare_run_command(
        self,
        *,
        glass_id: str,
        pre: PreprocessResult,
        effective_mask: np.ndarray,
        ellipse_mask: np.ndarray,
        exclusion_mask: np.ndarray,
        static_artifact_map: np.ndarray | None,
        crop_origin_y: float,
        accepted_foam_front_local_y: float | None = None,
        accepted_foam_component_mask: np.ndarray | None = None,
    ) -> _RunOilFrameCommand:
        key = str(glass_id)
        if not key:
            raise ValueError("Oil pipeline requires a Glass identity.")
        isolated_pre = _PreparedPreprocessInputs(
            *(
                _owned_readonly_array(getattr(pre, name))
                for name in (
                    "gray", "normalized", "blurred", "sobel_y_signed",
                    "sobel_y_abs", "canny", "horizontal_mask", "glare_mask",
                )
            )
        )
        payload = _PreparedRunInputs(
            glass_id=key,
            pre=isolated_pre,
            effective_mask=_owned_readonly_array(effective_mask),
            ellipse_mask=_owned_readonly_array(ellipse_mask),
            exclusion_mask=_owned_readonly_array(exclusion_mask),
            static_artifact_map=(
                None
                if static_artifact_map is None
                else _owned_readonly_array(static_artifact_map)
            ),
            crop_origin_y=float(crop_origin_y),
            accepted_foam_front_local_y=(
                None
                if accepted_foam_front_local_y is None
                else float(accepted_foam_front_local_y)
            ),
            accepted_foam_component_mask=(
                None
                if accepted_foam_component_mask is None
                else _owned_readonly_array(accepted_foam_component_mask)
            ),
        )
        return _RunOilFrameCommand(payload)

    def _submit(self, command):
        self._reject_reentry()
        with self.__ingress:
            sequence = self.__next_sequence
            self.__next_sequence += 1
            self.__assigned_sequences.append(sequence)
            while sequence != self.__next_to_execute:
                self.__ingress.wait()
        self.__owner_context.active = True
        self.__execution_sequences.append(sequence)
        try:
            return self._dispatch(command)
        finally:
            self.__owner_context.active = False
            with self.__ingress:
                self.__next_to_execute += 1
                self.__ingress.notify_all()

    def _dispatch(self, command):
        if type(command) is _RunOilFrameCommand:
            return self._run_owned(command.payload)
        if type(command) is _ResetGlassCommand:
            return self._reset_owned(command.glass_id)
        if type(command) is _ResetAllCommand:
            return self._reset_all_owned()
        if type(command) is _ReadSnapshotCommand:
            return self._snapshot_owned(command.glass_id)
        if type(command) is _ReadStateCountCommand:
            return len(self.__store.records)
        raise TypeError("Unsupported temporal owner command.")

    def _run_owned(self, payload: _PreparedRunInputs) -> OilCanonicalOutcome:
        prior_store = self.__store
        prior_record = prior_store.records.get(payload.glass_id)
        if prior_record is None:
            prior_record = GlassTemporalRecord.initial(payload.glass_id)
        try:
            raw = extract_raw_observations(
                payload.pre,
                payload.effective_mask,
                crop_origin_y=payload.crop_origin_y,
                bounds=self.bounds,
            )
            proposals = build_bounded_proposals(raw, self.bounds)
            hypotheses = evaluate_semantic_hypotheses(
                proposals,
                raw,
                payload.pre,
                payload.effective_mask,
                payload.ellipse_mask,
                payload.exclusion_mask,
                payload.static_artifact_map,
                crop_origin_y=payload.crop_origin_y,
                bounds=self.bounds,
            )
            if payload.accepted_foam_front_local_y is None:
                current = evaluate_typed_current_observation(
                    payload.pre,
                    payload.effective_mask,
                    hypotheses,
                )
            elif payload.accepted_foam_component_mask is None:
                current = evaluate_typed_current_observation(
                    payload.pre,
                    payload.effective_mask,
                    hypotheses,
                    accepted_foam_front_local_y=payload.accepted_foam_front_local_y,
                )
            else:
                current = evaluate_typed_current_observation(
                    payload.pre,
                    payload.effective_mask,
                    hypotheses,
                    accepted_foam_front_local_y=payload.accepted_foam_front_local_y,
                    accepted_foam_component_mask=payload.accepted_foam_component_mask,
                )
            raw_frame = SuccessfulPipelineFrame(
                raw_observations=raw,
                proposals=proposals,
                hypotheses=hypotheses,
                current_observation=current,
                frame_height=int(payload.pre.gray.shape[0]),
                frame_width=int(payload.pre.gray.shape[1]),
            )
            if isinstance(current, ShadowAmbiguousObservation):
                spatial_fallback = build_spatial_positive_fallback_frame(
                    pre=payload.pre,
                    effective_mask=payload.effective_mask,
                    ellipse_mask=payload.ellipse_mask,
                    exclusion_mask=payload.exclusion_mask,
                    static_artifact_map=payload.static_artifact_map,
                    base_raw_observations=raw,
                    crop_origin_y=payload.crop_origin_y,
                    bounds=self.bounds,
                    accepted_foam_front_local_y=payload.accepted_foam_front_local_y,
                    accepted_foam_component_mask=payload.accepted_foam_component_mask,
                )
                if spatial_fallback is not None:
                    raw_frame = spatial_fallback
        except Exception as exc:
            return self._failure_outcome(
                _failure_reason(exc), PipelineFailureStage.EVIDENCE_CONSTRUCTION
            )
        try:
            canonical = self._phase_a(raw_frame)
        except Exception as exc:
            return self._failure_outcome(_failure_reason(exc), PipelineFailureStage.PHASE_A)
        try:
            reduction = self.__reducer.reduce(prior_record, canonical)
        except Exception as exc:
            return self._failure_outcome(
                _failure_reason(exc), PipelineFailureStage.TEMPORAL_EVALUATION
            )
        try:
            self._validate_reduction(canonical, prior_record, reduction)
        except Exception as exc:
            return self._failure_outcome(_failure_reason(exc), PipelineFailureStage.PHASE_B)
        try:
            prepared_store = self._prepare_run_store(
                prior_store, payload.glass_id, reduction.next_record
            )
            self._validate_prepared_run_store(
                prior_store, prepared_store, payload.glass_id, reduction.next_record
            )
        except Exception as exc:
            return self._failure_outcome(
                _failure_reason(exc), PipelineFailureStage.OUTCOME_PREPARATION
            )
        self.__replacement_count += 1
        self.__store = prepared_store
        return reduction.outcome

    def _reset_owned(self, glass_id: str) -> None:
        prior = self.__store
        records = dict(prior.records)
        records.pop(glass_id, None)
        prepared = TemporalStoreState(records, prior.epoch + 1)
        self._validate_prepared_reset_store(prior, prepared, glass_id)
        self.__replacement_count += 1
        self.__store = prepared
        return None

    def _reset_all_owned(self) -> None:
        prior = self.__store
        prepared = TemporalStoreState({}, prior.epoch + 1)
        self._validate_prepared_reset_store(prior, prepared, None)
        self.__replacement_count += 1
        self.__store = prepared
        return None

    def _snapshot_owned(self, glass_id: str) -> TemporalAuditSnapshot:
        store = self.__store
        record = store.records.get(glass_id)
        if record is None:
            record = GlassTemporalRecord.initial(glass_id)
        return TemporalAuditSnapshot(
            glass_id=glass_id,
            epoch=store.epoch,
            version=record.version,
            state=record.temporal_state,
        )

    def _reject_reentry(self) -> None:
        if self._is_owner_active():
            raise TemporalReentryError("temporal_reentry_rejected")

    def _is_owner_active(self) -> bool:
        return bool(getattr(self.__owner_context, "active", False))

    @property
    def _debug_command_sequences(self) -> tuple[tuple[int, ...], tuple[int, ...]]:
        with self.__ingress:
            return tuple(self.__assigned_sequences), tuple(self.__execution_sequences)

    @property
    def _debug_store_reference(self) -> TemporalStoreState:
        return self.__store

    @property
    def _debug_store_replacement_count(self) -> int:
        return self.__replacement_count


    def _failure_outcome(
        self,
        reason: str,
        stage: PipelineFailureStage = PipelineFailureStage.EXTERNAL_RUNNER,
        *,
        visibility: float = 0.0,
    ) -> PipelineFailureOutcome:
        return PipelineFailureOutcome(
            reason=(str(reason)[:160] or "oil_hypothesis_execution_failed"),
            stage=stage,
            visibility=max(0.0, min(1.0, float(visibility))),
        )

    def _phase_a(self, frame: SuccessfulPipelineFrame) -> SuccessfulPipelineFrame:
        if type(frame) is not SuccessfulPipelineFrame:
            raise TypeError("Unsupported successful pipeline frame variant.")
        canonical = _canonical_dataclass(frame)
        if type(canonical) is not SuccessfulPipelineFrame:
            raise TypeError("Successful frame canonicalization changed its variant.")
        self._validate_evidence_graph(canonical)
        current = self._canonical_current(
            canonical.current_observation,
            canonical.hypotheses,
        )
        canonical = replace(canonical, current_observation=current)
        _json_safe(canonical.diagnostics)
        return canonical

    def _validate_evidence_graph(self, frame: SuccessfulPipelineFrame) -> None:
        raw = frame.raw_observations
        proposals = frame.proposals
        hypotheses = frame.hypotheses
        if len(raw) > self.bounds.total_raw_observations:
            raise ValueError("Raw observation bound exceeded.")
        if len(proposals) > self.bounds.total_proposals:
            raise ValueError("Proposal bound exceeded.")
        if len(hypotheses) > self.bounds.semantic_hypotheses:
            raise ValueError("Semantic hypothesis bound exceeded.")
        _unique_identities(raw, "raw observations")
        _unique_identities(proposals, "proposals")
        _unique_identities(hypotheses, "hypotheses")

        if raw != tuple(sorted(raw, key=lambda item: item.canonical_key)):
            raise ValueError("Raw observations are not in canonical order.")
        per_source_scale: dict[tuple[object, int], int] = {}
        source_indices: dict[tuple[object, int], list[int]] = {}
        source_offset: float | None = None
        raw_by_id = {item.identity: item for item in raw}
        for item in raw:
            key = (item.source_family, item.measurement_scale)
            per_source_scale[key] = per_source_scale.get(key, 0) + 1
            source_indices.setdefault(key, []).append(item.source_local_index)
            if not 0.0 <= item.local_y <= frame.frame_height - 1 + 1e-12:
                raise ValueError("Raw observation Y is outside the source frame.")
            if not _same(item.measurement_width_px, float(frame.frame_width)):
                raise ValueError("Raw observation width disagrees with the source frame.")
            offset = item.source_y - item.local_y
            if source_offset is None:
                source_offset = offset
            elif not _same(offset, source_offset):
                raise ValueError("Raw observation source/local Y provenance is incoherent.")
            self._validate_raw_observation_shape(item)
            if item.identity != _raw_observation_identity(item):
                raise ValueError("Raw observation identity disagrees with canonical content.")
        if any(
            count > self.bounds.observations_per_source_scale
            for count in per_source_scale.values()
        ):
            raise ValueError("Observation source/scale bound exceeded.")
        for indices in source_indices.values():
            if sorted(indices) != list(range(len(indices))):
                raise ValueError("Observation source-local indices are not canonical.")

        proposal_by_id = {item.identity: item for item in proposals}
        retained = 0
        for proposal in proposals:
            members = tuple(raw_by_id.get(identity) for identity in proposal.member_ids)
            if any(item is None for item in members):
                raise ValueError("Proposal references a non-canonical observation.")
            typed_members = tuple(item for item in members if item is not None)
            if len(typed_members) > self.bounds.members_per_proposal:
                raise ValueError("Proposal member bound exceeded.")
            retained += len(typed_members)
            ys = sorted(item.local_y for item in typed_members)
            if not ys:
                raise ValueError("Proposal must retain positive evidence.")
            if not _same(proposal.minimum_local_y, ys[0]) or not _same(
                proposal.maximum_local_y, ys[-1]
            ):
                raise ValueError("Proposal Y bounds disagree with member content.")
            if not _same(proposal.representative_local_y, float(median(ys))):
                raise ValueError("Proposal representative Y disagrees with members.")
            source_offset = float(
                median(item.source_y - item.local_y for item in typed_members)
            )
            if not _same(
                proposal.representative_source_y,
                proposal.representative_local_y + source_offset,
            ):
                raise ValueError("Proposal source Y disagrees with member provenance.")
            if proposal.source_family_count != len(
                {item.source_family for item in typed_members}
            ):
                raise ValueError("Proposal source-family count is not canonical.")
            expected_identity = stable_digest(
                "oil-shadow-proposal",
                (
                    ("member_ids", "|".join(proposal.member_ids)),
                    ("minimum_local_y", proposal.minimum_local_y),
                    ("maximum_local_y", proposal.maximum_local_y),
                    ("representative_local_y", proposal.representative_local_y),
                ),
            )
            if proposal.identity != expected_identity:
                raise ValueError("Proposal identity disagrees with canonical content.")
        if retained > self.bounds.total_retained_members:
            raise ValueError("Retained proposal member bound exceeded.")

        hypothesis_by_id = {item.identity: item for item in hypotheses}
        for hypothesis in hypotheses:
            if not hypothesis.proposal_ids or not set(hypothesis.proposal_ids) <= set(proposal_by_id):
                raise ValueError("Hypothesis references a non-canonical proposal.")
            if not set(hypothesis.observation_ids) <= set(raw_by_id):
                raise ValueError("Hypothesis references a non-canonical observation.")
            canonical_proposals = tuple(proposal_by_id[item] for item in hypothesis.proposal_ids)
            expected_observations = tuple(
                sorted({member for proposal in canonical_proposals for member in proposal.member_ids})
            )
            if hypothesis.observation_ids != expected_observations:
                raise ValueError("Hypothesis observations disagree with proposal membership.")
            expected_provenance = tuple(
                sorted(set(hypothesis.proposal_ids) | set(hypothesis.observation_ids))
            )
            if hypothesis.provenance != expected_provenance:
                raise ValueError("Hypothesis provenance disagrees with evidence content.")
            expected_minimum = min(item.minimum_local_y for item in canonical_proposals)
            expected_maximum = max(item.maximum_local_y for item in canonical_proposals)
            if not _same(hypothesis.minimum_local_y, expected_minimum) or not _same(
                hypothesis.maximum_local_y, expected_maximum
            ):
                raise ValueError("Hypothesis Y bounds disagree with proposal content.")
            proposal_offsets = [
                item.representative_source_y - item.representative_local_y
                for item in canonical_proposals
            ]
            if not _same(
                hypothesis.representative_source_y,
                hypothesis.representative_local_y + float(median(proposal_offsets)),
            ):
                raise ValueError("Hypothesis source Y disagrees with proposal provenance.")
            if hypothesis.diameter_px > self.bounds.maximum_proposal_diameter_px + 1e-12:
                raise ValueError("Hypothesis evidence diameter exceeds its bound.")
            self._validate_hypothesis_summaries(hypothesis, canonical_proposals)
            if hypothesis.identity != _hypothesis_identity(hypothesis):
                raise ValueError("Hypothesis identity disagrees with canonical content.")

        current = frame.current_observation
        if type(current) not in {
            ShadowBoundaryObservation,
            ShadowNoInterfaceObservation,
            ShadowAmbiguousObservation,
            ShadowUnavailableObservation,
        }:
            raise TypeError("Unsupported current-observation subclass.")
        if isinstance(current, ShadowBoundaryObservation):
            canonical = hypothesis_by_id.get(current.hypothesis.identity)
            if canonical is None or canonical != current.hypothesis:
                raise ValueError("Boundary observation is not canonical evidence.")
            if not set(current.alternatives) <= set(hypothesis_by_id):
                raise ValueError("Boundary alternatives are not canonical evidence.")
            if current.hypothesis.identity in current.alternatives:
                raise ValueError("Boundary alternatives duplicate the selected hypothesis.")
        elif isinstance(current, ShadowNoInterfaceObservation):
            if not current.evidence.available:
                raise ValueError("Positive no-interface evidence is unavailable.")
            expected_competing = max(
                (item.boundary_likelihood for item in hypotheses),
                default=0.0,
            )
            if not _same(current.evidence.competing_boundary_likelihood, expected_competing):
                raise ValueError("No-interface competing-boundary evidence is not canonical.")
        elif isinstance(current, ShadowAmbiguousObservation):
            if not set(current.hypothesis_ids) <= set(hypothesis_by_id):
                raise ValueError("Ambiguous observation references non-canonical evidence.")
            referenced = tuple(hypothesis_by_id[item] for item in current.hypothesis_ids)
            if current.projected_source_y is not None:
                if not any(
                    _same(current.projected_source_y, item.representative_source_y)
                    for item in referenced
                ):
                    raise ValueError("Ambiguous diagnostic Y is not canonical.")
                if not any(
                    _same(current.projected_source_y, item.representative_source_y)
                    and _same(current.boundary_likelihood, item.boundary_likelihood)
                    and _same(current.artifact_likelihood, item.artifact_likelihood)
                    and _same(current.ambiguity_likelihood, item.ambiguity_likelihood)
                    for item in referenced
                ):
                    raise ValueError("Ambiguous likelihoods disagree with canonical evidence.")
        _json_safe(_diagnostic_payload(current))

    def _validate_raw_observation_shape(self, item: RawEdgeObservation) -> None:
        if item.source_family is ShadowSourceFamily.HOUGH:
            if item.measurement_scale != 1 or not _same(item.band_height_px, 1.0):
                raise ValueError("Hough observation scale/band shape is invalid.")
            if item.source_angle_deg is None or item.source_angle_deg > 12.0 + 1e-12:
                raise ValueError("Hough observation angle is unavailable or out of range.")
            if item.polarity_available or abs(item.polarity) > 1e-12:
                raise ValueError("Hough observation cannot claim signed polarity evidence.")
            return
        if item.source_angle_deg is not None:
            raise ValueError("Non-Hough observation cannot retain a line angle.")
        if item.source_family in {ShadowSourceFamily.SOBEL, ShadowSourceFamily.CANNY}:
            if item.measurement_scale != 1 or not _same(item.band_height_px, 1.0):
                raise ValueError("Pixel-edge observation scale/band shape is invalid.")
            return
        if item.source_family is ShadowSourceFamily.SOBEL_DISTRIBUTED:
            scale = max(self.bounds.broad_band_scales)
            if item.measurement_scale != scale:
                raise ValueError("Distributed Sobel observation scale is invalid.")
            if not 2.0 * scale <= item.band_height_px <= 3.0 * scale:
                raise ValueError("Distributed Sobel observation span is invalid.")
            return
        if item.source_family is ShadowSourceFamily.REGION_STEP:
            if item.measurement_scale not in self.bounds.broad_band_scales:
                raise ValueError("Region-step observation uses an unsupported scale.")
            if not _same(item.band_height_px, float(item.measurement_scale)):
                raise ValueError("Region-step observation band disagrees with its scale.")
            return
        raise TypeError("Unsupported raw observation source family.")

    def _validate_hypothesis_summaries(
        self,
        hypothesis: SemanticHypothesis,
        proposals: tuple[BoundedYProposal, ...],
    ) -> None:
        broad = hypothesis.broad
        broad_scales = tuple(item.band_scale for item in broad.scales)
        if broad_scales != self.bounds.broad_band_scales:
            raise ValueError("Broad evidence scales are not canonical.")
        available_rows = tuple(item for item in broad.scales if item.available)
        if broad.available_scale_count != len(available_rows):
            raise ValueError("Broad available-scale count disagrees with evidence rows.")
        strengths = tuple(item.strength for item in available_rows)
        expected_scale_consistency = (
            0.0
            if not strengths
            else _bounded_unit(1.0 - (max(strengths) - min(strengths)))
        )
        signs = tuple(
            1.0 if item.signed_contrast > 0.0 else -1.0
            for item in available_rows
            if abs(item.signed_contrast) > 1e-12
        )
        expected_polarity_consistency = (
            0.0
            if not signs
            else max(signs.count(1.0), signs.count(-1.0)) / len(signs)
        )
        expected_signed = (
            0.0
            if not available_rows
            else sum(item.signed_contrast for item in available_rows) / len(available_rows)
        )
        expected_strength = (
            0.0
            if not strengths
            else _bounded_unit(
                sum(strengths) / len(strengths)
                * (0.55 + 0.45 * expected_scale_consistency)
            )
        )
        expected_visibility = (
            0.0
            if not broad.scales
            else _bounded_unit(
                sum(item.visible_support for item in broad.scales) / len(broad.scales)
            )
        )
        expected_glare = (
            0.0
            if not broad.scales
            else _bounded_unit(
                sum(item.glare_conflict for item in broad.scales) / len(broad.scales)
            )
        )
        expected_exclusion = (
            0.0
            if not broad.scales
            else _bounded_unit(
                sum(item.exclusion_conflict for item in broad.scales) / len(broad.scales)
            )
        )
        if not all((
            _same(broad.scale_consistency, expected_scale_consistency),
            _same(broad.polarity_consistency, expected_polarity_consistency),
            _same(broad.signed_contrast, expected_signed),
            _same(broad.strength, expected_strength),
            _same(broad.visibility, expected_visibility),
            _same(broad.glare_conflict, expected_glare),
            _same(broad.exclusion_conflict, expected_exclusion),
        )):
            raise ValueError("Broad evidence summary disagrees with retained scale content.")
        if available_rows:
            expected_transition = float(
                median(item.transition_local_y for item in available_rows)
            )
            if not _same(broad.transition_local_y, expected_transition):
                raise ValueError("Broad transition Y disagrees with retained scale content.")
        elif not any(
            _same(broad.transition_local_y, item.representative_local_y)
            for item in proposals
        ):
            raise ValueError("Unavailable broad transition Y lacks proposal provenance.")

        narrow = hypothesis.narrow
        if tuple(item.scale for item in narrow.scales) != self.bounds.narrow_scales:
            raise ValueError("Narrow evidence scales are not canonical.")
        available_narrow = tuple(item for item in narrow.scales if item.available)
        if narrow.available is not bool(available_narrow):
            raise ValueError("Narrow availability disagrees with retained scale content.")
        expected_persistence = (
            0.0
            if not available_narrow
            else _bounded_unit(
                sum(item.peak_strength for item in available_narrow)
                / len(available_narrow)
            )
        )
        if not _same(narrow.scale_persistence, expected_persistence):
            raise ValueError("Narrow scale persistence is not canonical.")
        if narrow.paired_edge_separation_px > self.bounds.narrow_lobe_search_radius_px + 1e-12:
            raise ValueError("Narrow paired-edge separation exceeds its search bound.")
        if abs(narrow.center_offset_px) > self.bounds.narrow_lobe_search_radius_px / 2.0 + 1e-12:
            raise ValueError("Narrow center offset exceeds its search bound.")
        if hypothesis.static_prior.contribution > self.bounds.maximum_static_prior + 1e-12:
            raise ValueError("Static-prior contribution exceeds its configured bound.")
        if len(proposals) == 1:
            expected_availability = _bounded_unit(
                0.55 * (broad.available_scale_count / max(1, len(broad.scales)))
                + 0.45 * float(narrow.available)
            )
            expected_visibility = _bounded_unit(
                0.65 * broad.visibility + 0.35 * (1.0 - narrow.glare_overlap)
            )
            if not _same(hypothesis.evidence_availability, expected_availability):
                raise ValueError("Hypothesis evidence availability is not canonical.")
            if not _same(hypothesis.visibility, expected_visibility):
                raise ValueError("Hypothesis visibility is not canonical.")
        if (
            hypothesis.boundary_likelihood - hypothesis.artifact_likelihood >= 0.14
            and hypothesis.ambiguity_likelihood < 0.65
        ):
            expected_label = ShadowHypothesisLabel.BOUNDARY_LIKE
        elif (
            hypothesis.artifact_likelihood - hypothesis.boundary_likelihood >= 0.14
            and hypothesis.ambiguity_likelihood < 0.65
        ):
            expected_label = ShadowHypothesisLabel.ARTIFACT_LIKE
        else:
            expected_label = ShadowHypothesisLabel.AMBIGUOUS
        if hypothesis.label is not expected_label:
            raise ValueError("Hypothesis label disagrees with canonical likelihoods.")

    def _canonical_current(
        self,
        current: ShadowCurrentObservation,
        hypotheses: tuple[SemanticHypothesis, ...],
    ) -> ShadowCurrentObservation:
        by_id = {item.identity: item for item in hypotheses}
        if isinstance(current, ShadowBoundaryObservation):
            selected = by_id[current.hypothesis.identity]
            return ShadowBoundaryObservation(
                hypothesis=selected,
                alternatives=tuple(current.alternatives),
                diagnostics=tuple(current.diagnostics),
            )
        if isinstance(current, ShadowNoInterfaceObservation):
            return ShadowNoInterfaceObservation(
                evidence=current.evidence,
                diagnostics=tuple(current.diagnostics),
            )
        if isinstance(current, ShadowAmbiguousObservation):
            return ShadowAmbiguousObservation(
                hypothesis_ids=tuple(current.hypothesis_ids),
                boundary_likelihood=current.boundary_likelihood,
                artifact_likelihood=current.artifact_likelihood,
                ambiguity_likelihood=current.ambiguity_likelihood,
                no_interface_likelihood=current.no_interface_likelihood,
                visibility=current.visibility,
                projected_source_y=current.projected_source_y,
                reason=current.reason,
                diagnostics=tuple(current.diagnostics),
            )
        if isinstance(current, ShadowUnavailableObservation):
            return ShadowUnavailableObservation(
                visibility=current.visibility,
                reason=current.reason,
                diagnostics=tuple(current.diagnostics),
            )
        raise TypeError("Unsupported current-observation variant.")

    def _validate_decision(
        self,
        current: ShadowCurrentObservation,
        hypotheses: tuple[SemanticHypothesis, ...],
        decision,
    ) -> None:
        if type(decision) not in {
            BoundaryAcceptedDecision,
            NoInterfaceAcceptedDecision,
            AmbiguousDecision,
            EvidenceUnavailableDecision,
            ReacquisitionPendingDecision,
        }:
            raise TypeError("Unsupported temporal-decision subclass.")
        _exact_dataclass_fields(decision)
        by_id = {item.identity: item for item in hypotheses}
        if isinstance(decision, BoundaryAcceptedDecision):
            if not isinstance(current, ShadowBoundaryObservation):
                raise ValueError("Boundary decision/current observation mismatch.")
            canonical = by_id.get(decision.selected_hypothesis.identity)
            if canonical is None or canonical != decision.selected_hypothesis:
                raise ValueError("Boundary decision selection is not canonical.")
            if canonical != current.hypothesis:
                raise ValueError("Boundary decision disagrees with current evidence.")
            if not _same(decision.accepted_source_y, canonical.representative_source_y):
                raise ValueError("Boundary decision source Y disagrees with evidence.")
        elif isinstance(decision, NoInterfaceAcceptedDecision):
            if not isinstance(current, ShadowNoInterfaceObservation):
                raise ValueError("No-interface decision/current observation mismatch.")
            if decision.evidence != current.evidence or not decision.evidence.available:
                raise ValueError("No-interface decision evidence is not canonical.")
        elif isinstance(decision, AmbiguousDecision):
            if not isinstance(current, ShadowAmbiguousObservation):
                raise ValueError("Ambiguous decision/current observation mismatch.")
            if decision.hypothesis_ids != current.hypothesis_ids:
                raise ValueError("Ambiguous decision identities disagree with evidence.")
            if not _same_optional(
                decision.projected_source_y,
                current.projected_source_y,
            ):
                raise ValueError("Ambiguous decision diagnostic Y disagrees with evidence.")
        elif isinstance(decision, EvidenceUnavailableDecision):
            if not isinstance(current, ShadowUnavailableObservation):
                raise ValueError("Unavailable decision/current observation mismatch.")
            if decision.reason != current.reason or not _same(
                decision.visibility,
                current.visibility,
            ):
                raise ValueError("Unavailable decision disagrees with successful evidence.")
        elif isinstance(decision, ReacquisitionPendingDecision):
            if not isinstance(current, ShadowBoundaryObservation):
                raise ValueError("Reacquisition decision/current observation mismatch.")
            canonical = by_id.get(decision.pending_hypothesis.identity)
            if canonical is None or canonical != decision.pending_hypothesis:
                raise ValueError("Reacquisition decision is not canonical.")
            if canonical != current.hypothesis:
                raise ValueError("Reacquisition decision disagrees with current evidence.")
        if decision.tracker_action.value not in {"ACCEPT_BOUNDARY", "NO_UPDATE"}:
            raise ValueError("Temporal decision forged a compatibility action.")
        if decision.smoothing_action.value not in {
            "PRESERVE",
            "CLEAR_BEFORE_ACCEPT",
            "CLEAR_STALE_AFTER_STABLE_ABSENCE",
        }:
            raise ValueError("Temporal decision forged a smoothing action.")

    def _validate_reduction(
        self,
        frame: SuccessfulPipelineFrame,
        prior_record: GlassTemporalRecord,
        reduction: CanonicalTemporalReduction,
    ) -> None:
        if type(reduction) is not CanonicalTemporalReduction:
            raise TypeError("Unsupported canonical temporal reduction.")
        _exact_dataclass_fields(reduction)
        decision = _canonical_dataclass(reduction.decision)
        if decision != reduction.decision:
            raise ValueError("Reduction decision canonicalization changed content.")
        self._validate_next_record(
            prior_record, reduction.next_record, reduction.decision.resources
        )
        self._validate_decision(
            frame.current_observation, frame.hypotheses, reduction.decision
        )
        state = reduction.next_record.temporal_state
        current = frame.current_observation
        if isinstance(current, ShadowBoundaryObservation):
            if not _same(
                state.last_static_contribution,
                current.hypothesis.static_prior.contribution,
            ) or not _same(
                state.last_static_available,
                float(current.hypothesis.static_prior.available),
            ):
                raise ValueError("Reduced static-prior state disagrees with boundary evidence.")
        elif state.last_static_contribution or state.last_static_available:
            raise ValueError("Non-boundary reduction retained static-prior state.")
        self._validate_transition_coherence(prior_record, reduction.decision, state)
        self._validate_prepared_outcome(reduction.outcome, frame, reduction)
        if reduction.resource_metrics != reduction.outcome.resources:
            raise ValueError("Reduction resource metrics disagree with its outcome.")
        if reduction.tracker_action is not reduction.outcome.tracker_action:
            raise ValueError("Reduction tracker action is incoherent.")
        if reduction.smoothing_action is not reduction.outcome.smoothing_action:
            raise ValueError("Reduction smoothing action is incoherent.")

    def _validate_next_record(
        self,
        prior_record: GlassTemporalRecord,
        record: GlassTemporalRecord,
        resources: TemporalResourceMetrics,
    ) -> None:
        expected = self._validate_record_value(record)
        if record.glass_id != prior_record.glass_id:
            raise ValueError("Proposed temporal record targets the wrong Glass.")
        if record.version != prior_record.version + 1:
            raise ValueError("Proposed temporal record version is invalid.")
        if resources != expected:
            raise ValueError("Proposed resource summary disagrees with state.")
        if resources.retained_scalar_count > self.__reducer.retained_scalar_limit:
            raise ValueError("Proposed retained temporal scalar bound exceeded.")

    def _validate_record_value(
        self,
        record: GlassTemporalRecord,
    ) -> TemporalResourceMetrics:
        if type(record) is not GlassTemporalRecord:
            raise TypeError("Unsupported temporal record.")
        _exact_dataclass_fields(record)
        if record.version < 1:
            raise ValueError("Stored temporal record version must be positive.")
        state = record.temporal_state
        if type(state) is not GlassTemporalState:
            raise TypeError("Unsupported temporal state.")
        _exact_dataclass_fields(state)
        replace(state)
        if state.glass_id != record.glass_id:
            raise ValueError("Temporal record identity disagrees with state.")
        if len(state.beam) > self.bounds.temporal_beam_width:
            raise ValueError("Temporal beam bound exceeded.")
        history_length = max((len(item.history) for item in state.beam), default=0)
        if history_length > self.bounds.temporal_history_window:
            raise ValueError("Temporal history bound exceeded.")
        if state.pending_count >= self.bounds.reacquisition_frames:
            raise ValueError("Pending reacquisition counter is not bounded.")
        if state.no_interface_count > self.bounds.no_interface_clear_frames:
            raise ValueError("No-interface counter bound exceeded.")
        if state.unavailable_count > self.bounds.unavailable_clear_frames:
            raise ValueError("Unavailable counter bound exceeded.")
        if state.no_interface_count and state.unavailable_count:
            raise ValueError("Mutually exclusive absence counters are both active.")
        if state.pending_count == 0:
            if state.pending_y is not None or state.pending_velocity is not None:
                raise ValueError("Cleared pending count retained pending motion state.")
        elif state.pending_y is None:
            raise ValueError("Pending reacquisition count requires a pending Y.")
        elif state.accepted_y is None:
            raise ValueError("Pending reacquisition requires an accepted boundary.")
        if state.accepted_y is None and state.accepted_velocity is not None:
            raise ValueError("Accepted velocity requires an accepted Y.")
        for item in state.beam:
            if type(item) is not _BeamItem:
                raise TypeError("Unsupported temporal beam item.")
            _exact_dataclass_fields(item)
            if len(item.history) > self.bounds.temporal_history_window:
                raise ValueError("Temporal beam history bound exceeded.")
            _json_safe(item.history)
            for history in item.history:
                if len(history) != 4:
                    raise ValueError("Temporal beam history row is malformed.")
            for scalar in (
                item.source_y,
                item.observation_score,
                item.cumulative_score,
                item.transition_cost,
                item.velocity,
            ):
                if scalar is not None and not math.isfinite(float(scalar)):
                    raise ValueError("Temporal beam scalar must be finite.")
        metrics = TemporalResourceMetrics(
            beam_count=len(state.beam),
            history_length=history_length,
            retained_scalar_count=sum(
                len(item.history) * 4 + 7 for item in state.beam
            ) + 12,
            reacquisition_count=state.pending_count,
        )
        if metrics.retained_scalar_count > self.__reducer.retained_scalar_limit:
            raise ValueError("Retained temporal scalar bound exceeded.")
        return metrics

    def _expected_resource_summary(
        self,
        frame: SuccessfulPipelineFrame,
        temporal: TemporalResourceMetrics,
    ) -> ShadowResourceSummary:
        proposals = frame.proposals
        return ShadowResourceSummary(
            raw_observation_count=len(frame.raw_observations),
            raw_observation_limit=self.bounds.total_raw_observations,
            broad_scale_count=len(self.bounds.broad_band_scales),
            broad_scale_limit=len(self.bounds.broad_band_scales),
            narrow_scale_count=len(self.bounds.narrow_scales),
            narrow_scale_limit=len(self.bounds.narrow_scales),
            narrow_examined_rows_per_hypothesis=min(
                frame.frame_height,
                2 * self.bounds.narrow_lobe_search_radius_px + 1,
            ),
            narrow_examined_rows_per_hypothesis_limit=(
                2 * self.bounds.narrow_lobe_search_radius_px + 1
            ),
            proposal_count=len(proposals),
            proposal_limit=self.bounds.total_proposals,
            maximum_proposal_diameter_px=max(
                (item.diameter_px for item in proposals),
                default=0.0,
            ),
            proposal_diameter_limit_px=self.bounds.maximum_proposal_diameter_px,
            maximum_members_per_proposal=max(
                (item.member_count for item in proposals),
                default=0,
            ),
            members_per_proposal_limit=self.bounds.members_per_proposal,
            retained_member_count=sum(item.member_count for item in proposals),
            retained_member_limit=self.bounds.total_retained_members,
            semantic_hypothesis_count=len(frame.hypotheses),
            semantic_hypothesis_limit=self.bounds.semantic_hypotheses,
            temporal_beam_count=temporal.beam_count,
            temporal_beam_limit=self.bounds.temporal_beam_width,
            temporal_history_length=temporal.history_length,
            temporal_history_limit=self.bounds.temporal_history_window,
            retained_temporal_scalar_count=temporal.retained_scalar_count,
            retained_temporal_scalar_limit=self.__reducer.retained_scalar_limit,
            static_prior_scalar_count=2,
            static_prior_scalar_limit=self.bounds.static_prior_scalars_per_glass,
            debug_scalar_count=0,
            debug_scalar_limit=self.bounds.maximum_debug_scalar_count,
        )

    def _prepare_run_store(
        self,
        prior: TemporalStoreState,
        glass_id: str,
        next_record: GlassTemporalRecord,
    ) -> TemporalStoreState:
        records = dict(prior.records)
        records[glass_id] = next_record
        return TemporalStoreState(records, prior.epoch + 1)

    def _validate_prepared_run_store(
        self,
        prior: TemporalStoreState,
        prepared: TemporalStoreState,
        glass_id: str,
        next_record: GlassTemporalRecord,
    ) -> None:
        self._validate_store_shape(prepared)
        if prepared.epoch != prior.epoch + 1:
            raise ValueError("Successful run must advance the store epoch once.")
        expected_keys = set(prior.records) | {glass_id}
        if set(prepared.records) != expected_keys:
            raise ValueError("Prepared run store changed the record domain.")
        if prepared.records[glass_id] is not next_record:
            raise ValueError("Prepared run store did not retain the reduced target record.")
        for key, record in prior.records.items():
            if key != glass_id and prepared.records[key] is not record:
                raise ValueError("Prepared run store replaced an untargeted Glass record.")

    def _validate_prepared_reset_store(
        self,
        prior: TemporalStoreState,
        prepared: TemporalStoreState,
        glass_id: str | None,
    ) -> None:
        self._validate_store_shape(prepared)
        if prepared.epoch != prior.epoch + 1:
            raise ValueError("Reset must advance the store epoch once.")
        if glass_id is None:
            if prepared.records:
                raise ValueError("Global reset must prepare an empty temporal store.")
            return
        expected_keys = set(prior.records) - {glass_id}
        if set(prepared.records) != expected_keys:
            raise ValueError("Glass reset changed the wrong record domain.")
        for key in expected_keys:
            if prepared.records[key] is not prior.records[key]:
                raise ValueError("Glass reset replaced an untargeted Glass record.")

    def _validate_store_shape(self, store: TemporalStoreState) -> None:
        if type(store) is not TemporalStoreState:
            raise TypeError("Unsupported temporal store variant.")
        _exact_dataclass_fields(store)
        if type(store.records).__name__ != "mappingproxy":
            raise TypeError("Temporal store records must be immutable.")
        for key, record in store.records.items():
            if key != record.glass_id:
                raise ValueError("Temporal store record identity is incoherent.")
            self._validate_record_value(record)


    def _validate_transition_coherence(
        self,
        prior_record: GlassTemporalRecord,
        decision,
        state: GlassTemporalState,
    ) -> None:
        prior = prior_record.temporal_state
        pending_cleared = (
            state.pending_y is None
            and state.pending_velocity is None
            and state.pending_count == 0
        )
        if isinstance(decision, BoundaryAcceptedDecision):
            y = decision.accepted_source_y
            if not _same_optional(state.accepted_y, y):
                raise ValueError("Accepted outcome Y disagrees with proposed state.")
            if not pending_cleared or state.no_interface_count or state.unavailable_count:
                raise ValueError("Accepted transition retained incompatible temporal state.")
            if state.smoothing_invalidated:
                raise ValueError("Accepted transition cannot retain invalidated smoothing.")
            if decision.acceptance_mode is BoundaryAcceptanceMode.INITIAL:
                if prior.accepted_y is not None or state.accepted_velocity is not None:
                    raise ValueError("Initial acceptance requires no prior accepted motion.")
            elif decision.acceptance_mode is BoundaryAcceptanceMode.CONTINUOUS:
                if prior.accepted_y is None:
                    raise ValueError("Continuous acceptance requires a prior accepted boundary.")
                expected_velocity = y - prior.accepted_y
                if not _same_optional(state.accepted_velocity, expected_velocity):
                    raise ValueError("Continuous acceptance velocity is incoherent.")
                continuity = self.bounds.maximum_proposal_diameter_px * 4.0
                predicted = prior.accepted_y + (prior.accepted_velocity or 0.0)
                if abs(y - prior.accepted_y) > continuity and abs(y - predicted) > continuity:
                    raise ValueError("Continuous acceptance violates motion continuity.")
            elif decision.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED:
                if prior.accepted_y is None or state.accepted_velocity is not None:
                    raise ValueError("Reacquired acceptance requires prior state and reset velocity.")
                continuity = self.bounds.maximum_proposal_diameter_px * 4.0
                predicted = prior.accepted_y + (prior.accepted_velocity or 0.0)
                if abs(y - prior.accepted_y) <= continuity or abs(y - predicted) <= continuity:
                    raise ValueError("Reacquired acceptance was still continuously reachable.")
                _velocity, expected_count = self._expected_pending_motion(prior, y)
                if expected_count < self.bounds.reacquisition_frames:
                    raise ValueError("Reacquired acceptance lacks bounded pending history.")
            else:
                raise TypeError("Unsupported boundary acceptance mode.")
            return

        if isinstance(decision, ReacquisitionPendingDecision):
            y = decision.pending_hypothesis.representative_source_y
            if prior.accepted_y is None:
                raise ValueError("Pending reacquisition requires a prior accepted boundary.")
            continuity = self.bounds.maximum_proposal_diameter_px * 4.0
            predicted = prior.accepted_y + (prior.accepted_velocity or 0.0)
            if abs(y - prior.accepted_y) <= continuity or abs(y - predicted) <= continuity:
                raise ValueError("Pending reacquisition was continuously reachable.")
            expected_velocity, expected_count = self._expected_pending_motion(prior, y)
            if not _same_optional(state.pending_y, y):
                raise ValueError("Pending reacquisition Y disagrees with decision.")
            if state.pending_count != expected_count or not _same_optional(
                state.pending_velocity, expected_velocity
            ):
                raise ValueError("Pending reacquisition motion/count is incoherent.")
            if not 1 <= state.pending_count < self.bounds.reacquisition_frames:
                raise ValueError("Pending reacquisition count is outside its pending range.")
            if not _same_optional(state.accepted_y, prior.accepted_y) or not _same_optional(
                state.accepted_velocity, prior.accepted_velocity
            ):
                raise ValueError("Pending reacquisition changed accepted state.")
            if state.no_interface_count or state.unavailable_count:
                raise ValueError("Pending reacquisition retained absence counters.")
            if state.smoothing_invalidated != prior.smoothing_invalidated:
                raise ValueError("Pending reacquisition changed smoothing authority.")
            return

        if isinstance(decision, NoInterfaceAcceptedDecision):
            expected_count = min(
                self.bounds.no_interface_clear_frames, prior.no_interface_count + 1
            )
            stable = expected_count >= self.bounds.no_interface_clear_frames
            if state.no_interface_count != expected_count or state.unavailable_count:
                raise ValueError("No-interface counters are incoherent.")
            if not pending_cleared:
                raise ValueError("No-interface transition retained pending boundary state.")
            expected_mode = (
                AbsenceStabilityMode.STABLE if stable else AbsenceStabilityMode.PENDING
            )
            if decision.stability_mode is not expected_mode:
                raise ValueError("No-interface stability mode disagrees with state.")
            if stable:
                if state.accepted_y is not None or state.accepted_velocity is not None:
                    raise ValueError("Stable no-interface transition retained accepted Y.")
                if not state.smoothing_invalidated:
                    raise ValueError("Stable no-interface transition must invalidate smoothing.")
            elif (
                not _same_optional(state.accepted_y, prior.accepted_y)
                or not _same_optional(state.accepted_velocity, prior.accepted_velocity)
                or state.smoothing_invalidated != prior.smoothing_invalidated
            ):
                raise ValueError("Pending no-interface transition changed accepted state.")
            return

        if isinstance(decision, EvidenceUnavailableDecision):
            expected_count = min(
                self.bounds.unavailable_clear_frames, prior.unavailable_count + 1
            )
            stable = expected_count >= self.bounds.unavailable_clear_frames
            if state.unavailable_count != expected_count or state.no_interface_count:
                raise ValueError("Unavailable counters are incoherent.")
            if not pending_cleared:
                raise ValueError("Unavailable transition retained pending boundary state.")
            expected_mode = (
                AbsenceStabilityMode.STABLE if stable else AbsenceStabilityMode.PENDING
            )
            if decision.stability_mode is not expected_mode:
                raise ValueError("Unavailable stability mode disagrees with state.")
            if stable:
                if state.accepted_y is not None or state.accepted_velocity is not None:
                    raise ValueError("Stable unavailable transition retained accepted Y.")
                if not state.smoothing_invalidated or state.beam:
                    raise ValueError("Stable unavailable transition did not clear stale state.")
            elif (
                not _same_optional(state.accepted_y, prior.accepted_y)
                or not _same_optional(state.accepted_velocity, prior.accepted_velocity)
                or state.smoothing_invalidated != prior.smoothing_invalidated
            ):
                raise ValueError("Pending unavailable transition changed accepted state.")
            return

        if isinstance(decision, AmbiguousDecision):
            if state.no_interface_count or state.unavailable_count:
                raise ValueError("Ambiguous transition retained incompatible counters.")
            if not pending_cleared:
                if not _pending_path_compatible(
                    self.bounds,
                    prior,
                    decision.projected_source_y,
                ):
                    raise ValueError("Ambiguous transition retained an incompatible pending path.")
                if (
                    not _same_optional(state.pending_y, prior.pending_y)
                    or not _same_optional(state.pending_velocity, prior.pending_velocity)
                    or state.pending_count != prior.pending_count
                ):
                    raise ValueError("Ambiguous transition advanced or changed pending state.")
            if (
                not _same_optional(state.accepted_y, prior.accepted_y)
                or not _same_optional(state.accepted_velocity, prior.accepted_velocity)
                or state.smoothing_invalidated != prior.smoothing_invalidated
            ):
                raise ValueError("Ambiguous transition changed accepted state.")
            return
        raise TypeError("Unsupported temporal transition coherence variant.")

    def _expected_pending_motion(
        self,
        prior: GlassTemporalState,
        y: float,
    ) -> tuple[float | None, int]:
        if prior.pending_y is None or not _pending_path_compatible(
            self.bounds,
            prior,
            y,
        ):
            return None, 1
        return y - prior.pending_y, prior.pending_count + 1

    def _validate_prepared_outcome(
        self,
        outcome: OilCanonicalOutcome,
        frame: SuccessfulPipelineFrame,
        reduction: CanonicalTemporalReduction,
    ) -> None:
        if type(outcome) not in {
            AcceptedBoundaryOutcome,
            NoInterfaceOutcome,
            AmbiguousOutcome,
            EvidenceUnavailableOutcome,
            ReacquisitionPendingOutcome,
        }:
            raise TypeError("Successful reduction prepared an unsupported outcome.")
        _exact_dataclass_fields(outcome)
        canonical = _canonical_dataclass(outcome)
        if canonical != outcome:
            raise ValueError("Prepared outcome canonicalization changed content.")
        if outcome.hypotheses != frame.hypotheses:
            raise ValueError("Prepared outcome evidence differs from Phase A.")
        base_resources = self._expected_resource_summary(
            frame, reduction.decision.resources
        )
        unfinalized = replace(outcome, resources=base_resources)
        expected_debug_count = _scalar_leaf_count(
            oil_runtime_metrics(unfinalized)
        ) + _scalar_leaf_count(oil_debug_detail(unfinalized))
        expected_resources = replace(
            base_resources, debug_scalar_count=expected_debug_count
        )
        if outcome.resources != expected_resources:
            raise ValueError("Prepared outcome resource summary is not canonical.")
        if outcome.resources.debug_scalar_count > self.bounds.maximum_debug_scalar_count:
            raise ValueError("Prepared outcome debug resource bound exceeded.")
        if outcome.tracker_action != reduction.decision.tracker_action:
            raise ValueError("Prepared outcome tracker action disagrees with decision.")
        if outcome.smoothing_action != reduction.decision.smoothing_action:
            raise ValueError("Prepared outcome smoothing action disagrees with decision.")
        decision = reduction.decision
        state = reduction.next_record.temporal_state
        if not _same(outcome.confidence, decision.confidence) or not _same(
            outcome.decision_margin, decision.decision_margin
        ):
            raise ValueError("Prepared outcome confidence disagrees with transition.")
        if outcome.reason != decision.reason:
            raise ValueError("Prepared outcome reason disagrees with transition.")
        if isinstance(decision, BoundaryAcceptedDecision):
            if not isinstance(outcome, AcceptedBoundaryOutcome):
                raise ValueError("Accepted decision prepared the wrong outcome variant.")
            if outcome.acceptance_mode is not decision.acceptance_mode:
                raise ValueError("Accepted outcome mode disagrees with transition.")
            if outcome.selected_hypothesis != decision.selected_hypothesis or not _same_optional(
                state.accepted_y, outcome.raw_source_y
            ):
                raise ValueError("Accepted outcome and committed Y are incoherent.")
        elif isinstance(decision, ReacquisitionPendingDecision):
            if not isinstance(outcome, ReacquisitionPendingOutcome):
                raise ValueError("Pending decision prepared the wrong outcome variant.")
            if outcome.pending_hypothesis != decision.pending_hypothesis or not _same_optional(
                state.pending_y, outcome.pending_hypothesis.representative_source_y
            ):
                raise ValueError("Pending outcome and proposed state are incoherent.")
        elif isinstance(decision, NoInterfaceAcceptedDecision):
            if not isinstance(outcome, NoInterfaceOutcome):
                raise ValueError("No-interface decision prepared the wrong outcome variant.")
            if outcome.evidence != decision.evidence or outcome.stability_mode is not decision.stability_mode:
                raise ValueError("No-interface outcome disagrees with transition.")
        elif isinstance(decision, EvidenceUnavailableDecision):
            if not isinstance(outcome, EvidenceUnavailableOutcome):
                raise ValueError("Unavailable decision prepared the wrong outcome variant.")
            if outcome.stability_mode is not decision.stability_mode or not _same(
                outcome.visibility, decision.visibility
            ):
                raise ValueError("Unavailable outcome disagrees with transition.")
        elif isinstance(decision, AmbiguousDecision):
            if not isinstance(outcome, AmbiguousOutcome):
                raise ValueError("Ambiguous decision prepared the wrong outcome variant.")
            if outcome.hypothesis_ids != decision.hypothesis_ids or not _same_optional(
                outcome.projected_source_y, decision.projected_source_y
            ):
                raise ValueError("Ambiguous outcome disagrees with transition.")
        _json_safe(oil_runtime_metrics(outcome))
        _json_safe(oil_debug_detail(outcome))

def _owned_readonly_array(value: np.ndarray) -> np.ndarray:
    if type(value) is not np.ndarray:
        raise TypeError("Oil command inputs must be numpy arrays.")
    owned = np.array(value, copy=True, order="K")
    owned.setflags(write=False)
    return owned


def _beam_order(item: _BeamItem) -> tuple[float, int, float, str]:
    kind_order = {
        ShadowObservationKind.BOUNDARY: 0,
        ShadowObservationKind.NO_INTERFACE: 1,
        ShadowObservationKind.AMBIGUOUS: 2,
        ShadowObservationKind.UNAVAILABLE: 3,
    }
    return (
        -item.cumulative_score,
        kind_order[item.kind],
        float("inf") if item.source_y is None else item.source_y,
        item.identity or "",
    )


def _unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Temporal scalar must be finite.")
    return min(1.0, max(0.0, number))

OilShadowPipeline = OilHypothesisPipeline


def outcome_hypotheses(outcome: OilCanonicalOutcome) -> tuple[SemanticHypothesis, ...]:
    return () if isinstance(outcome, PipelineFailureOutcome) else outcome.hypotheses


def oil_runtime_metrics(outcome: OilCanonicalOutcome) -> dict[str, Any]:
    failure = isinstance(outcome, PipelineFailureOutcome)
    hypotheses = outcome_hypotheses(outcome)
    resources = None if failure else outcome.resources
    selected = _selected_hypothesis(outcome)
    confidence = 0.0 if failure else float(outcome.confidence)
    margin = 0.0 if failure else float(outcome.decision_margin)
    status = "pipeline_failure" if failure else outcome.status.value
    reason = outcome.reason
    likelihoods = _outcome_likelihoods(outcome)
    no_interface = outcome.evidence if isinstance(outcome, NoInterfaceOutcome) else None
    metrics = {
        "oil_pipeline_available": not failure,
        "oil_pipeline_failure_reason": outcome.reason if failure else None,
        "oil_pipeline_failure_stage": outcome.stage.value if failure else None,
        "oil_decision_status": status,
        "oil_decision_reason": reason,
        "oil_selected_hypothesis_id": None if selected is None else selected.identity,
        "oil_temporal_projected_source_y": _projected_y(outcome),
        "oil_boundary_score": likelihoods["boundary"],
        "oil_artifact_score": likelihoods["artifact"],
        "oil_ambiguity_score": likelihoods["ambiguity"],
        "oil_no_interface_score": likelihoods["no_interface"],
        "oil_decision_confidence": confidence,
        "oil_decision_margin": margin,
        "oil_tracker_action": outcome.tracker_action.value,
        "oil_smoothing_action": outcome.smoothing_action.value,
        "oil_tracker_update_accepted": outcome.tracker_action.value == "ACCEPT_BOUNDARY",
        "oil_clear_smoothing": outcome.smoothing_action.value != "PRESERVE",
        "oil_reacquisition_count": 0,
        "oil_hypothesis_current_observation": _outcome_kind(outcome),
        "oil_no_interface_uniformity": 0.0 if no_interface is None else no_interface.region_uniformity,
        "oil_no_interface_weak_boundary": 0.0 if no_interface is None else no_interface.weak_boundary_evidence,
        "oil_no_interface_visibility": 0.0 if no_interface is None else no_interface.visibility,
        "oil_no_interface_glare_conflict": 0.0 if no_interface is None else no_interface.glare_conflict,
        "oil_no_interface_full_likelihood": 0.0 if no_interface is None else no_interface.full_likelihood,
        "oil_no_interface_empty_likelihood": 0.0 if no_interface is None else no_interface.empty_likelihood,
        "oil_no_interface_reason": "not_available" if no_interface is None else no_interface.reason,
    }
    resource_names = (
        "raw_observation_count",
        "raw_observation_limit",
        "broad_scale_count",
        "broad_scale_limit",
        "narrow_scale_count",
        "narrow_scale_limit",
        "narrow_examined_rows_per_hypothesis",
        "narrow_examined_rows_per_hypothesis_limit",
        "proposal_count",
        "proposal_limit",
        "maximum_proposal_diameter_px",
        "proposal_diameter_limit_px",
        "maximum_members_per_proposal",
        "members_per_proposal_limit",
        "retained_member_count",
        "retained_member_limit",
        "semantic_hypothesis_count",
        "semantic_hypothesis_limit",
        "temporal_beam_count",
        "temporal_beam_limit",
        "temporal_history_length",
        "temporal_history_limit",
        "retained_temporal_scalar_count",
        "retained_temporal_scalar_limit",
        "static_prior_scalar_count",
        "static_prior_scalar_limit",
        "debug_scalar_count",
        "debug_scalar_limit",
    )
    key_map = {
        "raw_observation_count": "oil_hypothesis_raw_observation_count",
        "raw_observation_limit": "oil_hypothesis_raw_observation_limit",
        "broad_scale_count": "oil_hypothesis_broad_scale_count",
        "broad_scale_limit": "oil_hypothesis_broad_scale_limit",
        "narrow_scale_count": "oil_hypothesis_narrow_scale_count",
        "narrow_scale_limit": "oil_hypothesis_narrow_scale_limit",
        "narrow_examined_rows_per_hypothesis": "oil_hypothesis_narrow_examined_rows_per_hypothesis",
        "narrow_examined_rows_per_hypothesis_limit": "oil_hypothesis_narrow_examined_rows_per_hypothesis_limit",
        "proposal_count": "oil_hypothesis_proposal_count",
        "proposal_limit": "oil_hypothesis_proposal_limit",
        "maximum_proposal_diameter_px": "oil_hypothesis_maximum_proposal_diameter_px",
        "proposal_diameter_limit_px": "oil_hypothesis_proposal_diameter_limit_px",
        "maximum_members_per_proposal": "oil_hypothesis_maximum_members_per_proposal",
        "members_per_proposal_limit": "oil_hypothesis_members_per_proposal_limit",
        "retained_member_count": "oil_hypothesis_retained_member_count",
        "retained_member_limit": "oil_hypothesis_retained_member_limit",
        "semantic_hypothesis_count": "oil_hypothesis_count",
        "semantic_hypothesis_limit": "oil_hypothesis_limit",
        "temporal_beam_count": "oil_hypothesis_temporal_beam_count",
        "temporal_beam_limit": "oil_hypothesis_temporal_beam_limit",
        "temporal_history_length": "oil_hypothesis_temporal_history_length",
        "temporal_history_limit": "oil_hypothesis_temporal_history_limit",
        "retained_temporal_scalar_count": "oil_hypothesis_retained_temporal_scalar_count",
        "retained_temporal_scalar_limit": "oil_hypothesis_retained_temporal_scalar_limit",
        "static_prior_scalar_count": "oil_hypothesis_static_prior_scalar_count",
        "static_prior_scalar_limit": "oil_hypothesis_static_prior_scalar_limit",
        "debug_scalar_count": "oil_hypothesis_debug_scalar_count",
        "debug_scalar_limit": "oil_hypothesis_debug_scalar_limit",
    }
    for name in resource_names:
        metrics[key_map[name]] = 0 if resources is None else getattr(resources, name)
    return metrics


def oil_debug_detail(outcome: OilCanonicalOutcome) -> dict[str, Any]:
    failure = isinstance(outcome, PipelineFailureOutcome)
    selected = _selected_hypothesis(outcome)
    resources = None if failure else outcome.resources
    return {
        "available": not failure,
        "failure_reason": outcome.reason if failure else None,
        "failure_stage": outcome.stage.value if failure else None,
        "current_observation": _outcome_kind(outcome),
        "temporal_status": "pipeline_failure" if failure else outcome.status.value,
        "temporal_reason": outcome.reason,
        "tracker_action": outcome.tracker_action.value,
        "smoothing_action": outcome.smoothing_action.value,
        "selected_hypothesis_id": None if selected is None else selected.identity,
        "projected_source_y": _projected_y(outcome),
        "decision_confidence": 0.0 if failure else outcome.confidence,
        "decision_margin": 0.0 if failure else outcome.decision_margin,
        "resource_counts": {
            "raw_observations": 0 if resources is None else resources.raw_observation_count,
            "proposals": 0 if resources is None else resources.proposal_count,
            "retained_members": 0 if resources is None else resources.retained_member_count,
            "hypotheses": 0 if resources is None else resources.semantic_hypothesis_count,
            "temporal_beam": 0 if resources is None else resources.temporal_beam_count,
            "temporal_history": 0 if resources is None else resources.temporal_history_length,
            "retained_temporal_scalars": 0 if resources is None else resources.retained_temporal_scalar_count,
        },
        "selected_evidence": None if selected is None else _hypothesis_detail(selected),
    }


def _hypothesis_detail(item: SemanticHypothesis) -> dict[str, Any]:
    return {
        "identity": item.identity,
        "label": item.label.value,
        "source_y": item.representative_source_y,
        "diameter_px": item.diameter_px,
        "observation_count": len(item.observation_ids),
        "proposal_count": len(item.proposal_ids),
        "boundary_likelihood": item.boundary_likelihood,
        "artifact_likelihood": item.artifact_likelihood,
        "ambiguity_likelihood": item.ambiguity_likelihood,
        "broad_strength": item.broad.strength,
        "broad_available_scales": item.broad.available_scale_count,
        "broad_scale_consistency": item.broad.scale_consistency,
        "narrow_peak_strength": item.narrow.peak_strength,
        "narrow_paired_edge_strength": item.narrow.paired_edge_strength,
        "visibility": item.visibility,
        "polarity_available": item.polarity_available,
        "polarity": item.polarity,
        "polarity_confidence": item.polarity_confidence,
        "static_prior_available": item.static_prior.available,
        "static_prior_contribution": item.static_prior.contribution,
    }


def _selected_hypothesis(outcome: OilCanonicalOutcome) -> SemanticHypothesis | None:
    if isinstance(outcome, AcceptedBoundaryOutcome):
        return outcome.selected_hypothesis
    if isinstance(outcome, ReacquisitionPendingOutcome):
        return outcome.pending_hypothesis
    return None


def _projected_y(outcome: OilCanonicalOutcome) -> float | None:
    if isinstance(outcome, AcceptedBoundaryOutcome):
        return outcome.raw_source_y
    if isinstance(outcome, AmbiguousOutcome):
        return outcome.projected_source_y
    return None


def _outcome_kind(outcome: OilCanonicalOutcome) -> str:
    if isinstance(outcome, AcceptedBoundaryOutcome):
        return "boundary"
    if isinstance(outcome, NoInterfaceOutcome):
        return "no_interface"
    if isinstance(outcome, AmbiguousOutcome):
        return "ambiguous"
    if isinstance(outcome, EvidenceUnavailableOutcome):
        return "unavailable"
    if isinstance(outcome, ReacquisitionPendingOutcome):
        return "boundary"
    return "pipeline_failure"


def _outcome_likelihoods(outcome: OilCanonicalOutcome) -> dict[str, float]:
    if isinstance(outcome, AcceptedBoundaryOutcome):
        item = outcome.selected_hypothesis
        return {
            "boundary": item.boundary_likelihood,
            "artifact": item.artifact_likelihood,
            "ambiguity": item.ambiguity_likelihood,
            "no_interface": 0.0,
        }
    if isinstance(outcome, NoInterfaceOutcome):
        return {
            "boundary": outcome.evidence.competing_boundary_likelihood,
            "artifact": 0.0,
            "ambiguity": 0.0,
            "no_interface": outcome.evidence.likelihood,
        }
    if isinstance(outcome, AmbiguousOutcome):
        return {
            "boundary": outcome.boundary_likelihood,
            "artifact": outcome.artifact_likelihood,
            "ambiguity": outcome.ambiguity_likelihood,
            "no_interface": outcome.no_interface_likelihood,
        }
    return {"boundary": 0.0, "artifact": 0.0, "ambiguity": 1.0, "no_interface": 0.0}


def _raw_observation_identity(item: RawEdgeObservation) -> str:
    if item.source_family is ShadowSourceFamily.HOUGH:
        scalar_items = (
            ("source_family", item.source_family.value),
            ("measurement_scale", item.measurement_scale),
            ("local_y", item.local_y),
            ("source_y", item.source_y),
            ("response_strength", item.response_strength),
            ("horizontal_support", item.horizontal_support),
            ("valid_mask_support", item.valid_mask_support),
            ("glare_visible_support", item.glare_visible_support),
            ("measurement_width_px", item.measurement_width_px),
            ("band_height_px", item.band_height_px),
            ("source_local_index", item.source_local_index),
            ("angle", item.source_angle_deg),
        )
    else:
        scalar_items = (
            ("source_family", item.source_family.value),
            ("measurement_scale", item.measurement_scale),
            ("local_y", item.local_y),
            ("source_y", item.source_y),
            ("polarity_available", item.polarity_available),
            ("polarity", item.polarity),
            ("response_strength", item.response_strength),
            ("horizontal_support", item.horizontal_support),
            ("valid_mask_support", item.valid_mask_support),
            ("glare_visible_support", item.glare_visible_support),
            ("measurement_width_px", item.measurement_width_px),
            ("band_height_px", item.band_height_px),
            ("source_local_index", item.source_local_index),
        )
    return stable_digest("oil-shadow-observation", scalar_items)


def _hypothesis_identity(item: SemanticHypothesis) -> str:
    if len(item.proposal_ids) == 1:
        return stable_digest(
            "oil-shadow-hypothesis",
            (
                ("proposal_id", item.proposal_ids[0]),
                ("representative_local_y", item.representative_local_y),
                ("boundary_likelihood", item.boundary_likelihood),
                ("artifact_likelihood", item.artifact_likelihood),
                ("ambiguity_likelihood", item.ambiguity_likelihood),
                ("polarity", item.polarity),
            ),
        )
    return stable_digest(
        "oil-shadow-deduplicated-hypothesis",
        (
            ("proposal_ids", "|".join(item.proposal_ids)),
            ("observation_ids", "|".join(item.observation_ids)),
            ("representative_local_y", item.representative_local_y),
            ("boundary", item.boundary_likelihood),
            ("artifact", item.artifact_likelihood),
            ("ambiguity", item.ambiguity_likelihood),
        ),
    )


def _bounded_unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Canonical bounded scalar must be finite.")
    return min(1.0, max(0.0, number))


def _canonical_dataclass(value):
    if not is_dataclass(value):
        raise TypeError("Canonical value must be a dataclass.")
    if type(value).__module__ != "oil_tracker.adapters.vision.oil_shadow_types":
        raise TypeError("Unsupported dataclass subclass at the oil trust boundary.")
    _exact_dataclass_fields(value)
    kwargs = {}
    for field in fields(value):
        kwargs[field.name] = _canonical_value(getattr(value, field.name))
    return type(value)(**kwargs)


def _canonical_value(value):
    if is_dataclass(value):
        return _canonical_dataclass(value)
    if isinstance(value, tuple):
        return tuple(_canonical_value(item) for item in value)
    if isinstance(value, Enum):
        return type(value)(value.value)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Canonical scalar must be finite.")
        return float(value)
    raise TypeError(f"Unsupported canonical value type: {type(value)!r}")


def _exact_dataclass_fields(value) -> None:
    expected = {field.name for field in fields(value)}
    actual = set(vars(value))
    if actual != expected:
        raise ValueError("Dataclass carries an extra/missing discriminator or field.")


def _unique_identities(values, name: str) -> None:
    identities = [item.identity for item in values]
    if len(identities) != len(set(identities)):
        raise ValueError(f"Duplicate {name} identities are prohibited.")


def _diagnostic_payload(current: ShadowCurrentObservation):
    if isinstance(current, ShadowBoundaryObservation):
        return current.diagnostics
    if isinstance(current, ShadowNoInterfaceObservation):
        return current.diagnostics
    if isinstance(current, ShadowAmbiguousObservation):
        return current.diagnostics
    if isinstance(current, ShadowUnavailableObservation):
        return current.diagnostics
    raise TypeError("Unsupported current observation.")


def _json_safe(value) -> None:
    json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def _pending_path_compatible(
    bounds: OilShadowBounds,
    state: GlassTemporalState,
    source_y: float | None,
) -> bool:
    if state.pending_y is None or source_y is None:
        return False
    tolerance = bounds.maximum_proposal_diameter_px * 2.0
    prediction = state.pending_y + (state.pending_velocity or 0.0)
    return (
        abs(source_y - state.pending_y) <= tolerance
        or abs(source_y - prediction) <= tolerance
    )


def _same(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9)


def _same_optional(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right
    return _same(left, right)


def _failure_reason(exc: Exception) -> str:
    return f"{type(exc).__name__}:{str(exc)[:120]}"


def _scalar_leaf_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_scalar_leaf_count(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return sum(_scalar_leaf_count(item) for item in value)
    return 1
