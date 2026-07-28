from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields, replace
from threading import Event

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
from oil_tracker.adapters.vision.oil_shadow_temporal import OilShadowTemporalTracker
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
    BoundaryAcceptedDecision,
    EvidenceUnavailableOutcome,
    NoInterfaceOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowUnavailableObservation,
    SuccessfulPipelineFrame,
    TemporalResourceMetrics,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _boundary_image(y: int = 130) -> np.ndarray:
    image = np.full((240, 320), 175, dtype=np.uint8)
    image[y:] = 70
    image[y - 1 : y + 2] = 225
    return image


def _unavailable_image() -> np.ndarray:
    return np.full((240, 320), 255, dtype=np.uint8)


def _inputs(image: np.ndarray):
    mask = np.full(image.shape[:2], 255, dtype=np.uint8)
    pre = preprocess(image, mask, DetectorSettings())
    return pre, mask


def _run(pipeline: OilHypothesisPipeline, image: np.ndarray, glass_id: str):
    pre, mask = _inputs(image)
    return pipeline.run(
        glass_id=glass_id,
        pre=pre,
        effective_mask=mask,
        ellipse_mask=mask,
        exclusion_mask=np.zeros_like(mask),
        static_artifact_map=None,
        crop_origin_y=0.0,
    )


