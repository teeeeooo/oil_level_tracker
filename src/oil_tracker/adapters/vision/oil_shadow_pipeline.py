from __future__ import annotations

from dataclasses import replace
import math
from typing import Any

import numpy as np

from .oil_shadow_observations import (
    build_bounded_proposals,
    evaluate_semantic_hypotheses,
    evaluate_typed_current_observation,
    extract_raw_observations,
)
from .oil_shadow_temporal import OilShadowTemporalTracker
from .oil_shadow_types import (
    OilShadowBounds,
    OilShadowFrameResult,
    SemanticHypothesis,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowResourceSummary,
    ShadowUnavailableObservation,
)
from .preprocessing import PreprocessResult


class OilHypothesisPipeline:
    """Official S5-B typed hypothesis pipeline with bounded scalar retained state."""

    def __init__(self, bounds: OilShadowBounds | None = None) -> None:
        self.bounds = bounds or OilShadowBounds()
        self.temporal = OilShadowTemporalTracker(self.bounds)

    @property
    def temporal_state_count(self) -> int:
        return self.temporal.state_count

    def reset(self, glass_id: str | None = None) -> None:
        self.temporal.reset(glass_id)

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
    ) -> OilShadowFrameResult:
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
        current = evaluate_typed_current_observation(
            pre,
            effective_mask,
            hypotheses,
        )
        temporal = self.temporal.evaluate(glass_id, current)
        resources = self._resource_summary(
            glass_id,
            raw_count=len(raw),
            proposals=proposals,
            hypotheses=hypotheses,
            debug_scalar_count=0,
            frame_height=pre.gray.shape[0],
        )
        preliminary = OilShadowFrameResult(
            available=True,
            failure_reason=None,
            raw_observations=raw,
            proposals=proposals,
            hypotheses=hypotheses,
            current_observation=current,
            temporal_decision=temporal,
            resources=resources,
        )
        debug_count = _scalar_leaf_count(
            oil_runtime_metrics(preliminary)
        ) + _scalar_leaf_count(oil_debug_detail(preliminary))
        if debug_count > self.bounds.maximum_debug_scalar_count:
            raise RuntimeError(
                "Oil hypothesis debug scalar contract exceeded its configured bound."
            )
        return replace(
            preliminary,
            resources=replace(resources, debug_scalar_count=debug_count),
        )

    def failure_result(
        self,
        *,
        glass_id: str,
        reason: str,
    ) -> OilShadowFrameResult:
        normalized_reason = str(reason)[:160] or "oil_hypothesis_execution_failed"
        current = ShadowUnavailableObservation(
            ShadowObservationKind.UNAVAILABLE,
            0.0,
            normalized_reason,
        )
        temporal = self.temporal.evaluate(glass_id, current)
        resources = self._resource_summary(
            glass_id,
            raw_count=0,
            proposals=(),
            hypotheses=(),
            debug_scalar_count=0,
            broad_scale_count=0,
            narrow_scale_count=0,
            frame_height=0,
        )
        preliminary = OilShadowFrameResult(
            available=False,
            failure_reason=normalized_reason,
            raw_observations=(),
            proposals=(),
            hypotheses=(),
            current_observation=current,
            temporal_decision=temporal,
            resources=resources,
        )
        debug_count = _scalar_leaf_count(
            oil_runtime_metrics(preliminary)
        ) + _scalar_leaf_count(oil_debug_detail(preliminary))
        return replace(
            preliminary,
            resources=replace(
                resources,
                debug_scalar_count=min(
                    debug_count,
                    self.bounds.maximum_debug_scalar_count,
                ),
            ),
        )

    def _resource_summary(
        self,
        glass_id: str,
        *,
        raw_count: int,
        proposals,
        hypotheses,
        debug_scalar_count: int,
        broad_scale_count: int | None = None,
        narrow_scale_count: int | None = None,
        frame_height: int,
    ) -> ShadowResourceSummary:
        beam_count, history_length, retained_scalars, static_scalars = (
            self.temporal.state_resource_counts(glass_id)
        )
        maximum_diameter = max(
            (item.diameter_px for item in proposals),
            default=0.0,
        )
        maximum_members = max(
            (item.member_count for item in proposals),
            default=0,
        )
        retained_members = sum(item.member_count for item in proposals)
        return ShadowResourceSummary(
            raw_observation_count=raw_count,
            raw_observation_limit=self.bounds.total_raw_observations,
            broad_scale_count=(
                len(self.bounds.broad_band_scales)
                if broad_scale_count is None
                else broad_scale_count
            ),
            broad_scale_limit=len(self.bounds.broad_band_scales),
            narrow_scale_count=(
                len(self.bounds.narrow_scales)
                if narrow_scale_count is None
                else narrow_scale_count
            ),
            narrow_scale_limit=len(self.bounds.narrow_scales),
            narrow_examined_rows_per_hypothesis=min(
                max(0, int(frame_height)),
                2 * self.bounds.narrow_lobe_search_radius_px + 1,
            ),
            narrow_examined_rows_per_hypothesis_limit=(
                2 * self.bounds.narrow_lobe_search_radius_px + 1
            ),
            proposal_count=len(proposals),
            proposal_limit=self.bounds.total_proposals,
            maximum_proposal_diameter_px=maximum_diameter,
            proposal_diameter_limit_px=self.bounds.maximum_proposal_diameter_px,
            maximum_members_per_proposal=maximum_members,
            members_per_proposal_limit=self.bounds.members_per_proposal,
            retained_member_count=retained_members,
            retained_member_limit=self.bounds.total_retained_members,
            semantic_hypothesis_count=len(hypotheses),
            semantic_hypothesis_limit=self.bounds.semantic_hypotheses,
            temporal_beam_count=beam_count,
            temporal_beam_limit=self.bounds.temporal_beam_width,
            temporal_history_length=history_length,
            temporal_history_limit=self.bounds.temporal_history_window,
            retained_temporal_scalar_count=retained_scalars,
            retained_temporal_scalar_limit=self.temporal.retained_scalar_limit,
            static_prior_scalar_count=static_scalars,
            static_prior_scalar_limit=self.bounds.static_prior_scalars_per_glass,
            debug_scalar_count=debug_scalar_count,
            debug_scalar_limit=self.bounds.maximum_debug_scalar_count,
        )


