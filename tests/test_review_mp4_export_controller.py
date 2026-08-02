from __future__ import annotations

from dataclasses import dataclass
import time

from oil_tracker.adapters.storage.review_mp4_exporter import (
    ReviewMp4ExportCancelled,
    ReviewMp4ExportProgress,
)
from oil_tracker.ui.controllers.review_mp4_export_controller import ReviewMp4ExportController


@dataclass(frozen=True)
class _Result:
    name: str


class _Exporter:
    def __init__(self, *, fail=False, steps=3):
        self.fail = fail
        self.steps = steps
        self.calls = []
        self.cancelled_calls = 0

    def export(self, *, cancellation, progress, name="run", **_payload):
        self.calls.append(name)
        for index in range(self.steps):
            if cancellation.cancelled:
                self.cancelled_calls += 1
                raise ReviewMp4ExportCancelled("cancelled")
            progress(ReviewMp4ExportProgress(index + 1, self.steps, index / 10.0))
            time.sleep(0.01)
        if self.fail:
            raise RuntimeError("export failed")
        return _Result(name)


def test_controller_runs_export_off_gui_thread_and_forwards_progress(qtbot):
    exporter = _Exporter()
    controller = ReviewMp4ExportController(exporter)
    completed = []
    progress = []
    controller.completed.connect(completed.append)
    controller.progress.connect(progress.append)
    controller.start(name="first")
    assert controller.running
    assert completed == []
    qtbot.waitUntil(lambda: bool(completed), timeout=3000)
    assert completed == [_Result("first")]
    assert len(progress) == 3
    assert exporter.calls == ["first"]
    assert not controller.running
    assert controller.close()


def test_controller_reports_failure_and_clears_worker(qtbot):
    controller = ReviewMp4ExportController(_Exporter(fail=True))
    failed = []
    controller.failed.connect(failed.append)
    controller.start(name="failure")
    qtbot.waitUntil(lambda: bool(failed), timeout=3000)
    assert failed == ["export failed"]
    assert controller.thread is None
    assert controller.worker is None
    assert controller.cancellation is None
    assert not controller.running
    assert controller.close()


def test_controller_cancellation_is_cooperative_and_terminal(qtbot):
    exporter = _Exporter(steps=100)
    controller = ReviewMp4ExportController(exporter)
    cancelled = []
    completed = []
    controller.cancelled.connect(lambda: cancelled.append(True))
    controller.completed.connect(completed.append)
    controller.start(name="cancel")
    qtbot.waitUntil(lambda: controller.running, timeout=1000)
    controller.cancel()
    qtbot.waitUntil(lambda: bool(cancelled), timeout=3000)
    assert cancelled == [True]
    assert completed == []
    assert exporter.cancelled_calls == 1
    assert not controller.running
    assert controller.close()


def test_controller_rejects_concurrent_export(qtbot):
    controller = ReviewMp4ExportController(_Exporter(steps=50))
    controller.start(name="first")
    qtbot.waitUntil(lambda: controller.running, timeout=1000)
    try:
        try:
            controller.start(name="second")
        except RuntimeError as exc:
            assert "already running" in str(exc)
        else:
            raise AssertionError("concurrent export should be rejected")
    finally:
        controller.cancel()
        qtbot.waitUntil(lambda: not controller.running, timeout=3000)
        assert controller.close()


def test_close_cancels_worker_and_releases_thread_references(qtbot):
    exporter = _Exporter(steps=100)
    controller = ReviewMp4ExportController(exporter)
    controller.start(name="close")
    qtbot.waitUntil(lambda: controller.running, timeout=1000)
    assert controller.close(timeout_ms=3000)
    assert controller.thread is None
    assert controller.worker is None
    assert controller.cancellation is None
    assert not controller.running


def test_close_without_active_export_keeps_controller_reusable(qtbot):
    controller = ReviewMp4ExportController(_Exporter())
    assert controller.close()
    completed = []
    controller.completed.connect(completed.append)
    controller.start(name="reopened")
    qtbot.waitUntil(lambda: completed == [_Result("reopened")], timeout=3000)
    assert not controller.running
    assert controller.close()
