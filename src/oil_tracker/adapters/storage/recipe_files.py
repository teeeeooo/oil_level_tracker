"""Recipe files: docs/20-architecture/recipe-file.md."""

from __future__ import annotations

import base64
import binascii
import json
import re
from pathlib import Path
from typing import Any

from oil_tracker.application.ports import RecipeListing, RecipeNameTaken, RecipeNotFound
from oil_tracker.domain.enums import JudgmentMode
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass, JudgmentRule, Recipe, ReferenceFrame

from .files import atomic_write_text

FORMAT = "oil-level-tracker-recipe"
SCHEMA_VERSION = 1
SUFFIX = ".recipe.json"

_RULE_NUMBERS = (
    "recovery_limit_sec",
    "stable_hold_sec",
    "minimum_valid_coverage_ratio",
    "allowed_sec",
    "allowed_px",
)
_ELLIPSE_NUMBERS = ("center_x", "center_y", "radius_x", "radius_y")
_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED = re.compile(r"^(con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(\..*)?$", re.IGNORECASE)


class UnreadableRecipe(ValueError):
    pass


def recipe_to_json(recipe: Recipe) -> str:
    frame = recipe.reference_frame
    data = {
        "format": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "id": recipe.id,
        "name": recipe.name,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
        "reference_frame": {
            "width": frame.width,
            "height": frame.height,
            "source_name": frame.source_name,
            "time_sec": frame.time_sec,
            "jpeg_base64": base64.b64encode(frame.jpeg).decode("ascii"),
        },
        "glasses": [
            {
                "id": glass.id,
                "name": glass.name,
                "ellipse": {key: getattr(glass.ellipse, key) for key in _ELLIPSE_NUMBERS},
                "zero_line_y": glass.zero_line_y,
                "judgment_rule": {
                    "mode": glass.judgment_rule.mode.value,
                    **{key: getattr(glass.judgment_rule, key) for key in _RULE_NUMBERS},
                },
            }
            for glass in recipe.glasses
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def recipe_from_json(text: str) -> Recipe:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise UnreadableRecipe("JSON 형식이 아닙니다.") from error
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise UnreadableRecipe("Recipe 파일이 아닙니다.")
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        raise UnreadableRecipe(f"지원하지 않는 Recipe 버전입니다: {version!r}")
    try:
        frame = data["reference_frame"]
        return Recipe(
            id=_text(data["id"]),
            name=_text(data["name"]),
            created_at=_text(data["created_at"]),
            updated_at=_text(data["updated_at"]),
            reference_frame=ReferenceFrame(
                width=_integer(frame["width"]),
                height=_integer(frame["height"]),
                source_name=_text(frame["source_name"]),
                time_sec=_number(frame["time_sec"]),
                jpeg=base64.b64decode(_text(frame["jpeg_base64"]), validate=True),
            ),
            glasses=tuple(_glass_from(raw) for raw in data["glasses"]),
        )
    except (KeyError, TypeError, ValueError, binascii.Error) as error:
        raise UnreadableRecipe(f"Recipe 내용이 올바르지 않습니다: {error}") from error


def _glass_from(raw: dict[str, Any]) -> Glass:
    rule = raw["judgment_rule"]
    return Glass(
        id=_text(raw["id"]),
        name=_text(raw["name"]),
        ellipse=Ellipse(**{key: _number(raw["ellipse"][key]) for key in _ELLIPSE_NUMBERS}),
        zero_line_y=_number(raw["zero_line_y"]),
        judgment_rule=JudgmentRule(
            mode=JudgmentMode(rule["mode"]),
            **{key: _number(rule[key]) for key in _RULE_NUMBERS},
        ),
    )


def _text(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError(f"expected text, got {type(value).__name__}")
    return value


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"expected a number, got {type(value).__name__}")
    return float(value)


def _integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected an integer, got {type(value).__name__}")
    return value


def file_name_for(recipe_name: str) -> str:
    """A Windows-safe file name for a Recipe name."""
    stem = _FORBIDDEN.sub("_", recipe_name.strip()).rstrip(". ")
    if not stem:
        stem = "_"
    if _RESERVED.match(stem):
        stem = "_" + stem
    return stem + SUFFIX


class RecipeFolder:
    """The Recipes folder. Implements application.ports.RecipeStore."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def list_recipes(self) -> RecipeListing:
        recipes: list[Recipe] = []
        unreadable: list[tuple[str, str]] = []
        seen: set[str] = set()
        for path, result in self._read_all():
            if isinstance(result, str):
                unreadable.append((path.name, result))
            elif result.id in seen:
                unreadable.append((path.name, "다른 파일과 Recipe ID가 같습니다."))
            else:
                seen.add(result.id)
                recipes.append(result)
        recipes.sort(key=lambda recipe: recipe.name.casefold())
        return RecipeListing(tuple(recipes), tuple(unreadable))

    def load(self, recipe_id: str) -> Recipe:
        for _, result in self._read_all():
            if isinstance(result, Recipe) and result.id == recipe_id:
                return result
        raise RecipeNotFound(f"Recipe를 찾을 수 없습니다: {recipe_id}")

    def save(self, recipe: Recipe) -> None:
        target = self.folder / file_name_for(recipe.name)
        previous: list[Path] = []
        for path, result in self._read_all():
            same_file = path.name.casefold() == target.name.casefold()
            same_recipe = isinstance(result, Recipe) and result.id == recipe.id
            if same_file and not same_recipe:
                raise RecipeNameTaken(f"같은 이름의 Recipe 파일이 이미 있습니다: {path.name}")
            if same_recipe and not same_file:
                previous.append(path)
        atomic_write_text(target, recipe_to_json(recipe))
        for path in previous:
            path.unlink(missing_ok=True)

    def _read_all(self) -> list[tuple[Path, Recipe | str]]:
        if not self.folder.is_dir():
            return []
        found: list[tuple[Path, Recipe | str]] = []
        for path in sorted(self.folder.glob("*" + SUFFIX)):
            try:
                found.append((path, recipe_from_json(path.read_text(encoding="utf-8"))))
            except UnreadableRecipe as error:
                found.append((path, str(error)))
            except (OSError, UnicodeDecodeError) as error:
                found.append((path, f"파일을 읽을 수 없습니다: {error}"))
        return found