def _raw_frame(image: np.ndarray) -> SuccessfulPipelineFrame:
    pre, mask = _inputs(image)
    bounds = OilHypothesisPipeline().bounds
    raw = extract_raw_observations(pre, mask, crop_origin_y=0.0, bounds=bounds)
    proposals = build_bounded_proposals(raw, bounds)
    hypotheses = evaluate_semantic_hypotheses(
        proposals,
        raw,
        pre,
        mask,
        mask,
        np.zeros_like(mask),
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


def _phase_b_setup():
    pipeline = OilHypothesisPipeline()
    canonical = pipeline._phase_a(_raw_frame(_boundary_image()))
    assert isinstance(canonical.current_observation, ShadowBoundaryObservation)
    snapshot = pipeline.temporal.snapshot("g")
    provisional = pipeline.temporal.evaluate(snapshot, canonical.current_observation)
    assert isinstance(provisional.decision, BoundaryAcceptedDecision)
    return pipeline, canonical, snapshot, provisional


def test_phase_a_valid_evidence_is_fresh_and_canonical():
    pipeline = OilHypothesisPipeline()
    raw = _raw_frame(_boundary_image())
    canonical = pipeline._phase_a(raw)
    assert canonical == raw
    assert canonical is not raw
    assert canonical.raw_observations is not raw.raw_observations
    assert canonical.hypotheses is not raw.hypotheses
    assert isinstance(canonical.current_observation, ShadowBoundaryObservation)
    assert canonical.current_observation.hypothesis in canonical.hypotheses


def test_phase_a_rejects_invalid_outer_shape():
    with pytest.raises(TypeError, match="successful pipeline frame"):
        OilHypothesisPipeline()._phase_a(object())  # type: ignore[arg-type]


def _phase_a_malformed_frames():
    boundary = _raw_frame(_boundary_image())
    raw_identity = replace(boundary.raw_observations[0], identity="e" * 24)
    raw_identity_mismatch = replace(
        boundary,
        raw_observations=(raw_identity,) + boundary.raw_observations[1:],
    )
    raw_source_y = replace(
        boundary.raw_observations[0],
        source_y=boundary.raw_observations[0].source_y + 1.0,
    )
    raw_source_y_mismatch = replace(
        boundary,
        raw_observations=(raw_source_y,) + boundary.raw_observations[1:],
    )
    raw_bound_excess = replace(
        boundary,
        raw_observations=(boundary.raw_observations * 10)[:49],
    )

    proposal = boundary.proposals[0]
    bad_proposal = replace(proposal, identity="f" * 24)
    identity_mismatch = replace(
        boundary,
        proposals=(bad_proposal,) + boundary.proposals[1:],
    )

    hypothesis = boundary.hypotheses[0]
    bad_provenance = replace(
        hypothesis,
        provenance=tuple(sorted(hypothesis.proposal_ids)),
    )
    provenance_mismatch = replace(
        boundary,
        hypotheses=(bad_provenance,) + boundary.hypotheses[1:],
    )

    bad_y = replace(
        hypothesis,
        representative_source_y=hypothesis.representative_source_y + 1.0,
    )
    y_mismatch = replace(
        boundary,
        hypotheses=(bad_y,) + boundary.hypotheses[1:],
    )
    available_count = hypothesis.broad.available_scale_count
    forged_count = (
        available_count - 1
        if available_count == len(hypothesis.broad.scales)
        else available_count + 1
    )
    bad_summary = replace(
        hypothesis,
        broad=replace(
            hypothesis.broad,
            available_scale_count=forged_count,
        ),
    )
    summary_mismatch = replace(
        boundary,
        hypotheses=(bad_summary,) + boundary.hypotheses[1:],
    )

    duplicated = replace(boundary.current_observation)
    object.__setattr__(duplicated, "stored_kind", "boundary")
    duplicate_discriminator = replace(boundary, current_observation=duplicated)

    unsafe = replace(boundary.current_observation)
    object.__setattr__(unsafe, "diagnostics", (("unsafe", object()),))
    unsafe_diagnostics = replace(boundary, current_observation=unsafe)

    no_interface = _raw_frame(np.full((240, 320), 75, dtype=np.uint8))
    assert isinstance(no_interface.current_observation, ShadowNoInterfaceObservation)
    unavailable_evidence = replace(
        no_interface.current_observation.evidence,
        available=False,
        likelihood=0.0,
        full_likelihood=0.0,
        empty_likelihood=0.0,
        region_uniformity=0.0,
        weak_boundary_evidence=0.0,
        competing_boundary_likelihood=0.0,
        visibility=0.0,
        glare_conflict=0.0,
        mean_intensity=None,
        texture=None,
        reason="forged unavailable",
    )
    forged_positive = object.__new__(ShadowNoInterfaceObservation)
    object.__setattr__(forged_positive, "evidence", unavailable_evidence)
    object.__setattr__(forged_positive, "diagnostics", ())
    positive_without_evidence = replace(
        no_interface,
        current_observation=forged_positive,
    )

    ambiguous = _raw_frame(np.full((240, 320), 120, dtype=np.uint8))
    if not isinstance(ambiguous.current_observation, ShadowAmbiguousObservation):
        ambiguous = boundary
        current = ShadowAmbiguousObservation(
            hypothesis_ids=(boundary.hypotheses[0].identity,),
            boundary_likelihood=0.45,
            artifact_likelihood=0.42,
            ambiguity_likelihood=0.8,
            no_interface_likelihood=0.2,
            visibility=0.9,
            projected_source_y=boundary.hypotheses[0].representative_source_y,
            reason="test",
        )
        ambiguous = replace(ambiguous, current_observation=current)
    nonfinite = replace(ambiguous.current_observation)
    object.__setattr__(nonfinite, "projected_source_y", float("nan"))
    nonfinite_scalar = replace(ambiguous, current_observation=nonfinite)

    @dataclass(frozen=True)
    class UnsupportedAmbiguous(ShadowAmbiguousObservation):
        pass

    source = ambiguous.current_observation
    assert isinstance(source, ShadowAmbiguousObservation)
    unsupported = UnsupportedAmbiguous(
        hypothesis_ids=source.hypothesis_ids,
        boundary_likelihood=source.boundary_likelihood,
        artifact_likelihood=source.artifact_likelihood,
        ambiguity_likelihood=source.ambiguity_likelihood,
        no_interface_likelihood=source.no_interface_likelihood,
        visibility=source.visibility,
        projected_source_y=source.projected_source_y,
        reason=source.reason,
        diagnostics=source.diagnostics,
    )
    unsupported_subclass = replace(ambiguous, current_observation=unsupported)

    return {
        "raw identity": raw_identity_mismatch,
        "raw source Y": raw_source_y_mismatch,
        "raw resource bound": raw_bound_excess,
        "proposal identity": identity_mismatch,
        "hypothesis provenance": provenance_mismatch,
        "hypothesis source Y": y_mismatch,
        "hypothesis summary": summary_mismatch,
        "duplicate discriminator": duplicate_discriminator,
        "unsafe diagnostics": unsafe_diagnostics,
        "positive no-interface unavailable": positive_without_evidence,
        "non-finite": nonfinite_scalar,
        "unsupported subclass": unsupported_subclass,
    }


@pytest.mark.parametrize("case", tuple(_phase_a_malformed_frames()))
def test_phase_a_rejects_malformed_evidence_graph(case):
    malformed = _phase_a_malformed_frames()[case]
    with pytest.raises((TypeError, ValueError)):
        OilHypothesisPipeline()._phase_a(malformed)


def test_phase_a_failure_prevents_temporal_evaluation_and_state_creation(monkeypatch):
    class SpyTemporal(OilShadowTemporalTracker):
        calls = 0

        def evaluate(self, snapshot, observation):
            self.calls += 1
            return super().evaluate(snapshot, observation)

    temporal = SpyTemporal()
    pipeline = OilHypothesisPipeline(temporal=temporal)

    def fail(_frame):
        raise ValueError("injected phase A failure")

    monkeypatch.setattr(pipeline, "_phase_a", fail)
    outcome = _run(pipeline, _boundary_image(), "new")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_A
    assert temporal.calls == 0
    assert temporal.state_count == 0


def test_evidence_construction_failure_returns_fresh_failure_without_state(monkeypatch):
    pipeline = OilHypothesisPipeline()

    def fail(*_args, **_kwargs):
        raise RuntimeError("injected evidence construction failure")

    monkeypatch.setattr(pipeline_module, "extract_raw_observations", fail)
    first = _run(pipeline, _boundary_image(), "g")
    second = _run(pipeline, _boundary_image(), "g")
    assert isinstance(first, PipelineFailureOutcome)
    assert isinstance(second, PipelineFailureOutcome)
    assert first is not second
    assert first.stage is PipelineFailureStage.EVIDENCE_CONSTRUCTION
    assert second.stage is PipelineFailureStage.EVIDENCE_CONSTRUCTION
    assert pipeline.temporal_state_count == 0


def test_temporal_evaluation_exception_returns_failure_without_state():
    class FailingTemporal(OilShadowTemporalTracker):
        def evaluate(self, snapshot, observation):
            raise RuntimeError("injected temporal evaluation failure")

    temporal = FailingTemporal()
    pipeline = OilHypothesisPipeline(temporal=temporal)
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.TEMPORAL_EVALUATION
    assert temporal.state_count == 0


def test_phase_b_owner_exception_returns_failure_without_commit(monkeypatch):
    pipeline = OilHypothesisPipeline()

    def fail(*_args, **_kwargs):
        raise RuntimeError("injected phase B owner failure")

    monkeypatch.setattr(pipeline, "_phase_b", fail)
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_B
    assert pipeline.temporal_state_count == 0


def test_forged_provisional_resource_is_rejected_before_commit():
    class ForgingTemporal(OilShadowTemporalTracker):
        def evaluate(self, snapshot, observation):
            result = super().evaluate(snapshot, observation)
            forged = replace(result)
            object.__setattr__(
                forged,
                "resources",
                TemporalResourceMetrics(
                    result.resources.beam_count,
                    result.resources.history_length,
                    result.resources.retained_scalar_count + 1,
                    result.resources.reacquisition_count,
                ),
            )
            return forged

    temporal = ForgingTemporal()
    pipeline = OilHypothesisPipeline(temporal=temporal)
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_B
    assert temporal.state_count == 0


def test_phase_b_rejects_decision_current_mismatch_without_commit():
    pipeline, canonical, snapshot, provisional = _phase_b_setup()
    current = canonical.current_observation
    assert isinstance(current, ShadowBoundaryObservation)
    forged = AmbiguousDecision(
        hypothesis_ids=(current.hypothesis.identity,),
        projected_source_y=current.hypothesis.representative_source_y,
        confidence=0.3,
        decision_margin=0.1,
        reason="forged",
        resources=provisional.resources,
    )
    bad = replace(provisional, decision=forged)
    with pytest.raises(ValueError, match="mismatch"):
        pipeline._phase_b("g", canonical, snapshot, bad)
    assert pipeline.temporal.state_count == 0


def test_phase_b_rejects_selection_content_y_mode_state_and_resources():
    cases = []
    pipeline, canonical, snapshot, provisional = _phase_b_setup()
    decision = provisional.decision
    assert isinstance(decision, BoundaryAcceptedDecision)

    alternate = replace(decision.selected_hypothesis, identity="a" * 24)
    cases.append(replace(provisional, decision=replace(decision, selected_hypothesis=alternate)))
    cases.append(
        replace(
            provisional,
            decision=replace(decision, accepted_source_y=decision.accepted_source_y + 1.0),
        )
    )
    forged_mode = replace(decision)
    object.__setattr__(forged_mode, "acceptance_mode", "forged")
    cases.append(replace(provisional, decision=forged_mode))
    cases.append(replace(provisional, next_state=replace(provisional.next_state, glass_id="other")))
    cases.append(replace(provisional, next_state=replace(provisional.next_state, version=99)))
    forged_resources = replace(provisional)
    object.__setattr__(
        forged_resources,
        "resources",
        TemporalResourceMetrics(
            provisional.resources.beam_count,
            provisional.resources.history_length,
            provisional.resources.retained_scalar_count + 1,
            provisional.resources.reacquisition_count,
        ),
    )
    cases.append(forged_resources)

    for bad in cases:
        with pytest.raises((TypeError, ValueError)):
            pipeline._phase_b("g", canonical, snapshot, bad)
        assert pipeline.temporal.state_count == 0


def test_legal_success_commits_exactly_once_and_reset_is_bounded():
    pipeline = OilHypothesisPipeline()
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, AcceptedBoundaryOutcome)
    snapshot = pipeline.temporal_snapshot("g")
    assert snapshot.version == 1
    assert snapshot.state.last_commit_token
    pipeline.reset("g")
    assert pipeline.temporal_state_count == 0
    pipeline.reset()
    assert pipeline.temporal_state_count == 0


