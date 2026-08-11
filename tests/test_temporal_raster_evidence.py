from __future__ import annotations

import cv2
import numpy as np

from oil_tracker.adapters.vision.temporal_raster_evidence import (
    RegisteredFoamMotionTracker,
)


def _scene(*, exposure: int = 0, shift_x: int = 0) -> tuple[np.ndarray, np.ndarray]:
    gray = np.full((100, 90), 80 + exposure, dtype=np.uint8)
    cv2.line(gray, (42 + shift_x, 12), (42 + shift_x, 88), 170 + exposure, 5)
    mask = np.zeros_like(gray)
    cv2.rectangle(mask, (37 + shift_x, 10), (47 + shift_x, 90), 255, -1)
    return gray, mask


def test_registered_static_streak_rejects_exposure_and_translation_jitter() -> None:
    tracker = RegisteredFoamMotionTracker()
    effective = np.full((100, 90), 255, dtype=np.uint8)
    first, first_mask = _scene()
    second, second_mask = _scene(exposure=9, shift_x=1)

    assert not tracker.evaluate("g", first, effective, first_mask, 10.0).available
    evidence = tracker.evaluate("g", second, effective, second_mask, 10.0)

    assert evidence.available
    assert evidence.internal_motion_support < 0.10
    assert evidence.dynamic_support < 0.10


def test_nonrigid_material_change_produces_internal_motion_support() -> None:
    tracker = RegisteredFoamMotionTracker()
    effective = np.full((100, 90), 255, dtype=np.uint8)
    first = np.full((100, 90), 80, dtype=np.uint8)
    second = first.copy()
    mask = np.zeros_like(first)
    cv2.rectangle(mask, (18, 35), (72, 88), 255, -1)
    for x, y in ((28, 48), (46, 59), (62, 73)):
        cv2.circle(first, (x, y), 7, 180, -1)
    for x, y in ((34, 53), (52, 68), (66, 82)):
        cv2.circle(second, (x, y), 7, 180, -1)

    tracker.evaluate("g", first, effective, mask, 35.0)
    evidence = tracker.evaluate("g", second, effective, mask, 35.0)

    assert evidence.available
    assert evidence.internal_motion_support > 0.20
    assert evidence.dynamic_support >= evidence.internal_motion_support


def test_identical_textured_material_has_zero_registered_motion() -> None:
    tracker = RegisteredFoamMotionTracker()
    effective = np.full((100, 90), 255, dtype=np.uint8)
    gray, mask = _scene()

    tracker.evaluate("g", gray, effective, mask, 10.0)
    evidence = tracker.evaluate("g", gray.copy(), effective, mask.copy(), 10.0)

    assert evidence.available
    assert evidence.exact_overlap == 1.0
    assert evidence.internal_motion_support == 0.0
    assert evidence.dynamic_support == 0.0


def test_tracker_reset_isolated_by_glass() -> None:
    tracker = RegisteredFoamMotionTracker()
    effective = np.full((40, 40), 255, dtype=np.uint8)
    gray = np.full((40, 40), 90, dtype=np.uint8)
    mask = np.zeros_like(gray)
    mask[20:, 10:30] = 255
    tracker.evaluate("a", gray, effective, mask, 20.0)
    tracker.evaluate("b", gray, effective, mask, 20.0)

    tracker.reset("a")

    assert tracker.state_count == 1
    assert not tracker.evaluate("a", gray, effective, mask, 20.0).available
    assert tracker.evaluate("b", gray, effective, mask, 20.0).available
