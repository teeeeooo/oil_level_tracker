from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

from .oil_shadow_types import (
    CompatibilityTrackerAction,
    OilCanonicalOutcome,
    ShadowObservationKind,
    ShadowResourceSummary,
    ShadowTemporalDecision,
    SmoothingAction,
)


@dataclass(frozen=True)
class _BeamItem:
    kind: ShadowObservationKind
    identity: str | None
    source_y: float | None
    observation_score: float
    cumulative_score: float
    transition_cost: float
    velocity: float | None
    history: tuple[tuple[str, str | None, float | None, float], ...]


@dataclass(frozen=True)
class GlassTemporalState:
    glass_id: str
    beam: tuple[_BeamItem, ...] = ()
    accepted_y: float | None = None
    accepted_velocity: float | None = None
    pending_y: float | None = None
    pending_velocity: float | None = None
    pending_count: int = 0
    no_interface_count: int = 0
    unavailable_count: int = 0
    smoothing_invalidated: bool = False
    last_static_contribution: float = 0.0
    last_static_available: float = 0.0

    def __post_init__(self) -> None:
        if type(self.glass_id) is not str or not self.glass_id:
            raise ValueError("Glass temporal state requires a Glass identity.")
        counters = (
            self.pending_count,
            self.no_interface_count,
            self.unavailable_count,
        )
        if any(type(value) is not int for value in counters):
            raise TypeError("Glass temporal counters must be integers.")
        if any(value < 0 for value in counters):
            raise ValueError("Glass temporal counters cannot be negative.")
        if type(self.smoothing_invalidated) is not bool:
            raise TypeError("Glass smoothing invalidation state must be boolean.")
        if type(self.beam) is not tuple:
            raise TypeError("Glass temporal beam must be immutable.")
        for value, name in (
            (self.accepted_y, "accepted Y"),
            (self.accepted_velocity, "accepted velocity"),
            (self.pending_y, "pending Y"),
            (self.pending_velocity, "pending velocity"),
        ):
            if value is not None and not math.isfinite(float(value)):
                raise ValueError(f"Glass temporal {name} must be finite.")
        for value, name in (
            (self.last_static_contribution, "static contribution"),
            (self.last_static_available, "static availability"),
        ):
            if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"Glass temporal {name} must be normalized.")


@dataclass(frozen=True)
class GlassTemporalRecord:
    glass_id: str
    version: int
    temporal_state: GlassTemporalState

    def __post_init__(self) -> None:
        if type(self.glass_id) is not str or not self.glass_id:
            raise ValueError("Glass temporal record requires a Glass identity.")
        if type(self.version) is not int:
            raise TypeError("Glass temporal record version must be an integer.")
        if self.version < 0:
            raise ValueError("Glass temporal record version cannot be negative.")
        if type(self.temporal_state) is not GlassTemporalState:
            raise TypeError("Glass temporal record requires the canonical state type.")
        if self.temporal_state.glass_id != self.glass_id:
            raise ValueError("Glass temporal record identity disagrees with state.")

    @classmethod
    def initial(cls, glass_id: str) -> GlassTemporalRecord:
        key = str(glass_id)
        return cls(key, 0, GlassTemporalState(key))


@dataclass(frozen=True)
class TemporalStoreState:
    records: Mapping[str, GlassTemporalRecord]
    epoch: int = 0

    def __post_init__(self) -> None:
        if type(self.epoch) is not int:
            raise TypeError("Temporal store epoch must be an integer.")
        if self.epoch < 0:
            raise ValueError("Temporal store epoch cannot be negative.")
        copied = dict(self.records)
        for key, record in copied.items():
            if not isinstance(key, str) or not key:
                raise ValueError("Temporal store requires non-empty Glass identities.")
            if type(record) is not GlassTemporalRecord:
                raise TypeError("Temporal store contains an unsupported record.")
            if key != record.glass_id or record.version < 1:
                raise ValueError("Temporal store record identity/version is invalid.")
        object.__setattr__(self, "records", MappingProxyType(copied))


@dataclass(frozen=True)
class TemporalAuditSnapshot:
    glass_id: str
    epoch: int
    version: int
    state: GlassTemporalState

    def __post_init__(self) -> None:
        if type(self.glass_id) is not str or not self.glass_id:
            raise ValueError("Temporal snapshot requires a Glass identity.")
        if type(self.epoch) is not int or type(self.version) is not int:
            raise TypeError("Temporal snapshot metadata must be integers.")
        if self.epoch < 0 or self.version < 0:
            raise ValueError("Temporal snapshot metadata cannot be negative.")
        if type(self.state) is not GlassTemporalState:
            raise TypeError("Temporal snapshot requires the canonical state type.")
        if self.state.glass_id != self.glass_id:
            raise ValueError("Temporal snapshot identity disagrees with state.")


@dataclass(frozen=True)
class CanonicalTemporalReduction:
    decision: ShadowTemporalDecision
    next_record: GlassTemporalRecord
    outcome: OilCanonicalOutcome
    tracker_action: CompatibilityTrackerAction
    smoothing_action: SmoothingAction
    resource_metrics: ShadowResourceSummary

    def __post_init__(self) -> None:
        if self.decision.tracker_action is not self.tracker_action:
            raise ValueError("Reduction tracker action disagrees with its decision.")
        if self.decision.smoothing_action is not self.smoothing_action:
            raise ValueError("Reduction smoothing action disagrees with its decision.")
        if self.outcome.tracker_action is not self.tracker_action:
            raise ValueError("Reduction tracker action disagrees with its outcome.")
        if self.outcome.smoothing_action is not self.smoothing_action:
            raise ValueError("Reduction smoothing action disagrees with its outcome.")
        if getattr(self.outcome, "resources", None) != self.resource_metrics:
            raise ValueError("Reduction resources disagree with its outcome.")


class TemporalReentryError(RuntimeError):
    """Raised when a public temporal operation re-enters its active owner command."""
