from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer


class ResultReviewCanvas(QWidget):
    """Read-only canvas with mutually exclusive general and debug render layers."""

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
        self._debug_record = None
        self._debug_actual_timestamp: float | None = None
        self._highlighted_candidate: int | None = None

    def set_message(self, message: str) -> None:
        self._frame = None
        self._rendered = None
        self._glass = None
        self._overlay = None
        self._debug_record = None
        self._highlighted_candidate = None
        self.label.setPixmap(QPixmap())
        self.label.setText(message)

    def set_review_frame(self, frame: np.ndarray, glass, overlay) -> None:
        self._frame = np.ascontiguousarray(frame.copy())
        self._glass = glass
        self._overlay = overlay
        self._debug_record = None
        self._highlighted_candidate = None
        self._rendered = self.renderer.render(self._frame, glass, overlay)
        self._refresh_pixmap()

    def set_debug_frame(self, frame: np.ndarray, glass, record, actual_timestamp: float) -> None:
        self._frame = np.ascontiguousarray(frame.copy())
        self._glass = glass
        self._overlay = None
        self._debug_record = record
        self._debug_actual_timestamp = float(actual_timestamp)
        self._highlighted_candidate = None
        self._render_debug()

    def refresh_overlay(self, glass, overlay) -> None:
        if self._frame is None:
            return
        self._glass = glass
        self._overlay = overlay
        self._debug_record = None
        self._highlighted_candidate = None
        self._rendered = self.renderer.render(self._frame, glass, overlay)
        self._refresh_pixmap()

    def set_candidate_highlight(self, candidate_index: int | None) -> None:
        self._highlighted_candidate = candidate_index
        if self._debug_record is not None and self._frame is not None:
            self._render_debug()

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

    def _render_debug(self) -> None:
        if self._frame is None or self._glass is None or self._debug_record is None:
            return
        image = np.ascontiguousarray(self._frame.copy())
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        ellipse = self._glass.geometry.ellipse
        cv2.ellipse(
            image,
            (int(round(ellipse.center_x)), int(round(ellipse.center_y))),
            (max(1, int(round(ellipse.radius_x))), max(1, int(round(ellipse.radius_y)))),
            0,
            0,
            360,
            (255, 220, 0),
            2,
            cv2.LINE_AA,
        )
        if self._glass.geometry.zero_line_y is not None:
            extent = ellipse.horizontal_extent_at(float(self._glass.geometry.zero_line_y))
            if extent is not None:
                cv2.line(
                    image,
                    (int(round(extent[0])), int(round(self._glass.geometry.zero_line_y))),
                    (int(round(extent[1])), int(round(self._glass.geometry.zero_line_y))),
                    (0, 230, 255),
                    1,
                    cv2.LINE_AA,
                )
        for index, candidate in enumerate(self._debug_record.candidates):
            y = candidate.get("canonical_y")
            try:
                y = float(y)
            except (TypeError, ValueError):
                continue
            extent = ellipse.horizontal_extent_at(y)
            if extent is None:
                continue
            selected = bool(candidate.get("selected"))
            rejected = bool(candidate.get("rejected"))
            foam = candidate.get("kind") == "foam_front"
            highlighted = index == self._highlighted_candidate
            color = (255, 0, 255) if foam else (30, 220, 30) if selected else (0, 90, 255) if rejected else (255, 180, 40)
            width = 4 if highlighted else 3 if selected else 2
            start = (int(round(extent[0])), int(round(y)))
            end = (int(round(extent[1])), int(round(y)))
            if rejected:
                _dashed_line(image, start, end, color, width, dash=9, gap=6)
            elif not selected:
                _dashed_line(image, start, end, color, width, dash=3, gap=5)
            else:
                cv2.line(image, start, end, color, width, cv2.LINE_AA)
            status = "SELECTED" if selected else "REJECTED" if rejected else "ELIGIBLE"
            rank = candidate.get("rank", index + 1)
            score = candidate.get("final_score")
            score_text = "-" if score is None else f"{float(score):.3f}"
            label = f"#{rank} {candidate.get('kind', '')} {status} score={score_text}"
            _outlined_text(image, label, (start[0] + 4, max(16, start[1] - 5)), color, 0.42)
        delta = self._debug_actual_timestamp - self._debug_record.timestamp_sec if self._debug_actual_timestamp is not None else 0.0
        _outlined_text(
            image,
            f"DEBUG TRACE {self._debug_record.timestamp_sec:.3f}s / DECODED {self._debug_actual_timestamp:.3f}s / DELTA {delta:+.3f}s",
            (14, 26),
            (255, 255, 255),
            0.56,
        )
        _outlined_text(image, "Official final tracking overlay is hidden in debug mode", (14, 49), (0, 220, 255), 0.48)
        self._rendered = image
        self._refresh_pixmap()

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


def _dashed_line(image, start, end, color, width: int, *, dash: int, gap: int) -> None:
    x0, y0 = start
    x1, y1 = end
    length = max(1, abs(x1 - x0))
    direction = 1 if x1 >= x0 else -1
    position = 0
    while position < length:
        segment_end = min(length, position + dash)
        cv2.line(
            image,
            (x0 + direction * position, y0),
            (x0 + direction * segment_end, y1),
            color,
            width,
            cv2.LINE_AA,
        )
        position += dash + gap


def _outlined_text(image, text: str, origin, color, scale: float) -> None:
    safe = str(text).encode("ascii", "replace").decode("ascii")
    cv2.putText(image, safe, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(image, safe, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
