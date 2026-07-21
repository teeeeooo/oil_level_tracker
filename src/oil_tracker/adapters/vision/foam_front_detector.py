from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


class FoamEvidenceStrength(str, Enum):
    NONE = "none"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class FoamDecisionStatus(str, Enum):
    NO_EVIDENCE = "no_evidence"
    WEAK_REJECTED = "weak_rejected"
    AMBIGUOUS = "ambiguous"
    MODERATE_EVIDENCE = "moderate_evidence"
    PERSISTENCE_PENDING = "persistence_pending"
    ACCEPTED_MODERATE = "accepted_moderate"
    ACCEPTED_STRONG = "accepted_strong"
    GLARE_REJECTED = "glare_rejected"


@dataclass(frozen=True)
class FoamComponentEvidence:
    label: int
    area_ratio: float
    height_ratio: float
    width_ratio: float
    bounding_box_fill_ratio: float
    bottom_connected: bool
    whiteness_ratio: float
    texture_support_ratio: float
    glare_overlap_ratio: float
    front_vertical_extent: float
    thin_horizontal: bool
    front_y: float
    final_score: float
    decision_status: FoamDecisionStatus


@dataclass(frozen=True)
class FoamDetectionResult:
    mask: np.ndarray
    variance_map: np.ndarray
    edge_density_map: np.ndarray
    whiteness_map: np.ndarray
    texture_evidence_map: np.ndarray
    glare_excluded_mask: np.ndarray
    combined_evidence_map: np.ndarray
    candidate: BoundaryCandidate | None
    components: tuple[FoamComponentEvidence, ...]
    selected_component: FoamComponentEvidence | None
    final_evidence_score: float
    evidence_strength: FoamEvidenceStrength
    decision_status: FoamDecisionStatus
    ambiguous: bool
    bottom_connected_area_ratio: float
    whiteness_ratio: float
    texture_support_ratio: float
    glare_overlap_ratio: float
    component_height_ratio: float
    component_width_ratio: float
    bounding_box_fill_ratio: float
    front_y: float | None

    def __post_init__(self) -> None:
        if self.decision_status in {
            FoamDecisionStatus.WEAK_REJECTED,
            FoamDecisionStatus.AMBIGUOUS,
            FoamDecisionStatus.GLARE_REJECTED,
        }:
            object.__setattr__(self, "candidate", None)
            object.__setattr__(self, "mask", np.zeros_like(self.mask, dtype=np.uint8))


