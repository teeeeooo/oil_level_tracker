from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ResultReviewCanvas(QWidget):
    """Read-only full-resolution image viewport with no raster processing responsibility."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("resultReviewCanvas")
        self.label = QLabel("결과 bundle을 열어 주세요.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumSize(640, 420)
        self.label.setStyleSheet("background:#141619; color:#d9dde3;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self._image = QImage()
        self._pixmap = QPixmap()

    @property
    def source_image_size(self) -> QSize:
        return self._image.size()

    def image(self) -> QImage:
        return QImage(self._image).copy()

    def set_image(self, image: QImage | None) -> None:
        if image is None or image.isNull():
            self.set_message("표시할 원본 영상 장면이 없습니다.")
            return
        self._image = QImage(image).copy()
        self._pixmap = QPixmap.fromImage(self._image)
        self.label.setText("")
        self._refresh_pixmap()

    def set_message(self, message: str) -> None:
        self._image = QImage()
        self._pixmap = QPixmap()
        self.label.setPixmap(QPixmap())
        self.label.setText(str(message))

    def _refresh_pixmap(self) -> None:
        if self._pixmap.isNull():
            return
        target = self.label.size()
        self.label.setText("")
        self.label.setPixmap(
            self._pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_pixmap()

    def closeEvent(self, event) -> None:
        self._image = QImage()
        self._pixmap = QPixmap()
        self.label.setPixmap(QPixmap())
        super().closeEvent(event)
