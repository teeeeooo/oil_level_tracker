from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path, PureWindowsPath
from uuid import uuid4

from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
from oil_tracker.adapters.system.app_paths import user_data_dir
from oil_tracker.domain.review import ReviewBundle


LOGGER = logging.getLogger(__name__)
RECENT_RESULT_HISTORY_SCHEMA_VERSION = 1
DEFAULT_RECENT_RESULT_LIMIT = 8


@dataclass(frozen=True)
class RecentResultEntry:
    path: str
    run_name: str = ""
    profile_name: str = ""
    source_video_name: str = ""

    def is_available(self) -> bool:
        return Path(self.path).expanduser().is_dir()

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "run_name": self.run_name,
            "profile_name": self.profile_name,
            "source_video_name": self.source_video_name,
        }

    @classmethod
    def from_dict(cls, payload) -> "RecentResultEntry":
        if not isinstance(payload, dict):
            raise ValueError("recent result entry must be an object")
        path = payload.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("recent result path is missing")
        return cls(
            path=path,
            run_name=_optional_text(payload.get("run_name")),
            profile_name=_optional_text(payload.get("profile_name")),
            source_video_name=_optional_text(payload.get("source_video_name")),
        )


class RecentResultHistory:
    """Persist bounded recent-result metadata outside immutable result bundles."""

    def __init__(
        self,
        storage_path: str | Path | None = None,
        *,
        max_entries: int = DEFAULT_RECENT_RESULT_LIMIT,
        bundle_reader: ResultBundleReader | None = None,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        self.storage_path = (
            Path(storage_path).expanduser()
            if storage_path is not None
            else user_data_dir() / "recent_results.json"
        )
        self.max_entries = int(max_entries)
        self.bundle_reader = bundle_reader or ResultBundleReader()

    def entries(self) -> tuple[RecentResultEntry, ...]:
        payload = self._read_payload()
        if payload is None:
            return ()
        raw_entries = payload.get("entries")
        if not isinstance(raw_entries, list):
            return ()
        result: list[RecentResultEntry] = []
        seen: set[str] = set()
        for raw in raw_entries:
            try:
                entry = RecentResultEntry.from_dict(raw)
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

    def register_path(self, path: str | Path) -> ReviewBundle:
        bundle = self.bundle_reader.read(path)
        self.record_bundle(bundle)
        return bundle

    def record_bundle(self, bundle: ReviewBundle) -> None:
        entry = RecentResultEntry(
            path=str(bundle.root),
            run_name=_optional_text(bundle.run_name),
            profile_name=_optional_text(bundle.recipe.name),
            source_video_name=_basename(bundle.source_video_path),
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
            LOGGER.warning("Recent result history could not be read: %s", exc)
            return None
        if not isinstance(payload, dict):
            return None
        if payload.get("schema_version") != RECENT_RESULT_HISTORY_SCHEMA_VERSION:
            return None
        return payload

    def _write_entries(self, entries: tuple[RecentResultEntry, ...]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": RECENT_RESULT_HISTORY_SCHEMA_VERSION,
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


def _path_key(value: str | Path) -> str:
    text = os.fspath(value)
    return os.path.normcase(os.path.normpath(os.path.expanduser(text)))


def _basename(value: str | Path) -> str:
    text = _optional_text(value)
    if not text:
        return ""
    if "\\" in text:
        return PureWindowsPath(text).name
    return Path(text).name
