from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
from PySide6.QtGui import QImage

from oil_tracker.adapters.presentation.qt_frame_image_converter import (
    FrameImageConversionError,
    QtFrameImageConverter,
)
from oil_tracker.adapters.vision.review_debug_overlay_renderer import ReviewDebugOverlayRenderer
from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer


class ReviewRasterPresentationError(ValueError):
    """A decoded or rendered frame cannot cross the Result Review Qt boundary."""


class ReviewFramePresenter:
    """Own one decoded raster and expose only detached Qt image snapshots."""

    def __init__(
        self,
        general_renderer: ReviewOverlayRenderer,
        debug_renderer: ReviewDebugOverlayRenderer,
        converter: QtFrameImageConverter,
    ) -> None:
        self.general_renderer = general_renderer
        self.debug_renderer = debug_renderer
        self.converter = converter
        self._source_frame: np.ndarray | None = None
        self._source_image = QImage()

    @property
    def has_frame(self) -> bool:
        return self._source_frame is not None and not self._source_image.isNull()

    @property
    def source_image(self) -> QImage:
        return QImage(self._source_image).copy()

    def accept_source_frame(self, frame) -> QImage:
        try:
            source_image = self.converter.to_qimage(frame)
        except (FrameImageConversionError, TypeError, ValueError) as exc:
            raise ReviewRasterPresentationError(str(exc)) from exc
        self._source_frame = np.ascontiguousarray(frame.copy())
        self._source_image = QImage(source_image).copy()
        return self.source_image

    def render_general(self, glass, overlay) -> QImage:
        frame = self._require_frame()
        try:
            rendered = self.general_renderer.render(frame, glass, overlay)
            return self.converter.to_qimage(rendered)
        except Exception as exc:
            if isinstance(exc, ReviewRasterPresentationError):
                raise
            raise ReviewRasterPresentationError(f"일반 overlay 장면을 만들 수 없습니다: {exc}") from exc

    def render_debug(
        self,
        glass,
        record,
        actual_timestamp: float,
        highlighted_candidate: int | None = None,
    ) -> QImage:
        frame = self._require_frame()
        try:
            rendered = self.debug_renderer.render(
                frame,
                glass,
                record,
                actual_timestamp,
                highlighted_candidate,
            )
            return self.converter.to_qimage(rendered)
        except Exception as exc:
            if isinstance(exc, ReviewRasterPresentationError):
                raise
            raise ReviewRasterPresentationError(f"디버그 overlay 장면을 만들 수 없습니다: {exc}") from exc

    def clear(self) -> None:
        self._source_frame = None
        self._source_image = QImage()

    def _require_frame(self) -> np.ndarray:
        if self._source_frame is None:
            raise ReviewRasterPresentationError("표시할 원본 영상 장면이 없습니다.")
        return self._source_frame


class ReviewPresentedVideoReader:
    """Wrap a decoded-frame reader and retain raster ownership outside the UI package."""

    def __init__(
        self,
        path: str | Path,
        *,
        reader_factory: Callable[[str | Path], object],
        presenter_factory: Callable[[], ReviewFramePresenter],
    ) -> None:
        self._reader = reader_factory(path)
        self._presenter = presenter_factory()
        self._closed = False

    @property
    def metadata(self):
        return self._reader.metadata

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def source_image(self) -> QImage:
        return self._presenter.source_image

    def read_at(self, timestamp_sec: float) -> tuple[QImage, int, float]:
        if self._closed:
            raise RuntimeError("이미 닫힌 Result Review video reader입니다.")
        frame, frame_index, actual_timestamp = self._reader.read_at(timestamp_sec)
        image = self._presenter.accept_source_frame(frame)
        return image, int(frame_index), float(actual_timestamp)

    def render_general(self, glass, overlay) -> QImage:
        return self._presenter.render_general(glass, overlay)

    def render_debug(
        self,
        glass,
        record,
        actual_timestamp: float,
        highlighted_candidate: int | None = None,
    ) -> QImage:
        return self._presenter.render_debug(
            glass,
            record,
            actual_timestamp,
            highlighted_candidate,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._reader.close()
        finally:
            self._presenter.clear()
