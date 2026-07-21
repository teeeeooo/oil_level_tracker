from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from oil_tracker.application.ports.regression_dataset_reader import (
    RegressionDataset,
    RegressionDatasetCase,
)
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.detector_benchmark import BenchmarkCategory, BenchmarkTruth
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.user_truth import TruthDisposition


FIXED_TIME = datetime(2026, 7, 21, 13, 0, 0, tzinfo=timezone.utc)


class _Reader:
    def __init__(self, dataset=None, error=None):
        self.dataset = dataset
        self.error = error

    def load(self, _path):
        if self.error:
            raise self.error
        return self.dataset


class _Writer:
    def __init__(self, baseline=None):
        self.baseline = baseline
        self.writes = []

    def load_result(self, _path):
        return self.baseline

    def write(self, payload, output_root, *, dataset_id, timestamp_token):
        self.writes.append(payload)
        return Path(output_root) / f"written-{dataset_id}-{timestamp_token}"


class _Detector:
    version = "fake-current-detector-v1"

    def __init__(self, instances, *, fail_case=None):
        self.instances = instances
        self.fail_case = fail_case
        self.calls = []
        self.reset_count = 0
        self.state = 0
        instances.append(self)

    def reset(self, glass_id=None):
        assert glass_id is None
        self.reset_count += 1
        self.state = 0

    def detect(self, frame, glass, frame_index, time_sec, debug=False):
        assert debug is False
        if frame.get("case_id") == self.fail_case:
            raise RuntimeError("detector exploded")
        self.state += 1
        self.calls.append((frame["case_id"], frame_index, time_sec, glass.detector_settings.canny_low))
        y = float(frame.get("base_y", 100.0)) + self.state
        return (
            PhaseDetection(
                glass_id=glass.id,
                frame_index=frame_index,
                time_sec=time_sec,
                fill_state=FillState.PARTIAL_VISIBLE,
                oil_air_level_y=y,
                oil_air_level_px_from_zero=glass.geometry.zero_line_y - y,
                raw_oil_air_level_y=y,
                smoothed_oil_air_level_y=y,
                overall_confidence=1.0,
            ),
            None,
        )


def _glass(canny_low=45):
    recipe = InspectionRecipe.empty(320, 240, "benchmark")
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "glass-1"
    glass.geometry.zero_line_y = 150.0
    glass.detector_settings.canny_low = canny_low
    recipe.glasses = [glass]
    return glass


def _case(
    case_id,
    *,
    timestamp=1.0,
    frame_index=30,
    sequence_id=None,
    sequence_order=None,
    glass=None,
    source_y_offset=0.0,
):
    glass = glass or _glass()
    return RegressionDatasetCase(
        dataset_id="dataset-1",
        case_id=case_id,
        sequence_id=sequence_id,
        sequence_order=sequence_order,
        category=BenchmarkCategory.CLEAR_OIL_BOUNDARY,
        disposition=TruthDisposition.CORRECTED,
        unusable_reasons=(),
        timestamp_sec=timestamp,
        frame_index=frame_index,
        frame_identity=f"{frame_index}@{timestamp:.9f}",
        frame={"case_id": case_id, "base_y": 100.0},
        source_y_offset=source_y_offset,
        analysis_height_px=100.0,
        glass=glass,
        truth=BenchmarkTruth(FillState.PARTIAL_VISIBLE, 101.0 + source_y_offset, False, None),
        fixture_manifest_hash=f"manifest-{case_id}",
        frame_hash=f"frame-{case_id}",
    )


def _dataset(cases):
    return RegressionDataset(
        root=Path("dataset"),
        dataset_id="dataset-1",
        schema_version=1,
        fingerprint="dataset-fingerprint",
        source_bundle_identity={"run_id": "run"},
        annotation_set_identity={"annotation_set_id": "truth"},
        cases=tuple(cases),
        warnings=(),
        catalog_present=True,
    )


def _service(dataset, writer, instances, *, fail_case=None):
    return DetectorBenchmarkService(
        _Reader(dataset),
        writer,
        lambda: _Detector(instances, fail_case=fail_case),
        clock=lambda: FIXED_TIME,
        runtime_metadata_factory=lambda: {
            "python": "3.test",
            "packages": {"numpy": "test", "opencv-python-headless": "test"},
        },
    )


