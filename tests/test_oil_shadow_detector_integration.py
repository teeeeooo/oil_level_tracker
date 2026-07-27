from __future__ import annotations

from datetime import datetime, timezone
import hashlib

import numpy as np

from benchmark_fixtures import export_benchmark_dataset
from foam_benchmark_fixtures import controlled_scenes
from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.application.services.detector_settings import detector_settings_to_json
from oil_tracker.domain.recipe import InspectionRecipe


def _glass(glass_id="shadow-glass"):
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = glass_id
    glass.geometry.zero_line_y = 150.0
    glass.detector_settings.minimum_final_confidence = 0.35
    glass.detector_settings.oil_tracker_update_confidence = 0.45
    glass.detector_settings.oil_path_min_margin = 0.04
    glass.detector_settings.oil_reacquire_frames = 2
    return glass


def _oil_frame(y=130):
    frame = np.full((240, 320, 3), 175, dtype=np.uint8)
    frame[y:] = 70
    frame[y - 1 : y + 2] = 225
    return frame


def _image_signature(images):
    return tuple(
        sorted(
            (
                key,
                value.shape,
                str(value.dtype),
                hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
            )
            for key, value in images.items()
        )
    )


def _official_snapshot(detection, artifacts):
    metrics = tuple(
        sorted(
            (key, value)
            for key, value in detection.debug_metrics.items()
            if not key.startswith("shadow_oil_")
        )
    )
    candidates = tuple(
        (
            item.source,
            item.kind.value,
            item.y,
            tuple(sorted(item.features.items())),
            tuple(sorted(item.penalties.items())),
            item.feature_score,
            item.penalty,
            item.final_score,
            item.selected,
            item.rejected,
            item.reject_reason,
        )
        for item in detection.candidates
    )
    artifact_snapshot = None
    if artifacts is not None:
        artifact_snapshot = (
            _image_signature(artifacts.images),
            tuple(sorted((key, tuple(value)) for key, value in artifacts.profiles.items())),
            tuple(tuple(sorted(row.items())) for row in artifacts.candidate_rows),
            tuple(
                sorted(
                    (key, value)
                    for key, value in artifacts.state.items()
                    if key != "shadow_oil" and not key.startswith("shadow_oil_")
                )
            ),
        )
    return (
        detection.fill_state,
        detection.raw_oil_air_level_y,
        detection.smoothed_oil_air_level_y,
        detection.raw_foam_front_y,
        detection.smoothed_foam_front_y,
        detection.oil_air_level_px_from_zero,
        detection.foam_front_px_from_zero,
        detection.oil_air_confidence,
        detection.foam_confidence,
        detection.visibility_confidence,
        detection.overall_confidence,
        tuple(detection.flags),
        candidates,
        metrics,
        artifact_snapshot,
    )


def test_shadow_enabled_disabled_are_officially_identical_for_oil_dropout_and_foam():
    enabled = OpenCvPhaseDetector(shadow_enabled=True)
    disabled = OpenCvPhaseDetector(shadow_enabled=False)
    glass_a = _glass()
    glass_b = _glass()
    foam = next(item.frame for item in controlled_scenes() if item.case_id == "white-foam")
    frames = (_oil_frame(130), np.full((240, 320, 3), 135, np.uint8), _oil_frame(132), foam)
    for index, frame in enumerate(frames, start=1):
        first = enabled.detect(frame.copy(), glass_a, index, index * 0.5, debug=True)
        second = disabled.detect(frame.copy(), glass_b, index, index * 0.5, debug=True)
        assert _official_snapshot(*first) == _official_snapshot(*second)
        assert all(not item.source.startswith("shadow") for item in first[0].candidates)
    assert enabled.version == disabled.version == "opencv-phase-detector-s5b-oil-v3"
    assert detector_settings_to_json(glass_a.detector_settings) == detector_settings_to_json(glass_b.detector_settings)


class _MutatingFailureRunner:
    def run(self, **kwargs):
        assert not kwargs["pre"].gray.flags.writeable
        assert not kwargs["effective_mask"].flags.writeable
        kwargs["pre"].gray[0, 0] = 0

    def reset(self, _glass_id=None):
        return None


