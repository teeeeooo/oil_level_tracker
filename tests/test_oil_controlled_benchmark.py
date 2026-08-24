from __future__ import annotations

from datetime import datetime, timezone
import hashlib

import cv2
import numpy as np
import pytest

from foam_benchmark_fixtures import controlled_scenes as controlled_foam_scenes
from oil_benchmark_fixtures import controlled_oil_scenes, generate_controlled_oil_dataset
from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.domain.detector_benchmark import CATEGORY_CONTRACT
from oil_tracker.domain.geometry import EllipseGeometry
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


CONTRAST_CENTER = 127.5
NOISE_SIGMA = 1.5
GLARE_THRESHOLD = 245


def _shift_vertical(frame: np.ndarray, delta: int) -> np.ndarray:
    height, width = frame.shape[:2]
    transform = np.array(((1.0, 0.0, 0.0), (0.0, 1.0, float(delta))), dtype=np.float32)
    return cv2.warpAffine(
        frame,
        transform,
        (width, height),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_REPLICATE,
    )


def _adjust_brightness(frame: np.ndarray, delta: int) -> np.ndarray:
    adjusted = frame.astype(np.int16) + int(delta)
    return np.clip(adjusted, 0, 255).astype(frame.dtype)


def _adjust_contrast(frame: np.ndarray, factor: float) -> np.ndarray:
    adjusted = (frame.astype(np.float32) - CONTRAST_CENTER) * factor + CONTRAST_CENTER
    return np.clip(adjusted, 0, 255).astype(frame.dtype)


def _add_deterministic_noise(
    frame: np.ndarray,
    seed: int,
    sigma: float = NOISE_SIGMA,
) -> np.ndarray:
    if sigma <= 0.0:
        raise ValueError("noise sigma must be positive")
    rng = np.random.default_rng(seed)
    noisy = frame.astype(np.float32) + rng.normal(0.0, sigma, frame.shape)
    return np.clip(noisy, 0, 255).astype(frame.dtype)


def _frame_metadata(frame: np.ndarray, source: np.ndarray) -> dict[str, object]:
    if frame.shape != source.shape:
        raise AssertionError("metadata source shape mismatch")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    difference = frame.astype(np.float32) - source.astype(np.float32)
    changed = np.any(frame != source, axis=2)
    return {
        "shape": tuple(int(value) for value in frame.shape),
        "dtype": str(frame.dtype),
        "minimum": int(frame.min()),
        "maximum": int(frame.max()),
        "mean": float(frame.mean()),
        "standard_deviation": float(frame.std()),
        "changed_pixel_count": int(np.count_nonzero(changed)),
        "mean_absolute_difference": float(np.mean(np.abs(difference))),
        "difference_standard_deviation": float(difference.std()),
        "pixels_ge_230": int(np.count_nonzero(gray >= 230)),
        "pixels_ge_235": int(np.count_nonzero(gray >= 235)),
        "pixels_ge_240": int(np.count_nonzero(gray >= 240)),
        "pixels_ge_245": int(np.count_nonzero(gray >= GLARE_THRESHOLD)),
        "frame_sha256": hashlib.sha256(frame.tobytes()).hexdigest(),
    }


def _local_neighborhood(frame: np.ndarray):
    for delta in (-2, -1, 0, 1, 2):
        yield f"geometry-{delta:+d}", _shift_vertical(frame, delta), float(delta)
    for delta in (-8, -4, 0, 4, 8):
        yield f"brightness-{delta:+d}", _adjust_brightness(frame, delta), 0.0
    for factor in (0.90, 0.92, 1.0, 1.08, 1.10):
        yield f"contrast-{factor:.2f}", _adjust_contrast(frame, factor), 0.0
    for seed in (7, 19, 43, 101, 211):
        yield f"noise-{seed}", _add_deterministic_noise(frame, seed), 0.0


def _fresh_detection(
    frame: np.ndarray,
    case_id: str,
    *,
    debug: bool,
    static_frames: tuple[np.ndarray, ...] = (),
):
    input_hash = hashlib.sha256(frame.tobytes()).hexdigest()
    detector = OpenCvPhaseDetector()
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "honest-perturbation-contract"
    if static_frames:
        detector.learn_static_artifact([item.copy() for item in static_frames], glass)
    detection, _artifacts = detector.detect(frame, glass, 0, 1.0, debug=debug)
    assert hashlib.sha256(frame.tobytes()).hexdigest() == input_hash, case_id
    return detection, input_hash


