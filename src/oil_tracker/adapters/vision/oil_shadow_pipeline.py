from __future__ import annotations

from dataclasses import dataclass, replace
import math
from threading import Condition, Lock, local

import numpy as np

from .oil_pipeline_diagnostics import (
    oil_debug_detail,
    oil_runtime_metrics,
    outcome_hypotheses,
    scalar_leaf_count as _scalar_leaf_count,
)
from .oil_pipeline_validation import (
    OilPipelineValidator,
    _boundary_motion_envelope,
    _pending_path_compatible,
)
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
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowResourceSummary,
    ShadowUnavailableObservation,
    SuccessfulPipelineFrame,
    TemporalResourceMetrics,
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
        continuity = _boundary_motion_envelope(self.bounds)
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

        continuity = _boundary_motion_envelope(self.bounds)
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
        self.__validator = OilPipelineValidator(
            self.bounds,
            self.__reducer.retained_scalar_limit,
        )
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
            incumbent_observation = (
                current
                if isinstance(current, ShadowBoundaryObservation)
                and payload.accepted_foam_component_mask is not None
                else None
            )
            if (
                isinstance(current, ShadowAmbiguousObservation)
                or incumbent_observation is not None
            ):
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
                    incumbent_observation=incumbent_observation,
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
        return self.__validator._phase_a(frame)

    def _validate_evidence_graph(self, frame: SuccessfulPipelineFrame) -> None:
        self.__validator._validate_evidence_graph(frame)

    def _validate_raw_observation_shape(self, item: RawEdgeObservation) -> None:
        self.__validator._validate_raw_observation_shape(item)

    def _validate_hypothesis_summaries(
        self,
        hypothesis: SemanticHypothesis,
        proposals: tuple[BoundedYProposal, ...],
    ) -> None:
        self.__validator._validate_hypothesis_summaries(hypothesis, proposals)

    def _canonical_current(
        self,
        current: ShadowCurrentObservation,
        hypotheses: tuple[SemanticHypothesis, ...],
    ) -> ShadowCurrentObservation:
        return self.__validator._canonical_current(current, hypotheses)

    def _validate_decision(
        self,
        current: ShadowCurrentObservation,
        hypotheses: tuple[SemanticHypothesis, ...],
        decision,
    ) -> None:
        self.__validator._validate_decision(current, hypotheses, decision)

    def _validate_reduction(
        self,
        frame: SuccessfulPipelineFrame,
        prior_record: GlassTemporalRecord,
        reduction: CanonicalTemporalReduction,
    ) -> None:
        self.__validator._validate_reduction(frame, prior_record, reduction)

    def _validate_next_record(
        self,
        prior_record: GlassTemporalRecord,
        record: GlassTemporalRecord,
        resources: TemporalResourceMetrics,
    ) -> None:
        self.__validator._validate_next_record(prior_record, record, resources)

    def _validate_record_value(
        self,
        record: GlassTemporalRecord,
    ) -> TemporalResourceMetrics:
        return self.__validator._validate_record_value(record)

    def _expected_resource_summary(
        self,
        frame: SuccessfulPipelineFrame,
        temporal: TemporalResourceMetrics,
    ) -> ShadowResourceSummary:
        return self.__validator._expected_resource_summary(frame, temporal)

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
        self.__validator._validate_prepared_run_store(
            prior, prepared, glass_id, next_record
        )

    def _validate_prepared_reset_store(
        self,
        prior: TemporalStoreState,
        prepared: TemporalStoreState,
        glass_id: str | None,
    ) -> None:
        self.__validator._validate_prepared_reset_store(prior, prepared, glass_id)

    def _validate_store_shape(self, store: TemporalStoreState) -> None:
        self.__validator._validate_store_shape(store)

    def _validate_transition_coherence(
        self,
        prior_record: GlassTemporalRecord,
        decision,
        state: GlassTemporalState,
    ) -> None:
        self.__validator._validate_transition_coherence(prior_record, decision, state)

    def _expected_pending_motion(
        self,
        prior: GlassTemporalState,
        y: float,
    ) -> tuple[float | None, int]:
        return self.__validator._expected_pending_motion(prior, y)

    def _validate_prepared_outcome(
        self,
        outcome: OilCanonicalOutcome,
        frame: SuccessfulPipelineFrame,
        reduction: CanonicalTemporalReduction,
    ) -> None:
        self.__validator._validate_prepared_outcome(outcome, frame, reduction)

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




def _failure_reason(exc: Exception) -> str:
    return f"{type(exc).__name__}:{str(exc)[:120]}"
