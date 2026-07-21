from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken
from oil_tracker.adapters.storage.regression_fixture_exporter import (
    RegressionFixtureExportCancelled,
)


LOGGER = logging.getLogger(__name__)


class TruthExportWorker(QObject):
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
        except RegressionFixtureExportCancelled:
            self.cancelled.emit(self.generation)
        except Exception as exc:
            LOGGER.exception("Truth fixture export worker failed")
            if self.cancellation.cancelled:
                self.cancelled.emit(self.generation)
            else:
                self.failed.emit(self.generation, str(exc))
        else:
            self.completed.emit(self.generation, result)


class TruthExportController(QObject):
    started = Signal(int, int)
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(int, str)
    cancelled = Signal(int)
    runningChanged = Signal(bool)

    def __init__(self, exporter, parent=None) -> None:
        super().__init__(parent)
        self.exporter = exporter
        self.thread: QThread | None = None
        self.worker: TruthExportWorker | None = None
        self.cancellation: SimpleCancellationToken | None = None
        self.generation = 0
        self._pending: tuple[int, dict] | None = None
        self._closing = False

    @property
    def running(self) -> bool:
        return self.thread is not None

    def start(self, *, generation: int | None = None, **payload) -> int:
        if self._closing:
            return self.generation
        requested = int(generation if generation is not None else self.generation + 1)
        self.generation = max(self.generation + (0 if generation is not None else 1), requested)
        requested = self.generation
        item = (requested, dict(payload))
        if self.running:
            self._pending = item
            self.cancel()
        else:
            self._start_now(*item)
        return requested

    def _start_now(self, generation: int, payload: dict) -> None:
        self.cancellation = SimpleCancellationToken()
        self.thread = QThread(self)
        self.worker = TruthExportWorker(
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
        total = len(tuple(payload.get("annotations", ())))
        self.started.emit(generation, total)
        self.runningChanged.emit(True)
        self.thread.start()

    def cancel(self) -> None:
        if self.cancellation is not None:
            self.cancellation.cancel()

    def invalidate(self) -> None:
        self.generation += 1
        self._pending = None
        self.cancel()

    @Slot(int, object)
    def _progress(self, generation: int, update) -> None:
        if generation == self.generation and not self._closing:
            self.progress.emit(update)

    @Slot(int, object)
    def _completed(self, generation: int, result) -> None:
        if generation == self.generation and not self._closing:
            self.completed.emit(result)
        self._finish_thread()

    @Slot(int, str)
    def _failed(self, generation: int, message: str) -> None:
        if generation == self.generation and not self._closing:
            self.failed.emit(generation, message)
        self._finish_thread()

    @Slot(int)
    def _cancelled(self, generation: int) -> None:
        if generation == self.generation and not self._closing:
            self.cancelled.emit(generation)
        self._finish_thread()

    def _finish_thread(self) -> None:
        thread = self.thread
        self.thread = None
        self.worker = None
        self.cancellation = None
        if thread is not None:
            thread.quit()
            thread.wait(5000)
            thread.deleteLater()
        self.runningChanged.emit(False)
        pending, self._pending = self._pending, None
        if pending is not None and not self._closing:
            QTimer.singleShot(0, lambda item=pending: self._start_now(*item))

    def close(self) -> None:
        self._closing = True
        self._pending = None
        self.cancel()
        thread = self.thread
        if thread is not None:
            thread.quit()
            if not thread.wait(5000):
                LOGGER.warning("Truth export worker did not stop during bounded close wait.")
                return
            thread.deleteLater()
        self.thread = None
        self.worker = None
        self.cancellation = None
        self.runningChanged.emit(False)
