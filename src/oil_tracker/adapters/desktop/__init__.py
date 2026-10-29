"""Operating-system integration: the native file dialog, opening a folder and the close question."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from oil_tracker.application.ports import DesktopUnavailable


class SystemDesktop:
    """Implements application.ports.Desktop. app.py supplies the window's file dialog and close question."""

    def __init__(
        self,
        pick_video: Callable[[], Path | None] | None = None,
        ask_before_closing: Callable[[bool], None] | None = None,
    ) -> None:
        self._pick_video = pick_video
        self._ask_before_closing = ask_before_closing

    def pick_video(self) -> Path | None:
        if self._pick_video is None:
            raise DesktopUnavailable("창이 없어 파일 대화상자를 열 수 없습니다.")
        return self._pick_video()

    def ask_before_closing(self, ask: bool) -> None:
        if self._ask_before_closing is not None:
            self._ask_before_closing(ask)

    def open_folder(self, folder: Path) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606 - opens Explorer on the app's own folder
        elif sys.platform == "darwin":
            subprocess.run(["open", str(folder)], check=False)
        else:
            subprocess.run(["xdg-open", str(folder)], check=False)
