"""Web UI spike entry point: build the context, serve it on 127.0.0.1, open a pywebview window."""
from __future__ import annotations

import argparse
import platform
import sys
import time
from pathlib import Path

from context import build_context, read_v1_glass
from server import SpikeState, log, start_server


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Oil level web UI spike")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--recipe", required=True, type=Path, help="v1 .oilrecipe; only the Glass geometry is read")
    parser.add_argument("--glass-index", type=int, default=0)
    parser.add_argument("--glass-name", default=None, help="exact Glass name in the Recipe; overrides --glass-index")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, default=None)
    parser.add_argument("--rate", type=float, default=2.0, help="context columns per second")
    parser.add_argument("--draft-spacing", type=float, default=2.0, help="seconds between naive draft points")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-window", action="store_true", help="serve only; open the URL in a browser")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    log("start", python=platform.python_version(), os=platform.platform(), frozen=getattr(sys, "frozen", False))
    glass = read_v1_glass(args.recipe, args.glass_index, args.glass_name)
    log("glass", name=repr(glass.name), cx=glass.cx, cy=glass.cy, rx=glass.rx, ry=glass.ry, zero_y=glass.zero_y)
    tag = args.glass_name or f"glass{args.glass_index}"
    out_dir = args.out or Path.cwd() / "webui-spike-output" / f"{args.video.stem}-{tag}"
    context = build_context(args.video, glass, args.start, args.end, args.rate,
                            progress=lambda done, total: log("context_progress", done=done, total=total),
                            draft_spacing=args.draft_spacing)
    log("context", columns=context.rgb.shape[1], rows=context.rgb.shape[0],
        build_sec=f"{context.build_sec:.2f}", draft_points=len(context.draft_points))
    state = SpikeState(args.video, glass, context, out_dir, resource_dir() / "static")
    server = start_server(state, args.port)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    log("server", url=url, out=out_dir)

    if args.no_window:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            return 0

    import webview  # imported late so --no-window runs without pywebview

    webview.create_window(f"유면 편집 spike - {args.video.name}", url, width=1500, height=950)
    webview.start()
    log("window_closed", renderer=getattr(webview, "renderer", "?"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
