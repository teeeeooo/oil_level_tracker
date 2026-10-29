"""Long work on a thread, polled by the UI: one analysis at a time (architecture.md, "Long work runs as a job")."""

from __future__ import annotations

import sys
import threading
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from oil_tracker.application.ports import AnalysisCancelled

ESTIMATE_AFTER = 0.02  # of the work, before the time left is shown
ESTIMATE_AFTER_SEC = 2.0

Work = Callable[[Callable[[int, int], None], Callable[[], bool]], object]


class JobsBusy(RuntimeError):
    pass


class UnknownJob(LookupError):
    pass


@dataclass
class _Job:
    id: str
    inspection_id: str
    started: float
    cancel: threading.Event = field(default_factory=threading.Event)
    thread: threading.Thread | None = None
    done: int = 0
    total: int = 0
    state: str = "running"  # running, finished, cancelled, failed
    message: str | None = None
    ended: float | None = None


class Jobs:
    def __init__(self, new_id: Callable[[], str], clock: Callable[[], float] = time.monotonic) -> None:
        self._new_id = new_id
        self._clock = clock
        self._jobs: dict[str, _Job] = {}
        self._lock = threading.Lock()

    def running(self) -> dict[str, Any] | None:
        with self._lock:
            job = next((j for j in self._jobs.values() if j.state == "running"), None)
            return None if job is None else self._status(job)

    def start(self, inspection_id: str, work: Work) -> dict[str, Any]:
        """Run `work(progress, cancelled)` on a new thread. JobsBusy while another one runs."""
        with self._lock:
            if any(j.state == "running" for j in self._jobs.values()):
                raise JobsBusy("다른 분석이 진행 중입니다.")
            job = _Job(self._new_id(), inspection_id, self._clock())
            self._jobs[job.id] = job
            job.thread = threading.Thread(target=self._run, args=(job, work), name=f"job-{job.id}", daemon=True)
            job.thread.start()
            return self._status(job)

    def status(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            return self._status(self._get(job_id))

    def cancel(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            job = self._get(job_id)
            job.cancel.set()
            return self._status(job)

    def stop_all(self, timeout: float) -> None:
        """Cancel every running job and wait up to `timeout` seconds for each, as the app closes."""
        with self._lock:
            running = [j for j in self._jobs.values() if j.state == "running"]
            for job in running:
                job.cancel.set()
        for job in running:
            if job.thread is not None:
                job.thread.join(timeout)

    def _run(self, job: _Job, work: Work) -> None:
        def progress(done: int, total: int) -> None:
            with self._lock:
                job.done, job.total = done, total

        try:
            work(progress, job.cancel.is_set)
            state, message = "finished", None
        except AnalysisCancelled:
            state, message = "cancelled", None
        except Exception as failure:  # noqa: BLE001 - the UI shows it; the use case recorded it
            traceback.print_exc(file=sys.stderr)
            state, message = "failed", str(failure) or type(failure).__name__
        with self._lock:
            job.state, job.message, job.ended = state, message, self._clock()

    def _get(self, job_id: str) -> _Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise UnknownJob(f"알 수 없는 작업입니다: {job_id}")
        return job

    def _status(self, job: _Job) -> dict[str, Any]:
        elapsed = (job.ended if job.ended is not None else self._clock()) - job.started
        fraction = job.done / job.total if job.total else 0.0
        if job.state == "finished":
            fraction = 1.0
        time_left = None
        if job.state == "running" and fraction >= ESTIMATE_AFTER and elapsed >= ESTIMATE_AFTER_SEC:
            time_left = elapsed * (1 - fraction) / fraction
        return {
            "id": job.id,
            "inspection_id": job.inspection_id,
            "state": job.state,
            "cancel_requested": job.cancel.is_set(),
            "fraction": fraction,
            "elapsed_sec": elapsed,
            "time_left_sec": time_left,
            "message": job.message,
        }
