from __future__ import annotations

from dataclasses import replace
import math
from uuid import uuid4

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.geometry import ArtifactTemplate, Rect
from oil_tracker.domain.recipe import GlassInspectionConfig


ARTIFACT_REJECT_REASON = "calibrated_artifact"


def attach_spatial_signature(
    candidate: BoundaryCandidate,
    support_mask: np.ndarray,
    glass: GlassInspectionConfig,
    *,
    crop_origin: tuple[int, int],
) -> BoundaryCandidate:
    """Attach normalized support geometry without changing candidate authority."""

    if support_mask.ndim != 2:
        raise ValueError("Artifact support mask must be two-dimensional.")
    ellipse = glass.geometry.ellipse
    local_y = int(round(float(candidate.y) - float(crop_origin[1])))
    band = slice(max(0, local_y - 2), min(support_mask.shape[0], local_y + 3))
    columns = np.flatnonzero(np.any(support_mask[band] > 0, axis=0))
    if columns.size:
        left = float(crop_origin[0] + columns[0])
        right = float(crop_origin[0] + columns[-1] + 1)
    else:
        extent = ellipse.horizontal_extent_at(float(candidate.y))
        if extent is None:
            left = right = float(ellipse.center_x)
        else:
            left, right = map(float, extent)
    center_x = 0.5 * (left + right)
    width = max(1.0, right - left)
    features = dict(candidate.features)
    features.update(
        {
            "artifact_center_x_norm": _unit(
                (center_x - ellipse.bounds.x) / max(1.0, ellipse.radius_x * 2.0)
            ),
            "artifact_center_y_norm": _unit(
                (float(candidate.y) - ellipse.bounds.y)
                / max(1.0, ellipse.radius_y * 2.0)
            ),
            "artifact_width_norm": _unit(
                width / max(1.0, ellipse.radius_x * 2.0)
            ),
            "artifact_height_norm": _unit(
                5.0 / max(1.0, ellipse.radius_y * 2.0)
            ),
            "artifact_angle_deg": 0.0,
        }
    )
    return replace(candidate, features=features)


def apply_artifact_templates(
    candidates: list[BoundaryCandidate] | tuple[BoundaryCandidate, ...],
    glass: GlassInspectionConfig,
) -> tuple[list[BoundaryCandidate], int]:
    """Reject only candidates matching a user-confirmed spatial template.

    Rejected candidates stay in the trace with their original scores and a
    calibrated match penalty. Geometry alone is not enough: line/point matches
    require both vertical proximity and horizontal support agreement.
    """

    output: list[BoundaryCandidate] = []
    rejected_count = 0
    for candidate in candidates:
        best: tuple[float, ArtifactTemplate] | None = None
        for template in glass.geometry.artifact_templates:
            score = artifact_match_score(candidate, template)
            if score < 0.72:
                continue
            if best is None or score > best[0]:
                best = score, template
        if best is None:
            output.append(candidate)
            continue
        score, template = best
        features = dict(candidate.features)
        penalties = dict(candidate.penalties)
        features["calibrated_artifact_match"] = float(score)
        penalties["calibrated_artifact_match"] = float(score)
        already_rejected = candidate.rejected
        output.append(
            replace(
                candidate,
                features=features,
                penalties=penalties,
                selected=False if not already_rejected else candidate.selected,
                rejected=True,
                reject_reason=(
                    candidate.reject_reason
                    if already_rejected and candidate.reject_reason
                    else f"{ARTIFACT_REJECT_REASON}:{template.id}"
                ),
            )
        )
        rejected_count += int(not already_rejected)
    return output, rejected_count


def artifact_match_score(
    candidate: BoundaryCandidate,
    template: ArtifactTemplate,
) -> float:
    features = candidate.features
    required = (
        "artifact_center_x_norm",
        "artifact_center_y_norm",
        "artifact_width_norm",
        "artifact_height_norm",
    )
    if any(key not in features for key in required):
        return 0.0
    cx = _unit(features[required[0]])
    cy = _unit(features[required[1]])
    width = max(0.005, _unit(features[required[2]]))
    height = max(0.005, _unit(features[required[3]]))
    vertical_tolerance = max(0.015, template.height * 0.5, height * 0.5)
    vertical = _unit(1.0 - abs(cy - template.center_y) / vertical_tolerance)
    if vertical <= 0.0:
        return 0.0

    if template.kind == "region":
        inside_x = abs(cx - template.center_x) <= template.width * 0.5
        return vertical if inside_x else 0.0
    if template.kind == "point":
        horizontal_tolerance = max(0.015, template.width * 0.5)
        horizontal = _unit(
            1.0 - abs(cx - template.center_x) / horizontal_tolerance
        )
        return min(vertical, horizontal)
    if template.kind != "line":
        return 0.0

    candidate_left = cx - width * 0.5
    candidate_right = cx + width * 0.5
    template_left = template.center_x - template.width * 0.5
    template_right = template.center_x + template.width * 0.5
    overlap = max(
        0.0,
        min(candidate_right, template_right) - max(candidate_left, template_left),
    )
    overlap_ratio = overlap / max(0.005, min(width, template.width))
    angle = abs(float(features.get("artifact_angle_deg", 0.0)) - template.angle_deg)
    angle = min(angle, 360.0 - angle)
    angle_support = _unit(1.0 - angle / 12.0)
    return _unit(0.55 * vertical + 0.35 * overlap_ratio + 0.10 * angle_support)


def template_from_candidate(
    candidate: BoundaryCandidate,
    *,
    name: str,
) -> ArtifactTemplate | None:
    features = candidate.features
    if "artifact_center_x_norm" not in features or "artifact_center_y_norm" not in features:
        return None
    width = max(0.02, _unit(features.get("artifact_width_norm", 0.0)))
    point_like = width < 0.12
    return ArtifactTemplate(
        id=str(uuid4()),
        kind="point" if point_like else "line",
        center_x=_unit(features["artifact_center_x_norm"]),
        center_y=_unit(features["artifact_center_y_norm"]),
        width=max(0.03, width if not point_like else 0.06),
        height=max(0.02, _unit(features.get("artifact_height_norm", 0.0)) * 2.0),
        angle_deg=float(features.get("artifact_angle_deg", 0.0)),
        name=name,
        note=f"detector proposal: {candidate.kind.value}/{candidate.source}",
    )


def region_template_from_source_rect(
    rect: Rect,
    glass: GlassInspectionConfig,
    *,
    name: str,
) -> ArtifactTemplate:
    bounds = glass.geometry.ellipse.bounds
    return ArtifactTemplate(
        id=str(uuid4()),
        kind="region",
        center_x=_unit((rect.x + rect.width * 0.5 - bounds.x) / bounds.width),
        center_y=_unit((rect.y + rect.height * 0.5 - bounds.y) / bounds.height),
        width=max(0.01, min(1.0, rect.width / bounds.width)),
        height=max(0.01, min(1.0, rect.height / bounds.height)),
        name=name,
        note="detector proposal: optical artifact region",
    )


def template_source_rect(
    template: ArtifactTemplate,
    glass: GlassInspectionConfig,
) -> Rect:
    bounds = glass.geometry.ellipse.bounds
    width = template.width * bounds.width
    height = template.height * bounds.height
    center_x = bounds.x + template.center_x * bounds.width
    center_y = bounds.y + template.center_y * bounds.height
    return Rect(center_x - width * 0.5, center_y - height * 0.5, width, height)


def _unit(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
