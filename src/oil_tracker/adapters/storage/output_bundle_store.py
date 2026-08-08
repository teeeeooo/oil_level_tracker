from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
from uuid import uuid4

from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
from oil_tracker.adapters.reporting.html_reporter import HtmlReporter
from oil_tracker.adapters.storage.image_capture_store import ImageCaptureStore
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository, atomic_write_text
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import cleanup_debug_staging
from oil_tracker.application.ports.progress import (
    AnalysisCancelled,
    AnalysisStage,
    build_progress_update,
)
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.domain.session import AnalysisSession


_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]+')
_WHITESPACE = re.compile(r"\s+")
_MAX_RUN_COMPONENT_BYTES = 96


class OutputBundleStore:
    def __init__(self) -> None:
        self.csv = CsvExporter()
        self.graphs = GraphRenderer()
        self.html = HtmlReporter()
        self.recipes = JsonRecipeRepository()
        self.captures = ImageCaptureStore()

    def write_bundle(
        self,
        result: AnalysisResult,
        recipe: InspectionRecipe,
        session: AnalysisSession,
        root: Path | None = None,
        debug_artifacts: dict | None = None,
        *,
        progress=None,
        cancellation=None,
    ) -> Path:
        root = Path(root or session.output_directory or Path.cwd()).expanduser()
        root.mkdir(parents=True, exist_ok=True)
        name = _result_bundle_name(session, datetime.now())
        final = _unique_path(root / name)
        temporary = root / f".{final.name}.tmp-{uuid4().hex[:8]}"
        completion = result.debug_trace_completion
        report_presentation = build_report_presentation(result, recipe)
        committed = False
        try:
            _check_cancelled(cancellation, AnalysisStage.RESULT_IMAGES)
            _emit(
                progress,
                AnalysisStage.RESULT_IMAGES,
                0.0,
                message="이벤트 장면 이미지를 준비하고 있습니다.",
            )
            for dirname in ("captures", "graphs", "assets", "logs"):
                (temporary / dirname).mkdir(parents=True, exist_ok=True)
            if completion is not None or debug_artifacts:
                (temporary / "debug").mkdir(parents=True, exist_ok=True)
            self.captures.create_event_captures(
                result,
                session.input_video_path,
                temporary / "captures",
                recipe=recipe,
                presentation=report_presentation,
                cancellation=cancellation,
                progress=lambda completed, total: _emit(
                    progress,
                    AnalysisStage.RESULT_IMAGES,
                    completed / max(1, total),
                    message="이벤트 장면 이미지를 생성하고 있습니다.",
                    completed=completed,
                    total=total,
                ),
            )
            _emit(
                progress,
                AnalysisStage.RESULT_IMAGES,
                1.0,
                message="결과 이미지 생성을 마쳤습니다.",
            )

            _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
            snapshot_steps = 6
            _emit(
                progress,
                AnalysisStage.CSV_AND_SNAPSHOTS,
                0.0,
                message="CSV와 결과 snapshot을 저장하고 있습니다.",
                total=snapshot_steps,
            )
            self.csv.export(result, temporary / "tracking_data.csv", temporary / "events.csv")
            _emit_snapshot(progress, 1, snapshot_steps, "tracking과 event CSV 저장 완료")
            _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
            self.recipes.save(temporary / "recipe_snapshot.oilrecipe", recipe)
            _emit_snapshot(progress, 2, snapshot_steps, "분석 프로필 snapshot 저장 완료")
            _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
            atomic_write_text(
                temporary / "session.json",
                json.dumps(session.to_dict(), ensure_ascii=False, indent=2),
            )
            _emit_snapshot(progress, 3, snapshot_steps, "분석 session snapshot 저장 완료")
            _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
            atomic_write_text(
                temporary / "retrospective_interpretation.json",
                json.dumps(
                    _retrospective_payload(result, session),
                    ensure_ascii=False,
                    indent=2,
                ),
            )
            _emit_snapshot(progress, 4, snapshot_steps, "retrospective interpretation 저장 완료")
            _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
            if completion is not None:
                _copy_debug_staging(
                    Path(completion.staging_directory),
                    temporary / "debug",
                    cancellation=cancellation,
                )
            if debug_artifacts:
                for relative, source in debug_artifacts.items():
                    _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
                    destination = temporary / "debug" / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
            _emit_snapshot(progress, 5, snapshot_steps, "debug snapshot 준비 완료")
            review_index = _review_index(result, recipe, session, completion)
            atomic_write_text(
                temporary / "review_index.json",
                json.dumps(review_index, ensure_ascii=False, indent=2),
            )
            _emit_snapshot(progress, 6, snapshot_steps, "결과 검토 index 저장 완료")

            _check_cancelled(cancellation, AnalysisStage.GRAPHS_AND_REPORT)
            _emit(
                progress,
                AnalysisStage.GRAPHS_AND_REPORT,
                0.0,
                message="유면 graph를 생성하고 있습니다.",
            )
            graph_paths = self.graphs.render(
                result,
                temporary / "graphs",
                recipe,
                presentation=report_presentation,
                cancellation=cancellation,
                progress=lambda completed, total: _emit(
                    progress,
                    AnalysisStage.GRAPHS_AND_REPORT,
                    0.85 * completed / max(1, total),
                    message="유면 graph를 생성하고 있습니다.",
                    completed=completed,
                    total=total,
                ),
            )
            _check_cancelled(cancellation, AnalysisStage.GRAPHS_AND_REPORT)
            self.html.render(
                result,
                recipe,
                session,
                graph_paths,
                temporary / "report.html",
                presentation=report_presentation,
            )
            _emit(
                progress,
                AnalysisStage.GRAPHS_AND_REPORT,
                1.0,
                message="graph와 HTML 보고서 생성을 마쳤습니다.",
            )

            _check_cancelled(cancellation, AnalysisStage.BUNDLE_FINALIZATION)
            _emit(
                progress,
                AnalysisStage.BUNDLE_FINALIZATION,
                0.0,
                message="결과 bundle을 검증하고 마무리하고 있습니다.",
                total=4,
            )
            result.manifest["output_bundle"] = final.name
            result.manifest["result_status"] = result.overall_state.value
            result.manifest["run_name"] = session.run_name
            result.manifest["review_index"] = "review_index.json"
            result.manifest["result_semantics_version"] = 2
            result.manifest["retrospective_interpretation"] = "retrospective_interpretation.json"
            result.manifest["debug_trace_level"] = session.debug_trace_level.value
            result.manifest["debug_record_count"] = completion.record_count if completion is not None else 0
            if completion is not None:
                result.manifest["debug_index"] = "debug/debug_index.json"
                result.manifest["debug_trace"] = "debug/debug_trace.jsonl"
            atomic_write_text(
                temporary / "analysis_manifest.json",
                json.dumps(result.manifest, ensure_ascii=False, indent=2),
            )
            _emit_finalization(progress, 1, 4, "최종 manifest 저장 완료")
            atomic_write_text(
                temporary / "logs" / "analysis.log",
                f"run_id={result.run_id}\nstatus={result.overall_state.value}\n",
            )
            _emit_finalization(progress, 2, 4, "분석 log 저장 완료")
            _validate_temporary_bundle(temporary)
            _emit_finalization(progress, 3, 4, "임시 bundle 검증 완료")
            _check_cancelled(cancellation, AnalysisStage.BUNDLE_FINALIZATION)
            os.replace(temporary, final)
            committed = True
            result.output_directory = str(final)
            cleanup_debug_staging(completion)
            result.debug_trace_completion = None
            _emit(
                progress,
                AnalysisStage.BUNDLE_FINALIZATION,
                1.0,
                message="결과 bundle 마무리를 완료했습니다.",
                completed=4,
                total=4,
                finalization_committed=True,
            )
            return final
        except Exception:
            if not committed and temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
            if not committed:
                cleanup_debug_staging(completion)
                result.debug_trace_completion = None
            raise


