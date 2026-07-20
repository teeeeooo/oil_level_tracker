from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from oil_tracker.domain.enums import FillState


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

    def update(self, raw_y: float | None, raw_foam_y: float | None, proposed_state: FillState) -> tuple[float | None, float | None, FillState]:
        oil = self._smooth(self._oil_values, raw_y)
        foam = self._smooth(self._foam_values, raw_foam_y)
        if oil is not None:
            self.previous_y = oil
        if foam is not None:
            self.previous_foam_y = foam
        state = self._stabilize_state(proposed_state)
        return oil, foam, state

    def _smooth(self, values: deque[float], value: float | None) -> float | None:
        if value is None:
            return None
        values.append(float(value))
        while len(values) > max(1, self.smoothing_window):
            values.popleft()
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
