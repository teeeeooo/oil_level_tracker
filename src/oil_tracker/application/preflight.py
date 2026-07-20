from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json
import math

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


class PreflightStatus(str, Enum):
    NORMAL = "normal"
    REVIEW = "review"
    FAILURE = "failure"


@dataclass(frozen=True)
class PreflightPolicy:
    compressor_min_offset_sec: float = 0.05
    end_guard_min_sec: float = 0.001
    position_jump_ratio: float = 0.35


DEFAULT_PREFLIGHT_POLICY = PreflightPolicy()


@dataclass(frozen=True)
class PreflightSampleRequest:
    labels: tuple[str, ...]
    requested_timestamps: tuple[float, ...]
    normalized_timestamp: float
    frame_key: int

    @property
    def label(self) -> str:
        return " · ".join(self.labels)

    @property
    def requested_timestamp(self) -> float:
        return self.requested_timestamps[0]


@dataclass(frozen=True)
class PreflightSamplePoint:
    labels: tuple[str, ...]
    requested_timestamps: tuple[float, ...]
    requested_timestamp: float
    actual_timestamp: float
    frame_index: int

    @property
    def label(self) -> str:
        return " · ".join(self.labels)


@dataclass(frozen=True)
class PreflightDetectionResult:
    glass_id: str
    glass_name: str
    sample_point: PreflightSamplePoint
    fill_state: FillState | None
    confidence: float | None
    oil_level_y: float | None
    oil_level_px_from_zero: float | None
    oil_level_mm_from_zero: float | None
    foam_detected: bool
    flags: tuple[str, ...]
    status: PreflightStatus
    reason: str


@dataclass(frozen=True)
class PreflightGlassSummary:
    glass_id: str
    glass_name: str
    minimum_confidence: float | None
    normal_count: int
    review_count: int
    failure_count: int
    representative_issue_timestamp: float | None
    representative_issue_reason: str
    position_jump_detected: bool


@dataclass(frozen=True)
class PreflightResult:
    overall_status: PreflightStatus
    samples: tuple[PreflightDetectionResult, ...]
    glass_summaries: tuple[PreflightGlassSummary, ...]
    video_path: str
    context_key: str
    analysis_start_sec: float
    analysis_end_sec: float
    compressor_start_sec: float | None


@dataclass(frozen=True)
class PreflightProgress:
    completed: int
    total: int
    sample_label: str
    glass_name: str


class PreflightCancelled(RuntimeError):
    pass


def build_preflight_schedule(
    start_sec: float,
    end_sec: float,
    metadata: VideoMetadata,
    compressor_start_sec: float | None,
    policy: PreflightPolicy = DEFAULT_PREFLIGHT_POLICY,
) -> list[PreflightSampleRequest]:
    if not math.isfinite(start_sec) or not math.isfinite(end_sec) or end_sec <= start_sec:
        raise ValueError("사전 점검 분석 구간이 올바르지 않습니다.")
    if metadata.fps <= 0:
        raise ValueError("영상 FPS 정보가 없어 대표 시점을 만들 수 없습니다.")

    duration = metadata.duration_sec if metadata.duration_sec > 0 else end_sec
    bounded_end = min(end_sec, duration)
    if bounded_end <= start_sec:
        raise ValueError("영상 범위 안에 사전 점검할 구간이 없습니다.")

    frame_period = 1.0 / metadata.fps
    last_decodable = max(start_sec, bounded_end - max(frame_period, policy.end_guard_min_sec))
    span = bounded_end - start_sec
    candidates: list[tuple[str, float]] = [("분석 시작", start_sec)]

    if compressor_start_sec is not None and start_sec <= compressor_start_sec <= bounded_end:
        offset = max(frame_period, policy.compressor_min_offset_sec)
        candidates.append(("압축기 기동 직후", min(last_decodable, compressor_start_sec + offset)))

    candidates.extend(
        (
            ("분석 구간 25%", start_sec + span * 0.25),
            ("분석 구간 50%", start_sec + span * 0.50),
            ("분석 구간 75%", start_sec + span * 0.75),
            ("분석 종료 직전", last_decodable),
        )
    )

    minimum_frame = int(math.ceil(start_sec * metadata.fps - 1e-9))
    maximum_frame = int(math.floor(last_decodable * metadata.fps + 1e-9))
    if metadata.frame_count > 0:
        maximum_frame = min(maximum_frame, metadata.frame_count - 1)
    if maximum_frame < minimum_frame:
        minimum_frame = maximum_frame = max(0, int(round(start_sec * metadata.fps)))
        if metadata.frame_count > 0:
            minimum_frame = maximum_frame = min(minimum_frame, metadata.frame_count - 1)

    merged: dict[int, dict[str, list]] = {}
    for label, requested in candidates:
        bounded = min(last_decodable, max(start_sec, requested))
        frame_key = int(round(bounded * metadata.fps))
        frame_key = min(maximum_frame, max(minimum_frame, frame_key))
        normalized = frame_key / metadata.fps
        entry = merged.setdefault(frame_key, {"labels": [], "requested": [], "normalized": normalized})
        if label not in entry["labels"]:
            entry["labels"].append(label)
        entry["requested"].append(float(requested))

    return [
        PreflightSampleRequest(
            labels=tuple(merged[key]["labels"]),
            requested_timestamps=tuple(merged[key]["requested"]),
            normalized_timestamp=float(merged[key]["normalized"]),
            frame_key=key,
        )
        for key in sorted(merged)
    ]


