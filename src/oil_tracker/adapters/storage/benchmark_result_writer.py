from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any, Iterable, Mapping

from oil_tracker.domain.detector_benchmark import CATEGORY_CONTRACT


class BenchmarkResultStorageError(ValueError):
    pass


class AtomicBenchmarkResultWriter:
    def load_result(self, path: str | Path) -> Mapping[str, Any]:
        source = Path(path).expanduser()
        if not source.is_file():
            raise BenchmarkResultStorageError(
                f"previous benchmark result does not exist: {source}"
            )
        try:
            payload = json.loads(
                source.read_text(encoding="utf-8"),
                parse_constant=lambda value: _invalid_constant(value),
                object_pairs_hook=_unique_object,
            )
        except BenchmarkResultStorageError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise BenchmarkResultStorageError(
                f"previous benchmark result JSON is malformed: {exc}"
            ) from exc
        if not isinstance(payload, dict):
            raise BenchmarkResultStorageError(
                "previous benchmark result must contain a JSON object"
            )
        return payload

    def write(
        self,
        payload: Mapping[str, Any],
        output_root: str | Path,
        *,
        dataset_id: str,
        timestamp_token: str,
    ) -> Path:
        root = Path(output_root).expanduser()
        if root.exists() and not root.is_dir():
            raise BenchmarkResultStorageError("benchmark output root must be a directory")
        root.mkdir(parents=True, exist_ok=True)
        safe_dataset_id = _safe_component(dataset_id)
        safe_timestamp = _safe_component(timestamp_token)
        final = root / f"detector_benchmark_{safe_dataset_id}_{safe_timestamp}"
        if final.exists() or final.is_symlink():
            raise BenchmarkResultStorageError(
                f"existing benchmark output cannot be overwritten: {final}"
            )
        staging = Path(
            tempfile.mkdtemp(
                prefix=f".{final.name}.tmp-",
                dir=str(root),
            )
        )
        try:
            _write_json(staging / "benchmark_result.json", payload)
            self._write_cases(staging / "benchmark_cases.csv", payload.get("cases", []))
            self._write_categories(
                staging / "benchmark_categories.csv",
                payload.get("category_summaries", {}),
            )
            self._write_summary(staging / "benchmark_summary.csv", payload)
            (staging / "benchmark_comparison.md").write_text(
                _comparison_markdown(payload),
                encoding="utf-8",
                newline="\n",
            )
            os.replace(staging, final)
            return final
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    @staticmethod
    def _write_cases(path: Path, cases: Iterable[Mapping[str, Any]]) -> None:
        fields = [
            "dataset_id",
            "case_id",
            "sequence_id",
            "sequence_order",
            "timestamp_sec",
            "frame_index",
            "frame_identity",
            "category",
            "disposition",
            "truth_fill_state",
            "predicted_fill_state",
            "truth_oil_boundary_present",
            "raw_oil_boundary_present",
            "smoothed_oil_boundary_present",
            "truth_oil_boundary_y",
            "raw_oil_boundary_y",
            "smoothed_oil_boundary_y",
            "raw_oil_absolute_error_px",
            "smoothed_oil_absolute_error_px",
            "raw_oil_normalized_error",
            "smoothed_oil_normalized_error",
            "truth_foam_present",
            "raw_foam_present",
            "smoothed_foam_present",
            "truth_foam_front_y",
            "raw_foam_front_y",
            "smoothed_foam_front_y",
            "raw_foam_absolute_error_px",
            "smoothed_foam_absolute_error_px",
            "raw_foam_normalized_error",
            "smoothed_foam_normalized_error",
            "analysis_height_px",
            "detector_valid",
            "included_in_accuracy",
            "exclusion_reason",
            "unavailable_reasons",
            "unusable_reasons",
            "detector_version",
            "settings_fingerprint",
            "flags",
        ]
        rows = []
        for case in cases:
            row = {field: case.get(field) for field in fields}
            for name in ("unavailable_reasons", "unusable_reasons", "flags"):
                value = row.get(name)
                row[name] = "|".join(str(item) for item in value) if value else ""
            rows.append(row)
        _write_csv(path, fields, rows)

    @staticmethod
    def _write_categories(
        path: Path, categories: Mapping[str, Mapping[str, Any]]
    ) -> None:
        metric_fields = [
            "raw_oil_mae",
            "raw_oil_median_absolute_error",
            "raw_oil_p90_absolute_error",
            "raw_oil_p95_absolute_error",
            "raw_oil_normalized_mae",
            "raw_oil_normalized_median_absolute_error",
            "raw_oil_normalized_p90_absolute_error",
            "raw_oil_normalized_p95_absolute_error",
            "smoothed_oil_mae",
            "smoothed_oil_median_absolute_error",
            "smoothed_oil_p90_absolute_error",
            "smoothed_oil_p95_absolute_error",
            "smoothed_oil_normalized_mae",
            "smoothed_oil_normalized_median_absolute_error",
            "smoothed_oil_normalized_p90_absolute_error",
            "smoothed_oil_normalized_p95_absolute_error",
            "raw_oil_detection_coverage",
            "smoothed_oil_detection_coverage",
            "fill_state_accuracy",
            "foam_precision",
            "foam_recall",
            "shimmer_foam_false_positive_rate",
            "raw_no_interface_false_boundary_rate",
            "smoothed_no_interface_false_boundary_rate",
            "raw_full_no_interface_false_boundary_rate",
            "smoothed_full_no_interface_false_boundary_rate",
            "raw_empty_no_interface_false_boundary_rate",
            "smoothed_empty_no_interface_false_boundary_rate",
        ]
        fields = [
            "category",
            "case_count",
            "usable_count",
            "unusable_count",
            "unavailable_case_count",
            *metric_fields,
        ]
        rows = []
        for category in CATEGORY_CONTRACT:
            summary = categories.get(category, {})
            metrics = summary.get("metrics", {})
            row = {
                "category": category,
                "case_count": summary.get("case_count", 0),
                "usable_count": summary.get("usable_count", 0),
                "unusable_count": summary.get("unusable_count", 0),
                "unavailable_case_count": summary.get("unavailable_case_count", 0),
            }
            for name in metric_fields:
                metric = metrics.get(name, {})
                row[name] = metric.get("value") if metric.get("status") == "evaluated" else None
            rows.append(row)
        _write_csv(path, fields, rows)

    @staticmethod
    def _write_summary(path: Path, payload: Mapping[str, Any]) -> None:
        fields = [
            "scope",
            "category",
            "metric",
            "status",
            "value",
            "numerator",
            "denominator",
            "evaluated_count",
            "excluded_count",
            "unavailable_count",
            "unit",
            "reason",
        ]
        rows: list[dict[str, Any]] = []
        for scope, category, summary in _summary_sources(payload):
            for metric_name, metric in sorted(summary.get("metrics", {}).items()):
                rows.append(
                    {
                        "scope": scope,
                        "category": category,
                        "metric": metric_name,
                        "status": metric.get("status"),
                        "value": metric.get("value"),
                        "numerator": metric.get("numerator"),
                        "denominator": metric.get("denominator"),
                        "evaluated_count": metric.get("evaluated_count"),
                        "excluded_count": metric.get("excluded_count"),
                        "unavailable_count": metric.get("unavailable_count"),
                        "unit": metric.get("unit"),
                        "reason": metric.get("reason"),
                    }
                )
        _write_csv(path, fields, rows)


