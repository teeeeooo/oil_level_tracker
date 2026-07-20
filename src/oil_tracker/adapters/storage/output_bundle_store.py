from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import shutil
from uuid import uuid4

from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
from oil_tracker.adapters.reporting.html_reporter import HtmlReporter
from oil_tracker.adapters.storage.image_capture_store import ImageCaptureStore
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository, atomic_write_text
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import cleanup_debug_staging
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.domain.session import AnalysisSession


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
    ) -> Path:
        root = root or Path(session.output_directory or Path.cwd())
        root.mkdir(parents=True, exist_ok=True)
        name = datetime.now().strftime("oil_level_analysis_%Y%m%d_%H%M%S")
        final = _unique_path(root / name)
        temporary = root / f".{final.name}.tmp-{uuid4().hex[:8]}"
        completion = result.debug_trace_completion
        try:
            for dirname in ("captures", "graphs", "assets", "logs"):
                (temporary / dirname).mkdir(parents=True, exist_ok=True)
            if completion is not None or debug_artifacts:
                (temporary / "debug").mkdir(parents=True, exist_ok=True)
            self.captures.create_event_captures(result, session.input_video_path, temporary / "captures")
            self.csv.export(result, temporary / "tracking_data.csv", temporary / "events.csv")
            graph_paths = self.graphs.render(result, temporary / "graphs")
            self.recipes.save(temporary / "recipe_snapshot.oilrecipe", recipe)
            atomic_write_text(temporary / "session.json", json.dumps(session.to_dict(), ensure_ascii=False, indent=2))
            if completion is not None:
                _copy_debug_staging(Path(completion.staging_directory), temporary / "debug")
            if debug_artifacts:
                for relative, source in debug_artifacts.items():
                    destination = temporary / "debug" / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
            review_index = _review_index(result, recipe, session, completion)
            atomic_write_text(
                temporary / "review_index.json",
                json.dumps(review_index, ensure_ascii=False, indent=2),
            )
            result.manifest["output_bundle"] = final.name
            result.manifest["result_status"] = result.overall_state.value
            result.manifest["review_index"] = "review_index.json"
            result.manifest["debug_trace_level"] = session.debug_trace_level.value
            result.manifest["debug_record_count"] = completion.record_count if completion is not None else 0
            if completion is not None:
                result.manifest["debug_index"] = "debug/debug_index.json"
                result.manifest["debug_trace"] = "debug/debug_trace.jsonl"
            atomic_write_text(temporary / "analysis_manifest.json", json.dumps(result.manifest, ensure_ascii=False, indent=2))
            self.html.render(result, recipe, session, graph_paths, temporary / "report.html")
            atomic_write_text(temporary / "logs" / "analysis.log", f"run_id={result.run_id}\nstatus={result.overall_state.value}\n")
            os.replace(temporary, final)
            result.output_directory = str(final)
            cleanup_debug_staging(completion)
            result.debug_trace_completion = None
            return final
        except Exception:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
            cleanup_debug_staging(completion)
            result.debug_trace_completion = None
            raise


def _copy_debug_staging(staging: Path, destination: Path) -> None:
    if not staging.is_dir():
        raise OSError(f"Debug trace staging directory is missing: {staging}")
    for source in staging.rglob("*"):
        relative = source.relative_to(staging)
        target = destination / relative
        if source.is_symlink():
            raise OSError("Debug trace staging must not contain symbolic links.")
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _review_index(result: AnalysisResult, recipe: InspectionRecipe, session: AnalysisSession, completion=None) -> dict:
    payload = {
        "schema_version": 1,
        "run_id": result.run_id,
        "source_video_path": session.input_video_path,
        "source_metadata": session.video_metadata.to_dict() if session.video_metadata else {},
        "analysis_range": [session.analysis_start_sec, session.effective_end_sec()],
        "compressor_start_sec": session.compressor_start_sec,
        "recipe_snapshot": "recipe_snapshot.oilrecipe",
        "session": "session.json",
        "tracking_data": "tracking_data.csv",
        "events": "events.csv",
        "manifest": "analysis_manifest.json",
        "glasses": [
            {
                "id": glass_result.glass_id,
                "name": glass_result.glass_name,
                "result_status": glass_result.result_state.value,
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
