from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from math import isfinite

from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import InspectionRecipe


_OPTION_LABELS = (
    ("judgment_rule", "판정 설정"),
    ("detector_settings", "검출기 설정"),
    ("margin_ratio", "테두리 제외 범위"),
    ("initial_state", "분석 시작 시 상태"),
    ("mm_per_pixel", "길이 환산값"),
    ("ellipse_size", "타원 크기"),
)


class GlassSettingsCopyError(ValueError):
    """Raised when an observation-window settings copy request is invalid."""

    def __init__(self, message: str, *, target_glass_id: str | None = None) -> None:
        super().__init__(message)
        self.target_glass_id = target_glass_id


@dataclass(frozen=True)
class GlassSettingsCopyOptions:
    judgment_rule: bool = True
    detector_settings: bool = True
    margin_ratio: bool = True
    initial_state: bool = True
    mm_per_pixel: bool = False
    ellipse_size: bool = False

    @property
    def any_selected(self) -> bool:
        return any(getattr(self, key) for key, _label in _OPTION_LABELS)

    @property
    def selected_count(self) -> int:
        return len(self.selected_labels())

    def selected_labels(self) -> tuple[str, ...]:
        return tuple(label for key, label in _OPTION_LABELS if getattr(self, key))


@dataclass(frozen=True)
class GlassSettingsCopyRequest:
    source_glass_id: str
    target_glass_ids: tuple[str, ...]
    options: GlassSettingsCopyOptions


@dataclass(frozen=True)
class GlassSettingsCopyResult:
    requested_target_ids: tuple[str, ...]
    changed_target_ids: tuple[str, ...]

    @property
    def is_no_op(self) -> bool:
        return not self.changed_target_ids


def copy_observation_window_settings(
    recipe: InspectionRecipe,
    request: GlassSettingsCopyRequest,
) -> GlassSettingsCopyResult:
    """Atomically copy selected settings from one glass to one or more targets.

    The function mutates ``recipe`` only after every target has been validated.
    Qt is intentionally not imported so the copy contract remains testable in
    the application layer.
    """

    source = next((glass for glass in recipe.glasses if glass.id == request.source_glass_id), None)
    if source is None:
        raise GlassSettingsCopyError("원본 관찰창이 현재 분석 프로필에 없습니다.")

    if not request.target_glass_ids:
        raise GlassSettingsCopyError("복사할 대상 관찰창을 한 개 이상 선택해 주세요.")
    if request.source_glass_id in request.target_glass_ids:
        raise GlassSettingsCopyError("원본 관찰창은 복사 대상에 포함할 수 없습니다.")
    if not request.options.any_selected:
        raise GlassSettingsCopyError("복사할 설정 항목을 한 개 이상 선택해 주세요.")

    target_ids = tuple(dict.fromkeys(request.target_glass_ids))
    glasses_by_id = {glass.id: glass for glass in recipe.glasses}
    missing = [target_id for target_id in target_ids if target_id not in glasses_by_id]
    if missing:
        raise GlassSettingsCopyError("복사 대상 관찰창이 현재 분석 프로필에 없습니다.")

    candidates = {}
    changed_target_ids: list[str] = []
    for target_id in target_ids:
        target = glasses_by_id[target_id]
        candidate = deepcopy(target)
        _apply_selected_settings(candidate, source, request.options)
        if request.options.ellipse_size:
            _validate_copied_ellipse(recipe, candidate)
        if candidate != target:
            candidates[target_id] = candidate
            changed_target_ids.append(target_id)

    if changed_target_ids:
        recipe.glasses = [candidates.get(glass.id, glass) for glass in recipe.glasses]

    return GlassSettingsCopyResult(target_ids, tuple(changed_target_ids))


def _apply_selected_settings(target, source, options: GlassSettingsCopyOptions) -> None:
    if options.judgment_rule:
        target.judgment_rule = deepcopy(source.judgment_rule)
    if options.detector_settings:
        target.detector_settings = deepcopy(source.detector_settings)
    if options.margin_ratio:
        target.geometry.margin_ratio = source.geometry.margin_ratio
    if options.initial_state:
        target.initial_state = source.initial_state
    if options.mm_per_pixel:
        target.mm_per_pixel = source.mm_per_pixel
    if options.ellipse_size:
        target_ellipse = target.geometry.ellipse
        source_ellipse = source.geometry.ellipse
        target.geometry.ellipse = EllipseGeometry(
            target_ellipse.center_x,
            target_ellipse.center_y,
            source_ellipse.radius_x,
            source_ellipse.radius_y,
        )


def _validate_copied_ellipse(recipe: InspectionRecipe, target) -> None:
    ellipse = target.geometry.ellipse
    values = (
        ellipse.center_x,
        ellipse.center_y,
        ellipse.radius_x,
        ellipse.radius_y,
        target.geometry.zero_line_y,
        target.geometry.margin_ratio,
    )
    invalid_number = any(value is None or not isfinite(float(value)) for value in values)
    outside_frame = (
        ellipse.radius_x <= 0
        or ellipse.radius_y <= 0
        or ellipse.center_x - ellipse.radius_x < 0
        or ellipse.center_y - ellipse.radius_y < 0
        or ellipse.center_x + ellipse.radius_x > recipe.reference_frame_width
        or ellipse.center_y + ellipse.radius_y > recipe.reference_frame_height
    )
    zero_line_outside = (
        target.geometry.zero_line_y is None
        or target.geometry.zero_line_y < ellipse.center_y - ellipse.radius_y
        or target.geometry.zero_line_y > ellipse.center_y + ellipse.radius_y
    )
    margin = target.geometry.margin_ratio
    invalid_margin = margin < 0 or margin >= 0.8
    effective_area_too_small = (
        2.0 * ellipse.radius_x * (1.0 - margin) < 4.0
        or 2.0 * ellipse.radius_y * (1.0 - margin) < 4.0
    )
    if invalid_number or outside_frame or zero_line_outside or invalid_margin or effective_area_too_small:
        raise GlassSettingsCopyError(
            f"{target.name}에는 선택한 타원 크기를 적용할 수 없습니다.\n"
            "현재 중심 위치 또는 기준점과 맞지 않습니다.",
            target_glass_id=target.id,
        )
