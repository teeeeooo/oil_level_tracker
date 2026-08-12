from __future__ import annotations

from copy import deepcopy
import math

import cv2

from oil_tracker.domain.geometry import Rect

from .artifact_calibration import (
    region_template_from_source_rect,
    template_from_candidate,
)
from .opencv_phase_detector import OpenCvPhaseDetector


def propose_artifact_templates(
    frame,
    glass,
    *,
    maximum_boundary_proposals: int = 10,
    maximum_glare_regions: int = 4,
):
    """Return detector-backed templates without mutating the edited Glass.

    Raster segmentation belongs to the vision adapter.  The UI only presents
    these proposals and records an explicit user selection.
    """

    detector_glass = deepcopy(glass)
    detector_glass.geometry.artifact_templates.clear()
    detection, artifacts = OpenCvPhaseDetector().detect(
        frame,
        detector_glass,
        0,
        0.0,
        debug=True,
    )

    proposals = []
    candidates = sorted(
        detection.candidates,
        key=lambda candidate: (-float(candidate.final_score), float(candidate.y)),
    )
    for candidate in candidates:
        if not math.isfinite(float(candidate.y)):
            continue
        template = template_from_candidate(
            candidate,
            name=f"경계 후보 {len(proposals) + 1}",
        )
        if template is None or any(
            abs(template.center_y - existing.center_y) <= 0.025
            and abs(template.center_x - existing.center_x) <= 0.08
            for existing in proposals
        ):
            continue
        proposals.append(template)
        if len(proposals) >= maximum_boundary_proposals:
            break

    if artifacts is None:
        return proposals
    glare = artifacts.images.get("glare_mask")
    if glare is None or glare.ndim != 2:
        return proposals

    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
        (glare > 0).astype("uint8"),
        connectivity=8,
    )
    origin_x = max(
        0,
        int(math.floor(detector_glass.geometry.ellipse.bounds.x)),
    )
    origin_y = max(
        0,
        int(math.floor(detector_glass.geometry.ellipse.bounds.y)),
    )
    regions = sorted(
        range(1, count),
        key=lambda label: -int(stats[label, cv2.CC_STAT_AREA]),
    )
    for label in regions[:maximum_glare_regions]:
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        if width * height < 8:
            continue
        proposals.append(
            region_template_from_source_rect(
                Rect(origin_x + x, origin_y + y, width, height),
                detector_glass,
                name=f"광학 구역 후보 {len(proposals) + 1}",
            )
        )
    return proposals