# Historical import compatibility; production code uses OilHypothesisPipeline.
OilShadowPipeline = OilHypothesisPipeline


def oil_runtime_metrics(result: OilShadowFrameResult) -> dict[str, Any]:
    likelihoods = _current_likelihoods(result)
    temporal = result.temporal_decision
    resources = result.resources
    no_interface = _current_no_interface(result)
    return {
        "oil_pipeline_available": bool(result.available),
        "oil_pipeline_failure_reason": result.failure_reason,
        "oil_decision_status": temporal.status.value,
        "oil_decision_reason": temporal.reason,
        "oil_selected_hypothesis_id": temporal.selected_hypothesis_id,
        "oil_temporal_projected_source_y": temporal.projected_source_y,
        "oil_boundary_score": likelihoods["boundary"],
        "oil_artifact_score": likelihoods["artifact"],
        "oil_ambiguity_score": likelihoods["ambiguity"],
        "oil_no_interface_score": likelihoods["no_interface"],
        "oil_decision_confidence": temporal.confidence,
        "oil_decision_margin": temporal.decision_margin,
        "oil_tracker_update_accepted": (
            temporal.status.value == "boundary_accepted"
        ),
        "oil_clear_smoothing": temporal.clear_smoothing,
        "oil_reacquisition_count": temporal.reacquisition_count,
        "oil_hypothesis_raw_observation_count": resources.raw_observation_count,
        "oil_hypothesis_raw_observation_limit": resources.raw_observation_limit,
        "oil_hypothesis_broad_scale_count": resources.broad_scale_count,
        "oil_hypothesis_broad_scale_limit": resources.broad_scale_limit,
        "oil_hypothesis_narrow_scale_count": resources.narrow_scale_count,
        "oil_hypothesis_narrow_scale_limit": resources.narrow_scale_limit,
        "oil_hypothesis_narrow_examined_rows_per_hypothesis": (
            resources.narrow_examined_rows_per_hypothesis
        ),
        "oil_hypothesis_narrow_examined_rows_per_hypothesis_limit": (
            resources.narrow_examined_rows_per_hypothesis_limit
        ),
        "oil_hypothesis_proposal_count": resources.proposal_count,
        "oil_hypothesis_proposal_limit": resources.proposal_limit,
        "oil_hypothesis_maximum_proposal_diameter_px": (
            resources.maximum_proposal_diameter_px
        ),
        "oil_hypothesis_proposal_diameter_limit_px": (
            resources.proposal_diameter_limit_px
        ),
        "oil_hypothesis_maximum_members_per_proposal": (
            resources.maximum_members_per_proposal
        ),
        "oil_hypothesis_members_per_proposal_limit": (
            resources.members_per_proposal_limit
        ),
        "oil_hypothesis_retained_member_count": resources.retained_member_count,
        "oil_hypothesis_retained_member_limit": resources.retained_member_limit,
        "oil_hypothesis_count": resources.semantic_hypothesis_count,
        "oil_hypothesis_limit": resources.semantic_hypothesis_limit,
        "oil_hypothesis_temporal_beam_count": resources.temporal_beam_count,
        "oil_hypothesis_temporal_beam_limit": resources.temporal_beam_limit,
        "oil_hypothesis_temporal_history_length": resources.temporal_history_length,
        "oil_hypothesis_temporal_history_limit": resources.temporal_history_limit,
        "oil_hypothesis_retained_temporal_scalar_count": (
            resources.retained_temporal_scalar_count
        ),
        "oil_hypothesis_retained_temporal_scalar_limit": (
            resources.retained_temporal_scalar_limit
        ),
        "oil_hypothesis_static_prior_scalar_count": resources.static_prior_scalar_count,
        "oil_hypothesis_static_prior_scalar_limit": resources.static_prior_scalar_limit,
        "oil_hypothesis_debug_scalar_count": resources.debug_scalar_count,
        "oil_hypothesis_debug_scalar_limit": resources.debug_scalar_limit,
        "oil_hypothesis_current_observation": result.current_observation.kind.value,
        "oil_no_interface_uniformity": (
            0.0 if no_interface is None else no_interface.region_uniformity
        ),
        "oil_no_interface_weak_boundary": (
            0.0 if no_interface is None else no_interface.weak_boundary_evidence
        ),
        "oil_no_interface_visibility": (
            0.0 if no_interface is None else no_interface.visibility
        ),
        "oil_no_interface_glare_conflict": (
            0.0 if no_interface is None else no_interface.glare_conflict
        ),
        "oil_no_interface_full_likelihood": (
            0.0 if no_interface is None else no_interface.full_likelihood
        ),
        "oil_no_interface_empty_likelihood": (
            0.0 if no_interface is None else no_interface.empty_likelihood
        ),
        "oil_no_interface_reason": (
            "not_available" if no_interface is None else no_interface.reason
        ),
    }


