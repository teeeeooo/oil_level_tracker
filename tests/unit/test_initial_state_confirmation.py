from __future__ import annotations

import pytest

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.preflight import preflight_context_key
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.initial_state_confirmation import confirm_initial_state
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, InitialStateConfirmation, VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from tests.fixtures.synthetic import glass_config


def _recipe(state=InitialObservationState.FULL_NO_INTERFACE):
    recipe = InspectionRecipe.empty(320, 240)
    glass = glass_config()
    glass.initial_state = state
    recipe.glasses.append(glass)
    return recipe, glass


def _session():
    metadata = VideoMetadata("video.mp4", 320, 240, 10.0, 5.0, 50)
    return AnalysisSession(
        input_video_path="video.mp4",
        video_metadata=metadata,
        analysis_start_sec=0.0,
        analysis_end_sec=5.0,
        compressor_start_sec=1.0,
        sampling_fps=2.0,
        resolution_confirmed=True,
    )


def _final_validate(recipe, session):
    return RecipeValidationService().validate(
        recipe,
        session,
        require_run_confirmation=True,
    )


def test_auto_and_missing_current_run_confirmation_block_final_readiness():
    auto_recipe, _ = _recipe(InitialObservationState.AUTO)
    assert any(issue.code == "READY_INITIAL_STATE_AUTO" for issue in _final_validate(auto_recipe, _session()).errors)

    recipe, _ = _recipe()
    assert any(
        issue.code == "READY_INITIAL_STATE_CONFIRMATION"
        for issue in _final_validate(recipe, _session()).errors
    )


def test_explicit_unknown_confirmation_satisfies_readiness_without_reconstruction_authority():
    recipe, glass = _recipe(InitialObservationState.UNKNOWN_REVIEW)
    session = _session()
    session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        InitialObservationState.UNKNOWN_REVIEW,
        session.input_video_path,
        session.analysis_start_sec,
    )
    result = _final_validate(recipe, session)
    assert not any(issue.code.startswith("READY_INITIAL_STATE") for issue in result.errors)


def test_confirmation_is_stale_when_state_video_or_analysis_start_changes():
    recipe, glass = _recipe()
    session = _session()
    session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        glass.initial_state,
        session.input_video_path,
        session.analysis_start_sec,
    )
    assert not any(issue.code.startswith("READY_INITIAL_STATE") for issue in _final_validate(recipe, session).errors)

    for mutation in (
        lambda: setattr(glass, "initial_state", InitialObservationState.EMPTY_NO_INTERFACE),
        lambda: setattr(session, "input_video_path", "other.mp4"),
        lambda: setattr(session, "analysis_start_sec", 0.5),
    ):
        original_state = glass.initial_state
        original_path = session.input_video_path
        original_start = session.analysis_start_sec
        mutation()
        assert any(
            issue.code == "READY_INITIAL_STATE_CONFIRMATION_STALE"
            for issue in _final_validate(recipe, session).errors
        )
        glass.initial_state = original_state
        session.input_video_path = original_path
        session.analysis_start_sec = original_start


def test_confirmation_round_trips_in_session_but_legacy_session_defaults_empty():
    session = _session()
    session.initial_state_confirmations["g1"] = InitialStateConfirmation(
        InitialObservationState.FULL_NO_INTERFACE,
        session.input_video_path,
        session.analysis_start_sec,
    )
    restored = AnalysisSession.from_dict(session.to_dict())
    assert restored.initial_state_confirmations == session.initial_state_confirmations

    legacy = session.to_dict()
    legacy.pop("initial_state_confirmations")
    assert AnalysisSession.from_dict(legacy).initial_state_confirmations == {}


def test_application_confirmation_policy_validates_and_snapshots_current_run_context():
    _, glass = _recipe()
    session = _session()

    confirmation = confirm_initial_state(glass, session)

    assert session.initial_state_confirmations == {glass.id: confirmation}
    assert confirmation.matches(glass.initial_state, session)

    with pytest.raises(ValueError, match="does not match"):
        confirm_initial_state(
            glass,
            session,
            InitialObservationState.EMPTY_NO_INTERFACE,
        )
    glass.initial_state = InitialObservationState.AUTO
    with pytest.raises(ValueError, match="AUTO cannot be confirmed"):
        confirm_initial_state(glass, session)