def _summary_sources(
    payload: Mapping[str, Any],
) -> Iterable[tuple[str, str | None, Mapping[str, Any]]]:
    yield "micro", None, payload.get("micro_aggregate", {})
    yield "macro_category", None, payload.get("macro_category_aggregate", {})
    categories = payload.get("category_summaries", {})
    for category in CATEGORY_CONTRACT:
        yield "category", category, categories.get(category, {})


def _comparison_markdown(payload: Mapping[str, Any]) -> str:
    comparison = payload.get("previous_baseline_comparison", {})
    status = comparison.get("status", "not_requested")
    lines = [
        "# Detector Benchmark Comparison",
        "",
        f"- Dataset fingerprint: `{payload.get('dataset', {}).get('fingerprint', '')}`",
        f"- Current run fingerprint: `{payload.get('run_fingerprint', '')}`",
        f"- Current detector: `{payload.get('detector', {}).get('version', '')}`",
        f"- Current settings: `{payload.get('detector', {}).get('settings_fingerprint', '')}`",
        "",
    ]
    if status != "comparable":
        lines.extend(
            [
                "## Status",
                "",
                "No previous comparable baseline was provided.",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- Previous run fingerprint: `{comparison.get('previous_run_fingerprint', '')}`",
            f"- Previous detector: `{comparison.get('previous_detector_version', '')}`",
            f"- Previous settings: `{comparison.get('previous_settings_fingerprint', '')}`",
            "",
            "## Micro aggregate changes",
            "",
            "| Metric | Previous | Current | Delta | Direction | Assessment |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for name, change in sorted(comparison.get("micro_metric_changes", {}).items()):
        lines.append(_comparison_row(name, change))
    lines.extend(["", "## Category changes", ""])
    for category in CATEGORY_CONTRACT:
        lines.extend(
            [
                f"### `{category}`",
                "",
                "| Metric | Previous | Current | Delta | Direction | Assessment |",
                "|---|---:|---:|---:|---|---|",
            ]
        )
        for name, change in sorted(
            comparison.get("category_metric_changes", {}).get(category, {}).items()
        ):
            lines.append(_comparison_row(name, change))
        lines.append("")
    return "\n".join(lines)


def _comparison_row(name: str, change: Mapping[str, Any]) -> str:
    if change.get("status") == "not_evaluated":
        return (
            f"| `{name}` |  |  |  | {change.get('direction') or ''} | "
            f"not evaluated: {change.get('reason', '')} |"
        )
    return (
        f"| `{name}` | {_format_number(change.get('previous'))} | "
        f"{_format_number(change.get('current'))} | {_format_number(change.get('delta'))} | "
        f"{change.get('direction') or ''} | {change.get('status', '')} |"
    )


def _format_number(value: Any) -> str:
    if value is None:
        return ""
    return f"{float(value):.9g}"


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(
    path: Path, fields: list[str], rows: Iterable[Mapping[str, Any]]
) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field)) for field in fields})


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def _safe_component(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value)).strip(".-_")
    return normalized or "dataset"


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise BenchmarkResultStorageError(f"duplicate JSON object key: {key}")
        output[key] = value
    return output


def _invalid_constant(value: str):
    raise BenchmarkResultStorageError(f"JSON constant is not allowed: {value}")
