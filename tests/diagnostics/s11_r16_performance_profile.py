from __future__ import annotations

"""Profile an exact fingerprint-guarded analysis and bundle path."""

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

import cv2
import numpy as np

from oil_tracker.adapters.storage.jsonl_debug_trace_writer import (
    JsonlDebugTraceWriterFactory,
)
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import (
    RecipeValidationService,
)
from oil_tracker.domain.session import DebugTraceLevel
from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_evidence_probe import (
    authoritative_input_hashes,
    repository_root,
)
from tests.diagnostics.s11_replay_provenance import (
    capture_runtime_provenance,
    validate_frozen_inputs,
)
from tests.diagnostics.s11_r15_material_ownership_replay import (
    R15_NUMERIC_OIL_COUNTS,
    R15_TRACKING_FINGERPRINTS,
)


@dataclass
class _Timings:
    reader_open: list[float] = field(default_factory=list)
    reader_read: list[float] = field(default_factory=list)
    reader_close: list[float] = field(default_factory=list)
    static_learning: list[float] = field(default_factory=list)
    detect: list[float] = field(default_factory=list)
    resolve: list[float] = field(default_factory=list)


def _timed(values: list[float], operation):
    started = time.perf_counter()
    try:
        return operation()
    finally:
        values.append(time.perf_counter() - started)


class _ProfilingReader:
    def __init__(self, delegate, timings: _Timings) -> None:
        self._delegate = delegate
        self._timings = timings

    def read_at(self, timestamp_sec: float):
        return _timed(
            self._timings.reader_read,
            lambda: self._delegate.read_at(timestamp_sec),
        )

    def close(self) -> None:
        _timed(self._timings.reader_close, self._delegate.close)

    def __getattr__(self, name: str):
        return getattr(self._delegate, name)


class _ProfilingDetector:
    def __init__(self, delegate, timings: _Timings) -> None:
        self._delegate = delegate
        self._timings = timings

    def reset(self, glass_id: str | None = None) -> None:
        self._delegate.reset(glass_id)

    def learn_static_artifact(self, frames, glass) -> None:
        _timed(
            self._timings.static_learning,
            lambda: self._delegate.learn_static_artifact(frames, glass),
        )

    def detect(self, frame, glass, frame_index, time_sec, debug: bool = False):
        return _timed(
            self._timings.detect,
            lambda: self._delegate.detect(
                frame,
                glass,
                frame_index,
                time_sec,
                debug=debug,
            ),
        )

    def resolve_sequence(self, detections, glass, confirmed_initial_state=None):
        return _timed(
            self._timings.resolve,
            lambda: self._delegate.resolve_sequence(
                detections,
                glass,
                confirmed_initial_state,
            ),
        )

    def __getattr__(self, name: str):
        return getattr(self._delegate, name)


def _sum(values: list[float]) -> float:
    return float(sum(values))


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    offset = int(round((len(ordered) - 1) * fraction))
    return float(ordered[offset])


def _latency_summary(values: list[float]) -> dict[str, float | int]:
    milliseconds = [value * 1000.0 for value in values]
    return {
        "count": len(milliseconds),
        "mean_ms": statistics.fmean(milliseconds) if milliseconds else 0.0,
        "median_ms": statistics.median(milliseconds) if milliseconds else 0.0,
        "p95_ms": _percentile(milliseconds, 0.95),
        "maximum_ms": max(milliseconds, default=0.0),
    }


def _reader_factory(timings: _Timings):
    def create(path: str):
        started = time.perf_counter()
        try:
            delegate = OpenCvVideoReader(path)
        finally:
            timings.reader_open.append(time.perf_counter() - started)
        return _ProfilingReader(delegate, timings)

    return create


