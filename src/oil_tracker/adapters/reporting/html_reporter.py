from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from oil_tracker import DETECTOR_VERSION, __version__
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.domain.session import AnalysisSession


class HtmlReporter:
    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parent / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(
        self,
        result: AnalysisResult,
        recipe: InspectionRecipe,
        session: AnalysisSession,
        graph_paths: dict[str, str],
        output_path: Path,
    ) -> None:
        template = self.environment.get_template("report.html.j2")
        html = template.render(
            result=result,
            recipe=recipe,
            session=session,
            graph_paths=graph_paths,
            app_version=__version__,
            detector_version=DETECTOR_VERSION,
        )
        # UTF-8 BOM helps Windows browsers and text viewers consistently detect Korean text.
        output_path.write_bytes(html.encode("utf-8-sig"))
