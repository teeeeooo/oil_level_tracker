from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import BoundaryKind, FillState


@dataclass
class BoundaryCandidate:
    source: str
    kind: BoundaryKind
    y: float
    features: dict[str, float] = field(default_factory=dict)
    penalties: dict[str, float] = field(default_factory=dict)
    feature_score: float = 0.0
    penalty: float = 0.0
    final_score: float = 0.0
    selected: bool = False
    rejected: bool = False
    reject_reason: str = ""


@dataclass
class PhaseDetection:
    glass_id: str
    frame_index: int
    time_sec: float
    fill_state: FillState
    oil_air_level_y: float | None = None
    oil_air_level_px_from_zero: float | None = None
    oil_air_level_mm_from_zero: float | None = None
    foam_front_y: float | None = None
    foam_front_px_from_zero: float | None = None
    foam_front_mm_from_zero: float | None = None
    oil_air_confidence: float = 0.0
    foam_confidence: float = 0.0
    visibility_confidence: float = 0.0
    overall_confidence: float = 0.0
    raw_oil_air_level_y: float | None = None
    raw_foam_front_y: float | None = None
    smoothed_oil_air_level_y: float | None = None
    smoothed_foam_front_y: float | None = None
    candidates: list[BoundaryCandidate] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    debug_metrics: dict[str, Any] = field(default_factory=dict)
