from __future__ import annotations

import numpy as np
import pytest

from oil_tracker.adapters.presentation.qt_frame_image_converter import (
    FrameImageConversionError,
    QtFrameImageConverter,
)


@pytest.fixture
def converter() -> QtFrameImageConverter:
    return QtFrameImageConverter()


def test_grayscale_uint8_preserves_size_and_value(converter):
    frame = np.array([[0, 17, 255], [4, 5, 6]], dtype=np.uint8)
    image = converter.to_qimage(frame)
    assert (image.width(), image.height()) == (3, 2)
    color = image.pixelColor(1, 0)
    assert (color.red(), color.green(), color.blue()) == (17, 17, 17)


def test_bgr_uint8_becomes_rgb(converter):
    frame = np.array([[[10, 20, 30], [1, 2, 3]]], dtype=np.uint8)
    image = converter.to_qimage(frame)
    assert (image.width(), image.height()) == (2, 1)
    color = image.pixelColor(0, 0)
    assert (color.red(), color.green(), color.blue(), color.alpha()) == (30, 20, 10, 255)


def test_bgra_uint8_becomes_rgba(converter):
    frame = np.array([[[10, 20, 30, 40]]], dtype=np.uint8)
    image = converter.to_qimage(frame)
    color = image.pixelColor(0, 0)
    assert (color.red(), color.green(), color.blue(), color.alpha()) == (30, 20, 10, 40)


def test_non_contiguous_source_is_supported(converter):
    base = np.zeros((3, 8, 3), dtype=np.uint8)
    base[1, 4] = (11, 22, 33)
    frame = base[:, ::2, :]
    assert not frame.flags.c_contiguous
    image = converter.to_qimage(frame)
    assert (image.width(), image.height()) == (4, 3)
    color = image.pixelColor(2, 1)
    assert (color.red(), color.green(), color.blue()) == (33, 22, 11)


def test_returned_qimage_is_detached_from_source_mutation(converter):
    frame = np.array([[[10, 20, 30]]], dtype=np.uint8)
    image = converter.to_qimage(frame)
    frame[0, 0] = (90, 100, 110)
    color = image.pixelColor(0, 0)
    assert (color.red(), color.green(), color.blue()) == (30, 20, 10)


@pytest.mark.parametrize(
    ("frame", "message"),
    [
        (np.zeros((0, 3, 3), dtype=np.uint8), "비어 있는"),
        (np.zeros((3,), dtype=np.uint8), "차원"),
        (np.zeros((2, 2, 2), dtype=np.uint8), "channel"),
        (np.zeros((2, 2, 3), dtype=np.float32), "dtype"),
        (object(), "numpy.ndarray"),
    ],
)
def test_invalid_frames_are_rejected_with_explicit_contract(converter, frame, message):
    with pytest.raises(FrameImageConversionError, match=message):
        converter.to_qimage(frame)