def detect_bottom_connected_foam(
    crop: np.ndarray,
    gray: np.ndarray,
    canny: np.ndarray | None = None,
    glare_mask: np.ndarray | DetectorSettings | None = None,
    effective_mask: np.ndarray | None = None,
    settings: DetectorSettings | None = None,
) -> FoamDetectionResult:
    """Evaluate generalized Foam evidence without mutating any input array.

    The preferred S5-A call supplies BGR/grayscale crop, gray, Canny, glare mask,
    effective mask and settings. The legacy four-argument adapter helper call
    ``(gray, canny, effective_mask, settings)`` remains supported for existing
    callers and uses the documented grayscale/no-glare fallback.
    """

    if settings is None and isinstance(glare_mask, DetectorSettings):
        legacy_gray = crop
        legacy_canny = gray
        legacy_effective_mask = canny
        settings = glare_mask
        crop = legacy_gray
        gray = legacy_gray
        canny = legacy_canny
        effective_mask = legacy_effective_mask
        glare_mask = np.zeros_like(legacy_gray, dtype=np.uint8)
    if settings is None or canny is None or glare_mask is None or effective_mask is None:
        raise TypeError(
            "detect_bottom_connected_foam requires either the six-argument S5-A "
            "contract or the legacy four-argument grayscale contract."
        )

    _validate_shapes(crop, gray, canny, glare_mask, effective_mask)
    valid = effective_mask > 0
    effective_area = max(1, int(np.count_nonzero(valid)))
    if not np.any(valid):
        return _empty_result(gray.shape)

    lightness, chroma = _lightness_and_chroma(crop, gray)
    raw_whiteness = _whiteness_score(lightness, chroma, settings)
    glare = (glare_mask > 0) & valid
    glare_excluded = valid & ~glare
    whiteness = np.where(glare_excluded, raw_whiteness, 0.0).astype(np.float32)

    variance, edge_density, texture = _texture_evidence(gray, canny, valid, settings)
    combined = np.clip(
        0.50 * whiteness + 0.35 * texture + 0.15 * np.minimum(whiteness, texture),
        0.0,
        1.0,
    ).astype(np.float32)

    raw_support = (
        valid
        & (raw_whiteness >= 0.12)
        & (texture >= 0.18)
        & ((0.50 * raw_whiteness + 0.35 * texture) >= 0.24)
    )
    support = raw_support.astype(np.uint8) * 255
    support = _clean_support_mask(support, min(gray.shape[:2]))
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        (support > 0).astype(np.uint8), connectivity=8
    )

    h, w = gray.shape[:2]
    bottom_band = np.zeros((h, w), dtype=bool)
    bottom_start = max(0, int(math.floor(h * 0.78)))
    bottom_band[bottom_start:, :] = valid[bottom_start:, :]

    component_rows: list[FoamComponentEvidence] = []
    component_masks: dict[int, np.ndarray] = {}
    for label in range(1, count):
        component = labels == label
        evidence = _component_evidence(
            label,
            component,
            stats[label],
            valid,
            bottom_band,
            whiteness,
            texture,
            glare,
            effective_area,
            settings,
        )
        component_rows.append(evidence)
        component_masks[label] = component

    component_rows.sort(key=_component_sort_key)
    selected = component_rows[0] if component_rows else None
    if selected is None:
        return FoamDetectionResult(
            mask=np.zeros_like(gray, dtype=np.uint8),
            variance_map=variance,
            edge_density_map=edge_density,
            whiteness_map=whiteness,
            texture_evidence_map=texture,
            glare_excluded_mask=glare_excluded.astype(np.uint8) * 255,
            combined_evidence_map=combined,
            candidate=None,
            components=(),
            selected_component=None,
            final_evidence_score=0.0,
            evidence_strength=FoamEvidenceStrength.NONE,
            decision_status=FoamDecisionStatus.NO_EVIDENCE,
            ambiguous=False,
            bottom_connected_area_ratio=0.0,
            whiteness_ratio=0.0,
            texture_support_ratio=0.0,
            glare_overlap_ratio=0.0,
            component_height_ratio=0.0,
            component_width_ratio=0.0,
            bounding_box_fill_ratio=0.0,
            front_y=None,
        )

    selected_mask = component_masks[selected.label] & glare_excluded
    mask = selected_mask.astype(np.uint8) * 255
    status = selected.decision_status
    strength = _strength_for_status(status)
    candidate = BoundaryCandidate(
        source="foam_evidence",
        kind=BoundaryKind.FOAM_FRONT,
        y=float(selected.front_y),
        features={
            "foam_score": float(selected.final_score),
            "bottom_connectivity": 1.0 if selected.bottom_connected else 0.0,
            "area_ratio": float(selected.area_ratio),
            "component_height_ratio": float(selected.height_ratio),
            "component_width_ratio": float(selected.width_ratio),
            "bounding_box_fill_ratio": float(selected.bounding_box_fill_ratio),
            "whiteness_ratio": float(selected.whiteness_ratio),
            "texture_support_ratio": float(selected.texture_support_ratio),
            "glare_overlap_ratio": float(selected.glare_overlap_ratio),
            "front_vertical_extent": float(selected.front_vertical_extent),
            "thin_horizontal": 1.0 if selected.thin_horizontal else 0.0,
        },
        feature_score=float(selected.final_score),
        final_score=float(selected.final_score),
        rejected=status
        in {
            FoamDecisionStatus.WEAK_REJECTED,
            FoamDecisionStatus.GLARE_REJECTED,
            FoamDecisionStatus.AMBIGUOUS,
        },
        reject_reason=_reject_reason(status),
    )
    return FoamDetectionResult(
        mask=mask,
        variance_map=variance,
        edge_density_map=edge_density,
        whiteness_map=whiteness,
        texture_evidence_map=texture,
        glare_excluded_mask=glare_excluded.astype(np.uint8) * 255,
        combined_evidence_map=combined,
        candidate=candidate,
        components=tuple(component_rows),
        selected_component=selected,
        final_evidence_score=float(selected.final_score),
        evidence_strength=strength,
        decision_status=status,
        ambiguous=status is FoamDecisionStatus.AMBIGUOUS,
        bottom_connected_area_ratio=float(selected.area_ratio),
        whiteness_ratio=float(selected.whiteness_ratio),
        texture_support_ratio=float(selected.texture_support_ratio),
        glare_overlap_ratio=float(selected.glare_overlap_ratio),
        component_height_ratio=float(selected.height_ratio),
        component_width_ratio=float(selected.width_ratio),
        bounding_box_fill_ratio=float(selected.bounding_box_fill_ratio),
        front_y=float(selected.front_y),
    )


