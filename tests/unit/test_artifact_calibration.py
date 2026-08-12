from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.artifact_calibration import (
    apply_artifact_templates,
    attach_spatial_signature,
    template_from_candidate,
)
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.geometry import ArtifactTemplate
from oil_tracker.domain.recipe import InspectionRecipe


def _candidate(y: float = 120.0) -> BoundaryCandidate:
    return BoundaryCandidate(
        source="proposal",
        kind=BoundaryKind.OIL_AIR,
        y=y,
        features={"sequence_eligible": 1.0},
        final_score=0.7,
    )


def test_artifact_template_roundtrip_uses_normalized_ellipse_coordinates() -> None:
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240)
    template = ArtifactTemplate(
        id="artifact-1",
        kind="line",
        center_x=0.5,
        center_y=0.35,
        width=0.70,
        height=0.04,
        name="고정 반사선",
    )
    glass.geometry.artifact_templates.append(template)
    recipe.glasses.append(glass)

    restored = InspectionRecipe.from_dict(recipe.to_dict())

    assert restored.glasses[0].geometry.artifact_templates == [template]


def test_calibrated_line_rejects_matching_support_but_not_same_y_elsewhere() -> None:
    glass = InspectionRecipe.default_glass(320, 240)
    support = np.zeros((130, 80), dtype=np.uint8)
    support[62, 20:61] = 255
    signed = attach_spatial_signature(
        _candidate(120.0),
        support,
        glass,
        crop_origin=(120, 58),
    )
    template = template_from_candidate(signed, name="선택한 반사선")
    assert template is not None
    glass.geometry.artifact_templates.append(template)

    rejected, count = apply_artifact_templates([signed], glass)

    assert count == 1
    assert rejected[0].rejected is True
    assert rejected[0].selected is False
    assert rejected[0].reject_reason == f"calibrated_artifact:{template.id}"
    assert rejected[0].features["calibrated_artifact_match"] >= 0.72

    elsewhere = BoundaryCandidate(
        source="proposal",
        kind=BoundaryKind.OIL_AIR,
        y=120.0,
        features={
            **signed.features,
            "artifact_center_x_norm": 0.02,
            "artifact_width_norm": 0.03,
        },
    )
    retained, count = apply_artifact_templates([elsewhere], glass)
    assert count == 0
    assert retained[0].rejected is False


def test_legacy_recipe_without_artifact_templates_remains_supported() -> None:
    recipe = InspectionRecipe.empty(320, 240)
    recipe.glasses.append(InspectionRecipe.default_glass(320, 240))
    payload = recipe.to_dict()
    payload["glasses"][0]["geometry"].pop("artifact_templates")

    restored = InspectionRecipe.from_dict(payload)

    assert restored.glasses[0].geometry.artifact_templates == []
