from __future__ import annotations

from enum import Enum

from oil_tracker.domain.enums import (
    FillState,
    InitialObservationState,
    JudgmentMode,
    ResultState,
    ValidationSeverity,
    WorkbenchState,
)

WORKBENCH_STATE_LABELS = {
    WorkbenchState.EMPTY: "비어 있음",
    WorkbenchState.DRAFT: "작성 중",
    WorkbenchState.DRAFT_DIRTY: "수정됨 · 재점검 필요",
    WorkbenchState.VALIDATED: "점검 완료",
    WorkbenchState.ANALYZING: "분석 중",
    WorkbenchState.ANALYZED: "분석 완료",
    WorkbenchState.ERROR: "오류",
}

VALIDATION_SEVERITY_LABELS = {
    ValidationSeverity.ERROR: "오류",
    ValidationSeverity.WARNING: "주의",
    ValidationSeverity.INFORMATION: "안내",
}

INITIAL_STATE_CHOICES = (
    ("자동으로 판단", InitialObservationState.AUTO),
    ("시작 시 오일이 가득 차 있음", InitialObservationState.FULL_NO_INTERFACE),
    ("시작 시 오일이 비어 있음", InitialObservationState.EMPTY_NO_INTERFACE),
    ("시작 시 유면이 보임", InitialObservationState.PARTIAL_VISIBLE),
    ("시작 시 거품이 보임", InitialObservationState.FULL_WITH_FOAM),
    ("시작 상태를 확인하기 어려움", InitialObservationState.UNKNOWN_REVIEW),
)

_INITIAL_STATE_UI_FALLBACK = {
    InitialObservationState.FILLING_VISIBLE: InitialObservationState.PARTIAL_VISIBLE,
    InitialObservationState.DRAINING_VISIBLE: InitialObservationState.PARTIAL_VISIBLE,
    InitialObservationState.FOAMING_VISIBLE: InitialObservationState.FULL_WITH_FOAM,
}

JUDGMENT_MODE_LABELS = {
    JudgmentMode.RECOVERY: "기준점 회복",
    JudgmentMode.HOLD_BELOW_ZERO: "기준점 아래 유지",
    JudgmentMode.HOLD_ABOVE_ZERO: "기준점 위 유지",
}

FILL_STATE_LABELS = {
    FillState.EMPTY_NO_INTERFACE: "오일 없음 · 유면 미표시",
    FillState.FILLING_VISIBLE: "오일 유입 중",
    FillState.PARTIAL_VISIBLE: "유면 확인됨",
    FillState.FULL_NO_INTERFACE: "오일 가득 참 · 유면 미표시",
    FillState.DRAINING_VISIBLE: "오일 감소 중",
    FillState.FULL_WITH_FOAM: "오일 가득 참 · 거품 있음",
    FillState.FOAMING_VISIBLE: "유면과 거품 확인됨",
    FillState.UNKNOWN_REVIEW: "확인 필요",
}

RESULT_STATE_LABELS = {
    ResultState.PASS: "합격",
    ResultState.FAIL: "불합격",
    ResultState.REVIEW_REQUIRED: "사용자 확인 필요",
    ResultState.NOT_APPLICABLE: "판정 대상 아님",
}


def enum_label(value: Enum | str | None, labels: dict[Enum, str]) -> str:
    if value is None:
        return "-"
    if value in labels:
        return labels[value]
    for enum_value, label in labels.items():
        if getattr(enum_value, "value", None) == value:
            return label
    return str(getattr(value, "value", value))


def workbench_state_label(value: WorkbenchState) -> str:
    return enum_label(value, WORKBENCH_STATE_LABELS)


def validation_severity_label(value: ValidationSeverity) -> str:
    return enum_label(value, VALIDATION_SEVERITY_LABELS)


def fill_state_label(value: FillState) -> str:
    return enum_label(value, FILL_STATE_LABELS)


def result_state_label(value: ResultState) -> str:
    return enum_label(value, RESULT_STATE_LABELS)


def initial_state_for_ui(value: InitialObservationState) -> InitialObservationState:
    return _INITIAL_STATE_UI_FALLBACK.get(value, value)
