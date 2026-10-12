from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from scripts.restore_s11_outputs import ROOT, restore


@pytest.fixture
def preservation(tmp_path):
    repo = tmp_path / "repo"
    output = repo / "sample/output"
    output.mkdir(parents=True)
    payload = b"frozen evidence\n"
    sha = hashlib.sha256(payload).hexdigest()
    archive = output / "preserved.zip"
    with zipfile.ZipFile(archive, "x") as bundle:
        bundle.writestr("objects/" + sha, payload)
    (output / "kept.json").write_bytes(payload)
    entries = [dict(path="sample/output/" + name, kind="file", bytes=len(payload),
                    mode=0o644, mtime_ns=1_700_000_000_000_000_000, sha256=sha,
                    disposition="archive", member="objects/" + sha)
               for name in ("run/a.json", "run/b.json", "unselected.json")]
    entries.append({**entries[0], "path": "sample/output/kept.json", "disposition": "retain"})
    data = dict(schema="s11-output-consolidation-v1", baseline_root=str(repo), entries=entries,
                archive=dict(path="sample/output/preserved.zip", sha256=hashlib.sha256(archive.read_bytes()).hexdigest()))
    manifest = tmp_path / "manifest.json.gz"
    manifest.write_bytes(gzip.compress(json.dumps(data).encode("utf-8")))
    return repo, manifest, archive, payload, data


def test_cli_outside_repo_restores_selected_duplicates_as_independent_files(preservation, tmp_path):
    repo, manifest, _, payload, _ = preservation
    dest = tmp_path / "restored"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/restore_s11_outputs.py"), "--repo", str(repo),
         "--manifest", str(manifest), "--prefix", "sample/output/run", "--destination", str(dest)],
        cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    assert json.loads(result.stdout)["files"] == 2
    a, b = dest / "sample/output/run/a.json", dest / "sample/output/run/b.json"
    assert a.read_bytes() == b.read_bytes() == payload
    a.write_bytes(b"edited independently")
    assert b.read_bytes() == payload
    assert not (dest / "sample/output/unselected.json").exists()


def test_existing_destination_and_corrupt_archive_leave_user_data_untouched(preservation, tmp_path):
    repo, manifest, archive, _, _ = preservation
    dest = tmp_path / "existing"
    dest.mkdir()
    (dest / "user.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        restore(manifest, dest, "sample/output/run", repo=repo)
    assert (dest / "user.txt").read_text(encoding="utf-8") == "keep"
    archive.write_bytes(archive.read_bytes() + b"unexpected change")
    fresh = tmp_path / "fresh"
    with pytest.raises(ValueError, match="SHA-256"):
        restore(manifest, fresh, "sample/output/run", repo=repo)
    assert not fresh.exists()


def test_changed_retained_file_and_unsafe_paths_fail_before_writing(preservation, tmp_path):
    repo, manifest, _, _, data = preservation
    (repo / "sample/output/kept.json").write_bytes(b"new evidence")
    dest = tmp_path / "fresh"
    with pytest.raises(ValueError, match="Retained input changed"):
        restore(manifest, dest, "sample/output/kept.json", repo=repo)
    data["entries"][0]["path"] = "sample/output/../../../escape"
    manifest.write_bytes(gzip.compress(json.dumps(data).encode("utf-8")))
    with pytest.raises(ValueError, match="Invalid output path"):
        restore(manifest, dest, "sample/output", repo=repo)
    assert not dest.exists()


def test_links_need_opt_in_and_cannot_target_outside_sample_tree(preservation, tmp_path):
    repo, manifest, _, _, data = preservation
    data["entries"].append(dict(path="sample/output/run/link", kind="symlink", target="/outside/secret"))
    manifest.write_bytes(gzip.compress(json.dumps(data).encode("utf-8")))
    dest = tmp_path / "fresh"
    with pytest.raises(ValueError, match="include-symlinks"):
        restore(manifest, dest, "sample/output/run", repo=repo)
    with pytest.raises(ValueError, match="outside"):
        restore(manifest, dest, "sample/output/run", repo=repo, include_symlinks=True)
    assert not dest.exists()


def test_bad_logical_mapping_rolls_back_partial_restore(preservation, tmp_path):
    repo, manifest, _, _, data = preservation
    data["entries"][1]["bytes"] += 1
    manifest.write_bytes(gzip.compress(json.dumps(data).encode("utf-8")))
    dest = tmp_path / "fresh"
    with pytest.raises(ValueError, match="Restored bytes mismatch"):
        restore(manifest, dest, "sample/output/run", repo=repo)
    assert not dest.exists()