def preflight_context_key(recipe: InspectionRecipe, session: AnalysisSession) -> str:
    metadata = session.video_metadata
    payload = {
        "recipe": recipe.to_dict(),
        "session": {
            "input_video_path": session.input_video_path,
            "video": None
            if metadata is None
            else {
                "path": metadata.path,
                "width": metadata.width,
                "height": metadata.height,
                "fps": metadata.fps,
                "duration_sec": metadata.duration_sec,
                "frame_count": metadata.frame_count,
            },
            "analysis_start_sec": session.analysis_start_sec,
            "analysis_end_sec": session.effective_end_sec(),
            "compressor_start_sec": session.compressor_start_sec,
            "sampling_fps": session.sampling_fps,
            "resolution_confirmed": session.resolution_confirmed,
        },
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def apply_position_jump_warnings(
    results: list[PreflightDetectionResult],
    glass_by_id: dict[str, object],
    policy: PreflightPolicy = DEFAULT_PREFLIGHT_POLICY,
) -> list[PreflightDetectionResult]:
    updated = list(results)
    indices_by_glass: dict[str, list[int]] = {}
    for index, result in enumerate(updated):
        if result.oil_level_y is not None and result.status != PreflightStatus.FAILURE:
            indices_by_glass.setdefault(result.glass_id, []).append(index)

    for glass_id, indices in indices_by_glass.items():
        glass = glass_by_id[glass_id]
        effective_height = max(
            1.0,
            2.0 * float(glass.geometry.ellipse.radius_y) * (1.0 - float(glass.geometry.margin_ratio)),
        )
        previous_index: int | None = None
        for index in indices:
            if previous_index is not None:
                previous = updated[previous_index]
                current = updated[index]
                jump_ratio = abs(float(current.oil_level_y) - float(previous.oil_level_y)) / effective_height
                if jump_ratio >= policy.position_jump_ratio:
                    flags = tuple(sorted(set(current.flags) | {"PREFLIGHT_POSITION_JUMP"}))
                    reason = "인접 대표 시점 대비 유면 위치가 급격히 변했습니다"
                    if current.status == PreflightStatus.REVIEW and current.reason:
                        reason = f"{current.reason}; {reason}"
                    updated[index] = replace(
                        current,
                        status=PreflightStatus.REVIEW,
                        reason=reason,
                        flags=flags,
                    )
            previous_index = index
    return updated


def summarize_preflight(
    results: list[PreflightDetectionResult],
    enabled_glasses: list[object],
) -> tuple[tuple[PreflightGlassSummary, ...], PreflightStatus]:
    summaries: list[PreflightGlassSummary] = []
    for glass in enabled_glasses:
        items = sorted(
            (result for result in results if result.glass_id == glass.id),
            key=lambda result: (result.sample_point.actual_timestamp, result.sample_point.frame_index),
        )
        confidences = [float(item.confidence) for item in items if item.confidence is not None]
        representative = next(
            (item for status in (PreflightStatus.FAILURE, PreflightStatus.REVIEW) for item in items if item.status == status),
            None,
        )
        summaries.append(
            PreflightGlassSummary(
                glass_id=glass.id,
                glass_name=glass.name,
                minimum_confidence=min(confidences) if confidences else None,
                normal_count=sum(item.status == PreflightStatus.NORMAL for item in items),
                review_count=sum(item.status == PreflightStatus.REVIEW for item in items),
                failure_count=sum(item.status == PreflightStatus.FAILURE for item in items),
                representative_issue_timestamp=None if representative is None else representative.sample_point.actual_timestamp,
                representative_issue_reason="" if representative is None else representative.reason,
                position_jump_detected=any("PREFLIGHT_POSITION_JUMP" in item.flags for item in items),
            )
        )

    if any(item.status == PreflightStatus.FAILURE for item in results):
        overall = PreflightStatus.FAILURE
    elif any(item.status == PreflightStatus.REVIEW for item in results):
        overall = PreflightStatus.REVIEW
    else:
        overall = PreflightStatus.NORMAL
    return tuple(summaries), overall
