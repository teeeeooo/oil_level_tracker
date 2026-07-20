from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .enums import EventType, FillState, ResultState
from .recipe import InspectionRecipe
from .session import AnalysisSession, VideoMetadata


@dataclass(frozen=True)
class ReviewTrackingSample:
    run_id: str
    glass_id: str
    frame_index: int
    timestamp_sec: float
    fill_state: FillState
    raw_oil_air_level_y: float | None = None
    raw_oil_air_level_px_from_zero: float | None = None
    raw_oil_air_level_mm_from_zero: float | None = None
    smoothed_oil_air_level_px_from_zero: float | None = None
    smoothed_oil_air_level_mm_from_zero: float | None = None
    oil_air_confidence: float = 0.0
    raw_foam_front_y: float | None = None
    raw_foam_front_px_from_zero: float | None = None
    raw_foam_front_mm_from_zero: float | None = None
    smoothed_foam_front_px_from_zero: float | None = None
    smoothed_foam_front_mm_from_zero: float | None = None
    foam_confidence: float = 0.0
    visibility_confidence: float = 0.0
    overall_confidence: float = 0.0
    is_valid: bool = False
    flags: tuple[str, ...] = ()
    input_order: int = 0

    def oil_boundary_y(self, zero_line_y: float | None) -> float | None:
        if zero_line_y is not None and self.smoothed_oil_air_level_px_from_zero is not None:
            return zero_line_y - self.smoothed_oil_air_level_px_from_zero
        return self.raw_oil_air_level_y

    def foam_front_y(self, zero_line_y: float | None) -> float | None:
        if zero_line_y is not None and self.smoothed_foam_front_px_from_zero is not None:
            return zero_line_y - self.smoothed_foam_front_px_from_zero
        return self.raw_foam_front_y


@dataclass(frozen=True)
class ReviewEvent:
    run_id: str
    glass_id: str
    event_type: EventType
    start_time_sec: float
    end_time_sec: float | None = None
    representative_frame_index: int | None = None
    oil_level_px: float | None = None
    oil_level_mm: float | None = None
    foam_front_px: float | None = None
    foam_front_mm: float | None = None
    confidence: float = 0.0
    capture_path: str = ""
    note: str = ""
    input_order: int = 0


@dataclass(frozen=True)
class ReviewGlass:
    id: str
    name: str
    result_state: ResultState = ResultState.NOT_APPLICABLE


@dataclass(frozen=True)
class LowConfidenceInterval:
    glass_id: str
    start_time_sec: float
    end_time_sec: float
    representative_time_sec: float
    minimum_confidence: float
    reasons: tuple[str, ...]
    sample_count: int


@dataclass(frozen=True)
class ReviewOverlayData:
    glass_id: str
    video_timestamp_sec: float
    sample: ReviewTrackingSample | None
    oil_boundary_y: float | None
    foam_front_y: float | None
    within_analysis_range: bool
    review_reasons: tuple[str, ...] = ()
    boundary_status: str = ""


@dataclass
class ReviewBundle:
    root: Path
    run_id: str
    recipe: InspectionRecipe
    session: AnalysisSession
    manifest: dict[str, Any]
    source_video_path: str
    source_video_candidates: tuple[str, ...]
    source_metadata: VideoMetadata | None
    analysis_start_sec: float
    analysis_end_sec: float
    compressor_start_sec: float | None
    glasses: tuple[ReviewGlass, ...]
    samples: tuple[ReviewTrackingSample, ...]
    events: tuple[ReviewEvent, ...]
    files: dict[str, Path] = field(default_factory=dict)
    debug_trace_level: str = "none"
    review_index: dict[str, Any] | None = None

    def glass_config(self, glass_id: str):
        return next((glass for glass in self.recipe.glasses if glass.id == glass_id), None)

    def glass_summary(self, glass_id: str) -> ReviewGlass | None:
        return next((glass for glass in self.glasses if glass.id == glass_id), None)
