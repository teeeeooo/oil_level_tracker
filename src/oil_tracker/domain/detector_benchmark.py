from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition


BENCHMARK_SCHEMA_VERSION = 1
BENCHMARK_CATALOG_SCHEMA_VERSION = 1
EVENT_TRUTH_UNAVAILABLE_REASON = (
    "regression fixture schema version 1 does not contain authoritative event truth"
)


class BenchmarkValidationError(ValueError):
    """Benchmark input or metric data is invalid."""


class BenchmarkComparisonError(BenchmarkValidationError):
    """A previous result cannot be compared safely."""


class BenchmarkCategory(str, Enum):
    CLEAR_OIL_BOUNDARY = "clear_oil_boundary"
    TRANSPARENT_OIL_FULL = "transparent_oil_full"
    TRANSPARENT_OIL_SHIMMER = "transparent_oil_shimmer"
    WHITE_FOAM = "white_foam"
    REFLECTION_OR_BLUR = "reflection_or_blur"
    STRUCTURAL_HORIZONTAL_EDGE = "structural_horizontal_edge"
    RAPID_OIL_FLOW = "rapid_oil_flow"
    NO_INTERFACE = "no_interface"


CATEGORY_LABELS_KO: Mapping[BenchmarkCategory, str] = {
    BenchmarkCategory.CLEAR_OIL_BOUNDARY: "뚜렷한 유면",
    BenchmarkCategory.TRANSPARENT_OIL_FULL: "투명 오일 가득 참",
    BenchmarkCategory.TRANSPARENT_OIL_SHIMMER: "투명 오일 교반·아지랑이",
    BenchmarkCategory.WHITE_FOAM: "실제 흰색 Foam",
    BenchmarkCategory.REFLECTION_OR_BLUR: "반사광·흐림",
    BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE: "구조물 수평 경계",
    BenchmarkCategory.RAPID_OIL_FLOW: "빠른 오일 유입·배출",
    BenchmarkCategory.NO_INTERFACE: "full/empty no-interface",
}

CATEGORY_CONTRACT = tuple(category.value for category in BenchmarkCategory)
NO_INTERFACE_STATES = frozenset(
    {FillState.FULL_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE}
)


@dataclass(frozen=True)
class BenchmarkTruth:
    fill_state: FillState | None
    oil_boundary_y: float | None
    foam_present: bool | None
    foam_front_y: float | None


@dataclass(frozen=True)
class BenchmarkPrediction:
    fill_state: FillState
    raw_oil_boundary_y: float | None
    smoothed_oil_boundary_y: float | None
    raw_foam_front_y: float | None
    smoothed_foam_front_y: float | None
    is_valid: bool
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class MetricValue:
    value: float | None
    numerator: float | int | None
    denominator: float | int
    evaluated_count: int
    excluded_count: int
    unavailable_count: int
    status: str
    reason: str | None = None
    unit: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "evaluated_count": self.evaluated_count,
            "excluded_count": self.excluded_count,
            "unavailable_count": self.unavailable_count,
            "status": self.status,
            "reason": self.reason,
            "unit": self.unit,
        }


