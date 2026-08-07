from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, is_dataclass, replace
from enum import Enum
import inspect
from pathlib import Path
from threading import Event, Lock
import time

import numpy as np
import pytest

from oil_tracker.adapters.vision import oil_shadow_pipeline as pipeline_module
from oil_tracker.adapters.vision.oil_shadow_observations import (
    build_bounded_proposals,
    evaluate_semantic_hypotheses,
    evaluate_typed_current_observation,
    extract_raw_observations,
)
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_temporal import (
    CanonicalTemporalReduction,
    GlassTemporalRecord,
    GlassTemporalState,
    TemporalReentryError,
    TemporalStoreState,
)
from oil_tracker.adapters.vision.oil_shadow_types import (
    AbsenceStabilityMode,
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
    BoundaryAcceptanceMode,
    BoundaryAcceptedDecision,
    EvidenceUnavailableDecision,
    EvidenceUnavailableOutcome,
    NoInterfaceAcceptedDecision,
    NoInterfaceOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
    ReacquisitionPendingDecision,
    ReacquisitionPendingOutcome,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowUnavailableObservation,
    SuccessfulPipelineFrame,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _boundary_image(y: int = 130) -> np.ndarray:
    image = np.full((240, 320), 175, dtype=np.uint8)
    image[y:] = 70
    image[y - 1 : y + 2] = 225
    return image


def _uniform(value: int) -> np.ndarray:
    return np.full((240, 320), value, dtype=np.uint8)


def _kwargs(image: np.ndarray, glass_id: str = "g") -> dict[str, object]:
    mask = np.full(image.shape[:2], 255, dtype=np.uint8)
    return {
        "glass_id": glass_id,
        "pre": preprocess(image, mask, DetectorSettings()),
        "effective_mask": mask,
        "ellipse_mask": mask.copy(),
        "exclusion_mask": np.zeros_like(mask),
        "static_artifact_map": None,
        "crop_origin_y": 0.0,
    }


def _run(pipeline: OilHypothesisPipeline, image: np.ndarray, glass_id: str = "g"):
    return pipeline.run(**_kwargs(image, glass_id))


def _raw_frame(image: np.ndarray) -> SuccessfulPipelineFrame:
    kwargs = _kwargs(image)
    pre = kwargs["pre"]
    mask = kwargs["effective_mask"]
    assert isinstance(pre, object) and isinstance(mask, np.ndarray)
    bounds = OilHypothesisPipeline().bounds
    raw = extract_raw_observations(pre, mask, crop_origin_y=0.0, bounds=bounds)
    proposals = build_bounded_proposals(raw, bounds)
    hypotheses = evaluate_semantic_hypotheses(
        proposals,
        raw,
        pre,
        mask,
        kwargs["ellipse_mask"],
        kwargs["exclusion_mask"],
        None,
        crop_origin_y=0.0,
        bounds=bounds,
    )
    current = evaluate_typed_current_observation(pre, mask, hypotheses)
    return SuccessfulPipelineFrame(
        raw_observations=raw,
        proposals=proposals,
        hypotheses=hypotheses,
        current_observation=current,
        frame_height=image.shape[0],
        frame_width=image.shape[1],
    )


def _reducer(pipeline: OilHypothesisPipeline):
    return getattr(pipeline, "_OilHypothesisPipeline__reducer")


def _ambiguous_frame(
    pipeline: OilHypothesisPipeline,
    frame: SuccessfulPipelineFrame,
    *,
    projected: bool = True,
) -> SuccessfulPipelineFrame:
    assert isinstance(frame.current_observation, ShadowBoundaryObservation)
    hypothesis = frame.current_observation.hypothesis
    current = ShadowAmbiguousObservation(
        hypothesis_ids=(hypothesis.identity,),
        boundary_likelihood=hypothesis.boundary_likelihood,
        artifact_likelihood=hypothesis.artifact_likelihood,
        ambiguity_likelihood=hypothesis.ambiguity_likelihood,
        no_interface_likelihood=0.2,
        visibility=hypothesis.visibility,
        projected_source_y=hypothesis.representative_source_y if projected else None,
        reason="test ambiguity",
    )
    return pipeline._phase_a(replace(frame, current_observation=current))


def _wait_for_assigned(pipeline: OilHypothesisPipeline, count: int) -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if len(pipeline._debug_command_sequences[0]) >= count:
            return
        time.sleep(0.005)
    raise AssertionError(f"only {pipeline._debug_command_sequences[0]} assigned")


def _assert_failure(outcome: object) -> PipelineFailureOutcome:
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.tracker_action.value == "NO_UPDATE"
    assert outcome.smoothing_action.value == "PRESERVE"
    assert not hasattr(outcome, "raw_source_y")
    assert not hasattr(outcome, "selected_hypothesis")
    return outcome


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


def test_phase_a_canonicalizes_fresh_evidence_and_rejects_forgery():
    pipeline = OilHypothesisPipeline()
    raw = _raw_frame(_boundary_image())
    canonical = pipeline._phase_a(raw)
    assert canonical == raw and canonical is not raw
    assert canonical.raw_observations is not raw.raw_observations
    assert canonical.hypotheses is not raw.hypotheses
    forged_raw = replace(raw.raw_observations[0], identity="x" * 24)
    with pytest.raises(ValueError):
        pipeline._phase_a(replace(raw, raw_observations=(forged_raw,) + raw.raw_observations[1:]))
    forged_hypothesis = replace(raw.hypotheses[0], representative_source_y=999.0)
    with pytest.raises(ValueError):
        pipeline._phase_a(replace(raw, hypotheses=(forged_hypothesis,) + raw.hypotheses[1:]))

    hypothesis = raw.hypotheses[0]
    mismatched_ambiguity = 0.0 if hypothesis.ambiguity_likelihood > 0.1 else 1.0
    forged_ambiguous = ShadowAmbiguousObservation(
        hypothesis_ids=(hypothesis.identity,),
        boundary_likelihood=hypothesis.boundary_likelihood,
        artifact_likelihood=hypothesis.artifact_likelihood,
        ambiguity_likelihood=mismatched_ambiguity,
        no_interface_likelihood=0.2,
        visibility=hypothesis.visibility,
        projected_source_y=hypothesis.representative_source_y,
        reason="forged cross-field mismatch",
    )
    with pytest.raises(
        ValueError,
        match="Ambiguous likelihoods disagree with canonical evidence",
    ):
        pipeline._phase_a(replace(raw, current_observation=forged_ambiguous))


def test_immutable_input_preparation_owns_independent_readonly_arrays():
    pipeline = OilHypothesisPipeline()
    kwargs = _kwargs(_boundary_image())
    command = pipeline._prepare_run_command(**kwargs)
    payload = command.payload
    prepared = (
        payload.pre.gray,
        payload.pre.normalized,
        payload.pre.blurred,
        payload.pre.sobel_y_signed,
        payload.pre.sobel_y_abs,
        payload.pre.canny,
        payload.pre.horizontal_mask,
        payload.pre.glare_mask,
        payload.effective_mask,
        payload.ellipse_mask,
        payload.exclusion_mask,
    )
    originals = (
        kwargs["pre"].gray,
        kwargs["pre"].normalized,
        kwargs["pre"].blurred,
        kwargs["pre"].sobel_y_signed,
        kwargs["pre"].sobel_y_abs,
        kwargs["pre"].canny,
        kwargs["pre"].horizontal_mask,
        kwargs["pre"].glare_mask,
        kwargs["effective_mask"],
        kwargs["ellipse_mask"],
        kwargs["exclusion_mask"],
    )
    assert all(not item.flags.writeable for item in prepared)
    assert all(not np.shares_memory(left, right) for left, right in zip(prepared, originals))
    assert len({item.__array_interface__["data"][0] for item in prepared}) == len(prepared)


def test_concurrent_commands_execute_in_assigned_total_order():
    pipeline = OilHypothesisPipeline()
    entered = Event()
    release = Event()
    original = pipeline._phase_a
    calls = 0

    def block_first(frame):
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            assert release.wait(timeout=5)
        return original(frame)

    pipeline._phase_a = block_first
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(_run, pipeline, _boundary_image(130), "a")
        assert entered.wait(timeout=5)
        second = executor.submit(_run, pipeline, _boundary_image(145), "b")
        _wait_for_assigned(pipeline, 2)
        assigned, executed = pipeline._debug_command_sequences
        assert assigned == (0, 1)
        assert executed == (0,)
        release.set()
        assert isinstance(first.result(timeout=5), AcceptedBoundaryOutcome)
        assert isinstance(second.result(timeout=5), AcceptedBoundaryOutcome)
    assert pipeline._debug_command_sequences == ((0, 1), (0, 1))
    assert pipeline.temporal_snapshot("a").version == 1
    assert pipeline.temporal_snapshot("b").version == 1


def test_different_glasses_never_reduce_temporal_state_simultaneously(monkeypatch):
    pipeline = OilHypothesisPipeline()
    reducer_type = type(_reducer(pipeline))
    original = reducer_type.reduce
    first_entered = Event()
    release = Event()
    guard = Lock()
    active = 0
    maximum = 0
    calls = 0

    def observed(self, record, frame):
        nonlocal active, maximum, calls
        with guard:
            active += 1
            maximum = max(maximum, active)
            calls += 1
            current = calls
        if current == 1:
            first_entered.set()
            assert release.wait(timeout=5)
        try:
            return original(self, record, frame)
        finally:
            with guard:
                active -= 1

    monkeypatch.setattr(reducer_type, "reduce", observed)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(_run, pipeline, _boundary_image(130), "a")
        assert first_entered.wait(timeout=5)
        second = executor.submit(_run, pipeline, _boundary_image(145), "b")
        _wait_for_assigned(pipeline, 2)
        time.sleep(0.05)
        assert calls == 1 and maximum == 1
        release.set()
        first.result(timeout=5)
        second.result(timeout=5)
    assert maximum == 1


def test_failed_command_does_not_stop_following_command():
    pipeline = OilHypothesisPipeline()
    original = pipeline._phase_a
    calls = 0

    def fail_once(frame):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("injected first-command failure")
        return original(frame)

    pipeline._phase_a = fail_once
    first = _assert_failure(_run(pipeline, _boundary_image(130), "g"))
    second = _run(pipeline, _boundary_image(132), "g")
    assert first.stage is PipelineFailureStage.PHASE_A
    assert isinstance(second, AcceptedBoundaryOutcome)
    assert pipeline._debug_command_sequences == ((0, 1), (0, 1))
    assert pipeline.temporal_snapshot("g").version == 1


def test_snapshot_and_count_observe_their_sequence_position():
    pipeline = OilHypothesisPipeline()
    entered = Event()
    release = Event()
    original = pipeline._phase_a

    def block(frame):
        entered.set()
        assert release.wait(timeout=5)
        return original(frame)

    pipeline._phase_a = block
    with ThreadPoolExecutor(max_workers=3) as executor:
        run = executor.submit(_run, pipeline, _boundary_image(), "g")
        assert entered.wait(timeout=5)
        snapshot = executor.submit(pipeline.temporal_snapshot, "g")
        _wait_for_assigned(pipeline, 2)
        count = executor.submit(lambda: pipeline.temporal_state_count)
        _wait_for_assigned(pipeline, 3)
        release.set()
        assert isinstance(run.result(timeout=5), AcceptedBoundaryOutcome)
        assert snapshot.result(timeout=5).version == 1
        assert count.result(timeout=5) == 1
    assert pipeline._debug_command_sequences == ((0, 1, 2), (0, 1, 2))


def test_reset_ordering_matrix_and_version_restart():
    pipeline = OilHypothesisPipeline()
    assert isinstance(_run(pipeline, _boundary_image(), "a"), AcceptedBoundaryOutcome)
    pipeline.reset("a")
    assert pipeline.temporal_snapshot("a").version == 0
    assert isinstance(_run(pipeline, _boundary_image(132), "a"), AcceptedBoundaryOutcome)
    assert pipeline.temporal_snapshot("a").version == 1
    pipeline.reset("a")
    assert isinstance(_run(pipeline, _boundary_image(134), "a"), AcceptedBoundaryOutcome)
    assert pipeline.temporal_snapshot("a").version == 1
    pipeline.reset()
    assert isinstance(_run(pipeline, _boundary_image(145), "b"), AcceptedBoundaryOutcome)
    assert pipeline.temporal_state_count == 1
    assert pipeline.temporal_snapshot("a").version == 0
    assert pipeline.temporal_snapshot("b").version == 1


def test_single_replacement_missing_reads_and_untargeted_identity():
    pipeline = OilHypothesisPipeline()
    initial_store = pipeline._debug_store_reference
    initial_count = pipeline._debug_store_replacement_count
    missing = pipeline.temporal_snapshot("missing")
    assert missing.version == 0 and pipeline.temporal_state_count == 0
    assert pipeline._debug_store_reference is initial_store
    assert pipeline._debug_store_replacement_count == initial_count

    _run(pipeline, _boundary_image(130), "a")
    store_a = pipeline._debug_store_reference
    assert store_a is not initial_store
    assert pipeline._debug_store_replacement_count == initial_count + 1
    record_a = store_a.records["a"]

    _run(pipeline, _boundary_image(145), "b")
    store_b = pipeline._debug_store_reference
    assert store_b.records["a"] is record_a
    assert pipeline._debug_store_replacement_count == initial_count + 2

    pipeline.reset("b")
    store_reset = pipeline._debug_store_reference
    assert store_reset.records["a"] is record_a
    assert "b" not in store_reset.records
    assert pipeline._debug_store_replacement_count == initial_count + 3


@pytest.mark.parametrize(
    ("point", "expected_stage"),
    (
        ("preparation", PipelineFailureStage.EXTERNAL_RUNNER),
        ("evidence", PipelineFailureStage.EVIDENCE_CONSTRUCTION),
        ("evidence_validation", PipelineFailureStage.PHASE_A),
        ("reducer", PipelineFailureStage.TEMPORAL_EVALUATION),
        ("reduction_value", PipelineFailureStage.TEMPORAL_EVALUATION),
        ("reduction_validation", PipelineFailureStage.PHASE_B),
        ("store_construction", PipelineFailureStage.OUTCOME_PREPARATION),
        ("store_validation", PipelineFailureStage.OUTCOME_PREPARATION),
    ),
)
def test_pre_replacement_failure_points_preserve_exact_store(monkeypatch, point, expected_stage):
    pipeline = OilHypothesisPipeline()
    before = pipeline._debug_store_reference
    replacements = pipeline._debug_store_replacement_count
    before_sequences = pipeline._debug_command_sequences

    def fail(*_args, **_kwargs):
        raise RuntimeError(f"injected {point} failure")

    if point == "preparation":
        monkeypatch.setattr(pipeline, "_prepare_run_command", fail)
    elif point == "evidence":
        monkeypatch.setattr(pipeline_module, "extract_raw_observations", fail)
    elif point == "evidence_validation":
        monkeypatch.setattr(pipeline, "_phase_a", fail)
    elif point == "reducer":
        monkeypatch.setattr(_reducer(pipeline), "reduce", fail)
    elif point == "reduction_value":
        monkeypatch.setattr(pipeline_module, "CanonicalTemporalReduction", fail)
    elif point == "reduction_validation":
        monkeypatch.setattr(pipeline, "_validate_reduction", fail)
    elif point == "store_construction":
        monkeypatch.setattr(pipeline, "_prepare_run_store", fail)
    else:
        monkeypatch.setattr(pipeline, "_validate_prepared_run_store", fail)

    outcome = _assert_failure(_run(pipeline, _boundary_image(), "g"))
    assert outcome.stage is expected_stage
    assert pipeline._debug_store_reference is before
    assert pipeline._debug_store_replacement_count == replacements
    if point == "preparation":
        assert pipeline._debug_command_sequences == before_sequences


def test_pipeline_failure_does_not_advance_successful_absence_counters(monkeypatch):
    pipeline = OilHypothesisPipeline()
    first = _run(pipeline, _uniform(255), "g")
    assert isinstance(first, EvidenceUnavailableOutcome)
    before_store = pipeline._debug_store_reference
    before = pipeline.temporal_snapshot("g")
    original = pipeline._phase_a
    monkeypatch.setattr(
        pipeline,
        "_phase_a",
        lambda _frame: (_ for _ in ()).throw(RuntimeError("injected validation failure")),
    )
    for _ in range(4):
        _assert_failure(_run(pipeline, _uniform(255), "g"))
        assert pipeline._debug_store_reference is before_store
        assert pipeline.temporal_snapshot("g") == before
    monkeypatch.setattr(pipeline, "_phase_a", original)
    second = _run(pipeline, _uniform(255), "g")
    assert isinstance(second, EvidenceUnavailableOutcome)
    assert pipeline.temporal_snapshot("g").state.unavailable_count == min(
        pipeline.bounds.unavailable_clear_frames,
        before.state.unavailable_count + 1,
    )


def test_fixed_reducer_complete_variant_coherence():
    pipeline = OilHypothesisPipeline()
    reducer = _reducer(pipeline)
    boundary_a = pipeline._phase_a(_raw_frame(_boundary_image(130)))
    boundary_far = pipeline._phase_a(_raw_frame(_boundary_image(200)))
    boundary_reacquired = pipeline._phase_a(_raw_frame(_boundary_image(198)))
    no_interface = pipeline._phase_a(_raw_frame(_uniform(75)))
    unavailable = pipeline._phase_a(_raw_frame(_uniform(255)))

    record = GlassTemporalRecord.initial("g")
    initial = reducer.reduce(record, boundary_a)
    continuous = reducer.reduce(initial.next_record, boundary_a)
    pending = reducer.reduce(continuous.next_record, boundary_far)
    reacquired = reducer.reduce(pending.next_record, boundary_reacquired)
    no_pending = reducer.reduce(initial.next_record, no_interface)
    no_record = no_pending.next_record
    for _ in range(pipeline.bounds.no_interface_clear_frames - 1):
        no_pending = reducer.reduce(no_record, no_interface)
        no_record = no_pending.next_record
    unavailable_pending = reducer.reduce(initial.next_record, unavailable)
    unavailable_record = unavailable_pending.next_record
    for _ in range(pipeline.bounds.unavailable_clear_frames - 1):
        unavailable_pending = reducer.reduce(unavailable_record, unavailable)
        unavailable_record = unavailable_pending.next_record

    hypothesis = boundary_a.hypotheses[0]
    ambiguous_current = ShadowAmbiguousObservation(
        hypothesis_ids=(hypothesis.identity,),
        boundary_likelihood=hypothesis.boundary_likelihood,
        artifact_likelihood=hypothesis.artifact_likelihood,
        ambiguity_likelihood=hypothesis.ambiguity_likelihood,
        no_interface_likelihood=0.2,
        visibility=hypothesis.visibility,
        projected_source_y=hypothesis.representative_source_y,
        reason="test ambiguity",
    )
    ambiguous_frame = pipeline._phase_a(
        replace(boundary_a, current_observation=ambiguous_current)
    )
    ambiguous = reducer.reduce(initial.next_record, ambiguous_frame)

    assert isinstance(initial.decision, BoundaryAcceptedDecision)
    assert initial.decision.acceptance_mode is BoundaryAcceptanceMode.INITIAL
    assert isinstance(continuous.decision, BoundaryAcceptedDecision)
    assert continuous.decision.acceptance_mode is BoundaryAcceptanceMode.CONTINUOUS
    assert isinstance(pending.decision, ReacquisitionPendingDecision)
    assert isinstance(pending.outcome, ReacquisitionPendingOutcome)
    assert pending.next_record.temporal_state.pending_y == pending.outcome.pending_hypothesis.representative_source_y
    assert isinstance(reacquired.outcome, AcceptedBoundaryOutcome)
    assert reacquired.outcome.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED
    assert reacquired.next_record.temporal_state.accepted_y == reacquired.outcome.raw_source_y
    assert reacquired.next_record.temporal_state.accepted_velocity is None
    assert isinstance(no_pending.decision, NoInterfaceAcceptedDecision)
    assert no_pending.decision.stability_mode is AbsenceStabilityMode.STABLE
    assert isinstance(no_pending.outcome, NoInterfaceOutcome)
    assert no_pending.outcome.smoothing_action.value == "CLEAR_STALE_AFTER_STABLE_ABSENCE"
    assert isinstance(unavailable_pending.decision, EvidenceUnavailableDecision)
    assert unavailable_pending.decision.stability_mode is AbsenceStabilityMode.STABLE
    assert isinstance(unavailable_pending.outcome, EvidenceUnavailableOutcome)
    assert isinstance(ambiguous.decision, AmbiguousDecision)
    assert isinstance(ambiguous.outcome, AmbiguousOutcome)
    assert ambiguous.next_record.temporal_state.accepted_y == initial.next_record.temporal_state.accepted_y
    for reduction in (
        initial, continuous, pending, reacquired, no_pending,
        unavailable_pending, ambiguous,
    ):
        assert isinstance(reduction, CanonicalTemporalReduction)
        assert reduction.decision.tracker_action is reduction.outcome.tracker_action
        assert reduction.decision.smoothing_action is reduction.outcome.smoothing_action
        assert reduction.resource_metrics == reduction.outcome.resources


def test_compatible_ambiguity_preserves_pending_without_confirming_it():
    pipeline = OilHypothesisPipeline()
    reducer = _reducer(pipeline)
    initial_frame = pipeline._phase_a(_raw_frame(_boundary_image(130)))
    pending_frame = pipeline._phase_a(_raw_frame(_boundary_image(200)))
    followup_frame = pipeline._phase_a(_raw_frame(_boundary_image(198)))

    initial = reducer.reduce(GlassTemporalRecord.initial("g"), initial_frame)
    pending = reducer.reduce(initial.next_record, pending_frame)
    ambiguous_frame = _ambiguous_frame(pipeline, pending_frame)
    ambiguous = reducer.reduce(pending.next_record, ambiguous_frame)

    assert isinstance(pending.outcome, ReacquisitionPendingOutcome)
    assert isinstance(ambiguous.outcome, AmbiguousOutcome)
    assert ambiguous.outcome.tracker_action.value == "NO_UPDATE"
    assert not hasattr(ambiguous.outcome, "raw_source_y")
    assert ambiguous.next_record.temporal_state.pending_y == pending.next_record.temporal_state.pending_y
    assert ambiguous.next_record.temporal_state.pending_velocity == pending.next_record.temporal_state.pending_velocity
    assert ambiguous.next_record.temporal_state.pending_count == pending.next_record.temporal_state.pending_count == 1
    pipeline._validate_reduction(ambiguous_frame, pending.next_record, ambiguous)

    reacquired = reducer.reduce(ambiguous.next_record, followup_frame)
    assert isinstance(reacquired.outcome, AcceptedBoundaryOutcome)
    assert reacquired.outcome.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED


def test_incompatible_or_unprojected_ambiguity_clears_pending():
    pipeline = OilHypothesisPipeline()
    reducer = _reducer(pipeline)
    initial_frame = pipeline._phase_a(_raw_frame(_boundary_image(130)))
    pending_frame = pipeline._phase_a(_raw_frame(_boundary_image(200)))
    incompatible_frame = _ambiguous_frame(pipeline, initial_frame)
    unprojected_frame = _ambiguous_frame(pipeline, pending_frame, projected=False)

    for ambiguous_frame in (incompatible_frame, unprojected_frame):
        initial = reducer.reduce(GlassTemporalRecord.initial("g"), initial_frame)
        pending = reducer.reduce(initial.next_record, pending_frame)
        ambiguous = reducer.reduce(pending.next_record, ambiguous_frame)
        state = ambiguous.next_record.temporal_state
        assert isinstance(ambiguous.outcome, AmbiguousOutcome)
        assert state.pending_y is None
        assert state.pending_velocity is None
        assert state.pending_count == 0
        pipeline._validate_reduction(ambiguous_frame, pending.next_record, ambiguous)


def test_no_interface_and_unavailable_still_clear_pending_reacquisition():
    pipeline = OilHypothesisPipeline()
    reducer = _reducer(pipeline)
    initial_frame = pipeline._phase_a(_raw_frame(_boundary_image(130)))
    pending_frame = pipeline._phase_a(_raw_frame(_boundary_image(200)))
    no_interface = pipeline._phase_a(_raw_frame(_uniform(75)))
    unavailable = pipeline._phase_a(_raw_frame(_uniform(255)))

    for absence_frame in (no_interface, unavailable):
        initial = reducer.reduce(GlassTemporalRecord.initial("g"), initial_frame)
        pending = reducer.reduce(initial.next_record, pending_frame)
        reduced = reducer.reduce(pending.next_record, absence_frame)
        state = reduced.next_record.temporal_state
        assert state.pending_y is None
        assert state.pending_velocity is None
        assert state.pending_count == 0
        pipeline._validate_reduction(absence_frame, pending.next_record, reduced)


def test_transition_coherence_rejects_illegal_ambiguous_pending_retention():
    pipeline = OilHypothesisPipeline()
    reducer = _reducer(pipeline)
    initial_frame = pipeline._phase_a(_raw_frame(_boundary_image(130)))
    pending_frame = pipeline._phase_a(_raw_frame(_boundary_image(200)))
    incompatible_frame = _ambiguous_frame(pipeline, initial_frame)
    initial = reducer.reduce(GlassTemporalRecord.initial("g"), initial_frame)
    pending = reducer.reduce(initial.next_record, pending_frame)
    ambiguous = reducer.reduce(pending.next_record, incompatible_frame)

    forged = replace(
        ambiguous.next_record.temporal_state,
        pending_y=pending.next_record.temporal_state.pending_y,
        pending_velocity=pending.next_record.temporal_state.pending_velocity,
        pending_count=pending.next_record.temporal_state.pending_count,
    )
    with pytest.raises(ValueError, match="incompatible pending path"):
        pipeline._validate_transition_coherence(pending.next_record, ambiguous.decision, forged)

    compatible_frame = _ambiguous_frame(pipeline, pending_frame)
    compatible = reducer.reduce(pending.next_record, compatible_frame)
    advanced = replace(compatible.next_record.temporal_state, pending_count=2)
    with pytest.raises(ValueError, match="advanced or changed pending state"):
        pipeline._validate_transition_coherence(pending.next_record, compatible.decision, advanced)


def test_active_owner_reentry_is_rejected_before_enqueue_and_owner_continues(monkeypatch):
    pipeline = OilHypothesisPipeline()
    original = pipeline._phase_a
    nested: list[PipelineFailureOutcome] = []
    nested_kwargs = _kwargs(_boundary_image(132), "nested")

    def reenter_run(frame):
        nested.append(_assert_failure(pipeline.run(**nested_kwargs)))
        return original(frame)

    monkeypatch.setattr(pipeline, "_phase_a", reenter_run)
    outer = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outer, AcceptedBoundaryOutcome)
    assert nested[0].reason == "temporal_reentry_rejected"
    assert pipeline._debug_command_sequences == ((0,), (0,))
    assert pipeline.temporal_state_count == 1

    for operation in (
        lambda: pipeline.reset(),
        lambda: pipeline.temporal_snapshot("g"),
        lambda: pipeline.temporal_state_count,
    ):
        monkeypatch.setattr(pipeline, "_phase_a", lambda _frame, op=operation: op())
        failed = _assert_failure(_run(pipeline, _boundary_image(134), "g"))
        assert failed.stage is PipelineFailureStage.PHASE_A
        assert "TemporalReentryError" in failed.reason
        monkeypatch.setattr(pipeline, "_phase_a", original)
        assert isinstance(_run(pipeline, _boundary_image(136), "g"), AcceptedBoundaryOutcome)


