from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from oil_tracker.adapters.vision import artifact_proposal
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import InspectionRecipe


def test_proposal_adapter_returns_boundary_and_glare_templates(monkeypatch):
    candidate = BoundaryCandidate(
        source="test-proposal",
        kind=BoundaryKind.OIL_AIR,
        y=200.0,
        features={
            "artifact_center_x_norm": 0.5,
            "artifact_center_y_norm": 0.4,
            "artifact_width_norm": 0.6,
            "artifact_height_norm": 0.02,
            "artifact_angle_deg": 0.0,
        },
        final_score=0.8,
    )
    glare = np.zeros((100, 80), dtype=np.uint8)
    glare[20:30, 10:25] = 255

    class FakeDetector:
        def detect(self, _frame, glass, _frame_index, _time_sec, *, debug):
            assert debug is True
            return (
                PhaseDetection(
                    glass_id=glass.id,
                    frame_index=0,
                    time_sec=0.0,
                    fill_state=FillState.UNKNOWN_REVIEW,
                    candidates=[candidate],
                ),
                SimpleNamespace(images={"glare_mask": glare}),
            )

    monkeypatch.setattr(artifact_proposal, "OpenCvPhaseDetector", FakeDetector)
    glass = InspectionRecipe.default_glass(640, 480)

    proposals = artifact_proposal.propose_artifact_templates(
        np.zeros((480, 640, 3), dtype=np.uint8),
        glass,
    )

    assert [proposal.kind for proposal in proposals] == ["line", "region"]
    assert glass.geometry.artifact_templates == []
