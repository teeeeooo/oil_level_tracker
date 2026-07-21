from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QFileDialog, QMessageBox

from oil_tracker.ui.result_review_window import ResultReviewWindow
from review_raster_fixtures import solid_image


class _RecordingExporter:
    def __init__(self, *, error=None):
        self.error = error
        self.calls = []

    def export(self, image, destination, **kwargs):
        self.calls.append((QImage(image).copy(), Path(destination), kwargs))
        if self.error is not None:
            raise self.error
        return Path(destination).with_suffix(".png")


def _window(qtbot, tmp_path, exporter):
    root = tmp_path / "bundle"
    root.mkdir()
    glass = SimpleNamespace(name="유면 관찰창 1")
    bundle = SimpleNamespace(
        root=root,
        glass_config=lambda _glass_id: glass,
    )
    window = ResultReviewWindow(png_exporter=exporter)
    qtbot.addWidget(window)
    window.bundle = bundle
    window.selected_glass_id = "glass-1"
    window.current_time = 2.125
    window.current_render_image = solid_image(640, 360, (10, 20, 30))
    window._set_state("영상 로드됨 · 일시정지")
    return window


def test_png_dialog_cancel_does_not_call_exporter(qtbot, tmp_path, monkeypatch):
    exporter = _RecordingExporter()
    window = _window(qtbot, tmp_path, exporter)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))
    window.save_current_png()
    assert exporter.calls == []
    assert not window.current_render_image.isNull()
    window.close()


def test_png_success_passes_detached_current_snapshot_and_protected_bundle_root(qtbot, tmp_path, monkeypatch):
    exporter = _RecordingExporter()
    window = _window(qtbot, tmp_path, exporter)
    destination = tmp_path / "한글 경로" / "현재 장면.any"
    messages = []
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(destination), "PNG"))
    monkeypatch.setattr(QMessageBox, "information", lambda _parent, title, message: messages.append((title, message)))
    window.save_current_png()
    assert len(exporter.calls) == 1
    image, requested, kwargs = exporter.calls[0]
    assert requested == destination
    assert (image.width(), image.height()) == (640, 360)
    assert kwargs["protected_roots"] == (window.bundle.root,)
    assert kwargs["overwrite"] is True
    assert messages and messages[-1][0] == "PNG 저장 완료"
    image.fill(0)
    assert window.current_render_image.pixelColor(0, 0).red() == 10
    window.close()


def test_png_export_failure_preserves_display_image_and_viewer_state(qtbot, tmp_path, monkeypatch):
    exporter = _RecordingExporter(error=OSError("disk full"))
    window = _window(qtbot, tmp_path, exporter)
    before_image = window.current_render_image.copy()
    before_state = window.state
    messages = []
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(tmp_path / "failed.png"), "PNG"))
    monkeypatch.setattr(QMessageBox, "critical", lambda _parent, title, message: messages.append((title, message)))
    window.save_current_png()
    assert len(exporter.calls) == 1
    assert messages and messages[-1][0] == "PNG 저장 실패"
    assert "disk full" in messages[-1][1]
    assert window.current_render_image == before_image
    assert window.state == before_state
    assert window.save_png_action.isEnabled()
    window.close()
