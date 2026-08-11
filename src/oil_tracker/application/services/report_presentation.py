from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median

from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.recipe import GlassInspectionConfig, InspectionRecipe
from oil_tracker.domain.results import (
    AnalysisResult,
    EventMarker,
    GlassAnalysisResult,
    TrackingSample,
)

from .event_presentation import event_type_label


MAX_REPORT_LANDMARKS = 12
MAX_REPORT_FOAM_EPISODES = 3
MINIMUM_FOAM_EPISODE_SEC = 0.5


@dataclass
class ReportLandmark:
    event_type: EventType
    timestamp_sec: float
    label: str
    description: str
    sample: TrackingSample | None
    emphasis: str
    end_time_sec: float | None = None
    source_event: EventMarker | None = None
    capture_path: str = ""
    priority: int = 100

    @property
    def oil_level_px(self) -> float | None:
        return _oil_px(self.sample)

    @property
    def oil_level_mm(self) -> float | None:
        return _oil_mm(self.sample)

    @property
    def foam_front_px(self) -> float | None:
        return _foam_px(self.sample)

    @property
    def foam_front_mm(self) -> float | None:
        return _foam_mm(self.sample)


@dataclass(frozen=True)
class ReportUnavailableInterval:
    start_time_sec: float
    end_time_sec: float

    @property
    def duration_sec(self) -> float:
        return max(0.0, self.end_time_sec - self.start_time_sec)

    @property
    def display(self) -> str:
        return f"{self.start_time_sec:.1f}–{self.end_time_sec:.1f}초"


@dataclass(frozen=True)
class ReportGlassPresentation:
    glass_id: str
    glass_name: str
    result_state: ResultState
    result_state_label: str
    movement_summary: str
    observation_note: str
    judgment_summary: str
    landmarks: tuple[ReportLandmark, ...]
    unavailable_intervals: tuple[ReportUnavailableInterval, ...]
    finite_oil_count: int
    foam_episode_count: int

    @property
    def has_oil(self) -> bool:
        return self.finite_oil_count > 0


@dataclass(frozen=True)
class ReportPresentation:
    overall_state: ResultState
    overall_state_label: str
    glasses: tuple[ReportGlassPresentation, ...]

    def for_glass(self, glass_id: str) -> ReportGlassPresentation | None:
        return next((item for item in self.glasses if item.glass_id == glass_id), None)

    @property
    def landmarks(self) -> tuple[ReportLandmark, ...]:
        return tuple(
            landmark
            for glass in self.glasses
            for landmark in glass.landmarks
        )


@dataclass(frozen=True)
class _FoamEpisode:
    start: TrackingSample
    last_present: TrackingSample
    disappearance: TrackingSample | None
    positive_count: int

    @property
    def duration_sec(self) -> float:
        return max(0.0, self.last_present.timestamp_sec - self.start.timestamp_sec)


def build_report_presentation(
    result: AnalysisResult,
    recipe: InspectionRecipe,
) -> ReportPresentation:
    configs = {glass.id: glass for glass in recipe.glasses}
    glasses = tuple(
        build_glass_report_presentation(
            glass_result,
            configs.get(glass_result.glass_id),
        )
        for glass_result in result.glass_results
    )
    return ReportPresentation(
        overall_state=result.overall_state,
        overall_state_label=_result_state_label(result.overall_state),
        glasses=glasses,
    )


