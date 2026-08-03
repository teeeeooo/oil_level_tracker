from __future__ import annotations

import json
from pathlib import Path

import pytest

from oil_tracker.adapters.storage.recent_profile_history import RecentProfileHistory
from oil_tracker.domain.recipe import InspectionRecipe


def _recipe(name: str) -> InspectionRecipe:
    return InspectionRecipe.empty(640, 480, name)


def test_first_run_and_persistence_round_trip(tmp_path):
    storage = tmp_path / "user-data" / "recent_profiles.json"
    history = RecentProfileHistory(storage)
    assert history.entries() == ()

    profile = tmp_path / "profile-a.oilrecipe"
    profile.write_text("immutable", encoding="utf-8")
    history.record_recipe(profile, _recipe("Profile A"))

    reloaded = RecentProfileHistory(storage)
    assert [(Path(entry.path), entry.profile_name) for entry in reloaded.entries()] == [
        (profile, "Profile A")
    ]


def test_newest_first_bound_and_duplicate_path_promotion(tmp_path):
    history = RecentProfileHistory(tmp_path / "recent.json", max_entries=3)
    profiles = []
    for name in ("A", "B", "C", "D"):
        path = tmp_path / f"{name}.oilrecipe"
        path.write_text(name, encoding="utf-8")
        profiles.append(path)

    for name, path in zip(("A", "B", "C"), profiles[:3]):
        history.record_recipe(path, _recipe(name))
    history.record_recipe(profiles[0], _recipe("A updated"))
    assert [(Path(entry.path).stem, entry.profile_name) for entry in history.entries()] == [
        ("A", "A updated"),
        ("C", "C"),
        ("B", "B"),
    ]

    history.record_recipe(profiles[3], _recipe("D"))
    assert [Path(entry.path).stem for entry in history.entries()] == ["D", "A", "C"]


def test_unicode_and_extension_normalization_use_actual_oilrecipe_path(tmp_path):
    history = RecentProfileHistory(tmp_path / "사용자 데이터" / "recent_profiles.json")
    requested = tmp_path / "반복 시험 프로필"
    actual = requested.with_suffix(".oilrecipe")
    actual.write_text("profile", encoding="utf-8")
    history.record_recipe(requested, _recipe("회수 시험 프로필"))

    entry = history.entries()[0]
    assert Path(entry.path) == actual
    assert entry.profile_name == "회수 시험 프로필"
    assert "회수 시험 프로필" in history.storage_path.read_text(encoding="utf-8")


def test_stale_entry_isolated_and_history_does_not_mutate_profile(tmp_path):
    storage = tmp_path / "recent.json"
    profile = tmp_path / "stale.oilrecipe"
    profile.write_bytes(b"profile truth")
    before = profile.read_bytes()

    history = RecentProfileHistory(storage)
    history.record_recipe(profile, _recipe("Stale"))
    assert profile.read_bytes() == before

    profile.unlink()
    entry = history.entries()[0]
    assert entry.profile_name == "Stale"
    assert entry.is_available() is False


def test_malformed_unreadable_and_invalid_entries_fail_safe(tmp_path, monkeypatch):
    storage = tmp_path / "recent.json"
    storage.write_text("{not-json", encoding="utf-8")
    history = RecentProfileHistory(storage)
    assert history.entries() == ()
    original_read_text = Path.read_text

    def fail_read_text(path, *args, **kwargs):
        if path == storage:
            raise OSError("unreadable")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_read_text)
    assert history.entries() == ()


def test_invalid_and_duplicate_persisted_entries_are_skipped_deterministically(tmp_path):
    storage = tmp_path / "recent.json"
    valid = tmp_path / "valid.oilrecipe"
    payload = {
        "schema_version": 1,
        "entries": [
            {"path": ""},
            {"path": str(valid), "profile_name": "first"},
            {"path": str(valid), "profile_name": "duplicate"},
            "not-an-object",
        ],
    }
    storage.write_text(json.dumps(payload), encoding="utf-8")

    entries = RecentProfileHistory(storage).entries()
    assert len(entries) == 1
    assert entries[0].path == str(valid)
    assert entries[0].profile_name == "first"


def test_failed_atomic_replace_preserves_previous_valid_history(tmp_path, monkeypatch):
    storage = tmp_path / "recent.json"
    history = RecentProfileHistory(storage)
    first = tmp_path / "first.oilrecipe"
    second = tmp_path / "second.oilrecipe"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")
    history.record_recipe(first, _recipe("first"))
    previous = storage.read_bytes()

    def fail_replace(_source, _destination):
        raise OSError("replace failed")

    monkeypatch.setattr(
        "oil_tracker.adapters.storage.recent_profile_history.os.replace",
        fail_replace,
    )
    with pytest.raises(OSError, match="replace failed"):
        history.record_recipe(second, _recipe("second"))

    assert storage.read_bytes() == previous
    assert not list(storage.parent.glob(".recent.json.*.tmp"))


def test_recent_profile_state_is_separate_from_recent_result_and_run_identity(tmp_path):
    history = RecentProfileHistory(tmp_path / "recent_profiles.json")
    profile = tmp_path / "profile.oilrecipe"
    profile.write_text("truth", encoding="utf-8")
    recipe = _recipe("Profile Truth")
    history.record_recipe(profile, recipe)

    payload = json.loads(history.storage_path.read_text(encoding="utf-8"))
    assert history.storage_path.name == "recent_profiles.json"
    assert set(payload["entries"][0]) == {"path", "profile_name"}
    assert "run_name" not in payload["entries"][0]
    assert "source_video" not in payload["entries"][0]
