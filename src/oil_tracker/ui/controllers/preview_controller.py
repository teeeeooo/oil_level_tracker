from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot


class PreviewSignals(QObject):
    completed = Signal(int, object, object)
    failed = Signal(int, str)


class PreviewTask(QRunnable):
    def __init__(self, generation: int, use_case, frame, glass, frame_index: int, time_sec: float) -> None:
        super().__init__()
        self.generation = generation
        self.use_case = use_case
        self.frame = frame.copy()
        self.glass = glass
        self.frame_index = frame_index
        self.time_sec = time_sec
        self.signals = PreviewSignals()

    @Slot()
    def run(self) -> None:
        try:
            detection, artifacts = self.use_case.execute(self.frame, self.glass, self.frame_index, self.time_sec, debug=True)
            self.signals.completed.emit(self.generation, detection, artifacts)
        except Exception as exc:
            self.signals.failed.emit(self.generation, str(exc))


class PreviewController(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def __init__(self, use_case, parent=None) -> None:
        super().__init__(parent)
        self.use_case = use_case
        self.pool = QThreadPool.globalInstance()
        self.generation = 0

    def invalidate(self) -> None:
        self.generation += 1

    def request(self, frame, glass, frame_index: int, time_sec: float) -> None:
        self.generation += 1
        generation = self.generation
        task = PreviewTask(generation, self.use_case, frame, glass, frame_index, time_sec)
        task.signals.completed.connect(self._completed)
        task.signals.failed.connect(self._failed)
        self.pool.start(task)

    @Slot(int, object, object)
    def _completed(self, generation: int, detection, artifacts) -> None:
        if generation == self.generation:
            self.previewReady.emit(detection, artifacts)

    @Slot(int, str)
    def _failed(self, generation: int, message: str) -> None:
        if generation == self.generation:
            self.previewFailed.emit(message)
