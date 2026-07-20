from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .enums import EventType, FillState, ResultState
from .results import EventMarker, TrackingSample
from .review import ReviewTrackingSample


class RedetectionMode(str, Enum):
    CURRENT = "current"
    SHORT = "short"
    FULL = "full"


class RedetectionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    SETTINGS_STALE = "settings_stale"
    CONTEXT_STALE = "context_stale"


@dataclass(frozen=True)
class RedetectionPolicy:
    short_before_sec: float = 2.0
    short_after_sec: float = 2.0
    short_warmup_sec: float = 2.0
    short_max_display_duration_sec: float = 30.0
    alignment_min_tolerance_sec: float = 0.05
    alignment_interval_ratio: float = 0.55
    event_tolerance_interval_ratio: float = 0.75
    max_consecutive_sample_failures: int = 8
    record_cache_size: int = 8
    image_cache_size: int = 4

    def alignment_tolerance(self, sampling_fps: float) -> float:
        fps = max(0.1, float(sampling_fps or 0.0))
        return max(self.alignment_min_tolerance_sec, self.alignment_interval_ratio / fps)

    def event_tolerance(self, sampling_fps: float) -> float:
        fps = max(0.1, float(sampling_fps or 0.0))
        return max(self.alignment_min_tolerance_sec, self.event_tolerance_interval_ratio / fps)


@dataclass(frozen=True)
class RedetectionRange:
    display_start_sec: float
    display_end_sec: float
    warmup_start_sec: float

    @property
    def display_duration_sec(self) -> float:
        return max(0.0, self.display_end_sec - self.display_start_sec)


@dataclass(frozen=True)
class RedetectionRequest:
    request_id: str
    generation: int
    bundle_root: str
    official_run_id: str
    source_video_path: str
    selected_glass_id: str
    target_timestamp_sec: float
    mode: RedetectionMode
    requested_range: RedetectionRange
    recipe_snapshot_json: str
    session_snapshot_json: str
    detector_settings_json: str


@dataclass(frozen=True)
class DetectorSettingDiff:
    field_name: str
    category: str
    baseline_value: Any
    temporary_value: Any
    numeric_delta: float | None
    changed: bool


@dataclass(frozen=True)
class RedetectionCandidate:
    rank: int
    kind: str
    source: str
    canonical_y: float | None
    feature_score: float
    total_penalty: float
    final_score: float
    selected: bool
    rejected: bool
    reject_reason: str
    features: dict[str, Any] = field(default_factory=dict)
    penalties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RedetectionSample:
    nominal_timestamp_sec: float
    requested_timestamp_sec: float
    actual_timestamp_sec: float | None
    frame_index: int | None
    tracking_sample: TrackingSample | None
    fill_state: FillState | None
    confidence: float | None
    is_valid: bool
    flags: tuple[str, ...]
    selected_candidate: RedetectionCandidate | None
    debug_record_id: str
    error_message: str = ""
    warmup: bool = False

    @property
    def succeeded(self) -> bool:
        return self.tracking_sample is not None and not self.error_message


@dataclass(frozen=True)
class RedetectionComparisonPoint:
    nominal_timestamp_sec: float
    official_sample: ReviewTrackingSample | None
    rerun_sample: RedetectionSample | None
    official_timestamp_sec: float | None
    rerun_actual_timestamp_sec: float | None
    oil_position_delta_px: float | None
    oil_position_delta_mm: float | None
    foam_position_delta_px: float | None
    foam_position_delta_mm: float | None
    confidence_delta: float | None
    fill_state_same: bool | None
    validity_same: bool | None
    flags_added: tuple[str, ...]
    flags_removed: tuple[str, ...]
    candidate_comparison_available: bool
    match_status: str


@dataclass(frozen=True)
class RedetectionEventComparison:
    event_type: EventType
    official_event: Any | None
    rerun_event: EventMarker | None
    status: str
    timestamp_delta_sec: float | None


@dataclass(frozen=True)
class RedetectionComparisonSummary:
    comparison_sample_count: int = 0
    official_only_count: int = 0
    rerun_only_count: int = 0
    matched_count: int = 0
    oil_mean_absolute_delta_px: float | None = None
    oil_max_absolute_delta_px: float | None = None
    oil_mean_absolute_delta_mm: float | None = None
    oil_max_absolute_delta_mm: float | None = None
    foam_mean_absolute_delta_px: float | None = None
    foam_max_absolute_delta_px: float | None = None
    foam_mean_absolute_delta_mm: float | None = None
    foam_max_absolute_delta_mm: float | None = None
    confidence_mean_delta: float | None = None
    fill_state_change_count: int = 0
    validity_change_count: int = 0
    event_added_count: int = 0
    event_removed_count: int = 0
    event_shifted_count: int = 0
    official_judgment: ResultState | None = None
    rerun_judgment: ResultState | None = None
    judgment_changed: bool = False


@dataclass(frozen=True)
class RedetectionProgress:
    generation: int
    stage: str
    processed_samples: int
    total_samples: int
    current_timestamp_sec: float | None = None
    message: str = ""

    @property
    def fraction(self) -> float:
        return 0.0 if self.total_samples <= 0 else min(1.0, max(0.0, self.processed_samples / self.total_samples))


@dataclass(frozen=True)
class RedetectionResult:
    request: RedetectionRequest
    workspace_root: str
    settings_diffs: tuple[DetectorSettingDiff, ...]
    samples: tuple[RedetectionSample, ...]
    comparisons: tuple[RedetectionComparisonPoint, ...]
    rerun_events: tuple[EventMarker, ...]
    event_comparisons: tuple[RedetectionEventComparison, ...]
    summary: RedetectionComparisonSummary
    official_judgment_note: str = ""
    rerun_judgment_note: str = ""
    rerun_valid_coverage_ratio: float | None = None
    candidate_baseline_available: bool = False
    limitation_message: str = ""
    warnings: tuple[str, ...] = ()
