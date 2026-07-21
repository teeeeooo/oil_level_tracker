from __future__ import annotations

from datetime import datetime, timezone

from oil_benchmark_fixtures import controlled_oil_scenes, generate_controlled_oil_dataset
from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.domain.detector_benchmark import CATEGORY_CONTRACT
from oil_tracker.domain.recipe import InspectionRecipe


FIXED_TIME = datetime(2026, 7, 21, 19, 0, 0, tzinfo=timezone.utc)


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


def test_controlled_oil_dataset_is_stable_external_style_and_multi_category(tmp_path):
    dataset_path, scenes = generate_controlled_oil_dataset(tmp_path)
    reader = FilesystemRegressionDatasetReader()
    first = reader.load(dataset_path)
    second = reader.load(dataset_path)
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64
    assert len(first.cases) == len(scenes)
    assert len({case.sequence_id for case in first.cases if case.sequence_id}) >= 8
    assert sum(case.usable for case in first.cases) < len(first.cases)
    categories = {case.category.value for case in first.cases}
    assert {
        "clear_oil_boundary",
        "transparent_oil_shimmer",
        "reflection_or_blur",
        "structural_horizontal_edge",
        "rapid_oil_flow",
        "no_interface",
    } <= categories
    assert categories <= set(CATEGORY_CONTRACT)


def test_feature_detector_meets_controlled_oil_absolute_gates(tmp_path):
    dataset_path, _scenes = generate_controlled_oil_dataset(tmp_path)
    payload = _service().run(dataset_path, tmp_path / "results").payload
    assert payload["benchmark_schema_version"] == 1
    assert payload["detector"]["version"] == "opencv-phase-detector-s5b-oil-v3"

    clear = payload["category_summaries"]["clear_oil_boundary"]
    rapid = payload["category_summaries"]["rapid_oil_flow"]
    no_interface = payload["category_summaries"]["no_interface"]
    micro = payload["micro_aggregate"]

    assert _metric(clear, "raw_oil_detection_coverage") == 1.0
    assert _metric(clear, "smoothed_oil_detection_coverage") == 1.0
    assert _metric(clear, "raw_oil_median_absolute_error") <= 2.0
    assert _metric(clear, "raw_oil_p95_absolute_error") <= 4.0
    assert _metric(clear, "smoothed_oil_median_absolute_error") <= 3.0
    assert _metric(clear, "smoothed_oil_p95_absolute_error") <= 6.0
    assert _metric(rapid, "raw_oil_median_absolute_error") <= 3.0
    assert _metric(rapid, "raw_oil_p95_absolute_error") <= 6.0
    assert _metric(no_interface, "raw_no_interface_false_boundary_rate") == 0.0
    assert _metric(no_interface, "smoothed_no_interface_false_boundary_rate") == 0.0
    assert _metric(micro, "raw_oil_detection_coverage") is not None
    assert _metric(micro, "smoothed_oil_detection_coverage") is not None


def test_temporal_side_contracts_use_same_controlled_scene_generator():
    scenes = controlled_oil_scenes()
    grouped = {}
    for scene in scenes:
        if scene.sequence_id is not None:
            grouped.setdefault(scene.sequence_id, []).append(scene)

    outputs = {
        sequence_id: _run_sequence(sorted(values, key=lambda item: item.sequence_order))
        for sequence_id, values in grouped.items()
    }
    assert outputs["one-frame-dropout"][1].raw_oil_air_level_y is None
    assert outputs["one-frame-dropout"][1].smoothed_oil_air_level_y is None
    assert outputs["multi-frame-dropout"][1].raw_oil_air_level_y is None
    assert outputs["multi-frame-dropout"][2].raw_oil_air_level_y is None
    assert outputs["visible-to-no-interface"][2].raw_oil_air_level_y is None
    assert outputs["visible-to-no-interface"][3].smoothed_oil_air_level_y is None
    assert outputs["no-interface-to-visible"][3].raw_oil_air_level_y is not None
    assert outputs["large-jump-new-path"][4].raw_oil_air_level_y is not None
    assert outputs["transient-false-line"][1].raw_oil_air_level_y is None


def _run_sequence(scenes):
    detector = OpenCvPhaseDetector()
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = f"controlled-{scenes[0].sequence_id}"
    outputs = []
    for index, scene in enumerate(scenes):
        detection, _artifacts = detector.detect(
            scene.frame,
            glass,
            index,
            scene.timestamp,
            debug=False,
        )
        outputs.append(detection)
    return outputs
