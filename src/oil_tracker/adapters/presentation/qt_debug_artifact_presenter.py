from __future__ import annotations

from PySide6.QtGui import QImage

from oil_tracker.adapters.presentation.qt_frame_image_converter import (
    FrameImageConversionError,
    QtFrameImageConverter,
)


class DebugArtifactPresentationError(ValueError):
    """A stored detector artifact cannot cross the Qt presentation boundary."""


class QtDebugArtifactPresenter:
    def __init__(self, converter: QtFrameImageConverter) -> None:
        self.converter = converter

    def present(self, repository, record, image_key: str) -> QImage | None:
        image = repository.load_image(record, image_key)
        if image is None:
            return None
        try:
            return self.converter.to_qimage(image)
        except (FrameImageConversionError, TypeError, ValueError) as exc:
            raise DebugArtifactPresentationError(
                f"debug artifact 이미지를 표시할 수 없습니다: {image_key}"
            ) from exc
