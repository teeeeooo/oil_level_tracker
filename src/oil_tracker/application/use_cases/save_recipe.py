from pathlib import Path

from oil_tracker.application.ports.recipe_repository import RecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.recipe import InspectionRecipe


class SaveRecipeUseCase:
    def __init__(self, repository: RecipeRepository, validator: RecipeValidationService) -> None:
        self.repository = repository
        self.validator = validator

    def execute(self, path: Path, recipe: InspectionRecipe) -> None:
        result = self.validator.validate(recipe, structural_only=True)
        if not result.is_structurally_valid:
            raise ValueError("Recipe has structural errors and cannot be saved.")
        previous_updated_at = recipe.updated_at
        recipe.touch()
        try:
            self.repository.save(path, recipe)
        except Exception:
            recipe.updated_at = previous_updated_at
            raise