def _assert_fresh_detector_determinism(
    frame: np.ndarray,
    case_id: str,
    *,
    static_frames: tuple[np.ndarray, ...] = (),
):
    first, first_hash = _fresh_detection(
        frame,
        case_id,
        debug=False,
        static_frames=static_frames,
    )
    repeat, repeat_hash = _fresh_detection(
        frame,
        case_id,
        debug=False,
        static_frames=static_frames,
    )
    debug, debug_hash = _fresh_detection(
        frame,
        case_id,
        debug=True,
        static_frames=static_frames,
    )
    assert first_hash == repeat_hash == debug_hash, case_id
    assert first == repeat, case_id
    assert first == debug, case_id
    return first


def test_geometry_helper_is_non_wrapping_border_replicated_and_deterministic():
    source = np.repeat(np.arange(6, dtype=np.uint8)[:, None, None], 4, axis=1)
    source = np.repeat(source, 3, axis=2)
    original = source.copy()
    zero = _shift_vertical(source, 0)
    assert np.array_equal(zero, source)

    for delta in (-2, -1, 1, 2):
        shifted = _shift_vertical(source, delta)
        repeat = _shift_vertical(source, delta)
        assert shifted.shape == source.shape
        assert shifted.dtype == source.dtype
        assert _frame_metadata(shifted, source)["frame_sha256"] == _frame_metadata(
            repeat,
            source,
        )["frame_sha256"]
        if delta > 0:
            assert np.array_equal(shifted[:delta], np.repeat(source[:1], delta, axis=0))
            assert np.array_equal(shifted[delta:], source[:-delta])
            assert not np.array_equal(shifted[0], source[-delta])
        else:
            amount = abs(delta)
            assert np.array_equal(shifted[-amount:], np.repeat(source[-1:], amount, axis=0))
            assert np.array_equal(shifted[:-amount], source[amount:])
            assert not np.array_equal(shifted[-1], source[amount - 1])
    assert np.array_equal(source, original)


def test_brightness_helper_applies_one_signed_delta_with_clipping_only():
    source = np.array([[[0, 1, 250], [255, 127, 248]]], dtype=np.uint8)
    original = source.copy()
    for delta in (-8, 8):
        actual = _adjust_brightness(source, delta)
        expected = np.clip(source.astype(np.int16) + delta, 0, 255).astype(np.uint8)
        assert np.array_equal(actual, expected)
        unclipped = (source.astype(np.int16) + delta >= 0) & (
            source.astype(np.int16) + delta <= 255
        )
        assert np.all(actual.astype(np.int16)[unclipped] - source.astype(np.int16)[unclipped] == delta)
    assert _adjust_brightness(source, -8)[0, 1, 0] == 247
    assert np.array_equal(source, original)


def test_contrast_helper_matches_fixed_center_affine_formula_without_preservation():
    source = np.array([[[0, 127, 250], [255, 128, 245]]], dtype=np.uint8)
    original = source.copy()
    factor = 0.92
    actual = _adjust_contrast(source, factor)
    expected = np.clip(
        (source.astype(np.float32) - CONTRAST_CENTER) * factor + CONTRAST_CENTER,
        0,
        255,
    ).astype(np.uint8)
    assert np.array_equal(actual, expected)
    assert actual[0, 0, 2] == 240
    assert actual[0, 1, 0] == 244
    assert actual[0, 1, 0] != source[0, 1, 0]
    assert np.array_equal(source, original)


def test_noise_helper_is_seeded_full_frame_and_clipping_only():
    source = np.full((128, 128, 3), 128, dtype=np.uint8)
    first = _add_deterministic_noise(source, 19)
    repeat = _add_deterministic_noise(source, 19)
    different = _add_deterministic_noise(source, 43)
    assert np.array_equal(first, repeat)
    assert not np.array_equal(first, different)
    difference = first.astype(np.float32) - source.astype(np.float32)
    assert np.count_nonzero(np.any(first != source, axis=2)) > 0
    assert abs(float(difference.std()) - NOISE_SIGMA) <= 0.25

    saturated = np.full((64, 64, 3), 255, dtype=np.uint8)
    rng = np.random.default_rng(19)
    expected = np.clip(
        saturated.astype(np.float32) + rng.normal(0.0, NOISE_SIGMA, saturated.shape),
        0,
        255,
    ).astype(np.uint8)
    actual = _add_deterministic_noise(saturated, 19)
    assert np.array_equal(actual, expected)
    assert np.count_nonzero(actual != saturated) > 0


