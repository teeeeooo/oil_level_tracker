from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from statistics import median

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import timestamp_schedule
from oil_tracker.application.services.detection_processing import learn_static_artifacts
from oil_tracker.domain.enums import FillState
from tests.diagnostics.s11_evidence_probe import (
    CORPUS_STEMS,
    ProbeCase,
    decode_frame,
    file_sha256,
    load_cases,
    repository_root,
)

ESTIMATOR_DESIGN_BASE_SHA = "4bb52a2718d176874c59a97b9164453165a90c00"
PRODUCTION_STREAM_BASELINE_SHA = "f8742d0789fc4bcab93224f8866731209031f2f9"
SAMPLING_FPS = 2.0
MAXIMUM_SUPPORT_INTERVALS = 2.0
# These are corpus execution windows only; the estimator never branches by sample identity.
# Each bounded window follows the checked-in Recipe qualification description.
QUALIFICATION_WINDOWS: dict[str, tuple[float, float | None]] = {
    "base_sample_1": (0.0, None),
    "sample2": (0.0, 2.0),
    "sample3": (30.03, 105.0),
    "sample4": (0.0, 56.0),
}
CENSORED_NO_INTERFACE = {
    FillState.FULL_NO_INTERFACE.value,
    FillState.EMPTY_NO_INTERFACE.value,
}
BLOCKING_FLAGS = {"DETECTION_LOST", "FOGGED_OR_GLARE"}


@dataclass(frozen=True)
class TrajectoryObservation:
    target_sec: float
    actual_sec: float
    frame_index: int
    raw_oil_y: float | None
    smoothed_oil_y: float | None
    fill_state: str
    flags: tuple[str, ...]


@dataclass(frozen=True)
class TruthBaseline:
    case_id: str
    sample: str
    frame_index: int
    time_sec: float
    truth_oil_y: float
    normally_observed: bool
    production_oil_y: float | None
    production_error_px: float | None
    fill_state: str
    flags: tuple[str, ...]


@dataclass(frozen=True)
class TrajectoryEstimate:
    case_id: str
    sample: str
    provenance: str
    oil_y: float | None
    truth_oil_y: float
    error_px: float | None
    reason: str
    left_anchor_sec: float | None = None
    left_anchor_y: float | None = None
    right_anchor_sec: float | None = None
    right_anchor_y: float | None = None
    support_span_sec: float | None = None


def _truth_baseline(case: ProbeCase) -> TruthBaseline:
    detector = OpenCvPhaseDetector()
    detection, _artifacts = detector.detect(
        decode_frame(case),
        case.glass,
        case.frame_index,
        case.time_sec,
        debug=False,
    )
    oil_y = detection.raw_oil_air_level_y
    return TruthBaseline(
        case_id=case.case_id,
        sample=case.sample,
        frame_index=case.frame_index,
        time_sec=case.time_sec,
        truth_oil_y=case.truth_oil_y,
        normally_observed=oil_y is not None,
        production_oil_y=None if oil_y is None else float(oil_y),
        production_error_px=None if oil_y is None else abs(float(oil_y) - case.truth_oil_y),
        fill_state=detection.fill_state.value,
        flags=tuple(detection.flags),
    )


def _production_stream(root: Path, sample: str) -> tuple[TrajectoryObservation, ...]:
    recipe = JsonRecipeRepository().load(root / "sample" / f"{sample}.oilrecipe")
    glass = recipe.glasses[0]
    reader = OpenCvVideoReader(root / "sample" / f"{sample}.mp4")
    start, requested_end = QUALIFICATION_WINDOWS[sample]
    end = reader.metadata.duration_sec if requested_end is None else min(requested_end, reader.metadata.duration_sec)
    schedule = timestamp_schedule(start, end, SAMPLING_FPS)
    detector = OpenCvPhaseDetector()
    detector.reset()
    learn_static_artifacts(reader, detector, [glass], schedule)
    rows: list[TrajectoryObservation] = []
    try:
        for target in schedule:
            frame, frame_index, actual_sec = reader.read_at(target)
            detection, _artifacts = detector.detect(
                frame,
                glass,
                frame_index,
                actual_sec,
                debug=False,
            )
            rows.append(
                TrajectoryObservation(
                    target_sec=float(target),
                    actual_sec=float(actual_sec),
                    frame_index=int(frame_index),
                    raw_oil_y=(None if detection.raw_oil_air_level_y is None else float(detection.raw_oil_air_level_y)),
                    smoothed_oil_y=(None if detection.smoothed_oil_air_level_y is None else float(detection.smoothed_oil_air_level_y)),
                    fill_state=detection.fill_state.value,
                    flags=tuple(detection.flags),
                )
            )
    finally:
        reader.close()
    return tuple(rows)


