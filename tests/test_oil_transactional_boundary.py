from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields, replace
import inspect
from threading import Barrier, Event, RLock

import numpy as np
import pytest

from oil_tracker.adapters.vision import oil_shadow_pipeline as pipeline_module
from oil_tracker.adapters.vision import oil_shadow_temporal as temporal_module
from oil_tracker.adapters.vision.oil_shadow_observations import (
    build_bounded_proposals,
    evaluate_semantic_hypotheses,
    evaluate_typed_current_observation,
    extract_raw_observations,
)
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_temporal import (
    GlassTemporalSnapshot,
    GlassTemporalState,
    OilShadowTemporalModel,
    TemporalCommitError,
)
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
    BoundaryAcceptedDecision,
    EvidenceUnavailableDecision,
    EvidenceUnavailableOutcome,
    NoInterfaceAcceptedDecision,
    NoInterfaceOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
    ReacquisitionPendingDecision,
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
    snapshot = GlassTemporalSnapshot("g", 0, 0, GlassTemporalState("g"))
    provisional = OilShadowTemporalModel().evaluate(snapshot, canonical.current_observation)
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


def _private(pipeline: OilHypothesisPipeline, name: str):
    return getattr(pipeline, f"_OilHypothesisPipeline__{name}")


def _set_private(pipeline: OilHypothesisPipeline, name: str, value) -> None:
    setattr(pipeline, f"_OilHypothesisPipeline__{name}", value)


def _wait_for_barrier(barrier, predicate) -> None:
    with barrier._condition:
        while not predicate():
            assert barrier._condition.wait(timeout=5)


class _ObservedLock:
    def __init__(self) -> None:
        self._lock = RLock()
        self.waiting = Event()

    def __enter__(self):
        if not self._lock.acquire(blocking=False):
            self.waiting.set()
            assert self._lock.acquire(timeout=5)
        return self

    def __exit__(self, *_exc):
        self._lock.release()


class _BlockingStateDict(dict):
    def __init__(self, committed: Event, release: Event):
        super().__init__()
        self._committed = committed
        self._release = release

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._committed.set()
        assert self._release.wait(timeout=5)


class _RejectingStateDict(dict):
    def __init__(self, rejected_key: str | None = None):
        super().__init__()
        self._rejected_key = rejected_key

    def __setitem__(self, key, value):
        if self._rejected_key is None or key == self._rejected_key:
            raise RuntimeError("injected state replacement failure")
        super().__setitem__(key, value)


def test_phase_a_failure_prevents_temporal_evaluation_and_state_creation(monkeypatch):
    calls = 0
    original = OilShadowTemporalModel.evaluate

    def spy(self, snapshot, observation):
        nonlocal calls
        calls += 1
        return original(self, snapshot, observation)

    monkeypatch.setattr(OilShadowTemporalModel, "evaluate", spy)
    pipeline = OilHypothesisPipeline()
    monkeypatch.setattr(
        pipeline,
        "_phase_a",
        lambda _frame: (_ for _ in ()).throw(ValueError("injected phase A failure")),
    )
    outcome = _run(pipeline, _boundary_image(), "new")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_A
    assert calls == 0
    assert pipeline.temporal_state_count == 0


def test_evidence_construction_failure_returns_fresh_failure_without_state(monkeypatch):
    pipeline = OilHypothesisPipeline()
    monkeypatch.setattr(
        pipeline_module,
        "extract_raw_observations",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("injected evidence construction failure")
        ),
    )
    first = _run(pipeline, _boundary_image(), "g")
    second = _run(pipeline, _boundary_image(), "g")
    assert isinstance(first, PipelineFailureOutcome)
    assert isinstance(second, PipelineFailureOutcome)
    assert first is not second
    assert first.stage is PipelineFailureStage.EVIDENCE_CONSTRUCTION
    assert second.stage is PipelineFailureStage.EVIDENCE_CONSTRUCTION
    assert pipeline.temporal_state_count == 0


