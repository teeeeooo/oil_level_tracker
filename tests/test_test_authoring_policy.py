from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = ROOT / "tests"
_QT_FIXTURES = {"qapp", "qtbot"}


def _test_paths() -> tuple[Path, ...]:
    return tuple(sorted(TESTS_ROOT.rglob("test_*.py")))


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _fixtures(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    args = function.args
    return {
        value.arg
        for value in (*args.posonlyargs, *args.args, *args.kwonlyargs)
    }


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def test_repository_test_text_io_declares_encoding():
    violations: list[str] = []
    for path in _test_paths():
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {"read_text", "write_text"}:
                continue
            if not any(keyword.arg == "encoding" for keyword in node.keywords):
                violations.append(f"{_relative(path)}:{node.lineno}:{node.func.attr}")
    assert violations == []


def test_noninteractive_subprocess_runs_define_stdin_and_text_encoding():
    violations: list[str] = []
    for path in _test_paths():
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if not (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr == "run"
            ):
                continue
            keywords = {keyword.arg for keyword in node.keywords if keyword.arg}
            if "stdin" not in keywords:
                violations.append(f"{_relative(path)}:{node.lineno}:stdin")
            if keywords.intersection({"text", "universal_newlines"}) and "encoding" not in keywords:
                violations.append(f"{_relative(path)}:{node.lineno}:encoding")
    assert violations == []


def _import_aliases(tree: ast.Module, module: str, symbol: str) -> set[str]:
    aliases: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.module != module:
            continue
        for imported in node.names:
            if imported.name == symbol:
                aliases.add(imported.asname or imported.name)
    return aliases


def test_direct_qt_event_loop_owners_request_repository_lifecycle():
    violations: list[str] = []
    for path in _test_paths():
        tree = _tree(path)
        timer_aliases = _import_aliases(tree, "PySide6.QtCore", "QTimer")
        review_aliases = _import_aliases(
            tree,
            "oil_tracker.ui.controllers.result_review_controller",
            "ResultReviewController",
        )
        for function in tree.body:
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not function.name.startswith("test_"):
                continue
            direct_timer = any(
                isinstance(node, ast.Name) and node.id in timer_aliases
                for node in ast.walk(function)
            )
            direct_review = any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in review_aliases
                for node in ast.walk(function)
            )
            if (direct_timer or direct_review) and not _fixtures(function).intersection(_QT_FIXTURES):
                violations.append(f"{_relative(path)}:{function.lineno}:{function.name}")
    assert violations == []


def test_unsaved_close_decision_suite_remains_explicit():
    path = TESTS_ROOT / "gui" / "test_unsaved_profile_close_guard.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required = {
        "test_dirty_close_cancel_preserves_workbench_and_reader": "StandardButton.Cancel",
        "test_dirty_close_discard_does_not_write_profile": "StandardButton.Discard",
        "test_dirty_close_save_uses_existing_authoritative_profile_path": "StandardButton.Save",
        "test_save_failure_during_close_keeps_workbench_open": "window.close() is False",
    }
    assert required.keys() <= functions.keys()
    for name, semantic_token in required.items():
        function = functions[name]
        function_source = ast.get_source_segment(source, function) or ""
        assert "qtbot" in _fixtures(function)
        assert "_confirm_unsaved_profile_close" in function_source
        assert semantic_token in function_source
