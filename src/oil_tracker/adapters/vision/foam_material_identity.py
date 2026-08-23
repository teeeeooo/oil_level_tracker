from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import GlassInspectionConfig

from .oil_candidate_evidence import (
    OilCandidateEvidence,
    OilCandidateEvidenceIndex,
    unit,
)


@dataclass(frozen=True)
class FoamMaterialIdentity:
    """Observation-only identity for a Foam front and its residue continuation.

    This object never publishes Foam, Oil, or state. It only records which
    material-path proposals continue the same upper material boundary and the
    current row from which a distinct lower Oil proposal can be reserved.
    """

    opposition_by_candidate: dict[tuple[int, int], float]
    row_by_frame: dict[int, float]
    seed_age_seconds_by_frame: dict[int, float]
    seeded_frame_count: int
    continued_frame_count: int

    def opposition(self, frame_offset: int, candidate_offset: int) -> float:
        return self.opposition_by_candidate.get((frame_offset, candidate_offset), 0.0)

    def row(self, frame_offset: int) -> float | None:
        return self.row_by_frame.get(frame_offset)

    def seed_age_seconds(self, frame_offset: int) -> float | None:
        """Return age of the latest direct Foam observation at this frame.

        A continued residue row remains useful as opposition evidence, but its
        mere persistence must not grant a new Oil anchor below it.
        """

        return self.seed_age_seconds_by_frame.get(frame_offset)


def track_foam_material_identity(
    detections: Sequence[PhaseDetection],
    glass: GlassInspectionConfig,
    *,
    maximum_missing_seconds: float = 3.0,
    maximum_seed_age_seconds: float = 12.0,
    evidence_index: OilCandidateEvidenceIndex | None = None,
) -> FoamMaterialIdentity:
    """Follow eligible Foam into a bounded cross-family residue identity."""

    maximum_jump = max(
        12.0,
        float(glass.detector_settings.temporal_max_jump_px),
    )
    match_tolerance = foam_material_identity_tolerance(glass)
    maximum_drift = max(
        36.0,
        min(72.0, float(glass.geometry.ellipse.radius_y) * 2.0 * 0.12),
    )
    active_y: float | None = None
    seed_y: float | None = None
    seed_time: float | None = None
    last_time: float | None = None
    seeded = 0
    continued = 0
    opposition: dict[tuple[int, int], float] = {}
    rows: dict[int, float] = {}
    seed_ages: dict[int, float] = {}

    for frame_offset, detection in enumerate(detections):
        foam_rows = tuple(
            float(candidate.y)
            for candidate in detection.candidates
            if candidate.kind is BoundaryKind.FOAM_FRONT
            and unit(candidate.features.get("sequence_foam_eligible", 0.0)) >= 0.5
        )
        if foam_rows:
            active_y = (
                min(foam_rows, key=lambda row: abs(row - active_y))
                if active_y is not None
                else max(foam_rows)
            )
            seed_y = active_y
            seed_time = float(detection.time_sec)
            last_time = seed_time
            seeded += 1
        elif active_y is not None:
            now = float(detection.time_sec)
            if (
                seed_y is None
                or seed_time is None
                or last_time is None
                or now - seed_time > maximum_seed_age_seconds
                or now - last_time > maximum_missing_seconds
            ):
                active_y = None
                seed_y = None
                seed_time = None
                last_time = None
                continue
            continuations = tuple(
                (candidate_offset, candidate)
                for candidate_offset, candidate in enumerate(detection.candidates)
                if candidate.kind is BoundaryKind.OIL_AIR
                and _can_continue_material_identity(
                    candidate,
                    evidence_index=evidence_index,
                )
                and abs(float(candidate.y) - active_y) <= maximum_jump
                and abs(float(candidate.y) - seed_y) <= maximum_drift
            )
            if continuations:
                _offset, continuation = min(
                    continuations,
                    key=lambda item: (
                        abs(float(item[1].y) - active_y),
                        -float(item[1].final_score),
                    ),
                )
                active_y = float(continuation.y)
                last_time = now
                continued += 1
            else:
                if now - last_time > maximum_missing_seconds:
                    active_y = None
                    seed_y = None
                    seed_time = None
                    last_time = None

        if active_y is None:
            continue
        rows[frame_offset] = active_y
        if seed_time is not None:
            seed_ages[frame_offset] = max(
                0.0,
                float(detection.time_sec) - seed_time,
            )
        for candidate_offset, candidate in enumerate(detection.candidates):
            if candidate.kind is not BoundaryKind.OIL_AIR:
                continue
            evidence = _evidence(candidate, evidence_index)
            if not _has_material_identity_evidence(evidence):
                continue
            distance = abs(float(candidate.y) - active_y)
            if distance > match_tolerance:
                continue
            opposition[(frame_offset, candidate_offset)] = unit(
                1.0 - distance / match_tolerance
            )

    return FoamMaterialIdentity(
        opposition_by_candidate=opposition,
        row_by_frame=rows,
        seed_age_seconds_by_frame=seed_ages,
        seeded_frame_count=seeded,
        continued_frame_count=continued,
    )


def _can_continue_material_identity(
    candidate: BoundaryCandidate,
    *,
    evidence_index: OilCandidateEvidenceIndex | None = None,
) -> bool:
    evidence = _evidence(candidate, evidence_index)
    return bool(
        _has_material_identity_evidence(evidence)
        and evidence.artifact_signature <= 0.48
        and evidence.ambiguity <= 0.75
    )


def _evidence(
    candidate: BoundaryCandidate,
    evidence_index: OilCandidateEvidenceIndex | None,
) -> OilCandidateEvidence:
    if evidence_index is None:
        return OilCandidateEvidence.from_candidate(candidate)
    return evidence_index.evidence(candidate)


def _has_material_identity_evidence(evidence: OilCandidateEvidence) -> bool:
    return bool(
        evidence.availability.material_texture
        and (
            evidence.material_texture_conflict >= 0.30
            or evidence.raw_material_row_support >= 0.35
            or (evidence.material_path and evidence.sector_fraction >= 0.60)
        )
    )


def foam_material_identity_tolerance(glass: GlassInspectionConfig) -> float:
    height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    return max(5.0, min(10.0, height * 0.012))
