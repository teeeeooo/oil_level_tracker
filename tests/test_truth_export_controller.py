from __future__ import annotations

from dataclasses import dataclass
import time

import pytest

from oil_tracker.adapters.storage.regression_fixture_exporter import (
    FixtureExportProgress,
    RegressionFixtureExportCancelled,
)
from oil_tracker.ui.controllers.truth_export_controller import TruthExportController


@dataclass(frozen=True)
class _Result:
    name: str


class _Exporter:
    def __init__(self, *, fail: bool = False, steps: int = 3) -> None:
        self.fail = fail
        self.steps = steps
        self.calls = []
        self.cancelled_calls = 0

    def export(self, *, annotations, cancellation, progress, name="run", **_payload):
        annotations = tuple(annotations)
        self.calls.append(name)
        for index in range(self.steps):
            if cancellation.cancelled:
                self.cancelled_calls += 1
                raise RegressionFixtureExportCancelled("cancelled")
            progress(
                FixtureExportProgress(
                    annotation_id=str(annotations[0]) if annotations else "",
                    processed_fixtures=index,
                    total_fixtures=self.steps,
                    stage="work",
                    message=f"step {index}",
                )
            )
            time.sleep(0.01)
        if self.fail:
            raise RuntimeError("export failed")
        return _Result(name)


def test_export_controller_runs_off_gui_thread_and_emits_progress(qtbot):
    exporter = _Exporter()
    controller = TruthExportController(exporter)
    completed = []
    progress = []
    controller.completed.connect(completed.append)
    controller.progress.connect(progress.append)
    generation = controller.start(annotations=("a",), name="first")
    assert generation == 1
    assert controller.running
    assert completed == []
    qtbot.waitUntil(lambda: bool(completed), timeout=3000)
    assert completed == [_Result("first")]
    assert progress
    assert exporter.calls == ["first"]
    assert not controller.running
    controller.close()


def test_export_controller_reports_failure_without_raw_exception(qtbot):
    controller = TruthExportController(_Exporter(fail=True))
    failed = []
    controller.failed.connect(lambda generation, message: failed.append((generation, message)))
    controller.start(annotations=("a",), name="failure")
    qtbot.waitUntil(lambda: bool(failed), timeout=3000)
    assert failed == [(1, "export failed")]
    assert not controller.running
    controller.close()


def test_export_controller_cancellation_is_cooperative_and_terminal(qtbot):
    exporter = _Exporter(steps=100)
    controller = TruthExportController(exporter)
    cancelled = []
    completed = []
    controller.cancelled.connect(cancelled.append)
    controller.completed.connect(completed.append)
    generation = controller.start(annotations=("a",), name="cancel")
    qtbot.waitUntil(lambda: controller.running, timeout=1000)
    controller.cancel()
    qtbot.waitUntil(lambda: bool(cancelled), timeout=3000)
    assert cancelled == [generation]
    assert completed == []
    assert exporter.cancelled_calls == 1
    controller.close()


def test_rapid_restart_cancels_old_generation_and_surfaces_only_latest(qtbot):
    exporter = _Exporter(steps=20)
    controller = TruthExportController(exporter)
    completed = []
    cancelled = []
    controller.completed.connect(completed.append)
    controller.cancelled.connect(cancelled.append)
    first = controller.start(annotations=("a",), name="old")
    second = controller.start(annotations=("b",), name="latest")
    assert second > first
    qtbot.waitUntil(lambda: completed == [_Result("latest")], timeout=5000)
    assert exporter.calls == ["old", "latest"]
    assert completed == [_Result("latest")]
    assert first not in cancelled
    controller.close()


def test_invalidate_suppresses_stale_completion(qtbot):
    exporter = _Exporter(steps=10)
    controller = TruthExportController(exporter)
    completed = []
    failed = []
    cancelled = []
    controller.completed.connect(completed.append)
    controller.failed.connect(lambda generation, message: failed.append((generation, message)))
    controller.cancelled.connect(cancelled.append)
    controller.start(annotations=("a",), name="stale")
    controller.invalidate()
    qtbot.waitUntil(lambda: not controller.running, timeout=3000)
    assert completed == []
    assert failed == []
    assert cancelled == []
    controller.close()


def test_close_cancels_worker_and_clears_references(qtbot):
    exporter = _Exporter(steps=100)
    controller = TruthExportController(exporter)
    controller.start(annotations=("a",), name="close")
    qtbot.waitUntil(lambda: controller.running, timeout=1000)
    controller.close()
    assert controller.thread is None
    assert controller.worker is None
    assert controller.cancellation is None
    assert not controller.running
