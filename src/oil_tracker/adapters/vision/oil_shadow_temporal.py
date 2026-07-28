from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, replace
import math
from threading import Condition, RLock, local
from typing import Iterator

from .oil_shadow_types import (
    AbsenceStabilityMode,
    AmbiguousDecision,
    BoundaryAcceptanceMode,
    BoundaryAcceptedDecision,
    EvidenceUnavailableDecision,
    NoInterfaceAcceptedDecision,
    OilShadowBounds,
    ReacquisitionPendingDecision,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowCurrentObservation,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowTemporalDecision,
    ShadowUnavailableObservation,
    TemporalResourceMetrics,
)


@dataclass(frozen=True)
class _BeamItem:
    kind: ShadowObservationKind
    identity: str | None
    source_y: float | None
    observation_score: float
    cumulative_score: float
    transition_cost: float
    velocity: float | None
    history: tuple[tuple[str, str | None, float | None, float], ...]


@dataclass(frozen=True)
class GlassTemporalState:
    glass_id: str
    version: int = 0
    beam: tuple[_BeamItem, ...] = ()
    accepted_y: float | None = None
    accepted_velocity: float | None = None
    pending_y: float | None = None
    pending_velocity: float | None = None
    pending_count: int = 0
    no_interface_count: int = 0
    unavailable_count: int = 0
    smoothing_invalidated: bool = False
    last_static_contribution: float = 0.0
    last_static_available: float = 0.0
    last_commit_token: str | None = None

    def __post_init__(self) -> None:
        if not self.glass_id:
            raise ValueError("Glass temporal state requires a Glass identity.")
        if self.version < 0:
            raise ValueError("Glass temporal state version cannot be negative.")
        if any(value < 0 for value in (
            self.pending_count,
            self.no_interface_count,
            self.unavailable_count,
        )):
            raise ValueError("Glass temporal counters cannot be negative.")
        for value, name in (
            (self.accepted_y, "accepted Y"),
            (self.accepted_velocity, "accepted velocity"),
            (self.pending_y, "pending Y"),
            (self.pending_velocity, "pending velocity"),
        ):
            if value is not None and not math.isfinite(float(value)):
                raise ValueError(f"Glass temporal {name} must be finite.")
        for value, name in (
            (self.last_static_contribution, "static contribution"),
            (self.last_static_available, "static availability"),
        ):
            if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"Glass temporal {name} must be normalized.")
        if not isinstance(self.beam, tuple):
            raise TypeError("Glass temporal beam must be immutable.")


@dataclass(frozen=True)
class GlassTemporalSnapshot:
    glass_id: str
    reset_generation: int
    version: int
    state: GlassTemporalState

    def __post_init__(self) -> None:
        if self.reset_generation < 0:
            raise ValueError("Temporal reset generation cannot be negative.")
        if self.glass_id != self.state.glass_id or self.version != self.state.version:
            raise ValueError("Temporal snapshot identity/version disagrees with state.")


@dataclass(frozen=True)
class TemporalAuditSnapshot:
    glass_id: str
    reset_generation: int
    version: int
    state: GlassTemporalState


@dataclass(frozen=True)
class ProvisionalTemporalResult:
    decision: ShadowTemporalDecision
    next_state: GlassTemporalState
    resources: TemporalResourceMetrics

    def __post_init__(self) -> None:
        if self.decision.resources != self.resources:
            raise ValueError("Provisional decision resources disagree with next state.")


class TemporalCommitError(RuntimeError):
    """Raised when a transaction-local immutable proposal cannot be committed."""


