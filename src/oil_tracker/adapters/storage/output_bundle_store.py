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
        try:
            for dirname in ("captures", "graphs", "assets", "logs"):
                (temporary / dirname).mkdir(parents=True, exist_ok=True)
            if debug_artifacts:
                (temporary / "debug").mkdir(parents=True, exist_ok=True)
            self.captures.create_event_captures(result, session.input_video_path, temporary / "captures")
            self.csv.export(result, temporary / "tracking_data.csv", temporary / "events.csv")
            graph_paths = self.graphs.render(result, temporary / "graphs")
            self.recipes.save(temporary / "recipe_snapshot.oilrecipe", recipe)
            atomic_write_text(temporary / "session.json", json.dumps(session.to_dict(), ensure_ascii=False, indent=2))
            result.manifest["output_bundle"] = final.name
            result.manifest["result_status"] = result.overall_state.value
            atomic_write_text(temporary / "analysis_manifest.json", json.dumps(result.manifest, ensure_ascii=False, indent=2))
            self.html.render(result, recipe, session, graph_paths, temporary / "report.html")
            atomic_write_text(temporary / "logs" / "analysis.log", f"run_id={result.run_id}\nstatus={result.overall_state.value}\n")
            if debug_artifacts:
                for relative, source in debug_artifacts.items():
                    destination = temporary / "debug" / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
            os.replace(temporary, final)
            result.output_directory = str(final)
            return final
        except Exception:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
            raise


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.name}_{counter}")
        if not candidate.exists():
            return candidate
        counter += 1
