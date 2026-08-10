from __future__ import annotations

from dataclasses import replace
import math

from oil_tracker.domain.oil_boundary_topology import (
    BOTTOM_ENTRANCE_MIN_RELATIVE_POSITION,
    TOP_ENTRANCE_MAX_RELATIVE_POSITION,
    boundary_relative_position,
)
from oil_tracker.domain.enums import FillState, InitialObservationState, JudgmentMode, ResultState
from oil_tracker.domain.retrospective import RetrospectiveInterpretation, RetrospectiveStatus
from oil_tracker.domain.results import TrackingSample


_BARRIER_FLAGS = {
    "DETECTION_LOST",
    "FOGGED_OR_GLARE",
    "DETECTION_FAILED",
    "REDETECTION_SAMPLE_FAILED",
    "FRAME_UNAVAILABLE",
    "UNAVAILABLE",
}
_FOAM_STATES = {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE}


def reconstruct_initial_state(glass, samples: list[TrackingSample], confirmation) -> RetrospectiveInterpretation:
    prior = getattr(confirmation, "state", None)
    if prior not in {InitialObservationState.FULL_NO_INTERFACE, InitialObservationState.EMPTY_NO_INTERFACE}:
        return RetrospectiveInterpretation(
            glass_id=glass.id,
            status=RetrospectiveStatus.NOT_APPLICABLE,
            confirmed_prior=prior,
            reason="Confirmed current-run state does not grant retrospective FULL/EMPTY authority.",
        )
    if not samples:
        return _unresolved(glass.id, prior, "No observed samples are available.")

    accepted: list[tuple[int, TrackingSample, float]] = []
    first_boundary_index: int | None = None
    for index, sample in enumerate(samples):
        contradiction = _contradiction_reason(sample, prior)
        if contradiction:
            return RetrospectiveInterpretation(
                glass_id=glass.id,
                status=RetrospectiveStatus.CONFLICT,
                confirmed_prior=prior,
                reason=contradiction,
            )
        boundary_y = _accepted_boundary_y(sample)
        barrier = _barrier_reason(
            sample,
            has_numeric_boundary=boundary_y is not None,
        )
        if barrier:
            if len(accepted) < 2:
                return _unresolved(glass.id, prior, "Inference barrier before sufficient positive evidence.", (barrier,))
            break
        if boundary_y is None:
            continue
        if first_boundary_index is None:
            first_boundary_index = index
            if index == 0:
                return RetrospectiveInterpretation(
                    glass_id=glass.id,
                    status=RetrospectiveStatus.NOT_APPLICABLE,
                    confirmed_prior=prior,
                    reason="No leading unresolved interval precedes direct numeric Oil evidence.",
                )
        ellipse = glass.geometry.ellipse
        top = ellipse.center_y - ellipse.radius_y
        bottom = ellipse.center_y + ellipse.radius_y
        accepted.append((index, sample, boundary_relative_position(boundary_y, top, bottom)))
        if len(accepted) >= 2:
            break

    if first_boundary_index is None or len(accepted) < 2:
        return _unresolved(glass.id, prior, "Fewer than two real accepted numeric Oil boundary observations establish direction.")

    first_index, first, first_relative = accepted[0]
    _second_index, second, second_relative = accepted[1]
    delta_y = float(second.raw_oil_air_level_y) - float(first.raw_oil_air_level_y)
    if prior is InitialObservationState.FULL_NO_INTERFACE:
        topology_ok = first_relative <= TOP_ENTRANCE_MAX_RELATIVE_POSITION
        topology_opposite = first_relative >= BOTTOM_ENTRANCE_MIN_RELATIVE_POSITION
        direction_ok = delta_y > 1e-9
        direction_opposite = delta_y < -1e-9
        state = FillState.FULL_NO_INTERFACE
    else:
        topology_ok = first_relative >= BOTTOM_ENTRANCE_MIN_RELATIVE_POSITION
        topology_opposite = first_relative <= TOP_ENTRANCE_MAX_RELATIVE_POSITION
        direction_ok = delta_y < -1e-9
        direction_opposite = delta_y > 1e-9
        state = FillState.EMPTY_NO_INTERFACE

    evidence_kwargs = dict(
        evidence_frame_indices=(first.frame_index, second.frame_index),
        evidence_timestamps_sec=(first.timestamp_sec, second.timestamp_sec),
        evidence_relative_positions=(first_relative, second_relative),
    )
    if topology_opposite or (topology_ok and direction_opposite):
        return RetrospectiveInterpretation(
            glass_id=glass.id,
            status=RetrospectiveStatus.CONFLICT,
            confirmed_prior=prior,
            reason="Prior-independent numeric boundary topology/direction contradicts the confirmed prior.",
            **evidence_kwargs,
        )
    if not topology_ok or not direction_ok:
        return RetrospectiveInterpretation(
            glass_id=glass.id,
            status=RetrospectiveStatus.UNRESOLVED,
            confirmed_prior=prior,
            reason="Numeric evidence is real but does not establish compatible entrance topology and direction.",
            **evidence_kwargs,
        )

    prefix = samples[:first_index]
    return RetrospectiveInterpretation(
        glass_id=glass.id,
        status=RetrospectiveStatus.ACCEPTED,
        confirmed_prior=prior,
        interpreted_state=state,
        start_time_sec=prefix[0].timestamp_sec,
        end_time_sec=prefix[-1].timestamp_sec,
        start_frame_index=prefix[0].frame_index,
        end_frame_index=prefix[-1].frame_index,
        reason="Leading unresolved interval reconstructed from confirmed prior plus independent numeric entrance topology and direction.",
        **evidence_kwargs,
    )


