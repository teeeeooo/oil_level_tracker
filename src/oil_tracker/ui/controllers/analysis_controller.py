from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot

from oil_tracker.application.ports.progress import AnalysisCancelled, MonotonicProgressSink
from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken


class AnalysisWorker(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, analyze_use_case, result_store, recipe, session, cancellation) -> None:
        super().__init__()
        self.analyze_use_case = analyze_use_case
        self.result_store = result_store
        self.recipe = recipe
        self.session = session
        self.cancellation = cancellation
        self._terminal_emitted = False

    @Slot()
    def run(self) -> None:
        reporter = MonotonicProgressSink(self.progress.emit)
        try:
            result = self.analyze_use_case.execute(
                self.recipe,
                self.session,
                progress=reporter,
                cancellation=self.cancellation,
            )
            output = self.result_store.write_bundle(
                result,
                self.recipe,
                self.session,
                Path(self.session.output_directory)
                if self.session.output_directory
                else None,
                progress=reporter,
                cancellation=self.cancellation,
            )
            self._emit_completed(result, str(output))
        except AnalysisCancelled:
            self._emit_cancelled()
        except Exception as exc:
            self._emit_failed(str(exc))

    def _emit_completed(self, result, output: str) -> None:
        if not self._terminal_emitted:
            self._terminal_emitted = True
            self.completed.emit(result, output)

    def _emit_failed(self, message: str) -> None:
        if not self._terminal_emitted:
            self._terminal_emitted = True
            self.failed.emit(message)

    def _emit_cancelled(self) -> None:
        if not self._terminal_emitted:
            self._terminal_emitted = True
            self.cancelled.emit()


class AnalysisController(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, analyze_use_case, result_store, parent=None) -> None:
        super().__init__(parent)
        self.analyze_use_case = analyze_use_case
        self.result_store = result_store
        self.thread: QThread | None = None
        self.worker: AnalysisWorker | None = None
        self.cancellation: SimpleCancellationToken | None = None
        self._terminal_received = False

    @property
    def is_running(self) -> bool:
        return self.thread is not None

    def start(self, recipe, session) -> None:
        if self.thread is not None:
            raise RuntimeError("Analysis is already running.")
        self._terminal_received = False
        self.cancellation = SimpleCancellationToken()
        self.thread = QThread(self)
        self.worker = AnalysisWorker(
            self.analyze_use_case,
            self.result_store,
            recipe,
            session,
            self.cancellation,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._forward_progress)
        self.worker.completed.connect(self._complete)
        self.worker.failed.connect(self._fail)
        self.worker.cancelled.connect(self._cancelled)
        self.thread.start()

    def cancel(self) -> None:
        if self.cancellation:
            self.cancellation.cancel()

    def shutdown(self, timeout_ms: int = 5000) -> bool:
        if self.thread is None:
            return True
        self.cancel()
        thread = self.thread
        thread.quit()
        finished = thread.wait(max(0, int(timeout_ms)))
        if finished:
            self._release_references()
        return bool(finished)

    @Slot(object)
    def _forward_progress(self, update) -> None:
        if self.sender() is self.worker and not self._terminal_received:
            self.progress.emit(update)

    @Slot(object, str)
    def _complete(self, result, output: str) -> None:
        if not self._accept_terminal():
            return
        self.completed.emit(result, output)
        self._cleanup()

    @Slot(str)
    def _fail(self, message: str) -> None:
        if not self._accept_terminal():
            return
        self.failed.emit(message)
        self._cleanup()

    @Slot()
    def _cancelled(self) -> None:
        if not self._accept_terminal():
            return
        self.cancelled.emit()
        self._cleanup()

    def _accept_terminal(self) -> bool:
        if self.sender() is not self.worker or self._terminal_received:
            return False
        self._terminal_received = True
        return True

    def _cleanup(self) -> None:
        if self.thread:
            self.thread.quit()
            self.thread.wait(5000)
        self._release_references()

    def _release_references(self) -> None:
        if self.worker:
            self.worker.deleteLater()
        if self.thread:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self.cancellation = None
