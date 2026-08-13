from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.oil_supplemental_path import (
    generate_calibrated_high_recall_candidates,
    generate_distributed_sobel_candidates,
)
from oil_tracker.adapters.vision.preprocessing import PreprocessResult


def _preprocess_with_hidden_distributed_ridge() -> tuple[PreprocessResult, np.ndarray]:
    height, width = 112, 40
    gray = np.full((height, width), 90, dtype=np.uint8)
    sobel = np.zeros((height, width), dtype=np.uint8)
    signed = np.zeros((height, width), dtype=np.float32)
    horizontal = np.zeros((height, width), dtype=np.uint8)
    for row in (8, 18, 28, 38, 48, 58):
        sobel[row] = 255
        signed[row] = 120.0
        horizontal[row] = 255
    for row in (72, 82, 92):
        sobel[row] = 64
        signed[row] = 40.0
        horizontal[row] = 255
    mask = np.full_like(gray, 255)
    pre = PreprocessResult(
        gray=gray,
        normalized=gray,
        blurred=gray,
        sobel_y_signed=signed,
        sobel_y_abs=sobel,
        canny=horizontal,
        horizontal_mask=horizontal,
        glare_mask=np.zeros_like(gray),
    )
    return pre, mask


def test_distributed_sobel_retains_one_ridge_below_global_top_rows() -> None:
    pre, mask = _preprocess_with_hidden_distributed_ridge()

    candidates = generate_distributed_sobel_candidates(
        pre,
        mask,
        None,
        crop_origin_y=100.0,
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.y == 182.0
    assert candidate.source == "r8_distributed_sobel_path"
    assert candidate.features["r8_supplemental_path"] == 1.0
    assert candidate.features["distributed_sobel_group_count"] == 3.0
    assert candidate.features["distributed_sobel_group_span_px"] == 20.0


def test_distributed_sobel_requires_matching_raster_shapes() -> None:
    pre, mask = _preprocess_with_hidden_distributed_ridge()

    try:
        generate_distributed_sobel_candidates(
            pre,
            mask[:-1],
            None,
            crop_origin_y=0.0,
        )
    except ValueError as exc:
        assert "share one raster shape" in str(exc)
    else:
        raise AssertionError("shape mismatch must be rejected")


def test_calibrated_high_recall_keeps_multiple_distributed_weak_rows() -> None:
    pre, mask = _preprocess_with_hidden_distributed_ridge()

    candidates = generate_calibrated_high_recall_candidates(
        pre,
        mask,
        None,
        crop_origin_y=100.0,
        limit=5,
    )

    assert 2 <= len(candidates) <= 5
    assert all(candidate.source == "r9_calibrated_high_recall" for candidate in candidates)
    assert all(
        candidate.features["r9_calibrated_high_recall"] == 1.0
        for candidate in candidates
    )
    assert all(candidate.features["sequence_eligible"] == 1.0 for candidate in candidates)


def test_calibrated_high_recall_excludes_glare_dominated_rows() -> None:
    pre, mask = _preprocess_with_hidden_distributed_ridge()
    pre.glare_mask[26:31] = 255

    candidates = generate_calibrated_high_recall_candidates(
        pre,
        mask,
        None,
        crop_origin_y=0.0,
        limit=12,
    )

    assert all(abs(candidate.y - 28.0) > 5.0 for candidate in candidates)
