from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from oil_tracker.domain.recipe import DetectorSettings


@dataclass
class PreprocessResult:
    gray: np.ndarray
    normalized: np.ndarray
    blurred: np.ndarray
    sobel_y_signed: np.ndarray
    sobel_y_abs: np.ndarray
    canny: np.ndarray
    horizontal_mask: np.ndarray
    glare_mask: np.ndarray


def preprocess(crop: np.ndarray, effective_mask: np.ndarray, settings: DetectorSettings) -> PreprocessResult:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop.copy()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    normalized = clahe.apply(gray)
    blurred = cv2.GaussianBlur(normalized, (5, 5), 0)
    sobel_signed = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
    sobel_abs = cv2.convertScaleAbs(sobel_signed)
    canny = cv2.Canny(blurred, settings.canny_low, settings.canny_high)
    canny = cv2.bitwise_and(canny, effective_mask)
    kernel_width = max(5, int(round(crop.shape[1] * 0.12)))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, 1))
    horizontal = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    horizontal = cv2.bitwise_and(horizontal, effective_mask)
    glare = _optical_glare_mask(crop, gray, effective_mask, settings)
    return PreprocessResult(gray, normalized, blurred, sobel_signed, sobel_abs, canny, horizontal, glare)


def _optical_glare_mask(
    crop: np.ndarray,
    gray: np.ndarray,
    effective_mask: np.ndarray,
    settings: DetectorSettings,
) -> np.ndarray:
    """Return bounded saturation and elongated-caustic opposition.

    Sight-glass glare is frequently below the absolute saturation threshold. A
    smooth vertical light ridge can therefore look textured after Canny/CLAHE
    and become both Foam and Oil evidence.  R6 adds only the optical class that
    can be identified without knowing the video: locally bright, low-chroma,
    vertically coherent support.  Compact bright material remains outside this
    additional mask.
    """

    valid = effective_mask > 0
    saturated = valid & (gray >= int(settings.glare_threshold))
    if not np.any(valid):
        return np.zeros_like(gray, dtype=np.uint8)

    gray_f = gray.astype(np.float32)
    base = max(3, min(gray.shape[:2]))
    field_kernel = _odd_kernel(max(9, int(round(base * 0.18))), upper=61)
    illumination = cv2.GaussianBlur(gray_f, (field_kernel, field_kernel), 0)
    residual = gray_f - illumination

    values = gray_f[valid]
    bright_floor = max(72.0, float(np.percentile(values, 72.0)))
    positive = residual[valid]
    residual_floor = max(12.0, float(np.percentile(positive, 90.0)))

    if crop.ndim == 3 and crop.shape[2] >= 3:
        bgr = crop[:, :, :3].astype(np.int16, copy=False)
        chroma_span = np.max(bgr, axis=2) - np.min(bgr, axis=2)
        low_chroma = chroma_span <= 20
    else:
        low_chroma = np.ones_like(valid)

    bright_residual = (
        valid
        & low_chroma
        & (gray_f >= bright_floor)
        & (residual >= residual_floor)
    )
    # Keep only optically elongated or hollow residuals. A straight caustic is
    # very tall and narrow; a curved crescent may be less elongated but remains
    # sparse inside its bounding box. Filled compact material, including a
    # large Foam droplet, must remain available to the material classifier.
    component_mask = np.zeros_like(gray, dtype=np.uint8)
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        bright_residual.astype(np.uint8),
        connectivity=8,
    )
    minimum_height = max(8, int(round(gray.shape[0] * 0.12)))
    for label in range(1, count):
        width = max(1, int(stats[label, cv2.CC_STAT_WIDTH]))
        height = max(1, int(stats[label, cv2.CC_STAT_HEIGHT]))
        area = int(stats[label, cv2.CC_STAT_AREA])
        aspect_ratio = height / width
        fill_ratio = area / max(1, width * height)
        caustic_shape = aspect_ratio >= 2.0 or (
            aspect_ratio >= 1.35 and fill_ratio <= 0.55
        )
        if height < minimum_height or not caustic_shape or area < minimum_height:
            continue
        component_mask[labels == label] = 255

    caustic = component_mask
    if np.any(caustic):
        radius = max(1, min(3, int(round(base * 0.012))))
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (2 * radius + 1, 2 * radius + 1),
        )
        caustic = cv2.dilate(caustic, kernel)
    overlay = _digital_overlay_mask(crop, valid)
    glare = saturated | ((caustic > 0) & valid) | (overlay > 0)
    return glare.astype(np.uint8) * 255


def _digital_overlay_mask(crop: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Identify thin, wide chromatic HUD strokes inside a configured ROI."""

    if crop.ndim != 3 or crop.shape[2] < 3 or not np.any(valid):
        return np.zeros(valid.shape, dtype=np.uint8)
    bgr = crop[:, :, :3].astype(np.int16, copy=False)
    maximum = np.max(bgr, axis=2)
    minimum = np.min(bgr, axis=2)
    chroma = maximum - minimum
    colorful = valid & (chroma >= 48) & (maximum >= 92)
    columns = np.flatnonzero(np.any(valid, axis=0))
    if columns.size < 12 or not np.any(colorful):
        return np.zeros(valid.shape, dtype=np.uint8)
    effective_width = int(columns[-1] - columns[0] + 1)
    horizontal_length = max(9, int(round(effective_width * 0.18)))
    core = cv2.morphologyEx(
        colorful.astype(np.uint8) * 255,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_length, 1)),
    )
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        core,
        connectivity=8,
    )
    result = np.zeros(valid.shape, dtype=np.uint8)
    maximum_height = max(3, int(round(valid.shape[0] * 0.065)))
    minimum_width = max(horizontal_length, int(round(effective_width * 0.32)))
    for label in range(1, count):
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = max(1, int(stats[label, cv2.CC_STAT_HEIGHT]))
        if width < minimum_width or height > maximum_height or width / height < 5.0:
            continue
        result[labels == label] = 255
    if np.any(result):
        # Mask the antialiased/blurred edge around the encoded stroke as well;
        # otherwise the line itself disappears and its two halo edges become
        # even cleaner Oil candidates.
        vertical_radius = max(3, min(12, int(round(valid.shape[0] * 0.04))))
        result = cv2.dilate(
            result,
            cv2.getStructuringElement(
                cv2.MORPH_RECT,
                (3, 2 * vertical_radius + 1),
            ),
        )
        result = cv2.bitwise_and(result, valid.astype(np.uint8) * 255)
    return result


def _odd_kernel(value: int, *, upper: int) -> int:
    value = min(max(3, int(value)), int(upper))
    if value % 2:
        return value
    return value + 1 if value < upper else value - 1
