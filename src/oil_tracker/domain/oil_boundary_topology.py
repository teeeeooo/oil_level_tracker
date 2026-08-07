from __future__ import annotations

# Existing S5-B transition topology. These values centralize the already-established
# candidate-scorer boundaries; changing them is a detector-threshold change.
TOP_ENTRANCE_MAX_RELATIVE_POSITION = 0.32
BOTTOM_ENTRANCE_MIN_RELATIVE_POSITION = 0.68


def boundary_relative_position(y: float, top: float, bottom: float) -> float:
    return (float(y) - float(top)) / max(1.0, float(bottom) - float(top))
