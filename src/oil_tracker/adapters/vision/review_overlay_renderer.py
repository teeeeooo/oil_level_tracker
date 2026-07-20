from __future__ import annotations

import cv2
import numpy as np

from oil_tracker.domain.review import ReviewOverlayData


class ReviewOverlayRenderer:
    """Render final saved analysis values onto a full-resolution source frame."""

    def render(self, frame: np.ndarray, glass, overlay: ReviewOverlayData) -> np.ndarray:
        image = np.ascontiguousarray(frame.copy())
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        if not overlay.within_analysis_range:
            self._text(image, "OUTSIDE ANALYSIS RANGE", (16, 30), (0, 190, 255), 0.75)
            return image

        ellipse = glass.geometry.ellipse
        invalid = overlay.sample is not None and (not overlay.sample.is_valid or bool(overlay.review_reasons))
        roi_color = (0, 80, 255) if invalid else (255, 220, 0)
        cv2.ellipse(
            image,
            (int(round(ellipse.center_x)), int(round(ellipse.center_y))),
            (max(1, int(round(ellipse.radius_x))), max(1, int(round(ellipse.radius_y)))),
            0,
            0,
            360,
            roi_color,
            2,
            cv2.LINE_AA,
        )
        for zone in glass.geometry.exclusions:
            rect = zone.rect
            cv2.rectangle(
                image,
                (int(round(rect.x)), int(round(rect.y))),
                (int(round(rect.right)), int(round(rect.bottom))),
                (0, 140, 255),
                1,
                cv2.LINE_AA,
            )

        zero_y = glass.geometry.zero_line_y
        if zero_y is not None:
            self._horizontal_line(image, ellipse, float(zero_y), (0, 230, 255), 2)
        if overlay.oil_boundary_y is not None:
            self._horizontal_line(image, ellipse, overlay.oil_boundary_y, (50, 220, 50), 3)
        if overlay.foam_front_y is not None:
            self._horizontal_line(image, ellipse, overlay.foam_front_y, (255, 120, 40), 3)

        sample = overlay.sample
        state = sample.fill_state.value if sample is not None else "NO SAMPLE"
        confidence = f"{sample.overall_confidence:.3f}" if sample is not None else "-"
        sample_time = f"{sample.timestamp_sec:.3f}s" if sample is not None else "-"
        lines = (
            glass.name,
            f"STATE {state}  CONF {confidence}",
            f"VIDEO {overlay.video_timestamp_sec:.3f}s  SAMPLE {sample_time}",
        )
        y = max(24, int(round(ellipse.center_y - ellipse.radius_y)) - 58)
        x = max(8, int(round(ellipse.center_x - ellipse.radius_x)))
        for line in lines:
            self._text(image, line, (x, y), (255, 255, 255), 0.55)
            y += 22
        if overlay.review_reasons:
            self._text(image, "REVIEW: " + ", ".join(overlay.review_reasons), (x, y), (0, 80, 255), 0.52)
        return image

    def _horizontal_line(self, image, ellipse, y: float, color, width: int) -> None:
        extent = ellipse.horizontal_extent_at(float(y))
        if extent is None:
            return
        cv2.line(
            image,
            (int(round(extent[0])), int(round(y))),
            (int(round(extent[1])), int(round(y))),
            color,
            width,
            cv2.LINE_AA,
        )

    def _text(self, image, text: str, origin, color, scale: float) -> None:
        safe = str(text).encode("ascii", "replace").decode("ascii")
        cv2.putText(image, safe, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(image, safe, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
