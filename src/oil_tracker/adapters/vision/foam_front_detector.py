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
    INCOHERENT_REJECTED = "incoherent_rejected"
    STATIC_REJECTED = "static_rejected"


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
    material_support_mask: np.ndarray
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


_OIL_CONTEXT_WIDE_COMPONENT_RATIO = 0.70
_OIL_CONTEXT_MAX_HOLLOW_FILL_RATIO = 0.30
_OIL_CONTEXT_WIDE_ROW_SPAN_RATIO = 0.35
_OIL_CONTEXT_MIN_WIDE_ROW_FRACTION = 0.25
_OIL_CONTEXT_MIN_ROW_COMPACTNESS = 0.65
_PUBLICATION_MIN_WIDE_ROW_FRACTION = 0.50
_PUBLICATION_NARROW_MAX_WIDTH_RATIO = 0.50
_PUBLICATION_NARROW_MIN_ROW_COMPACTNESS = 0.95

_CHROMATIC_SUPPORT_MIN_CHROMA_RATIO = 0.20
_CHROMATIC_SUPPORT_MIN_TEXTURE = 0.05
_CHROMATIC_SEED_MIN_TEXTURE = 0.20
_CHROMATIC_SEED_MIN_SCORE = 0.20
_CHROMATIC_COMPONENT_MIN_RATIO = 0.35
_LAYER_MIN_AREA_MULTIPLIER = 2.5
_LAYER_MAX_HEIGHT_RATIO = 0.68
_LAYER_MIN_WIDTH_RATIO = 0.55
_LAYER_MIN_DOMINANT_THIRD_OCCUPANCY = 0.20
_LAYER_MIN_EDGE_CONCENTRATION_RATIO = 1.30


@dataclass(frozen=True)
class FoamOilContextAuthority:
    authoritative: bool
    reason: str
    wide_row_fraction: float
    wide_row_compactness_median: float


@dataclass(frozen=True)
class FoamLayerCoherence:
    coherent: bool
    reason: str
    wide_row_fraction: float
    wide_row_compactness_median: float


def evaluate_foam_layer_coherence(result: FoamDetectionResult) -> FoamLayerCoherence:
    """Require an accepted component to represent a coherent material layer.

    A component may have a wide bounding box while every material row remains
    fragmented. Genuine partial Foam may instead be narrow, but its occupied
    rows must then remain compact. This publication proof is independent from
    the D1 Oil-context handoff and preserves the raw current-frame evidence.
    """

    if result.candidate is None or not np.any(result.mask):
        return FoamLayerCoherence(
            False,
            "foam_layer_not_currently_accepted",
            0.0,
            0.0,
        )
    _structural, wide_row_fraction, compactness_median = (
        _wide_hollow_component_metrics(
            result.mask > 0,
            width_ratio=float(result.component_width_ratio),
            fill_ratio=float(result.bounding_box_fill_ratio),
        )
    )
    wide_layer = wide_row_fraction >= _PUBLICATION_MIN_WIDE_ROW_FRACTION
    narrow_compact_layer = bool(
        float(result.component_width_ratio)
        <= _PUBLICATION_NARROW_MAX_WIDTH_RATIO
        and compactness_median >= _PUBLICATION_NARROW_MIN_ROW_COMPACTNESS
    )
    coherent = bool(wide_layer or narrow_compact_layer)
    return FoamLayerCoherence(
        coherent,
        (
            "foam_layer_row_topology_coherent"
            if coherent
            else "foam_layer_row_topology_fragmented"
        ),
        float(wide_row_fraction),
        float(compactness_median),
    )


def evaluate_foam_oil_context_authority(result: FoamDetectionResult) -> FoamOilContextAuthority:
    """Qualify whether accepted Foam may constrain S5-B Oil observation.

    S5-A Foam publication and S5-B routing are separate responsibilities.  A
    bright sight-glass rim can form one wide connected U-shaped component while
    remaining hollow across individual rows. S5-A rejects that known structural
    class, while this handoff check independently keeps the same class from
    masking or re-routing Oil evidence if an accepted input still reaches D1.
    """

    if result.candidate is None or not np.any(result.mask):
        return FoamOilContextAuthority(False, "foam_context_not_currently_accepted", 0.0, 0.0)

    support = result.mask > 0
    wide_hollow_structure, wide_row_fraction, compactness_median = (
        _wide_hollow_component_metrics(
            support,
            width_ratio=float(result.component_width_ratio),
            fill_ratio=float(result.bounding_box_fill_ratio),
        )
    )
    if wide_hollow_structure:
        return FoamOilContextAuthority(
            False,
            "wide_hollow_structural_or_refractive_component",
            float(wide_row_fraction),
            float(compactness_median),
        )
    return FoamOilContextAuthority(
        True,
        "foam_context_structurally_consistent",
        float(wide_row_fraction),
        float(compactness_median),
    )


