from __future__ import annotations

import math

import cv2
import numpy as np

from oil_tracker.adapters.vision.review_overlay_renderer import _copy_bgr_frame


class ReviewDebugOverlayRenderer:
    """Render saved detector candidates without mixing official tracking overlays."""

    def render(
        self,
        frame: np.ndarray,
        glass,
        record,
        actual_timestamp: float,
        highlighted_candidate: int | None = None,
    ) -> np.ndarray:
        image = _copy_bgr_frame(frame)

        ellipse = glass.geometry.ellipse
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
        if glass.geometry.zero_line_y is not None:
            extent = ellipse.horizontal_extent_at(float(glass.geometry.zero_line_y))
            if extent is not None:
                cv2.line(
                    image,
                    (int(round(extent[0])), int(round(glass.geometry.zero_line_y))),
                    (int(round(extent[1])), int(round(glass.geometry.zero_line_y))),
                    (0, 230, 255),
                    1,
                    cv2.LINE_AA,
                )

        for index, candidate in enumerate(record.candidates):
            y = _finite_number(candidate.get("canonical_y"))
            if y is None:
                continue
            extent = ellipse.horizontal_extent_at(y)
            if extent is None:
                continue
            selected = bool(candidate.get("selected"))
            rejected = bool(candidate.get("rejected"))
            foam = candidate.get("kind") == "foam_front"
            highlighted = index == highlighted_candidate
            color = (
                (255, 0, 255)
                if foam
                else (30, 220, 30)
                if selected
                else (0, 90, 255)
                if rejected
                else (255, 180, 40)
            )
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
            score = _finite_number(candidate.get("final_score"))
            score_text = "-" if score is None else f"{score:.3f}"
            label = f"#{rank} {candidate.get('kind', '')} {status} score={score_text}"
            _outlined_text(image, label, (start[0] + 4, max(16, start[1] - 10)), color, 0.42)

        decoded = float(actual_timestamp)
        delta = decoded - float(record.timestamp_sec)
        _outlined_text(
            image,
            f"DEBUG TRACE {record.timestamp_sec:.3f}s",
            (14, 24),
            (255, 255, 255),
            0.54,
        )
        _outlined_text(
            image,
            f"DECODED {decoded:.3f}s  DELTA {delta:+.3f}s",
            (14, 47),
            (255, 255, 255),
            0.50,
        )
        _outlined_text(
            image,
            "Official final tracking overlay is hidden in debug mode",
            (14, 70),
            (0, 220, 255),
            0.45,
        )
        return image


def _finite_number(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


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
