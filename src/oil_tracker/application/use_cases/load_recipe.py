from pathlib import Path

from oil_tracker.application.ports.recipe_repository import RecipeRepository
from oil_tracker.domain.recipe import InspectionRecipe


class LoadRecipeUseCase:
    def __init__(self, repository: RecipeRepository) -> None:
        self.repository = repository

    def execute(self, path: Path) -> InspectionRecipe:
        return self.repository.load(path)
