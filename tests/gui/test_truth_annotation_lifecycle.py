from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QMessageBox, QWidget

from oil_tracker.adapters.presentation.qt_frame_image_converter import FrameImageConversionError
from oil_tracker.adapters.storage.json_truth_repository import build_truth_bundle_identity
from oil_tracker.application.services.user_truth import TruthSession, TruthSessionStatus, UserTruthService
from oil_tracker.ui.truth_annotation_coordinator import TruthAnnotationCoordinator
from user_truth_fixtures import make_truth_bundle, make_truth_set_and_annotation


class _Viewer(QWidget):
    truthRequested = Signal()
    bundleChanged = Signal(object)
    sourceVideoChanged = Signal(object)
    selectedGlassChanged = Signal(str)
    viewerClosing = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.bundle = None
        self.active_video_path = None
        self.current_frame = None
        self.current_frame_index = 60
        self.current_time = 2.0
        self.selected_glass_id = "glass-1"
        self.debug_repository = None
        self.bundle_guards = []
        self.glass_guards = []
        self.close_guards = []
        self.truth_markers = ()
        self.selected_truth_id = ""

    def add_bundle_change_guard(self, callback) -> None:
        self.bundle_guards.append(callback)

    def add_glass_change_guard(self, callback) -> None:
        self.glass_guards.append(callback)

    def add_close_guard(self, callback) -> None:
        self.close_guards.append(callback)

    def set_truth_annotations(self, annotations, *, selected_id: str = "") -> None:
        self.truth_markers = tuple(annotations)
        self.selected_truth_id = selected_id


class _RecordingConverter:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.calls = []
        self.error = error

    def to_qimage(self, frame) -> QImage:
        self.calls.append(frame)
        if self.error is not None:
            raise self.error
        image = QImage(320, 240, QImage.Format.Format_RGB32)
        image.fill(QColor(12, 34, 56))
        return image


def _coordinator(qtbot, *, converter=None):
    viewer = _Viewer()
    qtbot.addWidget(viewer)
    coordinator = TruthAnnotationCoordinator(viewer, frame_image_converter=converter)
    coordinator._ensure_window()
    qtbot.addWidget(coordinator.window)
    return coordinator, viewer


def test_truth_session_state_machine_is_external_viewer_state(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    identity = build_truth_bundle_identity(bundle)
    truth_set = UserTruthService().create_set(identity)
    session = TruthSession()
    assert session.status is TruthSessionStatus.NONE
    session.attach_new(truth_set)
    assert session.status is TruthSessionStatus.NEW
    assert not session.dirty
    session.mark_dirty()
    assert session.status is TruthSessionStatus.MODIFIED
    assert session.dirty
    session.mark_saving()
    assert session.status is TruthSessionStatus.SAVING
    path = tmp_path / "truth.oiltruth"
    session.mark_saved(path)
    assert session.status is TruthSessionStatus.SAVED
    assert session.path == path
    assert not session.dirty
    session.mark_dirty()
    session.mark_failed()
    assert session.status is TruthSessionStatus.SAVE_FAILED
    assert session.dirty
    session.clear()
    assert session.status is TruthSessionStatus.NONE
    assert session.truth_set is None
    assert session.path is None


def test_capture_converts_viewer_frame_once_and_canvas_receives_qimage(qtbot, tmp_path):
    converter = _RecordingConverter()
    coordinator, viewer = _coordinator(qtbot, converter=converter)
    viewer.bundle = make_truth_bundle(tmp_path)
    viewer.active_video_path = tmp_path / "source.mp4"
    viewer.current_frame = object()
    viewer.selected_glass_id = viewer.bundle.recipe.glasses[0].id

    coordinator.capture_current_frame()

    assert converter.calls == [viewer.current_frame]
    assert coordinator.window.context() is not None
    assert coordinator.window.canvas.source_image_size.width() == 320
    assert coordinator.window.canvas.source_image_size.height() == 240
    assert not coordinator._draft_image.isNull()
    assert not hasattr(coordinator.window.canvas, "_frame")
    coordinator.close()


def test_annotation_save_reuses_coordinator_draft_image_without_canvas_private_state(qtbot, tmp_path):
    converter = _RecordingConverter()
    coordinator, viewer = _coordinator(qtbot, converter=converter)
    viewer.bundle = make_truth_bundle(tmp_path)
    viewer.active_video_path = tmp_path / "source.mp4"
    original_frame = object()
    viewer.current_frame = original_frame
    viewer.selected_glass_id = viewer.bundle.recipe.glasses[0].id

    coordinator.capture_current_frame()
    original_color = coordinator._draft_image.pixelColor(0, 0)
    coordinator.confirm_official()
    viewer.current_frame = object()

    assert coordinator.save_annotation()
    assert converter.calls == [original_frame]
    assert coordinator._draft_image.pixelColor(0, 0) == original_color
    assert coordinator.window.canvas.source_image_size == coordinator._draft_image.size()
    assert not hasattr(coordinator.window.canvas, "_frame")
    coordinator.close()


def test_converter_failure_is_presented_as_bounded_korean_error(qtbot, tmp_path):
    converter = _RecordingConverter(error=FrameImageConversionError("raw numpy failure"))
    coordinator, viewer = _coordinator(qtbot, converter=converter)
    viewer.bundle = make_truth_bundle(tmp_path)
    viewer.active_video_path = tmp_path / "source.mp4"
    viewer.current_frame = object()
    viewer.selected_glass_id = viewer.bundle.recipe.glasses[0].id

    coordinator.capture_current_frame()

    message = coordinator.window.validation_label.text()
    assert "이미지로 변환할 수 없습니다" in message
    assert "raw numpy failure" not in message
    assert coordinator.window.context() is None
    assert coordinator._draft_image.isNull()
    coordinator.close()


def test_draft_change_cancel_preserves_context_and_blocks_transition(qtbot, monkeypatch):
    coordinator, _viewer = _coordinator(qtbot)
    coordinator.draft_dirty = True
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )
    assert not coordinator._guard_draft_change("bundle 변경")
    assert coordinator.draft_dirty
    coordinator.close()


