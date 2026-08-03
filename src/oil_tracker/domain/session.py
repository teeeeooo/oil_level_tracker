from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class DebugTraceLevel(str, Enum):
    NONE = "none"
    BASIC = "basic"
    FULL = "full"

    def __str__(self) -> str:
        return self.value


@dataclass
class VideoMetadata:
    path: str
    width: int
    height: int
    fps: float
    duration_sec: float
    frame_count: int
    codec: str = ""
    timestamp_reliability_warning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VideoMetadata":
        return cls(
            path=str(data.get("path", "")),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            fps=float(data.get("fps", 0.0)),
            duration_sec=float(data.get("duration_sec", 0.0)),
            frame_count=int(data.get("frame_count", 0)),
            codec=str(data.get("codec", "")),
            timestamp_reliability_warning=str(data.get("timestamp_reliability_warning", "")),
        )


@dataclass
class AnalysisSession:
    input_video_path: str = ""
    video_metadata: VideoMetadata | None = None
    analysis_start_sec: float = 0.0
    analysis_end_sec: float | None = None
    compressor_start_sec: float | None = None
    sampling_fps: float = 2.0
    output_directory: str = ""
    run_name: str = ""
    run_note: str = ""
    resolution_confirmed: bool = True
    debug_trace_level: DebugTraceLevel = DebugTraceLevel.BASIC

    def effective_end_sec(self) -> float | None:
        if self.analysis_end_sec is not None:
            return self.analysis_end_sec
        return self.video_metadata.duration_sec if self.video_metadata else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_video_path": self.input_video_path,
            "video_metadata": self.video_metadata.to_dict() if self.video_metadata else None,
            "analysis_start_sec": self.analysis_start_sec,
            "analysis_end_sec": self.analysis_end_sec,
            "compressor_start_sec": self.compressor_start_sec,
            "sampling_fps": self.sampling_fps,
            "output_directory": self.output_directory,
            "run_name": self.run_name,
            "run_note": self.run_note,
            "resolution_confirmed": self.resolution_confirmed,
            "debug_trace_level": self.debug_trace_level.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisSession":
        metadata = data.get("video_metadata")
        raw_level = data.get("debug_trace_level")
        try:
            level = DebugTraceLevel.NONE if raw_level is None else DebugTraceLevel(str(raw_level))
        except ValueError as exc:
            raise ValueError(f"Invalid debug_trace_level: {raw_level!r}") from exc
        return cls(
            input_video_path=str(data.get("input_video_path", "")),
            video_metadata=VideoMetadata.from_dict(metadata) if isinstance(metadata, dict) else None,
            analysis_start_sec=float(data.get("analysis_start_sec", 0.0)),
            analysis_end_sec=_optional_float(data.get("analysis_end_sec")),
            compressor_start_sec=_optional_float(data.get("compressor_start_sec")),
            sampling_fps=float(data.get("sampling_fps", 2.0)),
            output_directory=str(data.get("output_directory", "")),
            run_name=str(data.get("run_name", "")),
            run_note=str(data.get("run_note", "")),
            resolution_confirmed=_parse_bool(data.get("resolution_confirmed", True)),
            debug_trace_level=level,
        )


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")
