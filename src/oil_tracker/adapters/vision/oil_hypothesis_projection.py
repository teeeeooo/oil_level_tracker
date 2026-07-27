from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

from .oil_shadow_types import (
    OilShadowFrameResult,
    SemanticHypothesis,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceEvidence,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowTemporalStatus,
    ShadowUnavailableObservation,
)
from .preprocessing import PreprocessResult
from .row_features import masked_band_intensity_profiles, masked_row_mean, row_coverage


@dataclass(frozen=True)
class OilProductionProjection:
    selected_candidate: BoundaryCandidate | None
    candidates: tuple[BoundaryCandidate, ...]
    raw_source_y: float | None
    confidence: float
    tracker_update_accepted: bool
    clear_smoothing: bool
    no_interface_evidence: ShadowNoInterfaceEvidence | None
    flags: tuple[str, ...]


def validate_production_result(result: OilShadowFrameResult) -> None:
    decision = result.temporal_decision
    current = result.current_observation
    hypothesis_ids = [item.identity for item in result.hypotheses]
    if len(hypothesis_ids) != len(set(hypothesis_ids)):
        raise ValueError("typed oil result contains duplicate hypothesis identities")

    if decision.status is ShadowTemporalStatus.BOUNDARY_ACCEPTED:
        boundary = _validated_boundary_current(result, "accepted typed boundary")
        if decision.observation_kind is not ShadowObservationKind.BOUNDARY:
            raise ValueError("accepted typed boundary has the wrong observation kind")
        if decision.selected_hypothesis_id is None or decision.projected_source_y is None:
            raise ValueError("accepted typed boundary is missing identity or source Y")
        if decision.selected_hypothesis_id != boundary.identity:
            raise ValueError("accepted typed boundary identity disagrees with current evidence")
        _require_same_y(
            decision.projected_source_y,
            boundary.representative_source_y,
            "accepted typed boundary Y disagrees with current evidence",
        )
        return

    if decision.status is ShadowTemporalStatus.REACQUISITION_PENDING:
        boundary = _validated_boundary_current(result, "typed reacquisition")
        if decision.observation_kind is not ShadowObservationKind.BOUNDARY:
            raise ValueError("typed reacquisition decision has the wrong observation kind")
        if decision.selected_hypothesis_id is None or decision.projected_source_y is not None:
            raise ValueError("typed reacquisition must retain identity without numeric output")
        if decision.selected_hypothesis_id != boundary.identity:
            raise ValueError("typed reacquisition identity disagrees with current evidence")
        return

    if decision.status is ShadowTemporalStatus.NO_INTERFACE_ACCEPTED:
        if not isinstance(current, ShadowNoInterfaceObservation):
            raise ValueError("typed no-interface decision has the wrong current observation")
        if decision.observation_kind is not ShadowObservationKind.NO_INTERFACE:
            raise ValueError("typed no-interface decision has the wrong observation kind")
        if decision.selected_hypothesis_id is not None or decision.projected_source_y is not None:
            raise ValueError("typed no-interface decision cannot expose a boundary")
        return

    if decision.status is ShadowTemporalStatus.AMBIGUOUS:
        if not isinstance(current, ShadowAmbiguousObservation):
            raise ValueError("typed ambiguous decision has the wrong current observation")
        if decision.observation_kind is not ShadowObservationKind.AMBIGUOUS:
            raise ValueError("typed ambiguous decision has the wrong observation kind")
        if decision.selected_hypothesis_id is not None:
            raise ValueError("typed ambiguous decision cannot select a hypothesis")
        if not _same_optional_y(decision.projected_source_y, current.projected_source_y):
            raise ValueError("typed ambiguous projected Y disagrees with current evidence")
        return

    if decision.status is ShadowTemporalStatus.UNAVAILABLE:
        if not isinstance(current, ShadowUnavailableObservation):
            raise ValueError("typed unavailable decision has the wrong current observation")
        if decision.observation_kind is not ShadowObservationKind.UNAVAILABLE:
            raise ValueError("typed unavailable decision has the wrong observation kind")
        if decision.selected_hypothesis_id is not None or decision.projected_source_y is not None:
            raise ValueError("typed unavailable decision cannot expose a boundary")
        return

    raise ValueError(f"unsupported typed oil temporal status: {decision.status!r}")


def project_production_result(result: OilShadowFrameResult) -> OilProductionProjection:
    validate_production_result(result)
    decision = result.temporal_decision
    accepted = decision.status is ShadowTemporalStatus.BOUNDARY_ACCEPTED
    selected_id = decision.selected_hypothesis_id if accepted else None
    candidates = tuple(
        _candidate_from_hypothesis(item, result, selected_id)
        for item in sorted(
            result.hypotheses,
            key=lambda value: (value.representative_source_y, value.identity),
        )
    )
    selected = next((item for item in candidates if item.selected), None)
    raw_source_y = None if selected is None else float(selected.y)
    no_interface = (
        result.current_observation.evidence
        if isinstance(result.current_observation, ShadowNoInterfaceObservation)
        else None
    )
    return OilProductionProjection(
        selected_candidate=selected,
        candidates=candidates,
        raw_source_y=raw_source_y,
        confidence=float(decision.confidence),
        tracker_update_accepted=accepted,
        clear_smoothing=bool(decision.clear_smoothing),
        no_interface_evidence=no_interface,
        flags=_decision_flags(result),
    )


