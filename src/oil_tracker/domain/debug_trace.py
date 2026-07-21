from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


DEBUG_TRACE_SCHEMA_VERSION = 1


class DebugCaptureReason(str, Enum):
    FIRST_SAMPLE = "first_sample"
    LAST_SAMPLE = "last_sample"
    COMPRESSOR_NEAREST = "compressor_nearest"
    INVALID = "invalid"
    LOW_CONFIDENCE = "low_confidence"
    UNKNOWN_REVIEW = "unknown_review"
    DETECTION_LOST = "detection_lost"
    GLARE_OR_FOG = "glare_or_fog"
    FOAM = "foam"
    OIL_POSITION_JUMP = "oil_position_jump"
    FOAM_POSITION_JUMP = "foam_position_jump"
    STATE_TRANSITION = "state_transition"
    CANDIDATE_AMBIGUITY = "candidate_ambiguity"
    NO_SELECTED_CANDIDATE = "no_selected_candidate"
    REJECTED_ONLY = "rejected_only"
    FULL_TRACE = "full_trace"


@dataclass(frozen=True)
class DebugCaptureDecision:
    capture: bool
    reasons: tuple[DebugCaptureReason, ...] = ()


@dataclass(frozen=True)
class DebugTraceSummary:
    record_id: str
    run_id: str
    glass_id: str
    frame_index: int
    timestamp_sec: float
    capture_reasons: tuple[str, ...]
    confidence: float
    fill_state: str
    artifact_availability: tuple[str, ...]
    byte_offset: int
    byte_length: int


@dataclass(frozen=True)
class DebugBundleIndex:
    schema_version: int
    run_id: str
    trace_level: str
    trace_path: str
    record_count: int
    records: tuple[DebugTraceSummary, ...]
    glass_counts: dict[str, int] = field(default_factory=dict)
    reason_counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class DebugTraceRecord:
    schema_version: int
    record_id: str
    run_id: str
    glass_id: str
    glass_name: str
    frame_index: int
    timestamp_sec: float
    capture_reasons: tuple[str, ...]
    fill_state: str
    confidence: dict[str, float | None]
    flags: tuple[str, ...]
    positions: dict[str, float | None]
    state: dict[str, Any]
    candidates: tuple[dict[str, Any], ...]
    images: dict[str, str]
    profiles: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class DebugTraceCompletion:
    staging_directory: str
    trace_level: str
    record_count: int
    index_relative_path: str = "debug_index.json"
    trace_relative_path: str = "debug_trace.jsonl"
