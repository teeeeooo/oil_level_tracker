from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum
import json
import math
from statistics import median
from typing import Any, Callable

import numpy as np

from .oil_shadow_observations import (
    build_bounded_proposals,
    evaluate_semantic_hypotheses,
    evaluate_typed_current_observation,
    extract_raw_observations,
)
from .oil_shadow_temporal import (
    GlassTemporalSnapshot,
    GlassTemporalState,
    OilShadowTemporalModel,
    ProvisionalTemporalResult,
    TemporalAuditSnapshot,
    _OilTemporalAuthority,
    _TemporalTransactionSession,
)
from .oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
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
    ShadowHypothesisLabel,
    ShadowNoInterfaceObservation,
    ShadowResourceSummary,
    ShadowSourceFamily,
    ShadowUnavailableObservation,
    SuccessfulPipelineFrame,
    TemporalResourceMetrics,
    stable_digest,
)
from .preprocessing import PreprocessResult


OutcomePreparer = Callable[
    [SuccessfulPipelineFrame, ProvisionalTemporalResult, ShadowResourceSummary],
    OilCanonicalOutcome,
]


class OilHypothesisPipeline:
    """Sole S5-B production evidence, validation, prepare and commit owner."""

    def __init__(
        self,
        bounds: OilShadowBounds | None = None,
        *,
        temporal_evaluator: Callable[[GlassTemporalSnapshot, ShadowCurrentObservation], ProvisionalTemporalResult] | None = None,
        outcome_preparer: OutcomePreparer | None = None,
        commit_hook: Callable[[GlassTemporalSnapshot, GlassTemporalState], None] | None = None,
        handoff_hook: Callable[[str], None] | None = None,
        transaction_admitted_hook: Callable[[str], None] | None = None,
        global_reset_waiting_hook: Callable[[], None] | None = None,
    ) -> None:
        self.bounds = bounds or OilShadowBounds()
        self._temporal_model = OilShadowTemporalModel(self.bounds)
        self.__temporal_authority = _OilTemporalAuthority(
            self._temporal_model,
            evaluator=temporal_evaluator,
            commit_hook=commit_hook,
            handoff_hook=handoff_hook,
            transaction_admitted_hook=transaction_admitted_hook,
            global_reset_waiting_hook=global_reset_waiting_hook,
        )
        self._outcome_preparer = outcome_preparer or self._prepare_outcome

    @property
    def temporal_state_count(self) -> int:
        return self.__temporal_authority.state_count

    def temporal_snapshot(self, glass_id: str) -> TemporalAuditSnapshot:
        """Return an immutable read-only audit projection, never commit authority."""
        return self.__temporal_authority.audit_snapshot(glass_id)

    def reset(self, glass_id: str | None = None) -> None:
        self.__temporal_authority.reset(glass_id)

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
    ) -> OilCanonicalOutcome:
        key = str(glass_id)
        return self.__temporal_authority.execute(
            key,
            lambda session: self._run_transaction(
                session=session,
                glass_id=key,
                pre=pre,
                effective_mask=effective_mask,
                ellipse_mask=ellipse_mask,
                exclusion_mask=exclusion_mask,
                static_artifact_map=static_artifact_map,
                crop_origin_y=crop_origin_y,
            ),
        )

    def _run_transaction(
        self,
        *,
        session: _TemporalTransactionSession,
        glass_id: str,
        pre: PreprocessResult,
        effective_mask: np.ndarray,
        ellipse_mask: np.ndarray,
        exclusion_mask: np.ndarray,
        static_artifact_map: np.ndarray | None,
        crop_origin_y: float,
    ) -> OilCanonicalOutcome:
        try:
            raw = extract_raw_observations(
                pre,
                effective_mask,
                crop_origin_y=crop_origin_y,
                bounds=self.bounds,
            )
            proposals = build_bounded_proposals(raw, self.bounds)
            hypotheses = evaluate_semantic_hypotheses(
                proposals,
                raw,
                pre,
                effective_mask,
                ellipse_mask,
                exclusion_mask,
                static_artifact_map,
                crop_origin_y=crop_origin_y,
                bounds=self.bounds,
            )
            current = evaluate_typed_current_observation(pre, effective_mask, hypotheses)
            raw_frame = SuccessfulPipelineFrame(
                raw_observations=raw,
                proposals=proposals,
                hypotheses=hypotheses,
                current_observation=current,
                frame_height=int(pre.gray.shape[0]),
                frame_width=int(pre.gray.shape[1]),
            )
        except Exception as exc:
            return self.failure_outcome(
                _failure_reason(exc),
                PipelineFailureStage.EVIDENCE_CONSTRUCTION,
            )

        try:
            canonical = self._phase_a(raw_frame)
        except Exception as exc:
            return self.failure_outcome(_failure_reason(exc), PipelineFailureStage.PHASE_A)

        snapshot = session.snapshot
        try:
            provisional = session.evaluate(canonical.current_observation)
        except Exception as exc:
            return self.failure_outcome(
                _failure_reason(exc),
                PipelineFailureStage.TEMPORAL_EVALUATION,
            )

        try:
            resource_summary = self._phase_b(
                glass_id, canonical, snapshot, provisional
            )
        except Exception as exc:
            return self.failure_outcome(_failure_reason(exc), PipelineFailureStage.PHASE_B)

        try:
            prepared = self._outcome_preparer(canonical, provisional, resource_summary)
            prepared = self._finalize_debug_resources(prepared)
            self._validate_prepared_outcome(prepared, canonical, provisional)
            commit_token = self._commit_token(glass_id, snapshot, prepared)
        except Exception as exc:
            return self.failure_outcome(
                _failure_reason(exc),
                PipelineFailureStage.OUTCOME_PREPARATION,
            )

        try:
            session.commit(provisional.next_state, commit_token)
        except Exception as exc:
            return self.failure_outcome(_failure_reason(exc), PipelineFailureStage.COMMIT)
        return prepared

    def failure_outcome(
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

    def _phase_b(
        self,
        glass_id: str,
        frame: SuccessfulPipelineFrame,
        snapshot: GlassTemporalSnapshot,
        provisional: ProvisionalTemporalResult,
    ) -> ShadowResourceSummary:
        if type(snapshot) is not GlassTemporalSnapshot:
            raise TypeError("Unsupported temporal snapshot variant.")
        if snapshot.glass_id != glass_id:
            raise ValueError("Temporal snapshot targets the wrong Glass.")
        if type(provisional) is not ProvisionalTemporalResult:
            raise TypeError("Unsupported provisional temporal result.")
        decision = _canonical_dataclass(provisional.decision)
        if decision != provisional.decision:
            raise ValueError("Provisional decision canonicalization changed content.")
        state = provisional.next_state
        self._validate_next_state(snapshot, state, provisional.resources)
        self._validate_decision(frame.current_observation, frame.hypotheses, decision)
        if decision.resources != provisional.resources:
            raise ValueError("Decision and provisional resources disagree.")
        return self._resource_summary(frame, provisional.resources)

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

    def _validate_next_state(
        self,
        snapshot: GlassTemporalSnapshot,
        state: GlassTemporalState,
        resources: TemporalResourceMetrics,
    ) -> None:
        if type(state) is not GlassTemporalState:
            raise TypeError("Unsupported proposed state variant.")
        _exact_dataclass_fields(state)
        replace(state)
        if state.glass_id != snapshot.glass_id:
            raise ValueError("Proposed state targets the wrong Glass.")
        if state.version != snapshot.version + 1:
            raise ValueError("Proposed state version is invalid.")
        if state.last_commit_token is not None:
            raise ValueError("Uncommitted proposed state cannot carry a commit token.")
        if len(state.beam) > self.bounds.temporal_beam_width:
            raise ValueError("Proposed beam bound exceeded.")
        if max((len(item.history) for item in state.beam), default=0) > self.bounds.temporal_history_window:
            raise ValueError("Proposed history bound exceeded.")
        if state.pending_count >= self.bounds.reacquisition_frames:
            raise ValueError("Committed pending reacquisition counter is not bounded.")
        if state.no_interface_count > self.bounds.no_interface_clear_frames:
            raise ValueError("No-interface counter bound exceeded.")
        if state.unavailable_count > self.bounds.unavailable_clear_frames:
            raise ValueError("Unavailable counter bound exceeded.")
        for item in state.beam:
            if type(item).__name__ != "_BeamItem" or type(item).__module__ != __package__ + ".oil_shadow_temporal":
                raise TypeError("Unsupported temporal beam item.")
            _exact_dataclass_fields(item)
            if len(item.history) > self.bounds.temporal_history_window:
                raise ValueError("Temporal beam history bound exceeded.")
            _json_safe(item.history)
            for scalar in (
                item.source_y,
                item.observation_score,
                item.cumulative_score,
                item.transition_cost,
                item.velocity,
            ):
                if scalar is not None and not math.isfinite(float(scalar)):
                    raise ValueError("Temporal beam scalar must be finite.")
        expected = TemporalResourceMetrics(
            beam_count=len(state.beam),
            history_length=max((len(item.history) for item in state.beam), default=0),
            retained_scalar_count=sum(
                len(item.history) * 4 + 7 for item in state.beam
            ) + 12,
            reacquisition_count=state.pending_count,
        )
        if resources != expected:
            raise ValueError("Proposed resource summary disagrees with state.")
        if resources.retained_scalar_count > self._temporal_model.retained_scalar_limit:
            raise ValueError("Proposed retained temporal scalar bound exceeded.")

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
            retained_temporal_scalar_limit=self._temporal_model.retained_scalar_limit,
            static_prior_scalar_count=2,
            static_prior_scalar_limit=self.bounds.static_prior_scalars_per_glass,
            debug_scalar_count=0,
            debug_scalar_limit=self.bounds.maximum_debug_scalar_count,
        )

    def _prepare_outcome(
        self,
        frame: SuccessfulPipelineFrame,
        provisional: ProvisionalTemporalResult,
        resources: ShadowResourceSummary,
    ) -> OilCanonicalOutcome:
        decision = provisional.decision
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

    def _validate_prepared_outcome(
        self,
        outcome: OilCanonicalOutcome,
        frame: SuccessfulPipelineFrame,
        provisional: ProvisionalTemporalResult,
    ) -> None:
        if type(outcome) not in {
            AcceptedBoundaryOutcome,
            NoInterfaceOutcome,
            AmbiguousOutcome,
            EvidenceUnavailableOutcome,
            ReacquisitionPendingOutcome,
        }:
            raise TypeError("Successful transaction prepared an unsupported outcome.")
        _exact_dataclass_fields(outcome)
        canonical = _canonical_dataclass(outcome)
        if canonical != outcome:
            raise ValueError("Prepared outcome canonicalization changed content.")
        if outcome.hypotheses != frame.hypotheses:
            raise ValueError("Prepared outcome evidence differs from Phase A.")
        if outcome.resources.debug_scalar_count > self.bounds.maximum_debug_scalar_count:
            raise ValueError("Prepared outcome debug resource bound exceeded.")
        if outcome.tracker_action != provisional.decision.tracker_action:
            raise ValueError("Prepared outcome tracker action disagrees with decision.")
        if outcome.smoothing_action != provisional.decision.smoothing_action:
            raise ValueError("Prepared outcome smoothing action disagrees with decision.")
        _json_safe(oil_runtime_metrics(outcome))
        _json_safe(oil_debug_detail(outcome))

    @staticmethod
    def _commit_token(
        glass_id: str,
        snapshot: GlassTemporalSnapshot,
        outcome: OilCanonicalOutcome,
    ) -> str:
        selected = None
        if isinstance(outcome, AcceptedBoundaryOutcome):
            selected = outcome.selected_hypothesis.identity
        elif isinstance(outcome, ReacquisitionPendingOutcome):
            selected = outcome.pending_hypothesis.identity
        return stable_digest(
            "oil-temporal-commit",
            (
                ("glass_id", glass_id),
                ("prior_version", snapshot.version),
                ("outcome", type(outcome).__name__),
                ("selected", selected),
                ("reason", outcome.reason),
            ),
        )


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