def build_glass_report_presentation(
    glass: GlassAnalysisResult,
    config: GlassInspectionConfig | None,
) -> ReportGlassPresentation:
    samples = tuple(sorted(glass.samples, key=lambda item: (item.timestamp_sec, item.frame_index)))
    numeric = tuple((sample, _oil_px(sample)) for sample in samples if _oil_px(sample) is not None)
    cadence = _sample_cadence(samples)
    unavailable = _unavailable_intervals(samples, cadence)
    extrema = _extrema_landmarks(glass, numeric)
    foam_episodes = _foam_episodes(samples, cadence)
    foam_landmarks = _foam_landmarks(glass, foam_episodes)
    physical = _physical_event_landmarks(glass, samples, cadence)
    selected = _bounded_landmarks((*extrema, *foam_landmarks, *physical))
    has_missing_oil = len(numeric) < len(samples)
    has_internal_gap, has_edge_missing = _oil_gap_shape(samples)
    movement_summary = _movement_summary(
        config,
        numeric,
        len(foam_episodes),
        has_missing_oil,
    )
    observation_note = _observation_note(
        unavailable,
        has_missing_oil,
        has_internal_gap,
        has_edge_missing,
        bool(numeric),
    )
    return ReportGlassPresentation(
        glass_id=glass.glass_id,
        glass_name=glass.glass_name,
        result_state=glass.result_state,
        result_state_label=_result_state_label(glass.result_state),
        movement_summary=movement_summary,
        observation_note=observation_note,
        judgment_summary=_judgment_summary(glass.result_state),
        landmarks=selected,
        unavailable_intervals=unavailable,
        finite_oil_count=len(numeric),
        foam_episode_count=len(foam_episodes),
    )


def format_landmark_level(
    landmark: ReportLandmark,
    config: GlassInspectionConfig | None,
) -> str:
    if landmark.event_type is EventType.COMPRESSOR_START:
        return "시험 기준 시점"
    if landmark.event_type in {EventType.FOAM_START, EventType.FOAM_END}:
        if config is not None and config.mm_per_pixel is not None and config.mm_per_pixel > 0:
            if landmark.foam_front_mm is not None:
                return f"거품 경계 {landmark.foam_front_mm:+.2f} mm"
        if landmark.foam_front_px is not None:
            return f"거품 경계 {landmark.foam_front_px:+.1f} px"
        if landmark.event_type is EventType.FOAM_END:
            return "거품 경계가 더 이상 관측되지 않음"
        return "거품 경계 위치값 없음"
    if config is not None and config.mm_per_pixel is not None and config.mm_per_pixel > 0:
        if landmark.oil_level_mm is not None:
            return f"유면 {landmark.oil_level_mm:+.2f} mm"
    if landmark.oil_level_px is not None:
        return f"유면 {landmark.oil_level_px:+.1f} px"
    return "위치값 없음"


def _extrema_landmarks(
    glass: GlassAnalysisResult,
    numeric: tuple[tuple[TrackingSample, float | None], ...],
) -> tuple[ReportLandmark, ...]:
    if not numeric:
        return ()
    finite = tuple((sample, float(value)) for sample, value in numeric if value is not None)
    trusted = (
        tuple(item for item in finite if _r7_anchor(item[0]))
        if _is_r7_stream(sample for sample, _value in finite)
        else finite
    )
    if not trusted:
        return ()
    maximum = max(trusted, key=lambda item: (item[1], -item[0].timestamp_sec))[0]
    minimum = min(trusted, key=lambda item: (item[1], item[0].timestamp_sec))[0]
    return (
        _landmark_from_sample(
            glass,
            EventType.MAXIMUM_OIL_LEVEL,
            maximum,
            "관측된 유면이 가장 높았던 시점입니다.",
            "maximum",
            priority=0,
        ),
        _landmark_from_sample(
            glass,
            EventType.MINIMUM_OIL_LEVEL,
            minimum,
            "관측된 유면이 가장 낮았던 시점입니다.",
            "minimum",
            priority=0,
        ),
    )


