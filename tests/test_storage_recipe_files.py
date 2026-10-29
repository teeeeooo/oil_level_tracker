import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from oil_tracker.adapters.storage import locations
from oil_tracker.adapters.storage.recipe_files import (
    RecipeFolder,
    UnreadableRecipe,
    file_name_for,
    recipe_from_json,
    recipe_to_json,
)
from oil_tracker.application.ports import RecipeNameTaken, RecipeNotFound
from oil_tracker.domain.enums import JudgmentMode
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass, JudgmentRule, Recipe, ReferenceFrame


def make_recipe(recipe_id="r1", name="2호기 냉각") -> Recipe:
    return Recipe(
        id=recipe_id,
        name=name,
        reference_frame=ReferenceFrame(1280, 720, "SPL#4_Cooling_onoff_#2.mp4", 12.5, b"\xff\xd8\x00jpeg\xff\xd9"),
        glasses=(
            Glass("g1", "BASE", Ellipse(640.0, 360.0, 80.0, 200.0), 380.0),
            Glass(
                "g2",
                "Accum",
                Ellipse(900.5, 300.25, 60.0, 150.0),
                310.0,
                JudgmentRule(mode=JudgmentMode.HOLD_ABOVE_ZERO, allowed_sec=3.0, allowed_px=2.5),
            ),
        ),
        created_at="2026-10-29T01:02:03+00:00",
        updated_at="2026-10-29T04:05:06+00:00",
    )


def test_json_round_trip_keeps_every_field():
    recipe = make_recipe()
    assert recipe_from_json(recipe_to_json(recipe)) == recipe


def test_json_carries_format_and_schema_version():
    data = json.loads(recipe_to_json(make_recipe()))
    assert data["format"] == "oil-level-tracker-recipe"
    assert data["schema_version"] == 1


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": 2},  # a future version
        {"format": None},  # not ours, for example a v1 .oilrecipe
        {"glasses": [{"id": "g1"}]},
        {"reference_frame": {"width": "1280"}},
    ],
)
def test_reader_rejects_unknown_versions_and_broken_content(change):
    data = json.loads(recipe_to_json(make_recipe()))
    data.update(change)
    with pytest.raises(UnreadableRecipe):
        recipe_from_json(json.dumps(data))


def test_reader_rejects_text_that_is_not_json():
    with pytest.raises(UnreadableRecipe):
        recipe_from_json("not json")


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("2호기 냉각", "2호기 냉각.recipe.json"),
        ('A/B:C*?"<>|', "A_B_C______.recipe.json"),
        ("trailing. ", "trailing.recipe.json"),
        ("CON", "_CON.recipe.json"),
        ("lpt1.backup", "_lpt1.backup.recipe.json"),
        ("...", "_.recipe.json"),
    ],
)
def test_file_names_are_safe_on_windows(name, expected):
    assert file_name_for(name) == expected


def test_save_then_list_and_load(tmp_path):
    folder = RecipeFolder(tmp_path / "Recipes")
    assert folder.list_recipes().recipes == ()
    recipe = make_recipe()
    folder.save(recipe)
    assert (tmp_path / "Recipes" / "2호기 냉각.recipe.json").is_file()
    assert folder.list_recipes().recipes == (recipe,)
    assert folder.load("r1") == recipe
    with pytest.raises(RecipeNotFound):
        folder.load("missing")


def test_saving_again_replaces_and_renaming_moves_the_file(tmp_path):
    folder = RecipeFolder(tmp_path)
    folder.save(make_recipe())
    renamed = replace(make_recipe(), name="3호기")
    folder.save(renamed)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["3호기.recipe.json"]
    assert folder.load("r1") == renamed


def test_another_recipe_cannot_take_the_same_file_name(tmp_path):
    folder = RecipeFolder(tmp_path)
    folder.save(make_recipe("r1", "Line A"))
    with pytest.raises(RecipeNameTaken):
        folder.save(make_recipe("r2", "line a"))
    assert folder.load("r1").name == "Line A"


def test_list_reports_unreadable_and_duplicate_files(tmp_path):
    folder = RecipeFolder(tmp_path)
    folder.save(make_recipe("r1", "A"))
    (tmp_path / "broken.recipe.json").write_text("{", encoding="utf-8")
    (tmp_path / "copy of A.recipe.json").write_text(recipe_to_json(make_recipe("r1", "A")), encoding="utf-8")
    (tmp_path / "old.oilrecipe").write_text("{}", encoding="utf-8")  # v1 files are not listed
    listing = folder.list_recipes()
    assert [r.name for r in listing.recipes] == ["A"]
    assert sorted(name for name, _ in listing.unreadable) == ["broken.recipe.json", "copy of A.recipe.json"]


def test_failed_write_leaves_the_previous_file(tmp_path, monkeypatch):
    folder = RecipeFolder(tmp_path)
    folder.save(make_recipe())
    before = (tmp_path / "2호기 냉각.recipe.json").read_bytes()

    def fail(*_):
        raise OSError("disk full")

    monkeypatch.setattr("oil_tracker.adapters.storage.files.os.replace", fail)
    with pytest.raises(OSError):
        folder.save(replace(make_recipe(), updated_at="later"))
    assert (tmp_path / "2호기 냉각.recipe.json").read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["2호기 냉각.recipe.json"]


@pytest.mark.skipif(sys.platform == "win32", reason="the Windows path comes from the known-folder API")
def test_default_data_folder_is_under_documents():
    assert locations.default_data_folder() == Path.home() / "Documents" / "OilLevelTracker"