def test_temporal_evaluation_exception_returns_failure_without_state(monkeypatch):
    monkeypatch.setattr(
        OilShadowTemporalModel,
        "evaluate",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("injected temporal evaluation failure")
        ),
    )
    pipeline = OilHypothesisPipeline()
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.TEMPORAL_EVALUATION
    assert pipeline.temporal_state_count == 0


def test_phase_b_owner_exception_returns_failure_without_commit(monkeypatch):
    pipeline = OilHypothesisPipeline()
    monkeypatch.setattr(
        pipeline,
        "_phase_b",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("injected phase B owner failure")
        ),
    )
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_B
    assert pipeline.temporal_state_count == 0


def test_forged_provisional_resource_is_rejected_before_commit(monkeypatch):
    original = OilShadowTemporalModel.evaluate

    def forge(self, snapshot, observation):
        result = original(self, snapshot, observation)
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

    monkeypatch.setattr(OilShadowTemporalModel, "evaluate", forge)
    pipeline = OilHypothesisPipeline()
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_B
    assert pipeline.temporal_state_count == 0


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
    assert pipeline.temporal_state_count == 0


def test_phase_b_rejects_selection_content_y_mode_state_and_resources():
    cases = []
    pipeline, canonical, snapshot, provisional = _phase_b_setup()
    decision = provisional.decision
    assert isinstance(decision, BoundaryAcceptedDecision)
    alternate = replace(decision.selected_hypothesis, identity="a" * 24)
    cases.append(replace(provisional, decision=replace(decision, selected_hypothesis=alternate)))
    cases.append(replace(provisional, decision=replace(
        decision, accepted_source_y=decision.accepted_source_y + 1.0
    )))
    forged_mode = replace(decision)
    object.__setattr__(forged_mode, "acceptance_mode", "forged")
    cases.append(replace(provisional, decision=forged_mode))
    cases.append(replace(provisional, next_state=replace(provisional.next_state, glass_id="other")))
    cases.append(replace(provisional, next_state=replace(provisional.next_state, version=99)))
    forged_resources = replace(provisional)
    object.__setattr__(forged_resources, "resources", TemporalResourceMetrics(
        provisional.resources.beam_count,
        provisional.resources.history_length,
        provisional.resources.retained_scalar_count + 1,
        provisional.resources.reacquisition_count,
    ))
    cases.append(forged_resources)
    for bad in cases:
        with pytest.raises((TypeError, ValueError)):
            pipeline._phase_b("g", canonical, snapshot, bad)
        assert pipeline.temporal_state_count == 0


def _transition_cases():
    pipeline = OilHypothesisPipeline()
    model = OilShadowTemporalModel(pipeline.bounds)
    boundary_a = _raw_frame(_boundary_image(130)).current_observation
    boundary_b = _raw_frame(_boundary_image(200)).current_observation
    boundary_c = _raw_frame(_boundary_image(198)).current_observation
    no_interface = _raw_frame(np.full((240, 320), 75, dtype=np.uint8)).current_observation
    unavailable = _raw_frame(_unavailable_image()).current_observation
    ambiguous = ShadowAmbiguousObservation(
        hypothesis_ids=(),
        boundary_likelihood=0.45,
        artifact_likelihood=0.42,
        ambiguity_likelihood=0.8,
        no_interface_likelihood=0.2,
        visibility=0.9,
        projected_source_y=150.0,
        reason="test ambiguity",
    )
    empty = GlassTemporalSnapshot("g", 0, 0, GlassTemporalState("g"))
    accepted = model.evaluate(empty, boundary_a)
    accepted_snapshot = GlassTemporalSnapshot("g", 0, 1, accepted.next_state)
    pending = model.evaluate(accepted_snapshot, boundary_b)
    pending_snapshot = GlassTemporalSnapshot("g", 0, 2, pending.next_state)
    return pipeline, (
        (empty, accepted),
        (accepted_snapshot, pending),
        (pending_snapshot, model.evaluate(pending_snapshot, boundary_c)),
        (accepted_snapshot, model.evaluate(accepted_snapshot, no_interface)),
        (accepted_snapshot, model.evaluate(accepted_snapshot, unavailable)),
        (accepted_snapshot, model.evaluate(accepted_snapshot, ambiguous)),
    )


