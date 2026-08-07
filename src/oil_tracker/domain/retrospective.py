from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .enums import FillState, InitialObservationState


class RetrospectiveStatus(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ACCEPTED = "ACCEPTED"
    UNRESOLVED = "UNRESOLVED"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class RetrospectiveInterpretation:
    glass_id: str
    status: RetrospectiveStatus
    confirmed_prior: InitialObservationState | None = None
    interpreted_state: FillState | None = None
    start_time_sec: float | None = None
    end_time_sec: float | None = None
    start_frame_index: int | None = None
    end_frame_index: int | None = None
    evidence_frame_indices: tuple[int, ...] = ()
    evidence_timestamps_sec: tuple[float, ...] = ()
    evidence_relative_positions: tuple[float, ...] = ()
    barriers: tuple[str, ...] = ()
    reason: str = ""
    provenance: str = "initial_state_retrospective_v1"

    @property
    def accepted(self) -> bool:
        return self.status is RetrospectiveStatus.ACCEPTED

    @property
    def conflict(self) -> bool:
        return self.status is RetrospectiveStatus.CONFLICT

    def contains(self, timestamp_sec: float) -> bool:
        return (
            self.accepted
            and self.start_time_sec is not None
            and self.end_time_sec is not None
            and self.start_time_sec - 1e-9 <= timestamp_sec <= self.end_time_sec + 1e-9
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "glass_id": self.glass_id,
            "status": self.status.value,
            "confirmed_prior": self.confirmed_prior.value if self.confirmed_prior else None,
            "interpreted_state": self.interpreted_state.value if self.interpreted_state else None,
            "interval": [self.start_time_sec, self.end_time_sec],
            "frame_interval": [self.start_frame_index, self.end_frame_index],
            "evidence_frame_indices": list(self.evidence_frame_indices),
            "evidence_timestamps_sec": list(self.evidence_timestamps_sec),
            "evidence_relative_positions": list(self.evidence_relative_positions),
            "barriers": list(self.barriers),
            "reason": self.reason,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetrospectiveInterpretation":
        interval = data.get("interval") or [None, None]
        frame_interval = data.get("frame_interval") or [None, None]
        return cls(
            glass_id=str(data.get("glass_id", "")),
            status=RetrospectiveStatus(str(data.get("status"))),
            confirmed_prior=_optional_enum(data.get("confirmed_prior"), InitialObservationState),
            interpreted_state=_optional_enum(data.get("interpreted_state"), FillState),
            start_time_sec=_optional_float(interval[0] if len(interval) > 0 else None),
            end_time_sec=_optional_float(interval[1] if len(interval) > 1 else None),
            start_frame_index=_optional_int(frame_interval[0] if len(frame_interval) > 0 else None),
            end_frame_index=_optional_int(frame_interval[1] if len(frame_interval) > 1 else None),
            evidence_frame_indices=tuple(int(value) for value in data.get("evidence_frame_indices", ())),
            evidence_timestamps_sec=tuple(float(value) for value in data.get("evidence_timestamps_sec", ())),
            evidence_relative_positions=tuple(float(value) for value in data.get("evidence_relative_positions", ())),
            barriers=tuple(str(value) for value in data.get("barriers", ())),
            reason=str(data.get("reason", "")),
            provenance=str(data.get("provenance", "initial_state_retrospective_v1")),
        )


def _optional_enum(value, enum_type):
    return None if value in (None, "") else enum_type(str(value))


def _optional_float(value):
    return None if value is None else float(value)


def _optional_int(value):
    return None if value is None else int(value)
