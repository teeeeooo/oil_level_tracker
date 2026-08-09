from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from oil_tracker.domain.session import VideoMetadata


class VideoReader(Protocol):
    @property
    def metadata(self) -> VideoMetadata: ...
    def read_at(self, timestamp_sec: float) -> tuple[Any, int, float]: ...
    def close(self) -> None: ...


class VideoReaderFactory(Protocol):
    def __call__(self, path: str | Path) -> VideoReader: ...
