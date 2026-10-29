"""Entry point: start the local server and open the pywebview window."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from oil_tracker import bootstrap

VIDEO_TYPES = ("영상 (*.mp4;*.avi;*.mov;*.mkv;*.m4v)", "모든 파일 (*.*)")


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

    running = bootstrap.start(data_folder=args.data_folder, port=args.port, pick_video=pick_video)
    holder["window"] = webview.create_window(
        "Oil Level Tracker", running.url, width=1440, height=900, min_size=(1280, 800)
    )
    try:
        webview.start()
    finally:
        running.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
