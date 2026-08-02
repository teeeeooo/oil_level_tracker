from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable
from uuid import uuid4

import cv2

from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceRepository
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.adapters.vision.review_debug_overlay_renderer import ReviewDebugOverlayRenderer
from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer


class ReviewMp4ExportError(ValueError):
    """Base failure for a Result Review annotated MP4 export."""


class ReviewMp4DestinationError(ReviewMp4ExportError):
    pass


class ReviewMp4EncodingError(ReviewMp4ExportError):
    pass


class ReviewMp4ExportCancelled(ReviewMp4ExportError):
    pass


@dataclass(frozen=True)
class ReviewMp4ExportProgress:
    processed_frames: int
    estimated_total_frames: int
    timestamp_sec: float
    message: str = ""


@dataclass(frozen=True)
class ReviewMp4ExportResult:
    path: Path
    frame_count: int
    width: int
    height: int
    fps: float
    duration_sec: float
    analysis_start_sec: float
    analysis_end_sec: float
    include_debug: bool
    debug_frames: int


class ReviewMp4Exporter:
    """Render saved Result Review state over the analysis interval and publish atomically."""

    def __init__(
        self,
        *,
        reader_factory: Callable[[str | Path], object] = OpenCvVideoReader,
        writer_factory: Callable[[Path, float, tuple[int, int]], object] | None = None,
        general_renderer: ReviewOverlayRenderer | None = None,
        debug_renderer: ReviewDebugOverlayRenderer | None = None,
        debug_repository_factory=DebugTraceRepository,
        encoded_validator: Callable[[Path, int, int], None] | None = None,
        replacer: Callable[[str | os.PathLike, str | os.PathLike], None] = os.replace,
    ) -> None:
        self.reader_factory = reader_factory
        self.writer_factory = writer_factory or _OpenCvMp4Writer
        self.general_renderer = general_renderer or ReviewOverlayRenderer()
        self.debug_renderer = debug_renderer or ReviewDebugOverlayRenderer()
        self.debug_repository_factory = debug_repository_factory
        self.encoded_validator = encoded_validator or _validate_encoded_video
        self.replacer = replacer

    def export(
        self,
        *,
        bundle,
        query,
        source_video_path: str | Path,
        glass_id: str,
        destination: str | Path,
        include_debug: bool = False,
        cancellation=None,
        progress: Callable[[ReviewMp4ExportProgress], None] | None = None,
        overwrite: bool = False,
    ) -> ReviewMp4ExportResult:
        glass = bundle.glass_config(glass_id)
        if glass is None:
            raise ReviewMp4ExportError(f"결과 bundle에 없는 Glass입니다: {glass_id}")
        path = _prepare_destination(destination, bundle.root, source_video_path, overwrite)
        temporary = path.parent / f".{path.stem}.tmp-{uuid4().hex}.mp4"
        reader = writer = debug_repository = None
        published = False
        frame_count = 0
        debug_frames = 0
        try:
            _check_cancelled(cancellation)
            reader = self.reader_factory(source_video_path)
            metadata = reader.metadata
            width, height = int(metadata.width), int(metadata.height)
            fps = float(metadata.fps or 0.0)
            if width <= 0 or height <= 0 or fps <= 0:
                raise ReviewMp4EncodingError("원본 영상의 frame size 또는 FPS를 확인할 수 없습니다.")
            if (width, height) != (
                int(bundle.recipe.reference_frame_width),
                int(bundle.recipe.reference_frame_height),
            ):
                raise ReviewMp4EncodingError("분석 snapshot과 원본 영상의 해상도가 일치하지 않습니다.")
            writer = self.writer_factory(temporary, fps, (width, height))
            if include_debug and bundle.has_debug_trace:
                debug_repository = self.debug_repository_factory(bundle)
            start = float(bundle.analysis_start_sec)
            end = float(bundle.analysis_end_sec)
            estimated = max(1, int(round(max(0.0, end - start) * fps)) + 1)
            frame, frame_index, actual_timestamp = reader.read_at(start)
            previous_identity = None
            while True:
                _check_cancelled(cancellation)
                actual_timestamp = float(actual_timestamp)
                frame_index = int(frame_index)
                identity = (frame_index, actual_timestamp)
                if previous_identity == identity:
                    raise ReviewMp4EncodingError("원본 영상 reader가 동일 frame에서 진행하지 못했습니다.")
                previous_identity = identity
                if actual_timestamp > end + 1e-9:
                    break
                if actual_timestamp >= start - 1e-9:
                    overlay = query.overlay_at(glass_id, actual_timestamp)
                    rendered = self.general_renderer.render(frame, glass, overlay)
                    if include_debug:
                        record = _debug_record_for_frame(
                            debug_repository,
                            glass_id,
                            frame_index,
                            actual_timestamp,
                            fps,
                        )
                        rendered = self.debug_renderer.render_export(
                            rendered,
                            glass,
                            record,
                            actual_timestamp,
                        )
                        debug_frames += int(record is not None)
                    writer.write(rendered)
                    frame_count += 1
                    if progress is not None:
                        progress(
                            ReviewMp4ExportProgress(
                                frame_count,
                                estimated,
                                actual_timestamp,
                                f"{glass.name} annotated MP4 encoding",
                            )
                        )
                if metadata.frame_count > 0 and frame_index >= int(metadata.frame_count) - 1:
                    break
                try:
                    frame, frame_index, actual_timestamp = reader.read_next()
                except EOFError:
                    break
            _check_cancelled(cancellation)
            if frame_count <= 0:
                raise ReviewMp4EncodingError("분석 구간에서 내보낼 video frame을 찾지 못했습니다.")
            writer.close()
            writer = None
            self.encoded_validator(temporary, width, height)
            _check_cancelled(cancellation)
            if path.exists() and not overwrite:
                raise ReviewMp4DestinationError(f"기존 MP4 파일을 덮어쓸 수 없습니다: {path}")
            self.replacer(temporary, path)
            published = True
            return ReviewMp4ExportResult(
                path=path,
                frame_count=frame_count,
                width=width,
                height=height,
                fps=fps,
                duration_sec=frame_count / fps,
                analysis_start_sec=start,
                analysis_end_sec=end,
                include_debug=bool(include_debug),
                debug_frames=debug_frames,
            )
        finally:
            if writer is not None:
                writer.close()
            if reader is not None:
                reader.close()
            if debug_repository is not None:
                debug_repository.close()
            if not published:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass


def _prepare_destination(
    destination: str | Path,
    bundle_root: str | Path,
    source_video_path: str | Path,
    overwrite: bool,
) -> Path:
    path = Path(destination).expanduser()
    if path.suffix.lower() != ".mp4":
        path = path.with_suffix(".mp4")
    if not path.name or path.name in {".", ".."}:
        raise ReviewMp4DestinationError("MP4 destination 파일명이 올바르지 않습니다.")
    try:
        root = Path(bundle_root).expanduser().resolve(strict=True)
        source = Path(source_video_path).expanduser().resolve(strict=True)
        preflight = path.resolve(strict=False)
    except OSError as exc:
        raise ReviewMp4DestinationError(f"MP4 destination 경로를 확인할 수 없습니다: {exc}") from exc
    _ensure_unprotected_destination(preflight, root, source)
    if path.is_symlink():
        raise ReviewMp4DestinationError("symbolic link MP4 destination에는 저장할 수 없습니다.")
    if preflight.exists() and not overwrite:
        raise ReviewMp4DestinationError(f"기존 MP4 파일을 덮어쓸 수 없습니다: {preflight}")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        resolved_parent = path.parent.resolve(strict=True)
    except OSError as exc:
        raise ReviewMp4DestinationError(f"MP4 저장 폴더를 준비할 수 없습니다: {exc}") from exc
    resolved = resolved_parent / path.name
    _ensure_unprotected_destination(resolved, root, source)
    if resolved.is_symlink():
        raise ReviewMp4DestinationError("symbolic link MP4 destination에는 저장할 수 없습니다.")
    if resolved.exists() and not overwrite:
        raise ReviewMp4DestinationError(f"기존 MP4 파일을 덮어쓸 수 없습니다: {resolved}")
    return resolved


def _ensure_unprotected_destination(destination: Path, root: Path, source: Path) -> None:
    if destination == root or root in destination.parents:
        raise ReviewMp4DestinationError("annotated MP4는 공식 결과 bundle 내부에 저장할 수 없습니다.")
    if destination == source:
        raise ReviewMp4DestinationError("원본 source MP4를 annotated export destination으로 사용할 수 없습니다.")


def _debug_record_for_frame(
    repository,
    glass_id: str,
    frame_index: int,
    timestamp_sec: float,
    fps: float,
):
    if repository is None:
        return None
    tolerance = max(1e-6, 0.55 / max(1e-6, fps))
    matches = tuple(
        summary
        for summary in repository.summaries(glass_id)
        if int(summary.frame_index) == int(frame_index)
        and abs(float(summary.timestamp_sec) - float(timestamp_sec)) <= tolerance
    )
    if not matches:
        return None
    summary = min(
        matches,
        key=lambda item: (
            abs(float(item.timestamp_sec) - float(timestamp_sec)),
            item.record_id,
        ),
    )
    return repository.load_record(summary.record_id)


def _check_cancelled(cancellation) -> None:
    if cancellation is not None and bool(getattr(cancellation, "cancelled", False)):
        raise ReviewMp4ExportCancelled("Annotated MP4 export was cancelled.")


def _validate_encoded_video(path: Path, width: int, height: int) -> None:
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ReviewMp4EncodingError("완성된 임시 MP4를 다시 열 수 없습니다.")
        encoded_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        encoded_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        encoded_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if (encoded_width, encoded_height) != (width, height):
            raise ReviewMp4EncodingError("완성된 MP4의 frame geometry가 원본과 다릅니다.")
        if encoded_frames <= 0:
            raise ReviewMp4EncodingError("완성된 MP4에 video frame이 없습니다.")
        ok, frame = capture.read()
        if not ok or frame is None:
            raise ReviewMp4EncodingError("완성된 MP4의 첫 frame을 decode할 수 없습니다.")
    finally:
        capture.release()


class _OpenCvMp4Writer:
    def __init__(self, path: Path, fps: float, frame_size: tuple[int, int]) -> None:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self._writer = cv2.VideoWriter(str(path), fourcc, float(fps), tuple(frame_size))
        self._frame_size = tuple(frame_size)
        if not self._writer.isOpened():
            self._writer.release()
            raise ReviewMp4EncodingError("OpenCV MP4 video writer를 열 수 없습니다.")

    def write(self, frame) -> None:
        height, width = frame.shape[:2]
        if (width, height) != self._frame_size:
            raise ReviewMp4EncodingError("renderer가 원본과 다른 frame geometry를 반환했습니다.")
        self._writer.write(frame)

    def close(self) -> None:
        writer, self._writer = self._writer, None
        if writer is not None:
            writer.release()