def build_hypothesis_debug_profiles(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ellipse_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    hypotheses: tuple[SemanticHypothesis, ...],
) -> dict[str, list[float]]:
    signed_sobel = masked_row_mean(pre.sobel_y_signed, effective_mask)
    signed_sobel = np.clip(-signed_sobel / 80.0, -1.0, 1.0)
    coverage = row_coverage(pre.horizontal_mask, effective_mask)
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    contrast = masked_band_intensity_profiles(
        pre.blurred,
        visible,
        band=5,
        reference_mask=effective,
        minimum_fraction=0.45,
        minimum_pixels=5,
        include_center_extra=True,
    ).signed_difference
    contrast = np.clip(contrast / 80.0, -1.0, 1.0)
    semantic_support = np.zeros(effective_mask.shape[0], dtype=np.float32)
    for item in hypotheses:
        row = int(round(item.representative_local_y))
        if 0 <= row < semantic_support.size:
            semantic_support[row] = max(
                semantic_support[row],
                float(item.boundary_likelihood),
            )
    static = np.zeros(effective_mask.shape[0], dtype=np.float32)
    if static_artifact_map is not None:
        static = row_coverage(static_artifact_map, ellipse_mask)
    return {
        "oil_signed_sobel_profile": _finite_profile(signed_sobel),
        "oil_signed_contrast_profile": _finite_profile(contrast),
        "oil_horizontal_coverage_profile": _finite_profile(coverage),
        "oil_consensus_support_profile": _finite_profile(semantic_support),
        "oil_static_overlap_profile": _finite_profile(static),
    }


def selected_hypothesis(result: OilShadowFrameResult) -> SemanticHypothesis | None:
    identity = result.temporal_decision.selected_hypothesis_id
    return None if identity is None else _hypothesis_by_id(result, identity)


def current_no_interface_evidence(
    result: OilShadowFrameResult,
) -> ShadowNoInterfaceEvidence | None:
    current = result.current_observation
    if isinstance(current, ShadowNoInterfaceObservation):
        return current.evidence
    if isinstance(current, ShadowBoundaryObservation):
        return current.no_interface
    return None


def _candidate_from_hypothesis(
    item: SemanticHypothesis,
    result: OilShadowFrameResult,
    selected_id: str | None,
) -> BoundaryCandidate:
    selected = selected_id == item.identity
    decision = result.temporal_decision
    features = {
        "hypothesis_identity_token": _identity_token(item.identity),
        "provenance_token": _identity_token("|".join(item.provenance)),
        "local_y": float(item.representative_local_y),
        "source_y": float(item.representative_source_y),
        "minimum_local_y": float(item.minimum_local_y),
        "maximum_local_y": float(item.maximum_local_y),
        "proposal_diameter_px": float(item.diameter_px),
        "proposal_count": float(len(item.proposal_ids)),
        "observation_count": float(len(item.observation_ids)),
        "provenance_count": float(len(item.provenance)),
        "boundary_likelihood": float(item.boundary_likelihood),
        "artifact_likelihood": float(item.artifact_likelihood),
        "ambiguity_likelihood": float(item.ambiguity_likelihood),
        "observation_score": float(item.boundary_likelihood),
        "edge_strength": float(item.narrow.peak_strength),
        "horizontal_coverage": float(item.narrow.horizontal_coverage),
        "region_contrast": float(item.broad.strength),
        "temporal_score": float(decision.confidence),
        "state_transition_score": float(decision.decision_margin),
        "evidence_availability": float(item.evidence_availability),
        "visibility": float(item.visibility),
        "polarity_available": float(item.polarity_available),
        "polarity": float(item.polarity),
        "polarity_confidence": float(item.polarity_confidence),
        "broad_strength": float(item.broad.strength),
        "broad_available_scale_count": float(item.broad.available_scale_count),
        "broad_scale_consistency": float(item.broad.scale_consistency),
        "broad_polarity_consistency": float(item.broad.polarity_consistency),
        "broad_transition_local_y": float(item.broad.transition_local_y),
        "broad_visibility": float(item.broad.visibility),
        "narrow_peak_strength": float(item.narrow.peak_strength),
        "narrow_horizontal_coverage": float(item.narrow.horizontal_coverage),
        "narrow_signed_lobe_order": float(item.narrow.signed_lobe_order),
        "narrow_paired_edge_separation_px": float(item.narrow.paired_edge_separation_px),
        "narrow_paired_edge_strength": float(item.narrow.paired_edge_strength),
        "narrow_pulse_symmetry": float(item.narrow.pulse_symmetry),
        "narrow_center_offset_px": float(item.narrow.center_offset_px),
        "narrow_scale_persistence": float(item.narrow.scale_persistence),
        "static_prior_available": float(item.static_prior.available),
        "static_prior_coverage": float(item.static_prior.coverage),
        "static_prior_overlap": float(item.static_prior.overlap),
        "static_prior_contribution": float(item.static_prior.contribution),
        "temporal_selected": float(selected),
        "temporal_confidence": float(decision.confidence),
        "temporal_decision_margin": float(decision.decision_margin),
    }
    glare_conflict = float(
        max(item.broad.glare_conflict, item.narrow.glare_overlap)
    )
    exclusion_conflict = float(
        max(item.broad.exclusion_conflict, item.narrow.exclusion_overlap)
    )
    penalties = {
        "artifact_likelihood": float(item.artifact_likelihood),
        "ambiguity_likelihood": float(item.ambiguity_likelihood),
        "static_prior_contribution": float(item.static_prior.contribution),
        "glare_conflict": glare_conflict,
        "exclusion_conflict": exclusion_conflict,
        "glare_penalty": glare_conflict,
        "border_penalty": float(item.narrow.border_overlap),
        "exclusion_penalty": exclusion_conflict,
        "static_artifact_penalty": float(item.static_prior.contribution),
        "jump_penalty": 0.0,
    }
    candidate = BoundaryCandidate(
        source=f"oil_hypothesis:{item.identity}",
        kind=BoundaryKind.OIL_AIR,
        y=float(item.representative_source_y),
        features=features,
        penalties=penalties,
        feature_score=float(item.boundary_likelihood),
        penalty=float(min(1.0, item.artifact_likelihood + item.ambiguity_likelihood)),
        final_score=(
            float(decision.confidence)
            if selected
            else float(item.boundary_likelihood)
        ),
        selected=selected,
        rejected=not selected,
        reject_reason="" if selected else _reject_reason(item, result),
    )
    _assert_finite_candidate(candidate)
    return candidate


