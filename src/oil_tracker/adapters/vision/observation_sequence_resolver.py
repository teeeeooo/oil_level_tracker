from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig

from .foam_episode_resolver import FoamEpisodeResolver
from .oil_observation_resolver import OilObservationResolver


OBSERVATION_SEQUENCE_VERSION = "r10-calibrated-path-and-layer-v1"


@dataclass(frozen=True)
class ObservationSequenceDiagnostics:
    version: str
    frame_count: int
    oil_frame_count: int
    full_frame_count: int
    empty_frame_count: int
    unknown_frame_count: int
    eligible_oil_candidate_count: int
    ineligible_oil_candidate_count: int
    recurring_track_count: int
    maximum_track_opposition: float
    oil_candidate_only_count: int
    oil_continuation_eligible_count: int
    oil_anchor_eligible_count: int
    oil_qualified_anchor_count: int
    foam_raw_candidate_count: int
    foam_eligible_candidate_count: int
    foam_confirmed_frame_count: int
    foam_episode_count: int
    foam_rejected_static_episode_count: int
    foam_rejected_unconfirmed_episode_count: int
    foam_rejected_oil_alias_episode_count: int


@dataclass(frozen=True)
class ObservationSequenceResolution:
    detections: tuple[PhaseDetection, ...]
    diagnostics: ObservationSequenceDiagnostics


class ObservationSequenceResolver:
    """Compose independent Oil/state and Foam owners exactly once."""

    version = OBSERVATION_SEQUENCE_VERSION

    def __init__(self) -> None:
        self._oil = OilObservationResolver()
        self._foam = FoamEpisodeResolver()

    def resolve(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> ObservationSequenceResolution:
        oil = self._oil.resolve(
            detections,
            glass,
            confirmed_initial_state,
        )
        foam_detections, foam = self._foam.resolve(oil.detections, glass)
        diagnostics = ObservationSequenceDiagnostics(
            version=self.version,
            frame_count=oil.diagnostics.frame_count,
            oil_frame_count=oil.diagnostics.oil_frame_count,
            full_frame_count=oil.diagnostics.full_frame_count,
            empty_frame_count=oil.diagnostics.empty_frame_count,
            unknown_frame_count=oil.diagnostics.unknown_frame_count,
            eligible_oil_candidate_count=oil.diagnostics.eligible_candidate_count,
            ineligible_oil_candidate_count=oil.diagnostics.ineligible_candidate_count,
            recurring_track_count=oil.diagnostics.recurring_track_count,
            maximum_track_opposition=oil.diagnostics.maximum_track_opposition,
            oil_candidate_only_count=oil.diagnostics.candidate_only_count,
            oil_continuation_eligible_count=(
                oil.diagnostics.continuation_eligible_count
            ),
            oil_anchor_eligible_count=oil.diagnostics.anchor_eligible_count,
            oil_qualified_anchor_count=oil.diagnostics.qualified_anchor_count,
            foam_raw_candidate_count=foam.raw_candidate_count,
            foam_eligible_candidate_count=foam.eligible_candidate_count,
            foam_confirmed_frame_count=foam.confirmed_frame_count,
            foam_episode_count=foam.episode_count,
            foam_rejected_static_episode_count=foam.rejected_static_episode_count,
            foam_rejected_unconfirmed_episode_count=(
                foam.rejected_unconfirmed_episode_count
            ),
            foam_rejected_oil_alias_episode_count=(
                foam.rejected_oil_alias_episode_count
            ),
        )
        return ObservationSequenceResolution(foam_detections, diagnostics)