def test_draft_change_discard_allows_transition_without_saving(qtbot, monkeypatch):
    coordinator, _viewer = _coordinator(qtbot)
    coordinator.draft_dirty = True
    saved = []
    monkeypatch.setattr(coordinator, "save_annotation", lambda **kwargs: saved.append(True) or True)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard,
    )
    assert coordinator._guard_draft_change("glass 변경")
    assert not coordinator.draft_dirty
    assert saved == []
    coordinator.close()


def test_draft_change_save_delegates_to_annotation_validation(qtbot, monkeypatch):
    coordinator, _viewer = _coordinator(qtbot)
    coordinator.draft_dirty = True
    calls = []
    monkeypatch.setattr(
        coordinator,
        "save_annotation",
        lambda **kwargs: calls.append(kwargs) or True,
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    assert coordinator._guard_draft_change("glass 변경")
    assert calls == [{"quiet": True}]
    coordinator.close()


def test_dirty_truth_set_cancel_discard_and_save_contract(qtbot, tmp_path, monkeypatch):
    coordinator, viewer = _coordinator(qtbot)
    bundle = make_truth_bundle(tmp_path)
    viewer.bundle = bundle
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    coordinator.session.attach_new(truth_set)
    coordinator.session.mark_dirty()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )
    assert not coordinator._guard_truth_set_change("bundle 변경")
    assert coordinator.session.dirty

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard,
    )
    assert coordinator._guard_truth_set_change("bundle 변경")
    assert not coordinator.session.dirty

    coordinator.session.mark_dirty()
    calls = []
    monkeypatch.setattr(coordinator, "save_truth_set", lambda **kwargs: calls.append(kwargs) or True)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    assert coordinator._guard_truth_set_change("Viewer 닫기")
    assert calls == [{}]
    coordinator.close()


def test_bundle_change_guard_invalidates_export_before_prompt(qtbot, monkeypatch):
    coordinator, _viewer = _coordinator(qtbot)
    calls = []
    monkeypatch.setattr(coordinator.export_controller, "invalidate", lambda: calls.append("invalidate"))
    monkeypatch.setattr(coordinator, "_guard_draft_change", lambda _title: calls.append("draft") or True)
    monkeypatch.setattr(coordinator, "_guard_truth_set_change", lambda _title: calls.append("set") or True)
    assert coordinator._guard_bundle_change()
    assert calls == ["invalidate", "draft", "set"]
    coordinator.close()


def test_bundle_change_clears_active_truth_context_markers_and_draft_image(qtbot, tmp_path):
    coordinator, viewer = _coordinator(qtbot)
    old_bundle = make_truth_bundle(tmp_path / "old")
    truth_set, annotation, _service = make_truth_set_and_annotation(old_bundle)
    coordinator.session.attach_new(truth_set)
    viewer.set_truth_annotations((annotation,), selected_id=annotation.annotation_id)
    image = QImage(10, 10, QImage.Format.Format_RGB32)
    coordinator._draft_image = image

    new_bundle = make_truth_bundle(tmp_path / "new")
    coordinator._bundle_changed(new_bundle)
    assert coordinator.session.truth_set is None
    assert coordinator.identity == build_truth_bundle_identity(new_bundle)
    assert viewer.truth_markers == ()
    assert viewer.selected_truth_id == ""
    assert coordinator._draft_image.isNull()
    coordinator.close()


def test_source_loss_preserves_saved_annotation_metadata_but_disables_creation(qtbot, tmp_path):
    coordinator, viewer = _coordinator(qtbot)
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    viewer.bundle = bundle
    viewer.active_video_path = None
    viewer.current_frame = None
    coordinator.session.attach_new(truth_set)
    coordinator._refresh_annotations()
    coordinator._source_changed(None)
    assert coordinator.session.truth_set.annotations == [annotation]
    assert coordinator.window.annotation_list.count() == 1
    assert not coordinator.window.load_current_button.isEnabled()
    assert not coordinator.window.export_current_button.isEnabled()
    assert "원본 영상" in coordinator.window.validation_label.text()
    coordinator.close()


def test_truth_window_is_singleton_and_close_cleans_session_and_draft_image(qtbot, tmp_path):
    coordinator, viewer = _coordinator(qtbot)
    first = coordinator.window
    coordinator._ensure_window()
    assert coordinator.window is first
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    coordinator.session.attach_new(truth_set)
    coordinator._draft_image = QImage(10, 10, QImage.Format.Format_RGB32)
    coordinator.close()
    assert coordinator.window is None
    assert coordinator.session.truth_set is None
    assert coordinator._draft_image.isNull()
