from __future__ import annotations

from copy import deepcopy
from typing import Callable

from PySide6.QtGui import QUndoCommand

from oil_tracker.domain.recipe import InspectionRecipe


class RecipeSnapshotCommand(QUndoCommand):
    """Restore complete recipe snapshots while keeping session/video state untouched."""

    def __init__(
        self,
        controller,
        before: dict,
        after: dict,
        selected_before: str | None,
        selected_after: str | None,
        text: str,
        restored: Callable[[], None],
        *,
        already_applied: bool = True,
    ) -> None:
        super().__init__(text)
        self.controller = controller
        self.before = deepcopy(before)
        self.after = deepcopy(after)
        self.selected_before = selected_before
        self.selected_after = selected_after
        self.restored = restored
        self._skip_first_redo = already_applied

    def undo(self) -> None:
        self._restore(self.before, self.selected_before)

    def redo(self) -> None:
        if self._skip_first_redo:
            self._skip_first_redo = False
            return
        self._restore(self.after, self.selected_after)

    def _restore(self, snapshot: dict, selected_id: str | None) -> None:
        before = self.controller.recipe.to_dict()
        self.controller.invalidate_initial_state_confirmations_for_recipe_transition(
            before,
            snapshot,
        )
        self.controller.recipe = InspectionRecipe.from_dict(deepcopy(snapshot))
        existing_ids = {glass.id for glass in self.controller.recipe.glasses}
        self.controller.selected_glass_id = selected_id if selected_id in existing_ids else (
            self.controller.recipe.glasses[0].id if self.controller.recipe.glasses else None
        )
        self.controller.mark_dirty()
        self.restored()
