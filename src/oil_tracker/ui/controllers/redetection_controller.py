from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken
from oil_tracker.application.services.redetection_service import RedetectionCancelled


LOGGER = logging.getLogger(__name__)


class RedetectionWorker(QObject):
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(int, str)
    cancelled = Signal(int)

    def __init__(
        self,
        service,
        request,
        official_bundle,
        official_candidate_timestamps,
        cancellation,
    ) -> None:
        super().__init__()
        self.service = service
        self.request = request
        self.official_bundle = official_bundle
        self.official_candidate_timestamps = tuple(official_candidate_timestamps)
        self.cancellation = cancellation

    @Slot()
    def run(self) -> None:
        try:
            output = self.service.run(
                self.request,
                self.official_bundle,
                official_candidate_timestamps=self.official_candidate_timestamps,
                progress=self.progress.emit,
                cancellation=self.cancellation,
            )
        except RedetectionCancelled:
            self.cancelled.emit(self.request.generation)
        except Exception as exc:
            LOGGER.exception("Redetection worker failed")
            if self.cancellation.cancelled:
                self.cancelled.emit(self.request.generation)
            else:
                self.failed.emit(self.request.generation, str(exc))
        else:
            self.completed.emit(output)


class RedetectionController(QObject):
    started = Signal(int, str)
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(int, str)
    cancelled = Signal(int)
    runningChanged = Signal(bool)

    def __init__(self, service, parent=None) -> None:
        super().__init__(parent)
        self.service = service
        self.thread: QThread | None = None
        self.worker: RedetectionWorker | None = None
        self.cancellation: SimpleCancellationToken | None = None
        self.generation = 0
        self.current_workspace = None
        self.current_output = None
        self._pending = None
        self._closing = False

    @property
    def running(self) -> bool:
        return self.thread is not None

    def start(self, request, official_bundle, official_candidate_timestamps=()) -> None:
        if self._closing:
            return
        self.generation = max(self.generation, int(request.generation))
        payload = (request, official_bundle, tuple(official_candidate_timestamps))
        if self.running:
            self._pending = payload
            self.cancel()
            return
        self._start_now(*payload)

    def _start_now(self, request, official_bundle, official_candidate_timestamps) -> None:
        self._cleanup_completed_workspace()
        self.cancellation = SimpleCancellationToken()
        self.thread = QThread(self)
        self.worker = RedetectionWorker(
            self.service,
            request,
            official_bundle,
            official_candidate_timestamps,
            self.cancellation,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._progress)
        self.worker.completed.connect(self._complete)
        self.worker.failed.connect(self._fail)
        self.worker.cancelled.connect(self._cancelled)
        self.started.emit(request.generation, request.mode.value)
        self.runningChanged.emit(True)
        self.thread.start()

    def cancel(self) -> None:
        if self.cancellation is not None:
            self.cancellation.cancel()

    def invalidate(self, generation: int | None = None) -> None:
        if generation is not None:
            self.generation = max(self.generation, int(generation))
        else:
            self.generation += 1
        self._pending = None
        self.cancel()

    @Slot(object)
    def _progress(self, update) -> None:
        if update.generation == self.generation:
            self.progress.emit(update)

    @Slot(object)
    def _complete(self, output) -> None:
        generation = output.result.request.generation
        if generation != self.generation or self._closing:
            output.workspace.cleanup()
        else:
            self.current_workspace = output.workspace
            self.current_output = output
            self.completed.emit(output.result)
        self._finish_thread()

    @Slot(int, str)
    def _fail(self, generation: int, message: str) -> None:
        if generation == self.generation and not self._closing:
            self.failed.emit(generation, message)
        self._finish_thread()

    @Slot(int)
    def _cancelled(self, generation: int) -> None:
        if generation == self.generation and not self._closing:
            self.cancelled.emit(generation)
        self._finish_thread()

    def _finish_thread(self) -> None:
        thread, worker = self.thread, self.worker
        self.thread = None
        self.worker = None
        self.cancellation = None
        if thread is not None:
            thread.quit()
            thread.wait(5000)
            thread.deleteLater()
        if worker is not None:
            worker.deleteLater()
        self.runningChanged.emit(False)
        pending, self._pending = self._pending, None
        if pending is not None and not self._closing:
            QTimer.singleShot(0, lambda payload=pending: self._start_now(*payload))

    def _cleanup_completed_workspace(self) -> None:
        workspace, self.current_workspace = self.current_workspace, None
        self.current_output = None
        if workspace is not None:
            workspace.cleanup()

    def close(self) -> None:
        self._closing = True
        self._pending = None
        self.cancel()
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait(5000)
        self.thread = None
        self.worker = None
        self.cancellation = None
        self._cleanup_completed_workspace()
