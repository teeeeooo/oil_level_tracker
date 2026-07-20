from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProgressUpdate:
    completed: int
    total: int
    timestamp_sec: float
    glass_name: str
    rate_fps: float


class ProgressSink(Protocol):
    def __call__(self, update: ProgressUpdate) -> None: ...


class CancellationToken(Protocol):
    @property
    def cancelled(self) -> bool: ...
