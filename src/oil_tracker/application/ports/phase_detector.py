from __future__ import annotations

from typing import Any, Protocol

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.recipe import GlassInspectionConfig


class PhaseDetector(Protocol):
    def detect(self, frame: Any, glass: GlassInspectionConfig, frame_index: int, time_sec: float, debug: bool = False) -> tuple[PhaseDetection, Any | None]: ...
    def reset(self, glass_id: str | None = None) -> None: ...
