from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum
import json
import math
from statistics import median

from .oil_pipeline_diagnostics import (
    oil_debug_detail,
    oil_runtime_metrics,
    scalar_leaf_count as _scalar_leaf_count,
)
from .oil_shadow_temporal import (
    CanonicalTemporalReduction,
    GlassTemporalRecord,
    GlassTemporalState,
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


@dataclass(frozen=True)
class OilPipelineValidator:
    """Stateless canonical and temporal-invariant validation collaborator."""

    bounds: OilShadowBounds
    retained_scalar_limit: int

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
        if resources.retained_scalar_count > self.retained_scalar_limit:
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
        if metrics.retained_scalar_count > self.retained_scalar_limit:
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
            retained_temporal_scalar_limit=self.retained_scalar_limit,
            static_prior_scalar_count=2,
            static_prior_scalar_limit=self.bounds.static_prior_scalars_per_glass,
            debug_scalar_count=0,
            debug_scalar_limit=self.bounds.maximum_debug_scalar_count,
        )

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
    tolerance = _boundary_motion_envelope(bounds)
    prediction = state.pending_y + (state.pending_velocity or 0.0)
    return (
        abs(source_y - state.pending_y) <= tolerance
        or abs(source_y - prediction) <= tolerance
    )


def _boundary_motion_envelope(bounds: OilShadowBounds) -> float:
    """Use one bounded per-observation motion envelope for Oil continuity."""

    return bounds.maximum_proposal_diameter_px * 4.0


def _same(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9)


def _same_optional(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right
    return _same(left, right)
