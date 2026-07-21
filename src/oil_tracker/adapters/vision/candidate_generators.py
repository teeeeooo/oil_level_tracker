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

    glare_excluded = np.where(pre.glare_mask > 0, 0, effective_mask).astype(np.uint8)
    signed_region, region_profile, available = signed_region_contrast_profiles(
        pre.blurred,
        glare_excluded,
        band=4,
    )
    for y in local_maxima(region_profile, settings.candidate_top_k, minimum=settings.minimum_region_contrast * 0.5):
        candidates.append(
            BoundaryCandidate(
                "region_boundary",
                BoundaryKind.OIL_AIR,
                float(y),
                {
                    "generator_strength": float(region_profile[y]),
                    "generator_signed_region_contrast": float(signed_region[y]),
                    "generator_region_available": float(available[y]),
                },
            )
        )
    return _deduplicate(candidates)


def signed_region_contrast_profiles(
    gray: np.ndarray,
    mask: np.ndarray,
    band: int = 4,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return signed above-minus-below, absolute contrast, and availability profiles.

    Signed values are normalized to [-1, 1]. Absolute values are normalized to
    [0, 1]. The median is used so isolated glare remnants cannot dominate a band.
    """

    h = gray.shape[0]
    signed = np.zeros(h, dtype=np.float32)
    absolute = np.zeros(h, dtype=np.float32)
    available = np.zeros(h, dtype=np.float32)
    width = max(1, int(band))
    for y in range(width, h - width):
        above_mask = mask[y - width:y] > 0
        below_mask = mask[y:y + width] > 0
        if int(above_mask.sum()) < 5 or int(below_mask.sum()) < 5:
            continue
        above = float(np.median(gray[y - width:y][above_mask]))
        below = float(np.median(gray[y:y + width][below_mask]))
        difference = above - below
        signed[y] = float(np.clip(difference / 255.0, -1.0, 1.0))
        absolute[y] = float(np.clip(abs(difference) / 255.0, 0.0, 1.0))
        available[y] = 1.0
    return signed, absolute, available


def _region_contrast_profile(gray: np.ndarray, mask: np.ndarray, band: int = 4) -> np.ndarray:
    """Backward-compatible absolute profile helper used by existing tests."""

    _signed, absolute, _available = signed_region_contrast_profiles(gray, mask, band)
    return absolute


def _deduplicate(candidates: list[BoundaryCandidate], tolerance: float = 2.0) -> list[BoundaryCandidate]:
    ordered = sorted(
        candidates,
        key=lambda c: (
            -float(c.features.get("generator_strength", 0.0)),
            c.source,
            float(c.y),
        ),
    )
    result: list[BoundaryCandidate] = []
    for candidate in ordered:
        same = next((x for x in result if x.source == candidate.source and abs(x.y - candidate.y) <= tolerance), None)
        if same is None:
            result.append(candidate)
    return result