def _decision_flags(result: OilShadowFrameResult) -> tuple[str, ...]:
    status = result.temporal_decision.status
    flags: list[str] = []
    if status is ShadowTemporalStatus.AMBIGUOUS:
        flags.append("OIL_EVIDENCE_AMBIGUOUS")
    elif status is ShadowTemporalStatus.UNAVAILABLE:
        flags.append("OIL_PIPELINE_UNAVAILABLE")
    elif status is ShadowTemporalStatus.REACQUISITION_PENDING:
        flags.append("OIL_REACQUISITION_PENDING")
    if not result.available:
        flags.append("OIL_PIPELINE_FAILURE")
    return tuple(flags)


def _reject_reason(
    item: SemanticHypothesis,
    result: OilShadowFrameResult,
) -> str:
    status = result.temporal_decision.status
    if status is ShadowTemporalStatus.NO_INTERFACE_ACCEPTED:
        return "typed_no_interface_selected"
    if status is ShadowTemporalStatus.AMBIGUOUS:
        return "typed_ambiguous_observation"
    if status is ShadowTemporalStatus.UNAVAILABLE:
        return "typed_unavailable_observation"
    if status is ShadowTemporalStatus.REACQUISITION_PENDING:
        if item.identity == result.temporal_decision.selected_hypothesis_id:
            return "typed_reacquisition_pending"
        return "typed_not_temporally_selected"
    if item.label.value == "artifact_like":
        return "typed_artifact_likelihood"
    if item.label.value == "ambiguous":
        return "typed_ambiguous_hypothesis"
    return "typed_not_temporally_selected"


def _validated_boundary_current(
    result: OilShadowFrameResult,
    context: str,
) -> SemanticHypothesis:
    current = result.current_observation
    if not isinstance(current, ShadowBoundaryObservation):
        raise ValueError(f"{context} has the wrong current observation")
    canonical = _hypothesis_by_id(result, current.hypothesis.identity)
    if canonical is None:
        raise ValueError(f"{context} current hypothesis is not canonical")
    if current.hypothesis != canonical:
        raise ValueError(f"{context} current hypothesis disagrees with canonical content")
    _require_same_y(
        current.hypothesis.representative_source_y,
        canonical.representative_source_y,
        f"{context} current hypothesis Y disagrees with canonical content",
    )
    return canonical


def _same_optional_y(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9)


def _require_same_y(left: float, right: float, message: str) -> None:
    if not _same_optional_y(left, right):
        raise ValueError(message)


def _hypothesis_by_id(
    result: OilShadowFrameResult,
    identity: str,
) -> SemanticHypothesis | None:
    return next((item for item in result.hypotheses if item.identity == identity), None)


def _identity_token(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return float(int(digest, 16))


def _finite_profile(values: np.ndarray) -> list[float]:
    finite = np.nan_to_num(values, nan=0.0, posinf=1.0, neginf=-1.0)
    return [float(value) for value in finite]


def _assert_finite_candidate(candidate: BoundaryCandidate) -> None:
    scalars = [
        candidate.y,
        candidate.feature_score,
        candidate.penalty,
        candidate.final_score,
        *candidate.features.values(),
        *candidate.penalties.values(),
    ]
    if not all(math.isfinite(float(value)) for value in scalars):
        raise ValueError("typed oil candidate projection must be finite")
