from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QThread, Signal, Slot

from oil_tracker.adapters.storage.review_mp4_exporter import ReviewMp4ExportCancelled
from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken


LOGGER = logging.getLogger(__name__)


class ReviewMp4ExportWorker(QObject):
    progress = Signal(int, object)
    completed = Signal(int, object)
    failed = Signal(int, str)
    cancelled = Signal(int)

    def __init__(self, exporter, generation: int, payload: dict, cancellation) -> None:
        super().__init__()
        self.exporter = exporter
        self.generation = int(generation)
        self.payload = dict(payload)
        self.cancellation = cancellation

    @Slot()
    def run(self) -> None:
        try:
            result = self.exporter.export(
                **self.payload,
                cancellation=self.cancellation,
                progress=lambda update: self.progress.emit(self.generation, update),
            )
        except ReviewMp4ExportCancelled:
            self.cancelled.emit(self.generation)
        except Exception as exc:
            LOGGER.exception("Annotated MP4 export worker failed")
            if self.cancellation.cancelled:
                self.cancelled.emit(self.generation)
            else:
                self.failed.emit(self.generation, str(exc))
        else:
            self.completed.emit(self.generation, result)


class ReviewMp4ExportController(QObject):
    started = Signal()
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    runningChanged = Signal(bool)

    def __init__(self, exporter, parent=None) -> None:
        super().__init__(parent)
        self.exporter = exporter
        self.thread: QThread | None = None
        self.worker: ReviewMp4ExportWorker | None = None
        self.cancellation: SimpleCancellationToken | None = None
        self.generation = 0

    @property
    def running(self) -> bool:
        return self.thread is not None

    def start(self, **payload) -> None:
        if self.running:
            raise RuntimeError("Annotated MP4 export is already running.")
        self.generation += 1
        generation = self.generation
        self.cancellation = SimpleCancellationToken()
        self.thread = QThread(self)
        self.worker = ReviewMp4ExportWorker(
            self.exporter,
            generation,
            payload,
            self.cancellation,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.worker.deleteLater)
        self.worker.progress.connect(self._progress)
        self.worker.completed.connect(self._completed)
        self.worker.failed.connect(self._failed)
        self.worker.cancelled.connect(self._cancelled)
        self.started.emit()
        self.runningChanged.emit(True)
        self.thread.start()

    def cancel(self) -> None:
        if self.cancellation is not None:
            self.cancellation.cancel()

    @Slot(int, object)
    def _progress(self, generation: int, update) -> None:
        if generation == self.generation:
            self.progress.emit(update)

    @Slot(int, object)
    def _completed(self, generation: int, result) -> None:
        if generation != self.generation:
            return
        self.completed.emit(result)
        self._finish_thread(generation)

    @Slot(int, str)
    def _failed(self, generation: int, message: str) -> None:
        if generation != self.generation:
            return
        self.failed.emit(message)
        self._finish_thread(generation)

    @Slot(int)
    def _cancelled(self, generation: int) -> None:
        if generation != self.generation:
            return
        self.cancelled.emit()
        self._finish_thread(generation)

    def _finish_thread(self, generation: int) -> None:
        if generation != self.generation:
            return
        thread = self.thread
        self.thread = None
        self.worker = None
        self.cancellation = None
        if thread is not None:
            thread.quit()
            thread.wait(5000)
            thread.deleteLater()
        self.runningChanged.emit(False)

    def close(self, timeout_ms: int = 5000) -> bool:
        self.cancel()
        thread = self.thread
        if thread is None:
            return True
        thread.quit()
        finished = bool(thread.wait(max(0, int(timeout_ms))))
        if not finished:
            LOGGER.warning("Annotated MP4 export worker did not stop during bounded close wait.")
            return False
        self.generation += 1
        thread.deleteLater()
        self.thread = None
        self.worker = None
        self.cancellation = None
        self.runningChanged.emit(False)
        return True
