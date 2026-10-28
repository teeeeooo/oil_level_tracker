"""Local HTTP server bound to 127.0.0.1: static UI, context images, frames, saves, report."""
from __future__ import annotations

import base64
import json
import math
import os
import re
import socketserver
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import cv2

from context import Context, Glass, background_view, encode_png

STATIC_TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8"}


def log(key: str, **values) -> None:
    parts = " ".join(f"{k}={v}" for k, v in values.items())
    print(f"SPIKE {key} {parts}".rstrip(), flush=True)


class SpikeState:
    def __init__(self, video: Path, glass: Glass, context: Context, out_dir: Path, static_dir: Path):
        self.video = video
        self.glass = glass
        self.context = context
        self.out_dir = out_dir
        self.static_dir = static_dir
        self.context_png = encode_png(context.rgb)
        self.background_png = encode_png(background_view(context.rgb))
        self.capture = cv2.VideoCapture(str(video))
        self.capture_lock = threading.Lock()
        (out_dir / "edits").mkdir(parents=True, exist_ok=True)
        (out_dir / "reports").mkdir(parents=True, exist_ok=True)

    # ---- metadata and saved edits -------------------------------------------------
    def meta(self) -> dict:
        c, g = self.context, self.glass
        latest = self.latest_edit()
        return {
            "video": {"name": self.video.name, "fps": c.fps, "frame_count": c.frame_count,
                      "width": c.width, "height": c.height},
            "glass": {"name": g.name, "cx": g.cx, "cy": g.cy, "rx": g.rx, "ry": g.ry, "zero_y": g.zero_y},
            "context": {"times": c.times, "y0": c.y0, "rows": int(c.rgb.shape[0]),
                        "columns": int(c.rgb.shape[1]), "build_sec": round(c.build_sec, 2)},
            "draft": {"lines": [{"id": "oil-1", "kind": "oil", "points": c.draft_points}]},
            "saved": latest,
        }

    def _versions(self, folder: str, suffix: str) -> list[Path]:
        return sorted((self.out_dir / folder).glob(f"*-v[0-9][0-9][0-9]{suffix}"))

    def latest_edit(self) -> dict | None:
        versions = self._versions("edits", ".json")
        if not versions:
            return None
        doc = json.loads(versions[-1].read_text(encoding="utf-8"))
        return {"version": _version_of(versions[-1]), "doc": doc}

    def save_edit(self, doc: dict) -> dict:
        version = len(self._versions("edits", ".json")) + 1
        path = self.out_dir / "edits" / f"edit-v{version:03d}.json"
        doc = dict(doc, saved_at=datetime.now().isoformat(timespec="seconds"), version=version)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        log("save", version=version, lines=len(doc.get("lines", [])),
            points=sum(len(l.get("points", [])) for l in doc.get("lines", [])))
        return {"version": version, "path": str(path)}

    # ---- report -------------------------------------------------------------------
    def write_report(self, doc: dict) -> dict:
        version = len(self._versions("reports", ".html")) + 1
        path = self.out_dir / "reports" / f"report-v{version:03d}.html"
        data = {"meta": {k: v for k, v in self.meta().items() if k not in ("draft", "saved")},
                "doc": doc, "version": version,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "context_png": "data:image/png;base64," + base64.b64encode(self.context_png).decode()}
        css = (self.static_dir / "style.css").read_text(encoding="utf-8")
        render = (self.static_dir / "render.js").read_text(encoding="utf-8")
        payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        html = (REPORT_TEMPLATE.replace("@@TITLE@@", f"유면 보고서 v{version:03d} (spike)")
                .replace("@@CSS@@", css).replace("@@RENDER@@", render).replace("@@DATA@@", payload))
        path.write_text(html, encoding="utf-8")
        log("report", version=version, bytes=path.stat().st_size)
        return {"version": version, "path": str(path)}

    def open_path(self, path: str) -> None:
        target = Path(path).resolve()
        if self.out_dir.resolve() not in target.parents:
            raise ValueError("Only files in the output folder can be opened.")
        if sys.platform == "win32":
            os.startfile(target)  # noqa: S606 - opens the report in the default browser
        elif sys.platform == "darwin":
            subprocess.run(["open", str(target)], check=False)
        else:
            subprocess.run(["xdg-open", str(target)], check=False)

    # ---- frames -------------------------------------------------------------------
    def frame(self, t: float) -> tuple[bytes, dict]:
        g, c = self.glass, self.context
        began = time.perf_counter()
        index = max(0, min(c.frame_count - 1, int(round(t * c.fps))))
        with self.capture_lock:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = self.capture.read()
        if not ok:
            raise ValueError(f"Cannot decode frame {index}.")
        half_w, half_h = max(2.5 * g.rx, 120), max(1.8 * g.ry, 120)
        x0, x1 = max(0, int(g.cx - half_w)), min(c.width, int(g.cx + half_w))
        y0, y1 = max(0, int(g.cy - half_h)), min(c.height, int(g.cy + half_h))
        ok, data = cv2.imencode(".jpg", frame[y0:y1, x0:x1], [cv2.IMWRITE_JPEG_QUALITY, 90])
        decode_ms = (time.perf_counter() - began) * 1000
        return data.tobytes(), {"X-Frame-Time": f"{index / c.fps:.4f}", "X-Frame-Index": str(index),
                                "X-Crop": f"{x0},{y0},{x1 - x0},{y1 - y0}",
                                "X-Decode-Ms": f"{decode_ms:.1f}"}


