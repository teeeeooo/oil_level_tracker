from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


@dataclass
class FoamDetectionResult:
    mask: np.ndarray
    variance_map: np.ndarray
    edge_density_map: np.ndarray
    candidate: BoundaryCandidate | None
    bottom_connected_area_ratio: float


def detect_bottom_connected_foam(gray: np.ndarray, canny: np.ndarray, effective_mask: np.ndarray, settings: DetectorSettings) -> FoamDetectionResult:
    gray_f = gray.astype(np.float32)
    mean = cv2.boxFilter(gray_f, -1, (7, 7), normalize=True)
    mean_sq = cv2.boxFilter(gray_f * gray_f, -1, (7, 7), normalize=True)
    variance = np.maximum(0.0, mean_sq - mean * mean)
    edge_density = cv2.boxFilter((canny > 0).astype(np.float32), -1, (7, 7), normalize=True)
    texture = ((variance >= settings.foam_variance_threshold) | (edge_density >= settings.foam_edge_density_threshold)).astype(np.uint8) * 255
    texture = cv2.bitwise_and(texture, effective_mask)
    texture = cv2.morphologyEx(texture, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    texture = cv2.morphologyEx(texture, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

    count, labels, stats, _ = cv2.connectedComponentsWithStats((texture > 0).astype(np.uint8), connectivity=8)
    h, _ = texture.shape
    bottom_band = np.zeros_like(texture)
    bottom_band[int(h * 0.80):, :] = effective_mask[int(h * 0.80):, :]
    accepted = np.zeros_like(texture)
    effective_area = max(1, int(np.count_nonzero(effective_mask)))
    accepted_area = 0
    top_y: int | None = None
    for label in range(1, count):
        component = labels == label
        if not np.any(component & (bottom_band > 0)):
            continue
        area = int(stats[label, cv2.CC_STAT_AREA])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        bbox_fill_ratio = area / max(1, width * height)
        if area / effective_area < settings.foam_min_area_ratio:
            continue
        # A clear oil boundary or glass rim can form a thin component touching the
        # bottom band. Foam must occupy a genuinely textured two-dimensional area.
        if bbox_fill_ratio < 0.22 or height < max(8, int(h * 0.08)):
            continue
        accepted[component] = 255
        accepted_area += area
        ys = np.where(component)[0]
        if ys.size:
            candidate_top = int(ys.min())
            top_y = candidate_top if top_y is None else min(top_y, candidate_top)
    ratio = accepted_area / effective_area
    candidate = None
    if top_y is not None:
        vertical_extent = (h - top_y) / max(1, h)
        confidence = min(1.0, 0.45 + ratio * 4.0 + vertical_extent * 0.25)
        candidate = BoundaryCandidate(
            source="foam_texture",
            kind=BoundaryKind.FOAM_FRONT,
            y=float(top_y),
            features={"foam_score": confidence, "bottom_connectivity": 1.0, "area_ratio": ratio},
            feature_score=confidence,
            final_score=confidence,
        )
    return FoamDetectionResult(accepted, variance, edge_density, candidate, ratio)