def _wide_hollow_component_metrics(
    support: np.ndarray,
    *,
    width_ratio: float,
    fill_ratio: float,
) -> tuple[bool, float, float]:
    ys, xs = np.where(support)
    if ys.size == 0:
        return False, 0.0, 1.0
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    component = support[y0 : y1 + 1, x0 : x1 + 1]
    component_width = max(1, component.shape[1])
    compactness: list[float] = []
    for row in component:
        row_x = np.flatnonzero(row)
        if row_x.size == 0:
            continue
        span = int(row_x[-1] - row_x[0] + 1)
        if span / component_width < _OIL_CONTEXT_WIDE_ROW_SPAN_RATIO:
            continue
        compactness.append(float(row_x.size) / max(1, span))
    wide_row_fraction = len(compactness) / max(1, component.shape[0])
    compactness_median = (
        float(np.median(np.asarray(compactness, dtype=np.float32)))
        if compactness
        else 1.0
    )
    structural = (
        float(width_ratio) >= _OIL_CONTEXT_WIDE_COMPONENT_RATIO
        and float(fill_ratio) < _OIL_CONTEXT_MAX_HOLLOW_FILL_RATIO
        and wide_row_fraction >= _OIL_CONTEXT_MIN_WIDE_ROW_FRACTION
        and compactness_median < _OIL_CONTEXT_MIN_ROW_COMPACTNESS
    )
    return bool(structural), float(wide_row_fraction), float(compactness_median)


