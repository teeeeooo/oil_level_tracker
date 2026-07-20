from typing import Any

from oil_tracker.application.ports.phase_detector import PhaseDetector
from oil_tracker.domain.recipe import GlassInspectionConfig


class PreviewDetectionUseCase:
    def __init__(self, detector: PhaseDetector) -> None:
        self.detector = detector

    def execute(self, frame: Any, glass: GlassInspectionConfig, frame_index: int, time_sec: float, debug: bool = True):
        return self.detector.detect(frame, glass, frame_index, time_sec, debug=debug)
