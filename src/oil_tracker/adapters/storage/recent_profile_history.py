from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
from uuid import uuid4

from oil_tracker.adapters.system.app_paths import user_data_dir
from oil_tracker.domain.recipe import InspectionRecipe


LOGGER = logging.getLogger(__name__)
RECENT_PROFILE_HISTORY_SCHEMA_VERSION = 1
DEFAULT_RECENT_PROFILE_LIMIT = 8


@dataclass(frozen=True)
class RecentProfileEntry:
    path: str
    profile_name: str = ""

    def is_available(self) -> bool:
        return Path(self.path).expanduser().is_file()

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "profile_name": self.profile_name}

    @classmethod
    def from_dict(cls, payload) -> "RecentProfileEntry":
        if not isinstance(payload, dict):
            raise ValueError("recent profile entry must be an object")
        path = payload.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("recent profile path is missing")
        return cls(
            path=path,
            profile_name=_optional_text(payload.get("profile_name")),
        )


class RecentProfileHistory:
    """Persist bounded Profile navigation metadata outside .oilrecipe files."""

    def __init__(
        self,
        storage_path: str | Path | None = None,
        *,
        max_entries: int = DEFAULT_RECENT_PROFILE_LIMIT,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        self.storage_path = (
            Path(storage_path).expanduser()
            if storage_path is not None
            else user_data_dir() / "recent_profiles.json"
        )
        self.max_entries = int(max_entries)

    def entries(self) -> tuple[RecentProfileEntry, ...]:
        payload = self._read_payload()
        if payload is None:
            return ()
        raw_entries = payload.get("entries")
        if not isinstance(raw_entries, list):
            return ()
        result: list[RecentProfileEntry] = []
        seen: set[str] = set()
        for raw in raw_entries:
            try:
                entry = RecentProfileEntry.from_dict(raw)
            except (TypeError, ValueError):
                continue
            key = _path_key(entry.path)
            if key in seen:
                continue
            seen.add(key)
            result.append(entry)
            if len(result) >= self.max_entries:
                break
        return tuple(result)

    def record_recipe(self, path: str | Path, recipe: InspectionRecipe) -> None:
        normalized_path = _normalized_path(path)
        entry = RecentProfileEntry(
            path=str(normalized_path),
            profile_name=_optional_text(recipe.name),
        )
        key = _path_key(entry.path)
        current = [value for value in self.entries() if _path_key(value.path) != key]
        self._write_entries((entry, *current[: self.max_entries - 1]))

    def _read_payload(self) -> dict | None:
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            return None
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            LOGGER.warning("Recent profile history could not be read: %s", exc)
            return None
        if not isinstance(payload, dict):
            return None
        if payload.get("schema_version") != RECENT_PROFILE_HISTORY_SCHEMA_VERSION:
            return None
        return payload

    def _write_entries(self, entries: tuple[RecentProfileEntry, ...]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": RECENT_PROFILE_HISTORY_SCHEMA_VERSION,
            "entries": [entry.to_dict() for entry in entries],
        }
        temporary = self.storage_path.with_name(
            f".{self.storage_path.name}.{uuid4().hex}.tmp"
        )
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.storage_path)
        except Exception:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise


def _optional_text(value) -> str:
    return str(value or "").strip()


def _normalized_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.suffix.lower() != ".oilrecipe":
        path = path.with_suffix(".oilrecipe")
    return Path(os.path.abspath(os.path.normpath(os.fspath(path))))


def _path_key(value: str | Path) -> str:
    return os.path.normcase(os.path.normpath(os.path.expanduser(os.fspath(value))))