def test_store_is_immutable_complete_and_contains_no_raster():
    pipeline = OilHypothesisPipeline()
    _run(pipeline, _boundary_image(), "g")
    store = pipeline._debug_store_reference
    assert type(store) is TemporalStoreState
    assert type(store.records).__name__ == "mappingproxy"
    record = store.records["g"]
    assert type(record) is GlassTemporalRecord
    assert record.version == 1 and record.temporal_state.glass_id == "g"
    with pytest.raises(TypeError):
        store.records["x"] = GlassTemporalRecord.initial("x")  # type: ignore[index]
    _assert_no_raster(store)


def test_obsolete_transaction_and_parallel_mutation_surface_is_absent():
    source_root = Path(pipeline_module.__file__).parent
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            source_root / "oil_shadow_pipeline.py",
            source_root / "oil_shadow_temporal.py",
            source_root / "opencv_phase_detector.py",
            source_root / "oil_hypothesis_projection.py",
        )
    )
    for token in (
        "_LifecycleBarrier",
        "GlassTemporalSnapshot",
        "TemporalCommitError",
        "reset_generation",
        "commit_token",
        "__locks",
        "__states",
        "__versions",
        "validate_production_result",
        "last_commit_token",
    ):
        assert token not in source
    assert "different glass transactions remain parallel" not in source.lower()
    assert not hasattr(pipeline_module, "OilShadowTemporalModel")
    assert set(inspect.signature(OilHypothesisPipeline).parameters) == {"bounds"}
    pipeline = OilHypothesisPipeline()
    for name in ("commit", "execute", "evaluate", "session"):
        assert not hasattr(pipeline, name)