def test_unrelated_session_and_glass_edits_keep_current_run_confirmation():
    recipe, glass = _recipe()
    session = _session()
    controller = WorkbenchController(
        SaveRecipeUseCase(JsonRecipeRepository(), RecipeValidationService()),
        LoadRecipeUseCase(JsonRecipeRepository()),
        ValidateWorkbenchUseCase(RecipeValidationService()),
        reader_factory=lambda _path: None,
    )
    controller.recipe = recipe
    controller.session = session
    confirmation = controller.confirm_initial_state(glass.id)

    session.analysis_end_sec = 4.0
    session.compressor_start_sec = 2.0
    session.sampling_fps = 1.0
    before = recipe.to_dict()
    glass.detector_settings.minimum_final_confidence = 0.7
    after = recipe.to_dict()
    controller.invalidate_initial_state_confirmations_for_recipe_transition(before, after)

    assert controller.initial_state_confirmation(glass.id) == confirmation


def test_preflight_context_does_not_require_or_establish_confirmation():
    recipe, glass = _recipe()
    session = _session()
    before = preflight_context_key(recipe, session)
    assert session.initial_state_confirmations == {}
    session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        glass.initial_state,
        session.input_video_path,
        session.analysis_start_sec,
    )
    after = preflight_context_key(recipe, session)
    assert before == after


def test_fresh_confirmation_does_not_dirty_profile_and_controller_invalidates_owned_context(tmp_path):
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    controller = WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )
    controller.new_document(320, 240)
    glass = controller.add_glass()
    controller.update_initial_state(glass.id, InitialObservationState.FULL_NO_INTERFACE)
    controller.session.input_video_path = "video.mp4"
    controller.session.analysis_start_sec = 0.0
    controller.save(tmp_path / "profile.oilrecipe")
    assert controller.profile_has_unsaved_changes is False

    controller.confirm_initial_state(glass.id)
    assert controller.profile_has_unsaved_changes is False
    assert controller.initial_state_confirmation(glass.id) is not None

    controller.update_analysis_start(0.5)
    assert controller.initial_state_confirmation(glass.id) is None
    controller.confirm_initial_state(glass.id)
    controller.update_initial_state(glass.id, InitialObservationState.EMPTY_NO_INTERFACE)
    assert controller.initial_state_confirmation(glass.id) is None

    controller.confirm_initial_state(glass.id)
    controller.set_glass_enabled(glass.id, False)
    assert controller.initial_state_confirmation(glass.id) is not None
    controller.set_glass_enabled(glass.id, True)
    assert controller.initial_state_confirmation(glass.id) is None


def test_gui_readiness_and_headless_pipeline_share_final_confirmation_authority():
    recipe, glass = _recipe()
    session = _session()
    validation = ValidateWorkbenchUseCase(RecipeValidationService()).execute(recipe, session)
    assert any(issue.code == "READY_INITIAL_STATE_CONFIRMATION" for issue in validation.errors)

    reader_called = False

    def forbidden_reader(_path):
        nonlocal reader_called
        reader_called = True
        raise AssertionError("validation must block before decode")

    pipeline = AnalysisPipeline(forbidden_reader, object(), RecipeValidationService())
    with pytest.raises(ValueError, match="Current-run analysis start state confirmation is required"):
        pipeline.run(recipe, session)
    assert reader_called is False
    assert glass.initial_state is InitialObservationState.FULL_NO_INTERFACE


def test_new_analysis_session_starts_without_confirmation():
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    controller = WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )
    controller.new_document(320, 240)
    glass = controller.add_glass()
    controller.update_initial_state(glass.id, InitialObservationState.FULL_NO_INTERFACE)
    controller.session.input_video_path = "video.mp4"
    controller.confirm_initial_state(glass.id)
    assert controller.session.initial_state_confirmations

    controller.new_document(320, 240)
    assert controller.session.initial_state_confirmations == {}
