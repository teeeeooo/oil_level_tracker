from __future__ import annotations

from collections import defaultdict

import pytest

from oil_tracker.application.preflight import (
    PreflightCancelled,
    PreflightStatus,
    build_preflight_schedule,
)
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.preflight_check import (
    PreflightCancellationToken,
    PreflightCheckUseCase,
)
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


class FakeReader:
    def __init__(self, metadata: VideoMetadata, fail_calls: set[int] | None = None) -> None:
        self.metadata = metadata
        self.fail_calls = fail_calls or set()
        self.read_calls: list[float] = []
        self.closed = False
        self.frames: dict[int, object] = {}

    def read_at(self, timestamp: float):
        call_index = len(self.read_calls)
        self.read_calls.append(timestamp)
        if call_index in self.fail_calls:
            raise EOFError(f"decode-{call_index}")
        frame_index = int(round(timestamp * self.metadata.fps))
        frame = self.frames.setdefault(frame_index, {"frame_index": frame_index})
        return frame, frame_index + 100, timestamp + 0.003

    def close(self) -> None:
        self.closed = True


class FakeDetectorFactory:
    def __init__(self, result_fn=None, fail_calls: set[int] | None = None) -> None:
        self.result_fn = result_fn or self._normal
        self.fail_calls = fail_calls or set()
        self.instances: list[FakeDetector] = []
        self.detect_log: list[dict] = []

    def __call__(self):
        detector = FakeDetector(self, len(self.instances))
        self.instances.append(detector)
        return detector

    @staticmethod
    def _normal(call_index, frame, glass, frame_index, time_sec):
        zero = glass.geometry.zero_line_y or 0.0
        y = zero - 10.0
        return PhaseDetection(
            glass.id,
            frame_index,
            time_sec,
            FillState.PARTIAL_VISIBLE,
            oil_air_level_y=y,
            oil_air_level_px_from_zero=10.0,
            overall_confidence=0.9,
        )


class FakeDetector:
    def __init__(self, owner: FakeDetectorFactory, instance_index: int) -> None:
        self.owner = owner
        self.instance_index = instance_index
        self.calls = 0

    def detect(self, frame, glass, frame_index, time_sec, debug=False):
        call_index = len(self.owner.detect_log)
        self.calls += 1
        self.owner.detect_log.append(
            {
                "call_index": call_index,
                "instance_index": self.instance_index,
                "frame_identity": id(frame),
                "glass_id": glass.id,
                "initial_state": glass.initial_state,
                "frame_index": frame_index,
                "time_sec": time_sec,
                "debug": debug,
            }
        )
        if call_index in self.owner.fail_calls:
            raise RuntimeError(f"detector-{call_index}")
        return self.owner.result_fn(call_index, frame, glass, frame_index, time_sec), None

    def reset(self, glass_id=None):
        return None


def _metadata(*, fps: float = 10.0, duration: float = 10.0) -> VideoMetadata:
    return VideoMetadata("video.mp4", 640, 480, fps, duration, int(fps * duration))


def _recipe(glass_count: int = 1) -> InspectionRecipe:
    recipe = InspectionRecipe.empty(640, 480)
    recipe.glasses = [InspectionRecipe.default_glass(640, 480, index + 1) for index in range(glass_count)]
    return recipe


def _session(metadata: VideoMetadata | None = None) -> AnalysisSession:
    metadata = metadata or _metadata()
    return AnalysisSession(
        input_video_path=metadata.path,
        video_metadata=metadata,
        analysis_start_sec=0.0,
        analysis_end_sec=metadata.duration_sec,
        compressor_start_sec=2.0,
        sampling_fps=min(2.0, metadata.fps),
    )


def _use_case(reader: FakeReader, detector_factory: FakeDetectorFactory) -> PreflightCheckUseCase:
    return PreflightCheckUseCase(lambda _path: reader, detector_factory, RecipeValidationService())


def test_enabled_glasses_share_one_decoded_frame_per_sample_and_record_actual_position():
    metadata = _metadata()
    recipe = _recipe(3)
    recipe.glasses[0].initial_state = InitialObservationState.FULL_NO_INTERFACE
    recipe.glasses[2].enabled = False
    session = _session(metadata)
    reader = FakeReader(metadata)
    detectors = FakeDetectorFactory()
    progress = []

    result = _use_case(reader, detectors).execute(recipe, session, progress=progress.append)
    schedule = build_preflight_schedule(0.0, 10.0, metadata, 2.0)

    assert len(reader.read_calls) == len(schedule)
    assert len(result.samples) == len(schedule) * 2
    assert {sample.glass_id for sample in result.samples} == {recipe.glasses[0].id, recipe.glasses[1].id}
    assert len(detectors.instances) == len(result.samples)
    assert all(detector.calls == 1 for detector in detectors.instances)
    assert all(not item["debug"] for item in detectors.detect_log)

    identities_by_frame = defaultdict(set)
    for item in detectors.detect_log:
        identities_by_frame[item["frame_index"]].add(item["frame_identity"])
    assert all(len(identities) == 1 for identities in identities_by_frame.values())

    first = result.samples[0]
    assert first.sample_point.actual_timestamp == pytest.approx(reader.read_calls[0] + 0.003)
    assert first.sample_point.frame_index == int(round(reader.read_calls[0] * metadata.fps)) + 100
    assert progress[-1].completed == progress[-1].total == len(result.samples)

    first_glass_states = [
        item["initial_state"] for item in detectors.detect_log if item["glass_id"] == recipe.glasses[0].id
    ]
    assert first_glass_states[0] == InitialObservationState.FULL_NO_INTERFACE
    assert all(state == InitialObservationState.AUTO for state in first_glass_states[1:])
    assert reader.closed