def _chromatic_foam_support(
    chroma: np.ndarray,
    warm_chroma: np.ndarray,
    texture: np.ndarray,
    valid: np.ndarray,
    settings: DetectorSettings,
) -> tuple[np.ndarray, np.ndarray]:
    chroma_ceiling = max(1e-6, float(settings.foam_max_chroma))
    warm_ratio = np.clip(warm_chroma.astype(np.float32) / chroma_ceiling, 0.0, 1.0)
    chromatic_band = (
        valid
        & (warm_chroma >= _CHROMATIC_SUPPORT_MIN_CHROMA_RATIO * chroma_ceiling)
        & (chroma <= chroma_ceiling)
    )
    membership = chromatic_band & (texture >= _CHROMATIC_SUPPORT_MIN_TEXTURE)
    evidence = np.where(
        chromatic_band,
        np.sqrt(warm_ratio * np.clip(texture, 0.0, 1.0)),
        0.0,
    ).astype(np.float32)
    seed = (
        membership
        & (texture >= _CHROMATIC_SEED_MIN_TEXTURE)
        & (evidence >= _CHROMATIC_SEED_MIN_SCORE)
    )
    if not np.any(seed):
        return np.zeros_like(valid, dtype=bool), evidence
    count, labels = cv2.connectedComponents(membership.astype(np.uint8), connectivity=8)
    keep = np.zeros(max(1, count), dtype=bool)
    keep[np.unique(labels[seed])] = True
    keep[0] = False
    return keep[labels], evidence


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

    lightness, chroma, warm_chroma = _lightness_and_chroma(crop, gray)
    raw_whiteness = _whiteness_score(lightness, chroma, settings)
    glare = (glare_mask > 0) & valid
    glare_excluded = valid & ~glare
    whiteness = np.where(glare_excluded, raw_whiteness, 0.0).astype(np.float32)

    variance, edge_density, texture = _texture_evidence(
        gray,
        canny,
        glare_excluded,
        settings,
    )
    chromatic_support, chromatic_evidence = _chromatic_foam_support(
        chroma, warm_chroma, texture, glare_excluded, settings
    )
    white_support = (
        glare_excluded
        & (whiteness >= 0.12)
        & (texture >= 0.18)
        & ((0.50 * whiteness + 0.35 * texture) >= 0.24)
    )
    white_clean = _clean_support_mask(
        white_support.astype(np.uint8) * 255,
        min(gray.shape[:2]),
    )
    if _has_material_nonstructural_support_component(white_clean, valid, settings):
        chromatic_support = np.zeros_like(valid, dtype=bool)
        chromatic_evidence = np.zeros_like(texture, dtype=np.float32)
        support = white_clean
    else:
        raw_support = white_support | chromatic_support
        support = _clean_support_mask(
            raw_support.astype(np.uint8) * 255,
            min(gray.shape[:2]),
        )
    support = cv2.bitwise_and(
        support,
        glare_excluded.astype(np.uint8) * 255,
    )
    combined = np.maximum(
        np.clip(
            0.50 * whiteness + 0.35 * texture + 0.15 * np.minimum(whiteness, texture),
            0.0,
            1.0,
        ),
        chromatic_evidence,
    ).astype(np.float32)
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        (support > 0).astype(np.uint8), connectivity=8
    )

    h, w = gray.shape[:2]
    bottom_band = np.zeros((h, w), dtype=bool)
    bottom_start = max(0, int(math.floor(h * 0.78)))
    bottom_band[bottom_start:, :] = valid[bottom_start:, :]

    structural_boxes = _structural_support_boxes(labels, stats, valid)
    component_rows: list[FoamComponentEvidence] = []
    component_masks: dict[int, np.ndarray] = {}
    for label in range(1, count):
        component = labels == label
        structural_substrate_present, front_from_lower_edge = _structural_substrate_relation(
            label,
            stats,
            structural_boxes,
            h,
        )
        evidence = _component_evidence(
            label,
            component,
            stats[label],
            valid,
            bottom_band,
            whiteness,
            texture,
            chromatic_support,
            glare,
            effective_area,
            settings,
            structural_substrate_present=structural_substrate_present,
            front_from_lower_edge=front_from_lower_edge,
        )
        component_rows.append(evidence)
        component_masks[label] = component

    component_rows.sort(key=_component_sort_key)
    selected = component_rows[0] if component_rows else None
    if selected is None:
        return FoamDetectionResult(
            mask=np.zeros_like(gray, dtype=np.uint8),
            material_support_mask=np.zeros_like(gray, dtype=np.uint8),
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
        material_support_mask=selected_mask.astype(np.uint8) * 255,
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
        material_support_mask=zeros_u8.copy(),
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


def _lightness_and_chroma(
    crop: np.ndarray,
    gray: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if crop.ndim == 2:
        zeros = np.zeros_like(gray, dtype=np.float32)
        return gray.astype(np.float32), zeros, zeros.copy()
    if crop.ndim != 3 or crop.shape[2] not in (3, 4):
        raise ValueError("Foam crop must be grayscale, BGR or BGRA.")
    bgr = crop[:, :, :3]
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    a = lab[:, :, 1] - 128.0
    b = lab[:, :, 2] - 128.0
    chroma = np.sqrt(a * a + b * b).astype(np.float32)
    warm_chroma = np.clip(b - np.maximum(a, 0.0), 0.0, None).astype(np.float32)
    return lab[:, :, 0], chroma, warm_chroma


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
    close_size = _odd_kernel(max(3, int(round(base * 0.040))), upper=9)
    open_size = _odd_kernel(max(3, int(round(base * 0.012))), upper=5)
    closed = cv2.morphologyEx(
        mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_size, close_size))
    )
    return cv2.morphologyEx(
        closed, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_size, open_size))
    )


def _has_material_nonstructural_support_component(
    support: np.ndarray,
    valid: np.ndarray,
    settings: DetectorSettings,
) -> bool:
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        (support > 0).astype(np.uint8), connectivity=8
    )
    effective_area = max(1, int(np.count_nonzero(valid)))
    height = max(1, int(valid.shape[0]))
    width = max(1, int(valid.shape[1]))
    min_area = max(1e-6, float(settings.foam_min_area_ratio))
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        component_width = max(1, int(stats[label, cv2.CC_STAT_WIDTH]))
        component_height = max(1, int(stats[label, cv2.CC_STAT_HEIGHT]))
        area_ratio = float(area) / effective_area
        height_ratio = float(component_height) / height
        if area_ratio < min_area or height_ratio < 0.075:
            continue
        width_ratio = float(component_width) / width
        fill_ratio = float(area) / max(1, component_width * component_height)
        structural, _wide_rows, _compactness = _wide_hollow_component_metrics(
            labels == label,
            width_ratio=width_ratio,
            fill_ratio=fill_ratio,
        )
        if not structural:
            return True
    return False


