from __future__ import annotations

import cv2
import numpy as np

from oil_tracker.adapters.vision.foam_front_detector import (
    FoamDecisionStatus,
    FoamEvidenceStrength,
    detect_bottom_connected_foam,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _settings() -> DetectorSettings:
    return DetectorSettings(
        foam_min_evidence_score=0.36,
        foam_strong_evidence_score=0.55,
        foam_min_whiteness_ratio=0.20,
        foam_max_glare_overlap_ratio=0.20,
    )


def _detect(crop: np.ndarray, settings: DetectorSettings | None = None):
    settings = settings or _settings()
    mask = np.full(crop.shape[:2], 255, dtype=np.uint8)
    pre = preprocess(crop, mask, settings)
    return detect_bottom_connected_foam(
        crop, pre.gray, pre.canny, pre.glare_mask, mask, settings
    )


def _white_foam(height: int = 160, width: int = 120, *, level: int = 220) -> np.ndarray:
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    top = height // 2
    yy, xx = np.indices((height - top, width))
    pattern = ((xx // 3 + yy // 3) % 2).astype(np.uint8)
    values = np.where(pattern[..., None] == 0, level, max(80, level - 75)).astype(np.uint8)
    image[top:, :, :] = values
    for y in range(top + 5, height, 13):
        for x in range(4, width, 15):
            cv2.circle(image, (x, y), 3, (245, 245, 245), 1)
    return image


def test_diffuse_white_bottom_connected_foam_has_strong_combined_evidence():
    result = _detect(_white_foam())
    assert result.candidate is not None
    assert result.evidence_strength in {FoamEvidenceStrength.MODERATE, FoamEvidenceStrength.STRONG}
    assert result.decision_status in {
        FoamDecisionStatus.MODERATE_EVIDENCE,
        FoamDecisionStatus.ACCEPTED_STRONG,
    }
    assert result.whiteness_ratio >= 0.20
    assert result.texture_support_ratio >= 0.22
    assert result.bottom_connected_area_ratio > 0
    assert 0.0 <= result.final_evidence_score <= 1.0


def test_low_light_white_foam_and_partial_front_remain_supported():
    low = _detect(_white_foam(level=165))
    partial = _white_foam()
    partial[:80, 60:] = 45
    partial_result = _detect(partial)
    assert low.candidate is not None
    assert low.decision_status is not FoamDecisionStatus.GLARE_REJECTED
    assert partial_result.candidate is not None
    assert partial_result.component_width_ratio > 0.25


def test_saturated_high_variance_shimmer_is_not_accepted_as_foam():
    height, width = 160, 120
    image = np.zeros((height, width, 3), dtype=np.uint8)
    yy, xx = np.indices((height, width))
    image[:, :, 0] = np.where((xx + yy) % 4 < 2, 245, 25)
    image[:, :, 1] = np.where((xx * 2 + yy) % 5 < 2, 70, 180)
    image[:, :, 2] = 20
    result = _detect(image)
    assert result.decision_status not in {
        FoamDecisionStatus.ACCEPTED_STRONG,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }
    assert result.whiteness_ratio < 0.20


def test_variance_only_and_edge_only_do_not_create_strong_foam():
    height, width = 160, 120
    variance_only = np.full((height, width, 3), 70, dtype=np.uint8)
    rng = np.random.default_rng(1234)
    noise = rng.integers(0, 100, size=(height // 2, width), dtype=np.uint8)
    variance_only[height // 2 :, :, 1] = noise
    edge_only = np.full((height, width, 3), 70, dtype=np.uint8)
    cv2.line(edge_only, (0, height - 20), (width - 1, height - 20), (220, 220, 220), 1)
    assert _detect(variance_only).decision_status is not FoamDecisionStatus.ACCEPTED_STRONG
    assert _detect(edge_only).decision_status is not FoamDecisionStatus.ACCEPTED_STRONG


def test_clipped_glare_and_thin_horizontal_structure_are_rejected():
    settings = _settings()
    settings.foam_max_glare_overlap_ratio = 0.05
    glare = _white_foam()
    glare[80:, ::2] = 255
    glare_result = _detect(glare, settings)
    assert glare_result.decision_status in {
        FoamDecisionStatus.GLARE_REJECTED,
        FoamDecisionStatus.WEAK_REJECTED,
        FoamDecisionStatus.AMBIGUOUS,
    }

    line = np.full((160, 120, 3), 55, dtype=np.uint8)
    cv2.rectangle(line, (2, 142), (117, 147), (215, 215, 215), -1)
    line_result = _detect(line)
    assert line_result.decision_status not in {
        FoamDecisionStatus.ACCEPTED_STRONG,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }


def test_grayscale_fallback_shapes_dtype_finite_and_input_immutability():
    color = _white_foam()
    gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    before = gray.copy()
    settings = _settings()
    mask = np.full(gray.shape, 255, dtype=np.uint8)
    pre = preprocess(gray, mask, settings)
    result = detect_bottom_connected_foam(
        gray, pre.gray, pre.canny, pre.glare_mask, mask, settings
    )
    assert np.array_equal(gray, before)
    for image in (
        result.variance_map,
        result.edge_density_map,
        result.whiteness_map,
        result.texture_evidence_map,
        result.combined_evidence_map,
    ):
        assert image.shape == gray.shape
        assert np.isfinite(image).all()
    assert result.mask.shape == gray.shape
    assert result.mask.dtype == np.uint8
    assert result.glare_excluded_mask.dtype == np.uint8


def test_relative_texture_kernels_support_small_and_large_regions():
    small = _detect(_white_foam(80, 60))
    large = _detect(_white_foam(320, 240))
    assert small.candidate is not None
    assert large.candidate is not None
    assert small.texture_evidence_map.shape == (80, 60)
    assert large.texture_evidence_map.shape == (320, 240)