@pytest.mark.parametrize(
    "variant",
    (
        "initial_boundary",
        "continuous_boundary",
        "reacquired_boundary",
        "reacquisition_pending",
        "no_interface_pending",
        "no_interface_stable",
        "unavailable_pending",
        "unavailable_stable",
        "ambiguous",
    ),
)
def test_each_reducer_variant_failure_preserves_exact_prior_store(
    monkeypatch,
    variant: str,
):
    pipeline = OilHypothesisPipeline()
    target_image = _boundary_image(130)
    expected_type: type[object] = AcceptedBoundaryOutcome
    expected_mode = None

    if variant == "initial_boundary":
        expected_mode = BoundaryAcceptanceMode.INITIAL
    elif variant == "continuous_boundary":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        target_image = _boundary_image(132)
        expected_mode = BoundaryAcceptanceMode.CONTINUOUS
    elif variant == "reacquisition_pending":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        target_image = _boundary_image(200)
        expected_type = ReacquisitionPendingOutcome
    elif variant == "reacquired_boundary":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        assert isinstance(
            _run(pipeline, _boundary_image(200)), ReacquisitionPendingOutcome
        )
        target_image = _boundary_image(198)
        expected_mode = BoundaryAcceptanceMode.REACQUIRED
    elif variant == "no_interface_pending":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        target_image = _uniform(75)
        expected_type = NoInterfaceOutcome
        expected_mode = AbsenceStabilityMode.PENDING
    elif variant == "no_interface_stable":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        assert isinstance(_run(pipeline, _uniform(75)), NoInterfaceOutcome)
        target_image = _uniform(75)
        expected_type = NoInterfaceOutcome
        expected_mode = AbsenceStabilityMode.STABLE
    elif variant == "unavailable_pending":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        target_image = _uniform(255)
        expected_type = EvidenceUnavailableOutcome
        expected_mode = AbsenceStabilityMode.PENDING
    elif variant == "unavailable_stable":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        for _ in range(pipeline.bounds.unavailable_clear_frames - 1):
            assert isinstance(_run(pipeline, _uniform(255)), EvidenceUnavailableOutcome)
        target_image = _uniform(255)
        expected_type = EvidenceUnavailableOutcome
        expected_mode = AbsenceStabilityMode.STABLE
    elif variant == "ambiguous":
        assert isinstance(_run(pipeline, _boundary_image(130)), AcceptedBoundaryOutcome)
        expected_type = AmbiguousOutcome

        def ambiguous_current(_pre, _mask, hypotheses):
            hypothesis = hypotheses[0]
            return ShadowAmbiguousObservation(
                hypothesis_ids=(hypothesis.identity,),
                boundary_likelihood=hypothesis.boundary_likelihood,
                artifact_likelihood=hypothesis.artifact_likelihood,
                ambiguity_likelihood=hypothesis.ambiguity_likelihood,
                no_interface_likelihood=0.0,
                visibility=hypothesis.visibility,
                projected_source_y=hypothesis.representative_source_y,
                reason="injected canonical ambiguity",
            )

        monkeypatch.setattr(
            pipeline_module,
            "evaluate_typed_current_observation",
            ambiguous_current,
        )
    else:
        raise AssertionError(variant)

    reducer = _reducer(pipeline)
    original = reducer.reduce

    def fail_after_variant(prior_record, frame):
        reduction = original(prior_record, frame)
        assert isinstance(reduction.outcome, expected_type)
        if expected_mode is not None:
            actual_mode = getattr(
                reduction.outcome,
                "acceptance_mode",
                getattr(reduction.outcome, "stability_mode", None),
            )
            assert actual_mode is expected_mode
        raise RuntimeError(f"injected {variant} reducer failure")

    monkeypatch.setattr(reducer, "reduce", fail_after_variant)
    before_store = pipeline._debug_store_reference
    before_replacements = pipeline._debug_store_replacement_count
    outcome = _assert_failure(_run(pipeline, target_image))
    assert outcome.stage is PipelineFailureStage.TEMPORAL_EVALUATION
    assert pipeline._debug_store_reference is before_store
    assert pipeline._debug_store_replacement_count == before_replacements


