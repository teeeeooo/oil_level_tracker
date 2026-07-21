from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4

from oil_tracker.application.services.detector_settings import clone_detector_settings
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.recipe import InspectionRecipe


class DetectorSettingsApplyScope(str, Enum):
    SELECTED = "selected"
    ALL = "all"


class DetectorSettingsApplyError(ValueError):
    pass


@dataclass(frozen=True)
class WorkbenchCompatibility:
    compatible: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class DetectorSettingsApplyResult:
    changed_glass_ids: tuple[str, ...]

    @property
    def is_no_op(self) -> bool:
        return not self.changed_glass_ids


def check_workbench_compatibility(
    workbench_recipe: InspectionRecipe,
    workbench_state: WorkbenchState,
    snapshot_recipe: InspectionRecipe,
    selected_glass_id: str,
    scope: DetectorSettingsApplyScope,
) -> WorkbenchCompatibility:
    reasons: list[str] = []
    if workbench_state is WorkbenchState.ANALYZING:
        reasons.append("현재 Workbench에서 분석이 진행 중입니다.")
    if workbench_recipe.recipe_id != snapshot_recipe.recipe_id:
        reasons.append("현재 Workbench profile과 결과 snapshot의 recipe ID가 다릅니다.")
    if (
        workbench_recipe.reference_frame_width != snapshot_recipe.reference_frame_width
        or workbench_recipe.reference_frame_height != snapshot_recipe.reference_frame_height
    ):
        reasons.append("현재 Workbench와 결과 snapshot의 기준 해상도가 다릅니다.")
    if scope is DetectorSettingsApplyScope.SELECTED:
        if not any(glass.id == selected_glass_id for glass in workbench_recipe.glasses):
            reasons.append("현재 Workbench에 동일한 관찰창 ID가 없습니다.")
    elif not workbench_recipe.glasses:
        reasons.append("현재 Workbench에 적용할 관찰창이 없습니다.")
    return WorkbenchCompatibility(not reasons, tuple(reasons))


def apply_detector_settings(
    recipe: InspectionRecipe,
    selected_glass_id: str,
    settings,
    scope: DetectorSettingsApplyScope,
) -> DetectorSettingsApplyResult:
    targets = (
        [glass for glass in recipe.glasses if glass.id == selected_glass_id]
        if scope is DetectorSettingsApplyScope.SELECTED
        else list(recipe.glasses)
    )
    if not targets:
        raise DetectorSettingsApplyError("검출 설정을 적용할 관찰창이 없습니다.")
    changed: list[str] = []
    for glass in targets:
        candidate = clone_detector_settings(settings)
        if glass.detector_settings != candidate:
            glass.detector_settings = candidate
            changed.append(glass.id)
    return DetectorSettingsApplyResult(tuple(changed))


def create_profile_from_snapshot(
    snapshot_recipe: InspectionRecipe,
    selected_glass_id: str,
    settings,
    scope: DetectorSettingsApplyScope,
    *,
    name_suffix: str = " - 재검출 설정",
) -> InspectionRecipe:
    recipe = InspectionRecipe.from_dict(snapshot_recipe.to_dict())
    result = apply_detector_settings(recipe, selected_glass_id, settings, scope)
    if scope is DetectorSettingsApplyScope.SELECTED and not result.changed_glass_ids:
        # A no-op profile is still a valid explicit snapshot copy.
        if not any(glass.id == selected_glass_id for glass in recipe.glasses):
            raise DetectorSettingsApplyError("선택 관찰창이 결과 snapshot에 없습니다.")
    now = datetime.now(timezone.utc).isoformat()
    recipe.recipe_id = str(uuid4())
    recipe.name = f"{recipe.name}{name_suffix}"
    recipe.created_at = now
    recipe.updated_at = now
    return recipe


def normalized_recipe_destination(path: str | Path) -> Path:
    destination = Path(path).expanduser()
    return destination if destination.suffix.lower() == ".oilrecipe" else destination.with_suffix(".oilrecipe")


def ensure_profile_destination_outside_bundle(
    bundle_root: str | Path,
    destination: str | Path,
) -> Path:
    try:
        root = Path(bundle_root).expanduser().resolve(strict=True)
    except OSError as exc:
        raise DetectorSettingsApplyError("공식 결과 bundle 경로를 확인할 수 없습니다.") from exc
    if not root.is_dir():
        raise DetectorSettingsApplyError("공식 결과 bundle 경로가 폴더가 아닙니다.")
    candidate = normalized_recipe_destination(destination)
    parent = candidate.parent
    try:
        resolved_parent = parent.resolve(strict=True)
    except OSError as exc:
        raise DetectorSettingsApplyError("저장 폴더 경로를 확인할 수 없습니다.") from exc
    resolved_candidate = (
        candidate.resolve(strict=True)
        if candidate.exists() or candidate.is_symlink()
        else resolved_parent / candidate.name
    )
    if resolved_candidate == root or root in resolved_candidate.parents:
        raise DetectorSettingsApplyError(
            "새 profile은 공식 결과 bundle 내부에 저장할 수 없습니다. "
            "결과 bundle 밖의 폴더를 선택해 주세요."
        )
    return candidate
