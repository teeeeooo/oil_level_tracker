"""Opt-in top-exit FULL closure applied after Oil path selection."""

from __future__ import annotations

from dataclasses import replace
import math
from typing import TYPE_CHECKING

from oil_tracker.domain.detection import PhaseDetection

from .oil_candidate_authority import OilCandidateAuthority
from .oil_interface_selector import (
    oil_candidate_confidence as _oil_confidence,
    recurrence_hard_contradiction as _recurrence_hard_contradiction,
)
from .oil_phase_identity import OilIdentityContradiction, OilPhaseIdentity
from .oil_phase_lifecycle import OilMaterialPhase, OilMaterialPhasePolicy
from .oil_sequence_types import (
    OilCandidateRef as _CandidateRef,
    OilSequenceNode as _Node,
    TrackletLifecycle,
)

if TYPE_CHECKING:
    from .oil_observation_resolver import (
        OilObservationResolverConfig,
        OilPathLifecycleResult,
    )


def close_top_exit_full(
    result: OilPathLifecycleResult,
    detections: tuple[PhaseDetection, ...],
    phase_layers: tuple[tuple[_Node, ...], ...],
    refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
    *,
    config: OilObservationResolverConfig,
    policy: OilMaterialPhasePolicy,
    hard_unavailable: tuple[bool, ...],
) -> OilPathLifecycleResult:
    """Close a selected rising owner, without altering any numeric selection.

    Unlike the pre-selection phase loop, this seam knows the actual observed
    owner. Only a consecutive bounded witness reaching the configured top can
    seed absence-state evidence. A reset cannot resume an old FULL episode.
    """
    top = policy.geometry_top_y
    tolerance = policy.handoff_direction_reversal_tolerance_px
    minimum_progress = max(
        4.0, policy.geometry_height * policy.drain_minimum_progress_ratio,
    )
    window_limit = max(1, config.tracklet_confirmation_window_frames)
    window: list[int] = []
    closure: dict[str, object] | None = None
    path = list(result.path)
    phases = list(result.material_phases)
    reasons = list(result.material_phase_reasons)
    owners = list(result.material_phase_owner_chains)
    diagnostics = []
    for index, (detection, node) in enumerate(zip(detections, result.path, strict=True)):
        current_refs = refs_by_frame[index]
        usable = not hard_unavailable[index] and all(
            _optional_finite(detection.debug_metrics.get(key)) is not None
            for key in ("effective_gray_mean", "effective_gray_std", "effective_gray_dynamic_range")
        )
        dt = detection.time_sec - detections[index - 1].time_sec if index else 0.0
        if closure is not None and not 0.0 < dt <= closure["maximum_gap_sec"] + 1e-6:
            usable = False
        empty = (_optional_finite(detection.debug_metrics.get("oil_no_interface_empty_likelihood")) or 0.0) >= config.state_min_evidence
        opposed = index in result.material_phase_ambiguous_frames or any(
            ref.identity_contradiction is not OilIdentityContradiction.NONE
            for ref in current_refs
        )
        current_interface = any(item.kind == "oil" for item in phase_layers[index])
        record: dict[str, object] = {
            "enabled": True, "reason": "NO_TOP_EXIT_WITNESS",
            "geometry_top_y": top, "endpoint_tolerance_px": tolerance,
            "minimum_progress_px": minimum_progress,
            "predicates": {"current_raster_available": usable, "empty_clear": not empty,
                           "ambiguity_clear": not opposed, "no_current_interface": not current_interface},
            "witness": [],
            "motion_phase": result.material_phases[index].value,
            "motion_reason": result.material_phase_reasons[index],
        }
        if not usable or empty or opposed:
            window, closure = [], None
            record["reason"] = "CURRENT_EVIDENCE_RESET"
        elif node.kind == "oil":
            closure = None
            ref = node.candidate_ref
            assert ref is not None and node.y is not None
            supported = (
                ref.tracklet_admitted and not ref.tracklet_incompatible
                and ref.tracklet_lifecycle in {TrackletLifecycle.CONFIRMED, TrackletLifecycle.CONTINUING}
                and ref.evidence.availability.material_texture
                and ref.evidence.material_texture_conflict < policy.material_conflict_limit
                and ref.tracklet_material_conflict < policy.material_conflict_limit
                and not _recurrence_hard_contradiction(ref)
                and ref.identity_contradiction is OilIdentityContradiction.NONE
                and len({item.candidate_ref.tracklet_id for item in phase_layers[index]
                         if item.candidate_ref is not None}) == 1
            )
            if window:
                prior = result.path[window[-1]]
                assert prior.candidate_ref is not None and prior.y is not None
                if (prior.candidate_ref.tracklet_id != ref.tracklet_id
                        or not math.isfinite(dt) or dt <= 0.0
                        or not 0.0 <= prior.y - node.y <= policy.maximum_jump_px):
                    window = []
            window = (window + [index])[-window_limit:] if supported else []
            record["reason"] = "OBSERVED_OWNER" if supported else "UNQUALIFIED_SELECTED_OWNER"
        elif current_interface or node.kind != "unknown":
            window, closure = [], None
            record["reason"] = "CURRENT_INTERFACE_OR_STATE_RESET"
        else:
            if window:
                refs = [result.path[offset].candidate_ref for offset in window]
                assert all(ref is not None for ref in refs)
                first, last = refs[0], refs[-1]
                assert first is not None and last is not None
                maximum_gap = max(
                    (detections[b].time_sec - detections[a].time_sec
                     for a, b in zip(window, window[1:])), default=0.0,
                )
                predicates = {
                    "consecutive_observations": len(window) >= max(2, config.tracklet_confirmation_min_observations),
                    "immediate_disappearance": window[-1] == index - 1,
                    "bounded_time_gap": 0.0 < dt <= maximum_gap + 1e-6,
                    "independent_anchor": any(ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                        and ref.phase_identity in {OilPhaseIdentity.DIRECT_INTERFACE, OilPhaseIdentity.ORDERED_LOWER_INTERFACE}
                        for ref in refs),
                    "upward_progress": first.candidate.y - last.candidate.y >= minimum_progress,
                    "recent_upward_direction": last.tracklet_recent_direction < 0,
                    "directional_agreement": last.tracklet_recent_directional_agreement >= policy.minimum_directional_agreement,
                    "top_reached": abs(last.candidate.y - top) <= tolerance,
                }
                record["predicates"].update(predicates)
                record["witness"] = [
                    {"frame_offset": offset, "frame_index": detections[offset].frame_index,
                     "time_sec": detections[offset].time_sec,
                     "tracklet_id": ref.tracklet_id, "row_hypothesis_id": ref.row_hypothesis_id,
                     "source": ref.candidate.source, "y": ref.candidate.y}
                    for offset, ref in zip(window, refs, strict=True)
                ]
                if all(predicates.values()):
                    closure = {"witness": record["witness"], "owner": last.tracklet_id,
                               "confirmation_frame_index": detection.frame_index,
                               "maximum_gap_sec": maximum_gap,
                               "confidence": min(_oil_confidence(ref) for ref in refs)}
                    record["reason"] = "TOP_EXIT_FULL_CONFIRMED"
                else:
                    record["reason"] = "TOP_EXIT_NOT_PROVEN"
                window = []
            if closure is not None:
                if record["reason"] != "TOP_EXIT_FULL_CONFIRMED":
                    record["reason"] = "TOP_EXIT_FULL_CONTINUING"
                record.update(closure)
                path[index] = _Node("full", node.emission, "full:top_exit",
                                    state_evidence_source="top_exit",
                                    temporal_state_evidence=closure["confidence"])
                phases[index] = OilMaterialPhase.FILLED_BARRIER
                reasons[index] = record["reason"]
                owners[index] = (closure["owner"],)
        diagnostic = dict(result.material_phase_diagnostics[index])
        diagnostic["top_exit_full"] = record
        if path[index].state_evidence_source == "top_exit":
            diagnostic["allowed_mode"] = "state_only"
            diagnostic["allowed_tracklet_ids"] = []
        diagnostics.append(diagnostic)
    return replace(result, path=tuple(path), material_phases=tuple(phases),
                   material_phase_reasons=tuple(reasons), material_phase_owner_chains=tuple(owners),
                   material_phase_diagnostics=tuple(diagnostics))


def _optional_finite(value: object) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None
