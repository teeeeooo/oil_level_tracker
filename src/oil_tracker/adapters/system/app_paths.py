from __future__ import annotations

import os
from pathlib import Path


def user_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    path = base / "RotaryOilLevelTracker"
    path.mkdir(parents=True, exist_ok=True)
    return path
