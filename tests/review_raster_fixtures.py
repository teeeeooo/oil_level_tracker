from __future__ import annotations

from PySide6.QtGui import QColor, QImage

from oil_tracker.adapters.presentation.qt_debug_artifact_presenter import QtDebugArtifactPresenter
from oil_tracker.adapters.presentation.qt_frame_image_converter import QtFrameImageConverter
from oil_tracker.adapters.presentation.review_frame_presenter import (
    ReviewFramePresenter,
    ReviewPresentedVideoReader,
)
from oil_tracker.adapters.storage.review_png_exporter import ReviewPngExporter
from oil_tracker.adapters.vision.review_debug_overlay_renderer import ReviewDebugOverlayRenderer
from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer


def review_presenter_factory() -> ReviewFramePresenter:
    return ReviewFramePresenter(
        ReviewOverlayRenderer(),
        ReviewDebugOverlayRenderer(),
        QtFrameImageConverter(),
    )


def presented_reader_factory(raw_reader_factory):
    def factory(path):
        return ReviewPresentedVideoReader(
            path,
            reader_factory=raw_reader_factory,
            presenter_factory=review_presenter_factory,
        )

    return factory


def debug_artifact_presenter() -> QtDebugArtifactPresenter:
    return QtDebugArtifactPresenter(QtFrameImageConverter())


def png_exporter() -> ReviewPngExporter:
    return ReviewPngExporter()


def solid_image(width: int, height: int, rgb=(12, 34, 56)) -> QImage:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(*rgb))
    return image
