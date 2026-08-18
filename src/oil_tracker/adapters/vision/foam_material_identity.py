from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import GlassInspectionConfig

from .oil_candidate_evidence import OilCandidateEvidence, unit


@dataclass(frozen=True)
class FoamMaterialIdentity:
    """Observation-only identity for a Foam front and its residue continuation.

    This object never publishes Foam, Oil, or state. It only records which
    material-path proposals continue the same upper material boundary and the
    current row from which a distinct lower Oil proposal can be reserved.
    """

    opposition_by_candidate: dict[tuple[int, int], float]
    row_by_frame: dict[int, float]
    seeded_frame_count: int
    continued_frame_count: int

    def opposition(self, frame_offset: int, candidate_offset: int) -> float:
        return self.opposition_by_candidate.get((frame_offset, candidate_offset), 0.0)

    def row(self, frame_offset: int) -> float | None:
        return self.row_by_frame.get(frame_offset)


def track_foam_material_identity(
    detections: Sequence[PhaseDetection],
    glass: GlassInspectionConfig,
    *,
    maximum_missing_frames: int = 4,
) -> FoamMaterialIdentity:
    """Follow eligible Foam into a nearby material-path residue boundary."""

    maximum_jump = max(
        12.0,
        float(glass.detector_settings.temporal_max_jump_px),
    )
    match_tolerance = max(18.0, maximum_jump * 0.75)
    active_y: float | None = None
    missing = 0
    seeded = 0
    continued = 0
    opposition: dict[tuple[int, int], float] = {}
    rows: dict[int, float] = {}

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
            missing = 0
            seeded += 1
        elif active_y is not None:
            continuations = tuple(
                (candidate_offset, candidate)
                for candidate_offset, candidate in enumerate(detection.candidates)
                if candidate.kind is BoundaryKind.OIL_AIR
                and _can_continue_material_identity(candidate)
                and abs(float(candidate.y) - active_y) <= maximum_jump
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
                missing = 0
                continued += 1
            else:
                missing += 1
                if missing > maximum_missing_frames:
                    active_y = None

        if active_y is None:
            continue
        rows[frame_offset] = active_y
        for candidate_offset, candidate in enumerate(detection.candidates):
            if candidate.kind is not BoundaryKind.OIL_AIR:
                continue
            evidence = OilCandidateEvidence.from_candidate(candidate)
            if not evidence.material_path:
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
        seeded_frame_count=seeded,
        continued_frame_count=continued,
    )


def _can_continue_material_identity(candidate: BoundaryCandidate) -> bool:
    evidence = OilCandidateEvidence.from_candidate(candidate)
    return bool(
        evidence.material_path
        and (
            evidence.material_texture_conflict >= 0.30
            or evidence.raw_material_row_support >= 0.35
            or evidence.sector_fraction >= 0.60
        )
        and evidence.artifact_signature <= 0.48
        and evidence.ambiguity <= 0.75
    )
