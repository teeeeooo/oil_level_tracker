"""Entry point: start the local server and open the pywebview window."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from oil_tracker import bootstrap

VIDEO_TYPES = ("영상 (*.mp4;*.avi;*.mov;*.mkv;*.m4v)", "모든 파일 (*.*)")
# pywebview's own close question, asked while the editor holds unsaved edits (Product SSOT §6)
CLOSE_QUESTION = {
    "global.quitConfirmation": "저장하지 않은 편집이 있습니다. 저장하지 않고 닫을까요?",
    "global.quit": "닫기",
    "global.cancel": "취소",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="oil_tracker", description="Oil Level Tracker v2")
    parser.add_argument("--data-folder", type=Path, default=None, help="default: Documents/OilLevelTracker")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-window", action="store_true", help="serve only and print the URL")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
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

    holder: dict[str, webview.Window] = {}

    def pick_video() -> Path | None:
        chosen = holder["window"].create_file_dialog(
            webview.FileDialog.OPEN, allow_multiple=False, file_types=VIDEO_TYPES
        )
        return Path(chosen[0]) if chosen else None

    def ask_before_closing(ask: bool) -> None:
        holder["window"].confirm_close = ask  # read when the window is asked to close

    running = bootstrap.start(
        data_folder=args.data_folder, port=args.port, pick_video=pick_video, ask_before_closing=ask_before_closing
    )
    holder["window"] = webview.create_window(
        "Oil Level Tracker", running.url, width=1440, height=900, min_size=(1280, 800), localization=CLOSE_QUESTION
    )
    try:
        webview.start()
    finally:
        running.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