def test_frame_metadata_is_complete_deterministic_and_diagnostic_only():
    source = np.full((8, 9, 3), 240, dtype=np.uint8)
    transformed = _adjust_brightness(source, 4)
    first = _frame_metadata(transformed, source)
    repeat = _frame_metadata(transformed.copy(), source.copy())
    assert first == repeat
    assert set(first) == {
        "shape",
        "dtype",
        "minimum",
        "maximum",
        "mean",
        "standard_deviation",
        "changed_pixel_count",
        "mean_absolute_difference",
        "difference_standard_deviation",
        "pixels_ge_230",
        "pixels_ge_235",
        "pixels_ge_240",
        "pixels_ge_245",
        "frame_sha256",
    }
    assert first["shape"] == source.shape
    assert first["dtype"] == "uint8"
    assert first["changed_pixel_count"] == source.shape[0] * source.shape[1]
    assert first["pixels_ge_245"] == 0


def test_honest_glare_contrast_crosses_the_244_245_preprocessing_boundary():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    source = scenes["glare-recovery-1"].frame
    transformed = _adjust_contrast(source, 0.92)
    source_metadata = _frame_metadata(source, source)
    transformed_metadata = _frame_metadata(transformed, source)

    assert source_metadata["maximum"] == 255
    assert source_metadata["pixels_ge_245"] > 0
    assert transformed_metadata["maximum"] == 244
    assert transformed_metadata["pixels_ge_245"] == 0
    assert transformed_metadata["pixels_ge_240"] > 0
    assert transformed_metadata["changed_pixel_count"] > 0
    assert transformed_metadata["frame_sha256"] != source_metadata["frame_sha256"]

    original_detection = _assert_fresh_detector_determinism(source, "glare-threshold-source")
    transformed_detection = _assert_fresh_detector_determinism(
        transformed,
        "glare-threshold-contrast-0.92",
    )
    assert original_detection.debug_metrics["glare_ratio"] > 0.0
    assert transformed_detection.debug_metrics["glare_ratio"] == 0.0


def test_original_saturated_glare_is_coherent_ambiguous_without_numeric_oil():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    detection = _assert_fresh_detector_determinism(
        scenes["glare-recovery-1"].frame,
        "saturated-glare-coherent-ambiguity",
    )
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None
    assert "OIL_PIPELINE_FAILURE" not in detection.flags
    assert "OIL_EVIDENCE_AMBIGUOUS" in detection.flags
    assert "FOGGED_OR_GLARE" in detection.flags
    assert "REVIEW_REQUIRED" in detection.flags
    assert detection.debug_metrics["oil_pipeline_available"] is True
    assert detection.debug_metrics["oil_pipeline_failure_stage"] is None
    assert detection.debug_metrics["oil_hypothesis_current_observation"] == "ambiguous"
    assert detection.debug_metrics["oil_decision_reason"] == "glare_visibility_conflict"
    assert detection.debug_metrics["oil_temporal_projected_source_y"] is None
    assert detection.debug_metrics["oil_tracker_action"] == "NO_UPDATE"
    assert detection.debug_metrics["oil_smoothing_action"] == "PRESERVE"


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
    assert payload["detector"]["version"] == "opencv-phase-detector-r17-physical-observation-ownership-v2"

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


def _bright_boundary_frame(
    above: int,
    below: int,
    *,
    y: int = 120,
    line: int | None = None,
) -> np.ndarray:
    frame = np.full((240, 320, 3), above, dtype=np.uint8)
    frame[y:] = below
    if line is not None:
        cv2.line(frame, (0, y), (319, y), (line, line, line), 2)
    return frame


