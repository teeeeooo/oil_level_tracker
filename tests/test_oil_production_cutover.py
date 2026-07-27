from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import inspect
import json
import math

import numpy as np
import pytest

from benchmark_fixtures import export_benchmark_dataset
from foam_benchmark_fixtures import controlled_scenes
from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision import (
    candidate_generators,
    candidate_scorer,
    oil_candidate_consensus,
    oil_no_interface,
    oil_temporal_path,
)
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_hypothesis_projection import (
    validate_production_result,
)
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    OilShadowFrameResult,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowTemporalStatus,
    ShadowUnavailableObservation,
)
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.application.services.detector_settings import detector_settings_to_json
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe


DETECTOR_VERSION = "opencv-phase-detector-s5b-typed-production-v1"


def _glass(glass_id: str = "typed-glass", initial=InitialObservationState.AUTO):
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = glass_id
    glass.geometry.zero_line_y = 150.0
    glass.initial_state = initial
    glass.detector_settings.minimum_final_confidence = 0.35
    return glass


def _oil_frame(y: int = 130):
    frame = np.full((240, 320, 3), 175, dtype=np.uint8)
    frame[y:] = 70
    frame[y - 1 : y + 2] = 225
    return frame


def _uniform_frame(value: int):
    return np.full((240, 320, 3), value, dtype=np.uint8)


def _pipeline_result(
    frame: np.ndarray,
    glass_id: str,
    pipeline: OilHypothesisPipeline | None = None,
) -> OilShadowFrameResult:
    owner = pipeline or OilHypothesisPipeline()
    glass = _glass(glass_id)
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    return owner.run(
        glass_id=glass.id,
        pre=pre,
        effective_mask=bundle.effective_mask,
        ellipse_mask=bundle.ellipse_mask,
        exclusion_mask=bundle.exclusion_mask,
        static_artifact_map=None,
        crop_origin_y=float(bundle.crop_origin[1]),
    )


def _ambiguous_observation(result: OilShadowFrameResult):
    current = result.current_observation
    assert isinstance(current, ShadowBoundaryObservation)
    hypothesis = current.hypothesis
    return ShadowAmbiguousObservation(
        kind=ShadowObservationKind.AMBIGUOUS,
        hypothesis_ids=(hypothesis.identity,),
        boundary_likelihood=hypothesis.boundary_likelihood,
        artifact_likelihood=hypothesis.artifact_likelihood,
        ambiguity_likelihood=max(0.35, hypothesis.ambiguity_likelihood),
        no_interface_likelihood=current.no_interface.likelihood,
        visibility=hypothesis.visibility,
        projected_source_y=hypothesis.representative_source_y,
        reason="adversarial_typed_result",
    )


def _white_foam_frame() -> np.ndarray:
    return next(
        item.frame.copy()
        for item in controlled_scenes()
        if item.case_id == "white-foam"
    )


