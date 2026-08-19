from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.oil_supplemental_path import (
    generate_calibrated_high_recall_candidates,
    generate_distributed_sobel_candidates,
    generate_phase_transition_candidates,
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
    assert candidate.source == "distributed_sobel_path"
    assert candidate.features["supplemental_path"] == 1.0
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
    assert all(candidate.source == "calibrated_high_recall" for candidate in candidates)
    assert all(
        candidate.features["calibrated_high_recall"] == 1.0
        for candidate in candidates
    )
    assert all(candidate.features["sequence_eligible"] == 1.0 for candidate in candidates)
    assert any(
        candidate.features["vertical_reserve"] == 1.0
        for candidate in candidates
    )


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


def test_phase_transition_scan_recovers_diffuse_non_peak_boundary() -> None:
    height, width = 96, 50
    gray = np.full((height, width), 70, dtype=np.uint8)
    for row in range(38, 59):
        gray[row] = 70 + int(round((row - 38) * 3.0))
    gray[59:] = 130
    zero = np.zeros_like(gray)
    pre = PreprocessResult(
        gray=gray,
        normalized=gray,
        blurred=gray,
        sobel_y_signed=zero.astype(np.float32),
        sobel_y_abs=zero,
        canny=zero,
        horizontal_mask=zero,
        glare_mask=zero.copy(),
    )
    mask = np.full_like(gray, 255)

    assert generate_calibrated_high_recall_candidates(
        pre,
        mask,
        None,
        crop_origin_y=0.0,
        limit=6,
    ) == ()
    candidates = generate_phase_transition_candidates(
        pre,
        mask,
        None,
        crop_origin_y=100.0,
        limit=4,
    )

    assert candidates
    assert any(138.0 <= candidate.y <= 160.0 for candidate in candidates)
    assert all(candidate.source == "phase_transition_scan" for candidate in candidates)
    assert all(candidate.features["phase_transition_scan"] == 1.0 for candidate in candidates)
    assert len(candidates) <= 4


def test_phase_transition_scan_rejects_flat_and_single_sector_scratch() -> None:
    height, width = 96, 50
    flat = np.full((height, width), 90, dtype=np.uint8)
    scratch = flat.copy()
    scratch[48:, :8] = 150
    mask = np.full_like(flat, 255)
    zero = np.zeros_like(flat)

    def preprocessed(gray: np.ndarray) -> PreprocessResult:
        return PreprocessResult(
            gray=gray,
            normalized=gray,
            blurred=gray,
            sobel_y_signed=zero.astype(np.float32),
            sobel_y_abs=zero,
            canny=zero,
            horizontal_mask=zero,
            glare_mask=zero.copy(),
        )

    assert generate_phase_transition_candidates(
        preprocessed(flat),
        mask,
        None,
        crop_origin_y=0.0,
    ) == ()
    assert generate_phase_transition_candidates(
        preprocessed(scratch),
        mask,
        None,
        crop_origin_y=0.0,
    ) == ()