class OilShadowTemporalModel:
    """Pure deterministic temporal evaluator with no live-state authority."""

    def __init__(self, bounds: OilShadowBounds | None = None) -> None:
        self.bounds = bounds or OilShadowBounds()

    @property
    def retained_scalar_limit(self) -> int:
        return self.bounds.temporal_beam_width * (
            self.bounds.temporal_history_window * 4 + 7
        ) + 12

    def evaluate(
        self,
        snapshot: GlassTemporalSnapshot,
        observation: ShadowCurrentObservation,
    ) -> ProvisionalTemporalResult:
        """Return a deterministic immutable proposal without touching live state."""

        prior = snapshot.state
        alternatives = self._alternatives(observation)
        beam = self._advance_beam(prior.beam, alternatives)
        provisional = replace(prior, beam=beam)
        best = beam[0] if beam else None
        second = beam[1] if len(beam) > 1 else None
        margin = (
            _unit(best.cumulative_score - second.cumulative_score)
            if best is not None and second is not None
            else (0.0 if best is None else _unit(best.observation_score))
        )
        provisional = self._record_static_state(provisional, observation)

        if isinstance(observation, ShadowBoundaryObservation):
            decision, next_state = self._boundary_decision(provisional, observation, margin)
        elif isinstance(observation, ShadowNoInterfaceObservation):
            decision, next_state = self._no_interface_decision(provisional, observation, margin)
        elif isinstance(observation, ShadowUnavailableObservation):
            decision, next_state = self._unavailable_decision(provisional, observation, margin)
        elif isinstance(observation, ShadowAmbiguousObservation):
            decision, next_state = self._ambiguous_decision(provisional, observation, margin)
        else:
            raise TypeError("Unsupported successful current-observation variant.")

        next_state = replace(
            next_state,
            version=snapshot.version + 1,
            last_commit_token=None,
        )
        resources = self._resources(next_state)
        decision = replace(decision, resources=resources)
        return ProvisionalTemporalResult(decision, next_state, resources)

    def _advance_beam(
        self,
        previous: tuple[_BeamItem, ...],
        alternatives: tuple[tuple[ShadowObservationKind, str | None, float | None, float], ...],
    ) -> tuple[_BeamItem, ...]:
        priors: tuple[_BeamItem | None, ...] = previous or (None,)
        expanded: list[_BeamItem] = []
        for prior in priors:
            for kind, identity, source_y, score in alternatives:
                transition, velocity = self._transition(prior, kind, source_y)
                history = () if prior is None else prior.history
                history = (history + ((kind.value, identity, source_y, score),))[
                    -self.bounds.temporal_history_window :
                ]
                prior_score = 0.0 if prior is None else prior.cumulative_score * 0.72
                expanded.append(
                    _BeamItem(
                        kind=kind,
                        identity=identity,
                        source_y=source_y,
                        observation_score=score,
                        cumulative_score=prior_score + score - transition,
                        transition_cost=transition,
                        velocity=velocity,
                        history=history,
                    )
                )
        collapsed: dict[tuple[ShadowObservationKind, str | None], _BeamItem] = {}
        for item in expanded:
            key = (item.kind, item.identity)
            current = collapsed.get(key)
            if current is None or _beam_order(item) < _beam_order(current):
                collapsed[key] = item
        return tuple(
            sorted(collapsed.values(), key=_beam_order)[: self.bounds.temporal_beam_width]
        )

    def _transition(
        self,
        prior: _BeamItem | None,
        kind: ShadowObservationKind,
        source_y: float | None,
    ) -> tuple[float, float | None]:
        if prior is None:
            return 0.0, None
        if kind is ShadowObservationKind.UNAVAILABLE:
            return 0.10, prior.velocity
        if kind is ShadowObservationKind.AMBIGUOUS:
            return 0.08, prior.velocity
        if kind is ShadowObservationKind.NO_INTERFACE:
            return (
                0.02 if prior.kind is ShadowObservationKind.NO_INTERFACE else 0.11,
                None,
            )
        if (
            source_y is None
            or prior.source_y is None
            or prior.kind is not ShadowObservationKind.BOUNDARY
        ):
            return 0.10, None
        velocity = source_y - prior.source_y
        continuity = self.bounds.maximum_proposal_diameter_px * 4.0
        jump_cost = min(0.62, 0.10 * (abs(velocity) / max(1.0, continuity)) ** 1.35)
        acceleration_cost = 0.0
        if prior.velocity is not None:
            acceleration_cost = min(
                0.24,
                0.08 * abs(velocity - prior.velocity) / max(1.0, continuity),
            )
        return min(0.90, jump_cost + acceleration_cost), velocity

    def _boundary_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowBoundaryObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        hypothesis = observation.hypothesis
        y = hypothesis.representative_source_y
        confidence = _unit(
            hypothesis.boundary_likelihood * (1.0 - 0.35 * hypothesis.ambiguity_likelihood)
        )
        state = replace(state, no_interface_count=0, unavailable_count=0)
        if state.accepted_y is None:
            return self._accept_boundary(
                state,
                hypothesis,
                y,
                confidence,
                margin,
                BoundaryAcceptanceMode.INITIAL,
                "initial_shadow_boundary",
            )

        continuity = self.bounds.maximum_proposal_diameter_px * 4.0
        predicted = state.accepted_y + (state.accepted_velocity or 0.0)
        if abs(y - state.accepted_y) <= continuity or abs(y - predicted) <= continuity:
            return self._accept_boundary(
                state,
                hypothesis,
                y,
                confidence,
                margin,
                BoundaryAcceptanceMode.CONTINUOUS,
                "continuous_shadow_boundary",
            )

        tolerance = self.bounds.maximum_proposal_diameter_px * 2.0
        if state.pending_y is None:
            pending_count = 1
            pending_velocity = None
        else:
            pending_prediction = state.pending_y + (state.pending_velocity or 0.0)
            pending_continuous = (
                abs(y - state.pending_y) <= tolerance
                or abs(y - pending_prediction) <= tolerance
            )
            pending_count = state.pending_count + 1 if pending_continuous else 1
            pending_velocity = y - state.pending_y if pending_continuous else None
        state = replace(
            state,
            pending_y=y,
            pending_velocity=pending_velocity,
            pending_count=pending_count,
        )
        if pending_count >= self.bounds.reacquisition_frames:
            return self._accept_boundary(
                state,
                hypothesis,
                y,
                confidence,
                margin,
                BoundaryAcceptanceMode.REACQUIRED,
                "bounded_shadow_reacquisition",
            )
        resources = self._resources(state)
        decision = ReacquisitionPendingDecision(
            pending_hypothesis=hypothesis,
            confidence=confidence,
            decision_margin=margin,
            reason="large_shadow_motion_waiting_for_consistency",
            resources=resources,
        )
        return decision, state

    def _accept_boundary(
        self,
        state: GlassTemporalState,
        hypothesis,
        y: float,
        confidence: float,
        margin: float,
        mode: BoundaryAcceptanceMode,
        reason: str,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        prior = state.accepted_y
        velocity = (
            None
            if prior is None or mode is BoundaryAcceptanceMode.REACQUIRED
            else y - prior
        )
        next_state = replace(
            state,
            accepted_y=y,
            accepted_velocity=velocity,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
            smoothing_invalidated=False,
        )
        decision = BoundaryAcceptedDecision(
            selected_hypothesis=hypothesis,
            accepted_source_y=y,
            confidence=confidence,
            decision_margin=margin,
            acceptance_mode=mode,
            reason=reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _no_interface_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowNoInterfaceObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        count = min(
            self.bounds.no_interface_clear_frames,
            state.no_interface_count + 1,
        )
        stable = count >= self.bounds.no_interface_clear_frames
        next_state = replace(
            state,
            no_interface_count=count,
            unavailable_count=0,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
        )
        if stable:
            next_state = replace(
                next_state,
                accepted_y=None,
                accepted_velocity=None,
                smoothing_invalidated=True,
            )
        mode = AbsenceStabilityMode.STABLE if stable else AbsenceStabilityMode.PENDING
        decision = NoInterfaceAcceptedDecision(
            evidence=observation.evidence,
            confidence=observation.evidence.likelihood,
            decision_margin=margin,
            stability_mode=mode,
            reason=observation.evidence.reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _unavailable_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowUnavailableObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        count = min(
            self.bounds.unavailable_clear_frames,
            state.unavailable_count + 1,
        )
        stable = count >= self.bounds.unavailable_clear_frames
        next_state = replace(
            state,
            unavailable_count=count,
            no_interface_count=0,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
        )
        if stable:
            next_state = replace(
                next_state,
                accepted_y=None,
                accepted_velocity=None,
                smoothing_invalidated=True,
                beam=(),
            )
        mode = AbsenceStabilityMode.STABLE if stable else AbsenceStabilityMode.PENDING
        decision = EvidenceUnavailableDecision(
            visibility=observation.visibility,
            confidence=observation.visibility,
            decision_margin=margin,
            stability_mode=mode,
            reason=observation.reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _ambiguous_decision(
        self,
        state: GlassTemporalState,
        observation: ShadowAmbiguousObservation,
        margin: float,
    ) -> tuple[ShadowTemporalDecision, GlassTemporalState]:
        next_state = replace(
            state,
            no_interface_count=0,
            unavailable_count=0,
            pending_y=None,
            pending_velocity=None,
            pending_count=0,
        )
        confidence = _unit(
            max(
                observation.boundary_likelihood,
                observation.artifact_likelihood,
                observation.no_interface_likelihood,
            ) * (1.0 - 0.45 * observation.ambiguity_likelihood)
        )
        decision = AmbiguousDecision(
            hypothesis_ids=observation.hypothesis_ids,
            projected_source_y=observation.projected_source_y,
            confidence=confidence,
            decision_margin=margin,
            reason=observation.reason,
            resources=self._resources(next_state),
        )
        return decision, next_state

    def _alternatives(
        self,
        observation: ShadowCurrentObservation,
    ) -> tuple[tuple[ShadowObservationKind, str | None, float | None, float], ...]:
        if isinstance(observation, ShadowBoundaryObservation):
            item = observation.hypothesis
            return (
                (
                    ShadowObservationKind.BOUNDARY,
                    item.identity,
                    item.representative_source_y,
                    item.boundary_likelihood,
                ),
                (
                    ShadowObservationKind.AMBIGUOUS,
                    None,
                    item.representative_source_y,
                    item.ambiguity_likelihood * 0.55,
                ),
            )
        if isinstance(observation, ShadowNoInterfaceObservation):
            return ((
                ShadowObservationKind.NO_INTERFACE,
                None,
                None,
                observation.evidence.likelihood,
            ),)
        if isinstance(observation, ShadowUnavailableObservation):
            return ((
                ShadowObservationKind.UNAVAILABLE,
                None,
                None,
                0.20 * observation.visibility,
            ),)
        if not isinstance(observation, ShadowAmbiguousObservation):
            raise TypeError("Unsupported successful current-observation variant.")
        alternatives: list[tuple[ShadowObservationKind, str | None, float | None, float]] = [
            (
                ShadowObservationKind.AMBIGUOUS,
                None,
                observation.projected_source_y,
                observation.ambiguity_likelihood,
            )
        ]
        if observation.projected_source_y is not None:
            alternatives.append((
                ShadowObservationKind.BOUNDARY,
                observation.hypothesis_ids[0] if observation.hypothesis_ids else None,
                observation.projected_source_y,
                observation.boundary_likelihood * 0.55,
            ))
        if observation.no_interface_likelihood > 0.0:
            alternatives.append((
                ShadowObservationKind.NO_INTERFACE,
                None,
                None,
                observation.no_interface_likelihood * 0.55,
            ))
        return tuple(alternatives)

    @staticmethod
    def _record_static_state(
        state: GlassTemporalState,
        observation: ShadowCurrentObservation,
    ) -> GlassTemporalState:
        if isinstance(observation, ShadowBoundaryObservation):
            return replace(
                state,
                last_static_contribution=observation.hypothesis.static_prior.contribution,
                last_static_available=float(observation.hypothesis.static_prior.available),
            )
        return replace(
            state,
            last_static_contribution=0.0,
            last_static_available=0.0,
        )

    def _resources(self, state: GlassTemporalState) -> TemporalResourceMetrics:
        return TemporalResourceMetrics(
            beam_count=len(state.beam),
            history_length=max((len(item.history) for item in state.beam), default=0),
            retained_scalar_count=self._retained_scalar_count(state),
            reacquisition_count=state.pending_count,
        )

    @staticmethod
    def _retained_scalar_count(state: GlassTemporalState) -> int:
        beam_scalars = sum(len(item.history) * 4 + 7 for item in state.beam)
        return beam_scalars + 12


class _LifecycleBarrier:
    """Writer-priority shared/exclusive lifecycle barrier with no callback seams."""

    def __init__(self) -> None:
        self._condition = Condition(RLock())
        self._local = local()
        self._active_transactions = 0
        self._transaction_waiters = 0
        self._reset_active = False
        self._reset_waiters = 0

    @contextmanager
    def transaction(self) -> Iterator[None]:
        depth = int(getattr(self._local, "transaction_depth", 0))
        if depth:
            self._local.transaction_depth = depth + 1
            try:
                yield
            finally:
                self._local.transaction_depth = depth
            return
        with self._condition:
            waiting = self._reset_active or bool(self._reset_waiters)
            if waiting:
                self._transaction_waiters += 1
                self._condition.notify_all()
            try:
                while self._reset_active or self._reset_waiters:
                    self._condition.wait()
            finally:
                if waiting:
                    self._transaction_waiters -= 1
            self._active_transactions += 1
            self._local.transaction_depth = 1
            self._condition.notify_all()
        try:
            yield
        finally:
            with self._condition:
                self._local.transaction_depth = 0
                self._active_transactions -= 1
                if self._active_transactions == 0:
                    self._condition.notify_all()

    @contextmanager
    def global_reset(self) -> Iterator[None]:
        if int(getattr(self._local, "transaction_depth", 0)):
            raise RuntimeError("Global reset cannot start inside a temporal transaction.")
        with self._condition:
            self._reset_waiters += 1
            self._condition.notify_all()
            try:
                while self._reset_active or self._active_transactions:
                    self._condition.wait()
                self._reset_active = True
            finally:
                self._reset_waiters -= 1
        try:
            yield
        finally:
            with self._condition:
                self._reset_active = False
                self._condition.notify_all()


def _beam_order(item: _BeamItem) -> tuple[float, int, float, str]:
    kind_order = {
        ShadowObservationKind.BOUNDARY: 0,
        ShadowObservationKind.NO_INTERFACE: 1,
        ShadowObservationKind.AMBIGUOUS: 2,
        ShadowObservationKind.UNAVAILABLE: 3,
    }
    return (
        -item.cumulative_score,
        kind_order[item.kind],
        float("inf") if item.source_y is None else item.source_y,
        item.identity or "",
    )


def _unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Temporal scalar must be finite.")
    return min(1.0, max(0.0, number))