def _candidate_signature(detection):
    return tuple(
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


class _ExactTypedResultRunner:
    def __init__(self, result: OilShadowFrameResult):
        self.result = result

    def run(self, **_kwargs):
        return self.result

    def reset(self, _glass_id=None):
        return None


def _coherent_typed_results() -> tuple[OilShadowFrameResult, ...]:
    boundary = _pipeline_result(_oil_frame(), "coherent-boundary")
    no_interface = _pipeline_result(_uniform_frame(75), "coherent-no-interface")
    assert isinstance(boundary.current_observation, ShadowBoundaryObservation)
    assert isinstance(no_interface.current_observation, ShadowNoInterfaceObservation)

    hypothesis = boundary.current_observation.hypothesis
    reacquisition = replace(
        boundary,
        temporal_decision=replace(
            boundary.temporal_decision,
            status=ShadowTemporalStatus.REACQUISITION_PENDING,
            observation_kind=ShadowObservationKind.BOUNDARY,
            selected_hypothesis_id=hypothesis.identity,
            projected_source_y=None,
            reason="coherent_reacquisition",
        ),
    )
    ambiguous_observation = _ambiguous_observation(boundary)
    ambiguous = replace(
        boundary,
        current_observation=ambiguous_observation,
        temporal_decision=replace(
            boundary.temporal_decision,
            status=ShadowTemporalStatus.AMBIGUOUS,
            observation_kind=ShadowObservationKind.AMBIGUOUS,
            selected_hypothesis_id=None,
            projected_source_y=ambiguous_observation.projected_source_y,
            reason="coherent_ambiguous",
        ),
    )
    unavailable = OilHypothesisPipeline().failure_result(
        glass_id="coherent-unavailable",
        reason="coherent_unavailable",
    )
    return boundary, reacquisition, no_interface, ambiguous, unavailable


def _forged_observation_kind(observation, kind: ShadowObservationKind):
    forged = replace(observation)
    object.__setattr__(forged, "kind", kind)
    return forged


def _malformed_typed_results() -> tuple[tuple[str, OilShadowFrameResult], ...]:
    boundary, reacquisition, no_interface, ambiguous, unavailable = (
        _coherent_typed_results()
    )
    current_boundary = boundary.current_observation
    current_no_interface = no_interface.current_observation
    assert isinstance(current_boundary, ShadowBoundaryObservation)
    assert isinstance(current_no_interface, ShadowNoInterfaceObservation)
    hypothesis = current_boundary.hypothesis
    ambiguous_current = _ambiguous_observation(boundary)
    unavailable_current = ShadowUnavailableObservation(
        ShadowObservationKind.UNAVAILABLE,
        0.0,
        "adversarial_unavailable",
    )
    coherent_ambiguous_current = ambiguous.current_observation
    coherent_unavailable_current = unavailable.current_observation
    assert isinstance(coherent_ambiguous_current, ShadowAmbiguousObservation)
    assert isinstance(coherent_unavailable_current, ShadowUnavailableObservation)

    forged_boundary_for_accepted = _forged_observation_kind(
        current_boundary,
        ShadowObservationKind.NO_INTERFACE,
    )
    forged_boundary_for_reacquisition = _forged_observation_kind(
        current_boundary,
        ShadowObservationKind.AMBIGUOUS,
    )
    forged_no_interface = _forged_observation_kind(
        current_no_interface,
        ShadowObservationKind.BOUNDARY,
    )
    forged_ambiguous = _forged_observation_kind(
        coherent_ambiguous_current,
        ShadowObservationKind.UNAVAILABLE,
    )
    forged_unavailable = _forged_observation_kind(
        coherent_unavailable_current,
        ShadowObservationKind.NO_INTERFACE,
    )

    reacquisition_decision = replace(
        boundary.temporal_decision,
        status=ShadowTemporalStatus.REACQUISITION_PENDING,
        observation_kind=ShadowObservationKind.BOUNDARY,
        projected_source_y=None,
        reason="malformed_reacquisition",
    )
    no_interface_decision = replace(
        no_interface.temporal_decision,
        status=ShadowTemporalStatus.NO_INTERFACE_ACCEPTED,
        observation_kind=ShadowObservationKind.NO_INTERFACE,
        selected_hypothesis_id=None,
        projected_source_y=None,
        reason="malformed_no_interface",
    )
    ambiguous_decision = replace(
        boundary.temporal_decision,
        status=ShadowTemporalStatus.AMBIGUOUS,
        observation_kind=ShadowObservationKind.AMBIGUOUS,
        selected_hypothesis_id=None,
        projected_source_y=ambiguous_current.projected_source_y,
        reason="malformed_ambiguous",
    )
    unavailable_decision = replace(
        boundary.temporal_decision,
        status=ShadowTemporalStatus.UNAVAILABLE,
        observation_kind=ShadowObservationKind.UNAVAILABLE,
        selected_hypothesis_id=None,
        projected_source_y=None,
        reason="malformed_unavailable",
    )

    alternate = replace(hypothesis, identity="alternate-hypothesis-id")
    altered_current_hypothesis = replace(
        hypothesis,
        representative_source_y=hypothesis.representative_source_y + 1.0,
    )
    altered_current = replace(
        current_boundary,
        hypothesis=altered_current_hypothesis,
    )
    wrong_identity = replace(
        boundary,
        hypotheses=(hypothesis, alternate),
        temporal_decision=replace(
            boundary.temporal_decision,
            selected_hypothesis_id=alternate.identity,
        ),
    )
    unsupported_decision = replace(boundary.temporal_decision)
    object.__setattr__(unsupported_decision, "status", "unsupported_status")

    return (
        (
            "boundary accepted with forged boundary kind",
            replace(boundary, current_observation=forged_boundary_for_accepted),
        ),
        (
            "reacquisition pending with forged boundary kind",
            replace(
                reacquisition,
                current_observation=forged_boundary_for_reacquisition,
            ),
        ),
        (
            "no-interface accepted with forged no-interface kind",
            replace(no_interface, current_observation=forged_no_interface),
        ),
        (
            "ambiguous with forged ambiguous kind",
            replace(ambiguous, current_observation=forged_ambiguous),
        ),
        (
            "unavailable with forged unavailable kind",
            replace(unavailable, current_observation=forged_unavailable),
        ),
        (
            "boundary accepted with no-interface current",
            replace(boundary, current_observation=current_no_interface),
        ),
        (
            "boundary accepted with ambiguous current",
            replace(boundary, current_observation=ambiguous_current),
        ),
        (
            "boundary accepted with unavailable current",
            replace(boundary, current_observation=unavailable_current),
        ),
        (
            "reacquisition pending with non-boundary current",
            replace(
                boundary,
                current_observation=current_no_interface,
                temporal_decision=reacquisition_decision,
            ),
        ),
        (
            "no-interface accepted with boundary current",
            replace(
                no_interface,
                current_observation=current_boundary,
                temporal_decision=no_interface_decision,
            ),
        ),
        (
            "ambiguous with wrong current type",
            replace(boundary, temporal_decision=ambiguous_decision),
        ),
        (
            "unavailable with wrong current type",
            replace(boundary, temporal_decision=unavailable_decision),
        ),
        ("boundary selected identity disagrees with current", wrong_identity),
        (
            "current boundary content disagrees with canonical tuple",
            replace(boundary, current_observation=altered_current),
        ),
        (
            "accepted projected Y disagrees with current and canonical",
            replace(
                boundary,
                temporal_decision=replace(
                    boundary.temporal_decision,
                    projected_source_y=hypothesis.representative_source_y + 1.0,
                ),
            ),
        ),
        (
            "ambiguous projected Y disagrees with current",
            replace(
                boundary,
                current_observation=ambiguous_current,
                temporal_decision=replace(
                    ambiguous_decision,
                    projected_source_y=(
                        float(ambiguous_current.projected_source_y) + 1.0
                    ),
                ),
            ),
        ),
        (
            "unsupported temporal status",
            replace(boundary, temporal_decision=unsupported_decision),
        ),
    )


def test_coherent_typed_result_combinations_validate():
    for result in _coherent_typed_results():
        validate_production_result(result)


def test_production_detector_does_not_call_legacy_oil_owners(monkeypatch):
    source = inspect.getsource(OpenCvPhaseDetector)
    for forbidden_name in (
        "generate_oil_air_candidates",
        "build_oil_candidate_consensus",
        "score_candidates",
        "evaluate_no_interface",
        "OilTemporalPath",
    ):
        assert forbidden_name not in source

    def forbidden(*_args, **_kwargs):
        raise AssertionError("legacy oil owner was called")

    monkeypatch.setattr(candidate_generators, "generate_oil_air_candidates", forbidden)
    monkeypatch.setattr(oil_candidate_consensus, "build_oil_candidate_consensus", forbidden)
    monkeypatch.setattr(candidate_scorer, "score_candidates", forbidden)
    monkeypatch.setattr(oil_no_interface, "evaluate_no_interface", forbidden)
    monkeypatch.setattr(oil_temporal_path.OilTemporalPath, "evaluate", forbidden)

    detection, _ = OpenCvPhaseDetector().detect(
        _oil_frame(),
        _glass(),
        1,
        0.0,
    )
    assert detection.raw_oil_air_level_y is not None
    assert detection.debug_metrics["oil_pipeline_available"] is True


def test_accepted_typed_boundary_projects_official_raw_smoothed_and_candidate():
    detector = OpenCvPhaseDetector()
    detection, artifacts = detector.detect(
        _oil_frame(130),
        _glass(),
        1,
        0.0,
        debug=True,
    )

    assert detector.version == DETECTOR_VERSION
    assert detection.debug_metrics["oil_decision_status"] == "boundary_accepted"
    assert detection.raw_oil_air_level_y is not None
    assert detection.smoothed_oil_air_level_y == detection.raw_oil_air_level_y
    selected = [
        item
        for item in detection.candidates
        if item.kind.value == "oil_air" and item.selected
    ]
    assert len(selected) == 1
    candidate = selected[0]
    assert candidate.source.startswith("oil_hypothesis:")
    assert candidate.y == detection.raw_oil_air_level_y
    assert candidate.features["source_y"] == candidate.y
    assert candidate.features["temporal_selected"] == 1.0
    assert candidate.features["boundary_likelihood"] > 0.0
    assert candidate.features["provenance_count"] > 0.0
    assert {
        "edge_strength",
        "horizontal_coverage",
        "region_contrast",
        "temporal_score",
        "state_transition_score",
    } <= set(candidate.features)
    assert {
        "glare_penalty",
        "border_penalty",
        "exclusion_penalty",
        "static_artifact_penalty",
        "jump_penalty",
    } <= set(candidate.penalties)
    assert detection.oil_air_confidence == candidate.features["temporal_confidence"]
    assert all(math.isfinite(float(value)) for value in candidate.features.values())
    assert all(math.isfinite(float(value)) for value in candidate.penalties.values())
    assert artifacts is not None
    assert artifacts.state["oil_hypothesis"]["selected_hypothesis_id"] in candidate.source


def test_reacquisition_pending_has_no_numeric_oil_or_selected_candidate():
    detector = OpenCvPhaseDetector()
    glass = _glass("reacquisition")
    accepted, _ = detector.detect(_oil_frame(130), glass, 1, 0.0)
    pending, _ = detector.detect(_oil_frame(90), glass, 2, 0.5)
    assert accepted.raw_oil_air_level_y is not None
    assert pending.debug_metrics["oil_decision_status"] == "reacquisition_pending"
    assert pending.raw_oil_air_level_y is None
    assert pending.smoothed_oil_air_level_y is None
    assert "OIL_REACQUISITION_PENDING" in pending.flags
    assert not any(
        item.selected for item in pending.candidates if item.kind.value == "oil_air"
    )


def test_no_interface_full_empty_and_ambiguous_have_no_numeric_oil():
    cases = (
        (75, InitialObservationState.FULL_NO_INTERFACE, FillState.FULL_NO_INTERFACE),
        (205, InitialObservationState.EMPTY_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE),
        (135, InitialObservationState.AUTO, FillState.UNKNOWN_REVIEW),
    )
    for value, initial, expected_state in cases:
        detection, _ = OpenCvPhaseDetector().detect(
            _uniform_frame(value),
            _glass(f"no-interface-{value}", initial),
            1,
            0.0,
        )
        assert detection.debug_metrics["oil_decision_status"] == "no_interface_accepted"
        assert detection.raw_oil_air_level_y is None
        assert detection.smoothed_oil_air_level_y is None
        assert not any(
            item.selected for item in detection.candidates if item.kind.value == "oil_air"
        )
        assert detection.fill_state is expected_state


def test_stable_no_interface_clears_stale_smoothing():
    detector = OpenCvPhaseDetector()
    glass = _glass("stable-clear")
    accepted, _ = detector.detect(_oil_frame(130), glass, 1, 0.0)
    assert accepted.raw_oil_air_level_y is not None
    first, _ = detector.detect(_uniform_frame(75), glass, 2, 0.5)
    second, _ = detector.detect(_uniform_frame(75), glass, 3, 1.0)
    assert first.raw_oil_air_level_y is None
    assert first.smoothed_oil_air_level_y is None
    assert first.debug_metrics["oil_clear_smoothing"] is False
    assert second.raw_oil_air_level_y is None
    assert second.smoothed_oil_air_level_y is None
    assert second.debug_metrics["oil_clear_smoothing"] is True
    assert second.debug_metrics["oil_smoothing_sample_count"] == 0


class _FailAfterAcceptedRunner:
    def __init__(self):
        self.pipeline = OilHypothesisPipeline()
        self.calls = 0

    @property
    def temporal_state_count(self):
        return self.pipeline.temporal_state_count

    def run(self, **kwargs):
        self.calls += 1
        if self.calls > 1:
            raise RuntimeError("typed oil failure")
        return self.pipeline.run(**kwargs)

    def reset(self, glass_id=None):
        self.pipeline.reset(glass_id)


def test_pipeline_failure_has_no_legacy_fallback_and_stable_unavailable_clears():
    detector = OpenCvPhaseDetector(oil_runner=_FailAfterAcceptedRunner())
    glass = _glass("unavailable-clear")
    accepted, _ = detector.detect(_oil_frame(), glass, 1, 0.0)
    assert accepted.raw_oil_air_level_y is not None

    failures = [
        detector.detect(_oil_frame(), glass, index, index * 0.5)[0]
        for index in range(2, 8)
    ]
    assert all(item.raw_oil_air_level_y is None for item in failures)
    assert all(item.smoothed_oil_air_level_y is None for item in failures)
    assert all(item.debug_metrics["oil_pipeline_available"] is False for item in failures)
    assert all("OIL_PIPELINE_FAILURE" in item.flags for item in failures)
    assert failures[-1].debug_metrics["oil_clear_smoothing"] is True
    assert failures[-1].debug_metrics["oil_smoothing_sample_count"] == 0
    assert not any(
        item.source in {"oil_consensus", "sobel", "canny", "hough", "region_boundary"}
        for detection in failures
        for item in detection.candidates
        if item.kind.value == "oil_air"
    )


class _InvalidRunner:
    def run(self, **_kwargs):
        return {"not": "typed"}

    def reset(self, _glass_id=None):
        return None


def test_invalid_typed_return_projects_unavailable_without_numeric_output():
    detection, _ = OpenCvPhaseDetector(oil_runner=_InvalidRunner()).detect(
        _oil_frame(),
        _glass("invalid"),
        1,
        0.0,
    )
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None
    assert detection.debug_metrics["oil_pipeline_available"] is False
    assert "TypeError" in detection.debug_metrics["oil_pipeline_failure_reason"]
    assert "OIL_PIPELINE_FAILURE" in detection.flags


def _foam_projection_snapshot(detection, artifacts):
    foam_candidates = tuple(
        item
        for item in _candidate_signature(detection)
        if item[1] == "foam_front"
    )
    foam_metrics = tuple(
        sorted(
            (key, value)
            for key, value in detection.debug_metrics.items()
            if key.startswith("foam_")
        )
    )
    foam_images = {
        key: value
        for key, value in artifacts.images.items()
        if key.startswith("foam_")
    }
    return (
        detection.fill_state,
        detection.raw_foam_front_y,
        detection.smoothed_foam_front_y,
        detection.foam_front_y,
        detection.foam_confidence,
        foam_candidates,
        foam_metrics,
        _image_signature(foam_images),
    )


@pytest.mark.parametrize(
    ("case_name", "malformed_result"),
    _malformed_typed_results(),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_malformed_exact_typed_results_fail_closed_without_harming_foam(
    case_name,
    malformed_result,
):
    frame = _white_foam_frame()
    before = frame.copy()
    glass = _glass(f"malformed-{case_name}")
    baseline, baseline_artifacts = OpenCvPhaseDetector(
        oil_runner=_InvalidRunner()
    ).detect(frame.copy(), glass, 1, 0.0, debug=True)
    detection, artifacts = OpenCvPhaseDetector(
        oil_runner=_ExactTypedResultRunner(malformed_result)
    ).detect(frame, glass, 1, 0.0, debug=True)

    assert np.array_equal(frame, before), case_name
    assert detection.raw_oil_air_level_y is None, case_name
    assert detection.smoothed_oil_air_level_y is None, case_name
    assert detection.debug_metrics["oil_pipeline_available"] is False, case_name
    assert "ValueError" in detection.debug_metrics["oil_pipeline_failure_reason"], case_name
    assert "OIL_PIPELINE_FAILURE" in detection.flags, case_name
    assert not any(
        item.selected
        for item in detection.candidates
        if item.kind.value == "oil_air"
    ), case_name
    assert not any(
        item.source
        in {"oil_consensus", "sobel", "canny", "hough", "region_boundary"}
        for item in detection.candidates
        if item.kind.value == "oil_air"
    ), case_name
    assert artifacts is not None and baseline_artifacts is not None
    assert "foam_decision_status" in detection.debug_metrics
    assert _foam_projection_snapshot(detection, artifacts) == _foam_projection_snapshot(
        baseline,
        baseline_artifacts,
    ), case_name


class _AdversarialRasterRunner:
    def __init__(self):
        self.mutated_names = set()

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
        for name, array in arrays.items():
            assert array is not None
            assert not array.flags.writeable
            assert array.flags.owndata
            assert array.base is None
            array.setflags(write=True)
            array[...] = 0 if np.any(array != 0) else 1
            self.mutated_names.add(name)
        raise RuntimeError("adversarial typed raster mutation")

    def reset(self, _glass_id=None):
        return None


def test_pipeline_raster_mutation_and_failure_do_not_damage_frame_or_foam():
    runner = _AdversarialRasterRunner()
    detector = OpenCvPhaseDetector(oil_runner=runner)
    glass = _glass("raster-isolation")
    static = _oil_frame(115)
    detector.learn_static_artifact([static.copy()] * 3, glass)
    frame = _oil_frame(130)
    before = frame.copy()

    detection, artifacts = detector.detect(frame, glass, 1, 0.0, debug=True)
    assert np.array_equal(frame, before)
    assert len(runner.mutated_names) == 12
    assert detection.raw_oil_air_level_y is None
    assert detection.debug_metrics["oil_pipeline_available"] is False
    assert artifacts is not None
    assert _image_signature(artifacts.images)
    assert "foam_decision_status" in detection.debug_metrics


def test_candidate_and_debug_projection_are_deterministic_provenance_based_and_finite():
    first, artifacts_a = OpenCvPhaseDetector().detect(
        _oil_frame(), _glass("det-a"), 1, 0.0, debug=True
    )
    second, artifacts_b = OpenCvPhaseDetector().detect(
        _oil_frame(), _glass("det-b"), 1, 0.0, debug=True
    )
    assert _candidate_signature(first) == _candidate_signature(second)
    assert artifacts_a is not None and artifacts_b is not None
    assert artifacts_a.profiles == artifacts_b.profiles
    assert artifacts_a.candidate_rows == artifacts_b.candidate_rows
    assert artifacts_a.state["oil_hypothesis"] == artifacts_b.state["oil_hypothesis"]
    oil_candidates = [item for item in first.candidates if item.kind.value == "oil_air"]
    assert oil_candidates
    assert all(item.source.startswith("oil_hypothesis:") for item in oil_candidates)
    assert not any(item.source == "oil_consensus" for item in first.candidates)
    assert not any(key.startswith("shadow_oil_") for key in first.debug_metrics)
    assert not any("legacy" in key for key in first.debug_metrics)
    json.dumps(first.debug_metrics, allow_nan=False, sort_keys=True)
    json.dumps(artifacts_a.candidate_rows, allow_nan=False, sort_keys=True)
    json.dumps(artifacts_a.state, allow_nan=False, sort_keys=True)


def test_debug_false_artifacts_remain_none_and_typed_bounds_are_reported():
    detection, artifacts = OpenCvPhaseDetector().detect(
        _oil_frame(),
        _glass("debug-false"),
        1,
        0.0,
        debug=False,
    )
    assert artifacts is None
    assert detection.debug_metrics["oil_pipeline_available"] is True
    assert (
        detection.debug_metrics["oil_hypothesis_raw_observation_count"]
        <= detection.debug_metrics["oil_hypothesis_raw_observation_limit"]
    )
    assert (
        detection.debug_metrics["oil_hypothesis_count"]
        <= detection.debug_metrics["oil_hypothesis_limit"]
    )
    assert (
        detection.debug_metrics["oil_hypothesis_debug_scalar_count"]
        <= detection.debug_metrics["oil_hypothesis_debug_scalar_limit"]
    )


def test_typed_temporal_state_is_glass_local_and_resettable():
    detector = OpenCvPhaseDetector()
    detector.detect(_oil_frame(125), _glass("a"), 1, 0.0)
    detector.detect(_oil_frame(145), _glass("b"), 1, 0.0)
    assert detector.oil_temporal_state_count == 2
    detector.reset("a")
    assert detector.oil_temporal_state_count == 1
    detector.reset()
    assert detector.oil_temporal_state_count == 0
    assert detector.foam_temporal_state_count == 0


def test_benchmark_identifies_typed_production_detector_and_keeps_settings_fingerprint(tmp_path):
    dataset = export_benchmark_dataset(tmp_path, label="typed-production")
    settings = _glass().detector_settings
    before = detector_settings_to_json(settings)
    service = DetectorBenchmarkService(
        FilesystemRegressionDatasetReader(),
        AtomicBenchmarkResultWriter(),
        OpenCvPhaseDetector,
        clock=lambda: datetime(2026, 7, 27, 12, 0, 0, tzinfo=timezone.utc),
        runtime_metadata_factory=lambda: {
            "python": "typed-production",
            "packages": {
                "numpy": "typed-production",
                "opencv-python-headless": "typed-production",
            },
        },
    )
    payload = service.run(dataset, tmp_path / "result").payload
    assert payload["detector"]["version"] == DETECTOR_VERSION
    assert detector_settings_to_json(settings) == before
    assert payload["detector"]["settings_fingerprint"]
    assert all(item["settings_fingerprint"] for item in payload["cases"])
