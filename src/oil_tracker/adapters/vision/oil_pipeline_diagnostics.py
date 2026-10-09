from __future__ import annotations

from dataclasses import dataclass
import json
import math
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


# A1 uses a separate frame-local sidecar: none of these values enter outcomes,
# candidate features, temporal state or OilCandidateEvidenceIndex.
MEASUREMENT_LINEAGE_SCHEMA = "oil-measurement-lineage-v1"
SCORE_DEPENDENCIES = {
    "narrow_boundary": ("narrow.peak_strength", "narrow.horizontal_coverage", "narrow.scale_persistence"),
    "pulse_artifact": ("narrow.paired_edge_strength", "narrow.pulse_symmetry", "narrow.border_overlap", "narrow.exclusion_overlap", "narrow.glare_overlap"),
    "boundary": ("broad.strength", "narrow_boundary", "polarity_confidence", "visibility", "pulse_artifact", "static_prior.contribution"),
    "structural_artifact": ("pulse_artifact", "narrow.static_overlap", "broad.scale_consistency", "broad.polarity_consistency"),
    "plateau_collision_artifact": ("bright_plateau_artifact", "pulse_artifact", "narrow.scale_persistence", "narrow.horizontal_coverage", "broad.glare_conflict", "narrow.border_overlap"),
    "artifact": ("structural_artifact", "broad.strength", "static_prior.contribution", "plateau_collision_artifact"),
    "ambiguity": ("boundary", "artifact", "polarity_confidence", "visibility", "availability"),
}


@dataclass(frozen=True)
class OilMeasurementLineage:
    """Immutable JSON payload bound to one pre-sort candidate, with no rasters."""
    candidate_input_index: int
    source: str
    source_y: float
    record_json: str


