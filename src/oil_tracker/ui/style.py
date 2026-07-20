from __future__ import annotations

from importlib.resources import files


def load_application_stylesheet() -> str:
    styles = files("oil_tracker.resources.styles")
    return "\n".join(
        (
            styles.joinpath("app.qss").read_text(encoding="utf-8"),
            styles.joinpath("compact.qss").read_text(encoding="utf-8"),
        )
    )
