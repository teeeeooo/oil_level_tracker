# PyInstaller one-folder build for the web UI spike.
# Run from the repository root: pyinstaller --noconfirm spikes/webui/spike.spec
from pathlib import Path

HERE = Path(SPECPATH)

a = Analysis(
    [str(HERE / "app.py")],
    pathex=[str(HERE)],
    datas=[(str(HERE / "static"), "static")],
    hiddenimports=[],
    excludes=["matplotlib", "PySide6", "PyQt5", "PyQt6", "tkinter", "IPython", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="oil-webui-spike", console=True)
coll = COLLECT(exe, a.binaries, a.datas, name="oil-webui-spike")
