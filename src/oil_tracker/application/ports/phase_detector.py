from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig


class PhaseDetector(Protocol):
    """Observe one frame while retaining detector-local serialized state."""

    version: str

    def detect(self, frame: Any, glass: GlassInspectionConfig, frame_index: int, time_sec: float, debug: bool = False) -> tuple[PhaseDetection, Any | None]: ...
    def reset(self, glass_id: str | None = None) -> None: ...


class StaticArtifactLearner(Protocol):
    """Prepare static evidence for the same detector instance used by a run."""

    def learn_static_artifact(
        self,
        frames: Sequence[Any],
        glass: GlassInspectionConfig,
    ) -> None: ...


class CompletedWindowResolution(Protocol):
    """Typed result returned by a completed-window observation owner."""

    detections: Sequence[PhaseDetection]
    diagnostics: Any | None


class CompletedWindowResolver(Protocol):
    """Resolve final Oil/state/Foam observations after frame acquisition."""

    def resolve_sequence(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> CompletedWindowResolution: ...


class PreparedFrameDetector(PhaseDetector, StaticArtifactLearner, Protocol):
    """Current-frame detector with the official static-preparation capability."""


class AnalysisDetector(
    PreparedFrameDetector,
    CompletedWindowResolver,
    Protocol,
):
    """Complete official analysis capability implemented by one detector."""