def _structural_support_boxes(
    labels: np.ndarray,
    stats: np.ndarray,
    valid: np.ndarray,
) -> tuple[tuple[int, int, int, int, int], ...]:
    _, w = valid.shape
    boxes: list[tuple[int, int, int, int, int]] = []
    for label in range(1, int(stats.shape[0])):
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        width = max(1, int(stats[label, cv2.CC_STAT_WIDTH]))
        height = max(1, int(stats[label, cv2.CC_STAT_HEIGHT]))
        area = int(stats[label, cv2.CC_STAT_AREA])
        width_ratio = width / max(1, w)
        fill_ratio = area / max(1, width * height)
        structural, _wide_rows, _compactness = _wide_hollow_component_metrics(
            labels == label,
            width_ratio=width_ratio,
            fill_ratio=fill_ratio,
        )
        if structural:
            boxes.append((label, x, x + width - 1, y, y + height - 1))
    return tuple(boxes)


def _structural_substrate_relation(
    label: int,
    stats: np.ndarray,
    structural_boxes: tuple[tuple[int, int, int, int, int], ...],
    frame_height: int,
) -> tuple[bool, bool]:
    x0 = int(stats[label, cv2.CC_STAT_LEFT])
    y0 = int(stats[label, cv2.CC_STAT_TOP])
    width = max(1, int(stats[label, cv2.CC_STAT_WIDTH]))
    height = max(1, int(stats[label, cv2.CC_STAT_HEIGHT]))
    x1 = x0 + width - 1
    y1 = y0 + height - 1
    max_gap = max(3, int(round(frame_height * 0.12)))
    substrate_present = False
    for structural_label, sx0, sx1, sy0, sy1 in structural_boxes:
        if structural_label == label or sy1 <= y1:
            continue
        overlap = max(0, min(x1, sx1) - max(x0, sx0) + 1)
        if overlap / max(1, width) < 0.35:
            continue
        gap = sy0 - y1 - 1
        if gap > max_gap:
            continue
        substrate_present = True
        if 3 <= gap <= max_gap:
            return True, True
    return substrate_present, False


def _material_layer_ok(
    *,
    area_ratio: float,
    height_ratio: float,
    width_ratio: float,
    min_area: float,
) -> bool:
    return bool(
        area_ratio >= min_area * _LAYER_MIN_AREA_MULTIPLIER
        and height_ratio <= _LAYER_MAX_HEIGHT_RATIO
        and width_ratio >= _LAYER_MIN_WIDTH_RATIO
    )


def _has_one_sided_layer_occupancy(
    component: np.ndarray,
    valid: np.ndarray | None = None,
) -> bool:
    ys, xs = np.where(component)
    if ys.size == 0:
        return False
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    layer = component[y0 : y1 + 1, x0 : x1 + 1]
    row_population = np.count_nonzero(layer, axis=1).astype(np.float32)
    if valid is None:
        row_capacity = np.full(layer.shape[0], max(1, layer.shape[1]), dtype=np.float32)
    else:
        valid_layer = valid[y0 : y1 + 1, x0 : x1 + 1]
        row_capacity = np.maximum(np.count_nonzero(valid_layer, axis=1), 1).astype(np.float32)
    row_occupancy = row_population / row_capacity
    third = max(1, int(math.ceil(layer.shape[0] / 3.0)))
    top_occupancy = float(np.mean(row_occupancy[:third]))
    bottom_occupancy = float(np.mean(row_occupancy[-third:]))
    dominant = max(top_occupancy, bottom_occupancy)
    opposite = min(top_occupancy, bottom_occupancy)
    concentration = dominant / max(1e-6, opposite)
    return bool(
        dominant >= _LAYER_MIN_DOMINANT_THIRD_OCCUPANCY
        and concentration >= _LAYER_MIN_EDGE_CONCENTRATION_RATIO
    )


def _detached_layer_topology(
    component: np.ndarray,
    *,
    area_ratio: float,
    height_ratio: float,
    width_ratio: float,
    bottom_connected: bool,
    min_area: float,
    front_from_lower_edge: bool,
) -> tuple[bool, float]:
    ys = np.where(component)[0]
    default_front = float(ys.min()) if ys.size else float(component.shape[0] - 1)
    if (
        bottom_connected
        or not _material_layer_ok(
            area_ratio=area_ratio,
            height_ratio=height_ratio,
            width_ratio=width_ratio,
            min_area=min_area,
        )
        or not _has_one_sided_layer_occupancy(component)
    ):
        return False, default_front

    y0, y1 = int(ys.min()), int(ys.max())
    front_y = float(y1 if front_from_lower_edge else y0)
    return True, front_y