def test_all_temporal_decision_variants_have_coherent_next_state():
    pipeline, cases = _transition_cases()
    for snapshot, provisional in cases:
        pipeline._validate_transition_coherence(
            snapshot, provisional.decision, provisional.next_state
        )


def test_transition_coherence_rejects_load_bearing_state_divergence():
    pipeline, cases = _transition_cases()
    corruptions = []
    for snapshot, provisional in cases:
        state = provisional.next_state
        if isinstance(provisional.decision, BoundaryAcceptedDecision):
            bad = replace(state, accepted_y=(state.accepted_y or 0.0) + 1.0)
        elif isinstance(provisional.decision, ReacquisitionPendingDecision):
            bad = replace(state, pending_y=(state.pending_y or 0.0) + 1.0)
        elif isinstance(provisional.decision, NoInterfaceAcceptedDecision):
            bad = replace(state, no_interface_count=0)
        elif isinstance(provisional.decision, EvidenceUnavailableDecision):
            bad = replace(state, unavailable_count=0)
        else:
            bad = replace(state, accepted_y=999.0)
        corruptions.append((snapshot, provisional.decision, bad))
    for snapshot, decision, bad in corruptions:
        with pytest.raises(ValueError):
            pipeline._validate_transition_coherence(snapshot, decision, bad)


def test_published_boundary_and_pending_outcomes_match_committed_state():
    pipeline = OilHypothesisPipeline()
    accepted = _run(pipeline, _boundary_image(130), "g")
    assert isinstance(accepted, AcceptedBoundaryOutcome)
    assert pipeline.temporal_snapshot("g").state.accepted_y == accepted.raw_source_y
    pending = _run(pipeline, _boundary_image(200), "g")
    assert pending.__class__.__name__ == "ReacquisitionPendingOutcome"
    snapshot = pipeline.temporal_snapshot("g")
    assert snapshot.state.pending_y == pending.pending_hypothesis.representative_source_y
    reacquired = _run(pipeline, _boundary_image(198), "g")
    assert isinstance(reacquired, AcceptedBoundaryOutcome)
    snapshot = pipeline.temporal_snapshot("g")
    assert snapshot.state.accepted_y == reacquired.raw_source_y
    assert snapshot.state.pending_y is None


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
    pipeline = OilHypothesisPipeline()
    before = pipeline.temporal_snapshot("g")
    _set_private(pipeline, "states", _RejectingStateDict())
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.COMMIT
    assert pipeline.temporal_snapshot("g") == before
    assert pipeline.temporal_state_count == 0


def test_outcome_construction_and_validation_fail_before_commit(monkeypatch):
    pipeline = OilHypothesisPipeline()
    monkeypatch.setattr(
        pipeline,
        "_prepare_outcome",
        lambda *_args: (_ for _ in ()).throw(
            RuntimeError("injected outcome construction failure")
        ),
    )
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.OUTCOME_PREPARATION
    assert pipeline.temporal_state_count == 0

    pipeline = OilHypothesisPipeline()
    monkeypatch.setattr(
        pipeline,
        "_validate_prepared_outcome",
        lambda *_args: (_ for _ in ()).throw(
            RuntimeError("injected prepared validation failure")
        ),
    )
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.OUTCOME_PREPARATION
    assert pipeline.temporal_state_count == 0


