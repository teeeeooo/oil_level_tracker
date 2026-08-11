from __future__ import annotations

import cv2
import numpy as np

from oil_tracker.adapters.vision.oil_material_path import (
    generate_material_path_candidates,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def test_curved_cross_column_phase_path_generates_candidate() -> None:
    frame = np.full((120, 120, 3), 145, dtype=np.uint8)
    points = np.asarray(((4, 66), (30, 64), (60, 61), (90, 59), (115, 57)), np.int32)
    polygon = np.vstack((points, np.asarray(((119, 119), (0, 119)), np.int32)))
    cv2.fillPoly(frame, [polygon], (78, 78, 78))
    mask = np.full(frame.shape[:2], 255, dtype=np.uint8)
    pre = preprocess(frame, mask, DetectorSettings())

    candidates = generate_material_path_candidates(
        pre,
        mask,
        None,
        crop_origin_y=10.0,
    )

    assert candidates
    assert abs(candidates[0].y - 71.0) <= 6.0
    assert candidates[0].features["material_path_sector_count"] >= 3.0
    assert candidates[0].features["sequence_eligible"] == 1.0


def test_single_sector_edge_does_not_generate_cross_column_candidate() -> None:
    frame = np.full((120, 120, 3), 120, dtype=np.uint8)
    frame[60:, :20] = 50
    mask = np.full(frame.shape[:2], 255, dtype=np.uint8)
    pre = preprocess(frame, mask, DetectorSettings())

    candidates = generate_material_path_candidates(
        pre,
        mask,
        None,
        crop_origin_y=0.0,
    )

    assert not candidates
