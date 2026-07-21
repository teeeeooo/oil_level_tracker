from __future__ import annotations

from dataclasses import asdict
import json
from uuid import uuid4

from oil_tracker.application.services.analysis_pipeline import timestamp_schedule
from oil_tracker.application.services.detector_settings import detector_settings_to_json
from oil_tracker.domain.redetection import (
    RedetectionMode,
    RedetectionPolicy,
    RedetectionRange,
    RedetectionRequest,
)


class RedetectionRequestError(ValueError):
    pass


def build_redetection_range(
    bundle,
    target_timestamp_sec: float,
    mode: RedetectionMode,
    *,
    before_sec: float | None = None,
    after_sec: float | None = None,
    policy: RedetectionPolicy | None = None,
) -> RedetectionRange:
    policy = policy or RedetectionPolicy()
    start = float(bundle.analysis_start_sec)
    end = float(bundle.analysis_end_sec)
    target = min(end, max(start, float(target_timestamp_sec)))
    if mode is RedetectionMode.CURRENT:
        return RedetectionRange(target, target, target)
    if mode is RedetectionMode.FULL:
        return RedetectionRange(start, end, start)
    before = policy.short_before_sec if before_sec is None else float(before_sec)
    after = policy.short_after_sec if after_sec is None else float(after_sec)
    if before < 0 or after < 0:
        raise RedetectionRequestError("앞뒤 구간 길이는 0초 이상이어야 합니다.")
    if before + after > policy.short_max_display_duration_sec + 1e-9:
        raise RedetectionRequestError(
            f"짧은 구간의 전체 길이는 {policy.short_max_display_duration_sec:g}초를 초과할 수 없습니다."
        )
    display_start = max(start, target - before)
    display_end = min(end, target + after)
    warmup_start = max(start, display_start - policy.short_warmup_sec)
    return RedetectionRange(display_start, display_end, warmup_start)


def build_redetection_request(
    bundle,
    source_video_path,
    selected_glass_id: str,
    target_timestamp_sec: float,
    mode: RedetectionMode,
    detector_settings,
    generation: int,
    *,
    before_sec: float | None = None,
    after_sec: float | None = None,
    policy: RedetectionPolicy | None = None,
) -> RedetectionRequest:
    glass = bundle.glass_config(selected_glass_id)
    if glass is None:
        raise RedetectionRequestError("선택한 관찰창이 결과 snapshot에 없습니다.")
    if not source_video_path:
        raise RedetectionRequestError("재검출할 원본 영상이 없습니다. 원본 영상을 다시 지정해 주세요.")
    requested_range = build_redetection_range(
        bundle,
        target_timestamp_sec,
        mode,
        before_sec=before_sec,
        after_sec=after_sec,
        policy=policy,
    )
    target = min(
        float(bundle.analysis_end_sec),
        max(float(bundle.analysis_start_sec), float(target_timestamp_sec)),
    )
    return RedetectionRequest(
        request_id=str(uuid4()),
        generation=int(generation),
        bundle_root=str(bundle.root),
        official_run_id=str(bundle.run_id),
        source_video_path=str(source_video_path),
        selected_glass_id=str(selected_glass_id),
        target_timestamp_sec=target,
        mode=mode,
        requested_range=requested_range,
        recipe_snapshot_json=json.dumps(
            bundle.recipe.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
        session_snapshot_json=json.dumps(
            bundle.session.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
        detector_settings_json=detector_settings_to_json(detector_settings),
    )


def redetection_schedule(request: RedetectionRequest) -> tuple[tuple[float, bool], ...]:
    """Return ``(nominal timestamp, warmup)`` preserving the official schedule."""
    if request.mode is RedetectionMode.CURRENT:
        return ((request.target_timestamp_sec, False),)
    session = json.loads(request.session_snapshot_json)
    start = float(session.get("analysis_start_sec", 0.0))
    end_value = session.get("analysis_end_sec")
    metadata = session.get("video_metadata") or {}
    end = float(end_value if end_value is not None else metadata.get("duration_sec", 0.0))
    fps = float(session.get("sampling_fps", 0.0))
    schedule = timestamp_schedule(start, end, fps)
    requested = request.requested_range
    selected = []
    for timestamp in schedule:
        if timestamp < requested.warmup_start_sec - 1e-9:
            continue
        if timestamp > requested.display_end_sec + 1e-9:
            continue
        warmup = timestamp < requested.display_start_sec - 1e-9
        selected.append((timestamp, warmup))
    return tuple(selected)


def full_static_artifact_schedule(request: RedetectionRequest) -> tuple[float, ...]:
    session = json.loads(request.session_snapshot_json)
    start = float(session.get("analysis_start_sec", 0.0))
    end_value = session.get("analysis_end_sec")
    metadata = session.get("video_metadata") or {}
    end = float(end_value if end_value is not None else metadata.get("duration_sec", 0.0))
    fps = float(session.get("sampling_fps", 0.0))
    return tuple(timestamp_schedule(start, end, fps))
