from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from oil_tracker.domain.recipe import InspectionRecipe


class JsonRecipeRepository:
    def save(self, path: Path, recipe: InspectionRecipe) -> None:
        if path.suffix.lower() != ".oilrecipe":
            path = path.with_suffix(".oilrecipe")
        payload = json.dumps(recipe.to_dict(), ensure_ascii=False, indent=2, allow_nan=False)
        atomic_write_text(path, payload)

    def load(self, path: Path) -> InspectionRecipe:
        data = json.loads(path.read_text(encoding="utf-8"))
        return InspectionRecipe.from_dict(data)


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