def _foam_episodes(
    samples: tuple[TrackingSample, ...],
    cadence: float,
) -> tuple[_FoamEpisode, ...]:
    support = [
        index
        for index, sample in enumerate(samples)
        if _foam_present(sample) or _foam_confirmation_pending(sample)
    ]
    if not support:
        return ()
    dropout_tolerance = max(0.5, min(1.0, cadence))
    groups: list[list[int]] = [[support[0]]]
    for index in support[1:]:
        previous = groups[-1][-1]
        absent_span = samples[index].timestamp_sec - samples[previous].timestamp_sec - cadence
        if absent_span <= dropout_tolerance + 1e-9:
            groups[-1].append(index)
        else:
            groups.append([index])

    episodes: list[_FoamEpisode] = []
    for support_group in groups:
        accepted_group = [
            index for index in support_group if _foam_present(samples[index])
        ]
        if not accepted_group:
            continue
        start_index = accepted_group[0]
        end_index = accepted_group[-1]
        start = samples[start_index]
        last = samples[end_index]
        short_group = (
            len(accepted_group) < 2
            or last.timestamp_sec - start.timestamp_sec
            < MINIMUM_FOAM_EPISODE_SEC - 1e-9
        )
        if short_group and not (
            len(accepted_group) == 1 and _confirmed_foam_publication(start)
        ):
            continue
        support_end_index = support_group[-1]
        disappearance = (
            samples[support_end_index + 1]
            if support_end_index + 1 < len(samples)
            else None
        )
        episodes.append(
            _FoamEpisode(start, last, disappearance, len(accepted_group))
        )

    material = sorted(
        episodes,
        key=lambda item: (-item.duration_sec, -item.positive_count, item.start.timestamp_sec),
    )[:MAX_REPORT_FOAM_EPISODES]
    return tuple(sorted(material, key=lambda item: item.start.timestamp_sec))


def _foam_landmarks(
    glass: GlassAnalysisResult,
    episodes: tuple[_FoamEpisode, ...],
) -> tuple[ReportLandmark, ...]:
    output: list[ReportLandmark] = []
    for number, episode in enumerate(episodes, start=1):
        start = _landmark_from_sample(
            glass,
            EventType.FOAM_START,
            episode.start,
            f"확인된 거품 관측 구간 {number}이 시작된 시점입니다.",
            "foam",
            priority=10,
            end_time_sec=episode.last_present.timestamp_sec,
        )
        start.label = f"거품 발생 {number}"
        output.append(start)
        if episode.disappearance is not None:
            end = _landmark_from_sample(
                glass,
                EventType.FOAM_END,
                episode.disappearance,
                f"거품 관측 구간 {number} 이후 처음으로 거품이 보이지 않은 시점입니다.",
                "foam",
                priority=10,
            )
            end.label = f"거품 소멸 {number}"
            output.append(end)
    return tuple(output)


def _physical_event_landmarks(
    glass: GlassAnalysisResult,
    samples: tuple[TrackingSample, ...],
    cadence: float,
) -> tuple[ReportLandmark, ...]:
    descriptions = {
        EventType.COMPRESSOR_START: "시험에서 기록한 압축기 기동 시점입니다.",
        EventType.OIL_DROP_START: (
            "저장된 관측에서 유면의 지속 하강이 처음 확인된 시점입니다. "
            "관측 공백이 있으면 실제 물리적 시작은 더 이를 수 있습니다."
        ),
        EventType.ZERO_CROSS_DOWN: "관측 유면이 기준점 아래로 이동한 시점입니다.",
        EventType.ZERO_CROSS_UP: "관측 유면이 기준점 위로 회복된 시점입니다.",
        EventType.ZERO_STABLE_RECOVERY: "관측 유면이 기준점 위에서 안정적으로 유지되기 시작한 시점입니다.",
        EventType.OIL_BOUNDARY_APPEARED_FROM_TOP: "상단에서 유면 경계가 처음 관측된 시점입니다.",
        EventType.OIL_BOUNDARY_APPEARED_FROM_BOTTOM: "하단에서 유면 경계가 처음 관측된 시점입니다.",
    }
    emphasis = {
        EventType.COMPRESSOR_START: "timing",
        EventType.OIL_DROP_START: "oil",
        EventType.ZERO_CROSS_DOWN: "oil",
        EventType.ZERO_CROSS_UP: "oil",
        EventType.ZERO_STABLE_RECOVERY: "oil",
        EventType.OIL_BOUNDARY_APPEARED_FROM_TOP: "oil",
        EventType.OIL_BOUNDARY_APPEARED_FROM_BOTTOM: "oil",
    }
    output: list[ReportLandmark] = []
    seen: set[EventType] = set()
    for event in sorted(glass.events, key=lambda item: (item.start_time_sec, item.event_type.value)):
        if event.event_type not in descriptions or event.event_type in seen:
            continue
        seen.add(event.event_type)
        sample = _nearest_sample(samples, event.start_time_sec, cadence)
        output.append(
            ReportLandmark(
                event_type=event.event_type,
                timestamp_sec=float(event.start_time_sec),
                end_time_sec=event.end_time_sec,
                label=event_type_label(event.event_type),
                description=descriptions[event.event_type],
                sample=sample,
                emphasis=emphasis[event.event_type],
                source_event=event,
                priority=20,
            )
        )
    return tuple(output)