def test_shadow_failure_and_attempted_input_mutation_are_isolated():
    failing = OpenCvPhaseDetector(shadow_runner=_MutatingFailureRunner())
    baseline = OpenCvPhaseDetector(shadow_enabled=False)
    glass_a = _glass()
    glass_b = _glass()
    frame = _oil_frame(130)
    before = frame.copy()
    failed = failing.detect(frame, glass_a, 1, 0.0, debug=True)
    control = baseline.detect(before.copy(), glass_b, 1, 0.0, debug=True)
    assert np.array_equal(frame, before)
    assert _official_snapshot(*failed) == _official_snapshot(*control)
    assert failed[0].debug_metrics["shadow_oil_available"] is False
    assert "ValueError" in failed[0].debug_metrics["shadow_oil_failure_reason"]


class _AdversarialRasterOwnershipRunner:
    def __init__(self):
        self.mutated_names = set()
        self.base_depths = {}

    def run(self, **kwargs):
        arrays = {
            "pre.gray": kwargs["pre"].gray,
            "pre.normalized": kwargs["pre"].normalized,
            "pre.blurred": kwargs["pre"].blurred,
            "pre.sobel_y_signed": kwargs["pre"].sobel_y_signed,
            "pre.sobel_y_abs": kwargs["pre"].sobel_y_abs,
            "pre.canny": kwargs["pre"].canny,
            "pre.horizontal_mask": kwargs["pre"].horizontal_mask,
            "pre.glare_mask": kwargs["pre"].glare_mask,
            "effective_mask": kwargs["effective_mask"],
            "ellipse_mask": kwargs["ellipse_mask"],
            "exclusion_mask": kwargs["exclusion_mask"],
            "static_artifact_map": kwargs["static_artifact_map"],
        }
        assert arrays["static_artifact_map"] is not None
        for name, array in arrays.items():
            assert array is not None
            assert not array.flags.writeable
            chain = [array]
            while isinstance(chain[-1].base, np.ndarray):
                chain.append(chain[-1].base)
            owner = chain[-1]
            self.base_depths[name] = len(chain) - 1
            assert owner.flags.owndata
            assert owner.base is None
            before = array.copy()
            owner.setflags(write=True)
            writable = np.asarray(owner)
            replacement = 0 if np.any(writable != 0) else 1
            writable[...] = replacement
            assert not np.array_equal(array, before)
            self.mutated_names.add(name)
        raise RuntimeError("adversarial shadow raster mutation")

    def reset(self, _glass_id=None):
        return None


def test_shadow_owned_rasters_survive_base_chain_mutation_and_failure():
    runner = _AdversarialRasterOwnershipRunner()
    failing = OpenCvPhaseDetector(shadow_runner=runner)
    baseline = OpenCvPhaseDetector(shadow_enabled=False)
    glass_a = _glass("ownership-a")
    glass_b = _glass("ownership-b")
    static = _oil_frame(115)
    failing.learn_static_artifact([static.copy()] * 3, glass_a)
    baseline.learn_static_artifact([static.copy()] * 3, glass_b)
    frame = _oil_frame(130)
    before = frame.copy()

    failed = failing.detect(frame, glass_a, 1, 0.0, debug=True)
    control = baseline.detect(before.copy(), glass_b, 1, 0.0, debug=True)

    expected_names = {
        "pre.gray",
        "pre.normalized",
        "pre.blurred",
        "pre.sobel_y_signed",
        "pre.sobel_y_abs",
        "pre.canny",
        "pre.horizontal_mask",
        "pre.glare_mask",
        "effective_mask",
        "ellipse_mask",
        "exclusion_mask",
        "static_artifact_map",
    }
    assert runner.mutated_names == expected_names
    assert runner.base_depths == {name: 0 for name in expected_names}
    assert np.array_equal(frame, before)
    assert _official_snapshot(*failed) == _official_snapshot(*control)
    assert failing.version == baseline.version == "opencv-phase-detector-s5b-oil-v3"
    assert failed[0].debug_metrics["shadow_oil_available"] is False
    assert "RuntimeError" in failed[0].debug_metrics["shadow_oil_failure_reason"]