def _empty_result(shape: tuple[int, int]) -> FoamDetectionResult:
    zeros_u8 = np.zeros(shape, dtype=np.uint8)
    zeros_f = np.zeros(shape, dtype=np.float32)
    return FoamDetectionResult(
        mask=zeros_u8,
        variance_map=zeros_f,
        edge_density_map=zeros_f.copy(),
        whiteness_map=zeros_f.copy(),
        texture_evidence_map=zeros_f.copy(),
        glare_excluded_mask=zeros_u8.copy(),
        combined_evidence_map=zeros_f.copy(),
        candidate=None,
        components=(),
        selected_component=None,
        final_evidence_score=0.0,
        evidence_strength=FoamEvidenceStrength.NONE,
        decision_status=FoamDecisionStatus.NO_EVIDENCE,
        ambiguous=False,
        bottom_connected_area_ratio=0.0,
        whiteness_ratio=0.0,
        texture_support_ratio=0.0,
        glare_overlap_ratio=0.0,
        component_height_ratio=0.0,
        component_width_ratio=0.0,
        bounding_box_fill_ratio=0.0,
        front_y=None,
    )


def _validate_shapes(crop, gray, canny, glare_mask, effective_mask) -> None:
    shape = gray.shape[:2]
    if gray.ndim != 2:
        raise ValueError("Foam grayscale input must be two-dimensional.")
    if crop.shape[:2] != shape:
        raise ValueError("Foam crop and grayscale shapes must match.")
    for name, image in (
        ("canny", canny),
        ("glare_mask", glare_mask),
        ("effective_mask", effective_mask),
    ):
        if image.shape[:2] != shape:
            raise ValueError(f"Foam {name} shape must match the crop.")


