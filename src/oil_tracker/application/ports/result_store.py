from __future__ import annotations

from pathlib import Path
from typing import Protocol

from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.domain.session import AnalysisSession


class ResultStore(Protocol):
    def write_bundle(self, result: AnalysisResult, recipe: InspectionRecipe, session: AnalysisSession, root: Path | None = None, debug_artifacts: dict | None = None) -> Path: ...
