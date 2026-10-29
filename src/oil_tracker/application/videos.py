"""Videos opened for viewing frames, by id."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .ports import Frame, OpenVideo, Region, VideoInfo, VideoOpener


class UnknownVideo(LookupError):
    pass


@dataclass(frozen=True)
class OpenedVideo:
    id: str
    info: VideoInfo


class VideoSessions:
    def __init__(self, opener: VideoOpener, new_id: Callable[[], str]) -> None:
        self._opener = opener
        self._new_id = new_id
        self._videos: dict[str, OpenVideo] = {}
        self._paths: dict[str, Path] = {}
        self._lock = threading.Lock()

    def open(self, path: Path) -> OpenedVideo:
        video = self._opener(path)
        video_id = self._new_id()
        with self._lock:
            self._videos[video_id] = video
            self._paths[video_id] = path
        return OpenedVideo(video_id, video.info)

    def info(self, video_id: str) -> VideoInfo:
        return self._get(video_id).info

    def path(self, video_id: str) -> Path:
        self._get(video_id)
        with self._lock:
            return self._paths[video_id]

    def frame(
        self, video_id: str, time_sec: float, *, max_size: int | None = None, crop: Region | None = None
    ) -> Frame:
        return self._get(video_id).frame_at(time_sec, max_size=max_size, crop=crop)

    def close(self, video_id: str) -> None:
        with self._lock:
            video = self._videos.pop(video_id, None)
            self._paths.pop(video_id, None)
        if video is not None:
            video.close()

    def close_all(self) -> None:
        with self._lock:
            videos = list(self._videos.values())
            self._videos.clear()
            self._paths.clear()
        for video in videos:
            video.close()

    def _get(self, video_id: str) -> OpenVideo:
        with self._lock:
            video = self._videos.get(video_id)
        if video is None:
            raise UnknownVideo(f"열려 있지 않은 영상입니다: {video_id}")
        return video
