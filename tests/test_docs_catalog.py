from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("docs_catalog", ROOT / "scripts" / "check_docs_catalog.py")
assert SPEC and SPEC.loader
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)

CATALOG = """
- [문서 역할](README.md#document-maintenance-lifecycle) · [현재 작업](00-project/work-plan.md)
- [checker](../scripts/check_docs_catalog.py) · [external](https://example.com/a.md) · [here](#날짜-근거)

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-22 (`abc1234`) | [review](50-diagnostics/s11/review.md) | 검토 |
| 2026-10-22 | [S11 diagnostics](50-diagnostics/s11/) | 폴더 |
"""
TRACKED = [
    "docs/README.md",
    "docs/00-project/work-plan.md",
    "docs/50-diagnostics/s11/review.md",
    "scripts/check_docs_catalog.py",
    "src/oil_tracker/module.py",
]


def test_complete_catalog_passes_with_anchors_external_and_folder_links() -> None:
    assert catalog.catalog_findings(CATALOG, TRACKED) == []


def test_tracked_docs_file_missing_from_the_catalog_fails() -> None:
    findings = catalog.catalog_findings(CATALOG, [*TRACKED, "docs/50-diagnostics/s11/review/summary.json"])
    assert findings == ["not in the catalog: docs/50-diagnostics/s11/review/summary.json"]


def test_files_outside_docs_need_no_catalog_row() -> None:
    assert catalog.catalog_findings(CATALOG, [*TRACKED, "tests/test_new.py"]) == []


def test_catalog_link_to_an_untracked_file_fails() -> None:
    untracked = [path for path in TRACKED if path != "docs/00-project/work-plan.md"]
    assert catalog.catalog_findings(CATALOG, untracked) == [
        "catalog links an untracked path: docs/00-project/work-plan.md"
    ]


def test_moved_file_needs_its_new_path_in_the_catalog() -> None:
    moved = [*TRACKED[:2], "docs/90-archive/50-diagnostics/2026/review.md", *TRACKED[3:]]
    assert catalog.catalog_findings(CATALOG, moved) == [
        "not in the catalog: docs/90-archive/50-diagnostics/2026/review.md",
        "catalog links an untracked path: docs/50-diagnostics/s11",
        "catalog links an untracked path: docs/50-diagnostics/s11/review.md",
    ]
