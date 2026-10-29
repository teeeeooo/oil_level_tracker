"""Glass geometry in source-frame pixels."""

from __future__ import annotations

import math
from dataclasses import dataclass

MINIMUM_RADIUS_PX = 8.0


@dataclass(frozen=True)
class Ellipse:
    """An axis-aligned ellipse. y grows downward, as in the source frame."""

    center_x: float
    center_y: float
    radius_x: float
    radius_y: float

    @property
    def left(self) -> float:
        return self.center_x - self.radius_x

    @property
    def right(self) -> float:
        return self.center_x + self.radius_x

    @property
    def top(self) -> float:
        return self.center_y - self.radius_y

    @property
    def bottom(self) -> float:
        return self.center_y + self.radius_y

    def problems(self, frame_width: int, frame_height: int) -> list[str]:
        values = (self.center_x, self.center_y, self.radius_x, self.radius_y)
        if not all(math.isfinite(value) for value in values):
            return ["타원 좌표가 올바른 숫자가 아닙니다."]
        problems: list[str] = []
        if self.radius_x < MINIMUM_RADIUS_PX or self.radius_y < MINIMUM_RADIUS_PX:
            problems.append(f"타원 반지름은 {MINIMUM_RADIUS_PX:g} px 이상이어야 합니다.")
        if self.left < 0 or self.top < 0 or self.right > frame_width or self.bottom > frame_height:
            problems.append("타원이 프레임 밖으로 나갑니다.")
        return problems