def project_state_aware_samples(
    samples: list[TrackingSample],
    interpretation: RetrospectiveInterpretation | None,
) -> list[TrackingSample]:
    if interpretation is None or not interpretation.accepted or interpretation.interpreted_state is None:
        return list(samples)
    projected = []
    for sample in samples:
        if interpretation.contains(sample.timestamp_sec):
            projected.append(
                replace(
                    sample,
                    fill_state=interpretation.interpreted_state,
                    is_valid=True,
                    flags=[*sample.flags, "RETROSPECTIVE_INITIAL_STATE"],
                )
            )
        else:
            projected.append(sample)
    return projected


def observed_coverage(samples: list[TrackingSample]) -> float:
    return 0.0 if not samples else sum(sample.is_valid for sample in samples) / len(samples)


def effective_state_aware_coverage(
    samples: list[TrackingSample],
    interpretation: RetrospectiveInterpretation | None,
) -> float:
    return observed_coverage(project_state_aware_samples(samples, interpretation))


def samples_for_judgment(samples, interpretation, mode: JudgmentMode):
    if mode is JudgmentMode.RECOVERY:
        return list(samples)
    return project_state_aware_samples(list(samples), interpretation)


def enforce_conflict_review(
    outcome,
    interpretation: RetrospectiveInterpretation | None,
):
    if interpretation is None or not interpretation.conflict:
        return outcome
    return replace(
        outcome,
        state=ResultState.REVIEW_REQUIRED,
        note=f"{outcome.note} Retrospective initial-state conflict requires review.",
    )


def annotate_judgment_provenance(
    outcome,
    interpretation: RetrospectiveInterpretation | None,
    mode: JudgmentMode,
):
    if interpretation is None or not interpretation.accepted or mode is JudgmentMode.RECOVERY:
        return outcome
    return replace(
        outcome,
        note=_append_note(outcome.note, "provenance=retrospective_initial_state"),
    )