@dataclass(frozen=True)
class BenchmarkCaseEvaluation:
    dataset_id: str
    case_id: str
    sequence_id: str | None
    sequence_order: int | None
    timestamp_sec: float
    frame_index: int
    frame_identity: str
    category: BenchmarkCategory
    disposition: TruthDisposition
    truth_fill_state: FillState | None
    predicted_fill_state: FillState
    truth_oil_boundary_present: bool | None
    raw_oil_boundary_present: bool
    smoothed_oil_boundary_present: bool
    truth_oil_boundary_y: float | None
    raw_oil_boundary_y: float | None
    smoothed_oil_boundary_y: float | None
    raw_oil_absolute_error_px: float | None
    smoothed_oil_absolute_error_px: float | None
    raw_oil_normalized_error: float | None
    smoothed_oil_normalized_error: float | None
    truth_foam_present: bool | None
    raw_foam_present: bool
    smoothed_foam_present: bool
    truth_foam_front_y: float | None
    raw_foam_front_y: float | None
    smoothed_foam_front_y: float | None
    raw_foam_absolute_error_px: float | None
    smoothed_foam_absolute_error_px: float | None
    raw_foam_normalized_error: float | None
    smoothed_foam_normalized_error: float | None
    analysis_height_px: float
    detector_valid: bool
    included_in_accuracy: bool
    exclusion_reason: str | None
    unavailable_reasons: tuple[str, ...]
    unusable_reasons: tuple[str, ...]
    detector_version: str
    settings_fingerprint: str
    flags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "case_id": self.case_id,
            "sequence_id": self.sequence_id,
            "sequence_order": self.sequence_order,
            "timestamp_sec": self.timestamp_sec,
            "frame_index": self.frame_index,
            "frame_identity": self.frame_identity,
            "category": self.category.value,
            "disposition": self.disposition.value,
            "truth_fill_state": self.truth_fill_state.value if self.truth_fill_state else None,
            "predicted_fill_state": self.predicted_fill_state.value,
            "truth_oil_boundary_present": self.truth_oil_boundary_present,
            "raw_oil_boundary_present": self.raw_oil_boundary_present,
            "smoothed_oil_boundary_present": self.smoothed_oil_boundary_present,
            "truth_oil_boundary_y": self.truth_oil_boundary_y,
            "raw_oil_boundary_y": self.raw_oil_boundary_y,
            "smoothed_oil_boundary_y": self.smoothed_oil_boundary_y,
            "raw_oil_absolute_error_px": self.raw_oil_absolute_error_px,
            "smoothed_oil_absolute_error_px": self.smoothed_oil_absolute_error_px,
            "raw_oil_normalized_error": self.raw_oil_normalized_error,
            "smoothed_oil_normalized_error": self.smoothed_oil_normalized_error,
            "truth_foam_present": self.truth_foam_present,
            "raw_foam_present": self.raw_foam_present,
            "smoothed_foam_present": self.smoothed_foam_present,
            "truth_foam_front_y": self.truth_foam_front_y,
            "raw_foam_front_y": self.raw_foam_front_y,
            "smoothed_foam_front_y": self.smoothed_foam_front_y,
            "raw_foam_absolute_error_px": self.raw_foam_absolute_error_px,
            "smoothed_foam_absolute_error_px": self.smoothed_foam_absolute_error_px,
            "raw_foam_normalized_error": self.raw_foam_normalized_error,
            "smoothed_foam_normalized_error": self.smoothed_foam_normalized_error,
            "analysis_height_px": self.analysis_height_px,
            "detector_valid": self.detector_valid,
            "included_in_accuracy": self.included_in_accuracy,
            "exclusion_reason": self.exclusion_reason,
            "unavailable_reasons": list(self.unavailable_reasons),
            "unusable_reasons": list(self.unusable_reasons),
            "detector_version": self.detector_version,
            "settings_fingerprint": self.settings_fingerprint,
            "flags": list(self.flags),
        }


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def fingerprint_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def deterministic_percentile(values: Sequence[float], percentile: float) -> float | None:
    """Return a deterministic linear percentile using the inclusive endpoints policy.

    The interpolation rank is ``(n - 1) * percentile``. This is stable for both
    odd and even sample counts and does not require NumPy or SciPy.
    """

    if not values:
        return None
    if not 0.0 <= percentile <= 1.0:
        raise BenchmarkValidationError("percentile must be between 0 and 1")
    ordered = sorted(_finite(value, "percentile sample") for value in values)
    rank = (len(ordered) - 1) * percentile
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def evaluate_case(
    *,
    dataset_id: str,
    case_id: str,
    sequence_id: str | None,
    sequence_order: int | None,
    timestamp_sec: float,
    frame_index: int,
    frame_identity: str,
    category: BenchmarkCategory,
    disposition: TruthDisposition,
    truth: BenchmarkTruth,
    prediction: BenchmarkPrediction,
    analysis_height_px: float,
    detector_version: str,
    settings_fingerprint: str,
    unusable_reasons: Iterable[str] = (),
) -> BenchmarkCaseEvaluation:
    height = _finite(analysis_height_px, "analysis height")
    if height <= 0:
        raise BenchmarkValidationError("analysis height must be greater than zero")
    usable = disposition is not TruthDisposition.UNUSABLE
    unavailable: list[str] = []
    if not usable:
        truth_oil_presence: bool | None = None
        exclusion_reason = "fixture disposition is unusable"
    elif truth.oil_boundary_y is not None:
        truth_oil_presence = True
        exclusion_reason = None
    elif truth.fill_state in NO_INTERFACE_STATES:
        truth_oil_presence = False
        exclusion_reason = None
    else:
        truth_oil_presence = None
        exclusion_reason = None
        unavailable.append("authoritative oil-boundary presence is unavailable")

    truth_oil_y = _optional_finite(truth.oil_boundary_y, "truth oil boundary")
    truth_foam_y = _optional_finite(truth.foam_front_y, "truth foam front")
    raw_oil_y = _optional_finite(prediction.raw_oil_boundary_y, "raw oil boundary")
    smoothed_oil_y = _optional_finite(
        prediction.smoothed_oil_boundary_y, "smoothed oil boundary"
    )
    raw_foam_y = _optional_finite(prediction.raw_foam_front_y, "raw foam front")
    smoothed_foam_y = _optional_finite(
        prediction.smoothed_foam_front_y, "smoothed foam front"
    )

    raw_oil_error = _absolute_error(truth_oil_y, raw_oil_y) if usable else None
    smoothed_oil_error = (
        _absolute_error(truth_oil_y, smoothed_oil_y) if usable else None
    )
    raw_foam_error = _absolute_error(truth_foam_y, raw_foam_y) if usable else None
    smoothed_foam_error = (
        _absolute_error(truth_foam_y, smoothed_foam_y) if usable else None
    )
    if usable and truth_oil_y is not None and raw_oil_y is None:
        unavailable.append("raw detector oil boundary is missing")
    if usable and truth_oil_y is not None and smoothed_oil_y is None:
        unavailable.append("smoothed detector oil boundary is missing")
    if usable and truth_foam_y is not None and raw_foam_y is None:
        unavailable.append("raw detector foam front is missing")
    if usable and truth_foam_y is not None and smoothed_foam_y is None:
        unavailable.append("smoothed detector foam front is missing")
    if usable and truth.fill_state is None:
        unavailable.append("authoritative fill state is unavailable")
    if usable and truth.foam_present is None:
        unavailable.append("authoritative foam presence is unavailable")

    normalized_unusable = tuple(sorted({str(value) for value in unusable_reasons if str(value)}))
    return BenchmarkCaseEvaluation(
        dataset_id=str(dataset_id),
        case_id=str(case_id),
        sequence_id=str(sequence_id) if sequence_id else None,
        sequence_order=sequence_order,
        timestamp_sec=_finite(timestamp_sec, "timestamp"),
        frame_index=int(frame_index),
        frame_identity=str(frame_identity),
        category=category,
        disposition=disposition,
        truth_fill_state=truth.fill_state if usable else None,
        predicted_fill_state=prediction.fill_state,
        truth_oil_boundary_present=truth_oil_presence,
        raw_oil_boundary_present=raw_oil_y is not None,
        smoothed_oil_boundary_present=smoothed_oil_y is not None,
        truth_oil_boundary_y=truth_oil_y if usable else None,
        raw_oil_boundary_y=raw_oil_y,
        smoothed_oil_boundary_y=smoothed_oil_y,
        raw_oil_absolute_error_px=raw_oil_error,
        smoothed_oil_absolute_error_px=smoothed_oil_error,
        raw_oil_normalized_error=_normalized(raw_oil_error, height),
        smoothed_oil_normalized_error=_normalized(smoothed_oil_error, height),
        truth_foam_present=truth.foam_present if usable else None,
        raw_foam_present=raw_foam_y is not None,
        smoothed_foam_present=smoothed_foam_y is not None,
        truth_foam_front_y=truth_foam_y if usable else None,
        raw_foam_front_y=raw_foam_y,
        smoothed_foam_front_y=smoothed_foam_y,
        raw_foam_absolute_error_px=raw_foam_error,
        smoothed_foam_absolute_error_px=smoothed_foam_error,
        raw_foam_normalized_error=_normalized(raw_foam_error, height),
        smoothed_foam_normalized_error=_normalized(smoothed_foam_error, height),
        analysis_height_px=height,
        detector_valid=bool(prediction.is_valid),
        included_in_accuracy=usable,
        exclusion_reason=exclusion_reason,
        unavailable_reasons=tuple(sorted(set(unavailable))),
        unusable_reasons=normalized_unusable,
        detector_version=str(detector_version),
        settings_fingerprint=str(settings_fingerprint),
        flags=tuple(sorted({str(value) for value in prediction.flags})),
    )


