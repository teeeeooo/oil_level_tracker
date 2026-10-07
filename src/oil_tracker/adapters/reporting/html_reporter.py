from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from oil_tracker import DETECTOR_VERSION, __version__
from oil_tracker.application.services.report_presentation import (
    ReportPresentation,
    build_report_presentation,
    format_landmark_level,
)
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.domain.session import AnalysisSession


class HtmlReporter:
    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parent / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,  # Templates end in .j2; suffix-based HTML detection misses them.
        )

    def render(
        self,
        result: AnalysisResult,
        recipe: InspectionRecipe,
        session: AnalysisSession,
        graph_paths: dict[str, str],
        output_path: Path,
        *,
        presentation: ReportPresentation | None = None,
        source_contexts: dict[str, dict] | None = None,
    ) -> None:
        template = self.environment.get_template("report.html.j2")
        presentation = presentation or build_report_presentation(result, recipe)
        html = template.render(
            result=result,
            recipe=recipe,
            session=session,
            graph_paths=graph_paths,
            source_contexts=source_contexts or {},
            presentation=presentation,
            glass_configs={glass.id: glass for glass in recipe.glasses},
            format_landmark_level=format_landmark_level,
            video_name=Path(session.input_video_path).name,
            app_version=__version__,
            detector_version=DETECTOR_VERSION,
        )
        # UTF-8 BOM helps Windows browsers and text viewers consistently detect Korean text.
        output_path.write_bytes(html.encode("utf-8-sig"))