def _run_once(
    *,
    root: Path,
    output_root: Path,
    sample: str,
    repeat: int,
    debug_trace_level: DebugTraceLevel,
    behavior_owner: str,
    expected_numeric_oil_count: int,
    expected_tracking_fingerprint: str,
) -> dict[str, object]:
    start_sec, end_sec = replay.QUALIFICATION_WINDOWS[sample]
    video_path = root / "sample" / f"{sample}.mp4"
    repeat_root = output_root / f"run-{repeat:02d}"
    repeat_root.mkdir(parents=True, exist_ok=True)

    end_to_end_started = time.perf_counter()
    setup_started = time.perf_counter()
    recipe, session = replay._session(
        sample,
        video_path,
        repeat_root,
        start_sec,
        end_sec,
        run_label="S11-R16 PERF",
        run_note=f"{behavior_owner} fingerprint-guarded performance profile",
    )
    session.debug_trace_level = debug_trace_level
    session_setup_sec = time.perf_counter() - setup_started

    timings = _Timings()
    detector = _ProfilingDetector(OpenCvPhaseDetector(), timings)
    pipeline_started = time.perf_counter()
    result = AnalysisPipeline(
        _reader_factory(timings),
        detector,
        RecipeValidationService(),
        (
            None
            if debug_trace_level is DebugTraceLevel.NONE
            else JsonlDebugTraceWriterFactory(staging_parent=repeat_root)
        ),
    ).run(recipe, session)
    pipeline_sec = time.perf_counter() - pipeline_started

    output_started = time.perf_counter()
    bundle = OutputBundleStore().write_bundle(
        result,
        recipe,
        session,
        repeat_root,
    )
    bundle_output_sec = time.perf_counter() - output_started
    end_to_end_sec = time.perf_counter() - end_to_end_started

    summary = replay._sample_summary(sample, result, recipe, bundle)
    expected = (
        replay.ACCEPTED_ROW_COUNTS[sample],
        expected_numeric_oil_count,
        expected_tracking_fingerprint,
    )
    actual = (
        summary["tracking_row_count"],
        summary["numeric_oil_count"],
        summary["tracking_fingerprint_sha256"],
    )
    if actual != expected:
        raise AssertionError(
            f"{sample} behavior changed during performance profile: "
            f"expected {expected}, got {actual}"
        )

    measured_pipeline_sec = sum(
        (
            _sum(timings.reader_open),
            _sum(timings.reader_read),
            _sum(timings.reader_close),
            _sum(timings.static_learning),
            _sum(timings.detect),
            _sum(timings.resolve),
        )
    )
    source_duration_sec = max(
        1e-9,
        float(session.effective_end_sec() or end_sec) - float(start_sec),
    )
    return {
        "repeat": repeat,
        "sample": sample,
        "source_duration_sec": source_duration_sec,
        "session_setup_sec": session_setup_sec,
        "pipeline_sec": pipeline_sec,
        "bundle_output_sec": bundle_output_sec,
        "end_to_end_sec": end_to_end_sec,
        "realtime_factor": end_to_end_sec / source_duration_sec,
        "stage_seconds": {
            "reader_open": _sum(timings.reader_open),
            "reader_read": _sum(timings.reader_read),
            "reader_close": _sum(timings.reader_close),
            "static_learning": _sum(timings.static_learning),
            "detect": _sum(timings.detect),
            "completed_window_resolve": _sum(timings.resolve),
            "application_outcome_assembly": max(
                0.0,
                pipeline_sec - measured_pipeline_sec,
            ),
            "bundle_output": bundle_output_sec,
        },
        "detect_latency": _latency_summary(timings.detect),
        "static_learning_latency": _latency_summary(timings.static_learning),
        "resolve_latency": _latency_summary(timings.resolve),
        "reader_latency": _latency_summary(timings.reader_read),
        "tracking_row_count": summary["tracking_row_count"],
        "numeric_oil_count": summary["numeric_oil_count"],
        "tracking_fingerprint_sha256": summary["tracking_fingerprint_sha256"],
        "bundle": str(bundle),
    }