def _component_evidence(
    label: int,
    component: np.ndarray,
    stats: np.ndarray,
    valid: np.ndarray,
    bottom_band: np.ndarray,
    whiteness: np.ndarray,
    texture: np.ndarray,
    chromatic_support: np.ndarray,
    glare: np.ndarray,
    effective_area: int,
    settings: DetectorSettings,
    *,
    structural_substrate_present: bool,
    front_from_lower_edge: bool,
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
    chromatic_ratio = float(np.count_nonzero(component & chromatic_support)) / pixel_count
    glare_ratio = float(np.count_nonzero(component & glare)) / pixel_count
    ys = np.where(component)[0]
    thin_horizontal = height_ratio < 0.075 and width_ratio >= 0.30

    min_area = max(1e-6, float(settings.foam_min_area_ratio))
    min_whiteness = float(settings.foam_min_whiteness_ratio)
    white_ok = whiteness_ratio >= min_whiteness
    chromatic_ok = chromatic_ratio >= _CHROMATIC_COMPONENT_MIN_RATIO
    structural, _wide_rows, _compactness = _wide_hollow_component_metrics(
        component,
        width_ratio=width_ratio,
        fill_ratio=fill_ratio,
    )
    detached_layer, detached_front_y = _detached_layer_topology(
        component,
        area_ratio=area_ratio,
        height_ratio=height_ratio,
        width_ratio=width_ratio,
        bottom_connected=bottom_connected,
        min_area=min_area,
        front_from_lower_edge=front_from_lower_edge,
    )
    detached_layer = (
        detached_layer
        and texture_ratio >= 0.28
        and (white_ok or chromatic_ok)
        and (not structural_substrate_present or front_from_lower_edge)
    )
    bottom_chromatic_layer = (
        bottom_connected
        and not white_ok
        and chromatic_ok
        and texture_ratio >= 0.28
        and _material_layer_ok(
            area_ratio=area_ratio,
            height_ratio=height_ratio,
            width_ratio=width_ratio,
            min_area=min_area,
        )
        and _has_one_sided_layer_occupancy(component, valid)
    )
    if bottom_connected and ys.size:
        front_y = float(ys.min())
    elif detached_layer:
        front_y = float(detached_front_y)
    else:
        front_y = float(ys.min()) if ys.size else float(h - 1)
    vertical_extent = (h - front_y) / max(1.0, float(h))
    appearance_ratio = max(whiteness_ratio, chromatic_ratio)
    area_score = _unit(area_ratio / max(min_area * 3.0, 1e-6))
    height_score = _unit(height_ratio / 0.28)
    width_score = _unit(width_ratio / 0.55)
    fill_score = _unit((fill_ratio - 0.12) / 0.58)
    bottom_score = 1.0 if bottom_connected else 0.0
    score = (
        0.22 * appearance_ratio
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

    minimum = float(settings.foam_min_evidence_score)
    strong = float(settings.foam_strong_evidence_score)
    shape_ok = (
        ((bottom_connected and white_ok) or bottom_chromatic_layer or detached_layer)
        and area_ratio >= min_area
        and height_ratio >= 0.075
        and not thin_horizontal
        and not structural
    )
    strong_appearance_ok = white_ok or chromatic_ok
    moderate_appearance_ok = whiteness_ratio >= min_whiteness * 0.75 or chromatic_ok
    texture_ok = texture_ratio >= 0.28
    if glare_ratio > float(settings.foam_max_glare_overlap_ratio):
        status = FoamDecisionStatus.GLARE_REJECTED
    elif structural:
        status = FoamDecisionStatus.WEAK_REJECTED
    elif score >= strong and shape_ok and strong_appearance_ok and texture_ok:
        status = FoamDecisionStatus.ACCEPTED_STRONG
    elif score >= minimum and shape_ok and moderate_appearance_ok and texture_ratio >= 0.22:
        status = FoamDecisionStatus.MODERATE_EVIDENCE
    elif score >= minimum * 0.80 and (strong_appearance_ok != texture_ok or shape_ok):
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
        FoamDecisionStatus.INCOHERENT_REJECTED,
        FoamDecisionStatus.STATIC_REJECTED,
    }:
        return FoamEvidenceStrength.WEAK
    return FoamEvidenceStrength.NONE


def _reject_reason(status: FoamDecisionStatus) -> str:
    return {
        FoamDecisionStatus.WEAK_REJECTED: "foam_evidence_below_minimum",
        FoamDecisionStatus.AMBIGUOUS: "foam_evidence_conflicting",
        FoamDecisionStatus.GLARE_REJECTED: "foam_glare_overlap_exceeded",
        FoamDecisionStatus.INCOHERENT_REJECTED: "foam_layer_row_topology_fragmented",
        FoamDecisionStatus.STATIC_REJECTED: "foam_static_artifact_overlap",
    }.get(status, "")


def _unit(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return max(0.0, min(1.0, float(value)))
