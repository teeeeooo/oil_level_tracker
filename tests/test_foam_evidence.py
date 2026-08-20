from __future__ import annotations

from dataclasses import replace

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.vision.foam_front_detector import (
    FoamDecisionStatus,
    FoamEvidenceStrength,
    detect_bottom_connected_foam,
    evaluate_foam_layer_coherence,
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
    assert result.selected_component is not None
    assert result.selected_component.bottom_connected
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


def test_dark_yellow_tapered_foam_survives_without_whiteness_membership():
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    warm_a = np.array((60, 85, 105), dtype=np.uint8)
    warm_b = np.array((35, 55, 80), dtype=np.uint8)
    for y in range(45, 115):
        fraction = (y - 45) / 70.0
        half_width = int(round(48 - 27 * fraction))
        for x in range(60 - half_width, 60 + half_width):
            image[y, x] = warm_a if ((x // 3 + y // 3) % 2 == 0) else warm_b

    result = _detect(image)

    assert result.candidate is not None
    assert result.selected_component is not None
    assert not result.selected_component.bottom_connected
    assert result.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert result.whiteness_ratio == 0.0
    assert result.texture_support_ratio >= 0.28
    assert result.front_y == 45.0


def test_compact_detached_white_droplet_is_preserved_as_material_candidate():
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    cv2.ellipse(image, (34, 75), (18, 30), 0, 0, 360, (210, 210, 210), -1)
    for y in range(50, 100, 7):
        cv2.circle(image, (34 + (y % 3) - 1, y), 3, (245, 245, 245), 1)

    result = _detect(image)

    assert result.candidate is not None
    assert result.selected_component is not None
    assert result.selected_component.material_phenotype == "detached_droplet"
    assert result.candidate.features["foam_detached_droplet"] == 1.0
    assert not result.selected_component.bottom_connected


def test_bottom_connected_dark_yellow_tapered_foam_requires_and_keeps_layer_topology():
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    warm_a = np.array((60, 85, 105), dtype=np.uint8)
    warm_b = np.array((35, 55, 80), dtype=np.uint8)
    for y in range(55, height):
        fraction = (y - 55) / (height - 55)
        half_width = int(round(48 - 34 * fraction))
        for x in range(60 - half_width, 60 + half_width):
            image[y, x] = warm_a if ((x // 3 + y // 3) % 2 == 0) else warm_b

    result = _detect(image)
    assert result.candidate is not None
    assert result.selected_component is not None
    assert result.selected_component.bottom_connected
    assert result.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert result.whiteness_ratio == 0.0
    assert result.texture_support_ratio >= 0.28
    assert result.front_y == 55.0


@pytest.mark.parametrize("pattern", ("vertical", "horizontal", "grid", "random"))
def test_representative_detached_warm_structure_cannot_gain_foam_authority(pattern: str):
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    warm = np.array((60, 85, 105), dtype=np.uint8)
    y0, y1, x0, x1 = 40, 120, 15, 105
    mask = np.zeros((height, width), dtype=bool)
    if pattern in {"vertical", "grid"}:
        for x in range(x0, x1, 10):
            mask[y0:y1, x : x + 3] = True
    if pattern in {"horizontal", "grid"}:
        for y in range(y0, y1, 10):
            mask[y : y + 3, x0:x1] = True
    if pattern == "random":
        rng = np.random.default_rng(211)
        mask[y0:y1, x0:x1] = rng.random((y1 - y0, x1 - x0)) > 0.55
    image[mask] = warm

    result = _detect(image)
    assert result.candidate is None
    assert result.decision_status not in {
        FoamDecisionStatus.ACCEPTED_STRONG,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }


@pytest.mark.parametrize("pattern", ("vertical", "horizontal", "grid", "random", "panel"))
def test_representative_bottom_connected_warm_structure_remains_non_authoritative(pattern: str):
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    warm = np.array((60, 85, 105), dtype=np.uint8)
    y0, y1, x0, x1 = 70, height, 15, 105
    if pattern in {"vertical", "grid"}:
        for x in range(x0, x1, 10):
            image[y0:y1, x : x + 3] = warm
    if pattern in {"horizontal", "grid"}:
        for y in range(y0, y1, 10):
            image[y : y + 3, x0:x1] = warm
    if pattern == "random":
        rng = np.random.default_rng(211)
        mask = rng.random((y1 - y0, x1 - x0)) > 0.55
        image[y0:y1, x0:x1][mask] = warm
    elif pattern == "panel":
        yy, xx = np.indices((y1 - y0, x1 - x0))
        checker = ((xx // 3 + yy // 3) % 2) == 0
        image[y0:y1, x0:x1] = np.where(
            checker[..., None],
            np.array((60, 85, 105), dtype=np.uint8),
            np.array((35, 55, 80), dtype=np.uint8),
        )

    result = _detect(image)
    assert result.candidate is None
    assert result.decision_status not in {
        FoamDecisionStatus.ACCEPTED_STRONG,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }


@pytest.mark.parametrize("appearance", ("white", "warm"))
def test_detached_layer_front_uses_structural_substrate_context_not_color_path(
    appearance: str,
):
    height, width = 160, 120
    image = np.full((height, width, 3), 45, dtype=np.uint8)
    warm_a = np.array((60, 85, 105), dtype=np.uint8)
    warm_b = np.array((35, 55, 80), dtype=np.uint8)
    for y in range(45, 90):
        fraction = (y - 45) / 45.0
        half_width = int(round(22 + 23 * fraction))
        for x in range(60 - half_width, 60 + half_width):
            if appearance == "white":
                image[y, x] = 220 if ((x // 3 + y // 3) % 2 == 0) else 150
            else:
                image[y, x] = warm_a if ((x // 3 + y // 3) % 2 == 0) else warm_b

    yy, xx = np.indices((height, width))
    bright = np.where((((xx // 3 + yy // 3) % 2) == 0)[..., None], 220, 150).astype(np.uint8)
    bright = np.repeat(bright, 3, axis=2)
    rim = np.zeros((height, width), dtype=bool)
    rim[96:150, 8:16] = True
    rim[96:150, 104:112] = True
    rim[142:150, 8:112] = True
    image[rim] = bright[rim]

    result = _detect(image)

    assert result.candidate is not None
    assert result.selected_component is not None
    assert not result.selected_component.bottom_connected
    assert result.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert result.front_y == 89.0


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


def test_genuine_foam_retains_layer_coherence():
    full = _detect(_white_foam())
    low_light = _detect(_white_foam(level=165))
    partial = _white_foam()
    partial[80:, 60:] = 45
    partial_result = _detect(partial)

    for result in (full, low_light, partial_result):
        assert result.candidate is not None
        assert evaluate_foam_layer_coherence(result).coherent


def test_foam_publication_requires_wide_rows_or_a_narrow_compact_layer():
    accepted = _detect(_white_foam())
    assert accepted.candidate is not None
    assert evaluate_foam_layer_coherence(accepted).coherent

    fragmented_mask = np.zeros_like(accepted.mask)
    for y in range(80, 150):
        offset = (y * 7) % 62
        fragmented_mask[y, 10 + offset : 13 + offset] = 255
    fragmented = replace(
        accepted,
        mask=fragmented_mask,
        component_width_ratio=0.78,
        bounding_box_fill_ratio=0.08,
    )
    fragmented_coherence = evaluate_foam_layer_coherence(fragmented)
    assert not fragmented_coherence.coherent
    assert fragmented_coherence.reason == "foam_layer_row_topology_fragmented"

    narrow_mask = np.zeros_like(accepted.mask)
    narrow_mask[80:150, 40:80] = 255
    narrow = replace(
        accepted,
        mask=narrow_mask,
        component_width_ratio=1.0 / 3.0,
        bounding_box_fill_ratio=1.0,
    )
    narrow_coherence = evaluate_foam_layer_coherence(narrow)
    assert narrow_coherence.coherent
    assert narrow_coherence.wide_row_compactness_median == 1.0


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