def _version_of(path: Path) -> int:
    match = re.search(r"-v(\d{3})\.", path.name)
    return int(match.group(1)) if match else 0


def make_handler(state: SpikeState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):  # keep stdout for SPIKE lines
            pass

        def _send(self, body: bytes, content_type: str, headers: dict | None = None, status: int = 200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.send_header("Access-Control-Expose-Headers", ", ".join((headers or {}).keys()))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, value, status: int = 200):
            self._send(json.dumps(value, ensure_ascii=False, allow_nan=False).encode(),
                       "application/json; charset=utf-8", status=status)

        def _body(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length) or b"{}")

        def do_GET(self):
            url = urlparse(self.path)
            try:
                if url.path in ("/", "/index.html"):
                    return self._static("index.html")
                if url.path.startswith("/static/"):
                    return self._static(url.path.removeprefix("/static/"))
                if url.path == "/api/meta":
                    return self._json(state.meta())
                if url.path == "/api/context.png":
                    return self._send(state.context_png, "image/png")
                if url.path == "/api/context_bg.png":
                    return self._send(state.background_png, "image/png")
                if url.path == "/api/frame":
                    t = float(parse_qs(url.query).get("t", ["0"])[0])
                    if not math.isfinite(t):
                        raise ValueError("t must be finite")
                    body, headers = state.frame(t)
                    return self._send(body, "image/jpeg", headers)
                self._json({"error": "not found"}, 404)
            except Exception as error:  # spike: report every failure to the UI
                self._json({"error": f"{type(error).__name__}: {error}"}, 500)

        def do_POST(self):
            url = urlparse(self.path)
            try:
                body = self._body()
                if url.path == "/api/save":
                    return self._json(state.save_edit(body["doc"]))
                if url.path == "/api/report":
                    return self._json(state.write_report(body["doc"]))
                if url.path == "/api/open":
                    state.open_path(body["path"])
                    return self._json({"ok": True})
                if url.path == "/api/log":
                    log(str(body.get("key", "ui")), **{k: v for k, v in body.items() if k != "key"})
                    return self._json({"ok": True})
                self._json({"error": "not found"}, 404)
            except Exception as error:
                self._json({"error": f"{type(error).__name__}: {error}"}, 500)

        def _static(self, name: str):
            path = (state.static_dir / name).resolve()
            if state.static_dir.resolve() not in path.parents or not path.is_file():
                return self._json({"error": "not found"}, 404)
            self._send(path.read_bytes(), STATIC_TYPES.get(path.suffix, "application/octet-stream"))

    return Handler


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def server_bind(self):
        # HTTPServer.server_bind calls socket.getfqdn(), a reverse DNS lookup that can
        # stall for tens of seconds on some networks; a 127.0.0.1 server never needs it.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]


def start_server(state: SpikeState, port: int = 0) -> ThreadingHTTPServer:
    server = LocalServer(("127.0.0.1", port), make_handler(state))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


REPORT_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
<style>@@CSS@@</style>
</head>
<body class="report">
<main id="report"></main>
<script>@@RENDER@@</script>
<script>const REPORT_DATA = @@DATA@@; Render.renderReport(document.getElementById("report"), REPORT_DATA);</script>
</body>
</html>
"""
