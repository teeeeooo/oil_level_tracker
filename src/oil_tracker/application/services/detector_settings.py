from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import json
import math
from typing import Any

from oil_tracker.domain.recipe import DetectorSettings
from oil_tracker.domain.redetection import DetectorSettingDiff


@dataclass(frozen=True)
class DetectorSettingField:
    name: str
    category: str
    value_type: type
    minimum: float | int | None
    maximum: float | int | None
    decimals: int
    step: float | int
    description: str


_FIELD_SPECS = (
    DetectorSettingField("canny_low", "edge", int, 0, 255, 0, 1, "Canny 경계 검출 하한입니다."),
    DetectorSettingField("canny_high", "edge", int, 0, 255, 0, 1, "Canny 경계 검출 상한입니다."),
    DetectorSettingField("hough_threshold", "hough", int, 1, 10000, 0, 1, "Hough 선 검출 누적 임계값입니다."),
    DetectorSettingField("hough_min_line_length_ratio", "hough", float, 0.0, 1.0, 6, 0.01, "유효 폭 대비 최소 수평선 길이 비율입니다."),
    DetectorSettingField("hough_max_line_gap", "hough", int, 0, 10000, 0, 1, "Hough 선분 사이의 최대 허용 간격입니다."),
    DetectorSettingField("hough_max_angle_deg", "hough", float, 0.0, 90.0, 6, 0.5, "수평선으로 인정할 최대 각도입니다."),
    DetectorSettingField("minimum_horizontal_coverage", "candidate", float, 0.0, 1.0, 6, 0.01, "후보가 확보해야 하는 최소 수평 연속 비율입니다."),
    DetectorSettingField("minimum_region_contrast", "candidate", float, 0.0, 1.0, 6, 0.01, "후보 위아래 영역의 최소 대비입니다."),
    DetectorSettingField("minimum_final_confidence", "confidence", float, 0.0, 1.0, 6, 0.01, "최종 검출을 유효하게 인정할 최소 신뢰도입니다."),
    DetectorSettingField("temporal_max_jump_px", "temporal", float, 0.0, 100000.0, 6, 1.0, "연속 sample 사이의 최대 유면 이동량입니다."),
    DetectorSettingField("smoothing_window", "temporal", int, 1, 1001, 0, 1, "유면 위치 smoothing에 사용하는 sample 수입니다."),
    DetectorSettingField("glare_threshold", "artifact", int, 0, 255, 0, 1, "과노출 반사광으로 분류하는 밝기 임계값입니다."),
    DetectorSettingField("glare_ratio_unknown", "artifact", float, 0.0, 1.0, 6, 0.01, "관찰 불가 상태로 전환할 반사광 면적 비율입니다."),
    DetectorSettingField("foam_variance_threshold", "foam", float, 0.0, 1000000.0, 6, 1.0, "거품 질감의 국부 분산 임계값입니다."),
    DetectorSettingField("foam_edge_density_threshold", "foam", float, 0.0, 1.0, 6, 0.01, "거품 영역의 최소 edge density입니다."),
    DetectorSettingField("foam_min_area_ratio", "foam", float, 0.0, 1.0, 6, 0.01, "하단 연결 거품의 최소 면적 비율입니다."),
    DetectorSettingField("state_hold_frames", "temporal", int, 1, 10000, 0, 1, "상태 전이를 확정하기 전에 유지할 sample 수입니다."),
    DetectorSettingField("candidate_top_k", "candidate", int, 1, 1000, 0, 1, "debug 결과에 유지할 후보의 최대 개수입니다."),
    DetectorSettingField("weight_edge", "score_weight", float, 0.0, 100.0, 8, 0.01, "edge strength score 가중치입니다."),
    DetectorSettingField("weight_coverage", "score_weight", float, 0.0, 100.0, 8, 0.01, "horizontal coverage score 가중치입니다."),
    DetectorSettingField("weight_region", "score_weight", float, 0.0, 100.0, 8, 0.01, "region contrast score 가중치입니다."),
    DetectorSettingField("weight_gradient_direction", "score_weight", float, 0.0, 100.0, 8, 0.01, "gradient 방향 score 가중치입니다."),
    DetectorSettingField("weight_temporal", "score_weight", float, 0.0, 100.0, 8, 0.01, "temporal continuity score 가중치입니다."),
    DetectorSettingField("weight_state", "score_weight", float, 0.0, 100.0, 8, 0.01, "state transition score 가중치입니다."),
    DetectorSettingField("penalty_glare", "penalty", float, 0.0, 100.0, 8, 0.01, "반사광 중첩 penalty입니다."),
    DetectorSettingField("penalty_border", "penalty", float, 0.0, 100.0, 8, 0.01, "glass rim 인접 penalty입니다."),
    DetectorSettingField("penalty_exclusion", "penalty", float, 0.0, 100.0, 8, 0.01, "제외 영역 중첩 penalty입니다."),
    DetectorSettingField("penalty_static", "penalty", float, 0.0, 100.0, 8, 0.01, "고정 artifact penalty입니다."),
    DetectorSettingField("penalty_jump", "penalty", float, 0.0, 100.0, 8, 0.01, "비정상 위치 급변 penalty입니다."),
)

