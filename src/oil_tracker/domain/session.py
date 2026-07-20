from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


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


@dataclass
class AnalysisSession:
    input_video_path: str = ""
    video_metadata: VideoMetadata | None = None
    analysis_start_sec: float = 0.0
    analysis_end_sec: float | None = None
    compressor_start_sec: float | None = None
    sampling_fps: float = 2.0
    output_directory: str = ""
    run_note: str = ""
    resolution_confirmed: bool = True

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
            "run_note": self.run_note,
            "resolution_confirmed": self.resolution_confirmed,
        }
