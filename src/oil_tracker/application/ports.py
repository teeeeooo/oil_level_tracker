"""Ports: what the use cases need from outside. Adapters implement them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from oil_tracker.domain.recipe import Recipe


class RecipeNotFound(LookupError):
    pass


class RecipeNameTaken(ValueError):
    pass


@dataclass(frozen=True)
class RecipeListing:
    recipes: tuple[Recipe, ...]
    unreadable: tuple[tuple[str, str], ...]  # (file name, reason)


class RecipeStore(Protocol):
    def list_recipes(self) -> RecipeListing: ...

    def load(self, recipe_id: str) -> Recipe: ...

    def save(self, recipe: Recipe) -> None:
        """Create or replace the Recipe with this id. Renaming moves its file."""
        ...
