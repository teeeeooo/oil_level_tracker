from __future__ import annotations

import cv2
import numpy as np
from dataclasses import asdict

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


def test_path_capture_preserves_candidates_and_sector_channel_provenance() -> None:
    frame = np.full((160, 150, 3), 160, dtype=np.uint8)
    points = np.asarray(((15, 94), (40, 88), (70, 82), (100, 76), (134, 70)), np.int32)
    cv2.fillPoly(frame, [np.vstack((points, ((134, 159), (15, 159))))], (70, 70, 70))
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    mask[:, 15:135] = 255
    pre = preprocess(frame, mask, DetectorSettings())
    plain = generate_material_path_candidates(pre, mask, None, crop_origin_y=31)
    paths = {}
    captured = generate_material_path_candidates(pre, mask, None, crop_origin_y=31, diagnostic_paths=paths)
    assert [asdict(c) for c in captured] == [asdict(c) for c in plain]
    assert captured
    for candidate in captured:
        evidence = paths[id(candidate)]
        samples = evidence.diagnostic_samples
        assert tuple(s.local_y for s in samples) == evidence.rows
        assert [s.sector_index for s in samples] == sorted(s.sector_index for s in samples)
        assert len(samples) >= 3
        for sample in samples:
            assert sample.start_x == 15 + round(120 * sample.sector_index / 5)
            assert sample.stop_x == 15 + round(120 * (sample.sector_index + 1) / 5)
            assert sample.contrast_channel == "blurred_gray_dynamic_range"
            assert sample.contrast_scale_px in (3, 6, 10)
        assert candidate.y == 31 + np.median(evidence.rows)


def test_capture_records_material_channel_without_changing_generation() -> None:
    frame = np.full((160, 150, 3), 145, dtype=np.uint8)
    mask = np.full(frame.shape[:2], 255, dtype=np.uint8)
    pre = preprocess(frame, mask, DetectorSettings())
    material = np.zeros(frame.shape[:2], dtype=np.float32)
    material[:80] = 0.8
    paths = {}
    captured = generate_material_path_candidates(
        pre, mask, None, crop_origin_y=0, material_evidence_map=material,
        diagnostic_paths=paths,
    )
    plain = generate_material_path_candidates(
        pre, mask, None, crop_origin_y=0, material_evidence_map=material,
    )
    assert captured and [asdict(c) for c in captured] == [asdict(c) for c in plain]
    for candidate in captured:
        assert all(s.contrast_channel == "raw_combined_material" for s in paths[id(candidate)].diagnostic_samples)
