from __future__ import annotations

import os
import sys


# This hook belongs only to the PyInstaller GUI artifact. PyInstaller executes
# custom runtime hooks before package-defined runtime hooks and the entry script,
# so the native Windows QPA choice is fixed before PySide6 GUI initialization.
if sys.platform == "win32":
    os.environ["QT_QPA_PLATFORM"] = "windows"
