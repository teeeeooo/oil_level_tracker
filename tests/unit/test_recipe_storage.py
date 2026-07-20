import json

import pytest

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.domain.recipe import InspectionRecipe
from tests.fixtures.synthetic import glass_config


def test_recipe_json_round_trip(tmp_path):
    recipe = InspectionRecipe.empty(320, 240, "Recipe")
    recipe.glasses.append(glass_config())
    path = tmp_path / "recipe.oilrecipe"
    JsonRecipeRepository().save(path, recipe)
    loaded = JsonRecipeRepository().load(path)
    assert loaded.to_dict() == recipe.to_dict()
    assert not list(tmp_path.glob("*.tmp"))


def test_unknown_future_schema_rejected(tmp_path):
    path = tmp_path / "future.oilrecipe"
    path.write_text(json.dumps({"schema_version": 99}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        JsonRecipeRepository().load(path)
