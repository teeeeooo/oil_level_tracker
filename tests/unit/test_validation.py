from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from tests.fixtures.synthetic import glass_config


def ready_session():
    metadata = VideoMetadata("video.avi", 320, 240, 10, 5, 50)
    return AnalysisSession("video.avi", metadata, 0, 5, 0, 2, resolution_confirmed=True)


def test_readiness_requires_glass():
    result = RecipeValidationService().validate(InspectionRecipe.empty(320, 240), ready_session())
    assert any(issue.code == "READY_GLASS" for issue in result.errors)


def test_ready_recipe_passes_with_warnings_only():
    recipe = InspectionRecipe.empty(320, 240); recipe.glasses.append(glass_config())
    result = RecipeValidationService().validate(recipe, ready_session())
    assert result.is_ready
    assert any(issue.code == "WARN_SCALE" for issue in result.warnings)


def test_resolution_mismatch_blocks_until_confirmed():
    recipe = InspectionRecipe.empty(640, 480); recipe.glasses.append(glass_config())
    session = ready_session(); session.resolution_confirmed = False
    result = RecipeValidationService().validate(recipe, session)
    assert any(issue.code == "READY_RESOLUTION" for issue in result.errors)
