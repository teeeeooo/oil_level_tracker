from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from oil_tracker.adapters.reporting.csv_exporter import EVENT_COLUMNS, TRACKING_COLUMNS
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.review import ReviewBundle, ReviewEvent, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel, VideoMetadata


SUPPORTED_REVIEW_INDEX_VERSION = 1


class ResultBundleError(ValueError):
    """A user-correctable result-bundle validation or parsing error."""


class ResultBundleReader:
    def __init__(self, recipe_repository: JsonRecipeRepository | None = None) -> None:
        self.recipe_repository = recipe_repository or JsonRecipeRepository()

    def read(self, source: str | Path) -> ReviewBundle:
        selected = Path(source).expanduser()
        root = self._bundle_root(selected)
        if not root.is_dir():
            raise ResultBundleError(f"결과 폴더가 아닙니다: {root}")

        default_manifest = root / "analysis_manifest.json"
        manifest_path = selected if selected.is_file() and selected.name == "analysis_manifest.json" else default_manifest
        manifest = self._read_json(manifest_path, required=True)
        index_path: Path | None = None
        if selected.is_file() and selected.name == "review_index.json":
            index_path = selected
        elif manifest.get("review_index"):
            index_path = self._safe_internal_path(root, manifest["review_index"], "analysis_manifest.json review_index")
        elif (root / "review_index.json").exists():
            index_path = root / "review_index.json"

        review_index = self._read_json(index_path, required=True) if index_path is not None else None
        if review_index is not None:
            version = self._required_int(review_index.get("schema_version"), index_path.name, "schema_version")
            if version != SUPPORTED_REVIEW_INDEX_VERSION:
                raise ResultBundleError(
                    f"지원하지 않는 review_index.json 버전입니다: {version}. "
                    f"지원 버전은 {SUPPORTED_REVIEW_INDEX_VERSION}입니다."
                )

        files = self._resolve_bundle_files(root, review_index)
        if review_index is not None and files["manifest"] != manifest_path.resolve():
            manifest_path = files["manifest"]
            manifest = self._read_json(manifest_path, required=True)
        try:
            recipe = self.recipe_repository.load(files["recipe_snapshot"])
        except FileNotFoundError as exc:
            raise ResultBundleError(f"필수 파일이 없습니다: {files['recipe_snapshot'].name}") from exc
        except json.JSONDecodeError as exc:
            raise ResultBundleError(f"{files['recipe_snapshot'].name} JSON 형식이 올바르지 않습니다: {exc.msg}") from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise ResultBundleError(f"{files['recipe_snapshot'].name} 내용을 읽을 수 없습니다: {exc}") from exc

        session_payload = self._read_json(files["session"], required=True)
        try:
            session = AnalysisSession.from_dict(session_payload)
        except (KeyError, TypeError, ValueError) as exc:
            raise ResultBundleError(f"session.json 내용을 읽을 수 없습니다: {exc}") from exc
        known_glass_ids = {glass.id for glass in recipe.glasses}
        samples = self._read_tracking(files["tracking_data"], known_glass_ids)
        if not samples:
            raise ResultBundleError("tracking_data.csv에 사용할 수 있는 tracking row가 없습니다.")
        events = self._read_events(files["events"], known_glass_ids)

        index = review_index or {}
        source_candidates = self._source_candidates(index, manifest, session)
        source_path = next((value for value in source_candidates if value), "")
        source_metadata = self._source_metadata(index, manifest, session)
        analysis_start, analysis_end = self._analysis_range(index, manifest, session, samples)
        compressor_start = self._optional_float(index.get("compressor_start_sec"), "review_index.json", "compressor_start_sec")
        if compressor_start is None:
            compressor_start = session.compressor_start_sec
        run_id = str(index.get("run_id") or manifest.get("run_id") or samples[0].run_id)
        glasses = self._review_glasses(index, recipe, events)
        debug_level, debug_index_path, debug_trace_path, debug_count, debug_warning = self._debug_contract(root, index)

        return ReviewBundle(
            root=root.resolve(),
            run_id=run_id,
            recipe=recipe,
            session=session,
            manifest=manifest,
            source_video_path=source_path,
            source_video_candidates=source_candidates,
            source_metadata=source_metadata,
            analysis_start_sec=analysis_start,
            analysis_end_sec=analysis_end,
            compressor_start_sec=compressor_start,
            glasses=glasses,
            samples=tuple(sorted(samples, key=lambda item: (item.glass_id, item.timestamp_sec, item.frame_index, item.input_order))),
            events=tuple(sorted(events, key=lambda item: (item.glass_id, item.start_time_sec, item.event_type.value, item.input_order))),
            files=files,
            debug_trace_level=debug_level.value,
            debug_index_path=debug_index_path,
            debug_trace_path=debug_trace_path,
            debug_record_count=debug_count,
            debug_warning=debug_warning,
            review_index=review_index,
        )

    def _debug_contract(self, root: Path, index: dict[str, Any]) -> tuple[DebugTraceLevel, str, str, int, str]:
        raw_level = index.get("debug_trace_level", "none")
        try:
            level = DebugTraceLevel(str(raw_level))
        except ValueError as exc:
            raise ResultBundleError(f"review_index.json debug_trace_level 값이 올바르지 않습니다: {raw_level}") from exc
        count = self._required_int(index.get("debug_record_count", 0), "review_index.json", "debug_record_count")
        if count < 0:
            raise ResultBundleError("review_index.json debug_record_count는 음수일 수 없습니다.")
        if level is DebugTraceLevel.NONE:
            return level, "", "", 0, ""
        index_pointer = str(index.get("debug_index") or "")
        trace_pointer = str(index.get("debug_trace") or "")
        if not index_pointer or not trace_pointer:
            return level, index_pointer, trace_pointer, count, "디버그 기록 경로가 불완전하여 디버그 모드를 사용할 수 없습니다."
        try:
            index_path = self._safe_internal_path(root, index_pointer, "review_index.json debug_index")
            trace_path = self._safe_internal_path(root, trace_pointer, "review_index.json debug_trace")
        except ResultBundleError as exc:
            return level, index_pointer, trace_pointer, count, str(exc)
        if not index_path.is_file() or not trace_path.is_file():
            return level, index_pointer, trace_pointer, count, "디버그 index 또는 trace 파일이 없어 디버그 모드를 사용할 수 없습니다."
        return level, index_pointer, trace_pointer, count, ""

    def _bundle_root(self, source: Path) -> Path:
        if source.is_dir():
            return source
        if source.is_file() and source.name in {"analysis_manifest.json", "review_index.json"}:
            return source.parent
        if source.exists():
            raise ResultBundleError("analysis_manifest.json, review_index.json 또는 결과 폴더를 선택해 주세요.")
        raise ResultBundleError(f"선택한 결과 경로가 존재하지 않습니다: {source}")

    def _resolve_bundle_files(self, root: Path, index: dict[str, Any] | None) -> dict[str, Path]:
        mapping = {
            "manifest": "analysis_manifest.json",
            "session": "session.json",
            "recipe_snapshot": "recipe_snapshot.oilrecipe",
            "tracking_data": "tracking_data.csv",
            "events": "events.csv",
        }
        if index:
            for key in tuple(mapping):
                if key in index and index[key] not in (None, ""):
                    mapping[key] = index[key]
        resolved: dict[str, Path] = {}
        for key, relative in mapping.items():
            path = self._safe_internal_path(root, relative, f"review_index.json {key}")
            if not path.is_file():
                raise ResultBundleError(f"필수 파일이 없습니다: {path.name}")
            resolved[key] = path
        return resolved

    def _safe_internal_path(self, root: Path, value: Any, field: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ResultBundleError(f"{field} 경로가 비어 있습니다.")
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ResultBundleError(f"{field}에 bundle 밖을 가리키는 경로를 사용할 수 없습니다: {value}")
        root_resolved = root.resolve()
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise ResultBundleError(f"{field} 경로가 결과 bundle 밖으로 벗어납니다: {value}") from exc
        return candidate

    def _read_json(self, path: Path | None, *, required: bool) -> dict[str, Any]:
        if path is None:
            if required:
                raise ResultBundleError("필수 JSON 파일 경로가 없습니다.")
            return {}
        if not path.is_file():
            if required:
                raise ResultBundleError(f"필수 파일이 없습니다: {path.name}")
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ResultBundleError(f"{path.name} JSON 형식이 올바르지 않습니다: {exc.msg}") from exc
        except OSError as exc:
            raise ResultBundleError(f"{path.name} 파일을 읽을 수 없습니다: {exc}") from exc
        if not isinstance(payload, dict):
            raise ResultBundleError(f"{path.name}의 최상위 값은 JSON object여야 합니다.")
        return payload

    def _read_tracking(self, path: Path, known_glass_ids: set[str]) -> list[ReviewTrackingSample]:
        rows = self._read_csv(path, TRACKING_COLUMNS)
        samples: list[ReviewTrackingSample] = []
        for order, row in enumerate(rows, start=1):
            line = order + 1
            try:
                glass_id = self._required_text(row.get("glass_id"), path.name, line, "glass_id")
                if glass_id not in known_glass_ids:
                    raise ResultBundleError(f"{path.name} row {line}: snapshot에 없는 glass_id입니다: {glass_id}")
                samples.append(
                    ReviewTrackingSample(
                        run_id=self._required_text(row.get("run_id"), path.name, line, "run_id"),
                        glass_id=glass_id,
                        frame_index=self._row_int(row, path, line, "frame_index"),
                        timestamp_sec=self._row_float(row, path, line, "timestamp_sec"),
                        fill_state=self._row_enum(row, path, line, "fill_state", FillState),
                        raw_oil_air_level_y=self._row_optional_float(row, path, line, "raw_oil_air_level_y"),
                        raw_oil_air_level_px_from_zero=self._row_optional_float(row, path, line, "raw_oil_air_level_px_from_zero"),
                        raw_oil_air_level_mm_from_zero=self._row_optional_float(row, path, line, "raw_oil_air_level_mm_from_zero"),
                        smoothed_oil_air_level_px_from_zero=self._row_optional_float(row, path, line, "smoothed_oil_air_level_px_from_zero"),
                        smoothed_oil_air_level_mm_from_zero=self._row_optional_float(row, path, line, "smoothed_oil_air_level_mm_from_zero"),
                        oil_air_confidence=self._row_float(row, path, line, "oil_air_confidence"),
                        raw_foam_front_y=self._row_optional_float(row, path, line, "raw_foam_front_y"),
                        raw_foam_front_px_from_zero=self._row_optional_float(row, path, line, "raw_foam_front_px_from_zero"),
                        raw_foam_front_mm_from_zero=self._row_optional_float(row, path, line, "raw_foam_front_mm_from_zero"),
                        smoothed_foam_front_px_from_zero=self._row_optional_float(row, path, line, "smoothed_foam_front_px_from_zero"),
                        smoothed_foam_front_mm_from_zero=self._row_optional_float(row, path, line, "smoothed_foam_front_mm_from_zero"),
                        foam_confidence=self._row_float(row, path, line, "foam_confidence"),
                        visibility_confidence=self._row_float(row, path, line, "visibility_confidence"),
                        overall_confidence=self._row_float(row, path, line, "overall_confidence"),
                        is_valid=self._row_bool(row, path, line, "is_valid"),
                        flags=tuple(flag.strip() for flag in str(row.get("flags", "")).split(";") if flag.strip()),
                        input_order=order,
                    )
                )
            except ResultBundleError:
                raise
            except (TypeError, ValueError) as exc:
                raise ResultBundleError(f"{path.name} row {line}을 읽을 수 없습니다: {exc}") from exc
        return samples

    def _read_events(self, path: Path, known_glass_ids: set[str]) -> list[ReviewEvent]:
        rows = self._read_csv(path, EVENT_COLUMNS)
        events: list[ReviewEvent] = []
        for order, row in enumerate(rows, start=1):
            line = order + 1
            glass_id = self._required_text(row.get("glass_id"), path.name, line, "glass_id")
            if glass_id not in known_glass_ids:
                raise ResultBundleError(f"{path.name} row {line}: snapshot에 없는 glass_id입니다: {glass_id}")
            events.append(
                ReviewEvent(
                    run_id=self._required_text(row.get("run_id"), path.name, line, "run_id"),
                    glass_id=glass_id,
                    event_type=self._row_enum(row, path, line, "event_type", EventType),
                    start_time_sec=self._row_float(row, path, line, "start_time_sec"),
                    end_time_sec=self._row_optional_float(row, path, line, "end_time_sec"),
                    representative_frame_index=self._row_optional_int(row, path, line, "representative_frame_index"),
                    oil_level_px=self._row_optional_float(row, path, line, "oil_level_px"),
                    oil_level_mm=self._row_optional_float(row, path, line, "oil_level_mm"),
                    foam_front_px=self._row_optional_float(row, path, line, "foam_front_px"),
                    foam_front_mm=self._row_optional_float(row, path, line, "foam_front_mm"),
                    confidence=self._row_float(row, path, line, "confidence"),
                    capture_path=str(row.get("capture_path", "") or ""),
                    note=str(row.get("note", "") or ""),
                    input_order=order,
                )
            )
        return events

    def _read_csv(self, path: Path, required_columns: list[str]) -> list[dict[str, str]]:
        try:
            with path.open("r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                columns = reader.fieldnames or []
                missing = [column for column in required_columns if column not in columns]
                if missing:
                    raise ResultBundleError(f"{path.name} 필수 column이 없습니다: {', '.join(missing)}")
                return list(reader)
        except ResultBundleError:
            raise
        except (csv.Error, OSError, UnicodeError) as exc:
            raise ResultBundleError(f"{path.name} CSV를 읽을 수 없습니다: {exc}") from exc

    def _source_candidates(self, index: dict[str, Any], manifest: dict[str, Any], session: AnalysisSession) -> tuple[str, ...]:
        values = [index.get("source_video_path"), manifest.get("source_video_path"), session.input_video_path]
        return tuple(dict.fromkeys(str(value) for value in values if value not in (None, "")))

    def _source_metadata(self, index: dict[str, Any], manifest: dict[str, Any], session: AnalysisSession) -> VideoMetadata | None:
        for value in (index.get("source_metadata"), manifest.get("source_metadata")):
            if isinstance(value, dict):
                try:
                    return VideoMetadata.from_dict(value)
                except (TypeError, ValueError) as exc:
                    raise ResultBundleError(f"source_metadata를 읽을 수 없습니다: {exc}") from exc
        return session.video_metadata

    def _analysis_range(self, index, manifest, session, samples) -> tuple[float, float]:
        value = index.get("analysis_range") or manifest.get("analysis_range")
        if isinstance(value, (list, tuple)) and len(value) == 2:
            start = self._required_float(value[0], "analysis_range", "start")
            end = self._required_float(value[1], "analysis_range", "end")
        else:
            start = float(session.analysis_start_sec)
            end = session.effective_end_sec()
            if end is None:
                end = max(sample.timestamp_sec for sample in samples)
        if end < start:
            raise ResultBundleError("분석 종료 시각이 시작 시각보다 빠릅니다.")
        return float(start), float(end)

    def _review_glasses(self, index, recipe, events) -> tuple[ReviewGlass, ...]:
        indexed = index.get("glasses") if isinstance(index.get("glasses"), list) else []
        indexed_by_id = {str(item.get("id")): item for item in indexed if isinstance(item, dict) and item.get("id")}
        states: dict[str, ResultState] = {}
        for event in events:
            if event.event_type == EventType.JUDGMENT_PASS:
                states[event.glass_id] = ResultState.PASS
            elif event.event_type == EventType.JUDGMENT_FAIL:
                states[event.glass_id] = ResultState.FAIL
            elif event.event_type == EventType.REVIEW_REQUIRED and event.glass_id not in states:
                states[event.glass_id] = ResultState.REVIEW_REQUIRED
        result = []
        for glass in recipe.glasses:
            item = indexed_by_id.get(glass.id, {})
            raw_state = item.get("result_status")
            try:
                state = ResultState(raw_state) if raw_state else states.get(glass.id, ResultState.NOT_APPLICABLE)
            except ValueError as exc:
                raise ResultBundleError(f"review_index.json glasses의 result_status가 올바르지 않습니다: {raw_state}") from exc
            result.append(ReviewGlass(glass.id, str(item.get("name") or glass.name), state))
        return tuple(result)

    def _row_enum(self, row, path, line, field, enum_type):
        value = self._required_text(row.get(field), path.name, line, field)
        try:
            return enum_type(value)
        except ValueError as exc:
            raise ResultBundleError(f"{path.name} row {line}: {field} enum 값이 올바르지 않습니다: {value}") from exc

    def _row_float(self, row, path, line, field) -> float:
        return self._required_float(row.get(field), path.name, f"row {line} {field}")

    def _row_optional_float(self, row, path, line, field) -> float | None:
        return self._optional_float(row.get(field), path.name, f"row {line} {field}")

    def _row_int(self, row, path, line, field) -> int:
        value = self._required_float(row.get(field), path.name, f"row {line} {field}")
        if not value.is_integer():
            raise ResultBundleError(f"{path.name} row {line}: {field}는 정수여야 합니다.")
        return int(value)

    def _row_optional_int(self, row, path, line, field) -> int | None:
        value = self._optional_float(row.get(field), path.name, f"row {line} {field}")
        if value is None:
            return None
        if not value.is_integer():
            raise ResultBundleError(f"{path.name} row {line}: {field}는 정수여야 합니다.")
        return int(value)

    def _row_bool(self, row, path, line, field) -> bool:
        value = row.get(field)
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
        raise ResultBundleError(f"{path.name} row {line}: {field} bool 값이 올바르지 않습니다: {value}")

    def _required_text(self, value, filename, line, field) -> str:
        text = str(value or "").strip()
        if not text:
            raise ResultBundleError(f"{filename} row {line}: {field} 값이 비어 있습니다.")
        return text

    def _required_float(self, value, filename, field) -> float:
        if value is None or value == "":
            raise ResultBundleError(f"{filename}: {field} 값이 비어 있습니다.")
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ResultBundleError(f"{filename}: {field} 숫자 값이 올바르지 않습니다: {value}") from exc

    def _required_int(self, value, filename, field) -> int:
        number = self._required_float(value, filename, field)
        if not number.is_integer():
            raise ResultBundleError(f"{filename}: {field}는 정수여야 합니다.")
        return int(number)

    def _optional_float(self, value, filename, field) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ResultBundleError(f"{filename}: {field} 숫자 값이 올바르지 않습니다: {value}") from exc
