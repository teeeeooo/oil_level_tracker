import threading
import time
from itertools import count

import pytest

from oil_tracker.adapters.http.jobs import Jobs, JobsBusy, UnknownJob
from oil_tracker.application.ports import AnalysisCancelled


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


@pytest.fixture
def jobs_and_clock():
    ids = count(1)
    clock = Clock()
    return Jobs(lambda: f"job{next(ids)}", clock), clock


def settle(jobs, job_id):
    for _ in range(500):
        status = jobs.status(job_id)
        if status["state"] != "running":
            return status
        time.sleep(0.01)
    raise AssertionError("the job did not end")


def test_a_job_runs_on_its_own_thread_and_finishes(jobs_and_clock):
    jobs, _ = jobs_and_clock
    seen = []
    started = jobs.start("i1", lambda progress, cancelled: seen.append(threading.current_thread().name))
    assert (started["id"], started["inspection_id"]) == ("job1", "i1")
    status = settle(jobs, "job1")
    assert (status["state"], status["fraction"], status["message"]) == ("finished", 1.0, None)
    assert seen == ["job-job1"]
    assert jobs.running() is None


def test_one_job_at_a_time_with_progress_and_time_left(jobs_and_clock):
    jobs, clock = jobs_and_clock
    release = threading.Event()
    reported = threading.Event()

    def work(progress, cancelled):
        progress(10, 100)
        reported.set()
        release.wait(5)

    jobs.start("i1", work)
    assert reported.wait(5)
    with pytest.raises(JobsBusy):
        jobs.start("i2", lambda progress, cancelled: None)
    clock.now += 1.0
    early = jobs.status("job1")
    assert early["fraction"] == pytest.approx(0.1) and early["time_left_sec"] is None  # too early to tell
    clock.now += 3.0
    status = jobs.running()
    assert status["id"] == "job1" and status["elapsed_sec"] == pytest.approx(4.0)
    assert status["time_left_sec"] == pytest.approx(36.0)
    release.set()
    assert settle(jobs, "job1")["time_left_sec"] is None


def test_cancelling_and_failing(jobs_and_clock):
    jobs, _ = jobs_and_clock

    def until_cancelled(progress, cancelled):
        while not cancelled():
            time.sleep(0.005)
        raise AnalysisCancelled()

    jobs.start("i1", until_cancelled)
    assert jobs.cancel("job1")["cancel_requested"] is True
    assert settle(jobs, "job1")["state"] == "cancelled"

    def broken(progress, cancelled):
        raise OSError("디스크가 가득 찼습니다")

    jobs.start("i2", broken)
    status = settle(jobs, "job2")
    assert (status["state"], status["message"]) == ("failed", "디스크가 가득 찼습니다")
    with pytest.raises(UnknownJob):
        jobs.status("nope")


def test_closing_stops_a_running_job(jobs_and_clock):
    jobs, _ = jobs_and_clock

    def until_cancelled(progress, cancelled):
        while not cancelled():
            time.sleep(0.005)
        raise AnalysisCancelled()

    jobs.start("i1", until_cancelled)
    jobs.stop_all(timeout=5)
    assert jobs.status("job1")["state"] == "cancelled"
