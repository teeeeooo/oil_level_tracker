from __future__ import annotations

from typing import Any, Protocol

from oil_tracker.domain.session import VideoMetadata


class VideoReader(Protocol):
    @property
    def metadata(self) -> VideoMetadata: ...
    def read_at(self, timestamp_sec: float) -> tuple[Any, int, float]: ...
    def close(self) -> None: ...
