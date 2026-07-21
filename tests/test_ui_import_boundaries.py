from __future__ import annotations

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "src" / "oil_tracker" / "ui"
ALLOWED_EXISTING_UI_IMAGE_IMPORTS = {
    "src/oil_tracker/ui/widgets/result_review_canvas.py",
}
_FORBIDDEN_IMPORT_ROOTS = {"cv2", "numpy"}


def _forbidden_imports(source: str) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found.update(
                alias.name.split(".", 1)[0]
                for alias in node.names
                if alias.name.split(".", 1)[0] in _FORBIDDEN_IMPORT_ROOTS
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".", 1)[0]
            if root in _FORBIDDEN_IMPORT_ROOTS:
                found.add(root)
    return found


def _ui_import_violations() -> dict[str, set[str]]:
    violations = {}
    for path in sorted(UI_ROOT.rglob("*.py")):
        relative = path.relative_to(ROOT).as_posix()
        forbidden = _forbidden_imports(path.read_text(encoding="utf-8"))
        if forbidden and relative not in ALLOWED_EXISTING_UI_IMAGE_IMPORTS:
            violations[relative] = forbidden
    return violations


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("import numpy as np\n", {"numpy"}),
        ("from numpy import ndarray\n", {"numpy"}),
        ("import cv2\n", {"cv2"}),
        ("from cv2.typing import MatLike\n", {"cv2"}),
        ("import math\nfrom pathlib import Path\n", set()),
    ],
)
def test_ast_import_guard_detects_forbidden_ui_dependencies(source, expected):
    assert _forbidden_imports(source) == expected


def test_ui_does_not_add_new_cv2_or_numpy_imports_beyond_temporary_debt():
    assert _ui_import_violations() == {}


def test_legacy_result_review_canvas_is_the_only_temporary_allowlisted_violation():
    assert ALLOWED_EXISTING_UI_IMAGE_IMPORTS == {
        "src/oil_tracker/ui/widgets/result_review_canvas.py",
    }
    legacy = ROOT / next(iter(ALLOWED_EXISTING_UI_IMAGE_IMPORTS))
    assert _forbidden_imports(legacy.read_text(encoding="utf-8")) == {"cv2", "numpy"}


def test_truth_annotation_ui_files_have_no_numpy_or_cv2_imports():
    paths = (
        UI_ROOT / "widgets" / "truth_annotation_canvas.py",
        UI_ROOT / "truth_annotation_window.py",
        UI_ROOT / "truth_annotation_coordinator.py",
    )
    assert {path.name: _forbidden_imports(path.read_text(encoding="utf-8")) for path in paths} == {
        "truth_annotation_canvas.py": set(),
        "truth_annotation_window.py": set(),
        "truth_annotation_coordinator.py": set(),
    }


def test_presentation_adapter_numpy_import_is_outside_ui_boundary():
    adapter = (
        ROOT
        / "src"
        / "oil_tracker"
        / "adapters"
        / "presentation"
        / "qt_frame_image_converter.py"
    )
    assert _forbidden_imports(adapter.read_text(encoding="utf-8")) == {"numpy"}
    assert UI_ROOT not in adapter.parents
