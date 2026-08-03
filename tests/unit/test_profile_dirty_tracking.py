from __future__ import annotations

import pytest

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession
from oil_tracker.ui.controllers.workbench_controller import PreparedWorkbenchReplacement, WorkbenchController


def _controller(repository=None):
    repository = repository or JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )


def test_initial_and_successfully_loaded_profile_are_clean(tmp_path):
    controller = _controller()
    assert controller.profile_has_unsaved_changes is False

    recipe = InspectionRecipe.empty(640, 480, "Loaded Profile")
    path = tmp_path / "loaded.oilrecipe"
    JsonRecipeRepository().save(path, recipe)
    controller.load(path)
    assert controller.profile_has_unsaved_changes is False


def test_save_establishes_clean_baseline_and_keeps_normalized_path(tmp_path):
    controller = _controller()
    controller.new_document(640, 480, "Unsaved Profile")
    controller.add_glass()
    assert controller.profile_has_unsaved_changes is True

    requested = tmp_path / "saved-profile"
    controller.save(requested)

    assert controller.recipe_path == requested.with_suffix(".oilrecipe")
    assert controller.recipe_path.is_file()
    assert controller.profile_has_unsaved_changes is False


def test_recipe_edit_dirty_and_restoring_serialized_content_returns_clean(tmp_path):
    controller = _controller()
    path = tmp_path / "profile.oilrecipe"
    controller.save(path)
    persisted = controller.recipe.to_dict()

    controller.recipe.name = "Changed"
    controller.mark_dirty()
    assert controller.profile_has_unsaved_changes is True

    controller.recipe = InspectionRecipe.from_dict(persisted)
    controller.mark_dirty()
    assert controller.profile_has_unsaved_changes is False


def test_session_only_changes_do_not_make_profile_dirty(tmp_path):
    controller = _controller()
    controller.save(tmp_path / "profile.oilrecipe")
    recipe_before = controller.recipe.to_dict()

    controller.state = WorkbenchState.ANALYZED
    controller.session.run_name = "Run 04"
    controller.session.analysis_start_sec = 1.0
    controller.session.analysis_end_sec = 9.0
    controller.session.compressor_start_sec = 2.0
    controller.session.sampling_fps = 3.0
    controller.mark_dirty()

    assert controller.state == WorkbenchState.DRAFT_DIRTY
    assert controller.recipe.to_dict() == recipe_before
    assert controller.profile_has_unsaved_changes is False


class _FailingSaveRepository(JsonRecipeRepository):
    def save(self, path, recipe):
        raise OSError("save failed")


def test_failed_save_does_not_establish_clean_baseline(tmp_path):
    controller = _controller(_FailingSaveRepository())
    controller.new_document(640, 480, "Unsaved")
    before = controller.recipe.to_dict()
    assert controller.profile_has_unsaved_changes is True

    with pytest.raises(OSError, match="save failed"):
        controller.save(tmp_path / "failed.oilrecipe")
    assert controller.recipe.to_dict() == before
    assert controller.profile_has_unsaved_changes is True


def test_new_profile_is_unsaved_but_same_profile_snapshot_starts_safe():
    controller = _controller()
    controller.new_document(640, 480, "New Profile")
    assert controller.recipe_path is None
    assert controller.profile_has_unsaved_changes is True

    class _Reader:
        def close(self):
            pass

    snapshot = InspectionRecipe.empty(640, 480, "Snapshot Profile")
    replacement = PreparedWorkbenchReplacement(
        recipe=InspectionRecipe.from_dict(snapshot.to_dict()),
        session=AnalysisSession(),
        reader=_Reader(),
        frame=object(),
        frame_index=0,
        timestamp_sec=0.0,
    )
    controller.commit_same_profile_video(replacement)

    assert controller.recipe_path is None
    assert controller.recipe.name == "Snapshot Profile"
    assert controller.profile_has_unsaved_changes is False
    controller.recipe.description = "user edit"
    assert controller.profile_has_unsaved_changes is True
