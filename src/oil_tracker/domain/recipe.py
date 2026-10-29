"""Recipe: the Glasses and judgment rules for one equipment and camera setup."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .enums import JudgmentMode
from .geometry import Ellipse
from .problems import Problem

MAXIMUM_NAME_LENGTH = 100


@dataclass(frozen=True)
class JudgmentRule:
    """Product SSOT §5. Heights are source-frame pixels from the zero line."""

    mode: JudgmentMode = JudgmentMode.RECOVERY
    recovery_limit_sec: float = 120.0
    stable_hold_sec: float = 5.0
    minimum_valid_coverage_ratio: float = 0.70
    allowed_sec: float = 5.0
    allowed_px: float = 0.0

    def problems(self) -> list[tuple[str, str]]:
        """Return (field, message) pairs."""
        problems: list[tuple[str, str]] = []
        positive = {
            "recovery_limit_sec": "회복 제한 시간",
            "stable_hold_sec": "안정 유지 시간",
        }
        non_negative = {
            "allowed_sec": "허용 시간",
            "allowed_px": "허용 높이",
        }
        for name, label in positive.items():
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                problems.append((name, f"{label}: 0보다 커야 합니다."))
        for name, label in non_negative.items():
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                problems.append((name, f"{label}: 0 이상이어야 합니다."))
        ratio = self.minimum_valid_coverage_ratio
        if not math.isfinite(ratio) or not 0.0 <= ratio <= 1.0:
            problems.append(("minimum_valid_coverage_ratio", "최소 유효 비율: 0과 1 사이여야 합니다."))
        return problems


@dataclass(frozen=True)
class Glass:
    id: str
    name: str
    ellipse: Ellipse
    zero_line_y: float
    judgment_rule: JudgmentRule = JudgmentRule()


@dataclass(frozen=True)
class ReferenceFrame:
    """The sample-video frame the Glasses were drawn on."""

    width: int
    height: int
    source_name: str
    time_sec: float
    jpeg: bytes


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    reference_frame: ReferenceFrame
    glasses: tuple[Glass, ...]
    created_at: str
    updated_at: str

    def matches_frame_size(self, width: int, height: int) -> bool:
        return (width, height) == (self.reference_frame.width, self.reference_frame.height)


def recipe_problems(recipe: Recipe) -> list[Problem]:
    problems: list[Problem] = []
    name = recipe.name.strip()
    if not name:
        problems.append(Problem("name", "Recipe 이름을 입력하세요."))
    elif len(name) > MAXIMUM_NAME_LENGTH:
        problems.append(Problem("name", f"Recipe 이름은 {MAXIMUM_NAME_LENGTH}자 이하여야 합니다."))

    frame = recipe.reference_frame
    if frame.width <= 0 or frame.height <= 0:
        problems.append(Problem("reference_frame", "기준 프레임 크기가 올바르지 않습니다."))
        return problems
    if not frame.jpeg:
        problems.append(Problem("reference_frame", "기준 프레임 이미지가 없습니다."))

    if not recipe.glasses:
        problems.append(Problem("glasses", "Glass를 하나 이상 추가하세요."))
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for glass in recipe.glasses:
        problems.extend(_glass_problems(glass, frame, seen_ids, seen_names))
    return problems


def _glass_problems(
    glass: Glass,
    frame: ReferenceFrame,
    seen_ids: set[str],
    seen_names: set[str],
) -> list[Problem]:
    problems: list[Problem] = []

    def add(field: str, message: str) -> None:
        problems.append(Problem(field, message, glass.id))

    if not glass.id or glass.id in seen_ids:
        add("id", "Glass ID가 비어 있거나 중복됩니다.")
    seen_ids.add(glass.id)

    name = glass.name.strip()
    if not name:
        add("name", "Glass 이름을 입력하세요.")
    elif len(name) > MAXIMUM_NAME_LENGTH:
        add("name", f"Glass 이름은 {MAXIMUM_NAME_LENGTH}자 이하여야 합니다.")
    elif name.casefold() in seen_names:
        add("name", f"Glass 이름 '{name}'이(가) 중복됩니다.")
    seen_names.add(name.casefold())

    ellipse_problems = glass.ellipse.problems(frame.width, frame.height)
    for message in ellipse_problems:
        add("ellipse", message)
    zero = glass.zero_line_y
    if not math.isfinite(zero):
        add("zero_line_y", "영점선 위치가 올바른 숫자가 아닙니다.")
    elif not ellipse_problems and not glass.ellipse.top <= zero <= glass.ellipse.bottom:
        add("zero_line_y", "영점선은 타원의 위아래 끝 사이에 있어야 합니다.")

    for field, message in glass.judgment_rule.problems():
        add(f"judgment_rule.{field}", message)
    return problems
