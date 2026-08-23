from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from oil_tracker.application.services.detection_run import (
    DetectionRunCoordinator,
    DetectionRunPolicy,
    DetectionTarget,
    SequenceResolutionMode,
)
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe


class _Reader:
    def __init__(self, _path: str) -> None:
        self.reads: list[float] = []
        self.closed = False

    def read_at(self, timestamp_sec: float):
        self.reads.append(timestamp_sec)
        return np.zeros((8, 8, 3), np.uint8), int(timestamp_sec * 10), timestamp_sec

    def close(self) -> None:
        self.closed = True


class _Detector:
    version = "characterization"

    def __init__(self) -> None:
        self.reset_count = 0
        self.detect_count = 0
        self.resolve_count = 0

    def reset(self, glass_id=None) -> None:
        self.reset_count += 1

    def learn_static_artifact(self, frames, glass) -> None:
        assert frames

    def detect(self, _frame, glass, frame_index, time_sec, debug=False):
        self.detect_count += 1
        return (
            PhaseDetection(
                glass.id,
                frame_index,
                time_sec,
                FillState.UNKNOWN_REVIEW,
            ),
            SimpleNamespace(debug=debug),
        )

    def resolve_sequence(self, detections, glass, confirmed_initial_state=None):
        self.resolve_count += 1
        assert all(item.glass_id == glass.id for item in detections)
        return SimpleNamespace(
            detections=tuple(detections),
            diagnostics={"mode": "completed"},
        )


def test_current_compatibility_reuses_static_decodes_without_resolution() -> None:
    readers: list[_Reader] = []

    def reader_factory(path):
        reader = _Reader(path)
        readers.append(reader)
        return reader

    detector = _Detector()
    glass = InspectionRecipe.default_glass(320, 240)
    result = DetectionRunCoordinator(reader_factory, detector).run(
        source_video_path="fixture.mp4",
        glasses=(glass,),
        targets=tuple(DetectionTarget(value) for value in (0.0, 1.0, 2.0)),
        static_schedule=(0.0, 1.0, 2.0),
        policy=DetectionRunPolicy(
            SequenceResolutionMode.CURRENT_FRAME_COMPATIBILITY,
            debug=True,
            reuse_static_decodes=True,
        ),
    )

    assert detector.reset_count == 1
    assert detector.detect_count == 3
    assert detector.resolve_count == 0
    assert readers[0].reads == [0.0, 1.0, 2.0]
    assert readers[0].closed
    assert not result.sequence_resolver_enabled


def test_completed_window_resolution_preserves_identity_and_diagnostics() -> None:
    detector = _Detector()
    glass = InspectionRecipe.default_glass(320, 240)
    result = DetectionRunCoordinator(_Reader, detector, detector).run(
        source_video_path="fixture.mp4",
        glasses=(glass,),
        targets=(DetectionTarget(1.0), DetectionTarget(2.0)),
        static_schedule=(1.0, 2.0),
        policy=DetectionRunPolicy(SequenceResolutionMode.COMPLETED_WINDOW),
    )

    rows = result.observations_by_glass[glass.id]
    assert detector.resolve_count == 1
    assert [(row.frame_index, row.actual_timestamp_sec) for row in rows] == [
        (10, 1.0),
        (20, 2.0),
    ]
    assert all(row.detection is row.resolved_detection for row in rows)
    assert result.sequence_diagnostics == {glass.id: {"mode": "completed"}}
