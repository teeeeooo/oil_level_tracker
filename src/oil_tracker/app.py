"""Entry point: start the local server and open the pywebview window."""

from __future__ import annotations

import argparse
import faulthandler
import json
import platform
import sys
import threading
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

from oil_tracker import __version__, bootstrap

VIDEO_TYPES = ("영상 (*.mp4;*.avi;*.mov;*.mkv;*.m4v)", "모든 파일 (*.*)")
# pywebview's own close question, asked while the editor holds unsaved edits (Product SSOT §6)
CLOSE_QUESTION = {
    "global.quitConfirmation": "저장하지 않은 편집이 있습니다. 저장하지 않고 닫을까요?",
    "global.quit": "닫기",
    "global.cancel": "취소",
}


LOG_FILE = "app.log"  # in the settings folder (Product SSOT §8)
LOG_OLD = "app.1.log"
LOG_ROLL_BYTES = 1_000_000

VIDEO_WINDOW_FILE = "video-window.json"  # where the video window was left, in the settings folder
VIDEO_WINDOW_SIZE = (1280, 800)
VIDEO_WINDOW_MIN = (960, 600)


class VideoWindow:
    """The full-size video window (Product SSOT §6; DESIGN.md §5): a second OS window, one at a
    time, opened again where it was left."""

    def __init__(self, webview: Any, origin: Callable[[], str], place_file: Path) -> None:
        self._webview = webview
        self._origin = origin
        self._file = place_file
        self._place = load_place(place_file)
        self._window: Any = None
        self._lock = threading.Lock()

    def show(self, path: str, title: str) -> None:
        url = self._origin() + path
        with self._lock:
            window = self._window
            if window is None:
                width, height = self._place.get("width", VIDEO_WINDOW_SIZE[0]), self._place.get("height", VIDEO_WINDOW_SIZE[1])
                x, y = self._place.get("x"), self._place.get("y")
                if not self._on_a_screen(x, y, width, height):
                    x = y = None
                window = self._webview.create_window(
                    title, url, width=width, height=height, x=x, y=y, min_size=VIDEO_WINDOW_MIN
                )
                # macOS reports floats
                window.events.moved += lambda x, y: self._place.update(x=round(x), y=round(y))
                window.events.resized += lambda width, height: self._place.update(width=round(width), height=round(height))
                window.events.closed += lambda: self._closed(window)
                self._window = window
                return
        if window.get_current_url() != url:  # another inspection
            window.load_url(url)
        window.set_title(title)
        window.restore()
        window.show()
        window.on_top = True  # brings it forward; pywebview has no call for that alone
        window.on_top = False

    def close(self) -> None:
        with self._lock:
            window = self._window
        if window is not None:
            window.destroy()

    def _closed(self, window: Any) -> None:
        with self._lock:
            if self._window is window:
                self._window = None
        save_place(self._file, self._place)

    def _on_a_screen(self, x: int | None, y: int | None, width: int, height: int) -> bool:
        """Whether the saved place still shows on a screen (a second monitor may be gone)."""
        if x is None or y is None:
            return False
        try:
            screens = self._webview.screens
        except Exception:  # noqa: BLE001 - no screen list: let the system place it
            return False
        return any(
            x + 80 < s.x + s.width and s.x < x + width - 80 and s.y <= y < s.y + s.height - 40 for s in screens
        )


def load_place(path: Path) -> dict[str, int]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    place = {k: v for k, v in raw.items() if k in ("x", "y", "width", "height") and type(v) is int}
    if place.get("width", VIDEO_WINDOW_MIN[0]) < VIDEO_WINDOW_MIN[0] or place.get("height", VIDEO_WINDOW_MIN[1]) < VIDEO_WINDOW_MIN[1]:
        place.pop("width", None)
        place.pop("height", None)
    return place


def save_place(path: Path, place: dict[str, int]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(place), encoding="utf-8")
    except OSError:
        pass  # the next window opens where the system puts it


class Tee:
    """Text for the console, written also to the log. A windowed build has no console (None)."""

    def __init__(self, *streams: TextIO | None) -> None:
        self._streams = [s for s in streams if s is not None]

    def write(self, text: str) -> int:
        for stream in self._streams:
            try:
                stream.write(text)
            except (OSError, ValueError):
                pass  # a closed console or log loses the line, not the app
        return len(text)

    def flush(self) -> None:
        for stream in self._streams:
            try:
                stream.flush()
            except (OSError, ValueError):
                pass

    def isatty(self) -> bool:
        return False


def start_log(folder: Path) -> TextIO | None:
    """The log in the settings folder: what goes to the console's error stream (the tracebacks), and a
    crash's stack, kept for a windowed build that has no console. Once it grows past LOG_ROLL_BYTES it
    becomes app.1.log at the next start. None when the folder cannot be written; the app runs on."""
    try:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / LOG_FILE
        if path.exists() and path.stat().st_size > LOG_ROLL_BYTES:
            path.replace(folder / LOG_OLD)
        log = path.open("a", encoding="utf-8", errors="backslashreplace", buffering=1)
    except OSError:
        return None
    build = "build" if getattr(sys, "frozen", False) else "source"
    log.write(
        f"--- {datetime.now().astimezone().isoformat(timespec='seconds')} start: {__version__} ({build}), "
        f"Python {platform.python_version()}, {platform.platform()}\n"
    )
    sys.stderr = Tee(sys.stderr, log)
    faulthandler.enable(log)
    return log


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="oil_tracker", description="Oil Level Tracker v2")
    parser.add_argument("--data-folder", type=Path, default=None, help="default: Documents/OilLevelTracker")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-window", action="store_true", help="serve only and print the URL")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    began = time.perf_counter()
    args = parse_args(argv)
    log = start_log(bootstrap.settings_folder())  # before pywebview, whose logger keeps the stream it finds
    if args.no_window:
        running = bootstrap.start(data_folder=args.data_folder, port=args.port)
        print(running.url, flush=True)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            return 0
        finally:
            running.close()

    import webview  # imported late so --no-window runs without pywebview

    holder: dict[str, Any] = {}
    video_window = VideoWindow(webview, lambda: holder["running"].origin, bootstrap.settings_folder() / VIDEO_WINDOW_FILE)

    def pick_video() -> Path | None:
        chosen = holder["window"].create_file_dialog(
            webview.FileDialog.OPEN, allow_multiple=False, file_types=VIDEO_TYPES
        )
        return Path(chosen[0]) if chosen else None

    def ask_before_closing(ask: bool) -> None:
        holder["window"].confirm_close = ask  # read when the window is asked to close

    running = bootstrap.start(
        data_folder=args.data_folder,
        port=args.port,
        pick_video=pick_video,
        ask_before_closing=ask_before_closing,
        video_window=(video_window.show, video_window.close),
    )
    holder["running"] = running
    holder["window"] = webview.create_window(
        "Oil Level Tracker", running.url, width=1440, height=900, min_size=(1280, 800), localization=CLOSE_QUESTION
    )
    holder["window"].events.closed += video_window.close  # the app ends with its main window
    if log is not None:  # how long the window takes (V2-5), counted from main(), after Python started
        holder["window"].events.loaded += lambda: log.write(f"window: page loaded {time.perf_counter() - began:.1f} s after start\n")
    try:
        webview.start()
    finally:
        running.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
