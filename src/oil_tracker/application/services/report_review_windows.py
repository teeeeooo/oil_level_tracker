"""Deterministic review budgets; never detector identity or trajectory repair."""
from __future__ import annotations

from dataclasses import dataclass
import math

from oil_tracker.domain.enums import EventType

MAX_REVIEW_WINDOWS = 4
EXTREMUM_CONTEXT_SEC = 2.0


@dataclass(frozen=True)
class SourceReviewWindow:
    start_sec: float
    end_sec: float
    reasons: tuple[str, ...]


def plan_source_review_windows(presentation, start: float, end: float) -> tuple[SourceReviewWindow, ...]:
    if not all(math.isfinite(x) for x in (start, end)) or start < 0 or end < start:
        raise ValueError("Invalid source review interval.")
    requests = []
    scenes = presentation.scene_captures
    if scenes:
        requests.append((scenes[0].timestamp_sec, scenes[-1].timestamp_sec, "가장 긴 Oil 관측 공백"))
    elif not presentation.has_oil or presentation.unavailable_intervals:
        requests.append((start, end, "관측 부족 구간을 포함한 전체 맥락"))
    for landmark in presentation.landmarks:
        if landmark.event_type in {EventType.MAXIMUM_OIL_LEVEL, EventType.MINIMUM_OIL_LEVEL}:
            label = "검출 최고값 주변" if landmark.event_type is EventType.MAXIMUM_OIL_LEVEL else "검출 최저값 주변"
            requests.append((landmark.timestamp_sec - EXTREMUM_CONTEXT_SEC,
                             landmark.timestamp_sec + EXTREMUM_CONTEXT_SEC, label))
    if not requests:
        requests.append((start, end, "전체 분석 구간 맥락"))
    # Broad gap/Foam context must not swallow a native-cadence extrema zoom.
    extrema = [r for r in requests if r[2].startswith("검출 ")]
    broad = [r for r in requests if not r[2].startswith("검출 ")]
    episodes = [item for item in presentation.landmarks
                if item.event_type is EventType.FOAM_START and item.end_time_sec is not None]
    if episodes:
        episode = max(episodes, key=lambda x: (x.end_time_sec - x.timestamp_sec, -x.timestamp_sec))
        broad.append((episode.timestamp_sec - EXTREMUM_CONTEXT_SEC,
                      episode.end_time_sec + EXTREMUM_CONTEXT_SEC, "주요 Foam 관측 구간"))
    clipped = sorted((max(start, a), min(end, b), reason) for a, b, reason in extrema
                     if math.isfinite(a) and math.isfinite(b) and b >= start and a <= end)
    merged: list[SourceReviewWindow] = []
    for a, b, reason in clipped:
        if merged and a <= merged[-1].end_sec:
            previous = merged.pop()
            merged.append(SourceReviewWindow(previous.start_sec, max(previous.end_sec, b),
                          tuple(dict.fromkeys((*previous.reasons, reason)))))
        else:
            merged.append(SourceReviewWindow(a, b, (reason,)))
    for a, b, reason in broad:
        a, b = max(start, a), min(end, b)
        if math.isfinite(a) and math.isfinite(b) and a <= b:
            existing = next((x for x in merged if x.start_sec == a and x.end_sec == b), None)
            if existing:
                merged[merged.index(existing)] = SourceReviewWindow(a, b, (*existing.reasons, reason))
            else:
                merged.append(SourceReviewWindow(a, b, (reason,)))
    return tuple(sorted(merged, key=lambda x: (x.start_sec, x.end_sec))[:MAX_REVIEW_WINDOWS])
