from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
from statistics import median
from time import perf_counter


def _read(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: str | Path, payload: dict) -> None:
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def generate(root: Path) -> None:
    from foam_benchmark_fixtures import generate_controlled_foam_dataset
    from oil_benchmark_fixtures import generate_controlled_oil_dataset
    from oil_tracker.adapters.storage.regression_dataset_reader import (
        FilesystemRegressionDatasetReader,
    )

    root.mkdir(parents=True, exist_ok=True)
    oil_path, _ = generate_controlled_oil_dataset(root / "oil")
    foam_path, _ = generate_controlled_foam_dataset(root / "foam")
    reader = FilesystemRegressionDatasetReader()
    oil = reader.load(oil_path)
    foam = reader.load(foam_path)
    payload = {
        "oil_path": str(oil_path),
        "foam_path": str(foam_path),
        "oil_fingerprint": oil.fingerprint,
        "foam_fingerprint": foam.fingerprint,
        "oil_case_count": len(oil.cases),
        "oil_sequence_count": len(
            {case.sequence_id for case in oil.cases if case.sequence_id}
        ),
        "oil_category_count": len({case.category.value for case in oil.cases}),
    }
    _write(root / "datasets.json", payload)
    print(json.dumps(payload, sort_keys=True))


def run(dataset_path: Path, destination: Path, label: str) -> None:
    from oil_tracker.adapters.storage.benchmark_result_writer import (
        AtomicBenchmarkResultWriter,
    )
    from oil_tracker.adapters.storage.regression_dataset_reader import (
        FilesystemRegressionDatasetReader,
    )
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.application.services.detector_benchmark_service import (
        DetectorBenchmarkService,
    )

    reader = FilesystemRegressionDatasetReader()
    service = DetectorBenchmarkService(
        reader,
        AtomicBenchmarkResultWriter(),
        OpenCvPhaseDetector,
        clock=lambda: datetime(2026, 7, 22, tzinfo=timezone.utc),
        runtime_metadata_factory=lambda: {
            "python": label,
            "packages": {
                "numpy": "pinned",
                "opencv-python-headless": "pinned",
            },
        },
    )
    result = service.run(dataset_path, destination.parent / f"{label}-results")
    dataset = reader.load(dataset_path)
    sequences: dict[str, list] = {}
    independent = []
    for case in dataset.cases:
        if case.sequence_id is None:
            independent.append((case,))
        else:
            sequences.setdefault(case.sequence_id, []).append(case)
    groups = [
        tuple(
            sorted(
                values,
                key=lambda item: (
                    item.sequence_order,
                    item.timestamp_sec,
                    item.case_id,
                ),
            )
        )
        for _key, values in sorted(sequences.items())
    ]
    groups.extend(independent)

    samples = []
    for iteration in range(7):
        started = perf_counter()
        count = 0
        for group in groups:
            detector = OpenCvPhaseDetector()
            detector.reset()
            for case in group:
                detector.detect(
                    case.frame,
                    case.glass,
                    case.frame_index,
                    case.timestamp_sec,
                    debug=False,
                )
                count += 1
        if iteration > 1:
            samples.append((perf_counter() - started) / max(1, count))
    output = {
        "dataset_fingerprint": dataset.fingerprint,
        "detector_version": OpenCvPhaseDetector.version,
        "cpu_median_seconds": median(samples),
        "cpu_samples_seconds": samples,
        "payload": result.payload,
    }
    _write(destination, output)
    print(
        json.dumps(
            {
                key: output[key]
                for key in (
                    "dataset_fingerprint",
                    "detector_version",
                    "cpu_median_seconds",
                )
            },
            sort_keys=True,
        )
    )


def _metric(result: dict, scope: str, name: str):
    payload = result["payload"]
    summary = (
        payload["micro_aggregate"]
        if scope == "micro"
        else payload["category_summaries"][scope]
    )
    return summary["metrics"][name]["value"]


