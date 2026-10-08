from dataclasses import replace
from types import SimpleNamespace

import numpy as np

from oil_tracker.adapters.vision.artifact_reference import capture_reference
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.geometry import ArtifactTemplate, EllipseGeometry
from oil_tracker.domain.recipe import InspectionRecipe


def reference_fixture():
    frame = np.zeros((120, 160, 3), np.uint8)
    frame[60:] = (80, 90, 100)
    glass = InspectionRecipe.default_glass(160, 120)
    glass.geometry.ellipse = EllipseGeometry(80, 60, 70, 50)
    template = ArtifactTemplate("reference-test", "line", .5, .5, .8, .04)
    edge = np.zeros((100, 140), np.uint8)
    edge[50, 10:130] = 255
    edge[40:61, 60] = 255  # Connected crossing extends outside the review scope.
    edge[48, 15:25] = 255  # Disconnected support remains distinct.
    effective = np.full_like(edge, 255)
    effective[50, 20] = 0
    glare = np.zeros_like(edge)
    glare[50, 21] = 255
    images = dict(original_roi=frame[10:110, 10:150], effective_mask=effective,
                  glare_mask=glare, canny=edge, horizontal_mask=np.full_like(edge, 255))
    native = {"status": "measured", "sectors": [{"path_source_y": 65, "source_x_range": [20, 40]}]}
    artifacts = SimpleNamespace(images=images, state={"oil_interface_diagnostics": {
        "candidates": [{"candidate_input_index": 2, "path_aligned": native}]}})
    candidate = BoundaryCandidate("material_path", BoundaryKind.OIL_AIR, 60,
                                  features={"artifact_center_x_norm": .5, "artifact_center_y_norm": .5,
                                            "artifact_width_norm": .8, "artifact_height_norm": .02}, final_score=.8)
    reference = capture_reference(frame, glass, template, artifacts, candidate=candidate, candidate_index=2)
    return frame, glass, replace(template, support_reference=reference), candidate, artifacts
