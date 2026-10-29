"""Where the app keeps its data (Product SSOT §8)."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

APP_FOLDER = "OilLevelTracker"
RECIPES = "Recipes"
INSPECTIONS = "Inspections"

_FOLDERID_DOCUMENTS = uuid.UUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7")


def default_data_folder() -> Path:
    """Documents\\OilLevelTracker, following a redirected Documents folder."""
    return documents_folder() / APP_FOLDER


def documents_folder() -> Path:
    if sys.platform == "win32":
        return _windows_known_folder(_FOLDERID_DOCUMENTS)
    return Path.home() / "Documents"


def _windows_known_folder(folder_id: uuid.UUID) -> Path:
    import ctypes
    from ctypes import wintypes

    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32
    shell32.SHGetKnownFolderPath.argtypes = [
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    shell32.SHGetKnownFolderPath.restype = ctypes.c_long
    ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole32.CoTaskMemFree.restype = None

    guid = (ctypes.c_ubyte * 16).from_buffer_copy(folder_id.bytes_le)
    pointer = ctypes.c_void_p()
    result = shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(pointer))
    try:
        if result != 0:
            raise OSError(f"SHGetKnownFolderPath failed: {result & 0xFFFFFFFF:#010x}")
        return Path(ctypes.wstring_at(pointer.value))
    finally:
        if pointer.value:
            ole32.CoTaskMemFree(pointer)