def capture_measurement_lineage(candidates, *, pre, bundle, static_map, measurement_exclusion=None):
    """Reproduce pure spatial measurements using their existing production owners.

    This deliberately never runs a temporal owner or resolver. Exact hypothesis
    ID, source Y and all three semantic scores must match before a reproduced
    record is attached. Spatial fallback uses its own existing owner and is
    attempted only for unmatched semantic IDs. Missing matches remain explicit.
    """
    from oil_tracker.domain.enums import BoundaryKind
    from . import oil_shadow_observations as observations
    from .oil_shadow_types import OilShadowBounds
    from .oil_supplemental_path import phase_transition_support

    bounds = OilShadowBounds()
    sink = {}
    expected = [c for c in candidates if c.kind is BoundaryKind.OIL_AIR and c.source.startswith("oil_hypothesis:")]
    if expected and pre.gray.ndim == 2 and all(pre.gray.shape):
        raw = observations.extract_raw_observations(pre, bundle.effective_mask,
            crop_origin_y=bundle.crop_origin[1], bounds=bounds)
        proposals = observations.build_bounded_proposals(raw, bounds)
        hypotheses = observations.evaluate_semantic_hypotheses(proposals, raw, pre,
            bundle.effective_mask, bundle.ellipse_mask, bundle.exclusion_mask, static_map,
            crop_origin_y=bundle.crop_origin[1], bounds=bounds, diagnostic_sink=sink)
        retained = {h.identity: (h, sink[h.identity], "canonical_absolute_broad") for h in hypotheses}
        if any(c.source.removeprefix("oil_hypothesis:") not in retained for c in expected):
            from .oil_spatial_fallback import _relative_region_observations, _relative_hypotheses
            relative_raw = _relative_region_observations(pre, bundle.effective_mask, raw,
                crop_origin_y=bundle.crop_origin[1], bounds=bounds)
            relative_proposals = observations.build_bounded_proposals(relative_raw, bounds)
            relative_sink = {}
            relative = _relative_hypotheses(relative_proposals, relative_raw, pre,
                bundle.effective_mask, bundle.ellipse_mask, bundle.exclusion_mask, static_map,
                crop_origin_y=bundle.crop_origin[1], bounds=bounds, diagnostic_sink=relative_sink)
            for h in relative:
                retained.setdefault(h.identity, (h, relative_sink[h.identity], "spatial_relative_broad"))
    else:
        retained = {}
    result = []
    for index, candidate in enumerate(candidates):
        if candidate.kind is not BoundaryKind.OIL_AIR or not math.isfinite(float(candidate.y)):
            continue
        record = {
            "status": "unavailable", "reason": "different_candidate_family",
            "candidate_scalar_source_y": float(candidate.y),
            "candidate_feature_score": float(candidate.feature_score),
            "candidate_final_score": float(candidate.final_score),
            "phase_support": (), "hypothesis": None,
        }
        if candidate.source.startswith("oil_hypothesis:"):
            found = retained.get(candidate.source.removeprefix("oil_hypothesis:"))
            if found is not None:
                hypothesis, detail, channel = found
                matches = float(candidate.y) == hypothesis.representative_source_y and all(
                    candidate.features.get(key) == getattr(hypothesis, key)
                    for key in ("boundary_likelihood", "artifact_likelihood", "ambiguity_likelihood"))
                if matches:
                    record.update(status="measured", reason="exact_id_y_score_reproduction",
                        hypothesis=detail, broad_channel=channel,
                        projection_score_rule="temporal_confidence_when_selected_else_boundary_likelihood")
                else:
                    record["reason"] = "hypothesis_source_y_or_score_mismatch"
            else:
                record["reason"] = "hypothesis_not_reproduced"
        elif candidate.source == "phase_transition_scan":
            local_y = float(candidate.y) - bundle.crop_origin[1]
            if local_y.is_integer() and 0 <= local_y < pre.gray.shape[0]:
                support = phase_transition_support(pre.normalized,
                    (bundle.effective_mask > 0) & ~(pre.glare_mask > 0),
                    local_y=int(local_y), crop_origin=bundle.crop_origin,
                    measurement_exclusion=measurement_exclusion)
                record.update(status="measured", reason="production_phase_scan_bands",
                    phase_support=support, phase_channel="normalized_float32",
                    phase_response_rule="max_radius(clipped_median(abs(pooled_delta)/48)); at_least_three_sectors",
                    phase_coverage_rule="available_pooled_sectors_over_five_at_strongest_radius",
                    phase_consistency_rule="fraction_radius_response_ge_max(0.08,strongest*0.60)")
                if measurement_exclusion is not None:
                    record["phase_pooling_rule"] = "legacy_unaffected_else_complete_common_x"
                    record["phase_support_counts_basis"] = "original_visibility; sampling contains actual used counts"
        result.append(OilMeasurementLineage(index, candidate.source, float(candidate.y),
            json.dumps(record, sort_keys=True, allow_nan=False)))
    return tuple(result)


def project_measurement_lineage(bindings, candidates, *, frame_index, glass_id, crop_origin):
    """Validate exact joins after calibration, preserving duplicate index identity."""
    from oil_tracker.domain.enums import BoundaryKind
    rows = []
    seen = set()
    for binding in bindings:
        index = binding.candidate_input_index
        if type(index) is not int or not 0 <= index < len(candidates) or index in seen:
            raise ValueError("Measurement lineage requires unique integral candidate indices.")
        seen.add(index)
        candidate = candidates[index]
        if candidate.kind is not BoundaryKind.OIL_AIR or candidate.source != binding.source or float(candidate.y) != binding.source_y:
            raise ValueError("Measurement lineage source/Y binding mismatch.")
        rows.append({"candidate_input_index": index, "source": binding.source,
            "source_y": binding.source_y, "rejected_after_calibration": candidate.rejected,
            **json.loads(binding.record_json)})
    return {"schema_version": MEASUREMENT_LINEAGE_SCHEMA, "diagnostic_only": True,
        "source_frame_index": frame_index, "glass_id": glass_id, "crop_origin": crop_origin,
        "coordinate_space": "source_frame_y", "candidate_index_space": "detection.candidates_before_trace_score_sort",
        "decision": "NOT_EVALUATED", "score_dependencies": dict(SCORE_DEPENDENCIES),
        "candidates": rows}
