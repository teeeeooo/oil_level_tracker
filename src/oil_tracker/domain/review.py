from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .enums import EventType, FillState, ResultState
from .recipe import InspectionRecipe
from .session import AnalysisSession, VideoMetadata


class ReviewCategory(str, Enum):
    INVALID = "invalid"
    LOW_CONFIDENCE = "low_confidence"
    REVIEW_REQUIRED = "review_required"
    FOAM = "foam"
    GLARE_OR_FOG = "glare_or_fog"
    DETECTION_LOST = "detection_lost"


class ReviewFilter(str, Enum):
    ALL = "all"
    INVALID = ReviewCategory.INVALID.value
    LOW_CONFIDENCE = ReviewCategory.LOW_CONFIDENCE.value
    REVIEW_REQUIRED = ReviewCategory.REVIEW_REQUIRED.value
    FOAM = ReviewCategory.FOAM.value
    GLARE_OR_FOG = ReviewCategory.GLARE_OR_FOG.value
    DETECTION_LOST = ReviewCategory.DETECTION_LOST.value

    @property
    def category(self) -> ReviewCategory | None:
        return None if self is ReviewFilter.ALL else ReviewCategory(self.value)


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
    categories: tuple[ReviewCategory, ...] = ()

    def matches(self, review_filter: ReviewFilter) -> bool:
        category = review_filter.category
        return category is None or category in self.categories


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


@dataclass(frozen=True)
class ReviewGraphPoint:
    timestamp_sec: float
    value: float | None
    is_valid: bool
    confidence: float


@dataclass(frozen=True)
class ReviewGraphSeries:
    name: str
    points: tuple[ReviewGraphPoint, ...]

    @property
    def has_values(self) -> bool:
        return any(point.value is not None for point in self.points)


@dataclass(frozen=True)
class ReviewGraphEventMarker:
    timestamp_sec: float
    label: str
    end_time_sec: float | None = None


@dataclass(frozen=True)
class ReviewGraphHighlight:
    start_time_sec: float
    end_time_sec: float
    categories: tuple[ReviewCategory, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ReviewGraphDebugMarker:
    timestamp_sec: float
    reasons: tuple[str, ...]
    selected: bool = False


@dataclass(frozen=True)
class ReviewGraphTruthMarker:
    timestamp_sec: float
    annotation_id: str
    disposition: str
    error_types: tuple[str, ...] = ()
    selected: bool = False


@dataclass(frozen=True)
class ReviewGraphModel:
    glass_id: str
    glass_name: str
    unit: str
    y_axis_label: str
    oil_air: ReviewGraphSeries
    foam_front: ReviewGraphSeries
    event_markers: tuple[ReviewGraphEventMarker, ...]
    highlights: tuple[ReviewGraphHighlight, ...]
    analysis_start_sec: float
    analysis_end_sec: float
    compressor_start_sec: float | None
    cursor_timestamp_sec: float
    debug_markers: tuple[ReviewGraphDebugMarker, ...] = ()
    truth_markers: tuple[ReviewGraphTruthMarker, ...] = ()
    axis_lower: float | None = None
    axis_upper: float | None = None
    analysis_top_boundary_value: float | None = None
    analysis_bottom_boundary_value: float | None = None
    range_source: str = "unavailable"
    range_reason: str = ""


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
    debug_index_path: str = ""
    debug_trace_path: str = ""
    debug_record_count: int = 0
    debug_warning: str = ""
    review_index: dict[str, Any] | None = None

    @property
    def has_debug_trace(self) -> bool:
        return self.debug_trace_level != "none" and self.debug_record_count > 0 and not self.debug_warning

    @property
    def run_name(self) -> str:
        index = self.review_index or {}
        for value in (
            index.get("run_name"),
            self.manifest.get("run_name"),
            getattr(self.session, "run_name", ""),
        ):
            text = str(value or "").strip()
            if text:
                return text
        return ""

    def glass_config(self, glass_id: str):
        return next((glass for glass in self.recipe.glasses if glass.id == glass_id), None)

    def glass_summary(self, glass_id: str) -> ReviewGlass | None:
        return next((glass for glass in self.glasses if glass.id == glass_id), None)
