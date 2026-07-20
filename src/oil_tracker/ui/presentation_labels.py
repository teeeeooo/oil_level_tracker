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

VALIDATION_MESSAGE_BY_CODE = {
    "STRUCT_SCHEMA": "지원하지 않는 프로필 형식입니다.",
    "STRUCT_FRAME": "기준 영상 크기가 올바르지 않습니다.",
    "STRUCT_DUPLICATE_GLASS": "같은 관찰창 ID가 중복되어 있습니다.",
    "STRUCT_ELLIPSE": "관찰창 타원이 영상 범위를 벗어나거나 크기가 올바르지 않습니다.",
    "STRUCT_MARGIN": "테두리 제외 비율은 0 이상 0.8 미만이어야 합니다.",
    "STRUCT_MARGIN_AREA": "테두리 제외 범위가 너무 커서 분석 영역이 거의 남지 않습니다.",
    "STRUCT_EXCLUSION": "검출 제외 영역의 크기가 올바르지 않습니다.",
    "STRUCT_EXCLUSION_BOUNDS": "검출 제외 영역은 영상 안에 있어야 합니다.",
    "STRUCT_SCALE": "mm/pixel 값은 0보다 커야 합니다.",
    "READY_GLASS": "분석에 포함된 유면 관찰창이 하나 이상 필요합니다.",
    "READY_ZERO": "기준점을 먼저 설정해 주세요.",
    "READY_ZERO_BOUNDS": "기준점은 관찰창 타원 안에 있어야 합니다.",
    "WARN_ZERO_EDGE": "기준점이 관찰창 가장자리에 너무 가깝습니다.",
    "WARN_SCALE": "길이 환산값이 없어 결과를 pixel 단위로 표시합니다.",
    "WARN_MARGIN": "테두리 제외 범위가 큰 편입니다.",
    "READY_COMPRESSOR": "기준점 회복 판정에는 압축기 기동 시각이 필요합니다.",
    "READY_VIDEO": "분석할 시험 영상을 선택해 주세요.",
    "READY_METADATA": "영상 정보를 읽을 수 없습니다.",
    "READY_RANGE": "분석 시작·종료 시각을 확인해 주세요.",
    "READY_FPS": "분석 빈도는 0보다 크고 원본 영상 FPS 이하여야 합니다.",
    "READY_RESOLUTION": "영상 해상도가 프로필과 다릅니다. 관찰창 위치를 확인해 주세요.",
    "WARN_RESOLUTION": "현재 영상 해상도가 프로필 기준 해상도와 다릅니다.",
    "WARN_DURATION": "분석 구간이 1초보다 짧습니다.",
}

VALIDATION_SHORT_MESSAGE_BY_CODE = {
    "STRUCT_ELLIPSE": "관찰 영역 수정 필요",
    "STRUCT_MARGIN": "테두리 제외 범위 수정 필요",
    "STRUCT_MARGIN_AREA": "유효 관찰 영역 수정 필요",
    "READY_ZERO": "기준점 설정 필요",
    "READY_ZERO_BOUNDS": "기준점 위치 수정 필요",
    "WARN_ZERO_EDGE": "기준점 확인 필요",
    "STRUCT_EXCLUSION": "제외 영역 수정 필요",
    "STRUCT_EXCLUSION_BOUNDS": "제외 영역 위치 수정 필요",
    "READY_COMPRESSOR": "압축기 기동 시각 필요",
    "STRUCT_SCALE": "길이 환산값 수정 필요",
    "WARN_SCALE": "길이 환산값 확인 필요",
    "WARN_MARGIN": "테두리 제외 범위 확인 필요",
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


def validation_issue_message(issue) -> str:
    return VALIDATION_MESSAGE_BY_CODE.get(issue.code, issue.message)


def validation_issue_short_message(issue) -> str:
    if issue is None:
        return ""
    return VALIDATION_SHORT_MESSAGE_BY_CODE.get(issue.code, validation_issue_message(issue))
