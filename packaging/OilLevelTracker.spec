# -*- mode: python ; coding: utf-8 -*-
# The Windows build (Product SSOT §2 A8, §9): PyInstaller one-folder, no console, OilLevelTracker.exe
# (user, 2026-11-02). Run it through scripts/build_package.py, which also checks the result.
import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"
WINDOWS = sys.platform == "win32"

a = Analysis(
    [str(SRC / "oil_tracker" / "__main__.py")],
    pathex=[str(SRC)],
    # The pages and the report's drawing module, read from beside the package's code
    # (bootstrap.WEB_FOLDER), so they go where oil_tracker/ is inside the build.
    datas=[(str(SRC / "oil_tracker" / "web"), "oil_tracker/web")],
    excludes=[
        "tkinter", "unittest", "pydoc", "doctest", "pytest", "playwright",
        # pywebview's other window toolkits: Windows uses WinForms with WebView2
        "PyQt5", "PyQt6", "PySide2", "PySide6", "qtpy", "gi", "cefpython3",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OilLevelTracker",
    icon=[str(ROOT / "packaging" / "OilLevelTracker.ico")] if WINDOWS else None,
    console=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name="OilLevelTracker")
