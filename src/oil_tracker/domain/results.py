from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import EventType, FillState, ResultState
from .retrospective import RetrospectiveInterpretation


@dataclass
class TrackingSample:
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
    oil_is_valid: bool | None = None
    foam_is_valid: bool | None = None
    flags: list[str] = field(default_factory=list)


@dataclass
class EventMarker:
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


@dataclass
class GlassAnalysisResult:
    glass_id: str
    glass_name: str
    result_state: ResultState
    samples: list[TrackingSample] = field(default_factory=list)
    events: list[EventMarker] = field(default_factory=list)
    valid_coverage_ratio: float = 0.0
    judgment_note: str = ""
    effective_state_aware_coverage_ratio: float = 0.0
    retrospective: RetrospectiveInterpretation | None = None


@dataclass
class AnalysisResult:
    run_id: str
    overall_state: ResultState
    glass_results: list[GlassAnalysisResult]
    started_at: str
    completed_at: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    manifest: dict[str, Any] = field(default_factory=dict)
    output_directory: str = ""
    debug_trace_completion: Any | None = None