def _landmark_from_sample(
    glass: GlassAnalysisResult,
    event_type: EventType,
    sample: TrackingSample,
    description: str,
    emphasis: str,
    *,
    priority: int,
    end_time_sec: float | None = None,
) -> ReportLandmark:
    source = _nearest_event(glass.events, event_type, sample.timestamp_sec)
    return ReportLandmark(
        event_type=event_type,
        timestamp_sec=float(sample.timestamp_sec),
        end_time_sec=end_time_sec,
        label=event_type_label(event_type),
        description=description,
        sample=sample,
        emphasis=emphasis,
        source_event=source,
        priority=priority,
    )


def _bounded_landmarks(landmarks: tuple[ReportLandmark, ...]) -> tuple[ReportLandmark, ...]:
    unique: dict[tuple[EventType, float], ReportLandmark] = {}
    for landmark in landmarks:
        key = (landmark.event_type, round(landmark.timestamp_sec, 6))
        incumbent = unique.get(key)
        if incumbent is None or landmark.priority < incumbent.priority:
            unique[key] = landmark
    selected = sorted(
        unique.values(),
        key=lambda item: (item.priority, item.timestamp_sec, item.event_type.value),
    )[:MAX_REPORT_LANDMARKS]
    return tuple(sorted(selected, key=lambda item: (item.timestamp_sec, item.event_type.value)))


def _movement_summary(
    config: GlassInspectionConfig | None,
    numeric: tuple[tuple[TrackingSample, float | None], ...],
    foam_episode_count: int,
    has_unavailable: bool,
) -> str:
    if not numeric:
        return "직접 관측된 유면 위치가 없어 상승·하강 흐름을 확정할 수 없습니다."
    finite = tuple((sample, float(value)) for sample, value in numeric if value is not None)
    first_sample, first_value = finite[0]
    last_sample, last_value = finite[-1]
    height = 0.0
    if config is not None:
        height = 2.0 * float(config.geometry.ellipse.radius_y)
    tolerance = max(2.0, 0.03 * height)
    delta = last_value - first_value
    if delta > tolerance:
        direction = "높아졌습니다"
    elif delta < -tolerance:
        direction = "낮아졌습니다"
    else:
        direction = "비슷한 높이로 유지되었습니다"
    first_text = _sample_level_text(first_sample, config)
    last_text = _sample_level_text(last_sample, config)
    qualifier = "관측 가능한 지점을 기준으로 " if has_unavailable else ""
    summary = (
        f"{qualifier}{first_sample.timestamp_sec:.1f}초 {first_text}에서 시작해 "
        f"{last_sample.timestamp_sec:.1f}초 {last_text}로 {direction}."
    )
    meaningful_deltas = [
        current_value - previous_value
        for (_previous_sample, previous_value), (_current_sample, current_value) in zip(
            finite,
            finite[1:],
        )
        if abs(current_value - previous_value) > tolerance
    ]
    if any(change > 0 for change in meaningful_deltas) and any(
        change < 0 for change in meaningful_deltas
    ):
        summary += " 분석 구간 중 상승과 하강이 모두 관측되었습니다."
    trusted = (
        tuple(item for item in finite if _r7_anchor(item[0]))
        if _is_r7_stream(sample for sample, _value in finite)
        else finite
    )
    extrema_source = trusted or finite
    maximum_sample, _ = max(
        extrema_source,
        key=lambda item: (item[1], -item[0].timestamp_sec),
    )
    minimum_sample, _ = min(
        extrema_source,
        key=lambda item: (item[1], item[0].timestamp_sec),
    )
    summary += (
        f" 관측 최고는 {maximum_sample.timestamp_sec:.1f}초 {_sample_level_text(maximum_sample, config)},"
        f" 관측 최저는 {minimum_sample.timestamp_sec:.1f}초 {_sample_level_text(minimum_sample, config)}입니다."
    )
    if foam_episode_count:
        summary += f" 보고서에 표시한 주요 거품 관측 구간은 {foam_episode_count}회입니다."
    return summary