def summarize_cases(cases: Sequence[BenchmarkCaseEvaluation]) -> dict[str, Any]:
    ordered = tuple(sorted(cases, key=_case_sort_key))
    total = len(ordered)
    usable = tuple(case for case in ordered if case.included_in_accuracy)
    unusable = tuple(case for case in ordered if not case.included_in_accuracy)
    excluded_count = len(unusable)
    unavailable_case_count = sum(bool(case.unavailable_reasons) for case in usable)
    metrics: dict[str, MetricValue] = {}

    _add_error_distribution(
        metrics,
        "raw_oil",
        usable,
        "raw_oil_absolute_error_px",
        "raw_oil_normalized_error",
        excluded_count,
    )
    _add_error_distribution(
        metrics,
        "smoothed_oil",
        usable,
        "smoothed_oil_absolute_error_px",
        "smoothed_oil_normalized_error",
        excluded_count,
    )
    _add_error_distribution(
        metrics,
        "raw_foam",
        usable,
        "raw_foam_absolute_error_px",
        "raw_foam_normalized_error",
        excluded_count,
    )
    _add_error_distribution(
        metrics,
        "smoothed_foam",
        usable,
        "smoothed_foam_absolute_error_px",
        "smoothed_foam_normalized_error",
        excluded_count,
    )

    raw_coverage = _boundary_confusion(usable, "raw_oil_boundary_present")
    smooth_coverage = _boundary_confusion(usable, "smoothed_oil_boundary_present")
    metrics["raw_oil_detection_coverage"] = _ratio_metric(
        raw_coverage["truth_present_detector_present"],
        raw_coverage["truth_present_detector_present"]
        + raw_coverage["truth_present_detector_missing"],
        excluded_count=excluded_count,
        unavailable_count=raw_coverage["unavailable"],
        reason="no usable fixture has authoritative oil-boundary presence",
    )
    metrics["smoothed_oil_detection_coverage"] = _ratio_metric(
        smooth_coverage["truth_present_detector_present"],
        smooth_coverage["truth_present_detector_present"]
        + smooth_coverage["truth_present_detector_missing"],
        excluded_count=excluded_count,
        unavailable_count=smooth_coverage["unavailable"],
        reason="no usable fixture has authoritative oil-boundary presence",
    )

    fill_confusion = _fill_state_confusion(usable)
    fill_evaluated = sum(sum(row.values()) for row in fill_confusion.values())
    fill_correct = sum(row.get(state, 0) for state, row in fill_confusion.items())
    metrics["fill_state_accuracy"] = _ratio_metric(
        fill_correct,
        fill_evaluated,
        excluded_count=excluded_count,
        unavailable_count=sum(case.truth_fill_state is None for case in usable),
        reason="no usable fixture has authoritative fill state",
    )

    foam_confusion = _foam_confusion(usable, "smoothed_foam_present")
    metrics["foam_precision"] = _ratio_metric(
        foam_confusion["true_positive"],
        foam_confusion["true_positive"] + foam_confusion["false_positive"],
        excluded_count=excluded_count,
        unavailable_count=foam_confusion["unavailable"],
        reason="foam precision denominator is zero",
    )
    metrics["foam_recall"] = _ratio_metric(
        foam_confusion["true_positive"],
        foam_confusion["true_positive"] + foam_confusion["false_negative"],
        excluded_count=excluded_count,
        unavailable_count=foam_confusion["unavailable"],
        reason="foam recall denominator is zero",
    )

    shimmer = tuple(
        case
        for case in usable
        if case.category is BenchmarkCategory.TRANSPARENT_OIL_SHIMMER
        and case.truth_foam_present is False
    )
    metrics["shimmer_foam_false_positive_rate"] = _ratio_metric(
        sum(case.smoothed_foam_present for case in shimmer),
        len(shimmer),
        excluded_count=excluded_count,
        unavailable_count=sum(
            case.category is BenchmarkCategory.TRANSPARENT_OIL_SHIMMER
            and case.truth_foam_present is None
            for case in usable
        ),
        reason="no usable shimmer fixture has authoritative Foam absence",
    )

    _add_no_interface_metrics(metrics, usable, excluded_count, raw=True)
    _add_no_interface_metrics(metrics, usable, excluded_count, raw=False)
    metrics["event_timestamp_difference_sec"] = MetricValue(
        value=None,
        numerator=None,
        denominator=0,
        evaluated_count=0,
        excluded_count=excluded_count,
        unavailable_count=len(usable),
        status="not_evaluated",
        reason=EVENT_TRUTH_UNAVAILABLE_REASON,
        unit="sec",
    )

    unusable_reason_breakdown: dict[str, int] = {}
    for case in unusable:
        reasons = case.unusable_reasons or ("unspecified",)
        for reason in reasons:
            unusable_reason_breakdown[reason] = unusable_reason_breakdown.get(reason, 0) + 1

    unavailable_reason_breakdown: dict[str, int] = {}
    for case in usable:
        for reason in case.unavailable_reasons:
            unavailable_reason_breakdown[reason] = unavailable_reason_breakdown.get(reason, 0) + 1
    unavailable_reason_breakdown[EVENT_TRUTH_UNAVAILABLE_REASON] = len(usable)

    return {
        "case_count": total,
        "usable_count": len(usable),
        "unusable_count": excluded_count,
        "unavailable_case_count": unavailable_case_count,
        "unusable_reason_breakdown": dict(sorted(unusable_reason_breakdown.items())),
        "unavailable_metric_reasons": dict(sorted(unavailable_reason_breakdown.items())),
        "metrics": {key: metrics[key].to_dict() for key in sorted(metrics)},
        "oil_boundary_coverage": {
            "raw": raw_coverage,
            "smoothed": smooth_coverage,
        },
        "fill_state_confusion_matrix": fill_confusion,
        "foam_presence_confusion": foam_confusion,
    }


