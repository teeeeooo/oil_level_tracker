from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.recent_profile_history import RecentProfileHistory
from oil_tracker.adapters.vision.debug_renderer import DebugRenderer
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow


class _Preview(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def request(self, *_args):
        pass


class _Analysis(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def start(self, *_args):
        pass

    def cancel(self):
        pass


def _controller() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )


def _window(qtbot, controller=None) -> MainWindow:
    window = MainWindow(controller or _controller(), _Preview(), _Analysis(), DebugRenderer())
    qtbot.addWidget(window)
    return window


def _write_profile(path: Path, name: str) -> InspectionRecipe:
    recipe = InspectionRecipe.empty(640, 480, name)
    recipe.glasses.append(InspectionRecipe.default_glass(640, 480))
    JsonRecipeRepository().save(path, recipe)
    return recipe


def test_successful_manual_load_registers_profile_and_restart_recovers_menu(
    qtbot, tmp_path, monkeypatch
):
    storage = tmp_path / "recent_profiles.json"
    profile = tmp_path / "수동 프로필.oilrecipe"
    _write_profile(profile, "수동 회수 프로필")
    history = RecentProfileHistory(storage)
    window = _window(qtbot)
    window.set_recent_profile_history(history)
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(profile), ""),
    )

    window.load_recipe()

    assert window.workbench.recipe.name == "수동 회수 프로필"
    assert Path(history.entries()[0].path) == profile
    restarted = RecentProfileHistory(storage)
    restarted_window = _window(qtbot)
    restarted_window.set_recent_profile_history(restarted)
    recent_actions = [action for action in restarted_window.recent_profile_menu.actions() if action.data()]
    assert len(recent_actions) == 1
    assert recent_actions[0].data() == str(profile)
    assert "수동 회수 프로필" in recent_actions[0].text()


def test_successful_save_registers_actual_normalized_oilrecipe_path(qtbot, tmp_path, monkeypatch):
    storage = tmp_path / "recent_profiles.json"
    controller = _controller()
    controller.recipe.name = "저장 프로필"
    controller.add_glass()
    window = _window(qtbot, controller)
    history = RecentProfileHistory(storage)
    window.set_recent_profile_history(history)
    requested = tmp_path / "저장 프로필"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(requested), ""),
    )

    window.save_recipe()

    actual = requested.with_suffix(".oilrecipe")
    assert actual.is_file()
    assert controller.recipe_path == actual
    assert Path(history.entries()[0].path) == actual
    assert history.entries()[0].profile_name == "저장 프로필"


def test_failed_profile_load_is_not_registered(qtbot, tmp_path, monkeypatch):
    history = RecentProfileHistory(tmp_path / "recent_profiles.json")
    window = _window(qtbot)
    window.set_recent_profile_history(history)
    missing = tmp_path / "missing.oilrecipe"
    errors = []
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(missing), ""),
    )
    monkeypatch.setattr(window, "_error", lambda title, message: errors.append((title, message)))

    window.load_recipe()

    assert errors and errors[0][0] == "프로필 열기 실패"
    assert history.entries() == ()


class _FailingHistory:
    def entries(self):
        return ()

    def record_recipe(self, _path, _recipe):
        raise OSError("history unavailable")


def test_history_failure_is_non_fatal_to_successful_load_and_save(qtbot, tmp_path, monkeypatch):
    source = tmp_path / "source.oilrecipe"
    _write_profile(source, "로드 성공")
    window = _window(qtbot)
    window.set_recent_profile_history(_FailingHistory())
    errors = []
    monkeypatch.setattr(window, "_error", lambda title, message: errors.append((title, message)))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: (str(source), ""))

    window.load_recipe()
    assert window.workbench.recipe.name == "로드 성공"
    assert window.workbench.recipe_path == source

    target = tmp_path / "save-after-history-failure"
    window.workbench.recipe_path = None
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_args, **_kwargs: (str(target), ""))
    window.save_recipe()

    assert target.with_suffix(".oilrecipe").is_file()
    assert errors == []


def test_recent_selection_uses_same_load_action_and_authoritative_recipe(qtbot, tmp_path, monkeypatch):
    storage = tmp_path / "recent_profiles.json"
    profile = tmp_path / "profile.oilrecipe"
    _write_profile(profile, "Authoritative Profile")
    seed = RecentProfileHistory(storage)
    seed.record_recipe(profile, InspectionRecipe.empty(640, 480, "Cached Name"))

    manual = _window(qtbot)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: (str(profile), ""))
    manual.load_recipe()
    manual_signature = (
        manual.workbench.recipe.to_dict(),
        manual.workbench.recipe_path,
        manual.workbench.state,
        manual.workbench.selected_glass_id,
    )

    recent = _window(qtbot)
    restarted = RecentProfileHistory(storage)
    recent.set_recent_profile_history(restarted)
    load_signals = []
    recent.actions["load"].triggered.connect(lambda *_args: load_signals.append(True))
    recent.open_recent_profile(profile)

    recent_signature = (
        recent.workbench.recipe.to_dict(),
        recent.workbench.recipe_path,
        recent.workbench.state,
        recent.workbench.selected_glass_id,
    )
    assert recent_signature == manual_signature
    assert load_signals == [True]
    assert restarted.entries()[0].profile_name == "Authoritative Profile"


def test_stale_recent_entry_does_not_block_valid_or_manual_profile(qtbot, tmp_path, monkeypatch):
    storage = tmp_path / "recent_profiles.json"
    valid = tmp_path / "valid.oilrecipe"
    stale = tmp_path / "stale.oilrecipe"
    manual = tmp_path / "manual.oilrecipe"
    valid_recipe = _write_profile(valid, "Valid")
    stale_recipe = _write_profile(stale, "Stale")
    _write_profile(manual, "Manual")
    history = RecentProfileHistory(storage)
    history.record_recipe(valid, valid_recipe)
    history.record_recipe(stale, stale_recipe)
    stale.unlink()

    window = _window(qtbot)
    window.set_recent_profile_history(RecentProfileHistory(storage))
    recent_actions = [action for action in window.recent_profile_menu.actions() if action.data()]
    assert len(recent_actions) == 2
    assert recent_actions[0].data() == str(stale)
    assert recent_actions[0].isEnabled() is False
    assert recent_actions[1].data() == str(valid)
    assert recent_actions[1].isEnabled() is True

    recent_actions[1].trigger()
    assert window.workbench.recipe.name == "Valid"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: (str(manual), ""))
    other = next(
        action
        for action in window.recent_profile_menu.actions()
        if action.objectName() == "otherProfileFileAction"
    )
    other.trigger()
    assert window.workbench.recipe.name == "Manual"
    assert window.workbench.recipe_path == manual
