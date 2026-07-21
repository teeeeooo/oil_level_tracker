import math

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


def test_ready_recipe_without_scale_has_no_scale_warning():
    recipe = InspectionRecipe.empty(320, 240)
    recipe.glasses.append(glass_config())
    recipe.glasses[0].mm_per_pixel = None
    result = RecipeValidationService().validate(recipe, ready_session())
    assert result.is_ready
    assert not any(issue.code == "WARN_SCALE" for issue in result.issues)


def test_valid_optional_scale_is_accepted_in_structural_and_full_validation():
    recipe = InspectionRecipe.empty(320, 240)
    recipe.glasses.append(glass_config())
    recipe.glasses[0].mm_per_pixel = 0.25
    validator = RecipeValidationService()
    assert not any(issue.code == "STRUCT_SCALE" for issue in validator.validate(recipe, structural_only=True).issues)
    assert validator.validate(recipe, ready_session()).is_ready


def test_enabled_optional_scale_must_be_finite_and_positive():
    validator = RecipeValidationService()
    for value in (0.0, -1.0, math.nan, math.inf, -math.inf):
        recipe = InspectionRecipe.empty(320, 240)
        recipe.glasses.append(glass_config())
        recipe.glasses[0].mm_per_pixel = value
        structural = validator.validate(recipe, structural_only=True)
        full = validator.validate(recipe, ready_session())
        assert any(issue.code == "STRUCT_SCALE" for issue in structural.errors)
        assert any(issue.code == "STRUCT_SCALE" for issue in full.errors)


def test_resolution_mismatch_blocks_until_confirmed():
    recipe = InspectionRecipe.empty(640, 480)
    recipe.glasses.append(glass_config())
    session = ready_session()
    session.resolution_confirmed = False
    result = RecipeValidationService().validate(recipe, session)
    assert any(issue.code == "READY_RESOLUTION" for issue in result.errors)
