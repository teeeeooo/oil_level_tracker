# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH).parents[1]
src_root = project_root / "src"
package_root = src_root / "oil_tracker"
runtime_hook = Path(SPECPATH) / "runtime_hooks" / "windows_qt_platform.py"

datas = [
    (str(package_root / "adapters" / "reporting" / "templates"), "oil_tracker/adapters/reporting/templates"),
    (str(package_root / "resources"), "oil_tracker/resources"),
]

a = Analysis(
    [str(package_root / "__main__.py")],
    pathex=[str(src_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(runtime_hook)],
    excludes=["tkinter", "PyQt5", "PyQt6"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RotaryOilLevelTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name="RotaryOilLevelTracker")