def oil_debug_detail(result: OilShadowFrameResult) -> dict[str, Any]:
    selected = _selected_hypothesis(result)
    return {
        "available": result.available,
        "failure_reason": result.failure_reason,
        "current_observation": result.current_observation.kind.value,
        "temporal_status": result.temporal_decision.status.value,
        "temporal_reason": result.temporal_decision.reason,
        "selected_hypothesis_id": result.temporal_decision.selected_hypothesis_id,
        "projected_source_y": result.temporal_decision.projected_source_y,
        "decision_confidence": result.temporal_decision.confidence,
        "decision_margin": result.temporal_decision.decision_margin,
        "resource_counts": {
            "raw_observations": result.resources.raw_observation_count,
            "proposals": result.resources.proposal_count,
            "retained_members": result.resources.retained_member_count,
            "hypotheses": result.resources.semantic_hypothesis_count,
            "temporal_beam": result.resources.temporal_beam_count,
            "temporal_history": result.resources.temporal_history_length,
            "retained_temporal_scalars": result.resources.retained_temporal_scalar_count,
        },
        "selected_evidence": None
        if selected is None
        else _hypothesis_detail(selected),
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


def _current_no_interface(result: OilShadowFrameResult):
    current = result.current_observation
    if isinstance(current, ShadowBoundaryObservation):
        return current.no_interface
    if isinstance(current, ShadowNoInterfaceObservation):
        return current.evidence
    return None


def _current_likelihoods(result: OilShadowFrameResult) -> dict[str, float]:
    current = result.current_observation
    if isinstance(current, ShadowBoundaryObservation):
        return {
            "boundary": current.hypothesis.boundary_likelihood,
            "artifact": current.hypothesis.artifact_likelihood,
            "ambiguity": current.hypothesis.ambiguity_likelihood,
            "no_interface": current.no_interface.likelihood,
        }
    if isinstance(current, ShadowNoInterfaceObservation):
        return {
            "boundary": current.evidence.competing_boundary_likelihood,
            "artifact": 0.0,
            "ambiguity": 0.0,
            "no_interface": current.evidence.likelihood,
        }
    if isinstance(current, ShadowAmbiguousObservation):
        return {
            "boundary": current.boundary_likelihood,
            "artifact": current.artifact_likelihood,
            "ambiguity": current.ambiguity_likelihood,
            "no_interface": current.no_interface_likelihood,
        }
    return {
        "boundary": 0.0,
        "artifact": 0.0,
        "ambiguity": 1.0,
        "no_interface": 0.0,
    }


def _selected_hypothesis(
    result: OilShadowFrameResult,
) -> SemanticHypothesis | None:
    selected_id = result.temporal_decision.selected_hypothesis_id
    if selected_id is None:
        return None
    return next(
        (item for item in result.hypotheses if item.identity == selected_id),
        None,
    )


def _scalar_leaf_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_scalar_leaf_count(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return sum(_scalar_leaf_count(item) for item in value)
    return 1
