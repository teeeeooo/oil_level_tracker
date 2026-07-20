from __future__ import annotations

import math

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings

from .preprocessing import PreprocessResult
from .row_features import local_maxima, masked_row_mean, row_coverage


def generate_oil_air_candidates(pre: PreprocessResult, effective_mask: np.ndarray, settings: DetectorSettings) -> list[BoundaryCandidate]:
    candidates: list[BoundaryCandidate] = []
    row_energy = masked_row_mean(pre.sobel_y_abs, effective_mask)
    energy_norm = row_energy / max(1.0, float(row_energy.max()))
    for y in local_maxima(energy_norm, settings.candidate_top_k, minimum=0.12):
        candidates.append(BoundaryCandidate("sobel", BoundaryKind.OIL_AIR, float(y), {"generator_strength": float(energy_norm[y])}))

    coverage = row_coverage(pre.horizontal_mask, effective_mask)
    for y in local_maxima(coverage, settings.candidate_top_k, minimum=settings.minimum_horizontal_coverage * 0.55):
        candidates.append(BoundaryCandidate("canny", BoundaryKind.OIL_AIR, float(y), {"generator_strength": float(coverage[y])}))

    lines = cv2.HoughLinesP(
        pre.canny,
        rho=1,
        theta=np.pi / 180,
        threshold=settings.hough_threshold,
        minLineLength=max(5, int(pre.canny.shape[1] * settings.hough_min_line_length_ratio)),
        maxLineGap=settings.hough_max_line_gap,
    )
    if lines is not None:
        for line in lines[: settings.candidate_top_k * 3]:
            x1, y1, x2, y2 = [int(v) for v in line[0]]
            angle = abs(math.degrees(math.atan2(y2 - y1, max(1, x2 - x1))))
            if angle <= settings.hough_max_angle_deg:
                length_ratio = math.hypot(x2 - x1, y2 - y1) / max(1.0, pre.canny.shape[1])
                candidates.append(BoundaryCandidate("hough", BoundaryKind.OIL_AIR, float((y1 + y2) / 2.0), {"generator_strength": min(1.0, length_ratio)}))

    region_profile = _region_contrast_profile(pre.blurred, effective_mask, band=4)
    for y in local_maxima(region_profile, settings.candidate_top_k, minimum=settings.minimum_region_contrast * 0.5):
        candidates.append(BoundaryCandidate("region_boundary", BoundaryKind.OIL_AIR, float(y), {"generator_strength": float(region_profile[y])}))
    return _deduplicate(candidates)


def _region_contrast_profile(gray: np.ndarray, mask: np.ndarray, band: int = 4) -> np.ndarray:
    h = gray.shape[0]
    profile = np.zeros(h, dtype=np.float32)
    for y in range(band, h - band):
        above_mask = mask[y - band:y] > 0
        below_mask = mask[y:y + band] > 0
        if above_mask.sum() < 5 or below_mask.sum() < 5:
            continue
        above = float(gray[y - band:y][above_mask].mean())
        below = float(gray[y:y + band][below_mask].mean())
        profile[y] = abs(above - below) / 255.0
    return profile


def _deduplicate(candidates: list[BoundaryCandidate], tolerance: float = 2.0) -> list[BoundaryCandidate]:
    ordered = sorted(candidates, key=lambda c: c.features.get("generator_strength", 0.0), reverse=True)
    result: list[BoundaryCandidate] = []
    for candidate in ordered:
        same = next((x for x in result if x.source == candidate.source and abs(x.y - candidate.y) <= tolerance), None)
        if same is None:
            result.append(candidate)
    return result