def _lightness_and_chroma(crop: np.ndarray, gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if crop.ndim == 2:
        return gray.astype(np.float32), np.zeros_like(gray, dtype=np.float32)
    if crop.ndim != 3 or crop.shape[2] not in (3, 4):
        raise ValueError("Foam crop must be grayscale, BGR or BGRA.")
    bgr = crop[:, :, :3]
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    a = lab[:, :, 1] - 128.0
    b = lab[:, :, 2] - 128.0
    return lab[:, :, 0], np.sqrt(a * a + b * b).astype(np.float32)


def _whiteness_score(
    lightness: np.ndarray,
    chroma: np.ndarray,
    settings: DetectorSettings,
) -> np.ndarray:
    light_floor = float(settings.foam_lightness_threshold)
    chroma_ceiling = max(1e-6, float(settings.foam_max_chroma))
    light_score = np.clip(
        (lightness.astype(np.float32) - light_floor) / max(1.0, 255.0 - light_floor),
        0.0,
        1.0,
    )
    chroma_score = np.clip(1.0 - chroma.astype(np.float32) / chroma_ceiling, 0.0, 1.0)
    return np.sqrt(light_score * chroma_score).astype(np.float32)


def _texture_evidence(
    gray: np.ndarray,
    canny: np.ndarray,
    valid: np.ndarray,
    settings: DetectorSettings,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = gray.shape[:2]
    base = max(3, min(h, w))
    small = _odd_kernel(max(3, int(round(base * 0.035))), upper=15)
    large = _odd_kernel(max(small + 2, int(round(base * 0.085))), upper=31)
    gray_f = gray.astype(np.float32)
    var_small = _local_variance(gray_f, small)
    var_large = _local_variance(gray_f, large)
    edge_f = (canny > 0).astype(np.float32)
    edge_small = cv2.boxFilter(edge_f, -1, (small, small), normalize=True)
    edge_large = cv2.boxFilter(edge_f, -1, (large, large), normalize=True)

    variance = 0.55 * var_small + 0.45 * var_large
    edge_density = 0.55 * edge_small + 0.45 * edge_large
    variance_score = np.clip(
        variance / max(1e-6, float(settings.foam_variance_threshold)), 0.0, 1.0
    )
    edge_score = np.clip(
        edge_density / max(1e-6, float(settings.foam_edge_density_threshold)), 0.0, 1.0
    )
    scale_consistency = np.minimum(
        np.clip(var_small / max(1e-6, float(settings.foam_variance_threshold)), 0.0, 1.0),
        np.clip(var_large / max(1e-6, float(settings.foam_variance_threshold)), 0.0, 1.0),
    )
    texture = np.clip(
        0.40 * np.sqrt(variance_score * edge_score)
        + 0.35 * np.minimum(variance_score, edge_score)
        + 0.25 * scale_consistency,
        0.0,
        1.0,
    )
    variance = np.where(valid, variance, 0.0).astype(np.float32)
    edge_density = np.where(valid, edge_density, 0.0).astype(np.float32)
    texture = np.where(valid, texture, 0.0).astype(np.float32)
    return variance, edge_density, texture


def _local_variance(gray_f: np.ndarray, kernel: int) -> np.ndarray:
    mean = cv2.boxFilter(gray_f, -1, (kernel, kernel), normalize=True)
    mean_sq = cv2.boxFilter(gray_f * gray_f, -1, (kernel, kernel), normalize=True)
    return np.maximum(0.0, mean_sq - mean * mean).astype(np.float32)


def _odd_kernel(value: int, *, upper: int) -> int:
    value = min(max(3, int(value)), int(upper))
    return value if value % 2 else value + 1 if value < upper else value - 1


def _clean_support_mask(mask: np.ndarray, base: int) -> np.ndarray:
    close_size = _odd_kernel(max(3, int(round(base * 0.025))), upper=9)
    open_size = _odd_kernel(max(3, int(round(base * 0.012))), upper=5)
    closed = cv2.morphologyEx(
        mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_size, close_size))
    )
    return cv2.morphologyEx(
        closed, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_size, open_size))
    )


