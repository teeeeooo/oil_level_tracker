# -*- mode: python ; coding: utf-8 -*-
# The Windows build (Product SSOT §2 A8, §9): PyInstaller one-folder, no console, OilLevelTracker.exe
# (user, 2026-11-02). Run it through scripts/build_package.py, which also checks the result.
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"
WINDOWS = sys.platform == "win32"
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def version_resource(version: str):
    """What the exe's Properties > Details show (P-2b): the product name and the app version. Windows
    only: the module needs pefile, which PyInstaller installs only there."""
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
    )

    numbers = tuple(int(part) for part in re.match(r"(\d+)\.(\d+)\.(\d+)", version).groups()) + (0,)
    strings = [
        StringStruct("FileDescription", "Oil Level Tracker"),
        StringStruct("FileVersion", version),
        StringStruct("InternalName", "OilLevelTracker"),
        StringStruct("OriginalFilename", "OilLevelTracker.exe"),
        StringStruct("ProductName", "Oil Level Tracker"),
        StringStruct("ProductVersion", version),
    ]
    return VSVersionInfo(
        ffi=FixedFileInfo(filevers=numbers, prodvers=numbers),
        kids=[
            StringFileInfo([StringTable("041204B0", strings)]),  # Korean, Unicode
            VarFileInfo([VarStruct("Translation", [0x0412, 1200])]),
        ],
    )


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
    version=version_resource(VERSION) if WINDOWS else None,
    console=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name="OilLevelTracker")
