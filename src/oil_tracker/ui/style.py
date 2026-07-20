from __future__ import annotations

from importlib.resources import files


def load_application_stylesheet() -> str:
    return files("oil_tracker.resources.styles").joinpath("app.qss").read_text(encoding="utf-8")