def _git_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _git_status(root: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        check=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _exact_source_head(root: Path, expected: str | None) -> str:
    head = _git_head(root)
    if expected is not None and head != expected:
        raise RuntimeError(
            f"Performance source head mismatch: expected {expected}, got {head}"
        )
    dirty = _git_status(root)
    if dirty:
        raise RuntimeError(
            "Performance evidence requires a clean exact source head; "
            f"worktree changes:\n{dirty}"
        )
    return head


def _require_runtime_match(actual: str, expected: str | None) -> None:
    if expected is not None and actual != expected:
        raise RuntimeError(
            "Performance runtime environment drift: "
            f"expected {expected}, got {actual}"
        )


def run_profile(
    *,
    root: Path,
    output_root: Path,
    sample: str = "sample4",
    repeats: int = 3,
    debug_trace_level: DebugTraceLevel = DebugTraceLevel.NONE,
    behavior_owner: str = "R15",
    expected_numeric_oil_count: int | None = None,
    expected_tracking_fingerprint: str | None = None,
    expected_source_head: str | None = None,
    expected_runtime_fingerprint: str | None = None,
) -> dict[str, object]:
    root = root.resolve()
    source_head = _exact_source_head(root, expected_source_head)
    inputs = validate_frozen_inputs(
        root=root,
        expected_inputs=authoritative_input_hashes(root),
        samples=(sample,),
    )
    runtime_provenance = capture_runtime_provenance(
        root / "sample" / f"{sample}.mp4"
    )
    actual_runtime_fingerprint = str(
        runtime_provenance["runtime_fingerprint_sha256"]
    )
    _require_runtime_match(actual_runtime_fingerprint, expected_runtime_fingerprint)
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    expected_numeric = (
        R15_NUMERIC_OIL_COUNTS[sample]
        if expected_numeric_oil_count is None
        else int(expected_numeric_oil_count)
    )
    expected_fingerprint = (
        R15_TRACKING_FINGERPRINTS[sample]
        if expected_tracking_fingerprint is None
        else str(expected_tracking_fingerprint)
    )
    runs = [
        _run_once(
            root=root,
            output_root=output_root,
            sample=sample,
            repeat=repeat,
            debug_trace_level=debug_trace_level,
            behavior_owner=behavior_owner,
            expected_numeric_oil_count=expected_numeric,
            expected_tracking_fingerprint=expected_fingerprint,
        )
        for repeat in range(1, repeats + 1)
    ]
    stage_names = tuple(runs[0]["stage_seconds"])
    all_detect_latencies = [
        float(run["detect_latency"]["mean_ms"]) for run in runs
    ]
    manifest = {
        "schema": "s11-r16-performance-profile-v1",
        "source_head": source_head,
        "source_worktree_clean": True,
        "behavior_owner": behavior_owner,
        "inputs": inputs,
        "runtime_provenance": runtime_provenance,
        "expected_runtime_fingerprint_sha256": expected_runtime_fingerprint,
        "behavior_contract": {
            "tracking_row_count": replay.ACCEPTED_ROW_COUNTS[sample],
            "numeric_oil_count": expected_numeric,
            "tracking_fingerprint_sha256": expected_fingerprint,
        },
        "sample": sample,
        "repeats": repeats,
        "normal_operational_config": {
            "sampling_fps": replay.SAMPLING_FPS,
            "debug_trace_level": debug_trace_level.value.upper(),
            "official_static_learning": "start/middle/end",
            "official_bundle_output": True,
        },
        "host": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
            "numpy": np.__version__,
        },
        "runs": runs,
        "median": {
            "end_to_end_sec": statistics.median(
                float(run["end_to_end_sec"]) for run in runs
            ),
            "realtime_factor": statistics.median(
                float(run["realtime_factor"]) for run in runs
            ),
            "detect_mean_ms_per_frame": statistics.median(all_detect_latencies),
            "stage_seconds": {
                name: statistics.median(
                    float(run["stage_seconds"][name]) for run in runs
                )
                for name in stage_names
            },
        },
        "acceptance_note": (
            "Timing is comparative evidence only. Tracking fingerprints and "
            "same-frame provenance remain correctness gates and cannot be traded "
            "for speed."
        ),
    }
    manifest_path = output_root / "performance_profile.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r16-performance-profile"),
    )
    parser.add_argument("--sample", choices=tuple(replay.QUALIFICATION_WINDOWS), default="sample4")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--behavior-owner", default="R15")
    parser.add_argument("--expected-numeric-oil-count", type=int)
    parser.add_argument("--expected-tracking-fingerprint")
    parser.add_argument(
        "--source-head",
        help="Require this exact clean Git HEAD for attributable timing evidence.",
    )
    parser.add_argument(
        "--expected-runtime-fingerprint",
        help=(
            "Require this exact replay runtime fingerprint before timing; "
            "environment drift invalidates comparative performance evidence."
        ),
    )
    parser.add_argument(
        "--debug-trace-level",
        choices=tuple(level.value for level in DebugTraceLevel),
        default=DebugTraceLevel.NONE.value,
    )
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    if (args.expected_numeric_oil_count is None) != (
        args.expected_tracking_fingerprint is None
    ):
        parser.error(
            "R16 override requires both expected numeric count and fingerprint"
        )
    manifest = run_profile(
        root=repository_root() if args.root is None else args.root,
        output_root=args.output_root,
        sample=args.sample,
        repeats=args.repeats,
        debug_trace_level=DebugTraceLevel(args.debug_trace_level),
        behavior_owner=args.behavior_owner,
        expected_numeric_oil_count=args.expected_numeric_oil_count,
        expected_tracking_fingerprint=args.expected_tracking_fingerprint,
        expected_source_head=args.source_head,
        expected_runtime_fingerprint=args.expected_runtime_fingerprint,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
