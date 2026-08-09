from __future__ import annotations

from typing import Any

from .oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousOutcome,
    EvidenceUnavailableOutcome,
    NoInterfaceOutcome,
    OilCanonicalOutcome,
    PipelineFailureOutcome,
    ReacquisitionPendingOutcome,
    SemanticHypothesis,
)


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


def scalar_leaf_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(scalar_leaf_count(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return sum(scalar_leaf_count(item) for item in value)
    return 1


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
