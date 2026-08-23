from __future__ import annotations

import inspect

import numpy as np

from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.phase_frame_detection import (
    CurrentFrameEvidenceOwner,
    CurrentFrameResultProjector,
    PhaseDebugProjector,
)
from oil_tracker.domain.recipe import InspectionRecipe


def test_detector_facade_delegates_bounded_current_frame_responsibilities() -> None:
    detector = OpenCvPhaseDetector()

    assert isinstance(detector._frame_evidence_owner, CurrentFrameEvidenceOwner)
    assert isinstance(detector._frame_result_projector, CurrentFrameResultProjector)
    assert isinstance(detector._debug_projector, PhaseDebugProjector)
    assert detector._frame_evidence_owner.static_maps is detector._static_maps
    assert (
        detector._frame_evidence_owner.static_foam_maps
        is detector._static_foam_maps
    )
    source = inspect.getsource(OpenCvPhaseDetector.detect)
    assert "_frame_evidence_owner.observe" in source
    assert "_frame_result_projector.project" in source
    assert "_debug_projector.project" in source
    assert len(source.splitlines()) <= 30


def test_debug_projection_is_not_materialized_for_normal_detection() -> None:
    detector = OpenCvPhaseDetector()
    glass = InspectionRecipe.default_glass(320, 240)
    frame = np.full((240, 320, 3), 96, np.uint8)
    sentinel = object()

    class DebugSpy:
        calls = 0

        def project(self, *_args):
            self.calls += 1
            return sentinel

    spy = DebugSpy()
    detector._debug_projector = spy

    _detection, artifacts = detector.detect(frame, glass, 0, 0.0, debug=False)
    assert artifacts is None
    assert spy.calls == 0

    detector.reset()
    _detection, artifacts = detector.detect(frame, glass, 0, 0.0, debug=True)
    assert artifacts is sentinel
    assert spy.calls == 1