def _copy_debug_staging(staging: Path, destination: Path, *, cancellation=None) -> None:
    if not staging.is_dir():
        raise OSError(f"Debug trace staging directory is missing: {staging}")
    for source in staging.rglob("*"):
        _check_cancelled(cancellation, AnalysisStage.CSV_AND_SNAPSHOTS)
        relative = source.relative_to(staging)
        target = destination / relative
        if source.is_symlink():
            raise OSError("Debug trace staging must not contain symbolic links.")
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _validate_temporary_bundle(temporary: Path) -> None:
    required = (
        "report.html",
        "tracking_data.csv",
        "events.csv",
        "recipe_snapshot.oilrecipe",
        "session.json",
        "analysis_manifest.json",
        "review_index.json",
        "retrospective_interpretation.json",
        "graphs/combined_levels.png",
        "logs/analysis.log",
    )
    missing = [relative for relative in required if not (temporary / relative).is_file()]
    if missing:
        raise OSError("Temporary result bundle is incomplete: " + ", ".join(missing))


def _check_cancelled(cancellation, stage: AnalysisStage) -> None:
    if cancellation is not None and cancellation.cancelled:
        label = build_progress_update(stage, 0.0).stage_label
        raise AnalysisCancelled(f"Analysis was cancelled during {label}.")


