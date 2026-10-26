"""One worker process per Glass for the frame loop of a detection run (opt-in).

Every Glass keeps its own detector state, so a worker that holds an identically
configured detector, its own video reader and only its Glass produces the same
detections as the shared sequential loop. The parent consumes the workers'
results in the sequential order (target by target, Glass by Glass), so every
callback, failure count and trace record keeps its order.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import multiprocessing
import pickle
import queue as queue_module
import time
from typing import Any

from oil_tracker.application.services.detection_processing import learn_static_artifacts
from oil_tracker.domain.recipe import GlassInspectionConfig

# A few records of look-ahead per Glass keep both workers busy while bounding
# the memory held by results the parent has not consumed yet.
QUEUE_SLOTS = 4
POLL_SEC = 0.5


class GlassWorkerError(RuntimeError):
    """A worker ended or disagreed with the other workers about a decoded frame."""


def worker_factories(detector, video_reader_factory) -> tuple[Callable[[], Any], Callable[[str], Any]] | None:
    """The picklable factories a worker needs, or None when the run must stay sequential."""

    factory = getattr(detector, "worker_factory", None)
    if not callable(factory):
        return None
    detector_factory = factory()
    try:
        pickle.dumps(detector_factory)
        pickle.dumps(video_reader_factory)
    except Exception:
        return None
    return detector_factory, video_reader_factory


def _portable(exc: Exception) -> Exception:
    try:
        pickle.loads(pickle.dumps(exc))
    except Exception:
        return RuntimeError(f"{type(exc).__name__}: {exc}")
    return exc


def _glass_worker(
    detector_factory,
    video_reader_factory,
    source_video_path: str,
    glass: GlassInspectionConfig,
    timestamps: Sequence[float],
    static_schedule: Sequence[float],
    debug: bool,
    results,
) -> None:
    try:
        detector = detector_factory()
        detector.reset()
        reader = video_reader_factory(source_video_path)
        try:
            learn_static_artifacts(reader, detector, (glass,), static_schedule)
            results.put(("static_ready",))
            for index, timestamp in enumerate(timestamps):
                try:
                    frame, frame_index, actual_timestamp = reader.read_at(timestamp)
                except Exception as exc:
                    results.put(("decode_error", index, _portable(exc)))
                    continue
                try:
                    detection, artifacts = detector.detect(
                        frame, glass, frame_index, actual_timestamp, debug=debug,
                    )
                except Exception as exc:
                    results.put(("detect_error", index, frame_index, actual_timestamp, _portable(exc)))
                    continue
                results.put(("ok", index, frame_index, actual_timestamp, detection, artifacts))
        finally:
            reader.close()
        results.put(("done",))
    except BaseException as exc:  # noqa: BLE001 - reported to the parent, which raises it
        results.put(("worker_error", _portable(exc) if isinstance(exc, Exception) else RuntimeError(repr(exc))))


class GlassWorkers:
    """The parent's view of one worker per Glass, read strictly in the sequential order."""

    def __init__(
        self,
        factories: tuple[Callable[[], Any], Callable[[str], Any]],
        source_video_path: str,
        glasses: Sequence[GlassInspectionConfig],
        timestamps: Sequence[float],
        static_schedule: Sequence[float],
        debug: bool,
    ) -> None:
        context = multiprocessing.get_context("spawn")
        self.glasses = tuple(glasses)
        self._queues = {}
        self._processes = {}
        self._current: dict[str, tuple] = {}
        self._current_index = -1
        # Time the parent spends blocked on the workers: near zero means the
        # parent's own work (trace writing) is the critical path.
        self.wait_sec = 0.0
        detector_factory, video_reader_factory = factories
        for glass in self.glasses:
            results = context.Queue(maxsize=QUEUE_SLOTS)
            process = context.Process(
                target=_glass_worker,
                args=(detector_factory, video_reader_factory, source_video_path, glass,
                      tuple(timestamps), tuple(static_schedule), debug, results),
                daemon=True,
            )
            process.start()
            self._queues[glass.id] = results
            self._processes[glass.id] = process

    def _next(self, glass_id: str, check_cancelled: Callable[[], None] | None):
        results = self._queues[glass_id]
        while True:
            if check_cancelled is not None:
                check_cancelled()
            started = time.perf_counter()
            try:
                message = results.get(timeout=POLL_SEC)
            except queue_module.Empty:
                self.wait_sec += time.perf_counter() - started
                if not self._processes[glass_id].is_alive():
                    raise GlassWorkerError(f"Detection worker for Glass {glass_id} ended unexpectedly.") from None
                continue
            self.wait_sec += time.perf_counter() - started
            if message[0] == "worker_error":
                raise message[1]
            return message

    def wait_static_ready(self, check_cancelled: Callable[[], None] | None = None) -> None:
        for glass in self.glasses:
            message = self._next(glass.id, check_cancelled)
            if message[0] != "static_ready":
                raise GlassWorkerError(f"Unexpected worker message before the frame loop: {message[0]}")

    def decode(self, index: int, check_cancelled: Callable[[], None] | None = None):
        """Collect every Glass's result for one target; return the first Glass's decode as the shared one."""

        self._current = {}
        for glass in self.glasses:
            message = self._next(glass.id, check_cancelled)
            if message[0] not in {"ok", "detect_error", "decode_error"} or message[1] != index:
                raise GlassWorkerError(f"Out-of-order worker message for Glass {glass.id}: {message[:2]}")
            self._current[glass.id] = message
        self._current_index = index
        first = self._current[self.glasses[0].id]
        if first[0] == "decode_error":
            raise first[2]
        return None, first[2], first[3]

    def detect(self, index: int, glass: GlassInspectionConfig, frame_index: int, actual_timestamp: float):
        if index != self._current_index:
            raise GlassWorkerError(f"Detection requested for target {index} before it was collected.")
        message = self._current[glass.id]
        if message[0] == "decode_error":
            raise message[2]
        if (message[2], message[3]) != (frame_index, actual_timestamp):
            raise GlassWorkerError(
                f"Glass {glass.id} decoded frame {message[2]} at {message[3]} s; "
                f"the shared decode is frame {frame_index} at {actual_timestamp} s."
            )
        if message[0] == "detect_error":
            raise message[4]
        return message[4], message[5]

    def close(self) -> None:
        for process in self._processes.values():
            if process.is_alive():
                process.terminate()
        for process in self._processes.values():
            process.join(timeout=5)
        for results in self._queues.values():
            results.close()
            results.cancel_join_thread()
