"""Time the analysis core on a video and a v2 Recipe, for A4 (Product SSOT §2) on Windows.

Runs what the V2-2 analysis will run: one pass over the video for every Glass, the background
view, the Oil draft and PNG encoding in pieces of 4,096 columns, with the source SHA-256 on a
second thread. Writes nothing. Each Glass line gives the context image's mean pixel value, so
runs with and without --hardware can be compared.

Usage: python scripts/time_analysis.py --video VIDEO --recipe RECIPE.recipe.json [--hardware]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import threading
import time
from pathlib import Path

import cv2

from oil_tracker.adapters.storage.recipe_files import recipe_from_json
from oil_tracker.adapters.video.context import background_view, build_contexts
from oil_tracker.adapters.video.draft import oil_draft

RATE = 2.0            # Product SSOT §3
PIECE_COLUMNS = 4096  # the cache's PNG pieces
A4_LIMIT_SEC = 180.0


def sha256_of(path: Path, result: dict) -> None:
    began = time.perf_counter()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    result.update(hex=digest.hexdigest(), seconds=time.perf_counter() - began, ended=time.perf_counter())


def png_pieces(image) -> tuple[float, int]:
    began = time.perf_counter()
    size = 0
    for start in range(0, image.shape[1], PIECE_COLUMNS):
        piece = image[:, start:start + PIECE_COLUMNS]
        ok, data = cv2.imencode(".png", piece[:, :, ::-1] if piece.ndim == 3 else piece)
        if not ok:
            raise RuntimeError("PNG encoding failed")
        size += len(data)
    return time.perf_counter() - began, size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--hardware", action="store_true", help="ask OpenCV for hardware decoding")
    args = parser.parse_args(argv)

    recipe = recipe_from_json(args.recipe.read_text(encoding="utf-8"))
    began = time.perf_counter()
    sha: dict = {}
    hashing = threading.Thread(target=sha256_of, args=(args.video, sha))
    hashing.start()
    last_report = [began]

    def progress(done: int, total: int) -> None:
        now = time.perf_counter()
        if now - last_report[0] >= 30 or done == total:
            print(f"  progress {done}/{total} frames at {now - began:.0f}s", flush=True)
            last_report[0] = now

    passed = build_contexts(args.video, [glass.ellipse for glass in recipe.glasses], start_sec=0,
                            end_sec=float("inf"), rate=RATE, hardware=args.hardware, on_progress=progress)
    pass_end = time.perf_counter()
    seconds = passed.seconds
    print(f'video name="{args.video.name}" bytes={args.video.stat().st_size} '
          f"columns={len(passed.times)} frames_decoded={passed.frames_decoded}")
    print(f"pass glasses={len(recipe.glasses)} hardware_requested={args.hardware} hardware_used={passed.hardware} "
          f"grab={seconds['grab']:.1f}s retrieve={seconds['retrieve']:.1f}s reduce={seconds['reduce']:.1f}s "
          f"total={pass_end - began:.1f}s")
    for glass, image in zip(recipe.glasses, passed.images):
        step = time.perf_counter()
        background = background_view(image.rgb)
        background_sec = time.perf_counter() - step
        step = time.perf_counter()
        draft = oil_draft(image.rgb)
        draft_sec = time.perf_counter() - step
        context_png, context_bytes = png_pieces(image.rgb)
        background_png, background_bytes = png_pieces(background)
        rows, columns = image.rgb.shape[:2]
        print(f'glass name="{glass.name}" context={columns}x{rows} mean={image.rgb.mean():.3f} '
              f"background={background_sec:.1f}s draft={draft_sec:.1f}s empty={draft.empty.mean():.0%} "
              f"png={context_png + background_png:.1f}s png_bytes={context_bytes + background_bytes}")
    hashing.join()
    end = time.perf_counter()
    print(f"sha256 seconds={sha['seconds']:.1f} finished_before_pass_end={'yes' if sha['ended'] <= pass_end else 'no'}")
    print(f"analysis total={end - began:.1f}s limit={A4_LIMIT_SEC:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
