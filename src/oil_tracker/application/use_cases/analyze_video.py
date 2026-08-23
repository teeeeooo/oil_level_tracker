from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from oil_tracker.application.ports.result_store import ResultStore
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.domain.session import AnalysisSession


@dataclass(frozen=True)
class AnalyzeVideoOutput:
    result: AnalysisResult
    output_path: Path


class AnalyzeVideoUseCase:
    """Own the complete analyze-and-persist application transaction."""

    def __init__(self, pipeline: AnalysisPipeline, result_store: ResultStore) -> None:
        self.pipeline = pipeline
        self.result_store = result_store

    def execute(
        self,
        recipe: InspectionRecipe,
        session: AnalysisSession,
        *,
        output_root: Path | None = None,
        progress=None,
        cancellation=None,
    ) -> AnalyzeVideoOutput:
        result = self.pipeline.run(
            recipe,
            session,
            progress=progress,
            cancellation=cancellation,
        )
        output_path = self.result_store.write_bundle(
            result,
            recipe,
            session,
            output_root,
            progress=progress,
            cancellation=cancellation,
        )
        return AnalyzeVideoOutput(result=result, output_path=output_path)
