from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession


class AnalyzeVideoUseCase:
    def __init__(self, pipeline: AnalysisPipeline) -> None:
        self.pipeline = pipeline

    def execute(self, recipe: InspectionRecipe, session: AnalysisSession, progress=None, cancellation=None):
        return self.pipeline.run(recipe, session, progress=progress, cancellation=cancellation)
