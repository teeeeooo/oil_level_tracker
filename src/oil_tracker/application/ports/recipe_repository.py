from __future__ import annotations

from pathlib import Path
from typing import Protocol

from oil_tracker.domain.recipe import InspectionRecipe


class RecipeRepository(Protocol):
    def save(self, path: Path, recipe: InspectionRecipe) -> None: ...
    def load(self, path: Path) -> InspectionRecipe: ...
