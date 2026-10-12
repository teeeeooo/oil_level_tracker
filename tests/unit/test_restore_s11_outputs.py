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


def test_additive_gzip_map_restores_removed_file_and_checks_both_hashes(preservation, tmp_path):
    repo, manifest, _, payload, data = preservation
    compressed = repo / "sample/output/kept.json.gz"
    compressed.write_bytes(gzip.compress(payload, mtime=0))
    mapping = dict(schema="s11-output-compression-v1",
                   base_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                   files=[dict(path="sample/output/kept.json", bytes=len(payload),
                               sha256=hashlib.sha256(payload).hexdigest(),
                               compressed=dict(path="sample/output/kept.json.gz", bytes=compressed.stat().st_size,
                                               sha256=hashlib.sha256(compressed.read_bytes()).hexdigest()))])
    overlay = manifest.with_name("compressed-files.json")
    overlay.write_text(json.dumps(mapping), encoding="utf-8")
    (repo / "sample/output/kept.json").unlink()
    dest = tmp_path / "restored"
    restore(manifest, dest, "sample/output/kept.json", repo=repo)
    assert (dest / "sample/output/kept.json").read_bytes() == payload
    compressed.write_bytes(compressed.read_bytes() + b"tampering")
    with pytest.raises(ValueError, match="Retained input changed"):
        restore(manifest, tmp_path / "bad", "sample/output/kept.json", repo=repo)
    assert not (tmp_path / "bad").exists()
    # Even a matching compressed hash must decode to the original pinned bytes.
    compressed.write_bytes(gzip.compress(b"different original", mtime=0))
    mapping["files"][0]["compressed"].update(bytes=compressed.stat().st_size,
                                            sha256=hashlib.sha256(compressed.read_bytes()).hexdigest())
    overlay.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(ValueError, match="Restored bytes mismatch"):
        restore(manifest, tmp_path / "bad-original", "sample/output/kept.json", repo=repo)
    assert not (tmp_path / "bad-original").exists()


def test_compression_overlay_cannot_change_pinned_original_or_manifest(preservation, tmp_path):
    repo, manifest, _, _, _ = preservation
    overlay = manifest.with_name("compressed-files.json")
    mapping = dict(schema="s11-output-compression-v1", base_manifest_sha256="wrong", files=[])
    overlay.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        restore(manifest, tmp_path / "bad", "sample/output/kept.json", repo=repo)
    mapping["base_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    mapping["files"] = [dict(path="sample/output/kept.json", bytes=0, sha256="wrong",
                            compressed=dict(path="sample/output/kept.json.gz"))]
    overlay.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid compressed-file mapping"):
        restore(manifest, tmp_path / "bad-original", "sample/output/kept.json", repo=repo)
    assert not (tmp_path / "bad-original").exists()


def test_additive_map_reuses_existing_archive_object_without_another_copy(preservation, tmp_path):
    repo, manifest, _, payload, data = preservation
    original_sha = hashlib.sha256(payload).hexdigest()
    mapping = dict(schema="s11-output-compression-v1",
                   base_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                   files=[dict(path="sample/output/kept.json", bytes=len(payload), sha256=original_sha,
                               compressed={**data["archive"], "format": "existing-zip",
                                           "member": "objects/" + original_sha})])
    overlay = manifest.with_name("compressed-files.json")
    overlay.write_text(json.dumps(mapping), encoding="utf-8")
    (repo / "sample/output/kept.json").unlink()
    restore(manifest, tmp_path / "restored", "sample/output/kept.json", repo=repo)
    assert (tmp_path / "restored/sample/output/kept.json").read_bytes() == payload
    mapping["files"][0]["compressed"]["member"] = "objects/wrong"
    overlay.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid existing ZIP mapping"):
        restore(manifest, tmp_path / "bad", "sample/output/kept.json", repo=repo)


def test_retirement_precedes_missing_archive_and_rejects_partial_restore(preservation, tmp_path):
    repo, manifest, archive, payload, data = preservation
    review = dict(schema="s11-output-retention-v1", default_disposition="retired",
                  base_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                  retained=[data["entries"][-1]])
    manifest.with_name("retention.json").write_text(json.dumps(review), encoding="utf-8")
    archive.unlink()  # Deliberate disposal, not an accidental missing archive.
    for prefix in ("sample/output/run/a.json", "sample/output"):
        destination = tmp_path / "must-not-exist"
        with pytest.raises(ValueError, match="Intentionally retired"):
            restore(manifest, destination, prefix, repo=repo)
        assert not destination.exists()
    destination = tmp_path / "retained"
    restore(manifest, destination, "sample/output/kept.json", repo=repo)
    assert (destination / "sample/output/kept.json").read_bytes() == payload


def test_retention_review_cannot_change_pins_or_select_unknown_paths(preservation, tmp_path):
    repo, manifest, _, _, data = preservation
    overlay = manifest.with_name("retention.json")
    review = dict(schema="s11-output-retention-v1", default_disposition="retired",
                  base_manifest_sha256="wrong", retained=[])
    overlay.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        restore(manifest, tmp_path / "bad", "sample/output/kept.json", repo=repo)
    review["base_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    for entry in ({**data["entries"][-1], "bytes": 0},
                  {**data["entries"][-1], "path": "sample/output/unknown.json"}):
        review["retained"] = [entry]
        overlay.write_text(json.dumps(review), encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid retained-file"):
            restore(manifest, tmp_path / "bad", "sample/output/kept.json", repo=repo)
    assert not (tmp_path / "bad").exists()
