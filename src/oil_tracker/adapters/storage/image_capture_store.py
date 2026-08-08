from __future__ import annotations

from pathlib import Path
import re

import cv2
import numpy as np

from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.application.services.report_presentation import (
    ReportLandmark,
    ReportPresentation,
    build_report_presentation,
)
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.domain.recipe import GlassInspectionConfig, InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, TrackingSample


class ImageCaptureStore:
    def create_event_captures(
        self,
        result: AnalysisResult,
        video_path: str,
        directory: Path,
        *,
        recipe: InspectionRecipe | None = None,
        presentation: ReportPresentation | None = None,
        cancellation=None,
        progress=None,
    ) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        if presentation is None:
            if recipe is None:
                raise ValueError("User report captures require a Recipe or presentation model.")
            presentation = build_report_presentation(result, recipe)
        configs = {} if recipe is None else {glass.id: glass for glass in recipe.glasses}
        landmarks = tuple(
            (glass.glass_id, glass.glass_name, landmark)
            for glass in presentation.glasses
            for landmark in glass.landmarks
        )
        reader = OpenCvVideoReader(video_path)
        completed = 0
        captured_at: dict[tuple[str, float], str] = {}
        try:
            for index, (glass_id, glass_name, landmark) in enumerate(landmarks, start=1):
                _check_cancelled(cancellation)
                capture_key = (glass_id, round(landmark.timestamp_sec, 6))
                reused = captured_at.get(capture_key)
                if reused is not None:
                    landmark.capture_path = reused
                    if landmark.source_event is not None:
                        landmark.source_event.capture_path = reused
                    completed += 1
                    _emit_progress(progress, completed, len(landmarks))
                    continue
                try:
                    frame, _, actual_time = reader.read_at(landmark.timestamp_sec)
                except Exception:
                    completed += 1
                    _emit_progress(progress, completed, len(landmarks))
                    continue
                image = _render_landmark_capture(
                    frame,
                    configs.get(glass_id),
                    landmark,
                    actual_time,
                )
                safe_name = _safe_component(glass_name) or "glass"
                filename = (
                    f"{safe_name}_{index:02d}_{landmark.event_type.value}_"
                    f"{landmark.timestamp_sec:.2f}.png"
                )
                path = directory / filename
                if _write_png(path, image):
                    relative = f"captures/{filename}"
                    captured_at[capture_key] = relative
                    landmark.capture_path = relative
                    if landmark.source_event is not None:
                        landmark.source_event.capture_path = relative
                completed += 1
                _emit_progress(progress, completed, len(landmarks))
        finally:
            reader.close()


def _render_landmark_capture(
    frame: np.ndarray,
    config: GlassInspectionConfig | None,
    landmark: ReportLandmark,
    actual_time: float,
) -> np.ndarray:
    image = _copy_bgr(frame)
    show_zero = False
    show_oil = False
    show_foam = False
    if config is not None:
        ellipse = config.geometry.ellipse
        cv2.ellipse(
            image,
            (int(round(ellipse.center_x)), int(round(ellipse.center_y))),
            (max(1, int(round(ellipse.radius_x))), max(1, int(round(ellipse.radius_y)))),
            0,
            0,
            360,
            (255, 210, 0),
            2,
            cv2.LINE_AA,
        )
        zero_y = config.geometry.zero_line_y
        if zero_y is not None:
            _horizontal_line(image, ellipse, float(zero_y), (0, 220, 255), 2)
            show_zero = True
        oil_y = _oil_source_y(landmark.sample, zero_y)
        foam_y = _foam_source_y(landmark.sample, zero_y)
        if oil_y is not None:
            _horizontal_line(image, ellipse, oil_y, (40, 220, 60), 3)
            show_oil = True
        if foam_y is not None:
            _horizontal_line(image, ellipse, foam_y, (255, 120, 40), 3)
            show_foam = True
        image = _crop_around_glass(image, config)
        image = _upscale_small_capture(image)
    return _capture_badges(
        image,
        actual_time,
        show_zero=show_zero,
        show_oil=show_oil,
        show_foam=show_foam,
    )


