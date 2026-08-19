from __future__ import annotations

from datetime import datetime, timezone
import json

from foam_benchmark_fixtures import S5B_SETTING_FIELDS, generate_controlled_foam_dataset
from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.domain.detector_benchmark import CATEGORY_CONTRACT


FIXED_TIME = datetime(2026, 7, 21, 16, 0, 0, tzinfo=timezone.utc)


def _service():
    return DetectorBenchmarkService(
        FilesystemRegressionDatasetReader(),
        AtomicBenchmarkResultWriter(),
        OpenCvPhaseDetector,
        clock=lambda: FIXED_TIME,
        runtime_metadata_factory=lambda: {
            "python": "controlled",
            "packages": {
                "numpy": "controlled",
                "opencv-python-headless": "controlled",
            },
        },
    )


def _metric(summary, name):
    return summary["metrics"][name]["value"]


def test_controlled_dataset_is_external_style_valid_and_fingerprint_is_stable(tmp_path):
    dataset_path, scenes = generate_controlled_foam_dataset(tmp_path)
    reader = FilesystemRegressionDatasetReader()
    first = reader.load(dataset_path)
    second = reader.load(dataset_path)
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64
    assert len(first.cases) == len(scenes)
    categories = {case.category.value for case in first.cases}
    assert {
        "white_foam",
        "transparent_oil_shimmer",
        "reflection_or_blur",
        "structural_horizontal_edge",
        "clear_oil_boundary",
        "no_interface",
    } <= categories
    assert set(categories) <= set(CATEGORY_CONTRACT)
    assert any(case.sequence_id == "transient-shimmer" for case in first.cases)
    assert any(case.sequence_id == "persistent-foam" for case in first.cases)

    recipe_paths = tuple(dataset_path.rglob("recipe_snapshot.oilrecipe"))
    assert recipe_paths
    for recipe_path in recipe_paths:
        payload = json.loads(recipe_path.read_text(encoding="utf-8"))
        for glass in payload.get("glasses", []):
            settings = glass.get("detector_settings", {})
            assert not set(S5B_SETTING_FIELDS).intersection(settings)


def test_feature_detector_meets_controlled_foam_and_shimmer_acceptance(tmp_path):
    dataset_path, _scenes = generate_controlled_foam_dataset(tmp_path)
    payload = _service().run(dataset_path, tmp_path / "results").payload
    micro = payload["micro_aggregate"]
    shimmer = payload["category_summaries"]["transparent_oil_shimmer"]
    white = payload["category_summaries"]["white_foam"]
    assert payload["benchmark_schema_version"] == 1
    assert payload["detector"]["version"] == "opencv-phase-detector-r13-phase-identity-recovery-v1"
    assert _metric(shimmer, "shimmer_foam_false_positive_rate") == 0.0
    assert _metric(micro, "foam_precision") == 1.0
    # The v1 fixture mixes three independent snapshots with one three-frame
    # sequence. R4 intentionally withholds every first strong observation, so
    # singleton frame-level recall is no longer a valid publication gate. The
    # persistent sequence must instead transition pending -> accepted -> accepted.
    assert _metric(micro, "foam_recall") == 2 / 6
    persistent = sorted(
        (
            case
            for case in payload["cases"]
            if case["sequence_id"] == "persistent-foam"
        ),
        key=lambda case: case["sequence_order"],
    )
    assert [case["raw_foam_present"] for case in persistent] == [False, True, True]
    assert "FOAM_PERSISTENCE_PENDING" in persistent[0]["flags"]
    assert all("FOAM_STRONG_EVIDENCE" in case["flags"] for case in persistent[1:])
    singletons = [
        case
        for case in payload["cases"]
        if case["category"] == "white_foam" and case["sequence_id"] is None
    ]
    assert len(singletons) == 3
    assert all("FOAM_PERSISTENCE_PENDING" in case["flags"] for case in singletons)
    assert _metric(white, "fill_state_accuracy") is not None


def test_controlled_oil_and_no_interface_cases_are_evaluable(tmp_path):
    dataset_path, _scenes = generate_controlled_foam_dataset(tmp_path)
    payload = _service().run(dataset_path, tmp_path / "results").payload
    clear = payload["category_summaries"]["clear_oil_boundary"]
    no_interface = payload["category_summaries"]["no_interface"]
    assert clear["oil_boundary_coverage"]["raw"]["truth_present_detector_present"] == 1
    assert clear["oil_boundary_coverage"]["smoothed"]["truth_present_detector_present"] == 1
    assert _metric(no_interface, "raw_no_interface_false_boundary_rate") is not None
    assert _metric(no_interface, "smoothed_no_interface_false_boundary_rate") is not None
