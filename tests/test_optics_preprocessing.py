from __future__ import annotations

import cv2
import numpy as np

from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _mask(shape: tuple[int, int]) -> np.ndarray:
    return np.full(shape, 255, dtype=np.uint8)


def test_unsaturated_vertical_low_chroma_caustic_is_glare_opposition() -> None:
    frame = np.full((120, 100, 3), 82, dtype=np.uint8)
    cv2.line(frame, (48, 12), (50, 108), (210, 210, 210), 5)

    result = preprocess(frame, _mask(frame.shape[:2]), DetectorSettings())

    assert result.gray[60, 49] < DetectorSettings().glare_threshold
    assert result.glare_mask[60, 49] == 255


def test_compact_bright_material_patch_is_not_promoted_to_caustic() -> None:
    frame = np.full((120, 100, 3), 82, dtype=np.uint8)
    cv2.circle(frame, (50, 62), 6, (205, 205, 205), -1)

    result = preprocess(frame, _mask(frame.shape[:2]), DetectorSettings())

    assert result.glare_mask[62, 50] == 0


def test_filled_tall_bright_material_droplet_is_not_promoted_to_caustic() -> None:
    frame = np.full((160, 120, 3), 45, dtype=np.uint8)
    cv2.ellipse(frame, (34, 75), (18, 30), 0, 0, 360, (210, 210, 210), -1)

    result = preprocess(frame, _mask(frame.shape[:2]), DetectorSettings())

    assert result.glare_mask[75, 34] == 0


def test_saturated_glare_remains_masked() -> None:
    frame = np.full((80, 80, 3), 75, dtype=np.uint8)
    frame[30:36, 20:60] = 255

    result = preprocess(frame, _mask(frame.shape[:2]), DetectorSettings())

    assert np.all(result.glare_mask[30:36, 20:60] == 255)


def test_thin_wide_colored_video_overlay_is_optics_opposition() -> None:
    frame = np.full((120, 160, 3), 80, dtype=np.uint8)
    cv2.line(frame, (15, 60), (145, 60), (20, 220, 30), 3)

    result = preprocess(frame, _mask(frame.shape[:2]), DetectorSettings())

    assert np.count_nonzero(result.glare_mask[56:65, 10:150]) > 300


def test_wide_chromatic_material_patch_is_not_treated_as_thin_overlay() -> None:
    frame = np.full((120, 160, 3), 80, dtype=np.uint8)
    frame[42:82, 22:138] = (35, 145, 205)

    result = preprocess(frame, _mask(frame.shape[:2]), DetectorSettings())

    assert np.count_nonzero(result.glare_mask[42:82, 22:138]) == 0
