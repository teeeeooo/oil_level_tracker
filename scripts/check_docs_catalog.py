#!/usr/bin/env python3
"""Check that the date catalog lists every Git-tracked file under docs/.

The rule is owned by docs/README.md ("날짜와 탐색"): a file created or moved
under docs/ enters docs/catalog-by-created-date.md in the same change. This
check reports tracked files the catalog does not link and catalog links whose
target is not tracked. It reads Git only and never edits the catalog.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "docs/catalog-by-created-date.md"
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def catalog_targets(catalog_text: str) -> set[str]:
    """Return the repository paths the catalog links, anchors removed."""

    targets: set[str] = set()
    for target in _LINK.findall(catalog_text):
        path = unquote(target.split("#", 1)[0])
        if not path or _SCHEME.match(path):
            continue
        targets.add(posixpath.normpath(posixpath.join(posixpath.dirname(CATALOG), path)))
    return targets


def catalog_findings(catalog_text: str, tracked: Iterable[str]) -> list[str]:
    tracked_paths = set(tracked)
    targets = catalog_targets(catalog_text)
    findings = [
        f"not in the catalog: {path}"
        for path in sorted(tracked_paths)
        if path.startswith("docs/") and path not in targets
    ]
    # A link to a folder is valid when the folder holds tracked files.
    directories: set[str] = set()
    for path in tracked_paths:
        parent = posixpath.dirname(path)
        while parent and parent not in directories:
            directories.add(parent)
            parent = posixpath.dirname(parent)
    findings.extend(
        f"catalog links an untracked path: {path}"
        for path in sorted(targets - tracked_paths - directories)
    )
    return findings


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", help="check this commit instead of the index and working catalog")
    args = parser.parse_args(argv)
    if args.ref:
        tracked = _git("ls-tree", "-r", "-z", "--name-only", args.ref).split("\0")
        catalog_text = _git("show", f"{args.ref}:{CATALOG}")
    else:
        tracked = _git("ls-files", "-z").split("\0")
        catalog_text = (ROOT / CATALOG).read_text(encoding="utf-8")
    findings = catalog_findings(catalog_text, [path for path in tracked if path])
    if findings:
        print("Docs catalog check FAILED (see docs/README.md, 날짜와 탐색):")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Docs catalog check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
