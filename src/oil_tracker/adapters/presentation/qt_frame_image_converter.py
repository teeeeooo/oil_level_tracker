from __future__ import annotations

import numpy as np
from PySide6.QtGui import QImage


class FrameImageConversionError(ValueError):
    """Raised when a decoded video frame cannot cross the Qt presentation boundary."""


class QtFrameImageConverter:
    """Convert uint8 OpenCV/NumPy frames into detached Qt image snapshots."""

    def to_qimage(self, frame) -> QImage:
        if not isinstance(frame, np.ndarray):
            raise FrameImageConversionError("frame은 numpy.ndarray여야 합니다.")
        if frame.dtype != np.uint8:
            raise FrameImageConversionError(
                f"지원하지 않는 frame dtype입니다: {frame.dtype}; uint8만 지원합니다."
            )
        if frame.size == 0 or any(int(length) == 0 for length in frame.shape):
            raise FrameImageConversionError("비어 있는 frame은 변환할 수 없습니다.")

        if frame.ndim == 2:
            array = np.ascontiguousarray(frame)
            image_format = QImage.Format.Format_Grayscale8
        elif frame.ndim == 3:
            channels = int(frame.shape[2])
            if channels == 3:
                array = np.ascontiguousarray(frame[:, :, ::-1])
                image_format = QImage.Format.Format_RGB888
            elif channels == 4:
                array = frame[:, :, [2, 1, 0, 3]].copy(order="C")
                image_format = QImage.Format.Format_RGBA8888
            else:
                raise FrameImageConversionError(
                    f"지원하지 않는 frame channel 수입니다: {channels}; 3 또는 4만 지원합니다."
                )
        else:
            raise FrameImageConversionError(
                f"지원하지 않는 frame 차원입니다: {frame.ndim}; 2D 또는 3D만 지원합니다."
            )

        height, width = int(array.shape[0]), int(array.shape[1])
        image = QImage(
            array.data,
            width,
            height,
            int(array.strides[0]),
            image_format,
        )
        if image.isNull():
            raise FrameImageConversionError("Qt image snapshot 생성에 실패했습니다.")
        return image.copy()


def blank_bgr_frame(width: int, height: int):
    """Create the uint8 BGR placeholder used before a video frame is decoded."""

    width = int(width)
    height = int(height)
    if width <= 0 or height <= 0:
        raise ValueError("placeholder frame 크기는 양수여야 합니다.")
    return np.zeros((height, width, 3), dtype=np.uint8)
