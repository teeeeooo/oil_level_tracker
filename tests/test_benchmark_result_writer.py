from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from oil_tracker.adapters.storage.benchmark_result_writer import (
    AtomicBenchmarkResultWriter,
    BenchmarkResultStorageError,
)
from oil_tracker.domain.detector_benchmark import (
    BENCHMARK_SCHEMA_VERSION,
    CATEGORY_CONTRACT,
    BenchmarkCategory,
    BenchmarkComparisonError,
    BenchmarkPrediction,
    BenchmarkTruth,
    compare_benchmark_payloads,
    evaluate_case,
    summarize_by_category,
)
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition


def _payload(*, dataset_fingerprint="dataset-fp", error=5.0, boundary=True):
    truth_y = 100.0
    predicted_y = truth_y + error if boundary else None
    case = evaluate_case(
        dataset_id="dataset-id",
        case_id="case-1",
        sequence_id=None,
        sequence_order=None,
        timestamp_sec=1.0,
        frame_index=30,
        frame_identity="30@1.000000000",
        category=BenchmarkCategory.CLEAR_OIL_BOUNDARY,
        disposition=TruthDisposition.CORRECTED,
        truth=BenchmarkTruth(FillState.PARTIAL_VISIBLE, truth_y, False, None),
        prediction=BenchmarkPrediction(
            FillState.PARTIAL_VISIBLE,
            predicted_y,
            predicted_y,
            None,
            None,
            boundary,
        ),
        analysis_height_px=100.0,
        detector_version="detector-v1",
        settings_fingerprint="settings-v1",
    )
    categories, micro, macro = summarize_by_category([case])
    return {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "category_contract": list(CATEGORY_CONTRACT),
        "generated_at": datetime(2026, 7, 21, tzinfo=timezone.utc).isoformat(),
        "run_fingerprint": f"run-{error}-{boundary}",
        "dataset": {
            "dataset_id": "dataset-id",
            "schema_version": 1,
            "fingerprint": dataset_fingerprint,
        },
        "detector": {
            "version": "detector-v1",
            "app_version": "0.1.0",
            "settings_fingerprint": "settings-v1",
            "settings_snapshots": {"settings-v1": {"canny_low": 45}},
            "case_settings_fingerprints": {"case-1": "settings-v1"},
        },
        "runtime": {"python": "3.test", "packages": {}},
        "source_revision": "revision",
        "case_count": 1,
        "usable_count": 1,
        "unusable_count": 0,
        "category_count": 1,
        "cases": [case.to_dict()],
        "category_summaries": categories,
        "micro_aggregate": micro,
        "macro_category_aggregate": macro,
        "unavailable_metric_reasons": micro["unavailable_metric_reasons"],
        "warnings": [],
        "previous_baseline_comparison": {"status": "not_requested"},
    }


def test_atomic_writer_creates_json_case_category_summary_and_markdown(tmp_path):
    payload = _payload()
    writer = AtomicBenchmarkResultWriter()
    output = writer.write(
        payload,
        tmp_path / "출력",
        dataset_id="dataset-id",
        timestamp_token="20260721_010203",
    )
    assert output.is_dir()
    assert {path.name for path in output.iterdir()} == {
        "benchmark_result.json",
        "benchmark_cases.csv",
        "benchmark_categories.csv",
        "benchmark_summary.csv",
        "benchmark_comparison.md",
    }
    loaded = json.loads((output / "benchmark_result.json").read_text(encoding="utf-8"))
    assert loaded == payload
    assert writer.load_result(output / "benchmark_result.json") == payload

    with (output / "benchmark_cases.csv").open(encoding="utf-8-sig", newline="") as handle:
        cases = list(csv.DictReader(handle))
    assert cases[0]["case_id"] == "case-1"
    assert cases[0]["raw_oil_absolute_error_px"] == "5.0"
    assert cases[0]["settings_fingerprint"] == "settings-v1"

    with (output / "benchmark_categories.csv").open(encoding="utf-8-sig", newline="") as handle:
        categories = list(csv.DictReader(handle))
    assert [row["category"] for row in categories] == list(CATEGORY_CONTRACT)
    assert categories[0]["raw_oil_mae"] == "5.0"

    with (output / "benchmark_summary.csv").open(encoding="utf-8-sig", newline="") as handle:
        summary = list(csv.DictReader(handle))
    assert any(row["scope"] == "micro" and row["metric"] == "raw_oil_mae" for row in summary)
    assert "No previous comparable baseline" in (output / "benchmark_comparison.md").read_text(encoding="utf-8")
    assert not list((tmp_path / "출력").glob(".*.tmp-*"))


