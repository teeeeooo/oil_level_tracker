from __future__ import annotations

from collections import OrderedDict
import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from oil_tracker.adapters.storage.bundle_asset_resolver import BundleAssetError, BundleAssetResolver
from oil_tracker.domain.debug_trace import (
    DEBUG_TRACE_SCHEMA_VERSION,
    DebugBundleIndex,
    DebugTraceRecord,
    DebugTraceSummary,
)
from oil_tracker.domain.session import DebugTraceLevel


class DebugTraceError(ValueError):
    """A debug trace is unsupported, malformed, missing, or unsafe."""


class DebugTraceRepository:
    def __init__(self, bundle, *, record_cache_size: int = 8, image_cache_size: int = 4) -> None:
        self.bundle = bundle
        self.root = Path(bundle.root)
        self.resolver = BundleAssetResolver()
        self.record_cache_size = max(1, int(record_cache_size))
        self.image_cache_size = max(1, int(image_cache_size))
        self._record_cache: OrderedDict[str, DebugTraceRecord] = OrderedDict()
        self._image_cache: OrderedDict[tuple[str, str], np.ndarray] = OrderedDict()
        self.record_load_count = 0
        self.image_load_count = 0
        self.index = self._load_index()
        self._by_id = {summary.record_id: summary for summary in self.index.records}

    @property
    def has_trace(self) -> bool:
        return bool(self.index.records)

    def summaries(self, glass_id: str | None = None, reasons: set[str] | None = None) -> tuple[DebugTraceSummary, ...]:
        values = self.index.records
        if glass_id:
            values = tuple(summary for summary in values if summary.glass_id == glass_id)
        if reasons:
            values = tuple(summary for summary in values if reasons.intersection(summary.capture_reasons))
        return values

    def nearest(self, glass_id: str, timestamp_sec: float, tolerance_sec: float) -> DebugTraceSummary | None:
        matches = self.summaries(glass_id)
        if not matches:
            return None
        candidate = min(matches, key=lambda item: (abs(item.timestamp_sec - timestamp_sec), item.frame_index, item.record_id))
        return candidate if abs(candidate.timestamp_sec - timestamp_sec) <= max(0.0, tolerance_sec) else None

    def load_record(self, record_id: str) -> DebugTraceRecord:
        cached = self._record_cache.get(record_id)
        if cached is not None:
            self._record_cache.move_to_end(record_id)
            return cached
        summary = self._by_id.get(record_id)
        if summary is None:
            raise DebugTraceError(f"debug index에 없는 record_id입니다: {record_id}")
        trace_path = self._trace_path()
        try:
            with trace_path.open("rb") as handle:
                handle.seek(summary.byte_offset)
                raw = handle.read(summary.byte_length)
        except OSError as exc:
            raise DebugTraceError(f"debug trace record를 읽을 수 없습니다: {exc}") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DebugTraceError(f"debug_trace.jsonl record 형식이 올바르지 않습니다: {record_id}") from exc
        if not isinstance(payload, dict):
            raise DebugTraceError(f"debug trace record는 JSON object여야 합니다: {record_id}")
        if str(payload.get("record_id")) != summary.record_id:
            raise DebugTraceError(f"debug index와 trace의 record_id가 일치하지 않습니다: {record_id}")
        if str(payload.get("run_id")) != self.bundle.run_id:
            raise DebugTraceError(f"debug trace run_id가 결과 bundle과 일치하지 않습니다: {record_id}")
        if str(payload.get("glass_id")) != summary.glass_id:
            raise DebugTraceError(f"debug index와 trace의 glass_id가 일치하지 않습니다: {record_id}")
        try:
            version = int(payload.get("schema_version"))
        except (TypeError, ValueError) as exc:
            raise DebugTraceError(f"debug trace schema_version이 올바르지 않습니다: {record_id}") from exc
        if version != DEBUG_TRACE_SCHEMA_VERSION:
            raise DebugTraceError(f"지원하지 않는 debug trace schema version입니다: {version}")
        record = DebugTraceRecord(
            schema_version=version,
            record_id=summary.record_id,
            run_id=self.bundle.run_id,
            glass_id=summary.glass_id,
            glass_name=str(payload.get("glass_name", "")),
            frame_index=_integer(payload.get("frame_index"), "frame_index"),
            timestamp_sec=_number(payload.get("timestamp_sec"), "timestamp_sec"),
            capture_reasons=tuple(str(value) for value in payload.get("capture_reasons", [])),
            fill_state=str(payload.get("fill_state", "")),
            confidence=_dict(payload.get("confidence"), "confidence"),
            flags=tuple(str(value) for value in payload.get("flags", [])),
            positions=_dict(payload.get("positions"), "positions"),
            state=_dict(payload.get("state"), "state"),
            candidates=tuple(_dict(value, "candidate") for value in payload.get("candidates", [])),
            images={str(key): str(value) for key, value in _dict(payload.get("images"), "images").items()},
            warnings=tuple(str(value) for value in payload.get("warnings", [])),
        )
        self.record_load_count += 1
        self._cache(self._record_cache, record_id, record, self.record_cache_size)
        return record

    def load_image(self, record: DebugTraceRecord | str, image_key: str) -> np.ndarray | None:
        if isinstance(record, str):
            record = self.load_record(record)
        cache_key = (record.record_id, image_key)
        cached = self._image_cache.get(cache_key)
        if cached is not None:
            self._image_cache.move_to_end(cache_key)
            return cached.copy()
        relative = record.images.get(image_key)
        if not relative:
            return None
        try:
            path = self.resolver.resolve_file(self.root, Path("debug") / relative, label=f"debug artifact {image_key}")
        except BundleAssetError:
            return None
        try:
            encoded = np.fromfile(str(path), dtype=np.uint8)
            image = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
        except Exception as exc:
            raise DebugTraceError(f"debug artifact를 읽을 수 없습니다: {image_key}: {exc}") from exc
        if image is None:
            raise DebugTraceError(f"debug artifact image decode에 실패했습니다: {image_key}")
        self.image_load_count += 1
        self._cache(self._image_cache, cache_key, image, self.image_cache_size)
        return image.copy()

    def close(self) -> None:
        self._record_cache.clear()
        self._image_cache.clear()

    def _load_index(self) -> DebugBundleIndex:
        review_index = self.bundle.review_index or {}
        raw_level = review_index.get("debug_trace_level", self.bundle.debug_trace_level)
        try:
            level = DebugTraceLevel(str(raw_level))
        except ValueError as exc:
            raise DebugTraceError(f"지원하지 않는 debug trace level입니다: {raw_level}") from exc
        if level is DebugTraceLevel.NONE:
            raise DebugTraceError("이 결과에는 디버그 기록이 없습니다.")
        pointer = review_index.get("debug_index")
        if not pointer:
            raise DebugTraceError("debug index 경로가 기록되어 있지 않습니다.")
        try:
            index_path = self.resolver.resolve_file(self.root, pointer, label="debug index")
        except BundleAssetError as exc:
            raise DebugTraceError(str(exc)) from exc
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise DebugTraceError(f"debug_index.json을 읽을 수 없습니다: {exc}") from exc
        if not isinstance(payload, dict):
            raise DebugTraceError("debug_index.json의 최상위 값은 JSON object여야 합니다.")
        version = _integer(payload.get("schema_version"), "schema_version")
        if version != DEBUG_TRACE_SCHEMA_VERSION:
            raise DebugTraceError(f"지원하지 않는 debug index schema version입니다: {version}")
        run_id = str(payload.get("run_id", ""))
        if run_id != self.bundle.run_id:
            raise DebugTraceError("debug index run_id가 결과 bundle과 일치하지 않습니다.")
        trace_file = str(payload.get("trace_file", ""))
        review_trace = str(review_index.get("debug_trace", ""))
        expected_trace = (Path(pointer).parent / trace_file).as_posix()
        if review_trace and Path(review_trace).as_posix() != expected_trace:
            raise DebugTraceError("review index와 debug index의 trace 경로가 일치하지 않습니다.")
        try:
            trace_path = self.resolver.resolve_file(self.root, expected_trace, label="debug trace")
        except BundleAssetError as exc:
            raise DebugTraceError(str(exc)) from exc
        trace_size = trace_path.stat().st_size
        known_glass_ids = {glass.id for glass in self.bundle.recipe.glasses}
        summaries = []
        for raw in payload.get("records", []):
            item = _dict(raw, "record summary")
            glass_id = str(item.get("glass_id", ""))
            if glass_id not in known_glass_ids:
                raise DebugTraceError(f"debug index에 snapshot에 없는 glass_id가 있습니다: {glass_id}")
            item_run_id = str(item.get("run_id", ""))
            if item_run_id != run_id:
                raise DebugTraceError("debug record summary run_id가 index와 일치하지 않습니다.")
            offset = _integer(item.get("byte_offset"), "byte_offset")
            length = _integer(item.get("byte_length"), "byte_length")
            if offset < 0 or length < 0 or offset + length > trace_size:
                raise DebugTraceError("debug record byte offset 또는 length가 trace 범위를 벗어납니다.")
            summaries.append(
                DebugTraceSummary(
                    record_id=str(item.get("record_id", "")),
                    run_id=run_id,
                    glass_id=glass_id,
                    frame_index=_integer(item.get("frame_index"), "frame_index"),
                    timestamp_sec=_number(item.get("timestamp_sec"), "timestamp_sec"),
                    capture_reasons=tuple(str(value) for value in item.get("capture_reasons", [])),
                    confidence=float(item["confidence"]) if item.get("confidence") is not None else 0.0,
                    fill_state=str(item.get("fill_state", "")),
                    artifact_availability=tuple(str(value) for value in item.get("artifact_availability", [])),
                    byte_offset=offset,
                    byte_length=length,
                )
            )
        declared_count = _integer(payload.get("record_count", len(summaries)), "record_count")
        if declared_count != len(summaries):
            raise DebugTraceError("debug index record_count가 record summary 개수와 일치하지 않습니다.")
        return DebugBundleIndex(
            schema_version=version,
            run_id=run_id,
            trace_level=level.value,
            trace_path=expected_trace,
            record_count=declared_count,
            records=tuple(sorted(summaries, key=lambda item: (item.glass_id, item.timestamp_sec, item.frame_index, item.record_id))),
            glass_counts={str(key): int(value) for key, value in _dict(payload.get("glass_record_counts", {}), "glass_record_counts").items()},
            reason_counts={str(key): int(value) for key, value in _dict(payload.get("capture_reason_counts", {}), "capture_reason_counts").items()},
        )

    def _trace_path(self) -> Path:
        try:
            return self.resolver.resolve_file(self.root, self.index.trace_path, label="debug trace")
        except BundleAssetError as exc:
            raise DebugTraceError(str(exc)) from exc

    @staticmethod
    def _cache(cache: OrderedDict, key, value, limit: int) -> None:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > limit:
            cache.popitem(last=False)


def _dict(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise DebugTraceError(f"{field} 값은 JSON object여야 합니다.")
    return value


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise DebugTraceError(f"{field} 값이 올바르지 않습니다.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise DebugTraceError(f"{field} 값이 올바르지 않습니다.") from exc


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise DebugTraceError(f"{field} 값이 올바르지 않습니다.")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DebugTraceError(f"{field} 값이 올바르지 않습니다.") from exc
