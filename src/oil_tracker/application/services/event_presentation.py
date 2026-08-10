from __future__ import annotations

from oil_tracker.domain.enums import EventType


EVENT_TYPE_LABELS: dict[EventType, str] = {
    EventType.ANALYSIS_START: "분석 시작",
    EventType.ANALYSIS_END: "분석 종료",
    EventType.COMPRESSOR_START: "압축기 기동",
    EventType.OIL_BOUNDARY_APPEARED_FROM_TOP: "상단에서 유면 출현",
    EventType.OIL_BOUNDARY_APPEARED_FROM_BOTTOM: "하단에서 유면 출현",
    EventType.OIL_DROP_START: "유면 하강 최초 관찰",
    EventType.MAXIMUM_OIL_LEVEL: "관측 최고 유면",
    EventType.MINIMUM_OIL_LEVEL: "관측 최저 유면",
    EventType.ZERO_CROSS_UP: "기준점 상향 통과",
    EventType.ZERO_CROSS_DOWN: "기준점 하향 통과",
    EventType.ZERO_STABLE_RECOVERY: "기준점 안정 회복",
    EventType.FULL_NO_INTERFACE_START: "가득 참 시작",
    EventType.EMPTY_NO_INTERFACE_START: "비어 있음 시작",
    EventType.FOAM_START: "거품 발생",
    EventType.FOAM_FRONT_RISING: "거품 경계 상승",
    EventType.FOAM_REACH_ZERO: "거품 기준점 도달",
    EventType.FOAM_REACH_TOP: "거품 상단 도달",
    EventType.FOAM_END: "거품 소멸",
    EventType.LOW_CONFIDENCE_START: "낮은 신뢰도 시작",
    EventType.LOW_CONFIDENCE_END: "낮은 신뢰도 종료",
    EventType.DETECTION_LOST: "검출 유실",
    EventType.FOGGED_OR_GLARE: "흐림 또는 반사광",
    EventType.REVIEW_REQUIRED: "사용자 확인 필요",
    EventType.JUDGMENT_PASS: "판정 합격",
    EventType.JUDGMENT_FAIL: "판정 불합격",
}


def event_type_label(event_type: EventType) -> str:
    return EVENT_TYPE_LABELS.get(event_type, event_type.value)