def test_repeated_pipeline_failure_does_not_advance_unavailable_counter(monkeypatch):
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
    pipeline = OilHypothesisPipeline()
    _set_private(pipeline, "states", _RejectingStateDict("a"))
    failed = _run(pipeline, _boundary_image(), "a")
    succeeded = _run(pipeline, _boundary_image(), "b")
    assert isinstance(failed, PipelineFailureOutcome)
    assert isinstance(succeeded, AcceptedBoundaryOutcome)
    assert pipeline.temporal_snapshot("a").version == 0
    assert pipeline.temporal_snapshot("b").version == 1
    assert pipeline.temporal_state_count == 1


def test_same_glass_transaction_serializes_fixed_flow(monkeypatch):
    entered = Event()
    release = Event()
    observed_lock = _ObservedLock()
    pipeline = OilHypothesisPipeline()
    _private(pipeline, "locks")["g"] = observed_lock
    original = pipeline._prepare_outcome
    calls = 0

    def blocking_prepare(*args):
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            assert release.wait(timeout=5)
        return original(*args)

    monkeypatch.setattr(pipeline, "_prepare_outcome", blocking_prepare)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(_run, pipeline, _boundary_image(130), "g")
        assert entered.wait(timeout=5)
        second = executor.submit(_run, pipeline, _boundary_image(132), "g")
        assert observed_lock.waiting.wait(timeout=5)
        release.set()
        assert isinstance(first.result(timeout=5), AcceptedBoundaryOutcome)
        assert isinstance(second.result(timeout=5), AcceptedBoundaryOutcome)
    assert pipeline.temporal_snapshot("g").version == 2


def test_different_glass_transactions_remain_parallel(monkeypatch):
    both_entered = Barrier(2)
    original = OilHypothesisPipeline._phase_a

    def rendezvous(self, frame):
        both_entered.wait(timeout=5)
        return original(self, frame)

    monkeypatch.setattr(OilHypothesisPipeline, "_phase_a", rendezvous)
    pipeline = OilHypothesisPipeline()
    with ThreadPoolExecutor(max_workers=2) as executor:
        a = executor.submit(_run, pipeline, _boundary_image(125), "a")
        b = executor.submit(_run, pipeline, _boundary_image(145), "b")
        assert isinstance(a.result(timeout=5), AcceptedBoundaryOutcome)
        assert isinstance(b.result(timeout=5), AcceptedBoundaryOutcome)
    assert pipeline.temporal_state_count == 2


def test_global_reset_blocks_new_transaction_after_writer_waits(monkeypatch):
    entered = Event()
    release = Event()
    original = OilHypothesisPipeline._phase_a
    calls = 0

    def block_first(self, frame):
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            assert release.wait(timeout=5)
        return original(self, frame)

    monkeypatch.setattr(OilHypothesisPipeline, "_phase_a", block_first)
    pipeline = OilHypothesisPipeline()
    barrier = _private(pipeline, "barrier")
    with ThreadPoolExecutor(max_workers=3) as executor:
        first = executor.submit(_run, pipeline, _boundary_image(), "a")
        assert entered.wait(timeout=5)
        reset = executor.submit(pipeline.reset)
        _wait_for_barrier(barrier, lambda: barrier._reset_waiters == 1)
        second = executor.submit(_run, pipeline, _boundary_image(132), "b")
        _wait_for_barrier(barrier, lambda: barrier._transaction_waiters == 1)
        assert calls == 1
        release.set()
        assert isinstance(first.result(timeout=5), AcceptedBoundaryOutcome)
        reset.result(timeout=5)
        assert isinstance(second.result(timeout=5), AcceptedBoundaryOutcome)
    assert pipeline.temporal_state_count == 1
    assert pipeline.temporal_snapshot("b").version == 1


