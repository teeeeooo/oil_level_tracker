"""Opt-in top-exit FULL closure applied after Oil path selection."""

from __future__ import annotations

from dataclasses import dataclass, replace
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
    TrackletConfirmationProfile,
    TrackletLifecycle,
)

if TYPE_CHECKING:
    from .oil_observation_resolver import (
        OilObservationResolverConfig,
        OilPathLifecycleResult,
    )

_INTERFACE_IDENTITIES = frozenset({
    OilPhaseIdentity.DIRECT_INTERFACE,
    OilPhaseIdentity.ORDERED_LOWER_INTERFACE,
})
_ANCHOR_PROFILES = frozenset({
    TrackletConfirmationProfile.ANCHOR_CORRIDOR,
    TrackletConfirmationProfile.ANCHOR_TRAJECTORY,
})


@dataclass(frozen=True)
class _WitnessRow:
    offset: int
    ref: _CandidateRef
    y: float
    selected: bool


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
    """Close a rising owner that leaves through the top band (v2).

    Numeric selection before closure is unchanged. A bounded consecutive
    same-owner witness must rise into the existing entrance band and then
    vanish. Only the exit row may be the owner's publishable but unselected
    row, because the selector compares it alone against unknown once the owner
    disappears. After confirmation, FULL holds until a drain release or EMPTY
    evidence; an unusable or opposed frame inside it fails closed as UNKNOWN.
    """
    top = policy.geometry_top_y
    height = max(1.0, policy.geometry_height)
    tolerance = policy.handoff_direction_reversal_tolerance_px
    minimum_progress = max(
        4.0, policy.geometry_height * policy.drain_minimum_progress_ratio,
    )
    window_limit = max(1, config.tracklet_confirmation_window_frames)
    window: list[_WitnessRow] = []
    closure: dict[str, object] | None = None
    path = list(result.path)
    phases = list(result.material_phases)
    reasons = list(result.material_phase_reasons)
    owners = list(result.material_phase_owner_chains)
    diagnostics = []

    def supported(ref: _CandidateRef, index: int) -> bool:
        return bool(
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

    def extend(row: _WitnessRow, dt: float) -> list[_WitnessRow]:
        current = window
        if current:
            prior = current[-1]
            if (prior.ref.tracklet_id != row.ref.tracklet_id or not prior.selected
                    or not math.isfinite(dt) or dt <= 0.0
                    or not -tolerance <= prior.y - row.y <= policy.maximum_jump_px):
                current = []
        if not supported(row.ref, row.offset):
            return []
        if not row.selected and (not current or not all(item.selected for item in current)):
            return []
        return (current + [row])[-window_limit:]

    def unselected_exit_row(index: int) -> _WitnessRow | None:
        if not window:
            return None
        owner = window[-1].ref.tracklet_id
        allowed = result.material_phase_diagnostics[index].get("allowed_tracklet_ids", ())
        if allowed is not None and owner not in allowed:
            return None
        rows = [item for item in result.layers[index] if item.kind == "oil"
                and item.candidate_ref is not None and item.candidate_ref.tracklet_id == owner]
        if len(rows) != 1:
            return None
        assert rows[0].candidate_ref is not None and rows[0].y is not None
        return _WitnessRow(index, rows[0].candidate_ref, rows[0].y, False)

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
            "enabled": True, "version": "v2", "reason": "NO_TOP_EXIT_WITNESS",
            "geometry_top_y": top, "endpoint_band_ratio": policy.entrance_band_ratio,
            "reversal_tolerance_px": tolerance, "minimum_progress_px": minimum_progress,
            "predicates": {"current_raster_available": usable, "empty_clear": not empty,
                           "ambiguity_clear": not opposed, "no_current_interface": not current_interface},
            "witness": [],
            "motion_phase": result.material_phases[index].value,
            "motion_reason": result.material_phase_reasons[index],
        }
        if closure is not None and (empty or result.material_phases[index] is OilMaterialPhase.DRAINING):
            record["episode_end"] = "EMPTY_EVIDENCE" if empty else "DRAIN_RELEASE"
            window, closure = [], None
        if closure is not None:
            record.update(closure)
            if usable and not opposed:
                record["reason"] = "TOP_EXIT_FULL_CONTINUING"
            else:
                record["reason"] = "TOP_EXIT_FULL_FRAME_UNAVAILABLE"
                path[index] = next(item for item in result.layers[index] if item.kind == "unknown")
        elif not usable or empty or opposed:
            window = []
            record["reason"] = "CURRENT_EVIDENCE_RESET"
        elif node.kind == "oil":
            assert node.candidate_ref is not None and node.y is not None
            window = extend(_WitnessRow(index, node.candidate_ref, node.y, True), dt)
            record["reason"] = "OBSERVED_OWNER" if window else "UNQUALIFIED_SELECTED_OWNER"
        elif node.kind == "unknown" and current_interface:
            row = unselected_exit_row(index)
            window = [] if row is None else extend(row, dt)
            record["reason"] = "UNSELECTED_EXIT_ROW" if window else "CURRENT_INTERFACE_OR_STATE_RESET"
        elif node.kind != "unknown":
            window = []
            record["reason"] = "CURRENT_INTERFACE_OR_STATE_RESET"
        elif window:
            refs = [row.ref for row in window]
            first, last = refs[0], refs[-1]
            maximum_gap = max(
                (detections[b.offset].time_sec - detections[a.offset].time_sec
                 for a, b in zip(window, window[1:])), default=0.0,
            )
            row_anchor = any(ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
                             and ref.phase_identity in _INTERFACE_IDENTITIES for ref in refs)
            tracklet_anchor = (last.tracklet_confirmation_profile in _ANCHOR_PROFILES
                               and any(ref.phase_identity in _INTERFACE_IDENTITIES for ref in refs))
            predicates = {
                "consecutive_observations": len(window) >= max(2, config.tracklet_confirmation_min_observations),
                "immediate_disappearance": window[-1].offset == index - 1,
                "bounded_time_gap": 0.0 < dt <= maximum_gap + 1e-6,
                "independent_anchor": row_anchor or tracklet_anchor,
                "upward_progress": first.candidate.y - last.candidate.y >= minimum_progress,
                "recent_upward_direction": last.tracklet_recent_direction < 0,
                "directional_agreement": last.tracklet_recent_directional_agreement >= policy.minimum_directional_agreement,
                "top_band_reached": (last.candidate.y - top) / height <= policy.entrance_band_ratio,
            }
            record["predicates"].update(predicates)
            record["anchor_source"] = ("window_row" if row_anchor else
                                       "tracklet_profile" if tracklet_anchor else None)
            record["witness"] = [
                {"frame_offset": row.offset, "frame_index": detections[row.offset].frame_index,
                 "time_sec": detections[row.offset].time_sec,
                 "tracklet_id": row.ref.tracklet_id, "row_hypothesis_id": row.ref.row_hypothesis_id,
                 "source": row.ref.candidate.source, "y": row.ref.candidate.y, "selected": row.selected}
                for row in window
            ]
            if all(predicates.values()):
                closure = {"witness": record["witness"], "owner": last.tracklet_id,
                           "anchor_source": record["anchor_source"],
                           "confirmation_frame_index": detection.frame_index,
                           "maximum_gap_sec": maximum_gap,
                           "confidence": min(_oil_confidence(ref) for ref in refs)}
                record.update(closure)
                record["reason"] = "TOP_EXIT_FULL_CONFIRMED"
            else:
                record["reason"] = "TOP_EXIT_NOT_PROVEN"
            window = []
        if closure is not None and record["reason"] != "TOP_EXIT_FULL_FRAME_UNAVAILABLE":
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
