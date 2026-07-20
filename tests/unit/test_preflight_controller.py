from __future__ import annotations

from types import SimpleNamespace
import threading
import time

from oil_tracker.application.preflight import PreflightCancelled, PreflightProgress
from oil_tracker.ui.controllers.preflight_controller import PreflightController


class ImmediateUseCase:
    def execute(self, recipe, _session, progress=None, cancellation=None):
        assert cancellation is not None
        if progress:
            progress(PreflightProgress(1, 1, "분석 시작", "관찰창 1"))
        return SimpleNamespace(marker=recipe["marker"])


class FailingUseCase:
    def execute(self, *_args, **_kwargs):
        raise RuntimeError("preflight failed")


class CancellableUseCase:
    def __init__(self) -> None:
        self.started = threading.Event()

    def execute(self, _recipe, _session, progress=None, cancellation=None):
        self.started.set()
        while not cancellation.cancelled:
            time.sleep(0.005)
        raise PreflightCancelled("cancelled")


class GenerationUseCase:
    def __init__(self) -> None:
        self.first_started = threading.Event()

    def execute(self, recipe, _session, progress=None, cancellation=None):
        if recipe["marker"] == "old":
            self.first_started.set()
            while not cancellation.cancelled:
                time.sleep(0.005)
            raise PreflightCancelled("old cancelled")
        if progress:
            progress(PreflightProgress(1, 1, "분석 종료 직전", "관찰창 2"))
        return SimpleNamespace(marker="new")


def _wait_for_cleanup(qtbot, controller: PreflightController) -> None:
    qtbot.waitUntil(lambda: not controller._runs, timeout=2000)


def test_controller_runs_off_gui_thread_and_emits_progress_and_completed(qtbot):
    controller = PreflightController(ImmediateUseCase())
    progress_updates = []
    controller.progress.connect(progress_updates.append)

    with qtbot.waitSignal(controller.completed, timeout=2000) as completed:
        controller.start({"marker": "done"}, {})
        assert controller.is_running

    assert completed.args[0].marker == "done"
    assert progress_updates[-1].sample_label == "분석 시작"
    _wait_for_cleanup(qtbot, controller)


def test_controller_emits_failed_for_non_cancellation_error(qtbot):
    controller = PreflightController(FailingUseCase())

    with qtbot.waitSignal(controller.failed, timeout=2000) as failed:
        controller.start({"marker": "failed"}, {})

    assert failed.args == ["preflight failed"]
    _wait_for_cleanup(qtbot, controller)


def test_controller_cancel_is_distinct_from_failure(qtbot):
    use_case = CancellableUseCase()
    controller = PreflightController(use_case)
    failures = []
    controller.failed.connect(failures.append)
    controller.start({"marker": "cancel"}, {})
    assert use_case.started.wait(1.0)

    with qtbot.waitSignal(controller.cancelled, timeout=2000):
        controller.cancel()

    assert failures == []
    _wait_for_cleanup(qtbot, controller)


def test_new_generation_suppresses_old_progress_and_terminal_signals(qtbot):
    use_case = GenerationUseCase()
    controller = PreflightController(use_case)
    completed_markers = []
    cancelled_count = []
    controller.completed.connect(lambda result: completed_markers.append(result.marker))
    controller.cancelled.connect(lambda: cancelled_count.append(True))

    controller.start({"marker": "old"}, {})
    assert use_case.first_started.wait(1.0)
    with qtbot.waitSignal(controller.completed, timeout=2000):
        controller.start({"marker": "new"}, {})

    assert completed_markers == ["new"]
    assert cancelled_count == []
    _wait_for_cleanup(qtbot, controller)


def test_invalidate_cancels_running_request_without_publishing_stale_cancel(qtbot):
    use_case = CancellableUseCase()
    controller = PreflightController(use_case)
    cancelled_count = []
    controller.cancelled.connect(lambda: cancelled_count.append(True))
    controller.start({"marker": "invalidate"}, {})
    assert use_case.started.wait(1.0)

    controller.invalidate()
    _wait_for_cleanup(qtbot, controller)

    assert cancelled_count == []