def estimate_held_out(
    baseline: TruthBaseline,
    stream: tuple[TrajectoryObservation, ...],
    *,
    temporal_max_jump_px: float,
) -> TrajectoryEstimate:
    def unavailable(reason: str, left=None, right=None) -> TrajectoryEstimate:
        return TrajectoryEstimate(
            baseline.case_id,
            baseline.sample,
            "unavailable",
            None,
            baseline.truth_oil_y,
            None,
            reason,
            None if left is None else left.actual_sec,
            None if left is None else left.raw_oil_y,
            None if right is None else right.actual_sec,
            None if right is None else right.raw_oil_y,
            None if left is None or right is None else right.actual_sec - left.actual_sec,
        )

    if baseline.fill_state in CENSORED_NO_INTERFACE:
        return unavailable("censored_no_interface_at_target")
    if BLOCKING_FLAGS.intersection(baseline.flags):
        return unavailable("occlusion_or_detection_loss_at_target")
    candidates = tuple(row for row in stream if row.frame_index != baseline.frame_index)
    left = next((row for row in reversed(candidates) if row.actual_sec < baseline.time_sec and row.raw_oil_y is not None), None)
    right = next((row for row in candidates if row.actual_sec > baseline.time_sec and row.raw_oil_y is not None), None)
    if left is None or right is None:
        return unavailable("missing_bracketing_observed_anchor", left, right)
    interior = tuple(row for row in stream if left.actual_sec < row.actual_sec < right.actual_sec and row.frame_index != baseline.frame_index)
    if any(row.fill_state in CENSORED_NO_INTERFACE for row in interior):
        return unavailable("censored_no_interface_inside_support", left, right)
    if any(BLOCKING_FLAGS.intersection(row.flags) for row in interior):
        return unavailable("occlusion_or_detection_loss_inside_support", left, right)
    support_span = right.actual_sec - left.actual_sec
    maximum_span = MAXIMUM_SUPPORT_INTERVALS / SAMPLING_FPS
    if support_span > maximum_span + 1e-6:
        return unavailable("unsupported_long_gap", left, right)
    assert left.raw_oil_y is not None and right.raw_oil_y is not None
    if abs(right.raw_oil_y - left.raw_oil_y) > float(temporal_max_jump_px):
        return unavailable("contradictory_anchor_jump", left, right)
    fraction = (baseline.time_sec - left.actual_sec) / support_span
    estimate = left.raw_oil_y + fraction * (right.raw_oil_y - left.raw_oil_y)
    return TrajectoryEstimate(
        baseline.case_id,
        baseline.sample,
        "estimated",
        float(estimate),
        baseline.truth_oil_y,
        abs(float(estimate) - baseline.truth_oil_y),
        "bounded_linear_bracketing",
        left.actual_sec,
        left.raw_oil_y,
        right.actual_sec,
        right.raw_oil_y,
        support_span,
    )


def _stream_summary(rows: tuple[TrajectoryObservation, ...]) -> dict[str, object]:
    numeric = sum(row.raw_oil_y is not None for row in rows)
    missing_runs: list[int] = []
    run = 0
    for row in rows:
        if row.raw_oil_y is None:
            run += 1
        elif run:
            missing_runs.append(run)
            run = 0
    if run:
        missing_runs.append(run)
    return {
        "sample_count": len(rows),
        "observed_numeric_count": numeric,
        "unavailable_count": len(rows) - numeric,
        "observed_numeric_ratio": numeric / len(rows) if rows else 0.0,
        "no_interface_count": sum(row.fill_state in CENSORED_NO_INTERFACE for row in rows),
        "blocking_flag_count": sum(bool(BLOCKING_FLAGS.intersection(row.flags)) for row in rows),
        "maximum_consecutive_missing_samples": max(missing_runs, default=0),
    }


def run_probe(root: Path | None = None) -> tuple[dict[str, tuple[TrajectoryObservation, ...]], tuple[TruthBaseline, ...], tuple[TrajectoryEstimate, ...]]:
    root = repository_root() if root is None else Path(root)
    cases = load_cases(root)
    baselines = tuple(_truth_baseline(case) for case in cases)
    streams = {sample: _production_stream(root, sample) for sample in CORPUS_STEMS}
    settings = {
        sample: JsonRecipeRepository().load(root / "sample" / f"{sample}.oilrecipe").glasses[0].detector_settings
        for sample in CORPUS_STEMS
    }
    estimates = tuple(
        estimate_held_out(
            baseline,
            streams[baseline.sample],
            temporal_max_jump_px=float(settings[baseline.sample].temporal_max_jump_px),
        )
        for baseline in baselines
    )
    return streams, baselines, estimates


def _aggregate_truth(baselines: tuple[TruthBaseline, ...]) -> dict[str, object]:
    observed = tuple(row for row in baselines if row.normally_observed)
    errors = tuple(row.production_error_px for row in observed if row.production_error_px is not None)
    return {
        "usable_truth_count": len(baselines),
        "normally_observed_count": len(observed),
        "normally_missing_count": len(baselines) - len(observed),
        "observed_oil_mae_px": None if not errors else sum(errors) / len(errors),
        "observed_oil_median_error_px": None if not errors else median(errors),
        "observed_oil_worst_error_px": None if not errors else max(errors),
    }