def test_debug_false_runs_shadow_but_keeps_artifact_contract_none():
    detector = OpenCvPhaseDetector()
    detection, artifacts = detector.detect(_oil_frame(), _glass(), 1, 0.0, debug=False)
    assert artifacts is None
    assert detection.debug_metrics["shadow_oil_available"] is True
    assert (
        detection.debug_metrics["shadow_oil_raw_observation_count"]
        <= detection.debug_metrics["shadow_oil_raw_observation_limit"]
    )
    assert (
        detection.debug_metrics["shadow_oil_proposal_count"]
        <= detection.debug_metrics["shadow_oil_proposal_limit"]
    )
    assert (
        detection.debug_metrics["shadow_oil_hypothesis_count"]
        <= detection.debug_metrics["shadow_oil_hypothesis_limit"]
    )
    assert (
        detection.debug_metrics["shadow_oil_debug_scalar_count"]
        <= detection.debug_metrics["shadow_oil_debug_scalar_limit"]
    )


def test_shadow_runtime_and_debug_evidence_are_deterministic_and_bounded():
    first = OpenCvPhaseDetector()
    second = OpenCvPhaseDetector()
    a, artifacts_a = first.detect(_oil_frame(), _glass(), 1, 0.0, debug=True)
    b, artifacts_b = second.detect(_oil_frame(), _glass(), 1, 0.0, debug=True)
    shadow_a = tuple(sorted((k, v) for k, v in a.debug_metrics.items() if k.startswith("shadow_oil_")))
    shadow_b = tuple(sorted((k, v) for k, v in b.debug_metrics.items() if k.startswith("shadow_oil_")))
    assert shadow_a == shadow_b
    assert artifacts_a is not None and artifacts_b is not None
    assert artifacts_a.state["shadow_oil"] == artifacts_b.state["shadow_oil"]
    assert "selected_hypothesis_id" in artifacts_a.state["shadow_oil"]
    assert "resource_counts" in artifacts_a.state["shadow_oil"]


def test_shadow_state_is_glass_local_and_reset_with_detector():
    detector = OpenCvPhaseDetector()
    detector.detect(_oil_frame(125), _glass("a"), 1, 0.0)
    detector.detect(_oil_frame(145), _glass("b"), 1, 0.0)
    assert detector.shadow_temporal_state_count == 2
    detector.reset("a")
    assert detector.shadow_temporal_state_count == 1
    detector.reset()
    assert detector.shadow_temporal_state_count == 0
    assert detector.oil_temporal_state_count == 0
    assert detector.foam_temporal_state_count == 0

def _benchmark_service(shadow_enabled):
    return DetectorBenchmarkService(
        FilesystemRegressionDatasetReader(),
        AtomicBenchmarkResultWriter(),
        lambda: OpenCvPhaseDetector(shadow_enabled=shadow_enabled),
        clock=lambda: datetime(2026, 7, 27, 12, 0, 0, tzinfo=timezone.utc),
        runtime_metadata_factory=lambda: {
            "python": "shadow-isolation",
            "packages": {
                "numpy": "shadow-isolation",
                "opencv-python-headless": "shadow-isolation",
            },
        },
    )


def test_benchmark_cases_metrics_and_settings_fingerprint_ignore_shadow_enablement(tmp_path):
    dataset = export_benchmark_dataset(tmp_path, label="shadow-isolation")
    enabled = _benchmark_service(True).run(dataset, tmp_path / "enabled").payload
    disabled = _benchmark_service(False).run(dataset, tmp_path / "disabled").payload
    assert enabled["detector"] == disabled["detector"]
    assert enabled["cases"] == disabled["cases"]
    assert enabled["category_summaries"] == disabled["category_summaries"]
    assert enabled["micro_aggregate"] == disabled["micro_aggregate"]
    assert enabled["macro_category_aggregate"] == disabled["macro_category_aggregate"]
    assert enabled["run_fingerprint"] == disabled["run_fingerprint"]
