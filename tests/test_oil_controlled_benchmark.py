from __future__ import annotations

from datetime import datetime, timezone

import cv2
import numpy as np

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


def _shift_vertical(frame: np.ndarray, delta: int) -> np.ndarray:
    shifted = np.roll(frame, delta, axis=0)
    if delta > 0:
        shifted[:delta] = frame[0]
    elif delta < 0:
        shifted[delta:] = frame[-1]
    return shifted


def _preserve_saturated_pixels(
    source: np.ndarray,
    adjusted: np.ndarray,
) -> np.ndarray:
    return np.where(source >= 245, source, adjusted).astype(np.uint8)


def _adjust_brightness(frame: np.ndarray, delta: int) -> np.ndarray:
    adjusted = np.clip(frame.astype(np.int16) + delta, 0, 255).astype(np.uint8)
    return _preserve_saturated_pixels(frame, adjusted)


def _adjust_contrast(frame: np.ndarray, factor: float) -> np.ndarray:
    adjusted = (frame.astype(np.float32) - 127.5) * factor + 127.5
    clipped = np.clip(adjusted, 0, 255).astype(np.uint8)
    return _preserve_saturated_pixels(frame, clipped)


def _add_deterministic_noise(
    frame: np.ndarray,
    seed: int,
    sigma: float = 1.5,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noisy = frame.astype(np.float32) + rng.normal(0.0, sigma, frame.shape)
    clipped = np.clip(noisy, 0, 255).astype(np.uint8)
    return _preserve_saturated_pixels(frame, clipped)


def _local_neighborhood(frame: np.ndarray):
    for delta in (-2, -1, 0, 1, 2):
        yield f"geometry-{delta:+d}", _shift_vertical(frame, delta), float(delta)
    for delta in (-8, -4, 0, 4, 8):
        yield f"brightness-{delta:+d}", _adjust_brightness(frame, delta), 0.0
    for factor in (0.90, 0.92, 1.0, 1.08, 1.10):
        yield f"contrast-{factor:.2f}", _adjust_contrast(frame, factor), 0.0
    for seed in (7, 19, 43):
        yield f"noise-{seed}", _add_deterministic_noise(frame, seed), 0.0


def _fresh_detection(
    frame: np.ndarray,
    case_id: str,
    *,
    debug: bool,
    static_frames: tuple[np.ndarray, ...] = (),
):
    detector = OpenCvPhaseDetector()
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = f"dominance-robustness-{case_id}"
    if static_frames:
        detector.learn_static_artifact([item.copy() for item in static_frames], glass)
    detection, _artifacts = detector.detect(frame, glass, 0, 1.0, debug=debug)
    return detection


def _assert_fresh_detector_determinism(
    frame: np.ndarray,
    case_id: str,
    *,
    static_frames: tuple[np.ndarray, ...] = (),
):
    first = _fresh_detection(
        frame,
        case_id,
        debug=False,
        static_frames=static_frames,
    )
    repeat = _fresh_detection(
        frame,
        case_id,
        debug=False,
        static_frames=static_frames,
    )
    debug = _fresh_detection(
        frame,
        case_id,
        debug=True,
        static_frames=static_frames,
    )
    assert first == repeat
    assert first == debug
    return first


def test_controlled_oil_dataset_is_stable_external_style_and_multi_category(tmp_path):
    dataset_path, scenes = generate_controlled_oil_dataset(tmp_path)
    reader = FilesystemRegressionDatasetReader()
    first = reader.load(dataset_path)
    second = reader.load(dataset_path)
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64
    assert len(first.cases) == len(scenes)
    assert len({case.sequence_id for case in first.cases if case.sequence_id}) >= 8
    assert any(not scene.usable_truth for scene in scenes)
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
    assert payload["detector"]["version"] == "opencv-phase-detector-s5b-typed-production-v1"

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
    assert _metric(rapid, "raw_oil_detection_coverage") >= 0.8695652174
    assert _metric(rapid, "smoothed_oil_detection_coverage") >= 0.8695652174
    assert _metric(rapid, "raw_oil_median_absolute_error") <= 3.0
    assert _metric(rapid, "raw_oil_p95_absolute_error") <= 6.0
    assert _metric(rapid, "smoothed_oil_median_absolute_error") <= 3.0
    assert _metric(rapid, "smoothed_oil_p95_absolute_error") <= 6.0
    assert _metric(no_interface, "raw_no_interface_false_boundary_rate") == 0.0
    assert _metric(no_interface, "smoothed_no_interface_false_boundary_rate") == 0.0
    assert _metric(micro, "raw_oil_detection_coverage") is not None
    assert _metric(micro, "smoothed_oil_detection_coverage") is not None


def test_direct_single_candidate_semantic_recall_targets_are_numeric():
    target_ids = {
        "clear-upper",
        "opposite-polarity",
        "structural-plus-real",
        "rapid-filling-0",
        "large-jump-new-path-0",
        "slow-motion-1",
        "slow-motion-3",
        "polarity-change-1",
        "polarity-change-2",
    }
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    assert target_ids <= scenes.keys()
    for case_id in sorted(target_ids):
        scene = scenes[case_id]
        detector = OpenCvPhaseDetector()
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"semantic-recall-{case_id}"
        detection, _artifacts = detector.detect(
            scene.frame,
            glass,
            0,
            scene.timestamp,
            debug=False,
        )
        assert detection.raw_oil_air_level_y is not None, case_id


def test_clear_and_rapid_local_neighborhoods_are_numeric_and_deterministic():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    for case_id in ("clear-upper", "rapid-filling-0"):
        scene = scenes[case_id]
        assert scene.oil_y is not None
        for probe_name, frame, truth_offset in _local_neighborhood(scene.frame):
            detection = _assert_fresh_detector_determinism(
                frame,
                f"positive-{case_id}-{probe_name}",
            )
            assert "OIL_PIPELINE_FAILURE" not in detection.flags
            assert detection.raw_oil_air_level_y is not None
            assert detection.fill_state.value != "UNKNOWN_REVIEW"
            expected_y = scene.oil_y + truth_offset
            assert abs(detection.raw_oil_air_level_y - expected_y) <= 4.0


def test_negative_local_neighborhoods_do_not_create_head_only_oil():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    thin_line = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.line(thin_line, (0, 120), (319, 120), (235, 235, 235), 1)
    paired_pulse = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.rectangle(paired_pulse, (0, 113), (319, 116), (235, 235, 235), -1)
    cv2.rectangle(paired_pulse, (0, 123), (319, 126), (45, 45, 45), -1)
    static_frames = tuple(thin_line.copy() for _ in range(4))
    controls = (
        ("thin-structural-line", thin_line, ()),
        ("paired-pulse", paired_pulse, ()),
        ("rim-adjacent-line", scenes["rim-line"].frame, ()),
        ("reflection-only", scenes["reflection-only"].frame, ()),
        ("glare-overlap", scenes["glare-recovery-1"].frame, ()),
        ("shimmer-only", scenes["shimmer-only"].frame, ()),
        ("static-overlap", thin_line, static_frames),
        ("uniform-full", scenes["full-no-interface"].frame, ()),
        ("uniform-empty", scenes["empty-no-interface"].frame, ()),
        ("transient-false-line", scenes["transient-false-line-1"].frame, ()),
    )

    for control_name, base_frame, learned_static in controls:
        for probe_name, frame, _truth_offset in _local_neighborhood(base_frame):
            detection = _assert_fresh_detector_determinism(
                frame,
                f"negative-{control_name}-{probe_name}",
                static_frames=learned_static,
            )
            assert detection.raw_oil_air_level_y is None
            if control_name != "glare-overlap":
                assert "OIL_PIPELINE_FAILURE" not in detection.flags
            if control_name == "uniform-full":
                assert detection.fill_state.value == "FULL_NO_INTERFACE"
            elif control_name == "uniform-empty":
                assert detection.fill_state.value == "EMPTY_NO_INTERFACE"

    structural_real = _assert_fresh_detector_determinism(
        scenes["structural-plus-real"].frame,
        "structural-plus-real-positive-control",
    )
    structural_only = _assert_fresh_detector_determinism(
        thin_line,
        "structural-only-negative-control",
    )
    assert structural_real.raw_oil_air_level_y is not None
    assert structural_only.raw_oil_air_level_y is None


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
    assert outputs["glare-recovery"][1].raw_oil_air_level_y is None
    assert outputs["glare-recovery"][2].raw_oil_air_level_y is None
    assert outputs["glare-recovery"][3].raw_oil_air_level_y is not None


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
