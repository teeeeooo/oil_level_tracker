from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer


class ResultReviewCanvas(QWidget):
    """Read-only canvas. It exposes no geometry mutation or drag signals."""

    def __init__(self, renderer: ReviewOverlayRenderer | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("resultReviewCanvas")
        self.renderer = renderer or ReviewOverlayRenderer()
        self.label = QLabel("결과 bundle을 열어 주세요.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumSize(640, 420)
        self.label.setStyleSheet("background:#141619; color:#d9dde3;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self._frame: np.ndarray | None = None
        self._rendered: np.ndarray | None = None
        self._glass = None
        self._overlay = None

    def set_message(self, message: str) -> None:
        self._frame = None
        self._rendered = None
        self._glass = None
        self._overlay = None
        self.label.setPixmap(QPixmap())
        self.label.setText(message)

    def set_review_frame(self, frame: np.ndarray, glass, overlay) -> None:
        self._frame = np.ascontiguousarray(frame.copy())
        self._glass = glass
        self._overlay = overlay
        self._rendered = self.renderer.render(self._frame, glass, overlay)
        self._refresh_pixmap()

    def refresh_overlay(self, glass, overlay) -> None:
        if self._frame is None:
            return
        self._glass = glass
        self._overlay = overlay
        self._rendered = self.renderer.render(self._frame, glass, overlay)
        self._refresh_pixmap()

    def rendered_image(self) -> np.ndarray | None:
        return None if self._rendered is None else self._rendered.copy()

    def save_png(self, path: str | Path) -> Path:
        if self._rendered is None:
            raise ValueError("저장할 원본 영상 장면이 없습니다.")
        destination = Path(path)
        if destination.suffix.lower() != ".png":
            destination = destination.with_suffix(".png")
        destination.parent.mkdir(parents=True, exist_ok=True)
        ok, encoded = cv2.imencode(".png", self._rendered)
        if not ok:
            raise OSError("PNG 인코딩에 실패했습니다.")
        try:
            encoded.tofile(str(destination))
        except OSError as exc:
            raise OSError(f"PNG 파일을 저장할 수 없습니다: {exc}") from exc
        return destination

    def _refresh_pixmap(self) -> None:
        if self._rendered is None:
            return
        rgb = np.ascontiguousarray(self._rendered[:, :, ::-1])
        image = QImage(
            rgb.data,
            rgb.shape[1],
            rgb.shape[0],
            rgb.strides[0],
            QImage.Format.Format_RGB888,
        ).copy()
        pixmap = QPixmap.fromImage(image)
        target = self.label.size()
        self.label.setText("")
        self.label.setPixmap(
            pixmap.scaled(target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_pixmap()