def summarize_by_category(
    cases: Sequence[BenchmarkCaseEvaluation],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    for category in BenchmarkCategory:
        categories[category.value] = summarize_cases(
            tuple(case for case in cases if case.category is category)
        )
    micro = summarize_cases(cases)
    macro = macro_category_aggregate(categories)
    return categories, micro, macro


def macro_category_aggregate(
    categories: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    metric_names = sorted(
        {
            metric_name
            for summary in categories.values()
            for metric_name in summary.get("metrics", {})
        }
    )
    output: dict[str, Any] = {}
    for metric_name in metric_names:
        available = []
        evaluated_count = excluded_count = unavailable_count = 0
        unit = None
        for category in sorted(categories):
            metric = categories[category].get("metrics", {}).get(metric_name)
            if not isinstance(metric, Mapping):
                continue
            evaluated_count += int(metric.get("evaluated_count", 0))
            excluded_count += int(metric.get("excluded_count", 0))
            unavailable_count += int(metric.get("unavailable_count", 0))
            unit = unit or metric.get("unit")
            if metric.get("status") == "evaluated" and metric.get("value") is not None:
                available.append(float(metric["value"]))
        if available:
            value = sum(available) / len(available)
            output[metric_name] = MetricValue(
                value=value,
                numerator=sum(available),
                denominator=len(available),
                evaluated_count=evaluated_count,
                excluded_count=excluded_count,
                unavailable_count=unavailable_count,
                status="evaluated",
                unit=unit,
            ).to_dict()
        else:
            output[metric_name] = MetricValue(
                value=None,
                numerator=None,
                denominator=0,
                evaluated_count=0,
                excluded_count=excluded_count,
                unavailable_count=unavailable_count,
                status="not_evaluated",
                reason="no category has an evaluated value for this metric",
                unit=unit,
            ).to_dict()
    evaluated_categories = sum(int(summary.get("usable_count", 0)) > 0 for summary in categories.values())
    return {
        "aggregation": "equal_weight_across_evaluated_categories",
        "category_count": len(categories),
        "evaluated_category_count": evaluated_categories,
        "metrics": output,
    }


def compare_benchmark_payloads(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    previous_version = int(previous.get("benchmark_schema_version", -1))
    current_version = int(current.get("benchmark_schema_version", -1))
    if previous_version != current_version or current_version != BENCHMARK_SCHEMA_VERSION:
        raise BenchmarkComparisonError(
            f"benchmark schema mismatch: previous={previous_version}, current={current_version}"
        )
    previous_dataset = previous.get("dataset", {})
    current_dataset = current.get("dataset", {})
    previous_fingerprint = str(previous_dataset.get("fingerprint", ""))
    current_fingerprint = str(current_dataset.get("fingerprint", ""))
    if not previous_fingerprint or previous_fingerprint != current_fingerprint:
        raise BenchmarkComparisonError(
            "dataset fingerprint mismatch; results are not directly comparable"
        )
    previous_contract = tuple(previous.get("category_contract", ()))
    current_contract = tuple(current.get("category_contract", ()))
    if previous_contract != current_contract or current_contract != CATEGORY_CONTRACT:
        raise BenchmarkComparisonError("benchmark category contract mismatch")

    micro = _compare_metric_maps(
        previous.get("micro_aggregate", {}).get("metrics", {}),
        current.get("micro_aggregate", {}).get("metrics", {}),
    )
    category_changes: dict[str, Any] = {}
    previous_categories = previous.get("category_summaries", {})
    current_categories = current.get("category_summaries", {})
    for category in CATEGORY_CONTRACT:
        category_changes[category] = _compare_metric_maps(
            previous_categories.get(category, {}).get("metrics", {}),
            current_categories.get(category, {}).get("metrics", {}),
        )
    previous_detector = previous.get("detector", {})
    current_detector = current.get("detector", {})
    return {
        "status": "comparable",
        "dataset_fingerprint": current_fingerprint,
        "previous_run_fingerprint": previous.get("run_fingerprint"),
        "current_run_fingerprint": current.get("run_fingerprint"),
        "previous_detector_version": previous_detector.get("version"),
        "current_detector_version": current_detector.get("version"),
        "previous_settings_fingerprint": previous_detector.get("settings_fingerprint"),
        "current_settings_fingerprint": current_detector.get("settings_fingerprint"),
        "micro_metric_changes": micro,
        "category_metric_changes": category_changes,
    }


def metric_direction(metric_name: str) -> str | None:
    lowered = metric_name.lower()
    if any(
        token in lowered
        for token in (
            "error",
            "mae",
            "median_absolute",
            "p90_absolute",
            "p95_absolute",
            "false_positive_rate",
            "false_boundary_rate",
            "timestamp_difference",
        )
    ):
        return "lower_is_better"
    if any(token in lowered for token in ("coverage", "accuracy", "precision", "recall")):
        return "higher_is_better"
    return None


def _compare_metric_maps(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in sorted(set(previous) | set(current)):
        old = previous.get(name)
        new = current.get(name)
        direction = metric_direction(name)
        if not isinstance(old, Mapping) or not isinstance(new, Mapping):
            output[name] = {
                "status": "not_evaluated",
                "reason": "metric is missing from one result",
                "direction": direction,
            }
            continue
        old_value = old.get("value") if old.get("status") == "evaluated" else None
        new_value = new.get("value") if new.get("status") == "evaluated" else None
        if old_value is None or new_value is None:
            output[name] = {
                "status": "not_evaluated",
                "reason": "metric is unavailable in one or both results",
                "previous": old_value,
                "current": new_value,
                "direction": direction,
            }
            continue
        previous_value = float(old_value)
        current_value = float(new_value)
        delta = current_value - previous_value
        if math.isclose(delta, 0.0, abs_tol=1e-12):
            status = "unchanged"
        elif direction == "lower_is_better":
            status = "improved" if delta < 0 else "regressed"
        elif direction == "higher_is_better":
            status = "improved" if delta > 0 else "regressed"
        else:
            status = "changed"
        output[name] = {
            "status": status,
            "previous": previous_value,
            "current": current_value,
            "delta": delta,
            "direction": direction,
        }
    return output


def _add_error_distribution(
    metrics: dict[str, MetricValue],
    prefix: str,
    cases: Sequence[BenchmarkCaseEvaluation],
    error_field: str,
    normalized_field: str,
    excluded_count: int,
) -> None:
    errors = [float(value) for case in cases if (value := getattr(case, error_field)) is not None]
    normalized = [
        float(value)
        for case in cases
        if (value := getattr(case, normalized_field)) is not None
    ]
    eligible = sum(
        case.truth_oil_boundary_y is not None
        if "oil" in prefix
        else case.truth_foam_front_y is not None
        for case in cases
    )
    unavailable = max(0, eligible - len(errors))
    _distribution_metrics(metrics, prefix, errors, excluded_count, unavailable, "px")
    _distribution_metrics(
        metrics,
        f"{prefix}_normalized",
        normalized,
        excluded_count,
        max(0, eligible - len(normalized)),
        "ratio",
    )


def _distribution_metrics(
    metrics: dict[str, MetricValue],
    prefix: str,
    values: Sequence[float],
    excluded_count: int,
    unavailable_count: int,
    unit: str,
) -> None:
    if not values:
        unavailable = MetricValue(
            value=None,
            numerator=None,
            denominator=0,
            evaluated_count=0,
            excluded_count=excluded_count,
            unavailable_count=unavailable_count,
            status="not_evaluated",
            reason="no matched authoritative truth and detector position",
            unit=unit,
        )
        for suffix in ("mae", "median_absolute_error", "p90_absolute_error", "p95_absolute_error"):
            metrics[f"{prefix}_{suffix}"] = unavailable
        return
    count = len(values)
    total = sum(values)
    metrics[f"{prefix}_mae"] = MetricValue(
        value=total / count,
        numerator=total,
        denominator=count,
        evaluated_count=count,
        excluded_count=excluded_count,
        unavailable_count=unavailable_count,
        status="evaluated",
        unit=unit,
    )
    for suffix, percentile in (
        ("median_absolute_error", 0.5),
        ("p90_absolute_error", 0.9),
        ("p95_absolute_error", 0.95),
    ):
        metrics[f"{prefix}_{suffix}"] = MetricValue(
            value=deterministic_percentile(values, percentile),
            numerator=None,
            denominator=count,
            evaluated_count=count,
            excluded_count=excluded_count,
            unavailable_count=unavailable_count,
            status="evaluated",
            unit=unit,
        )


def _boundary_confusion(
    cases: Sequence[BenchmarkCaseEvaluation], prediction_field: str
) -> dict[str, int]:
    output = {
        "truth_present_detector_present": 0,
        "truth_present_detector_missing": 0,
        "truth_absent_detector_absent": 0,
        "truth_absent_detector_false_boundary": 0,
        "unavailable": 0,
    }
    for case in cases:
        truth = case.truth_oil_boundary_present
        prediction = bool(getattr(case, prediction_field))
        if truth is None:
            output["unavailable"] += 1
        elif truth and prediction:
            output["truth_present_detector_present"] += 1
        elif truth and not prediction:
            output["truth_present_detector_missing"] += 1
        elif not truth and not prediction:
            output["truth_absent_detector_absent"] += 1
        else:
            output["truth_absent_detector_false_boundary"] += 1
    return output


def _fill_state_confusion(
    cases: Sequence[BenchmarkCaseEvaluation],
) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for case in cases:
        if case.truth_fill_state is None:
            continue
        truth = case.truth_fill_state.value
        predicted = case.predicted_fill_state.value
        output.setdefault(truth, {})[predicted] = output.setdefault(truth, {}).get(predicted, 0) + 1
    return {
        truth: dict(sorted(predictions.items()))
        for truth, predictions in sorted(output.items())
    }


def _foam_confusion(
    cases: Sequence[BenchmarkCaseEvaluation], prediction_field: str
) -> dict[str, int]:
    output = {
        "true_positive": 0,
        "false_positive": 0,
        "false_negative": 0,
        "true_negative": 0,
        "unavailable": 0,
    }
    for case in cases:
        truth = case.truth_foam_present
        predicted = bool(getattr(case, prediction_field))
        if truth is None:
            output["unavailable"] += 1
        elif truth and predicted:
            output["true_positive"] += 1
        elif truth and not predicted:
            output["false_negative"] += 1
        elif not truth and predicted:
            output["false_positive"] += 1
        else:
            output["true_negative"] += 1
    return output


def _add_no_interface_metrics(
    metrics: dict[str, MetricValue],
    cases: Sequence[BenchmarkCaseEvaluation],
    excluded_count: int,
    *,
    raw: bool,
) -> None:
    prefix = "raw" if raw else "smoothed"
    prediction_field = "raw_oil_boundary_present" if raw else "smoothed_oil_boundary_present"
    no_interface = tuple(
        case
        for case in cases
        if case.truth_fill_state in NO_INTERFACE_STATES
        and case.truth_oil_boundary_present is False
    )
    metrics[f"{prefix}_no_interface_false_boundary_rate"] = _ratio_metric(
        sum(bool(getattr(case, prediction_field)) for case in no_interface),
        len(no_interface),
        excluded_count=excluded_count,
        unavailable_count=0,
        reason="no usable full/empty no-interface fixture is available",
    )
    for state, name in (
        (FillState.FULL_NO_INTERFACE, "full_no_interface"),
        (FillState.EMPTY_NO_INTERFACE, "empty_no_interface"),
    ):
        selected = tuple(case for case in no_interface if case.truth_fill_state is state)
        metrics[f"{prefix}_{name}_false_boundary_rate"] = _ratio_metric(
            sum(bool(getattr(case, prediction_field)) for case in selected),
            len(selected),
            excluded_count=excluded_count,
            unavailable_count=0,
            reason=f"no usable {state.value} fixture is available",
        )


def _ratio_metric(
    numerator: int | float,
    denominator: int | float,
    *,
    excluded_count: int,
    unavailable_count: int,
    reason: str,
) -> MetricValue:
    if denominator <= 0:
        return MetricValue(
            value=None,
            numerator=numerator,
            denominator=denominator,
            evaluated_count=0,
            excluded_count=excluded_count,
            unavailable_count=unavailable_count,
            status="not_evaluated",
            reason=reason,
            unit="ratio",
        )
    return MetricValue(
        value=float(numerator) / float(denominator),
        numerator=numerator,
        denominator=denominator,
        evaluated_count=int(denominator),
        excluded_count=excluded_count,
        unavailable_count=unavailable_count,
        status="evaluated",
        unit="ratio",
    )


def _case_sort_key(case: BenchmarkCaseEvaluation) -> tuple[Any, ...]:
    group = case.sequence_id or f"~{case.case_id}"
    order = case.sequence_order if case.sequence_order is not None else 0
    return group, order, case.timestamp_sec, case.frame_index, case.case_id


def _absolute_error(truth: float | None, predicted: float | None) -> float | None:
    if truth is None or predicted is None:
        return None
    return abs(predicted - truth)


def _normalized(error: float | None, height: float) -> float | None:
    return None if error is None else error / height


def _finite(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BenchmarkValidationError(f"{field_name} must be numeric") from exc
    if not math.isfinite(number):
        raise BenchmarkValidationError(f"{field_name} must be finite")
    return number


def _optional_finite(value: Any, field_name: str) -> float | None:
    return None if value is None else _finite(value, field_name)