def test_independent_cases_and_sequences_get_fresh_detector_state():
    cases = [
        _case("a-2", timestamp=2.0, frame_index=60, sequence_id="a", sequence_order=1),
        _case("independent", timestamp=1.5, frame_index=45),
        _case("b-1", timestamp=1.0, frame_index=30, sequence_id="b", sequence_order=0),
        _case("a-1", timestamp=1.0, frame_index=30, sequence_id="a", sequence_order=0),
    ]
    instances = []
    writer = _Writer()
    run = _service(_dataset(cases), writer, instances).run("dataset", "output")
    assert len(instances) == 3
    assert all(instance.reset_count == 1 for instance in instances)
    assert [call[0] for call in instances[0].calls] == ["a-1", "a-2"]
    assert [call[0] for call in instances[1].calls] == ["b-1"]
    assert [call[0] for call in instances[2].calls] == ["independent"]
    results = {case["case_id"]: case for case in run.payload["cases"]}
    assert results["a-1"]["raw_oil_boundary_y"] == 101.0
    assert results["a-2"]["raw_oil_boundary_y"] == 102.0
    assert results["b-1"]["raw_oil_boundary_y"] == 101.0
    assert results["independent"]["raw_oil_boundary_y"] == 101.0


def test_sequence_uses_timestamp_order_not_input_order():
    cases = [
        _case("later", timestamp=3.0, frame_index=90, sequence_id="seq", sequence_order=0),
        _case("earlier", timestamp=1.0, frame_index=30, sequence_id="seq", sequence_order=1),
    ]
    instances = []
    _service(_dataset(cases), _Writer(), instances).run("dataset", "output")
    assert [call[0] for call in instances[0].calls] == ["earlier", "later"]


def test_recipe_detector_settings_are_reused_without_override_and_snapshotted():
    glass = _glass(canny_low=77)
    cases = [_case("settings", glass=glass)]
    instances = []
    run = _service(_dataset(cases), _Writer(), instances).run("dataset", "output")
    assert instances[0].calls[0][3] == 77
    detector = run.payload["detector"]
    case_fingerprint = detector["case_settings_fingerprints"]["settings"]
    assert detector["settings_snapshots"][case_fingerprint]["canny_low"] == 77
    assert detector["settings_fingerprint"]
    assert detector["version"] == "fake-current-detector-v1"
    assert detector["app_version"]


def test_roi_source_offset_is_restored_before_truth_evaluation():
    case = _case("roi", source_y_offset=25.0)
    instances = []
    run = _service(_dataset([case]), _Writer(), instances).run("dataset", "output")
    result = run.payload["cases"][0]
    assert result["raw_oil_boundary_y"] == 126.0
    assert result["truth_oil_boundary_y"] == 126.0
    assert result["raw_oil_absolute_error_px"] == 0.0


def test_input_order_does_not_change_case_order_or_metric_payload():
    cases = [_case("z", timestamp=2.0), _case("a", timestamp=1.0)]
    first_instances = []
    second_instances = []
    first = _service(_dataset(cases), _Writer(), first_instances).run("dataset", "output").payload
    second = _service(_dataset(reversed(cases)), _Writer(), second_instances).run("dataset", "output").payload
    assert [case["case_id"] for case in first["cases"]] == ["a", "z"]
    assert first["cases"] == second["cases"]
    assert first["category_summaries"] == second["category_summaries"]
    assert first["micro_aggregate"] == second["micro_aggregate"]
    assert first["macro_category_aggregate"] == second["macro_category_aggregate"]
    assert first["run_fingerprint"] == second["run_fingerprint"]


def test_detector_exception_propagates_without_completed_output():
    writer = _Writer()
    instances = []
    service = _service(_dataset([_case("bad")]), writer, instances, fail_case="bad")
    with pytest.raises(RuntimeError, match="detector exploded"):
        service.run("dataset", "output")
    assert writer.writes == []


def test_invalid_dataset_reader_failure_creates_no_output():
    writer = _Writer()
    service = DetectorBenchmarkService(
        _Reader(error=ValueError("invalid fixture")),
        writer,
        lambda: object(),
        clock=lambda: FIXED_TIME,
    )
    with pytest.raises(ValueError, match="invalid fixture"):
        service.run("dataset", "output")
    assert writer.writes == []


def test_repeated_run_is_deterministic_except_explicit_runtime_metadata():
    dataset = _dataset([_case("same")])
    first_instances = []
    second_instances = []
    first = _service(dataset, _Writer(), first_instances).run("dataset", "output").payload
    second = _service(dataset, _Writer(), second_instances).run("dataset", "output").payload
    assert first == second
    assert first["generated_at"] == FIXED_TIME.isoformat()
    assert first["source_revision"]
    assert first["run_fingerprint"]


def test_payload_records_counts_runtime_and_event_unavailability():
    instances = []
    run = _service(_dataset([_case("meta")]), _Writer(), instances).run("dataset", "output")
    payload = run.payload
    assert payload["benchmark_schema_version"] == 1
    assert payload["case_count"] == 1
    assert payload["usable_count"] == 1
    assert payload["unusable_count"] == 0
    assert payload["runtime"]["python"] == "3.test"
    assert payload["previous_baseline_comparison"] == {"status": "not_requested"}
    event = payload["micro_aggregate"]["metrics"]["event_timestamp_difference_sec"]
    assert event["status"] == "not_evaluated"
