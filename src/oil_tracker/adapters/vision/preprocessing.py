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
    glare = np.where(gray >= settings.glare_threshold, 255, 0).astype(np.uint8)
    glare = cv2.bitwise_and(glare, effective_mask)
    return PreprocessResult(gray, normalized, blurred, sobel_signed, sobel_abs, canny, horizontal, glare)