def _temporal(result: dict) -> tuple[int, int]:
    cases = {
        (case["sequence_id"], case["sequence_order"]): case
        for case in result["payload"]["cases"]
        if case["sequence_id"] is not None
    }
    checks = (
        not cases[("transient-false-line", 1)]["raw_oil_boundary_present"],
        not cases[("one-frame-dropout", 1)]["raw_oil_boundary_present"],
        not cases[("one-frame-dropout", 1)]["smoothed_oil_boundary_present"],
        not cases[("multi-frame-dropout", 1)]["raw_oil_boundary_present"],
        not cases[("multi-frame-dropout", 2)]["raw_oil_boundary_present"],
        not cases[("visible-to-no-interface", 3)]["smoothed_oil_boundary_present"],
        cases[("no-interface-to-visible", 3)]["raw_oil_boundary_present"],
        cases[("large-jump-new-path", 4)]["raw_oil_boundary_present"],
        not cases[("glare-recovery", 1)]["raw_oil_boundary_present"],
        not cases[("glare-recovery", 2)]["raw_oil_boundary_present"],
        cases[("glare-recovery", 3)]["raw_oil_boundary_present"],
    )
    return sum(map(bool, checks)), len(checks)


def compare(root: Path, base_sha: str, feature_sha: str) -> None:
    info = _read(root / "datasets.json")
    base_oil = _read(root / "base-oil.json")
    feature_oil = _read(root / "feature-oil.json")
    base_foam = _read(root / "base-foam.json")
    feature_foam = _read(root / "feature-foam.json")

    assert (
        base_oil["dataset_fingerprint"]
        == feature_oil["dataset_fingerprint"]
        == info["oil_fingerprint"]
    )
    assert (
        base_foam["dataset_fingerprint"]
        == feature_foam["dataset_fingerprint"]
        == info["foam_fingerprint"]
    )

    error_names = (
        "raw_oil_median_absolute_error",
        "raw_oil_p90_absolute_error",
        "raw_oil_p95_absolute_error",
        "smoothed_oil_median_absolute_error",
        "smoothed_oil_p90_absolute_error",
        "smoothed_oil_p95_absolute_error",
    )
    coverage_names = (
        "raw_oil_detection_coverage",
        "smoothed_oil_detection_coverage",
    )
    base_errors = {
        name: _metric(base_oil, "micro", name) for name in error_names
    }
    feature_errors = {
        name: _metric(feature_oil, "micro", name) for name in error_names
    }
    base_coverage = {
        name: _metric(base_oil, "micro", name) for name in coverage_names
    }
    feature_coverage = {
        name: _metric(feature_oil, "micro", name) for name in coverage_names
    }
    base_no_interface = {
        "raw": _metric(
            base_oil,
            "no_interface",
            "raw_no_interface_false_boundary_rate",
        ),
        "smoothed": _metric(
            base_oil,
            "no_interface",
            "smoothed_no_interface_false_boundary_rate",
        ),
    }
    feature_no_interface = {
        "raw": _metric(
            feature_oil,
            "no_interface",
            "raw_no_interface_false_boundary_rate",
        ),
        "smoothed": _metric(
            feature_oil,
            "no_interface",
            "smoothed_no_interface_false_boundary_rate",
        ),
    }
    base_temporal = _temporal(base_oil)
    feature_temporal = _temporal(feature_oil)
    base_foam_precision = _metric(base_foam, "micro", "foam_precision")
    feature_foam_precision = _metric(feature_foam, "micro", "foam_precision")
    base_foam_recall = _metric(base_foam, "micro", "foam_recall")
    feature_foam_recall = _metric(feature_foam, "micro", "foam_recall")
    base_shimmer_fpr = _metric(
        base_foam,
        "transparent_oil_shimmer",
        "shimmer_foam_false_positive_rate",
    )
    feature_shimmer_fpr = _metric(
        feature_foam,
        "transparent_oil_shimmer",
        "shimmer_foam_false_positive_rate",
    )
    base_cpu_ms = base_oil["cpu_median_seconds"] * 1000.0
    feature_cpu_ms = feature_oil["cpu_median_seconds"] * 1000.0
    cpu_ratio = feature_cpu_ms / max(base_cpu_ms, 1e-12)

    summary = {
        "base_sha": base_sha,
        "feature_sha": feature_sha,
        "dataset_fingerprint": info["oil_fingerprint"],
        "case_count": info["oil_case_count"],
        "sequence_count": info["oil_sequence_count"],
        "category_count": info["oil_category_count"],
        "base_detector": base_oil["detector_version"],
        "feature_detector": feature_oil["detector_version"],
        "base_errors": base_errors,
        "feature_errors": feature_errors,
        "base_coverage": base_coverage,
        "feature_coverage": feature_coverage,
        "base_no_interface_fpr": base_no_interface,
        "feature_no_interface_fpr": feature_no_interface,
        "base_temporal_recovery": f"{base_temporal[0]}/{base_temporal[1]}",
        "feature_temporal_recovery": (
            f"{feature_temporal[0]}/{feature_temporal[1]}"
        ),
        "base_foam_precision": base_foam_precision,
        "feature_foam_precision": feature_foam_precision,
        "base_foam_recall": base_foam_recall,
        "feature_foam_recall": feature_foam_recall,
        "base_shimmer_fpr": base_shimmer_fpr,
        "feature_shimmer_fpr": feature_shimmer_fpr,
        "base_cpu_ms": base_cpu_ms,
        "feature_cpu_ms": feature_cpu_ms,
        "cpu_ratio": cpu_ratio,
        "dependency_diff": "none",
    }
    _write(root / "controlled-summary.json", summary)
    print(json.dumps(summary, sort_keys=True, indent=2))

    assert all(
        feature_errors[name] is not None
        and (
            base_errors[name] is None
            or feature_errors[name] <= base_errors[name] + 1e-12
        )
        for name in error_names
    )
    assert all(
        feature_coverage[name] is not None
        and (
            base_coverage[name] is None
            or feature_coverage[name] + 1e-12 >= base_coverage[name]
        )
        for name in coverage_names
    )
    assert all(
        feature_no_interface[key] is not None
        and (
            base_no_interface[key] is None
            or feature_no_interface[key] <= base_no_interface[key] + 1e-12
        )
        for key in ("raw", "smoothed")
    )
    strict = any(
        base_errors[name] is None
        or feature_errors[name] < base_errors[name] - 1e-12
        for name in error_names
    )
    strict = strict or any(
        base_coverage[name] is None
        or feature_coverage[name] > base_coverage[name] + 1e-12
        for name in coverage_names
    )
    strict = strict or any(
        base_no_interface[key] is None
        or feature_no_interface[key] < base_no_interface[key] - 1e-12
        for key in ("raw", "smoothed")
    )
    assert strict
    assert feature_no_interface == {"raw": 0.0, "smoothed": 0.0}
    assert feature_temporal[0] == feature_temporal[1]
    assert feature_temporal[0] >= base_temporal[0]
    assert feature_foam_precision >= base_foam_precision
    assert feature_foam_recall >= base_foam_recall
    assert feature_shimmer_fpr <= base_shimmer_fpr
    assert feature_foam_precision == 1.0
    assert feature_foam_recall == 1.0
    assert feature_shimmer_fpr == 0.0
    assert math.isfinite(cpu_ratio)
    assert cpu_ratio <= 1.5


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("root", type=Path)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("dataset", type=Path)
    run_parser.add_argument("destination", type=Path)
    run_parser.add_argument("label")
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("root", type=Path)
    compare_parser.add_argument("base_sha")
    compare_parser.add_argument("feature_sha")
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.root)
    elif args.command == "run":
        run(args.dataset, args.destination, args.label)
    else:
        compare(args.root, args.base_sha, args.feature_sha)


if __name__ == "__main__":
    main()