def test_failed_reset_replaces_nothing_and_does_not_stop_owner_queue(monkeypatch):
    pipeline = OilHypothesisPipeline()
    assert isinstance(_run(pipeline, _boundary_image(130), "a"), AcceptedBoundaryOutcome)
    assert isinstance(_run(pipeline, _boundary_image(145), "b"), AcceptedBoundaryOutcome)
    before_store = pipeline._debug_store_reference
    record_a = before_store.records["a"]
    record_b = before_store.records["b"]
    before_replacements = pipeline._debug_store_replacement_count

    original = pipeline._validate_prepared_reset_store
    monkeypatch.setattr(
        pipeline,
        "_validate_prepared_reset_store",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("injected reset validation")),
    )
    with pytest.raises(RuntimeError, match="injected reset validation"):
        pipeline.reset("a")
    assert pipeline._debug_store_reference is before_store
    assert pipeline._debug_store_replacement_count == before_replacements

    monkeypatch.setattr(pipeline, "_validate_prepared_reset_store", original)
    snapshot = pipeline.temporal_snapshot("a")
    assert snapshot.version == 1
    assert pipeline.temporal_state_count == 2
    assert isinstance(_run(pipeline, _boundary_image(147), "b"), AcceptedBoundaryOutcome)
    assert pipeline._debug_store_reference.records["a"] is record_a
    assert pipeline._debug_store_reference.records["b"] is not record_b


def test_each_reset_performs_one_replacement_and_preserves_untargeted_record_identity():
    pipeline = OilHypothesisPipeline()
    _run(pipeline, _boundary_image(130), "a")
    _run(pipeline, _boundary_image(145), "b")
    before = pipeline._debug_store_reference
    record_b = before.records["b"]
    replacements = pipeline._debug_store_replacement_count

    pipeline.reset("a")
    local = pipeline._debug_store_reference
    assert local is not before
    assert local.records["b"] is record_b
    assert pipeline._debug_store_replacement_count == replacements + 1
    assert pipeline.temporal_snapshot("a").version == 0
    assert pipeline.temporal_state_count == 1

    replacements = pipeline._debug_store_replacement_count
    pipeline.reset()
    global_store = pipeline._debug_store_reference
    assert not global_store.records
    assert pipeline._debug_store_replacement_count == replacements + 1
    assert pipeline.temporal_state_count == 0