DETECTOR_SETTING_FIELDS = {spec.name: spec for spec in _FIELD_SPECS}


def detector_setting_fields() -> tuple[DetectorSettingField, ...]:
    return _FIELD_SPECS


def detector_settings_to_json(settings: DetectorSettings) -> str:
    return json.dumps(asdict(settings), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def detector_settings_from_json(payload: str) -> DetectorSettings:
    raw = json.loads(payload)
    if not isinstance(raw, dict):
        raise ValueError("검출 설정 snapshot 형식이 올바르지 않습니다.")
    known = {field.name for field in fields(DetectorSettings)}
    return DetectorSettings(**{key: value for key, value in raw.items() if key in known})


def clone_detector_settings(settings: DetectorSettings) -> DetectorSettings:
    return detector_settings_from_json(detector_settings_to_json(settings))


def compare_detector_settings(
    baseline: DetectorSettings,
    temporary: DetectorSettings,
) -> tuple[DetectorSettingDiff, ...]:
    output: list[DetectorSettingDiff] = []
    for spec in _FIELD_SPECS:
        left = getattr(baseline, spec.name)
        right = getattr(temporary, spec.name)
        changed = not _serialized_equal(left, right)
        numeric_delta = None
        if changed and _is_number(left) and _is_number(right):
            numeric_delta = float(right) - float(left)
        output.append(
            DetectorSettingDiff(
                field_name=spec.name,
                category=spec.category,
                baseline_value=left,
                temporary_value=right,
                numeric_delta=numeric_delta,
                changed=changed,
            )
        )
    return tuple(output)


def validate_detector_settings(settings: DetectorSettings) -> dict[str, str]:
    errors: dict[str, str] = {}
    for spec in _FIELD_SPECS:
        value = getattr(settings, spec.name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors[spec.name] = "숫자 값을 입력해 주세요."
            continue
        if not math.isfinite(float(value)):
            errors[spec.name] = "유한한 숫자를 입력해 주세요."
            continue
        if spec.value_type is int and int(value) != value:
            errors[spec.name] = "정수 값을 입력해 주세요."
            continue
        if spec.minimum is not None and value < spec.minimum:
            errors[spec.name] = f"{spec.minimum:g} 이상이어야 합니다."
        elif spec.maximum is not None and value > spec.maximum:
            errors[spec.name] = f"{spec.maximum:g} 이하여야 합니다."
    if "canny_low" not in errors and "canny_high" not in errors and settings.canny_low >= settings.canny_high:
        errors["canny_high"] = "Canny 상한은 하한보다 커야 합니다."
    weight_names = [spec.name for spec in _FIELD_SPECS if spec.category == "score_weight"]
    if not any(float(getattr(settings, name)) > 0.0 for name in weight_names if name not in errors):
        errors.setdefault("weight_edge", "score 가중치 중 하나 이상은 0보다 커야 합니다.")
    return errors


def update_detector_setting(settings: DetectorSettings, field_name: str, value: Any) -> DetectorSettings:
    spec = DETECTOR_SETTING_FIELDS.get(field_name)
    if spec is None:
        raise KeyError(field_name)
    payload = asdict(settings)
    payload[field_name] = int(value) if spec.value_type is int else float(value)
    return DetectorSettings(**payload)


def _serialized_equal(left: Any, right: Any) -> bool:
    if _is_number(left) and _is_number(right):
        if not math.isfinite(float(left)) or not math.isfinite(float(right)):
            return False
        return json.dumps(left, allow_nan=False) == json.dumps(right, allow_nan=False)
    return left == right


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