def _observation_note(
    intervals: tuple[ReportUnavailableInterval, ...],
    has_missing_oil: bool,
    has_internal_gap: bool,
    has_edge_missing: bool,
    has_oil: bool,
) -> str:
    if not has_missing_oil:
        return "그래프의 실선은 연속된 직접 관측 구간입니다."
    if not has_oil:
        return "분석 구간에 직접 관측된 유면 위치가 없어 유면 선을 표시하지 않습니다."
    parts: list[str] = []
    if intervals:
        shown = ", ".join(interval.display for interval in intervals[:3])
        suffix = "" if len(intervals) <= 3 else f" 외 {len(intervals) - 3}개 구간"
        parts.append(f"직접 유면 위치가 없는 주요 구간은 {shown}{suffix}입니다.")
    if has_internal_gap:
        gap_name = "짧은 직접 관측 공백" if not intervals else "직접 관측 공백"
        parts.append(
            f"{gap_name}을 건너는 점선은 앞뒤 관측점을 연결한 것이며 "
            "중간 측정값을 뜻하지 않습니다."
        )
    if has_edge_missing:
        parts.append("첫 관측 전이나 마지막 관측 후의 공백에는 유면 선을 임의로 연장하지 않습니다.")
    return " ".join(parts)


def _oil_gap_shape(samples: tuple[TrackingSample, ...]) -> tuple[bool, bool]:
    finite_indices = [index for index, sample in enumerate(samples) if _oil_px(sample) is not None]
    if not finite_indices:
        return False, bool(samples)
    first = finite_indices[0]
    last = finite_indices[-1]
    has_internal_gap = any(_oil_px(sample) is None for sample in samples[first : last + 1])
    return has_internal_gap, first > 0 or last < len(samples) - 1


def _unavailable_intervals(
    samples: tuple[TrackingSample, ...],
    cadence: float,
) -> tuple[ReportUnavailableInterval, ...]:
    groups: list[tuple[TrackingSample, TrackingSample]] = []
    start: TrackingSample | None = None
    last: TrackingSample | None = None
    for sample in samples:
        if _oil_px(sample) is None:
            start = start or sample
            last = sample
        elif start is not None and last is not None:
            groups.append((start, last))
            start = last = None
    if start is not None and last is not None:
        groups.append((start, last))
    minimum = max(1.0, cadence)
    intervals = [
        ReportUnavailableInterval(begin.timestamp_sec, end.timestamp_sec)
        for begin, end in groups
        if end.timestamp_sec - begin.timestamp_sec >= minimum - 1e-9
    ]
    return tuple(intervals)


def _nearest_event(
    events: list[EventMarker],
    event_type: EventType,
    timestamp_sec: float,
) -> EventMarker | None:
    candidates = [event for event in events if event.event_type is event_type]
    if not candidates:
        return None
    selected = min(candidates, key=lambda item: abs(item.start_time_sec - timestamp_sec))
    return selected if abs(selected.start_time_sec - timestamp_sec) <= 1e-6 else None


