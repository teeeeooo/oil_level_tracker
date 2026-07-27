from __future__ import annotations

from dataclasses import dataclass
import math

from .oil_shadow_types import (
    OilShadowBounds,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowCurrentObservation,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowTemporalDecision,
    ShadowTemporalStatus,
    ShadowUnavailableObservation,
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


@dataclass
class _GlassState:
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


class OilShadowTemporalTracker:
    """Bounded Glass-local temporal projection over immutable typed observations."""

    def __init__(self, bounds: OilShadowBounds | None = None) -> None:
        self.bounds = bounds or OilShadowBounds()
        self._states: dict[str, _GlassState] = {}

    @property
    def state_count(self) -> int:
        return len(self._states)

    @property
    def retained_scalar_limit(self) -> int:
        return (
            self.bounds.temporal_beam_width
            * (self.bounds.temporal_history_window * 4 + 7)
            + 10
        )

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._states.clear()
        else:
            self._states.pop(str(glass_id), None)

    def state_resource_counts(self, glass_id: str) -> tuple[int, int, int, int]:
        state = self._states.get(str(glass_id))
        if state is None:
            return 0, 0, 0, 0
        beam_count = len(state.beam)
        history_length = max((len(item.history) for item in state.beam), default=0)
        retained = self._retained_scalar_count(state)
        static_scalars = 2
        return beam_count, history_length, retained, static_scalars

    def evaluate(
        self,
        glass_id: str,
        observation: ShadowCurrentObservation,
    ) -> ShadowTemporalDecision:
        key = str(glass_id)
        state = self._states.setdefault(key, _GlassState())
        alternatives = self._alternatives(observation)
        state.beam = self._advance_beam(state.beam, alternatives)
        best = state.beam[0] if state.beam else None
        second = state.beam[1] if len(state.beam) > 1 else None
        margin = (
            _unit(best.cumulative_score - second.cumulative_score)
            if best is not None and second is not None
            else (0.0 if best is None else _unit(best.observation_score))
        )
        self._record_static_state(state, observation)

        if isinstance(observation, ShadowBoundaryObservation):
            return self._boundary_decision(state, observation, margin)
        if isinstance(observation, ShadowNoInterfaceObservation):
            return self._no_interface_decision(state, observation, margin)
        if isinstance(observation, ShadowUnavailableObservation):
            return self._unavailable_decision(state, observation, margin)
        return self._ambiguous_decision(state, observation, margin)

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
                history = (
                    history
                    + ((kind.value, identity, source_y, score),)
                )[-self.bounds.temporal_history_window :]
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
            sorted(collapsed.values(), key=_beam_order)[
                : self.bounds.temporal_beam_width
            ]
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
                0.08
                * abs(velocity - prior.velocity)
                / max(1.0, continuity),
            )
        return min(0.90, jump_cost + acceleration_cost), velocity

    def _boundary_decision(
        self,
        state: _GlassState,
        observation: ShadowBoundaryObservation,
        margin: float,
    ) -> ShadowTemporalDecision:
        hypothesis = observation.hypothesis
        y = hypothesis.representative_source_y
        confidence = _unit(
            hypothesis.boundary_likelihood
            * (1.0 - 0.35 * hypothesis.ambiguity_likelihood)
        )
        state.no_interface_count = 0
        state.unavailable_count = 0
        if state.accepted_y is None:
            return self._accept_boundary(
                state,
                hypothesis.identity,
                y,
                confidence,
                margin,
                clear=False,
                reason="initial_shadow_boundary",
            )

        continuity = self.bounds.maximum_proposal_diameter_px * 4.0
        predicted = state.accepted_y + (state.accepted_velocity or 0.0)
        continuous = (
            abs(y - state.accepted_y) <= continuity
            or abs(y - predicted) <= continuity
        )
        if continuous:
            return self._accept_boundary(
                state,
                hypothesis.identity,
                y,
                confidence,
                margin,
                clear=False,
                reason="continuous_shadow_boundary",
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
        state.pending_y = y
        state.pending_velocity = pending_velocity
        state.pending_count = pending_count
        if pending_count >= self.bounds.reacquisition_frames:
            return self._accept_boundary(
                state,
                hypothesis.identity,
                y,
                confidence,
                margin,
                clear=True,
                reason="bounded_shadow_reacquisition",
            )
        return self._decision(
            state,
            ShadowTemporalStatus.REACQUISITION_PENDING,
            ShadowObservationKind.BOUNDARY,
            hypothesis.identity,
            None,
            confidence,
            margin,
            False,
            "large_shadow_motion_waiting_for_consistency",
        )

    def _accept_boundary(
        self,
        state: _GlassState,
        identity: str,
        y: float,
        confidence: float,
        margin: float,
        *,
        clear: bool,
        reason: str,
    ) -> ShadowTemporalDecision:
        prior = state.accepted_y
        state.accepted_velocity = None if prior is None or clear else y - prior
        state.accepted_y = y
        self._clear_pending(state)
        state.smoothing_invalidated = False
        return self._decision(
            state,
            ShadowTemporalStatus.BOUNDARY_ACCEPTED,
            ShadowObservationKind.BOUNDARY,
            identity,
            y,
            confidence,
            margin,
            clear,
            reason,
        )

    def _no_interface_decision(
        self,
        state: _GlassState,
        observation: ShadowNoInterfaceObservation,
        margin: float,
    ) -> ShadowTemporalDecision:
        state.no_interface_count += 1
        state.unavailable_count = 0
        self._clear_pending(state)
        stable = state.no_interface_count >= self.bounds.no_interface_clear_frames
        clear = stable and (
            state.accepted_y is not None or not state.smoothing_invalidated
        )
        if stable:
            state.accepted_y = None
            state.accepted_velocity = None
            state.smoothing_invalidated = True
        return self._decision(
            state,
            ShadowTemporalStatus.NO_INTERFACE_ACCEPTED,
            ShadowObservationKind.NO_INTERFACE,
            None,
            None,
            observation.evidence.likelihood,
            margin,
            clear,
            observation.evidence.reason,
        )

    def _unavailable_decision(
        self,
        state: _GlassState,
        observation: ShadowUnavailableObservation,
        margin: float,
    ) -> ShadowTemporalDecision:
        state.unavailable_count += 1
        state.no_interface_count = 0
        self._clear_pending(state)
        clear = state.unavailable_count >= self.bounds.unavailable_clear_frames and (
            state.accepted_y is not None or not state.smoothing_invalidated
        )
        if clear:
            state.accepted_y = None
            state.accepted_velocity = None
            state.smoothing_invalidated = True
            state.beam = ()
        return self._decision(
            state,
            ShadowTemporalStatus.UNAVAILABLE,
            ShadowObservationKind.UNAVAILABLE,
            None,
            None,
            observation.visibility,
            margin,
            clear,
            observation.reason,
        )

    def _ambiguous_decision(
        self,
        state: _GlassState,
        observation: ShadowAmbiguousObservation,
        margin: float,
    ) -> ShadowTemporalDecision:
        state.no_interface_count = 0
        state.unavailable_count = 0
        self._clear_pending(state)
        confidence = _unit(
            max(
                observation.boundary_likelihood,
                observation.artifact_likelihood,
                observation.no_interface_likelihood,
            )
            * (1.0 - 0.45 * observation.ambiguity_likelihood)
        )
        return self._decision(
            state,
            ShadowTemporalStatus.AMBIGUOUS,
            ShadowObservationKind.AMBIGUOUS,
            None,
            observation.projected_source_y,
            confidence,
            margin,
            False,
            observation.reason,
        )

    def _decision(
        self,
        state: _GlassState,
        status: ShadowTemporalStatus,
        observation_kind: ShadowObservationKind,
        identity: str | None,
        source_y: float | None,
        confidence: float,
        margin: float,
        clear: bool,
        reason: str,
    ) -> ShadowTemporalDecision:
        beam_count = len(state.beam)
        history_length = max((len(item.history) for item in state.beam), default=0)
        return ShadowTemporalDecision(
            status=status,
            observation_kind=observation_kind,
            selected_hypothesis_id=identity,
            projected_source_y=source_y,
            confidence=_unit(confidence),
            decision_margin=_unit(margin),
            clear_smoothing=clear,
            reason=reason,
            beam_count=beam_count,
            history_length=history_length,
            retained_scalar_count=self._retained_scalar_count(state),
            reacquisition_count=state.pending_count,
        )

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
            return (
                (
                    ShadowObservationKind.NO_INTERFACE,
                    None,
                    None,
                    observation.evidence.likelihood,
                ),
            )
        if isinstance(observation, ShadowUnavailableObservation):
            return (
                (
                    ShadowObservationKind.UNAVAILABLE,
                    None,
                    None,
                    0.20 * observation.visibility,
                ),
            )
        alternatives = [
            (
                ShadowObservationKind.AMBIGUOUS,
                None,
                observation.projected_source_y,
                observation.ambiguity_likelihood,
            )
        ]
        if observation.projected_source_y is not None:
            alternatives.append(
                (
                    ShadowObservationKind.BOUNDARY,
                    observation.hypothesis_ids[0]
                    if observation.hypothesis_ids
                    else None,
                    observation.projected_source_y,
                    observation.boundary_likelihood * 0.55,
                )
            )
        if observation.no_interface_likelihood > 0.0:
            alternatives.append(
                (
                    ShadowObservationKind.NO_INTERFACE,
                    None,
                    None,
                    observation.no_interface_likelihood * 0.55,
                )
            )
        return tuple(alternatives)

    @staticmethod
    def _clear_pending(state: _GlassState) -> None:
        state.pending_y = None
        state.pending_velocity = None
        state.pending_count = 0

    @staticmethod
    def _record_static_state(
        state: _GlassState,
        observation: ShadowCurrentObservation,
    ) -> None:
        if isinstance(observation, ShadowBoundaryObservation):
            state.last_static_contribution = (
                observation.hypothesis.static_prior.contribution
            )
            state.last_static_available = float(
                observation.hypothesis.static_prior.available
            )
        else:
            state.last_static_contribution = 0.0
            state.last_static_available = 0.0

    @staticmethod
    def _retained_scalar_count(state: _GlassState) -> int:
        beam_scalars = sum(
            len(item.history) * 4 + 7 for item in state.beam
        )
        state_scalars = 10
        return beam_scalars + state_scalars


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
        return 0.0
    return min(1.0, max(0.0, number))