def _emit(progress, stage: AnalysisStage, fraction: float, **kwargs) -> None:
    if progress is not None:
        progress(build_progress_update(stage, fraction, **kwargs))


def _emit_snapshot(progress, completed: int, total: int, message: str) -> None:
    _emit(
        progress,
        AnalysisStage.CSV_AND_SNAPSHOTS,
        completed / max(1, total),
        message=message,
        completed=completed,
        total=total,
    )


def _emit_finalization(progress, completed: int, total: int, message: str) -> None:
    _emit(
        progress,
        AnalysisStage.BUNDLE_FINALIZATION,
        min(0.9, completed / max(1, total)),
        message=message,
        completed=completed,
        total=total,
    )


def _retrospective_payload(result: AnalysisResult, session: AnalysisSession) -> dict:
    return {
        "schema_version": 1,
        "result_semantics_version": 2,
        "run_id": result.run_id,
        "current_run_confirmations": {
            glass_id: confirmation.to_dict()
            for glass_id, confirmation in session.initial_state_confirmations.items()
        },
        "interpretations": [
            glass_result.retrospective.to_dict()
            for glass_result in result.glass_results
            if glass_result.retrospective is not None
        ],
        "coverage": {
            glass_result.glass_id: {
                "observed": glass_result.valid_coverage_ratio,
                "effective_state_aware": glass_result.effective_state_aware_coverage_ratio,
            }
            for glass_result in result.glass_results
        },
    }


def _review_index(result: AnalysisResult, recipe: InspectionRecipe, session: AnalysisSession, completion=None) -> dict:
    payload = {
        "schema_version": 2,
        "result_semantics_version": 2,
        "run_id": result.run_id,
        "run_name": session.run_name,
        "source_video_path": session.input_video_path,
        "source_metadata": session.video_metadata.to_dict() if session.video_metadata else {},
        "analysis_range": [session.analysis_start_sec, session.effective_end_sec()],
        "compressor_start_sec": session.compressor_start_sec,
        "recipe_snapshot": "recipe_snapshot.oilrecipe",
        "session": "session.json",
        "tracking_data": "tracking_data.csv",
        "events": "events.csv",
        "manifest": "analysis_manifest.json",
        "retrospective_interpretation": "retrospective_interpretation.json",
        "glasses": [
            {
                "id": glass_result.glass_id,
                "name": glass_result.glass_name,
                "result_status": glass_result.result_state.value,
                "observed_coverage_ratio": glass_result.valid_coverage_ratio,
                "effective_state_aware_coverage_ratio": glass_result.effective_state_aware_coverage_ratio,
                "retrospective_status": (
                    glass_result.retrospective.status.value
                    if glass_result.retrospective is not None
                    else "NOT_APPLICABLE"
                ),
            }
            for glass_result in result.glass_results
        ],
        "debug_trace_level": session.debug_trace_level.value,
        "debug_record_count": completion.record_count if completion is not None else 0,
    }
    if completion is not None:
        payload.update(
            {
                "debug_schema_version": 1,
                "debug_index": "debug/debug_index.json",
                "debug_trace": "debug/debug_trace.jsonl",
            }
        )
    return payload


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.name}_{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def _result_bundle_name(session: AnalysisSession, now: datetime) -> str:
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    run_component = _safe_run_name_component(session.run_name)
    if run_component:
        return f"oil_level_analysis_{run_component}_{timestamp}"
    return f"oil_level_analysis_{timestamp}"


def _safe_run_name_component(value: str) -> str:
    text = unicodedata.normalize("NFC", str(value or "")).strip()
    text = "".join(
        "_" if unicodedata.category(character).startswith("C") else character
        for character in text
    )
    text = _UNSAFE_FILENAME_CHARS.sub("_", text)
    text = _WHITESPACE.sub("_", text)
    text = re.sub(r"_+", "_", text).strip(" ._-")
    if not text or not any(character.isalnum() for character in text):
        return ""
    text = _truncate_utf8(text, _MAX_RUN_COMPONENT_BYTES).rstrip(" ._-")
    return text if any(character.isalnum() for character in text) else ""


def _truncate_utf8(value: str, max_bytes: int) -> str:
    parts: list[str] = []
    used = 0
    for character in value:
        size = len(character.encode("utf-8"))
        if used + size > max_bytes:
            break
        parts.append(character)
        used += size
    return "".join(parts)
