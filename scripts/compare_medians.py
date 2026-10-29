"""Compare ways to take the context's row medians on one PC, for A4 (the analysis time).

The row median (adapters/video/context.py) sorts each row of a Glass's band as int16. On the slowest
PC the medians share four cores with the decoder, so a cheaper median leaves more CPU to decoding.
Which way is cheapest depends on the CPU: NumPy sorts some types with SIMD (AVX2 for 32-bit types
on x86), others not. So this runs on that PC:
1. frames spread over the video, each way's medians against the app's (they must be identical),
   timed on one thread and on the app's number of worker threads;
2. the app's context pass over two minutes of the video, with the app's way and the two fastest
   identical ones, twice each in turn.

Usage: python scripts/compare_medians.py --video VIDEO --recipe RECIPE.recipe.json [--out RESULT.md]
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # this folder's code, even where another copy is installed

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from oil_tracker.adapters.storage.recipe_files import recipe_from_json  # noqa: E402
from oil_tracker.adapters.video import context  # noqa: E402
from oil_tracker.domain.geometry import Ellipse  # noqa: E402
from oil_tracker.domain.inspection import ANALYSIS_RATE, sample_indices  # noqa: E402

Median = Callable[[np.ndarray], np.ndarray]  # a BGR frame to one context column (rows x 3, RGB)
Factory = Callable[[context._Band], Median]
APP_MEDIAN = context._Band.median
FRAMES = 40
REPEATS = 3
PASS_SEC = 120.0
SIMD = ("AVX2", "AVX512F", "AVX512_SKX", "AVX512_ICL")


def sorting(dtype, outside: int, channel_first: bool) -> Factory:
    """The app's way in another type or layout: outside pixels sort last, two middle ranks per row."""
    def factory(band: context._Band) -> Median:
        def median(frame: np.ndarray) -> np.ndarray:
            crop = frame[band.y0:band.y1, band.x0:band.x1]
            if channel_first:  # 3 x rows x columns: each row contiguous for the sort
                data = np.ascontiguousarray(crop.transpose(2, 0, 1), dtype=dtype)
                data[:, band.outside] = outside
                data.sort(axis=2)
                pair = data[:, band.rows, band.low].astype(np.int16), data[:, band.rows, band.high].astype(np.int16)
                value = ((pair[0] + pair[1]) // 2).T
            else:
                data = crop.astype(dtype)
                data[band.outside] = outside
                data.sort(axis=1)
                value = (data[band.rows, band.low].astype(np.int16) + data[band.rows, band.high].astype(np.int16)) // 2
            value[band.empty] = 0
            return value[:, ::-1].astype(np.uint8)
        return median
    return factory


def selecting(dtype, below: int, above: int) -> Factory:
    """Half of each row's outside pixels below every value, the rest above: then the middle ranks of
    every row fall on the same one or two positions, and a partition finds them instead of a sort."""
    def factory(band: context._Band) -> Median:
        columns = band.outside.shape[1]
        outside_count = band.outside.sum(axis=1)
        lower = band.outside & (np.cumsum(band.outside, axis=1) <= (outside_count // 2)[:, None])
        upper = band.outside & ~lower
        low = np.clip(outside_count // 2 + band.low, 0, columns - 1)
        high = np.clip(outside_count // 2 + band.high, 0, columns - 1)
        kth = sorted({int(k) for k in np.concatenate([low, high])})

        def median(frame: np.ndarray) -> np.ndarray:
            data = np.ascontiguousarray(frame[band.y0:band.y1, band.x0:band.x1].transpose(2, 0, 1), dtype=dtype)
            data[:, lower] = below
            data[:, upper] = above
            data.partition(kth, axis=2)
            value = ((data[:, band.rows, low].astype(np.int16) + data[:, band.rows, high].astype(np.int16)) // 2).T
            value[band.empty] = 0
            return value[:, ::-1].astype(np.uint8)
        return median
    return factory


def counting(band: context._Band) -> Median:
    """An 8-bit histogram per row and channel; a rank's value is how many bins stay at or below it."""
    inside = ~band.outside
    rows = band.rows.size
    keys = np.nonzero(inside)[0] * 256
    low, high = band.low[:, None], band.high[:, None]

    def median(frame: np.ndarray) -> np.ndarray:
        crop = frame[band.y0:band.y1, band.x0:band.x1]
        value = np.empty((rows, 3), np.int16)
        for channel in range(3):  # RGB from BGR
            counts = np.bincount(keys + crop[..., 2 - channel][inside], minlength=rows * 256).reshape(rows, 256)
            below = counts.cumsum(axis=1)
            value[:, channel] = ((below <= low).sum(axis=1) + (below <= high).sum(axis=1)) // 2
        value[band.empty] = 0
        return value.astype(np.uint8)
    return median


APP = "`int16` 정렬 (지금)"
WAYS: dict[str, Factory] = {
    APP: lambda band: partial(APP_MEDIAN, band),
    "`int16` 정렬, 채널 먼저": sorting(np.int16, context._OUTSIDE, True),
    "`int32` 정렬": sorting(np.int32, context._OUTSIDE, False),
    "`int32` 정렬, 채널 먼저": sorting(np.int32, context._OUTSIDE, True),
    "`float32` 정렬": sorting(np.float32, context._OUTSIDE, False),
    "`float32` 정렬, 채널 먼저": sorting(np.float32, context._OUTSIDE, True),
    "`uint8` 정렬, 채널 먼저": sorting(np.uint8, 255, True),  # ties with 255 inside leave the ranks' values alone
    "`int16` 부분 정렬": selecting(np.int16, -context._OUTSIDE, context._OUTSIDE),
    "`int32` 부분 정렬": selecting(np.int32, -context._OUTSIDE, context._OUTSIDE),
    "`uint8` 부분 정렬": selecting(np.uint8, 0, 255),
    "8비트 계수": counting,
}


def simd() -> str:
    try:
        from numpy._core._multiarray_umath import __cpu_features__ as features
    except ImportError:
        return "?"
    return ", ".join(f"{name} {'예' if features.get(name) else '아니오'}" for name in SIMD)


def spread_frames(path: Path, count: int) -> tuple[list[np.ndarray], int, int, float, int]:
    """`count` frames the analysis would sample, spread over the video; and its size, fps and length."""
    capture = cv2.VideoCapture(str(path))
    try:
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        indices = sample_indices(fps, frame_count, 0.0, frame_count / fps, ANALYSIS_RATE)
        frames = []
        for k in np.linspace(0, len(indices) - 1, min(count, len(indices))).round().astype(int):
            capture.set(cv2.CAP_PROP_POS_FRAMES, indices[k])
            ok, frame = capture.read()
            if ok:
                frames.append(frame)
        return frames, width, height, fps, frame_count
    finally:
        capture.release()


def time_ways(bands: Sequence[context._Band], frames: Sequence[np.ndarray], repeats: int, threads: int) -> list[dict]:
    """Each way: identical to the app's or not, then ms per frame on one thread and on `threads`."""
    medians = {name: [factory(band) for band in bands] for name, factory in WAYS.items()}
    expected = [[m(frame) for m in medians[APP]] for frame in frames]
    rows = {name: {"name": name, "same": all(np.array_equal(m(frame), e) for frame, want in zip(frames, expected)
                                             for m, e in zip(ms, want)), "one": [], "many": 0.0}
            for name, ms in medians.items()}

    def run(ms: list[Median], part: Sequence[np.ndarray]) -> None:
        for frame in part:
            for m in ms:
                m(frame)

    pool = ThreadPoolExecutor(threads)
    try:
        for _ in range(repeats):  # each round goes through every way, so a slow spell hits them all
            for name, ms in medians.items():
                for frame in frames:
                    began = time.perf_counter()
                    run(ms, [frame])
                    rows[name]["one"].append(time.perf_counter() - began)
                began = time.perf_counter()
                list(pool.map(lambda part: run(ms, part), [frames[i::threads] for i in range(threads)]))
                rows[name]["many"] += time.perf_counter() - began
    finally:
        pool.shutdown()
    done = len(frames) * repeats
    return [{"name": r["name"], "same": r["same"], "one": 1000 * statistics.median(r["one"]),
             "many": 1000 * r["many"] / done} for r in rows.values()]


@contextmanager
def medians_by(factory: Factory):
    """Let the app's context pass take its medians the given way."""
    app_band = context._Band

    class Band(app_band):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self._median = factory(self)

        def median(self, frame: np.ndarray) -> np.ndarray:
            return self._median(frame)

    context._Band = Band
    try:
        yield
    finally:
        context._Band = app_band


def time_passes(path: Path, ellipses: Sequence[Ellipse], names: Sequence[str], start: float, end: float,
                rounds: int) -> list[dict]:
    found = {name: {"name": name, "same": True, "total": [], "seconds": {}} for name in names}
    expected = None
    for _ in range(rounds):
        for name in names:
            with medians_by(WAYS[name]):
                began = time.perf_counter()
                passed = context.build_contexts(path, ellipses, start_sec=start, end_sec=end, rate=ANALYSIS_RATE)
                found[name]["total"].append(time.perf_counter() - began)
            found[name]["seconds"] = passed.seconds
            images = [image.rgb for image in passed.images]
            if expected is None:
                expected = images
            found[name]["same"] &= all(np.array_equal(a, b) for a, b in zip(images, expected))
    return list(found.values())


def compare(video: Path, ellipses: Sequence[Ellipse], *, frames: int = FRAMES, repeats: int = REPEATS,
            pass_sec: float = PASS_SEC, rounds: int = 2, threads: int = context.REDUCE_WORKERS) -> dict:
    spread, width, height, fps, frame_count = spread_frames(video, frames)
    bands = [context._Band(e, width, height) for e in ellipses]
    ways = time_ways(bands, spread, repeats, threads)
    fastest = sorted((w for w in ways if w["same"] and w["name"] != APP), key=lambda w: w["many"])[:2]
    duration = frame_count / fps
    start = round(0.3 * duration, 1)
    end = min(duration, start + pass_sec)
    passes = time_passes(video, ellipses, [APP, *(w["name"] for w in fastest)], start, end, rounds)
    return {
        "numpy": np.__version__, "simd": simd(), "threads": threads, "frames": len(spread), "repeats": repeats,
        "bands": [f"{b.y1 - b.y0}x{b.x1 - b.x0}" for b in bands], "ways": ways, "range": (start, end),
        "passes": passes,
    }


def markdown(found: dict) -> list[str]:
    ways = {w["name"]: w for w in found["ways"]}
    app = ways[APP]
    lines = [
        "## A4: 중앙값 비교",
        "",
        f"- NumPy {found['numpy']}; SIMD: {found['simd']}",
        f"- 프레임 {found['frames']}장 × {found['repeats']}번, Glass 띠 {', '.join(found['bands'])}, "
        f"스레드 {found['threads']}개 (앱과 같은 수)",
        "",
        f"| 방식 | 출력 | 1스레드 ms/프레임 | 배율 | {found['threads']}스레드 ms/프레임 | 배율 |",
        "|---|---|---|---|---|---|",
    ]
    for w in found["ways"]:
        same = "기준" if w["name"] == APP else ("같음" if w["same"] else "**다름**")
        lines.append(f"| {w['name']} | {same} | {w['one']:.2f} | {app['one'] / w['one']:.2f} "
                     f"| {w['many']:.2f} | **{app['many'] / w['many']:.2f}** |")
    start, end = found["range"]
    lines += [
        "",
        f"앱의 맥락 패스, {start:.1f}~{end:.1f}초 구간 (초):",
        "",
        "| 방식 | 출력 | 1회 | 2회 | grab | retrieve | reduce | wait |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in found["passes"]:
        s = p["seconds"]
        same = "기준" if p["name"] == APP else ("같음" if p["same"] else "**다름**")
        totals = [f"{t:.2f}" for t in p["total"]] + ["—"] * (2 - len(p["total"]))
        lines.append(f"| {p['name']} | {same} | {totals[0]} | {totals[1]} | {s.get('grab', math.nan):.2f} "
                     f"| {s.get('retrieve', math.nan):.2f} | {s.get('reduce', math.nan):.2f} | {s.get('wait', math.nan):.2f} |")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="the result file (default: print only)")
    args = parser.parse_args(argv)
    recipe = recipe_from_json(args.recipe.read_text(encoding="utf-8"))
    text = "\n".join(markdown(compare(args.video, [g.ellipse for g in recipe.glasses]))) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
