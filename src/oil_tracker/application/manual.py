"""The user manual (P-2; DESIGN.md §5 "User manual"), opened from the help."""

from __future__ import annotations

from pathlib import Path

from oil_tracker.application.ports import Desktop


class Manual:
    """The manual's page, shipped beside the app's own pages, opened in the default browser."""

    def __init__(self, page: Path, desktop: Desktop) -> None:
        self.page = page
        self.desktop = desktop

    def open(self) -> None:
        self.desktop.open_file(self.page)