def annotate_retrospective_events(events, interpretation: RetrospectiveInterpretation):
    if not interpretation.accepted:
        return events
    attributable = {
        "FULL_NO_INTERFACE_START",
        "EMPTY_NO_INTERFACE_START",
        "OIL_BOUNDARY_APPEARED_FROM_TOP",
        "OIL_BOUNDARY_APPEARED_FROM_BOTTOM",
    }
    output = []
    for event in events:
        if event.event_type.value in attributable:
            output.append(replace(event, note=_append_note(event.note, "provenance=retrospective_initial_state")))
        else:
            output.append(event)
    return output


def merge_state_aware_events(
    observed_events,
    projected_events,
    interpretation: RetrospectiveInterpretation | None,
):
    """Keep observed-quality/numeric events and add only retrospective state events."""
    if interpretation is None or not interpretation.accepted:
        return list(observed_events)
    attributable = {
        "FULL_NO_INTERFACE_START",
        "EMPTY_NO_INTERFACE_START",
        "OIL_BOUNDARY_APPEARED_FROM_TOP",
        "OIL_BOUNDARY_APPEARED_FROM_BOTTOM",
    }
    output = list(observed_events)
    existing = {
        (event.event_type.value, round(event.start_time_sec, 6), event.end_time_sec)
        for event in output
    }
    for event in annotate_retrospective_events(projected_events, interpretation):
        if event.event_type.value not in attributable:
            continue
        key = (event.event_type.value, round(event.start_time_sec, 6), event.end_time_sec)
        if key not in existing:
            output.append(event)
            existing.add(key)
    return sorted(output, key=lambda event: (event.start_time_sec, event.event_type.value))


def _accepted_boundary_y(sample: TrackingSample) -> float | None:
    value = sample.raw_oil_air_level_y
    if not sample.is_valid or value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def _contradiction_reason(sample: TrackingSample, prior: InitialObservationState) -> str:
    if not sample.is_valid:
        return ""
    if (
        prior is InitialObservationState.FULL_NO_INTERFACE
        and sample.fill_state is FillState.EMPTY_NO_INTERFACE
    ):
        return "Observed direct EMPTY_NO_INTERFACE evidence contradicts the confirmed FULL prior."
    if (
        prior is InitialObservationState.EMPTY_NO_INTERFACE
        and sample.fill_state is FillState.FULL_NO_INTERFACE
    ):
        return "Observed direct FULL_NO_INTERFACE evidence contradicts the confirmed EMPTY prior."
    return ""


def _barrier_reason(
    sample: TrackingSample,
    *,
    has_numeric_boundary: bool = False,
) -> str:
    """Return sequence evidence that blocks a leading-state interpretation.

    Hard unavailable/failure evidence remains a barrier even on malformed input
    that also carries a number.  Authoritative Foam alone is a barrier, but it
    cannot erase an independently accepted canonical Oil boundary already
    constrained by the current-frame Foam topology.
    """

    flags = {str(flag).strip().upper() for flag in sample.flags}
    for flag in sorted(flags):
        if (
            flag in _BARRIER_FLAGS
            or "UNAVAILABLE" in flag
            or "FAILURE" in flag
            or "FAILED" in flag
            or "GLARE" in flag
            or "FOG" in flag
            or "DETECTION_LOST" in flag
        ):
            return flag
    if not has_numeric_boundary and (
        sample.fill_state in _FOAM_STATES
        or "FOAM_REACH_TOP" in flags
        or "FOAM_STRONG_EVIDENCE" in flags
        or "FOAM_MODERATE_EVIDENCE" in flags
    ):
        return "AUTHORITATIVE_FOAM"
    return ""


def _unresolved(glass_id, prior, reason, barriers=()):
    return RetrospectiveInterpretation(
        glass_id=glass_id,
        status=RetrospectiveStatus.UNRESOLVED,
        confirmed_prior=prior,
        barriers=tuple(barriers),
        reason=reason,
    )


def _append_note(existing: str, addition: str) -> str:
    return f"{existing}; {addition}" if existing else addition
