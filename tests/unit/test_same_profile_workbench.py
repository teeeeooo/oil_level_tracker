from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController, WorkbenchReplacementError


class _Reader:
    def __init__(self, path, *, width=320, height=240, fps=10.0, fail_read=False):
        self.path = str(path)
        self.metadata = VideoMetadata(self.path, width, height, fps, 8.0, 80, "fake")
        self.fail_read = fail_read
        self.closed = False

    def read_at(self, timestamp):
        if self.fail_read:
            raise OSError("decode failed")
        return np.zeros((self.metadata.height, self.metadata.width, 3), dtype=np.uint8), 0, 0.01

    def close(self):
        self.closed = True


class _Validator:
    def execute(self, recipe, session):
        return None


def _controller(factory):
    return WorkbenchController(None, None, _Validator(), reader_factory=factory)


def _snapshot():
    recipe = InspectionRecipe.empty(320, 240, "snapshot")
    recipe.glasses.append(InspectionRecipe.default_glass(320, 240, 1))
    return recipe


def test_prepare_deep_copies_snapshot_and_resets_session_fields():
    controller = _controller(lambda path: _Reader(path, fps=1.5))
    controller.session.run_name = "이전 시험"
    snapshot = _snapshot()
    prepared = controller.prepare_same_profile_video(snapshot, 3.0, "new.mp4")
    assert prepared.recipe is not snapshot
    assert prepared.recipe.glasses[0] is not snapshot.glasses[0]
    assert prepared.session.input_video_path == str(Path("new.mp4"))
    assert prepared.session.analysis_start_sec == 0.0
    assert prepared.session.analysis_end_sec == 8.0
    assert prepared.session.compressor_start_sec is None
    assert prepared.session.sampling_fps == 1.5
    assert prepared.session.output_directory == ""
    assert prepared.session.run_name == ""
    assert prepared.session.run_note == ""
    assert prepared.session.resolution_confirmed is True
    prepared.recipe.glasses[0].name = "changed"
    assert snapshot.glasses[0].name != "changed"
    prepared.close()


def test_commit_sets_draft_recipe_path_none_and_closes_previous_reader():
    readers = []

    def factory(path):
        reader = _Reader(path)
        readers.append(reader)
        return reader

    controller = _controller(factory)
    old = _Reader("old.mp4")
    controller.video_reader = old
    controller.recipe_path = Path("old.oilrecipe")
    controller.state = WorkbenchState.ANALYZED
    prepared = controller.prepare_same_profile_video(_snapshot(), 2.0, "new.mp4")
    controller.commit_same_profile_video(prepared)
    assert old.closed is True
    assert controller.video_reader is readers[-1]
    assert controller.recipe_path is None
    assert controller.state == WorkbenchState.DRAFT
    assert controller.selected_glass_id == controller.recipe.glasses[0].id
    prepared.close()
    assert controller.video_reader.closed is False


def test_resolution_mismatch_is_atomic_and_closes_candidate():
    candidate = _Reader("wrong.mp4", width=640, height=480)
    controller = _controller(lambda _path: candidate)
    original_recipe = controller.recipe
    original_session = controller.session
    original_reader = _Reader("old.mp4")
    controller.video_reader = original_reader
    with pytest.raises(WorkbenchReplacementError, match="해상도"):
        controller.prepare_same_profile_video(_snapshot(), 2.0, "wrong.mp4")
    assert controller.recipe is original_recipe
    assert controller.session is original_session
    assert controller.video_reader is original_reader
    assert original_reader.closed is False
    assert candidate.closed is True


def test_candidate_open_or_decode_failure_preserves_entire_workbench():
    original_reader = _Reader("old.mp4")

    def factory(path):
        if str(path) == "open-fail.mp4":
            raise OSError("open failed")
        return _Reader(path, fail_read=True)

    controller = _controller(factory)
    controller.video_reader = original_reader
    controller.recipe = _snapshot()
    controller.session = AnalysisSession(input_video_path="old.mp4")
    controller.state = WorkbenchState.VALIDATED
    controller.recipe_path = Path("saved.oilrecipe")
    before = (controller.recipe, controller.session, controller.video_reader, controller.state, controller.recipe_path)
    with pytest.raises(OSError):
        controller.prepare_same_profile_video(_snapshot(), 2.0, "open-fail.mp4")
    assert (controller.recipe, controller.session, controller.video_reader, controller.state, controller.recipe_path) == before
    with pytest.raises(OSError):
        controller.prepare_same_profile_video(_snapshot(), 2.0, "decode-fail.mp4")
    assert (controller.recipe, controller.session, controller.video_reader, controller.state, controller.recipe_path) == before
    assert original_reader.closed is False


def test_normal_open_video_replacement_resets_current_test_identity_without_mutating_recipe():
    controller = _controller(lambda path: _Reader(path))
    controller.recipe = _snapshot()
    controller.recipe.name = "재사용 프로필"
    recipe_before = controller.recipe.to_dict()
    original_reader = _Reader("old.mp4")
    controller.video_reader = original_reader
    controller.session = AnalysisSession(
        input_video_path="old.mp4",
        analysis_start_sec=1.0,
        analysis_end_sec=7.0,
        compressor_start_sec=2.0,
        output_directory="old-output",
        run_name="이전 시험",
        run_note="old note",
    )
    controller.state = WorkbenchState.ANALYZED

    controller.open_video("new.mp4")

    assert controller.session.input_video_path == "new.mp4"
    assert controller.session.run_name == ""
    assert controller.state == WorkbenchState.DRAFT_DIRTY
    assert original_reader.closed is True
    assert controller.recipe.to_dict() == recipe_before
    assert "run_name" not in controller.recipe.to_dict()


def test_normal_open_video_failure_preserves_existing_current_test_identity_and_workbench():
    original_reader = _Reader("old.mp4")

    def fail_open(_path):
        raise OSError("open failed")

    controller = _controller(fail_open)
    controller.recipe = _snapshot()
    recipe_before = controller.recipe.to_dict()
    controller.video_reader = original_reader
    controller.session = AnalysisSession(input_video_path="old.mp4", run_name="유지할 시험")
    controller.state = WorkbenchState.ANALYZED

    with pytest.raises(OSError, match="open failed"):
        controller.open_video("bad.mp4")

    assert controller.session.input_video_path == "old.mp4"
    assert controller.session.run_name == "유지할 시험"
    assert controller.video_reader is original_reader
    assert original_reader.closed is False
    assert controller.state == WorkbenchState.ANALYZED
    assert controller.recipe.to_dict() == recipe_before


def test_normal_open_video_metadata_failure_preserves_existing_current_test_identity():
    class MetadataFailureReader:
        closed = False

        @property
        def metadata(self):
            raise OSError("metadata failed")

        def close(self):
            self.closed = True

    controller = _controller(lambda _path: MetadataFailureReader())
    controller.session = AnalysisSession(input_video_path="old.mp4", run_name="유지할 시험")
    controller.state = WorkbenchState.ANALYZED

    with pytest.raises(OSError, match="metadata failed"):
        controller.open_video("bad-metadata.mp4")

    assert controller.session.run_name == "유지할 시험"
