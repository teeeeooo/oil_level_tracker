from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.ports.review_io import (
    SourceVideoError,
    SourceVideoMismatchError,
)
from oil_tracker.domain.review import ReviewBundle
from oil_tracker.domain.session import VideoMetadata


@dataclass(frozen=True)
class SourceVideoResolution:
    path: Path | None
    attempted_paths: tuple[Path, ...]
    original_path: str
    used_override: bool = False


@dataclass(frozen=True)
class SourceVideoValidation:
    path: Path
    metadata: VideoMetadata
    warnings: tuple[str, ...] = ()


class SourceVideoResolver:
    def __init__(self, reader_factory: Callable[[str | Path], object] = OpenCvVideoReader) -> None:
        self.reader_factory = reader_factory

    def resolve(self, bundle: ReviewBundle, override: str | Path | None = None) -> SourceVideoResolution:
        attempted: list[Path] = []
        if override not in (None, ""):
            candidate = Path(override).expanduser()
            attempted.append(candidate)
            if candidate.is_file():
                return SourceVideoResolution(candidate.resolve(), tuple(attempted), bundle.source_video_path, True)

        for raw in bundle.source_video_candidates:
            candidate = Path(raw).expanduser()
            candidates = [candidate] if candidate.is_absolute() else [bundle.root / candidate]
            for path in candidates:
                if path not in attempted:
                    attempted.append(path)
                if path.is_file():
                    return SourceVideoResolution(path.resolve(), tuple(attempted), bundle.source_video_path, False)

        basename = self._source_basename(bundle)
        if basename:
            for directory in (bundle.root, bundle.root.parent):
                candidate = directory / basename
                if candidate not in attempted:
                    attempted.append(candidate)
                if candidate.is_file():
                    return SourceVideoResolution(candidate.resolve(), tuple(attempted), bundle.source_video_path, False)
        return SourceVideoResolution(None, tuple(attempted), bundle.source_video_path, False)

    def validate_candidate(self, bundle: ReviewBundle, path: str | Path) -> SourceVideoValidation:
        candidate = Path(path).expanduser()
        if not candidate.is_file():
            raise SourceVideoError(f"선택한 원본 영상이 존재하지 않습니다: {candidate}")
        reader = None
        try:
            reader = self.reader_factory(candidate)
            metadata = reader.metadata
        except Exception as exc:
            raise SourceVideoError(f"원본 영상을 열 수 없습니다: {exc}") from exc
        finally:
            if reader is not None:
                reader.close()

        expected = bundle.source_metadata
        expected_width = expected.width if expected and expected.width > 0 else bundle.recipe.reference_frame_width
        expected_height = expected.height if expected and expected.height > 0 else bundle.recipe.reference_frame_height
        if metadata.width != expected_width or metadata.height != expected_height:
            raise SourceVideoMismatchError(
                "선택한 영상의 해상도가 분석 당시 영상과 다릅니다.\n"
                f"분석 당시: {expected_width}×{expected_height}\n"
                f"선택 영상: {metadata.width}×{metadata.height}\n"
                "좌표가 어긋날 수 있으므로 동일 해상도의 영상을 선택해 주세요."
            )

        warnings: list[str] = []
        if expected is not None:
            if expected.fps > 0 and metadata.fps > 0 and abs(expected.fps - metadata.fps) > max(0.05, expected.fps * 0.01):
                warnings.append(f"FPS 차이: 분석 당시 {expected.fps:.3f}, 선택 영상 {metadata.fps:.3f}")
            if expected.duration_sec > 0 and metadata.duration_sec > 0 and abs(expected.duration_sec - metadata.duration_sec) > max(0.25, expected.duration_sec * 0.01):
                warnings.append(
                    f"재생 시간 차이: 분석 당시 {expected.duration_sec:.3f}초, 선택 영상 {metadata.duration_sec:.3f}초"
                )
            if expected.codec and metadata.codec and expected.codec != metadata.codec:
                warnings.append(f"codec 차이: 분석 당시 {expected.codec}, 선택 영상 {metadata.codec}")
        return SourceVideoValidation(candidate.resolve(), metadata, tuple(warnings))

    def _source_basename(self, bundle: ReviewBundle) -> str:
        for raw in bundle.source_video_candidates:
            name = Path(raw).name
            if name:
                return name
        return Path(bundle.source_video_path).name if bundle.source_video_path else ""