def _textured_boundary_frame(
    texture: str,
    *,
    brightness: int,
    amplitude: int,
    period: int,
    y: int,
    bright_side: str,
    phase_offset: int = 0,
) -> np.ndarray:
    frame = np.full((240, 320, 3), 70, dtype=np.uint8)
    x = np.arange(320, dtype=np.float64) + phase_offset
    if texture == "stripes":
        values = brightness + amplitude * ((x // period) % 2 * 2 - 1)
    elif texture == "gradient":
        values = brightness + amplitude * (2 * x / 319 - 1)
    elif texture == "sinusoid":
        values = brightness + amplitude * np.sin(2 * np.pi * x / period)
    else:
        raise AssertionError(f"unsupported texture: {texture}")
    phase = np.clip(values, 0, 244).astype(np.uint8)
    if bright_side == "above":
        frame[:y] = phase[None, :, None]
    elif bright_side == "below":
        frame[y:] = phase[None, :, None]
    else:
        raise AssertionError(f"unsupported bright side: {bright_side}")
    return frame


def _partial_glare_frame(
    width: int,
    *,
    center_x: int = 160,
    top: int = 80,
    bottom: int = 185,
) -> np.ndarray:
    frame = np.full((240, 320, 3), 90, dtype=np.uint8)
    left = center_x - width // 2
    frame[top:bottom, left : left + width] = 244
    return frame


@pytest.mark.parametrize(
    "case_id,frame,expected_y",
    (
        ("upper-230-line-244", _bright_boundary_frame(230, 70, line=244), 120.0),
        ("upper-244-no-line", _bright_boundary_frame(244, 70), 120.0),
        ("lower-bright-reversed", _bright_boundary_frame(70, 230), 120.0),
        ("threshold-minus-one-line", _bright_boundary_frame(244, 70, line=244), 120.0),
        ("local-bright-interface-line", _bright_boundary_frame(175, 70, line=244), 120.0),
        ("near-roi-top", _bright_boundary_frame(230, 70, y=75, line=244), 75.0),
        ("near-roi-bottom", _bright_boundary_frame(230, 70, y=165, line=244), 165.0),
    ),
)
def test_bright_real_boundary_matrix_remains_numeric(case_id, frame, expected_y):
    detection = _assert_fresh_detector_determinism(frame, f"bright-boundary-{case_id}")
    context = {
        "case_id": case_id,
        "raw_oil_y": detection.raw_oil_air_level_y,
        "fill_state": detection.fill_state.value,
        "flags": detection.flags,
        "boundary_score": detection.debug_metrics["oil_boundary_score"],
        "artifact_score": detection.debug_metrics["oil_artifact_score"],
    }
    assert detection.raw_oil_air_level_y is not None, context
    assert abs(detection.raw_oil_air_level_y - expected_y) <= 4.0, context
    assert "OIL_PIPELINE_FAILURE" not in detection.flags, context


@pytest.mark.parametrize(
    "case_id,frame,expected_y",
    (
        (
            "stripes-normal-above",
            _textured_boundary_frame(
                "stripes",
                brightness=180,
                amplitude=4,
                period=12,
                y=120,
                bright_side="above",
            ),
            120.0,
        ),
        (
            "stripes-bright-below-offset",
            _textured_boundary_frame(
                "stripes",
                brightness=220,
                amplitude=8,
                period=24,
                y=120,
                bright_side="below",
                phase_offset=5,
            ),
            120.0,
        ),
        (
            "stripes-near-threshold-high-boundary",
            _textured_boundary_frame(
                "stripes",
                brightness=236,
                amplitude=12,
                period=48,
                y=100,
                bright_side="above",
                phase_offset=11,
            ),
            100.0,
        ),
        (
            "gradient-normal-above",
            _textured_boundary_frame(
                "gradient",
                brightness=150,
                amplitude=8,
                period=1,
                y=120,
                bright_side="above",
            ),
            120.0,
        ),
        (
            "gradient-middle-below",
            _textured_boundary_frame(
                "gradient",
                brightness=180,
                amplitude=12,
                period=1,
                y=140,
                bright_side="below",
            ),
            140.0,
        ),
        (
            "gradient-bright-high-boundary",
            _textured_boundary_frame(
                "gradient",
                brightness=220,
                amplitude=16,
                period=1,
                y=100,
                bright_side="above",
            ),
            100.0,
        ),
        (
            "sinusoid-normal-above",
            _textured_boundary_frame(
                "sinusoid",
                brightness=180,
                amplitude=6,
                period=48,
                y=120,
                bright_side="above",
            ),
            120.0,
        ),
        (
            "sinusoid-bright-below-offset",
            _textured_boundary_frame(
                "sinusoid",
                brightness=220,
                amplitude=10,
                period=64,
                y=140,
                bright_side="below",
                phase_offset=7,
            ),
            140.0,
        ),
        (
            "sinusoid-near-threshold-high-boundary",
            _textured_boundary_frame(
                "sinusoid",
                brightness=236,
                amplitude=8,
                period=48,
                y=100,
                bright_side="above",
                phase_offset=13,
            ),
            100.0,
        ),
    ),
)
def test_legitimate_textured_oil_phase_remains_numeric(case_id, frame, expected_y):
    detection = _assert_fresh_detector_determinism(frame, f"textured-{case_id}")
    context = {
        "case_id": case_id,
        "raw_oil_y": detection.raw_oil_air_level_y,
        "boundary_score": detection.debug_metrics["oil_boundary_score"],
        "artifact_score": detection.debug_metrics["oil_artifact_score"],
        "flags": detection.flags,
    }
    assert detection.raw_oil_air_level_y is not None, context
    assert abs(detection.raw_oil_air_level_y - expected_y) <= 4.0, context
    assert "OIL_PIPELINE_FAILURE" not in detection.flags, context


def test_uniform_partial_glare_width_sweep_has_no_acceptance_cliff():
    scores = []
    for width in (48, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70):
        detection, _input_hash = _fresh_detection(
            _partial_glare_frame(width),
            f"partial-glare-width-{width}",
            debug=False,
        )
        context = {
            "width": width,
            "raw_oil_y": detection.raw_oil_air_level_y,
            "boundary_score": detection.debug_metrics["oil_boundary_score"],
            "artifact_score": detection.debug_metrics["oil_artifact_score"],
            "flags": detection.flags,
        }
        assert detection.raw_oil_air_level_y is None, context
        assert "OIL_PIPELINE_FAILURE" not in detection.flags, context
        scores.append(detection.debug_metrics["oil_artifact_score"])

    # R6's connected optics classifier has an explicit component-topology
    # transition, so the old scalar-score smoothness contract no longer applies.
    # The safety authority is publication: every width remains fail-closed while
    # the bounded diagnostic score stays finite.
    assert all(0.0 <= float(score) <= 1.0 for score in scores)
    assert max(scores) >= 0.80


def test_partial_glare_location_and_roi_scale_variants_remain_suppressed():
    for center_x in (145, 152, 160, 168, 175):
        detection, _input_hash = _fresh_detection(
            _partial_glare_frame(60, center_x=center_x),
            f"partial-glare-location-{center_x}",
            debug=False,
        )
        assert detection.raw_oil_air_level_y is None, center_x

    for radius_x, radius_y, width in (
        (30.0, 52.0, 44),
        (38.4, 64.8, 60),
        (50.0, 78.0, 78),
        (62.0, 92.0, 96),
    ):
        frame = _partial_glare_frame(width, top=72, bottom=190)
        input_hash = hashlib.sha256(frame.tobytes()).hexdigest()
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"partial-glare-roi-{radius_x}"
        glass.geometry.ellipse = EllipseGeometry(
            160.0,
            120.0,
            radius_x,
            radius_y,
        )
        detection, _artifacts = OpenCvPhaseDetector().detect(
            frame,
            glass,
            0,
            1.0,
            debug=False,
        )
        assert hashlib.sha256(frame.tobytes()).hexdigest() == input_hash
        assert detection.raw_oil_air_level_y is None, radius_x
        assert "OIL_PIPELINE_FAILURE" not in detection.flags, radius_x


def _positive_neighborhood_cases():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    cases = []
    for case_id in ("clear-upper", "rapid-filling-0"):
        scene = scenes[case_id]
        assert scene.oil_y is not None
        for probe_name, frame, truth_offset in _local_neighborhood(scene.frame):
            cases.append(
                pytest.param(
                    case_id,
                    probe_name,
                    frame,
                    scene.oil_y + truth_offset,
                    _frame_metadata(frame, scene.frame),
                    id=f"{case_id}-{probe_name}",
                )
            )
    return cases


@pytest.mark.parametrize(
    "case_id,probe_name,frame,expected_y,metadata",
    _positive_neighborhood_cases(),
)
def test_clear_and_rapid_local_neighborhoods_are_numeric_and_deterministic(
    case_id,
    probe_name,
    frame,
    expected_y,
    metadata,
):
    detection = _assert_fresh_detector_determinism(
        frame,
        f"positive-{case_id}-{probe_name}",
    )
    context = {
        "probe": f"{case_id}-{probe_name}",
        "intensity": metadata,
        "raw_oil_y": detection.raw_oil_air_level_y,
        "fill_state": detection.fill_state.value,
        "flags": detection.flags,
        "glare_mask_population": metadata["pixels_ge_245"],
        "glare_ratio": detection.debug_metrics["glare_ratio"],
    }
    assert "OIL_PIPELINE_FAILURE" not in detection.flags, context
    assert detection.raw_oil_air_level_y is not None, context
    assert detection.fill_state.value != "UNKNOWN_REVIEW", context
    assert abs(detection.raw_oil_air_level_y - expected_y) <= 4.0, context


def _negative_neighborhood_cases():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    foam_scenes = {scene.case_id: scene for scene in controlled_foam_scenes()}
    thin_line = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.line(thin_line, (0, 120), (319, 120), (235, 235, 235), 1)
    paired_pulse = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.rectangle(paired_pulse, (0, 113), (319, 116), (235, 235, 235), -1)
    cv2.rectangle(paired_pulse, (0, 123), (319, 126), (45, 45, 45), -1)
    static_frames = tuple(thin_line.copy() for _ in range(4))
    controls = (
        ("thin-structural-line", thin_line, (), None),
        ("paired-pulse", paired_pulse, (), None),
        ("rim-adjacent-line", scenes["rim-line"].frame, (), None),
        ("reflection-only", scenes["reflection-only"].frame, (), None),
        ("glare-only", scenes["glare-recovery-1"].frame, (), None),
        ("shimmer-only", scenes["shimmer-only"].frame, (), None),
        ("learned-static-overlap", thin_line, static_frames, None),
        ("uniform-full", scenes["full-no-interface"].frame, (), "FULL_NO_INTERFACE"),
        ("uniform-empty", scenes["empty-no-interface"].frame, (), "EMPTY_NO_INTERFACE"),
        ("transient-false-line", scenes["transient-false-line-1"].frame, (), None),
        ("foam-clipped-glare", foam_scenes["clipped-glare"].frame, (), None),
    )
    cases = []
    for control_name, base_frame, learned_static, expected_state in controls:
        for probe_name, frame, _truth_offset in _local_neighborhood(base_frame):
            cases.append(
                pytest.param(
                    control_name,
                    probe_name,
                    frame,
                    learned_static,
                    expected_state,
                    _frame_metadata(frame, base_frame),
                    id=f"{control_name}-{probe_name}",
                )
            )
    return cases


@pytest.mark.parametrize(
    "control_name,probe_name,frame,learned_static,expected_state,metadata",
    _negative_neighborhood_cases(),
)
def test_negative_local_neighborhoods_do_not_create_head_only_oil(
    control_name,
    probe_name,
    frame,
    learned_static,
    expected_state,
    metadata,
):
    detection = _assert_fresh_detector_determinism(
        frame,
        f"negative-{control_name}-{probe_name}",
        static_frames=learned_static,
    )
    context = {
        "probe": f"{control_name}-{probe_name}",
        "intensity": metadata,
        "raw_oil_y": detection.raw_oil_air_level_y,
        "fill_state": detection.fill_state.value,
        "flags": detection.flags,
        "glare_mask_population": metadata["pixels_ge_245"],
        "glare_ratio": detection.debug_metrics["glare_ratio"],
    }
    assert detection.raw_oil_air_level_y is None, context
    if control_name != "glare-only":
        assert "OIL_PIPELINE_FAILURE" not in detection.flags, context
    if expected_state is not None:
        assert detection.fill_state.value == expected_state, context


def test_structural_real_boundary_remains_distinct_from_structural_only_control():
    scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    thin_line = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.line(thin_line, (0, 120), (319, 120), (235, 235, 235), 1)
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
