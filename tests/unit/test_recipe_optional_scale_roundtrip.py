from oil_tracker.domain.recipe import InspectionRecipe


def test_optional_scale_and_saved_glass_name_round_trip_without_schema_change():
    recipe = InspectionRecipe.empty(640, 480)
    glass = InspectionRecipe.default_glass(640, 480)
    glass.name = "유면 관찰창 legacy name"
    glass.mm_per_pixel = 0.25
    recipe.glasses.append(glass)

    payload = recipe.to_dict()
    restored = InspectionRecipe.from_dict(payload)

    assert restored.schema_version == recipe.schema_version == 1
    assert restored.glasses[0].name == "유면 관찰창 legacy name"
    assert restored.glasses[0].mm_per_pixel == 0.25
    assert restored.to_dict()["glasses"][0]["mm_per_pixel"] == 0.25


def test_scale_off_round_trip_stores_none_and_new_default_uses_glass_term():
    recipe = InspectionRecipe.empty(640, 480)
    glass = InspectionRecipe.default_glass(640, 480, 2)
    glass.mm_per_pixel = None
    recipe.glasses.append(glass)

    restored = InspectionRecipe.from_dict(recipe.to_dict())

    assert glass.name == "Glass 2"
    assert restored.glasses[0].mm_per_pixel is None
    assert restored.to_dict()["glasses"][0]["mm_per_pixel"] is None