def test_commit_failure_returns_pipeline_failure_and_preserves_prior_state():
    def fail(_snapshot, _state):
        raise RuntimeError("injected commit failure")

    temporal = OilShadowTemporalTracker(commit_hook=fail)
    pipeline = OilHypothesisPipeline(temporal=temporal)
    before = temporal.snapshot("g")
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.COMMIT
    assert temporal.snapshot("g") == before
    assert temporal.state_count == 0


def test_outcome_construction_and_prepared_validation_fail_before_commit():
    def raise_prepare(_frame, _proposal, _resources):
        raise RuntimeError("injected outcome construction failure")

    pipeline = OilHypothesisPipeline(outcome_preparer=raise_prepare)
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.OUTCOME_PREPARATION
    assert pipeline.temporal_state_count == 0

    normal = OilHypothesisPipeline()

    @dataclass(frozen=True)
    class UnsupportedAccepted(AcceptedBoundaryOutcome):
        pass

    def unsupported(frame, proposal, resources):
        prepared = normal._prepare_outcome(frame, proposal, resources)
        assert isinstance(prepared, AcceptedBoundaryOutcome)
        return UnsupportedAccepted(**{
            field.name: getattr(prepared, field.name)
            for field in fields(AcceptedBoundaryOutcome)
        })

    normal._outcome_preparer = unsupported
    outcome = _run(normal, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.OUTCOME_PREPARATION
    assert normal.temporal_state_count == 0


def test_repeated_pipeline_failure_does_not_advance_successful_unavailable_counter(monkeypatch):
    pipeline = OilHypothesisPipeline()
    first = _run(pipeline, _unavailable_image(), "g")
    assert isinstance(first, EvidenceUnavailableOutcome)
    before = pipeline.temporal_snapshot("g")

    original = pipeline._phase_a
    monkeypatch.setattr(
        pipeline,
        "_phase_a",
        lambda _frame: (_ for _ in ()).throw(ValueError("failure")),
    )
    failures = [_run(pipeline, _unavailable_image(), "g") for _ in range(8)]
    assert all(isinstance(item, PipelineFailureOutcome) for item in failures)
    assert pipeline.temporal_snapshot("g") == before

    monkeypatch.setattr(pipeline, "_phase_a", original)
    second = _run(pipeline, _unavailable_image(), "g")
    assert isinstance(second, EvidenceUnavailableOutcome)
    assert pipeline.temporal_snapshot("g").state.unavailable_count == min(
        pipeline.bounds.unavailable_clear_frames,
        before.state.unavailable_count + 1,
    )


def test_one_glass_commit_failure_does_not_affect_another_glass():
    def fail_a(snapshot, _state):
        if snapshot.glass_id == "a":
            raise RuntimeError("glass a failure")

    temporal = OilShadowTemporalTracker(commit_hook=fail_a)
    pipeline = OilHypothesisPipeline(temporal=temporal)
    failed = _run(pipeline, _boundary_image(), "a")
    succeeded = _run(pipeline, _boundary_image(), "b")
    assert isinstance(failed, PipelineFailureOutcome)
    assert isinstance(succeeded, AcceptedBoundaryOutcome)
    assert temporal.snapshot("a").version == 0
    assert temporal.snapshot("b").version == 1
    assert temporal.state_count == 1


def test_same_glass_transaction_serializes_prepare_commit_publish_order():
    entered = Event()
    release = Event()
    second_started = Event()
    pipeline = OilHypothesisPipeline()
    default_prepare = pipeline._prepare_outcome
    prepare_calls = 0

    def blocking_prepare(frame, proposal, resources):
        nonlocal prepare_calls
        prepare_calls += 1
        if prepare_calls == 1:
            entered.set()
            assert release.wait(timeout=5)
        return default_prepare(frame, proposal, resources)

    pipeline._outcome_preparer = blocking_prepare
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(_run, pipeline, _boundary_image(130), "g")
        assert entered.wait(timeout=5)
        second_started.set()
        second = executor.submit(_run, pipeline, _boundary_image(132), "g")
        assert second_started.is_set()
        assert not second.done()
        release.set()
        first_outcome = first.result(timeout=5)
        second_outcome = second.result(timeout=5)
    assert isinstance(first_outcome, AcceptedBoundaryOutcome)
    assert isinstance(second_outcome, AcceptedBoundaryOutcome)
    assert pipeline.temporal_snapshot("g").version == 2


def test_committed_state_is_not_observable_before_outcome_handoff():
    committed = Event()
    release = Event()

    class BlockingCommitTracker(OilShadowTemporalTracker):
        def commit(self, payload):
            result = super().commit(payload)
            committed.set()
            assert release.wait(timeout=5)
            return result

    temporal = BlockingCommitTracker()
    pipeline = OilHypothesisPipeline(temporal=temporal)
    with ThreadPoolExecutor(max_workers=2) as executor:
        operation = executor.submit(_run, pipeline, _boundary_image(), "g")
        assert committed.wait(timeout=5)
        observer = executor.submit(pipeline.temporal_snapshot, "g")
        assert not observer.done()
        release.set()
        outcome = operation.result(timeout=5)
        snapshot = observer.result(timeout=5)
    assert isinstance(outcome, AcceptedBoundaryOutcome)
    assert snapshot.version == 1
