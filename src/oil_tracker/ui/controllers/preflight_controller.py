from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from PySide6.QtCore import QObject, QThread, Signal, Slot

from oil_tracker.application.preflight import PreflightCancelled
from oil_tracker.application.use_cases.preflight_check import PreflightCancellationToken


class PreflightWorker(QObject):
    progress = Signal(int, object)
    completed = Signal(int, object)
    failed = Signal(int, str)
    cancelled = Signal(int)

    def __init__(self, generation: int, use_case, recipe, session, cancellation) -> None:
        super().__init__()
        self.generation = generation
        self.use_case = use_case
        self.recipe = recipe
        self.session = session
        self.cancellation = cancellation

    @Slot()
    def run(self) -> None:
        try:
            result = self.use_case.execute(
                self.recipe,
                self.session,
                progress=lambda update: self.progress.emit(self.generation, update),
                cancellation=self.cancellation,
            )
            self.completed.emit(self.generation, result)
        except PreflightCancelled:
            self.cancelled.emit(self.generation)
        except Exception as exc:
            if self.cancellation.cancelled:
                self.cancelled.emit(self.generation)
            else:
                self.failed.emit(self.generation, str(exc))


@dataclass
class _ActiveRun:
    thread: QThread
    worker: PreflightWorker
    cancellation: PreflightCancellationToken


class PreflightController(QObject):
    started = Signal()
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, use_case, parent=None) -> None:
        super().__init__(parent)
        self.use_case = use_case
        self.generation = 0
        self._runs: dict[int, _ActiveRun] = {}

    @property
    def is_running(self) -> bool:
        return self.generation in self._runs

    def start(self, recipe, session) -> None:
        self._invalidate_existing()
        self.generation += 1
        generation = self.generation
        cancellation = PreflightCancellationToken()
        thread = QThread(self)
        worker = PreflightWorker(
            generation,
            self.use_case,
            deepcopy(recipe),
            deepcopy(session),
            cancellation,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._progress)
        worker.completed.connect(self._completed)
        worker.failed.connect(self._failed)
        worker.cancelled.connect(self._cancelled)
        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.cancelled.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda gen=generation: self._cleanup(gen))
        self._runs[generation] = _ActiveRun(thread, worker, cancellation)
        self.started.emit()
        thread.start()

    def cancel(self) -> None:
        active = self._runs.get(self.generation)
        if active is not None:
            active.cancellation.cancel()

    def invalidate(self) -> None:
        self._invalidate_existing()
        self.generation += 1

    def _invalidate_existing(self) -> None:
        for active in self._runs.values():
            active.cancellation.cancel()

    @Slot(int, object)
    def _progress(self, generation: int, update) -> None:
        if generation == self.generation:
            self.progress.emit(update)

    @Slot(int, object)
    def _completed(self, generation: int, result) -> None:
        if generation == self.generation:
            self.completed.emit(result)

    @Slot(int, str)
    def _failed(self, generation: int, message: str) -> None:
        if generation == self.generation:
            self.failed.emit(message)

    @Slot(int)
    def _cancelled(self, generation: int) -> None:
        if generation == self.generation:
            self.cancelled.emit()

    def _cleanup(self, generation: int) -> None:
        active = self._runs.pop(generation, None)
        if active is not None:
            active.thread.deleteLater()
