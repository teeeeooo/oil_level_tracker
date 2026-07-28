from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum

import numpy as np

from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_temporal import (
    GlassTemporalRecord,
    GlassTemporalState,
    TemporalStoreState,
)
from oil_tracker.adapters.vision.oil_shadow_types import (
    AbsenceStabilityMode,
    AcceptedBoundaryOutcome,
    BoundaryAcceptanceMode,
    EvidenceUnavailableOutcome,
    NoInterfaceOutcome,
    OilShadowBounds,
    PipelineFailureOutcome,
    ReacquisitionPendingOutcome,
    SmoothingAction,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _boundary(y: int) -> np.ndarray:
    image = np.full((240, 320), 175, dtype=np.uint8)
    image[y:] = 70
    image[y - 1 : y + 2] = 225
    return image


def _uniform(value: int) -> np.ndarray:
    return np.full((240, 320), value, dtype=np.uint8)


def _run(pipeline: OilHypothesisPipeline, image: np.ndarray, glass_id: str = "g"):
    mask = np.full(image.shape, 255, dtype=np.uint8)
    return pipeline.run(
        glass_id=glass_id,
        pre=preprocess(image, mask, DetectorSettings()),
        effective_mask=mask,
        ellipse_mask=mask,
        exclusion_mask=np.zeros_like(mask),
        static_artifact_map=None,
        crop_origin_y=0.0,
    )


def _assert_no_raster(value: object) -> None:
    if isinstance(value, np.ndarray):
        raise AssertionError("temporal truth retained a raster")
    if isinstance(value, (str, int, float, bool, type(None), Enum)):
        return
    if isinstance(value, tuple):
        for item in value:
            _assert_no_raster(item)
        return
    if isinstance(value, dict) or type(value).__name__ == "mappingproxy":
        for item in value.values():
            _assert_no_raster(item)
        return
    if is_dataclass(value):
        for field in fields(value):
            _assert_no_raster(getattr(value, field.name))
        return
    raise AssertionError(type(value))


def test_missing_record_is_canonical_initial_and_read_does_not_insert():
    pipeline = OilHypothesisPipeline()
    before = pipeline._debug_store_reference
    snapshot = pipeline.temporal_snapshot("g")
    assert snapshot.version == 0
    assert snapshot.state == GlassTemporalState("g")
    assert pipeline.temporal_state_count == 0
    assert pipeline._debug_store_reference is before
    assert before == TemporalStoreState({})
    assert GlassTemporalRecord.initial("g").version == 0


def test_successful_temporal_mathematics_are_preserved_by_fixed_reducer():
    pipeline = OilHypothesisPipeline()
    initial = _run(pipeline, _boundary(130))
    continuous = _run(pipeline, _boundary(132))
    pending = _run(pipeline, _boundary(200))
    reacquired = _run(pipeline, _boundary(198))

    assert isinstance(initial, AcceptedBoundaryOutcome)
    assert initial.acceptance_mode is BoundaryAcceptanceMode.INITIAL
    assert isinstance(continuous, AcceptedBoundaryOutcome)
    assert continuous.acceptance_mode is BoundaryAcceptanceMode.CONTINUOUS
    assert pipeline.temporal_snapshot("g").version == 4
    assert isinstance(pending, ReacquisitionPendingOutcome)
    assert isinstance(reacquired, AcceptedBoundaryOutcome)
    assert reacquired.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED
    assert reacquired.smoothing_action is SmoothingAction.CLEAR_BEFORE_ACCEPT
    snapshot = pipeline.temporal_snapshot("g")
    assert snapshot.state.accepted_y == reacquired.raw_source_y
    assert snapshot.state.accepted_velocity is None
    assert snapshot.state.pending_y is None
    assert snapshot.state.pending_count == 0


def test_unavailable_and_no_interface_counters_remain_bounded():
    bounds = OilShadowBounds(unavailable_clear_frames=3, no_interface_clear_frames=2)
    pipeline = OilHypothesisPipeline(bounds)
    assert isinstance(_run(pipeline, _boundary(130)), AcceptedBoundaryOutcome)

    unavailable = [_run(pipeline, _uniform(255)) for _ in range(8)]
    assert all(isinstance(item, EvidenceUnavailableOutcome) for item in unavailable)
    assert unavailable[0].stability_mode is AbsenceStabilityMode.PENDING
    assert unavailable[2].stability_mode is AbsenceStabilityMode.STABLE
    assert unavailable[-1].smoothing_action is SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE
    assert pipeline.temporal_snapshot("g").state.unavailable_count == 3

    pipeline.reset("g")
    no_interface = [_run(pipeline, _uniform(75)) for _ in range(8)]
    assert all(isinstance(item, NoInterfaceOutcome) for item in no_interface)
    assert no_interface[0].stability_mode is AbsenceStabilityMode.PENDING
    assert no_interface[1].stability_mode is AbsenceStabilityMode.STABLE
    assert pipeline.temporal_snapshot("g").state.no_interface_count == 2


def test_temporal_resources_are_bounded_and_store_retains_no_raster():
    bounds = OilShadowBounds(temporal_beam_width=3, temporal_history_window=4)
    pipeline = OilHypothesisPipeline(bounds)
    sequence = (
        _boundary(130),
        _boundary(132),
        _boundary(200),
        _uniform(255),
        _uniform(75),
    )
    for index in range(30):
        outcome = _run(pipeline, sequence[index % len(sequence)])
        assert not isinstance(outcome, PipelineFailureOutcome)
        resources = outcome.resources
        assert resources.temporal_beam_count <= bounds.temporal_beam_width
        assert resources.temporal_history_length <= bounds.temporal_history_window
        assert resources.retained_temporal_scalar_count <= resources.retained_temporal_scalar_limit
    _assert_no_raster(pipeline._debug_store_reference)
