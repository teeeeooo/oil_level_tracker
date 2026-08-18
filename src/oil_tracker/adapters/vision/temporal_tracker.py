from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from oil_tracker.domain.enums import FillState

from .oil_shadow_types import CompatibilityTrackerAction, SmoothingAction


@dataclass
class TemporalTracker:
    smoothing_window: int = 5
    state_hold_frames: int = 2
    previous_y: float | None = None
    previous_foam_y: float | None = None
    current_state: FillState | None = None
    _oil_values: deque[float] = field(default_factory=deque)
    _foam_values: deque[float] = field(default_factory=deque)
    _pending_state: FillState | None = None
    _pending_count: int = 0

    @property
    def oil_sample_count(self) -> int:
        return len(self._oil_values)

    def update(
        self,
        raw_y: float | None,
        raw_foam_y: float | None,
        proposed_state: FillState,
        *,
        oil_tracker_action: CompatibilityTrackerAction,
        oil_smoothing_action: SmoothingAction,
        foam_update_accepted: bool | None = None,
        review_override: bool = False,
    ) -> tuple[float | None, float | None, FillState]:
        """Consume canonical oil actions and bounded Foam acceptance only."""

        if oil_tracker_action is CompatibilityTrackerAction.ACCEPT_BOUNDARY:
            if raw_y is None:
                raise ValueError("Accepted boundary action requires a numeric oil Y.")
            if oil_smoothing_action not in {
                SmoothingAction.PRESERVE,
                SmoothingAction.CLEAR_BEFORE_ACCEPT,
            }:
                raise ValueError("Accepted boundary has an incompatible smoothing action.")
        elif oil_tracker_action is CompatibilityTrackerAction.NO_UPDATE:
            if raw_y is not None:
                raise ValueError("No-update action cannot carry a numeric oil Y.")
            if oil_smoothing_action not in {
                SmoothingAction.PRESERVE,
                SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE,
            }:
                raise ValueError("No-update has an incompatible smoothing action.")
        else:
            raise TypeError("Unsupported compatibility tracker action.")

        if oil_smoothing_action in {
            SmoothingAction.CLEAR_BEFORE_ACCEPT,
            SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE,
        }:
            self._oil_values.clear()
            self.previous_y = None
        if foam_update_accepted is None:
            foam_update_accepted = raw_foam_y is not None

        oil = self._smooth_oil(
            raw_y
            if oil_tracker_action is CompatibilityTrackerAction.ACCEPT_BOUNDARY
            else None,
        )
        foam = self._smooth_median(
            self._foam_values,
            raw_foam_y if foam_update_accepted else None,
        )
        if oil is not None:
            self.previous_y = oil
        if foam is not None:
            self.previous_foam_y = foam
        review_required = review_override or proposed_state is FillState.UNKNOWN_REVIEW
        if review_required:
            self.current_state = FillState.UNKNOWN_REVIEW
            self._pending_state = None
            self._pending_count = 0
            state = FillState.UNKNOWN_REVIEW
        else:
            state = self._stabilize_state(proposed_state)
        return oil, foam, state

    def clear_foam(self) -> None:
        self._foam_values.clear()
        self.previous_foam_y = None

    def reset(self) -> None:
        self.previous_y = None
        self.previous_foam_y = None
        self.current_state = None
        self._oil_values.clear()
        self._foam_values.clear()
        self._pending_state = None
        self._pending_count = 0

    def _smooth_oil(self, value: float | None) -> float | None:
        """Track causal motion while retaining median suppression for reversals.

        The bounded path has already confidence-gated every value reaching this
        method. A monotonic accepted path therefore follows the latest measurement
        instead of accumulating median lag during rapid filling or draining. When
        accepted samples reverse direction, the bounded median still suppresses an
        isolated oscillation. No absolute pixel threshold is required.
        """

        if value is None:
            return None
        current = float(value)
        prior = tuple(self._oil_values)
        self._oil_values.append(current)
        self._trim(self._oil_values)
        if not prior:
            return current
        previous = prior[-1]
        delta = current - previous
        if delta == 0.0:
            return self._median(self._oil_values)
        if len(prior) == 1:
            return current
        prior_delta = previous - prior[-2]
        if prior_delta == 0.0 or delta * prior_delta > 0.0:
            return current
        return self._median(self._oil_values)

    def _smooth_median(
        self,
        values: deque[float],
        value: float | None,
    ) -> float | None:
        if value is None:
            return None
        values.append(float(value))
        self._trim(values)
        return self._median(values)

    def _trim(self, values: deque[float]) -> None:
        while len(values) > max(1, self.smoothing_window):
            values.popleft()

    @staticmethod
    def _median(values: deque[float]) -> float:
        ordered = sorted(values)
        return ordered[len(ordered) // 2]

    def _stabilize_state(self, proposed: FillState) -> FillState:
        if self.current_state is None:
            self.current_state = proposed
            return proposed
        if proposed == self.current_state:
            self._pending_state = None
            self._pending_count = 0
            return self.current_state
        if proposed != self._pending_state:
            self._pending_state = proposed
            self._pending_count = 1
        else:
            self._pending_count += 1
        if self._pending_count >= max(1, self.state_hold_frames):
            self.current_state = proposed
            self._pending_state = None
            self._pending_count = 0
        return self.current_state