def test_global_reset_waits_through_commit_to_outcome_handoff():
    committed = Event()
    release = Event()
    pipeline = OilHypothesisPipeline()
    _set_private(pipeline, "states", _BlockingStateDict(committed, release))
    barrier = _private(pipeline, "barrier")
    with ThreadPoolExecutor(max_workers=3) as executor:
        operation = executor.submit(_run, pipeline, _boundary_image(), "g")
        assert committed.wait(timeout=5)
        reset = executor.submit(pipeline.reset)
        _wait_for_barrier(barrier, lambda: barrier._reset_waiters == 1)
        observer = executor.submit(pipeline.temporal_snapshot, "g")
        _wait_for_barrier(barrier, lambda: barrier._transaction_waiters == 1)
        release.set()
        assert isinstance(operation.result(timeout=5), AcceptedBoundaryOutcome)
        reset.result(timeout=5)
        snapshot = observer.result(timeout=5)
    assert pipeline.temporal_state_count == 0
    assert snapshot.version == 2


def test_reset_crosses_active_multi_glass_transactions_without_deadlock(monkeypatch):
    both_active = Barrier(3)
    release = Event()
    original = OilHypothesisPipeline._phase_a
    calls = 0

    def block_two(self, frame):
        nonlocal calls
        calls += 1
        if calls <= 2:
            both_active.wait(timeout=5)
            assert release.wait(timeout=5)
        return original(self, frame)

    monkeypatch.setattr(OilHypothesisPipeline, "_phase_a", block_two)
    pipeline = OilHypothesisPipeline()
    barrier = _private(pipeline, "barrier")
    with ThreadPoolExecutor(max_workers=4) as executor:
        a = executor.submit(_run, pipeline, _boundary_image(125), "a")
        b = executor.submit(_run, pipeline, _boundary_image(145), "b")
        both_active.wait(timeout=5)
        reset = executor.submit(pipeline.reset)
        _wait_for_barrier(barrier, lambda: barrier._reset_waiters == 1)
        c = executor.submit(_run, pipeline, _boundary_image(135), "c")
        _wait_for_barrier(barrier, lambda: barrier._transaction_waiters == 1)
        assert calls == 2
        release.set()
        assert isinstance(a.result(timeout=5), AcceptedBoundaryOutcome)
        assert isinstance(b.result(timeout=5), AcceptedBoundaryOutcome)
        reset.result(timeout=5)
        assert isinstance(c.result(timeout=5), AcceptedBoundaryOutcome)
    assert pipeline.temporal_state_count == 1
    assert pipeline.temporal_snapshot("c").version == 1


