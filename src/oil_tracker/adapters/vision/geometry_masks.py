from __future__ import annotations

from dataclasses import dataclass
import math

import cv2
import numpy as np

from oil_tracker.domain.recipe import GlassInspectionConfig


@dataclass
class MaskBundle:
    crop: np.ndarray
    crop_origin: tuple[int, int]
    ellipse_mask: np.ndarray
    margin_mask: np.ndarray
    exclusion_mask: np.ndarray
    effective_mask: np.ndarray


def build_mask_bundle(frame: np.ndarray, glass: GlassInspectionConfig) -> MaskBundle:
    bounds = glass.geometry.crop_roi
    frame_h, frame_w = frame.shape[:2]
    x0 = max(0, int(math.floor(bounds.x)))
    y0 = max(0, int(math.floor(bounds.y)))
    x1 = min(frame_w, int(math.ceil(bounds.right)))
    y1 = min(frame_h, int(math.ceil(bounds.bottom)))
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Glass crop is outside the frame.")
    crop = frame[y0:y1, x0:x1].copy()
    h, w = crop.shape[:2]
    ellipse_mask = np.zeros((h, w), dtype=np.uint8)
    e = glass.geometry.ellipse
    center = (int(round(e.center_x - x0)), int(round(e.center_y - y0)))
    axes = (max(1, int(round(e.radius_x))), max(1, int(round(e.radius_y))))
    cv2.ellipse(ellipse_mask, center, axes, 0, 0, 360, 255, -1)

    ratio = float(glass.geometry.margin_ratio)
    margin_mask = np.zeros_like(ellipse_mask)
    inner_axes = (max(1, int(round(e.radius_x * (1.0 - ratio)))), max(1, int(round(e.radius_y * (1.0 - ratio)))))
    cv2.ellipse(margin_mask, center, inner_axes, 0, 0, 360, 255, -1)
    margin_mask = cv2.bitwise_and(margin_mask, ellipse_mask)

    exclusion_mask = np.zeros_like(ellipse_mask)
    for zone in glass.geometry.exclusions:
        r = zone.rect
        zx0 = max(0, int(math.floor(r.x - x0)))
        zy0 = max(0, int(math.floor(r.y - y0)))
        zx1 = min(w, int(math.ceil(r.right - x0)))
        zy1 = min(h, int(math.ceil(r.bottom - y0)))
        if zx1 > zx0 and zy1 > zy0:
            cv2.rectangle(exclusion_mask, (zx0, zy0), (zx1 - 1, zy1 - 1), 255, -1)
    effective_mask = cv2.bitwise_and(margin_mask, cv2.bitwise_not(exclusion_mask))
    return MaskBundle(crop, (x0, y0), ellipse_mask, margin_mask, exclusion_mask, effective_mask)


def effective_area_ratio(bundle: MaskBundle) -> float:
    ellipse_area = int(np.count_nonzero(bundle.ellipse_mask))
    return 0.0 if ellipse_area == 0 else float(np.count_nonzero(bundle.effective_mask)) / ellipse_area
