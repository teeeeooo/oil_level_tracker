from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
import os
import platform
from pathlib import Path
from typing import Any, Callable, Mapping

from oil_tracker.application.ports.benchmark_result_writer import BenchmarkResultWriter
from oil_tracker.application.ports.phase_detector import PhaseDetector
from oil_tracker.application.ports.regression_dataset_reader import (
    RegressionDataset,
    RegressionDatasetCase,
    RegressionDatasetReader,
)
from oil_tracker.application.services.detection_processing import (
    tracking_sample_from_detection,
)
from oil_tracker.domain.detector_benchmark import (
    BENCHMARK_SCHEMA_VERSION,
    CATEGORY_CONTRACT,
    BenchmarkPrediction,
    compare_benchmark_payloads,
    evaluate_case,
    fingerprint_json,
    summarize_by_category,
)


@dataclass(frozen=True)
class DetectorBenchmarkRun:
    output_path: Path
    payload: Mapping[str, Any]


class DetectorBenchmarkService:
    def __init__(
        self,
        dataset_reader: RegressionDatasetReader,
        result_writer: BenchmarkResultWriter,
        detector_factory: Callable[[], PhaseDetector],
        *,
        clock: Callable[[], datetime] | None = None,
        runtime_metadata_factory: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.dataset_reader = dataset_reader
        self.result_writer = result_writer
        self.detector_factory = detector_factory
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.runtime_metadata_factory = runtime_metadata_factory or default_runtime_metadata

    def run(
        self,
        dataset_path: str | Path,
        output_root: str | Path,
        *,
        baseline_path: str | Path | None = None,
    ) -> DetectorBenchmarkRun:
        dataset = self.dataset_reader.load(dataset_path)
        if not dataset.cases:
            raise ValueError("benchmark dataset contains no fixtures")
        settings_snapshots: dict[str, dict[str, Any]] = {}
        settings_assignments: dict[str, str] = {}
        evaluations = []
        detector_versions: set[str] = set()

        for group in _case_groups(dataset):
            detector = self.detector_factory()
            detector.reset()
            detector_version = str(detector.version)
            detector_versions.add(detector_version)
            for case in group:
                settings = asdict(case.glass.detector_settings)
                settings_fingerprint = fingerprint_json(settings)
                settings_snapshots.setdefault(settings_fingerprint, settings)
                settings_assignments[case.case_id] = settings_fingerprint
                detection, _artifacts = detector.detect(
                    case.frame,
                    case.glass,
                    case.frame_index,
                    case.timestamp_sec,
                    debug=False,
                )
                sample = tracking_sample_from_detection(
                    f"benchmark:{dataset.dataset_id}", case.glass, detection
                )
                offset = case.source_y_offset
                prediction = BenchmarkPrediction(
                    fill_state=detection.fill_state,
                    raw_oil_boundary_y=_with_offset(
                        detection.raw_oil_air_level_y, offset
                    ),
                    smoothed_oil_boundary_y=_with_offset(
                        detection.smoothed_oil_air_level_y, offset
                    ),
                    raw_foam_front_y=_with_offset(
                        detection.raw_foam_front_y, offset
                    ),
                    smoothed_foam_front_y=_with_offset(
                        detection.smoothed_foam_front_y, offset
                    ),
                    is_valid=sample.is_valid,
                    flags=tuple(detection.flags),
                )
                evaluations.append(
                    evaluate_case(
                        dataset_id=dataset.dataset_id,
                        case_id=case.case_id,
                        sequence_id=case.sequence_id,
                        sequence_order=case.sequence_order,
                        timestamp_sec=case.timestamp_sec,
                        frame_index=case.frame_index,
                        frame_identity=case.frame_identity,
                        category=case.category,
                        disposition=case.disposition,
                        truth=case.truth,
                        prediction=prediction,
                        analysis_height_px=case.analysis_height_px,
                        detector_version=detector_version,
                        settings_fingerprint=settings_fingerprint,
                        unusable_reasons=case.unusable_reasons,
                    )
                )
                _artifacts = None

        if len(detector_versions) != 1:
            raise RuntimeError(
                "detector factory returned inconsistent detector versions: "
                + ", ".join(sorted(detector_versions))
            )
        detector_version = next(iter(detector_versions))
        evaluations = sorted(evaluations, key=_evaluation_sort_key)
        category_summaries, micro, macro = summarize_by_category(evaluations)
        runtime = dict(self.runtime_metadata_factory())
        app_version = _package_version("rotary-oil-level-tracker", "0.1.0")
        source_revision = (
            os.environ.get("OIL_TRACKER_SOURCE_REVISION")
            or os.environ.get("GITHUB_SHA")
            or "unavailable"
        )
        settings_fingerprint = fingerprint_json(
            {
                "snapshots": {
                    key: settings_snapshots[key] for key in sorted(settings_snapshots)
                },
                "case_assignments": {
                    key: settings_assignments[key] for key in sorted(settings_assignments)
                },
            }
        )
        generated_at = self.clock().astimezone(timezone.utc)
        run_fingerprint = fingerprint_json(
            {
                "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
                "dataset_fingerprint": dataset.fingerprint,
                "app_version": app_version,
                "detector_version": detector_version,
                "settings_fingerprint": settings_fingerprint,
                "source_revision": source_revision,
                "runtime": runtime,
            }
        )
        payload: dict[str, Any] = {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "category_contract": list(CATEGORY_CONTRACT),
            "generated_at": generated_at.isoformat(),
            "run_fingerprint": run_fingerprint,
            "dataset": {
                "dataset_id": dataset.dataset_id,
                "schema_version": dataset.schema_version,
                "fingerprint": dataset.fingerprint,
                "source_bundle_identity": dataset.source_bundle_identity,
                "annotation_set_identity": dataset.annotation_set_identity,
                "catalog_present": dataset.catalog_present,
            },
            "detector": {
                "version": detector_version,
                "app_version": app_version,
                "settings_fingerprint": settings_fingerprint,
                "settings_snapshots": {
                    key: settings_snapshots[key] for key in sorted(settings_snapshots)
                },
                "case_settings_fingerprints": {
                    key: settings_assignments[key] for key in sorted(settings_assignments)
                },
            },
            "runtime": runtime,
            "source_revision": source_revision,
            "case_count": len(evaluations),
            "usable_count": micro["usable_count"],
            "unusable_count": micro["unusable_count"],
            "category_count": sum(
                summary["case_count"] > 0 for summary in category_summaries.values()
            ),
            "cases": [case.to_dict() for case in evaluations],
            "category_summaries": category_summaries,
            "micro_aggregate": micro,
            "macro_category_aggregate": macro,
            "unavailable_metric_reasons": micro["unavailable_metric_reasons"],
            "warnings": list(dataset.warnings),
            "previous_baseline_comparison": {"status": "not_requested"},
        }
        if baseline_path is not None:
            previous = self.result_writer.load_result(baseline_path)
            payload["previous_baseline_comparison"] = compare_benchmark_payloads(
                previous, payload
            )
        timestamp_token = generated_at.strftime("%Y%m%d_%H%M%S_%f")
        output = self.result_writer.write(
            payload,
            output_root,
            dataset_id=dataset.dataset_id,
            timestamp_token=timestamp_token,
        )
        return DetectorBenchmarkRun(output, payload)


def default_runtime_metadata() -> Mapping[str, Any]:
    return {
        "python": platform.python_version(),
        "packages": {
            "PySide6": _package_version("PySide6"),
            "numpy": _package_version("numpy"),
            "opencv-python-headless": _package_version("opencv-python-headless"),
            "matplotlib": _package_version("matplotlib"),
        },
    }


def _package_version(name: str, fallback: str = "unavailable") -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return fallback


def _case_groups(dataset: RegressionDataset) -> tuple[tuple[RegressionDatasetCase, ...], ...]:
    sequences: dict[str, list[RegressionDatasetCase]] = {}
    independent: list[RegressionDatasetCase] = []
    for case in dataset.cases:
        if case.sequence_id is None:
            independent.append(case)
        else:
            sequences.setdefault(case.sequence_id, []).append(case)
    groups = [
        tuple(sorted(values, key=_case_timestamp_sort_key))
        for _sequence_id, values in sorted(sequences.items())
    ]
    groups.extend((case,) for case in sorted(independent, key=_case_timestamp_sort_key))
    return tuple(groups)


def _case_timestamp_sort_key(case: RegressionDatasetCase) -> tuple[Any, ...]:
    return (
        case.timestamp_sec,
        case.frame_index,
        case.sequence_order if case.sequence_order is not None else 0,
        case.case_id,
    )


def _evaluation_sort_key(case) -> tuple[Any, ...]:
    return (
        case.sequence_id or f"~{case.case_id}",
        case.timestamp_sec,
        case.frame_index,
        case.sequence_order if case.sequence_order is not None else 0,
        case.case_id,
    )


def _with_offset(value: float | None, offset: float) -> float | None:
    return None if value is None else float(value) + float(offset)