def test_reset_waiter_reentry_is_rejected_without_self_deadlock(monkeypatch):
    pipeline = OilHypothesisPipeline()
    original = pipeline._phase_a

    def reenter(frame):
        pipeline.reset()
        return original(frame)

    monkeypatch.setattr(pipeline, "_phase_a", reenter)
    outcome = _run(pipeline, _boundary_image(), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_A
    assert "inside a temporal transaction" in outcome.reason
    pipeline.reset()
    assert pipeline.temporal_state_count == 0


def test_stale_snapshot_is_rejected_from_another_thread(monkeypatch):
    pipeline = OilHypothesisPipeline()
    stale = GlassTemporalSnapshot("g", 0, 0, GlassTemporalState("g"))
    accepted = _run(pipeline, _boundary_image(130), "g")
    assert isinstance(accepted, AcceptedBoundaryOutcome)
    before = pipeline.temporal_snapshot("g")
    monkeypatch.setattr(
        pipeline,
        "_OilHypothesisPipeline__snapshot_locked",
        lambda _key: stale,
    )
    with ThreadPoolExecutor(max_workers=1) as executor:
        outcome = executor.submit(_run, pipeline, _boundary_image(132), "g").result(
            timeout=5
        )
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.COMMIT
    monkeypatch.undo()
    assert pipeline.temporal_snapshot("g") == before


def test_replay_token_is_rejected_without_state_change(monkeypatch):
    pipeline = OilHypothesisPipeline()
    _run(pipeline, _boundary_image(130), "g")
    before = pipeline.temporal_snapshot("g")
    live = GlassTemporalSnapshot(
        before.glass_id,
        before.reset_generation,
        before.version,
        before.state,
    )
    assert before.state.last_commit_token is not None
    monkeypatch.setattr(
        pipeline,
        "_OilHypothesisPipeline__snapshot_locked",
        lambda _key: live,
    )
    monkeypatch.setattr(
        pipeline,
        "_commit_token",
        lambda *_args: before.state.last_commit_token,
    )
    outcome = _run(pipeline, _boundary_image(132), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.COMMIT
    monkeypatch.undo()
    assert pipeline.temporal_snapshot("g") == before


def test_cross_glass_snapshot_is_rejected_before_commit(monkeypatch):
    pipeline = OilHypothesisPipeline()
    _run(pipeline, _boundary_image(130), "a")
    before_a = pipeline.temporal_snapshot("a")
    snapshot_a = GlassTemporalSnapshot(
        before_a.glass_id,
        before_a.reset_generation,
        before_a.version,
        before_a.state,
    )
    monkeypatch.setattr(
        pipeline,
        "_OilHypothesisPipeline__snapshot_locked",
        lambda _key: snapshot_a,
    )
    outcome = _run(pipeline, _boundary_image(145), "b")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.PHASE_B
    monkeypatch.undo()
    assert pipeline.temporal_state_count == 1
    assert pipeline.temporal_snapshot("a") == before_a
    assert pipeline.temporal_snapshot("b").version == 0


def test_pre_reset_snapshot_is_rejected_after_generation_change(monkeypatch):
    pipeline = OilHypothesisPipeline()
    _run(pipeline, _boundary_image(130), "g")
    before_reset = pipeline.temporal_snapshot("g")
    stale = GlassTemporalSnapshot(
        before_reset.glass_id,
        before_reset.reset_generation,
        before_reset.version,
        before_reset.state,
    )
    pipeline.reset()
    with monkeypatch.context() as patch:
        patch.setattr(
            pipeline,
            "_OilHypothesisPipeline__snapshot_locked",
            lambda _key: stale,
        )
        outcome = _run(pipeline, _boundary_image(132), "g")
    assert isinstance(outcome, PipelineFailureOutcome)
    assert outcome.stage is PipelineFailureStage.COMMIT
    after = pipeline.temporal_snapshot("g")
    assert after.reset_generation == before_reset.reset_generation + 1
    assert after.version == before_reset.version + 1
    assert pipeline.temporal_state_count == 0


def test_production_object_graph_has_no_injection_session_or_commit_surface():
    parameters = inspect.signature(OilHypothesisPipeline).parameters
    assert set(parameters) == {"bounds"}
    pipeline = OilHypothesisPipeline()
    for name in (
        "temporal",
        "execute",
        "commit",
        "evaluate",
        "failure_outcome",
        "_outcome_preparer",
    ):
        assert not hasattr(pipeline, name)
    assert not hasattr(temporal_module, "_OilTemporalAuthority")
    assert not hasattr(temporal_module, "_TemporalTransactionSession")
    public_operations = {
        name for name, value in inspect.getmembers(OilHypothesisPipeline)
        if not name.startswith("_") and callable(value)
    }
    assert public_operations == {"reset", "run", "temporal_snapshot"}


def test_stale_replay_cross_thread_cross_glass_and_pre_reset_bypass_are_unavailable():
    pipeline = OilHypothesisPipeline()
    _run(pipeline, _boundary_image(), "g")
    snapshot = pipeline.temporal_snapshot("g")
    assert not hasattr(snapshot, "commit")
    assert not hasattr(snapshot, "evaluate")
    pipeline.reset()
    assert pipeline.temporal_snapshot("g").reset_generation == snapshot.reset_generation + 1

    def attempt_bypass():
        for name in ("commit", "execute", "evaluate"):
            with pytest.raises(AttributeError):
                getattr(pipeline, name)

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(attempt_bypass).result(timeout=5)
        executor.submit(attempt_bypass).result(timeout=5)
    with pytest.raises(TypeError):
        OilHypothesisPipeline(temporal_evaluator=lambda *_args: None)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        OilHypothesisPipeline(commit_hook=lambda *_args: None)  # type: ignore[call-arg]