def test_json_and_csv_ordering_are_stable(tmp_path):
    writer = AtomicBenchmarkResultWriter()
    first = writer.write(_payload(), tmp_path / "one", dataset_id="dataset", timestamp_token="same")
    second = writer.write(_payload(), tmp_path / "two", dataset_id="dataset", timestamp_token="same")
    for name in (
        "benchmark_result.json",
        "benchmark_cases.csv",
        "benchmark_categories.csv",
        "benchmark_summary.csv",
        "benchmark_comparison.md",
    ):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_existing_output_is_protected(tmp_path):
    writer = AtomicBenchmarkResultWriter()
    writer.write(_payload(), tmp_path, dataset_id="dataset", timestamp_token="same")
    with pytest.raises(BenchmarkResultStorageError, match="cannot be overwritten"):
        writer.write(_payload(), tmp_path, dataset_id="dataset", timestamp_token="same")


def test_failure_removes_staging_and_exposes_no_completed_output(tmp_path):
    class FailingWriter(AtomicBenchmarkResultWriter):
        @staticmethod
        def _write_categories(path, categories):
            raise OSError("category CSV failed")

    with pytest.raises(OSError, match="category CSV failed"):
        FailingWriter().write(
            _payload(),
            tmp_path,
            dataset_id="dataset",
            timestamp_token="failure",
        )
    assert not list(tmp_path.glob("detector_benchmark_*"))
    assert not list(tmp_path.glob(".*.tmp-*"))


def test_matching_baseline_reports_lower_and_higher_is_better_deltas(tmp_path):
    previous = _payload(error=10.0, boundary=False)
    current = _payload(error=5.0, boundary=True)
    comparison = compare_benchmark_payloads(previous, current)
    assert comparison["status"] == "comparable"
    error_change = comparison["micro_metric_changes"]["raw_oil_mae"]
    assert error_change["direction"] == "lower_is_better"
    assert error_change["status"] == "improved"
    coverage = comparison["micro_metric_changes"]["raw_oil_detection_coverage"]
    assert coverage["direction"] == "higher_is_better"
    assert coverage["status"] == "improved"

    current["previous_baseline_comparison"] = comparison
    output = AtomicBenchmarkResultWriter().write(
        current,
        tmp_path,
        dataset_id="dataset",
        timestamp_token="comparison",
    )
    markdown = (output / "benchmark_comparison.md").read_text(encoding="utf-8")
    assert "Micro aggregate changes" in markdown
    assert "improved" in markdown


def test_dataset_and_benchmark_schema_mismatch_are_non_comparable():
    previous = _payload()
    current = _payload(dataset_fingerprint="different")
    with pytest.raises(BenchmarkComparisonError, match="dataset fingerprint mismatch"):
        compare_benchmark_payloads(previous, current)

    current = _payload()
    previous["benchmark_schema_version"] = 99
    with pytest.raises(BenchmarkComparisonError, match="benchmark schema mismatch"):
        compare_benchmark_payloads(previous, current)


def test_category_contract_mismatch_is_rejected():
    previous = _payload()
    previous["category_contract"] = list(CATEGORY_CONTRACT[:-1])
    with pytest.raises(BenchmarkComparisonError, match="category contract mismatch"):
        compare_benchmark_payloads(previous, _payload())


def test_unavailable_metric_delta_is_explicit():
    previous = _payload(boundary=False)
    current = _payload(boundary=True)
    comparison = compare_benchmark_payloads(previous, current)
    change = comparison["micro_metric_changes"]["raw_oil_mae"]
    assert change["status"] == "not_evaluated"
    assert "unavailable" in change["reason"]


def test_malformed_previous_baseline_is_rejected_without_stack_assumptions(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(BenchmarkResultStorageError, match="malformed"):
        AtomicBenchmarkResultWriter().load_result(path)
