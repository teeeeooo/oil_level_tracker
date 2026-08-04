from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "packaging" / "pyinstaller" / "oil_tracker.spec"
HOOK = (
    ROOT
    / "packaging"
    / "pyinstaller"
    / "runtime_hooks"
    / "windows_qt_platform.py"
)


def _analysis_call() -> ast.Call:
    tree = ast.parse(SPEC.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        if isinstance(node.value.func, ast.Name) and node.value.func.id == "Analysis":
            return node.value
    raise AssertionError("PyInstaller Analysis(...) configuration not found")


def test_spec_registers_windows_qt_runtime_hook_for_gui_entry():
    analysis = _analysis_call()
    runtime_hooks = next(
        keyword.value for keyword in analysis.keywords if keyword.arg == "runtime_hooks"
    )
    assert isinstance(runtime_hooks, ast.List)
    assert len(runtime_hooks.elts) == 1
    registered = runtime_hooks.elts[0]
    assert isinstance(registered, ast.Call)
    assert isinstance(registered.func, ast.Name) and registered.func.id == "str"
    assert len(registered.args) == 1
    assert isinstance(registered.args[0], ast.Name)
    assert registered.args[0].id == "runtime_hook"

    entry_scripts = ast.unparse(analysis.args[0])
    assert "__main__.py" in entry_scripts
    assert HOOK.is_file()


def test_spec_runtime_hook_path_is_owned_beside_the_spec():
    source = SPEC.read_text(encoding="utf-8")
    assert (
        'runtime_hook = Path(SPECPATH) / "runtime_hooks" / "windows_qt_platform.py"'
        in source
    )


def _run_hook_in_subprocess(platform: str, inherited: str | None) -> str:
    env = os.environ.copy()
    if inherited is None:
        env.pop("QT_QPA_PLATFORM", None)
    else:
        env["QT_QPA_PLATFORM"] = inherited
    code = (
        "import os, runpy, sys; "
        f"sys.platform={platform!r}; "
        f"runpy.run_path({str(HOOK)!r}); "
        "print(os.environ.get('QT_QPA_PLATFORM', '<unset>'))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


@pytest.mark.parametrize("inherited", [None, "offscreen", "minimal"])
def test_windows_runtime_hook_forces_native_qpa(inherited):
    assert _run_hook_in_subprocess("win32", inherited) == "windows"


def test_non_windows_runtime_hook_does_not_force_windows():
    assert _run_hook_in_subprocess("darwin", "cocoa") == "cocoa"


def test_runtime_hook_has_no_qt_imports():
    tree = ast.parse(HOOK.read_text(encoding="utf-8"))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    assert not any(name.startswith("PySide6") for name in imported_modules)


def test_source_tree_entrypoints_do_not_import_packaged_runtime_hook():
    for relative in ("src/oil_tracker/__main__.py", "src/oil_tracker/cli.py"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "windows_qt_platform" not in source
        assert "packaging.pyinstaller" not in source
