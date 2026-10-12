"""Restore selected preserved S11 outputs into a new directory, without decoding video."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs/60-evidence/s11/2026-10-12-pre-cr1-cleanup/consolidation.json.gz"


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def output_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.parts[:2] != ("sample", "output")
        or ".." in path.parts
        or "\\" in value
        or ":" in value
        or path.as_posix() != value.rstrip("/")
    ):
        raise ValueError(f"Invalid output path: {value}")
    return path


def compressed_sources(manifest_path: Path, manifest: dict) -> dict:
    """Read an additive compressed storage map without rewriting historical pins."""
    mapping = manifest_path.with_name("compressed-files.json")
    if not mapping.exists():
        return {}
    data = json.loads(mapping.read_text(encoding="utf-8"))
    if data["schema"] != "s11-output-compression-v1" or data["base_manifest_sha256"] != digest(manifest_path):
        raise ValueError("Compressed-file map does not match preservation manifest")
    entries = {entry["path"]: entry for entry in manifest["entries"]}
    sources = {}
    for item in data["files"]:
        path = item["path"]
        output_path(path)
        output_path(item["compressed"]["path"])
        entry = entries.get(path)
        if (path in sources or not entry or entry["kind"] != "file"
                or entry["disposition"] != "retain"
                or any(item[k] != entry[k] for k in ("bytes", "sha256"))):
            raise ValueError("Invalid compressed-file mapping")
        storage = item["compressed"]
        if storage.get("format", "gzip") == "existing-zip":
            if (storage["path"] != manifest["archive"]["path"]
                    or storage["sha256"] != manifest["archive"]["sha256"]
                    or storage["member"] != "objects/" + entry["sha256"]):
                raise ValueError("Invalid existing ZIP mapping")
        elif storage.get("format", "gzip") != "gzip":
            raise ValueError("Unsupported compressed storage format")
        sources[path] = item["compressed"]
    return sources


def restore(
    manifest_path: Path,
    destination: Path,
    prefix: str,
    *,
    repo: Path = ROOT,
    include_symlinks: bool = False,
) -> dict[str, int]:
    """Copy original bytes and modes; never overwrite an existing destination.

    Kept files come from their pinned repository paths or an additive gzip map;
    archived files come from a self-contained ZIP object store. Each logical path
    gets an independent file.
    Historical absolute links require opt-in and are rebound inside this repo.
    """
    prefix_path = output_path(prefix)
    manifest = json.loads(gzip.decompress(manifest_path.read_bytes()))
    if manifest["schema"] != "s11-output-consolidation-v1":
        raise ValueError("Unsupported preservation manifest")
    compressed = compressed_sources(manifest_path, manifest)
    for entry in manifest["entries"]:
        storage = compressed.get(entry["path"], {})
        if storage.get("format") == "existing-zip":
            entry.update(disposition="archive", member=storage["member"])
    selected = [
        entry for entry in manifest["entries"]
        if output_path(entry["path"]).is_relative_to(prefix_path)
    ]
    if not selected:
        raise ValueError(f"No preserved paths match {prefix}")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination must not exist: {destination}")
    paths = [entry["path"] for entry in selected]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate logical paths in manifest")
    links = [entry for entry in selected if entry["kind"] == "symlink"]
    if links and not include_symlinks:
        raise ValueError("Selection includes historical links; use --include-symlinks explicitly")
    link_targets = {}
    for entry in links:
        target = PurePosixPath(entry["target"])
        baseline = PurePosixPath(manifest["baseline_root"])
        if ".." in target.parts or not target.is_relative_to(baseline / "sample"):
            raise ValueError("Historical link target is outside the repository sample tree")
        link_targets[entry["path"]] = repo / target.relative_to(baseline)
        if any(output_path(p) != output_path(entry["path"])
               and output_path(p).is_relative_to(output_path(entry["path"])) for p in paths):
            raise ValueError("A restored path would traverse a symlink")
    archive = repo / output_path(manifest["archive"]["path"])
    needs_archive = any(e["kind"] == "file" and e["disposition"] == "archive" for e in selected)
    if needs_archive and digest(archive) != manifest["archive"]["sha256"]:
        raise ValueError("Archive SHA-256 mismatch")
    for entry in selected:
        if entry["kind"] not in {"file", "symlink"}:
            raise ValueError("Unsupported entry kind")
        if entry["kind"] == "file" and entry["disposition"] == "retain":
            storage = compressed.get(entry["path"])
            source = repo / output_path(storage["path"] if storage else entry["path"])
            expected_sha = storage["sha256"] if storage else entry["sha256"]
            if source.is_symlink() or digest(source) != expected_sha:
                raise ValueError(f"Retained input changed: {entry['path']}")
            if storage and source.stat().st_size != storage["bytes"]:
                raise ValueError("Compressed file size mismatch")
    created: list[Path] = []
    destination.mkdir()  # Exclusive creation; ancestors must already exist.
    try:
        with ExitStack() as stack:
            bundle = stack.enter_context(zipfile.ZipFile(archive)) if needs_archive else None
            for entry in selected:
                if entry["kind"] == "symlink":
                    continue
                target = destination / output_path(entry["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                if entry["disposition"] == "archive":
                    expected_member = "objects/" + entry["sha256"]
                    if entry["member"] != expected_member:
                        raise ValueError("Invalid archive object mapping")
                    source = bundle.open(expected_member)
                elif entry["disposition"] == "retain":
                    storage = compressed.get(entry["path"])
                    if storage:
                        source = gzip.open(repo / output_path(storage["path"]), "rb")
                    else:
                        source = (repo / output_path(entry["path"])).open("rb")
                else:
                    raise ValueError("Unsupported disposition")
                with source, target.open("xb") as handle:
                    created.append(target)
                    shutil.copyfileobj(source, handle)
                if target.stat().st_size != entry["bytes"] or digest(target) != entry["sha256"]:
                    raise ValueError(f"Restored bytes mismatch: {entry['path']}")
                target.chmod(entry["mode"] & 0o777)
                os.utime(target, ns=(entry["mtime_ns"], entry["mtime_ns"]))
            for entry in links:
                target = destination / output_path(entry["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                source_target = link_targets[entry["path"]]
                target.symlink_to(source_target, target_is_directory=source_target.is_dir())
                created.append(target)
    except BaseException:
        for target in reversed(created):
            target.unlink(missing_ok=True)
        for base, directories, _ in os.walk(destination, topdown=False, followlinks=False):
            for name in directories:
                try:
                    (Path(base) / name).rmdir()
                except OSError:
                    pass
        try:
            destination.rmdir()
        except OSError:
            pass
        raise
    return {"files": len(selected) - len(links), "symlinks": len(links)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--prefix", required=True, help="Original repository-relative file or run directory")
    parser.add_argument("--destination", type=Path, required=True, help="New directory under an existing parent")
    parser.add_argument("--include-symlinks", action="store_true")
    args = parser.parse_args()
    result = restore(args.manifest, args.destination, args.prefix, repo=args.repo,
                     include_symlinks=args.include_symlinks)
    print(json.dumps({"destination": str(args.destination.resolve()), **result}))


if __name__ == "__main__":
    main()