def _aggregate_estimates(estimates: tuple[TrajectoryEstimate, ...]) -> dict[str, object]:
    estimated = tuple(row for row in estimates if row.provenance == "estimated")
    errors = tuple(row.error_px for row in estimated if row.error_px is not None)
    total = len(estimates)
    return {
        "held_out_estimated_count": len(estimated),
        "unavailable_count": total - len(estimated),
        "recoverable_coverage": len(estimated) / total if total else 0.0,
        "abstention_rate": (total - len(estimated)) / total if total else 0.0,
        "estimated_mae_px": None if not errors else sum(errors) / len(errors),
        "estimated_median_error_px": None if not errors else median(errors),
        "estimated_worst_error_px": None if not errors else max(errors),
        "estimated_worst_case_id": None if not errors else max(
            estimated,
            key=lambda row: -1.0 if row.error_px is None else row.error_px,
        ).case_id,
    }


def build_manifest(
    streams: dict[str, tuple[TrajectoryObservation, ...]],
    baselines: tuple[TruthBaseline, ...],
    estimates: tuple[TrajectoryEstimate, ...],
    root: Path | None = None,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    baseline_by_id = {row.case_id: row for row in baselines}
    anchor_rows = []
    for estimate in sorted(estimates, key=lambda row: row.case_id):
        baseline = baseline_by_id[estimate.case_id]
        item = asdict(estimate)
        item["production_provenance"] = "observed" if baseline.normally_observed else "unavailable"
        item["production_oil_y"] = baseline.production_oil_y
        item["production_error_px"] = baseline.production_error_px
        item["production_fill_state"] = baseline.fill_state
        item["production_flags"] = list(baseline.flags)
        anchor_rows.append(item)
    stream_by_sample = {sample: _stream_summary(rows) for sample, rows in streams.items()}
    stream_total = {
        "sample_count": sum(int(row["sample_count"]) for row in stream_by_sample.values()),
        "observed_numeric_count": sum(int(row["observed_numeric_count"]) for row in stream_by_sample.values()),
        "unavailable_count": sum(int(row["unavailable_count"]) for row in stream_by_sample.values()),
        "no_interface_count": sum(int(row["no_interface_count"]) for row in stream_by_sample.values()),
        "blocking_flag_count": sum(int(row["blocking_flag_count"]) for row in stream_by_sample.values()),
    }
    normally_missing_ids = {row.case_id for row in baselines if not row.normally_observed}
    recovered_missing = [row.case_id for row in estimates if row.provenance == "estimated" and row.case_id in normally_missing_ids]
    per_video = {}
    for sample in CORPUS_STEMS:
        selected = tuple(row for row in estimates if row.sample == sample)
        per_video[sample] = {
            **stream_by_sample[sample],
            "usable_truth_count": len(selected),
            "held_out_estimated_count": sum(row.provenance == "estimated" for row in selected),
            "unavailable_truth_count": sum(row.provenance == "unavailable" for row in selected),
        }
    inputs = {
        sample: {
            suffix: file_sha256(root / "sample" / f"{sample}.{suffix}")
            for suffix in ("mp4", "oilrecipe", "oiltruth")
        }
        for sample in CORPUS_STEMS
    }
    payload: dict[str, object] = {
        "schema": "s11-offline-temporal-trajectory-probe-v2",
        "estimator_design_base_sha": ESTIMATOR_DESIGN_BASE_SHA,
        "production_stream_baseline_sha": PRODUCTION_STREAM_BASELINE_SHA,
        "inputs": inputs,
        "estimator": {
            "method": "single-slot-bounded-linear-bracketing",
            "input": "production raw accepted Oil observations only",
            "sampling_fps": SAMPLING_FPS,
            "maximum_support_intervals": MAXIMUM_SUPPORT_INTERVALS,
            "maximum_support_span_sec": MAXIMUM_SUPPORT_INTERVALS / SAMPLING_FPS,
            "no_interface_semantics": "censored; never numeric",
            "feedback_to_detector_or_tracker": False,
        },
        "resource_bounds": {
            "bracketing_anchor_count": 2,
            "retained_estimator_temporal_state": 0,
            "retained_images": 0,
            "estimator_feedback_calls": 0,
        },
        "production_truth_anchor_baseline": _aggregate_truth(baselines),
        "production_stream_baseline": {"total": stream_total, "per_video": per_video},
        "held_out_reconstruction": {
            **_aggregate_estimates(estimates),
            "normally_missing_recovered_case_ids": recovered_missing,
        },
        "anchors": anchor_rows,
    }
    payload["conclusion"] = (
        "useful_bounded_trajectory"
        if recovered_missing
        else "insufficient_trajectory_evidence"
    )
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    payload["result_fingerprint_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the S11 offline temporal trajectory probe.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    streams, baselines, estimates = run_probe()
    manifest = build_manifest(streams, baselines, estimates)
    encoded = json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
