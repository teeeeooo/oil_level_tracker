from __future__ import annotations

from datetime import datetime, timezone
import json

from benchmark_fixtures import export_benchmark_dataset
from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService


FIXED_TIME = datetime(2026, 7, 21, 14, 0, 0, tzinfo=timezone.utc)


def _service():
    return DetectorBenchmarkService(
        FilesystemRegressionDatasetReader(),
        AtomicBenchmarkResultWriter(),
        OpenCvPhaseDetector,
        clock=lambda: FIXED_TIME,
        runtime_metadata_factory=lambda: {
            "python": "integration",
            "packages": {
                "numpy": "integration",
                "opencv-python-headless": "integration",
            },
        },
    )


def test_current_detector_runs_headlessly_on_phase2c3_fixture_dataset(tmp_path):
    dataset = export_benchmark_dataset(tmp_path, label="integration")
    run = _service().run(dataset, tmp_path / "output")
    assert run.output_path.is_dir()
    assert run.payload["case_count"] == 1
    assert run.payload["detector"]["version"] == "opencv-phase-detector-r14-phase-component-replacement-v1"
    assert run.payload["detector"]["settings_snapshots"]
    assert run.payload["cases"][0]["settings_fingerprint"]
    assert run.payload["cases"][0]["category"] == "clear_oil_boundary"
    assert run.payload["micro_aggregate"]["oil_boundary_coverage"]["raw"]
    stored = json.loads(
        (run.output_path / "benchmark_result.json").read_text(encoding="utf-8")
    )
    assert stored == run.payload


def test_current_detector_repeated_metrics_are_deterministic(tmp_path):
    dataset = export_benchmark_dataset(tmp_path, label="repeat")
    first = _service().run(dataset, tmp_path / "one").payload
    second = _service().run(dataset, tmp_path / "two").payload
    assert first["cases"] == second["cases"]
    assert first["category_summaries"] == second["category_summaries"]
    assert first["micro_aggregate"] == second["micro_aggregate"]
    assert first["macro_category_aggregate"] == second["macro_category_aggregate"]
    assert first["run_fingerprint"] == second["run_fingerprint"]
