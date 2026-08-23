from __future__ import annotations

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "src" / "oil_tracker" / "ui"
APPLICATION_ROOT = ROOT / "src" / "oil_tracker" / "application"
DOMAIN_ROOT = ROOT / "src" / "oil_tracker" / "domain"
_FORBIDDEN_IMPORT_ROOTS = {"cv2", "numpy"}
_INNER_FORBIDDEN_IMPORTS = (
    "oil_tracker.adapters",
    "oil_tracker.bootstrap",
    "oil_tracker.cli",
    "oil_tracker.ui",
    "oil_tracker.visualization",
    "PySide6",
    "cv2",
    "jinja2",
    "matplotlib",
    "numpy",
)
_CONCRETE_VIDEO_READER_MODULE = "oil_tracker.adapters.vision.opencv_video_reader"
_BUSINESS_ADAPTER_ROOTS = (
    "oil_tracker.adapters.storage",
    "oil_tracker.adapters.vision",
)


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
        if forbidden:
            violations[relative] = forbidden
    return violations


def _imported_modules(source: str) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _dependency_violations(root: Path, forbidden: tuple[str, ...]) -> dict[str, set[str]]:
    violations = {}
    for path in sorted(root.rglob("*.py")):
        imported = _imported_modules(path.read_text(encoding="utf-8"))
        found = {
            module
            for module in imported
            if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden)
        }
        if found:
            violations[path.relative_to(ROOT).as_posix()] = found
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


def test_entire_ui_tree_has_no_cv2_or_numpy_imports():
    assert _ui_import_violations() == {}


def test_domain_and_application_do_not_depend_on_outer_layers_or_raster_frameworks():
    assert _dependency_violations(
        DOMAIN_ROOT,
        (*_INNER_FORBIDDEN_IMPORTS, "oil_tracker.application"),
    ) == {}
    assert _dependency_violations(APPLICATION_ROOT, _INNER_FORBIDDEN_IMPORTS) == {}


def test_ui_does_not_import_the_concrete_opencv_video_reader():
    violations = _dependency_violations(UI_ROOT, (_CONCRETE_VIDEO_READER_MODULE,))
    assert violations == {}


def test_ui_depends_on_application_ports_not_storage_or_vision_business_adapters():
    assert _dependency_violations(UI_ROOT, _BUSINESS_ADAPTER_ROOTS) == {}


def test_ui_does_not_construct_business_io_or_detector_proposal_adapters():
    forbidden = (
        "BundleAssetResolver(",
        "DebugCaseExporter(",
        "DebugTraceRepository(",
        "JsonTruthRepository(",
        "RecentResultHistory(",
        "RegressionFixtureExporter(",
        "ResultBundleReader(",
        "SourceVideoResolver(",
        "OpenCvArtifactProposalService(",
    )
    violations = {
        path.relative_to(ROOT).as_posix(): tuple(
            value
            for value in forbidden
            if value in path.read_text(encoding="utf-8")
        )
        for path in sorted(UI_ROOT.rglob("*.py"))
    }
    assert {path: values for path, values in violations.items() if values} == {}


def test_ui_video_acquisition_owners_depend_on_the_application_reader_port():
    owners = (
        UI_ROOT / "controllers" / "workbench_controller.py",
        UI_ROOT / "widgets" / "video_preview_widget.py",
        UI_ROOT / "wizard" / "new_recipe_wizard.py",
    )
    assert {
        path.relative_to(ROOT).as_posix(): "oil_tracker.application.ports.video_reader"
        in _imported_modules(path.read_text(encoding="utf-8"))
        for path in owners
    } == {path.relative_to(ROOT).as_posix(): True for path in owners}


def test_ui_raster_import_guard_has_no_exception_collection():
    module = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    assigned_names = {
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert not {name for name in assigned_names if "ALLOW" in name.upper()}


def test_result_review_canvas_has_only_qt_display_responsibility():
    path = UI_ROOT / "widgets" / "result_review_canvas.py"
    source = path.read_text(encoding="utf-8")
    forbidden_fragments = (
        "ReviewOverlayRenderer",
        "ReviewDebugOverlayRenderer",
        "QtFrameImageConverter",
        "imencode",
        "tofile",
        "write_bytes",
        "mkdir",
        "os.replace",
        "set_review_frame",
        "set_debug_frame",
        "save_png",
        "rendered_image",
        "[:, :, ::-1]",
        "cv2.",
        "np.",
    )
    assert {value for value in forbidden_fragments if value in source} == set()
    assert "def set_image(" in source
    assert "QImage(image).copy()" in source


def test_result_review_ui_does_not_construct_raster_adapters():
    paths = (
        UI_ROOT / "result_review_window.py",
        UI_ROOT / "truth_annotation_coordinator.py",
        UI_ROOT / "widgets" / "result_debug_panel.py",
        UI_ROOT / "widgets" / "result_review_canvas.py",
    )
    forbidden = (
        "ReviewOverlayRenderer(",
        "ReviewDebugOverlayRenderer(",
        "QtFrameImageConverter(",
        "ReviewPngExporter(",
        "ReviewMp4Exporter(",
    )
    violations = {
        path.relative_to(ROOT).as_posix(): [value for value in forbidden if value in path.read_text(encoding="utf-8")]
        for path in paths
    }
    assert violations == {path.relative_to(ROOT).as_posix(): [] for path in paths}


def test_raster_adapters_are_outside_ui_and_domain_application_boundaries():
    adapter_paths = (
        ROOT / "src" / "oil_tracker" / "adapters" / "vision" / "review_overlay_renderer.py",
        ROOT / "src" / "oil_tracker" / "adapters" / "vision" / "review_debug_overlay_renderer.py",
        ROOT / "src" / "oil_tracker" / "adapters" / "presentation" / "review_frame_presenter.py",
        ROOT / "src" / "oil_tracker" / "adapters" / "storage" / "review_png_exporter.py",
        ROOT / "src" / "oil_tracker" / "adapters" / "storage" / "review_mp4_exporter.py",
    )
    assert all(path.is_file() and UI_ROOT not in path.parents for path in adapter_paths)
    for path in (
        ROOT / "src" / "oil_tracker" / "domain" / "review.py",
        ROOT / "src" / "oil_tracker" / "application" / "services" / "review_query.py",
    ):
        source = path.read_text(encoding="utf-8")
        assert _forbidden_imports(source) == set()
        assert "PySide6" not in source
