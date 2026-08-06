from __future__ import annotations

from dataclasses import replace

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.vision.foam_front_detector import (
    FoamDecisionStatus,
    FoamEvidenceStrength,
    detect_bottom_connected_foam,
    evaluate_foam_oil_context_authority,
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


def test_dark_yellow_textured_foam_survives_without_whiteness_membership():
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    yy, xx = np.indices((60, width))
    pattern = ((xx // 3 + yy // 3) % 2) == 0
    warm = np.where(
        pattern[..., None],
        np.array((60, 85, 105), dtype=np.uint8),
        np.array((35, 55, 80), dtype=np.uint8),
    )
    image[60:120, :, :] = warm

    result = _detect(image)

    assert result.candidate is not None
    assert result.selected_component is not None
    assert not result.selected_component.bottom_connected
    assert result.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert result.whiteness_ratio == 0.0
    assert result.texture_support_ratio >= 0.28
    assert result.front_y == 60.0


def test_substantial_detached_white_layer_uses_lower_edge_as_foam_front():
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    yy, xx = np.indices((50, 76))
    pattern = ((xx // 3 + yy // 3) % 2) == 0
    layer = np.where(pattern[..., None], 220, 150).astype(np.uint8)
    layer = np.repeat(layer, 3, axis=2)
    image[50:100, 22:98] = layer

    result = _detect(image)

    assert result.candidate is not None
    assert result.selected_component is not None
    assert not result.selected_component.bottom_connected
    assert result.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert result.component_height_ratio == pytest.approx(50 / height)
    assert result.component_width_ratio == pytest.approx(76 / width)
    assert result.front_y == 99.0

    too_thin = np.full((height, width, 3), 45, dtype=np.uint8)
    too_thin[70:95, 22:98] = layer[:25]
    thin_result = _detect(too_thin)
    assert thin_result.candidate is None


def test_wide_hollow_rim_is_rejected_but_filled_foam_can_replace_its_authority():
    height, width = 160, 120
    yy, xx = np.indices((height, width))
    bright = np.where((((xx // 3 + yy // 3) % 2) == 0)[..., None], 220, 150).astype(np.uint8)
    bright = np.repeat(bright, 3, axis=2)
    structural = np.full((height, width, 3), 45, dtype=np.uint8)
    rim = np.zeros((height, width), dtype=bool)
    rim[55:150, 8:17] = True
    rim[55:150, 103:112] = True
    rim[141:150, 8:112] = True
    structural[rim] = bright[rim]

    rejected = _detect(structural)
    assert rejected.candidate is None
    assert rejected.decision_status is FoamDecisionStatus.WEAK_REJECTED
    assert rejected.final_evidence_score >= 0.80
    assert rejected.component_width_ratio >= 0.70
    assert rejected.bounding_box_fill_ratio < 0.30

    with_foam = structural.copy()
    warm = np.where(
        ((((xx // 3 + yy // 3) % 2) == 0)[..., None]),
        np.array((60, 85, 105), dtype=np.uint8),
        np.array((35, 55, 80), dtype=np.uint8),
    )
    foam_region = (yy >= 80) & (yy < 145) & (xx >= 20) & (xx < 100)
    with_foam[foam_region] = warm[foam_region]
    accepted = _detect(with_foam)
    assert accepted.candidate is not None
    assert accepted.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert accepted.bounding_box_fill_ratio > 0.30


def test_genuine_foam_retains_oil_context_authority():
    full = _detect(_white_foam())
    low_light = _detect(_white_foam(level=165))
    partial = _white_foam()
    partial[80:, 60:] = 45
    partial_result = _detect(partial)

    for result in (full, low_light, partial_result):
        assert result.candidate is not None
        authority = evaluate_foam_oil_context_authority(result)
        assert authority.authoritative
        assert authority.reason == "foam_context_structurally_consistent"


def test_wide_hollow_structural_component_cannot_gain_oil_context_authority():
    accepted = _detect(_white_foam())
    assert accepted.candidate is not None

    mask = np.zeros_like(accepted.mask)
    mask[60:150, 10:16] = 255
    mask[60:150, 104:110] = 255
    mask[144:150, 10:110] = 255
    bbox_area = (150 - 60) * (110 - 10)
    structural = replace(
        accepted,
        mask=mask,
        component_width_ratio=(110 - 10) / mask.shape[1],
        bounding_box_fill_ratio=float(np.count_nonzero(mask)) / bbox_area,
    )

    authority = evaluate_foam_oil_context_authority(structural)
    assert structural.candidate is not None  # D1 remains defense in depth for handoff inputs.
    assert not authority.authoritative
    assert authority.reason == "wide_hollow_structural_or_refractive_component"
    assert authority.wide_row_fraction >= 0.25
    assert authority.wide_row_compactness_median < 0.65


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
