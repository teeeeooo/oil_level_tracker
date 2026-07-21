from __future__ import annotations

import gc
from types import SimpleNamespace

import numpy as np
import pytest
from PySide6.QtGui import QImage

from oil_tracker.adapters.presentation.qt_frame_image_converter import QtFrameImageConverter
from oil_tracker.adapters.presentation.review_frame_presenter import (
    ReviewFramePresenter,
    ReviewPresentedVideoReader,
    ReviewRasterPresentationError,
)
from oil_tracker.adapters.vision.review_debug_overlay_renderer import ReviewDebugOverlayRenderer
from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewOverlayData
from oil_tracker.domain.session import VideoMetadata


def _presenter():
    return ReviewFramePresenter(
        ReviewOverlayRenderer(),
        ReviewDebugOverlayRenderer(),
        QtFrameImageConverter(),
    )


def _glass():
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.geometry.zero_line_y = 140.0
    return glass


def _overlay(glass):
    return ReviewOverlayData(
        glass_id=glass.id,
        video_timestamp_sec=1.0,
        sample=None,
        oil_boundary_y=None,
        foam_front_y=None,
        within_analysis_range=True,
        review_reasons=(),
    )


def _record():
    return SimpleNamespace(
        timestamp_sec=1.0,
        candidates=(
            {
                "canonical_y": 120.0,
                "rank": 1,
                "kind": "oil_air",
                "selected": True,
                "rejected": False,
                "final_score": 0.8,
            },
        ),
    )


def test_accept_source_frame_returns_detached_image_and_keeps_adapter_owned_copy():
    presenter = _presenter()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[4, 5] = (10, 20, 30)
    image = presenter.accept_source_frame(frame)
    frame[4, 5] = (90, 100, 110)
    del frame
    gc.collect()
    color = image.pixelColor(5, 4)
    assert (color.red(), color.green(), color.blue()) == (30, 20, 10)
    assert presenter.has_frame
    source = presenter.source_image
    source.setPixelColor(5, 4, source.pixelColor(0, 0))
    retained = presenter.source_image.pixelColor(5, 4)
    assert (retained.red(), retained.green(), retained.blue()) == (30, 20, 10)


def test_general_and_debug_render_return_detached_original_resolution_images():
    presenter = _presenter()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    presenter.accept_source_frame(frame)
    glass = _glass()
    general = presenter.render_general(glass, _overlay(glass))
    debug = presenter.render_debug(glass, _record(), 1.012, highlighted_candidate=0)
    assert isinstance(general, QImage)
    assert isinstance(debug, QImage)
    assert (general.width(), general.height()) == (320, 240)
    assert (debug.width(), debug.height()) == (320, 240)
    assert general != debug
    debug.fill(0)
    rerendered = presenter.render_debug(glass, _record(), 1.012, highlighted_candidate=0)
    assert not rerendered.isNull()
    assert rerendered.pixelColor(160, 120).alpha() == 255


def test_render_requires_an_owned_source_frame():
    presenter = _presenter()
    with pytest.raises(ReviewRasterPresentationError, match="원본 영상 장면"):
        presenter.render_general(_glass(), _overlay(_glass()))


def test_invalid_source_frame_is_translated_to_presentation_error():
    presenter = _presenter()
    with pytest.raises(ReviewRasterPresentationError, match="numpy.ndarray"):
        presenter.accept_source_frame(object())


class _RawReader:
    instances = []

    def __init__(self, path):
        self.path = str(path)
        self.metadata = VideoMetadata(self.path, 320, 240, 10.0, 5.0, 50, "fake")
        self.closed = False
        self.__class__.instances.append(self)

    def read_at(self, timestamp):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame[:, :, 1] = 25
        return frame, 12, float(timestamp) + 0.01

    def close(self):
        self.closed = True


def test_presented_reader_never_returns_raw_array_and_releases_resources():
    reader = ReviewPresentedVideoReader(
        "source.mp4",
        reader_factory=_RawReader,
        presenter_factory=_presenter,
    )
    image, frame_index, actual = reader.read_at(1.0)
    assert isinstance(image, QImage)
    assert (image.width(), image.height()) == (320, 240)
    assert frame_index == 12
    assert actual == pytest.approx(1.01)
    source = reader.source_image
    assert isinstance(source, QImage) and not source.isNull()
    raw = reader._reader
    reader.close()
    assert raw.closed
    assert reader.source_image.isNull()
    reader.close()