def test_normal_review_failure_classification_and_glass_summary_minimum_confidence():
    def result_fn(call_index, _frame, glass, frame_index, time_sec):
        if call_index == 1:
            return PhaseDetection(
                glass.id,
                frame_index,
                time_sec,
                FillState.PARTIAL_VISIBLE,
                oil_air_level_y=200.0,
                overall_confidence=0.1,
                flags=["LOW_CONFIDENCE"],
            )
        if call_index == 2:
            return PhaseDetection(
                glass.id,
                frame_index,
                time_sec,
                FillState.PARTIAL_VISIBLE,
                overall_confidence=0.8,
                flags=["DETECTION_LOST"],
            )
        if call_index == 3:
            return PhaseDetection(
                glass.id,
                frame_index,
                time_sec,
                FillState.FOAMING_VISIBLE,
                oil_air_level_y=210.0,
                foam_front_y=180.0,
                overall_confidence=0.75,
                flags=["FOAM_REACH_TOP"],
            )
        return FakeDetectorFactory._normal(call_index, _frame, glass, frame_index, time_sec)

    recipe = _recipe()
    session = _session()
    reader = FakeReader(session.video_metadata)
    result = _use_case(reader, FakeDetectorFactory(result_fn)).execute(recipe, session)

    statuses = [sample.status for sample in result.samples]
    assert PreflightStatus.NORMAL in statuses
    assert PreflightStatus.REVIEW in statuses
    assert PreflightStatus.FAILURE in statuses
    assert result.overall_status == PreflightStatus.FAILURE
    summary = result.glass_summaries[0]
    assert summary.minimum_confidence == pytest.approx(0.1)
    assert summary.normal_count + summary.review_count + summary.failure_count == len(result.samples)
    assert summary.failure_count == 1
    assert any(sample.foam_detected for sample in result.samples)


def test_position_jump_is_an_advisory_warning_using_effective_glass_height():
    def result_fn(_call_index, _frame, glass, frame_index, time_sec):
        y = 120.0 if time_sec < 5.0 else 320.0
        return PhaseDetection(
            glass.id,
            frame_index,
            time_sec,
            FillState.PARTIAL_VISIBLE,
            oil_air_level_y=y,
            overall_confidence=0.9,
        )

    recipe = _recipe()
    session = _session()
    result = _use_case(
        FakeReader(session.video_metadata),
        FakeDetectorFactory(result_fn),
    ).execute(recipe, session)

    jump_samples = [sample for sample in result.samples if "PREFLIGHT_POSITION_JUMP" in sample.flags]
    assert jump_samples
    assert all(sample.status == PreflightStatus.REVIEW for sample in jump_samples)
    assert result.glass_summaries[0].position_jump_detected


def test_decode_and_detector_failures_are_recorded_and_later_samples_continue():
    recipe = _recipe()
    session = _session()
    reader = FakeReader(session.video_metadata, fail_calls={1})
    detectors = FakeDetectorFactory(fail_calls={1})

    result = _use_case(reader, detectors).execute(recipe, session)

    reasons = [sample.reason for sample in result.samples]
    assert any("영상 장면을 읽지 못했습니다" in reason for reason in reasons)
    assert any("관찰창 검출 중 오류" in reason for reason in reasons)
    assert len(result.samples) > 2
    assert result.samples[-1].sample_point.actual_timestamp > result.samples[0].sample_point.actual_timestamp
    assert reader.closed


def test_video_open_failure_is_a_whole_task_failure():
    use_case = PreflightCheckUseCase(
        lambda _path: (_ for _ in ()).throw(RuntimeError("open failed")),
        FakeDetectorFactory(),
        RecipeValidationService(),
    )

    with pytest.raises(ValueError, match="시험 영상을 열 수 없습니다"):
        use_case.execute(_recipe(), _session())


def test_reader_closes_on_cancellation_before_first_decode():
    session = _session()
    reader = FakeReader(session.video_metadata)
    token = PreflightCancellationToken()
    token.cancel()

    with pytest.raises(PreflightCancelled):
        _use_case(reader, FakeDetectorFactory()).execute(_recipe(), session, cancellation=token)

    assert reader.closed
    assert reader.read_calls == []


def test_each_sparse_sample_uses_a_new_detector_and_does_not_touch_live_preview_state():
    recipe = _recipe()
    session = _session()
    factory = FakeDetectorFactory()
    live_preview_detector = FakeDetectorFactory()()

    result = _use_case(FakeReader(session.video_metadata), factory).execute(recipe, session)

    assert len(factory.instances) == len(result.samples)
    assert all(detector.calls == 1 for detector in factory.instances)
    assert live_preview_detector.calls == 0