def _crop_around_glass(image: np.ndarray, config: GlassInspectionConfig) -> np.ndarray:
    ellipse = config.geometry.ellipse
    pad_x = max(24.0, ellipse.radius_x * 0.35)
    pad_y = max(24.0, ellipse.radius_y * 0.30)
    height, width = image.shape[:2]
    x0 = max(0, int(np.floor(ellipse.center_x - ellipse.radius_x - pad_x)))
    x1 = min(width, int(np.ceil(ellipse.center_x + ellipse.radius_x + pad_x)))
    y0 = max(0, int(np.floor(ellipse.center_y - ellipse.radius_y - pad_y)))
    y1 = min(height, int(np.ceil(ellipse.center_y + ellipse.radius_y + pad_y)))
    if x1 <= x0 or y1 <= y0:
        return image
    return np.ascontiguousarray(image[y0:y1, x0:x1])


def _upscale_small_capture(image: np.ndarray, minimum_long_edge: int = 320) -> np.ndarray:
    height, width = image.shape[:2]
    long_edge = max(height, width)
    if long_edge <= 0 or long_edge >= minimum_long_edge:
        return image
    scale = minimum_long_edge / long_edge
    return cv2.resize(
        image,
        (max(1, int(round(width * scale))), max(1, int(round(height * scale)))),
        interpolation=cv2.INTER_CUBIC,
    )


def _capture_badges(
    image: np.ndarray,
    timestamp_sec: float,
    *,
    show_zero: bool,
    show_oil: bool,
    show_foam: bool,
) -> np.ndarray:
    output = np.ascontiguousarray(image.copy())
    label = f"SOURCE {timestamp_sec:.2f} s"
    (text_width, text_height), _ = cv2.getTextSize(
        label,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        1,
    )
    cv2.rectangle(
        output,
        (8, 8),
        (min(output.shape[1] - 1, text_width + 24), min(output.shape[0] - 1, text_height + 24)),
        (15, 23, 42),
        -1,
    )
    cv2.putText(
        output,
        label,
        (16, text_height + 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    legend = []
    if show_zero:
        legend.append(("ZERO", (0, 220, 255)))
    if show_oil:
        legend.append(("OIL", (40, 220, 60)))
    if show_foam:
        legend.append(("FOAM", (255, 120, 40)))
    if legend:
        baseline_y = max(18, output.shape[0] - 14)
        cv2.rectangle(
            output,
            (8, max(0, baseline_y - 17)),
            (min(output.shape[1] - 1, 72 * len(legend) + 12), output.shape[0] - 5),
            (15, 23, 42),
            -1,
        )
        x = 16
        for label_text, color in legend:
            cv2.line(output, (x, baseline_y - 5), (x + 18, baseline_y - 5), color, 3, cv2.LINE_AA)
            cv2.putText(
                output,
                label_text,
                (x + 23, baseline_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            x += 72
    return output


def _horizontal_line(image, ellipse, y: float, color, width: int) -> None:
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


def _oil_source_y(sample: TrackingSample | None, zero_y: float | None) -> float | None:
    if sample is None:
        return None
    if zero_y is not None:
        level = _first_finite(
            sample.smoothed_oil_air_level_px_from_zero,
            sample.raw_oil_air_level_px_from_zero,
        )
        if level is not None:
            return float(zero_y) - level
    return _first_finite(sample.raw_oil_air_level_y)


def _foam_source_y(sample: TrackingSample | None, zero_y: float | None) -> float | None:
    if sample is None:
        return None
    if zero_y is not None:
        level = _first_finite(
            sample.smoothed_foam_front_px_from_zero,
            sample.raw_foam_front_px_from_zero,
        )
        if level is not None:
            return float(zero_y) - level
    return _first_finite(sample.raw_foam_front_y)


def _first_finite(*values: float | None) -> float | None:
    for value in values:
        if value is None:
            continue
        number = float(value)
        if np.isfinite(number):
            return number
    return None


def _copy_bgr(frame: np.ndarray) -> np.ndarray:
    image = np.ascontiguousarray(frame.copy())
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.ndim == 3 and image.shape[2] == 3:
        return image
    if image.ndim == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    raise ValueError("Unsupported source frame shape for report capture.")


def _write_png(path: Path, image: np.ndarray) -> bool:
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        return False
    path.write_bytes(encoded.tobytes())
    return True


def _safe_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_.")


def _emit_progress(progress, completed: int, total: int) -> None:
    if progress is not None:
        progress(completed, total)


def _check_cancelled(cancellation) -> None:
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis was cancelled while creating result images.")
