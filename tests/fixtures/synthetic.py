from __future__ import annotations

from uuid import uuid4

import cv2
import numpy as np

from oil_tracker.domain.geometry import EllipseGeometry, GlassGeometry
from oil_tracker.domain.recipe import GlassInspectionConfig

WIDTH = 320
HEIGHT = 240
CENTER = (160, 120)
AXES = (70, 100)


def glass_config() -> GlassInspectionConfig:
    geometry = GlassGeometry(EllipseGeometry(CENTER[0], CENTER[1], AXES[0], AXES[1]), zero_line_y=130, margin_ratio=0.06)
    glass = GlassInspectionConfig(str(uuid4()), "Glass A", geometry)
    glass.detector_settings.minimum_final_confidence = 0.28
    glass.detector_settings.minimum_horizontal_coverage = 0.12
    glass.detector_settings.minimum_region_contrast = 0.04
    glass.detector_settings.state_hold_frames = 1
    return glass


def base_frame(value: int = 220) -> np.ndarray:
    frame = np.full((HEIGHT, WIDTH, 3), 230, dtype=np.uint8)
    cv2.ellipse(frame, CENTER, AXES, 0, 0, 360, (value, value, value), -1)
    cv2.ellipse(frame, CENTER, AXES, 0, 0, 360, (40, 40, 40), 3)
    return frame


def partial_frame(boundary_y: int = 130) -> np.ndarray:
    frame = base_frame(210)
    mask = np.zeros((HEIGHT, WIDTH), np.uint8)
    cv2.ellipse(mask, CENTER, AXES, 0, 0, 360, 255, -1)
    oil = np.zeros_like(mask); oil[boundary_y:, :] = 255; oil = cv2.bitwise_and(mask, oil)
    frame[oil > 0] = (65, 75, 85)
    cv2.line(frame, (98, boundary_y), (222, boundary_y), (20, 20, 20), 3)
    return frame


def ambiguous_near_bottom_frame() -> np.ndarray:
    frame = base_frame(210)
    boundary_y = 190
    mask = np.zeros((HEIGHT, WIDTH), np.uint8)
    cv2.ellipse(mask, CENTER, AXES, 0, 0, 360, 255, -1)
    oil = np.zeros_like(mask)
    oil[boundary_y:, :] = 255
    oil = cv2.bitwise_and(mask, oil)
    frame[oil > 0] = (80, 80, 80)
    cv2.line(frame, (98, boundary_y), (222, boundary_y), (20, 20, 20), 1)
    return frame


def full_frame() -> np.ndarray:
    return base_frame(70)


def empty_frame() -> np.ndarray:
    return base_frame(215)


def glare_frame() -> np.ndarray:
    frame = base_frame(255)
    cv2.ellipse(frame, CENTER, AXES, 0, 0, 360, (255, 255, 255), -1)
    return frame


def foam_bottom_frame() -> np.ndarray:
    frame = base_frame(65)
    x0, x1, front, bottom = 105, 216, 145, 216
    yy, xx = np.indices((bottom - front, x1 - x0))
    patch = np.where(
        ((xx // 6 + yy // 6) % 2)[..., None] == 0,
        210,
        135,
    ).astype(np.uint8)
    frame[front:bottom, x0:x1] = patch
    for y in range(front + 4, bottom, 12):
        for x in range(x0 + 4, x1, 14):
            cv2.circle(frame, (x, y), 3, (225, 225, 225), 1)
    return frame


def disconnected_bubbles_frame() -> np.ndarray:
    frame = base_frame(65)
    for y in range(65, 105, 10):
        for x in range(130, 191, 12):
            cv2.circle(frame, (x, y), 3, (210, 210, 210), 1)
    return frame
