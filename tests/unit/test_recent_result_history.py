from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from oil_tracker.adapters.storage.recent_result_history import RecentResultHistory


class _Reader:
    def __init__(self, bundle=None):
        self.bundle = bundle
        self.paths = []

    def read(self, path):
        self.paths.append(Path(path))
        return self.bundle


def _bundle(root: Path, *, run_name="시험 01", profile_name="Profile A", source="sample.mp4"):
    root.mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(
        root=root,
        run_name=run_name,
        recipe=SimpleNamespace(name=profile_name),
        source_video_path=source,
    )


def test_first_run_and_persistence_round_trip(tmp_path):
    storage = tmp_path / "user-data" / "recent_results.json"
    history = RecentResultHistory(storage, bundle_reader=_Reader())
    assert history.entries() == ()
    bundle = _bundle(tmp_path / "result-a")
    history.record_bundle(bundle)

    reloaded = RecentResultHistory(storage, bundle_reader=_Reader())
    assert [entry.path for entry in reloaded.entries()] == [str(bundle.root)]
    assert reloaded.entries()[0].run_name == "시험 01"
    assert reloaded.entries()[0].profile_name == "Profile A"
    assert reloaded.entries()[0].source_video_name == "sample.mp4"


def test_history_is_bounded_newest_first_and_duplicate_moves_to_front(tmp_path):
    storage = tmp_path / "recent.json"
    history = RecentResultHistory(storage, max_entries=3, bundle_reader=_Reader())
    a = _bundle(tmp_path / "a", run_name="A")
    b = _bundle(tmp_path / "b", run_name="B")
    c = _bundle(tmp_path / "c", run_name="C")
    d = _bundle(tmp_path / "d", run_name="D")

    history.record_bundle(a)
    history.record_bundle(b)
    history.record_bundle(c)
    a.run_name = "A updated"
    history.record_bundle(a)
    assert [(entry.run_name, Path(entry.path).name) for entry in history.entries()] == [
        ("A updated", "a"),
        ("C", "c"),
        ("B", "b"),
    ]

    history.record_bundle(d)
    assert [entry.run_name for entry in history.entries()] == ["D", "A updated", "C"]


def test_unicode_paths_and_windows_source_name_are_preserved(tmp_path):
    storage = tmp_path / "사용자 데이터" / "recent_results.json"
    bundle = _bundle(
        tmp_path / "결과 번들 03",
        run_name="반복 시험 03",
        profile_name="회수 시험 프로필",
        source=r"C:\시험 영상\기동 03.mp4",
    )
    history = RecentResultHistory(storage, bundle_reader=_Reader())
    history.record_bundle(bundle)

    entry = history.entries()[0]
    assert entry.path == str(bundle.root)
    assert entry.run_name == "반복 시험 03"
    assert entry.profile_name == "회수 시험 프로필"
    assert entry.source_video_name == "기동 03.mp4"
    assert "반복 시험 03" in storage.read_text(encoding="utf-8")


def test_stale_entry_remains_readable_without_touching_bundle(tmp_path):
    storage = tmp_path / "recent.json"
    bundle = _bundle(tmp_path / "result-stale")
    marker = bundle.root / "immutable.txt"
    marker.write_text("official", encoding="utf-8")
    before = marker.read_bytes()

    history = RecentResultHistory(storage, bundle_reader=_Reader())
    history.record_bundle(bundle)
    assert marker.read_bytes() == before
    assert sorted(path.name for path in bundle.root.iterdir()) == ["immutable.txt"]

    marker.unlink()
    bundle.root.rmdir()
    entry = history.entries()[0]
    assert entry.path.endswith("result-stale")
    assert entry.is_available() is False


def test_corrupt_history_fails_safe_and_can_be_rebuilt(tmp_path):
    storage = tmp_path / "recent.json"
    storage.write_text("{not-json", encoding="utf-8")
    history = RecentResultHistory(storage, bundle_reader=_Reader())
    assert history.entries() == ()

    bundle = _bundle(tmp_path / "recovered", run_name="복구됨")
    history.record_bundle(bundle)
    payload = json.loads(storage.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["entries"][0]["run_name"] == "복구됨"


def test_register_path_uses_authoritative_bundle_reader(tmp_path):
    bundle = _bundle(tmp_path / "bundle", run_name="authoritative")
    reader = _Reader(bundle)
    history = RecentResultHistory(tmp_path / "recent.json", bundle_reader=reader)

    returned = history.register_path(bundle.root)

    assert returned is bundle
    assert reader.paths == [bundle.root]
    assert history.entries()[0].run_name == "authoritative"


def test_failed_atomic_replace_preserves_previous_valid_history(tmp_path, monkeypatch):
    storage = tmp_path / "recent.json"
    history = RecentResultHistory(storage, bundle_reader=_Reader())
    history.record_bundle(_bundle(tmp_path / "first", run_name="first"))
    previous = storage.read_bytes()

    def fail_replace(_source, _destination):
        raise OSError("replace failed")

    monkeypatch.setattr(
        "oil_tracker.adapters.storage.recent_result_history.os.replace",
        fail_replace,
    )
    with pytest.raises(OSError, match="replace failed"):
        history.record_bundle(_bundle(tmp_path / "second", run_name="second"))

    assert storage.read_bytes() == previous
