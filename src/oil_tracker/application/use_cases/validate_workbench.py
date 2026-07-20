from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession
from oil_tracker.domain.validation import ValidationResult


class ValidateWorkbenchUseCase:
    def __init__(self, service: RecipeValidationService) -> None:
        self.service = service

    def execute(self, recipe: InspectionRecipe, session: AnalysisSession) -> ValidationResult:
        return self.service.validate(recipe, session)
