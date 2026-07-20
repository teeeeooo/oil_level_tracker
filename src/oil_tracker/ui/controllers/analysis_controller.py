from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot

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

    @Slot()
    def run(self) -> None:
        try:
            result = self.analyze_use_case.execute(self.recipe, self.session, progress=self.progress.emit, cancellation=self.cancellation)
            output = self.result_store.write_bundle(result, self.recipe, self.session, Path(self.session.output_directory) if self.session.output_directory else None)
            self.completed.emit(result, str(output))
        except Exception as exc:
            if self.cancellation.cancelled:
                self.cancelled.emit()
            else:
                self.failed.emit(str(exc))


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

    def start(self, recipe, session) -> None:
        if self.thread is not None:
            raise RuntimeError("Analysis is already running.")
        self.cancellation = SimpleCancellationToken()
        self.thread = QThread(self)
        self.worker = AnalysisWorker(self.analyze_use_case, self.result_store, recipe, session, self.cancellation)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress)
        self.worker.completed.connect(self._complete)
        self.worker.failed.connect(self._fail)
        self.worker.cancelled.connect(self._cancelled)
        self.thread.start()

    def cancel(self) -> None:
        if self.cancellation:
            self.cancellation.cancel()

    @Slot(object, str)
    def _complete(self, result, output: str) -> None:
        self.completed.emit(result, output)
        self._cleanup()

    @Slot(str)
    def _fail(self, message: str) -> None:
        self.failed.emit(message)
        self._cleanup()

    @Slot()
    def _cancelled(self) -> None:
        self.cancelled.emit()
        self._cleanup()

    def _cleanup(self) -> None:
        if self.thread:
            self.thread.quit()
            self.thread.wait(3000)
            self.thread.deleteLater()
        if self.worker:
            self.worker.deleteLater()
        self.thread = None
        self.worker = None
        self.cancellation = None
