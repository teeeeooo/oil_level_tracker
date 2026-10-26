from __future__ import annotations

import functools

import numpy as np
import pytest

from oil_tracker.application.services.detection_run import (
    ConsecutiveDetectionFailures,
    DetectionRunCoordinator,
    DetectionRunPolicy,
    DetectionTarget,
    SequenceResolutionMode,
)
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe

# Module-level fakes, so that a spawned worker can import and rebuild them.
DECODE_FAILS_AT = 2.0


class Reader:
    def __init__(self, _path: str) -> None:
        pass

    def read_at(self, timestamp_sec: float):
        if timestamp_sec == DECODE_FAILS_AT:
            raise EOFError(f"no frame near {timestamp_sec}")
        return np.full((4, 4, 3), int(timestamp_sec * 10), np.uint8), int(timestamp_sec * 10), timestamp_sec

    def close(self) -> None:
        pass


class CleanReader(Reader):
    def read_at(self, timestamp_sec: float):
        return np.full((4, 4, 3), int(timestamp_sec * 10), np.uint8), int(timestamp_sec * 10), timestamp_sec


class Detector:
    version = "fake"

    def __init__(self, *, failing_glass: str = "B", failing_frames: tuple[int, ...] = (30,)) -> None:
        self.failing_glass = failing_glass
        self.failing_frames = failing_frames
        self.static: dict[str, int] = {}
        self.history: dict[str, list[int]] = {}

    def worker_factory(self):
        return functools.partial(type(self), failing_glass=self.failing_glass, failing_frames=self.failing_frames)

    def reset(self, glass_id=None) -> None:
        self.static.clear()
        self.history.clear()

    def learn_static_artifact(self, frames, glass) -> None:
        self.static[glass.id] = int(sum(int(frame[0, 0, 0]) for frame in frames))

    def detect(self, frame, glass, frame_index, time_sec, debug=False):
        if glass.name == self.failing_glass and frame_index in self.failing_frames:
            raise ValueError(f"cannot read Glass {glass.name} at frame {frame_index}")
        history = self.history.setdefault(glass.id, [])
        history.append(frame_index)
        detection = PhaseDetection(
            glass.id, frame_index, time_sec, FillState.PARTIAL_VISIBLE,
            raw_oil_air_level_y=float(self.static[glass.id] + len(history) + int(frame[0, 0, 0])),
        )
        return detection, {"debug": debug, "glass": glass.name, "history": tuple(history)}

    def resolve_sequence(self, detections, glass, confirmed_initial_state=None):
        from types import SimpleNamespace

        return SimpleNamespace(detections=tuple(detections), diagnostics={"rows": len(detections)})


def _glasses():
    first = InspectionRecipe.default_glass(320, 240, 1)
    first.id, first.name = "glass-a", "A"
    second = InspectionRecipe.default_glass(320, 240, 2)
    second.id, second.name = "glass-b", "B"
    return first, second


def _run(parallel: bool, *, maximum_failures: int = 10, reader_factory=Reader, glasses=None, detector=None,
         mode=SequenceResolutionMode.CURRENT_FRAME_COMPATIBILITY):
    detector = detector or Detector()
    events = []
    coordinator = DetectionRunCoordinator(reader_factory, detector, detector)
    result = coordinator.run(
        source_video_path="fixture.mp4",
        glasses=glasses or _glasses(),
        targets=tuple(DetectionTarget(value / 2) for value in range(8)),
        static_schedule=(0.0, 1.0),
        policy=DetectionRunPolicy(
            mode,
            debug=True,
            maximum_consecutive_failures=maximum_failures,
            parallel_glasses=parallel,
        ),
        on_observation=lambda row: events.append((
            row.glass.name, row.frame_index, row.actual_timestamp_sec,
            None if row.detection is None else row.detection.raw_oil_air_level_y,
            row.artifacts, None if row.error is None else (type(row.error).__name__, str(row.error)),
        )),
        on_progress=lambda row, completed, total: events.append(("progress", completed, total)),
    )
    rows = {
        glass_id: [(row.frame_index, row.actual_timestamp_sec, None if row.error is None else type(row.error).__name__,
                    None if row.resolved_detection is None else row.resolved_detection.raw_oil_air_level_y)
                   for row in items]
        for glass_id, items in result.observations_by_glass.items()
    }
    return coordinator.last_run_parallel, events, rows, result.sequence_diagnostics


def test_parallel_glasses_reproduce_the_sequential_run_with_its_failures():
    sequential = _run(False)
    parallel = _run(True)
    assert sequential[0] is False and parallel[0] is True
    assert parallel[1:] == sequential[1:]
    events = sequential[1]
    assert ("A", None, None, None, None, ("EOFError", "no frame near 2.0")) in events
    assert ("B", 30, 3.0, None, None, ("ValueError", "cannot read Glass B at frame 30")) in events


def test_parallel_glasses_reproduce_the_completed_window_resolution():
    kwargs = dict(reader_factory=CleanReader, mode=SequenceResolutionMode.COMPLETED_WINDOW)
    sequential = _run(False, detector=Detector(failing_frames=()), **kwargs)
    parallel = _run(True, detector=Detector(failing_frames=()), **kwargs)
    assert parallel[0] is True
    assert parallel[1:] == sequential[1:]
    assert sequential[3] == {"glass-a": {"rows": 8}, "glass-b": {"rows": 8}}


def test_parallel_glasses_stop_on_the_same_consecutive_failure():
    detector = Detector(failing_frames=(15,))  # B fails at 1.5 s, then the 2.0 s decode fails
    with pytest.raises(ConsecutiveDetectionFailures) as sequential:
        _run(False, maximum_failures=2, detector=detector)
    with pytest.raises(ConsecutiveDetectionFailures) as parallel:
        _run(True, maximum_failures=2, detector=Detector(failing_frames=(15,)))
    assert (sequential.value.target.timestamp_sec, sequential.value.count) == (2.0, 2)
    assert (parallel.value.target, parallel.value.count) == (sequential.value.target, sequential.value.count)


def test_parallel_glasses_fall_back_to_sequential_when_a_worker_cannot_be_built():
    assert _run(True, reader_factory=lambda path: Reader(path))[0] is False
    assert _run(True, glasses=_glasses()[:1])[0] is False