def _nearest_sample(
    samples: tuple[TrackingSample, ...],
    timestamp_sec: float,
    cadence: float,
) -> TrackingSample | None:
    if not samples:
        return None
    selected = min(samples, key=lambda item: abs(item.timestamp_sec - timestamp_sec))
    return selected if abs(selected.timestamp_sec - timestamp_sec) <= max(1.0, cadence * 1.5) else None


def _sample_cadence(samples: tuple[TrackingSample, ...]) -> float:
    deltas = [
        current.timestamp_sec - previous.timestamp_sec
        for previous, current in zip(samples, samples[1:])
        if current.timestamp_sec > previous.timestamp_sec
    ]
    return float(median(deltas)) if deltas else 0.5


def _sample_level_text(
    sample: TrackingSample,
    config: GlassInspectionConfig | None,
) -> str:
    if config is not None and config.mm_per_pixel is not None and config.mm_per_pixel > 0:
        value_mm = _oil_mm(sample)
        if value_mm is not None:
            return f"{value_mm:+.2f} mm"
    value_px = _oil_px(sample)
    return "위치값 없음" if value_px is None else f"{value_px:+.1f} px"


def _oil_px(sample: TrackingSample | None) -> float | None:
    if sample is None:
        return None
    return _finite_first(
        sample.smoothed_oil_air_level_px_from_zero,
        sample.raw_oil_air_level_px_from_zero,
    )


def _oil_mm(sample: TrackingSample | None) -> float | None:
    if sample is None:
        return None
    return _finite_first(
        sample.smoothed_oil_air_level_mm_from_zero,
        sample.raw_oil_air_level_mm_from_zero,
    )


def _foam_px(sample: TrackingSample | None) -> float | None:
    if sample is None:
        return None
    return _finite_first(
        sample.smoothed_foam_front_px_from_zero,
        sample.raw_foam_front_px_from_zero,
    )


def _foam_mm(sample: TrackingSample | None) -> float | None:
    if sample is None:
        return None
    return _finite_first(
        sample.smoothed_foam_front_mm_from_zero,
        sample.raw_foam_front_mm_from_zero,
    )


def _foam_present(sample: TrackingSample) -> bool:
    return (
        _foam_px(sample) is not None
        or _finite_first(sample.raw_foam_front_y) is not None
        or sample.fill_state in {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE}
    )


def _confirmed_foam_publication(sample: TrackingSample) -> bool:
    return any(
        flag in {"FOAM_STRONG_EVIDENCE", "FOAM_MODERATE_EVIDENCE"}
        for flag in sample.flags
    )


def _foam_confirmation_pending(sample: TrackingSample) -> bool:
    return "FOAM_PERSISTENCE_PENDING" in sample.flags


def _is_r7_stream(samples) -> bool:
    return any(
        any(str(flag).strip().upper().startswith("R7_") for flag in sample.flags)
        for sample in samples
    )


def _r7_anchor(sample: TrackingSample) -> bool:
    return "R7_OIL_ANCHOR" in {
        str(flag).strip().upper() for flag in sample.flags
    }


def _finite_first(*values: float | None) -> float | None:
    for value in values:
        if value is None:
            continue
        number = float(value)
        if math.isfinite(number):
            return number
    return None


def _result_state_label(state: ResultState) -> str:
    return {
        ResultState.PASS: "합격",
        ResultState.FAIL: "불합격",
        ResultState.REVIEW_REQUIRED: "사용자 확인 필요",
        ResultState.NOT_APPLICABLE: "판정 대상 아님",
    }.get(state, state.value)


def _judgment_summary(state: ResultState) -> str:
    return {
        ResultState.PASS: "설정된 판정 기준을 충족했습니다.",
        ResultState.FAIL: "설정된 판정 기준을 충족하지 못했습니다.",
        ResultState.REVIEW_REQUIRED: "자동 판정을 확정할 수 없어 사용자 확인이 필요합니다.",
        ResultState.NOT_APPLICABLE: "이 Glass는 판정 대상이 아닙니다.",
    }.get(state, "판정 내용을 확인해 주세요.")