def _component_evidence(
    label: int,
    component: np.ndarray,
    stats: np.ndarray,
    valid: np.ndarray,
    bottom_band: np.ndarray,
    whiteness: np.ndarray,
    texture: np.ndarray,
    glare: np.ndarray,
    effective_area: int,
    settings: DetectorSettings,
) -> FoamComponentEvidence:
    h, w = valid.shape
    area = int(stats[cv2.CC_STAT_AREA])
    width = int(stats[cv2.CC_STAT_WIDTH])
    height = int(stats[cv2.CC_STAT_HEIGHT])
    area_ratio = area / max(1, effective_area)
    height_ratio = height / max(1, h)
    width_ratio = width / max(1, w)
    fill_ratio = area / max(1, width * height)
    bottom_connected = bool(np.any(component & bottom_band))
    pixel_count = max(1, int(np.count_nonzero(component)))
    whiteness_ratio = float(np.count_nonzero(component & (whiteness >= 0.18))) / pixel_count
    texture_ratio = float(np.count_nonzero(component & (texture >= 0.22))) / pixel_count
    glare_ratio = float(np.count_nonzero(component & glare)) / pixel_count
    ys = np.where(component)[0]
    front_y = float(ys.min()) if ys.size else float(h - 1)
    vertical_extent = (h - front_y) / max(1.0, float(h))
    thin_horizontal = height_ratio < 0.075 and width_ratio >= 0.30

    min_area = max(1e-6, float(settings.foam_min_area_ratio))
    area_score = _unit(area_ratio / max(min_area * 3.0, 1e-6))
    height_score = _unit(height_ratio / 0.28)
    width_score = _unit(width_ratio / 0.55)
    fill_score = _unit((fill_ratio - 0.12) / 0.58)
    bottom_score = 1.0 if bottom_connected else 0.0
    score = (
        0.22 * whiteness_ratio
        + 0.22 * texture_ratio
        + 0.14 * area_score
        + 0.11 * height_score
        + 0.09 * width_score
        + 0.08 * fill_score
        + 0.09 * bottom_score
        + 0.05 * _unit(vertical_extent / 0.35)
        - 0.38 * glare_ratio
        - (0.28 if thin_horizontal else 0.0)
    )
    score = _unit(score)

    if glare_ratio > float(settings.foam_max_glare_overlap_ratio):
        status = FoamDecisionStatus.GLARE_REJECTED
    else:
        minimum = float(settings.foam_min_evidence_score)
        strong = float(settings.foam_strong_evidence_score)
        shape_ok = bottom_connected and area_ratio >= min_area and height_ratio >= 0.075 and not thin_horizontal
        white_ok = whiteness_ratio >= float(settings.foam_min_whiteness_ratio)
        texture_ok = texture_ratio >= 0.28
        if score >= strong and shape_ok and white_ok and texture_ok:
            status = FoamDecisionStatus.ACCEPTED_STRONG
        elif score >= minimum and shape_ok and whiteness_ratio >= float(settings.foam_min_whiteness_ratio) * 0.75 and texture_ratio >= 0.22:
            status = FoamDecisionStatus.MODERATE_EVIDENCE
        elif score >= minimum * 0.80 and (white_ok != texture_ok or shape_ok):
            status = FoamDecisionStatus.AMBIGUOUS
        else:
            status = FoamDecisionStatus.WEAK_REJECTED

    return FoamComponentEvidence(
        label=int(label),
        area_ratio=float(area_ratio),
        height_ratio=float(height_ratio),
        width_ratio=float(width_ratio),
        bounding_box_fill_ratio=float(fill_ratio),
        bottom_connected=bottom_connected,
        whiteness_ratio=float(whiteness_ratio),
        texture_support_ratio=float(texture_ratio),
        glare_overlap_ratio=float(glare_ratio),
        front_vertical_extent=float(vertical_extent),
        thin_horizontal=thin_horizontal,
        front_y=float(front_y),
        final_score=float(score),
        decision_status=status,
    )


def _component_sort_key(item: FoamComponentEvidence) -> tuple[float, float, float, int]:
    priority = {
        FoamDecisionStatus.ACCEPTED_STRONG: 0,
        FoamDecisionStatus.MODERATE_EVIDENCE: 1,
        FoamDecisionStatus.AMBIGUOUS: 2,
        FoamDecisionStatus.GLARE_REJECTED: 3,
        FoamDecisionStatus.WEAK_REJECTED: 4,
    }
    return (float(priority.get(item.decision_status, 5)), -item.final_score, item.front_y, item.label)


def _strength_for_status(status: FoamDecisionStatus) -> FoamEvidenceStrength:
    if status is FoamDecisionStatus.ACCEPTED_STRONG:
        return FoamEvidenceStrength.STRONG
    if status is FoamDecisionStatus.MODERATE_EVIDENCE:
        return FoamEvidenceStrength.MODERATE
    if status in {
        FoamDecisionStatus.WEAK_REJECTED,
        FoamDecisionStatus.AMBIGUOUS,
        FoamDecisionStatus.GLARE_REJECTED,
    }:
        return FoamEvidenceStrength.WEAK
    return FoamEvidenceStrength.NONE


def _reject_reason(status: FoamDecisionStatus) -> str:
    return {
        FoamDecisionStatus.WEAK_REJECTED: "foam_evidence_below_minimum",
        FoamDecisionStatus.AMBIGUOUS: "foam_evidence_conflicting",
        FoamDecisionStatus.GLARE_REJECTED: "foam_glare_overlap_exceeded",
    }.get(status, "")


def _unit(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return max(0.0, min(1.0, float(value)))
