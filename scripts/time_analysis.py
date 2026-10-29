"""Time the V2-2 analysis on one PC, for A4 (Product SSOT §2). A person runs it in a terminal.

Stages: the PC and its software, the source check, then one analysis per decoding mode. Each
analysis runs the adapter the app uses (adapters/video/analysis.py), with the source SHA-256 on a
second thread as the analysis use case will. It writes only the result file (Markdown) and prints
the same text at the end.

Usage: python scripts/time_analysis.py --video VIDEO --recipe RECIPE.recipe.json
           [--runs software,hardware] [--out RESULT.md]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # this folder's code, even where another copy is installed

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from oil_tracker.adapters.storage.recipe_files import recipe_from_json  # noqa: E402
from oil_tracker.adapters.video.analysis import run_analysis  # noqa: E402
from oil_tracker.domain.inspection import AnalysisSettings  # noqa: E402

A4_LIMIT_SEC = 180.0
RUNS = {"software": False, "hardware": True}
SOURCE_SUFFIXES = {".py", ".js", ".css", ".html"}


def source_digest(root: Path = ROOT, script: str = "time_analysis.py") -> tuple[str, int]:
    """One short digest over the code that runs, to compare with the request."""
    files = sorted(
        path for path in (root / "src").rglob("*")
        if path.suffix in SOURCE_SUFFIXES and "__pycache__" not in path.parts
    )
    files += [root / "pyproject.toml", root / "scripts" / script]
    digest = hashlib.sha256()
    for path in files:
        digest.update(f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode())
    return digest.hexdigest()[:12], len(files)


def package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "?"


def pc_inventory() -> dict[str, str]:
    """CPU, memory, GPU and OS. On Windows from CIM through PowerShell; elsewhere what Python knows."""
    found = {"cpu": platform.processor() or "?", "cores": "?", "logical": "?", "ram_gb": "?",
             "gpu": "?", "os": platform.platform()}
    if sys.platform != "win32":
        return found
    command = (
        "$p = Get-CimInstance Win32_Processor | Select-Object -First 1; "
        "$c = Get-CimInstance Win32_ComputerSystem; "
        "$g = (Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }) -join ' / '; "
        "$o = Get-CimInstance Win32_OperatingSystem; "
        "[pscustomobject]@{cpu=$p.Name.Trim(); cores=$p.NumberOfCores; logical=$p.NumberOfLogicalProcessors; "
        "ram_gb=[math]::Round($c.TotalPhysicalMemory / 1GB, 1); gpu=$g; os=$o.Caption} | ConvertTo-Json -Compress"
    )
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", command],
                             capture_output=True, text=True, timeout=60, check=True).stdout
        found.update({key: str(value) for key, value in json.loads(out).items()})
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        found["os"] += f" (PC 정보를 읽지 못함: {error})"
    return found


def video_facts(path: Path) -> dict[str, float | int]:
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise SystemExit(f"영상을 열 수 없습니다: {path}")
        return {
            "width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": float(capture.get(cv2.CAP_PROP_FPS)),
            "frames": int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        }
    finally:
        capture.release()


def sha256_of(path: Path, result: dict) -> None:
    began = time.perf_counter()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    result.update(seconds=time.perf_counter() - began, ended=time.perf_counter())


def context_mean(pieces: tuple[bytes, ...]) -> float:
    images = [cv2.imdecode(np.frombuffer(piece, np.uint8), cv2.IMREAD_UNCHANGED) for piece in pieces]
    return float(np.concatenate(images, axis=1).mean())


def one_run(name: str, video: Path, recipe, settings: AnalysisSettings) -> dict:
    began = time.perf_counter()
    sha: dict = {}
    hashing = threading.Thread(target=sha256_of, args=(video, sha))
    hashing.start()
    last_report = [began]

    def progress(done: int, total: int) -> None:
        now = time.perf_counter()
        if now - last_report[0] >= 30:
            print(f"  progress {100 * done / total:.0f}% at {now - began:.0f}s", flush=True)
            last_report[0] = now

    try:
        analysis, timings = run_analysis(video, recipe.glasses, settings, progress, lambda: False,
                                         hardware=RUNS[name])
        analysis_end = time.perf_counter()
    finally:
        hashing.join()
    end = time.perf_counter()
    glasses = []
    for glass, draft, images, seconds in zip(recipe.glasses, analysis.drafts, analysis.images, timings.glass_seconds):
        ys = draft.oil.ys
        glasses.append({
            "name": glass.name,
            "context": f"{len(ys)}x{images.rows}",
            "mean": context_mean(images.context_png),
            "empty": sum(y is None for y in ys) / len(ys),
            "png_bytes": sum(map(len, images.context_png + images.background_png)),
            **seconds,
        })
    return {
        "name": name,
        "hardware_used": timings.hardware_used,
        "frames_decoded": timings.frames_decoded,
        "pass": timings.pass_seconds,
        "glass_total": sum(sum(g[k] for k in ("draft", "background", "png")) for g in glasses),
        "sha256": sha.get("seconds", float("nan")),
        "sha256_in_time": sha.get("ended", float("inf")) <= analysis_end,
        "total": end - began,
        "glasses": glasses,
    }


def markdown(facts: dict, runs: list[dict], errors: list[tuple[str, str]]) -> str:
    pc, video = facts["pc"], facts["video"]
    lines = [
        "# A4 시간 측정 결과",
        "",
        f"- 측정: {facts['when']} (이 PC 시각)",
        f"- 소스: `source={facts['source'][0]} files={facts['source'][1]}`",
        f"- 소프트웨어: python {facts['python']}, opencv-python-headless {facts['opencv']}, numpy {facts['numpy']}",
        f"- CPU: {pc['cpu']}, cores={pc['cores']}, logical={pc['logical']}, RAM {pc['ram_gb']} GB",
        f"- GPU: {pc['gpu']}; OS: {pc['os']}",
        f"- 영상: `{video['name']}`, {video['bytes']} bytes, {video['width']}x{video['height']}, "
        f"{video['fps']:.3f} fps, {video['frames']} frames",
        f"- Recipe: `{facts['recipe']}`, Glass {facts['glass_count']}개; 영상 전체, 초당 2장",
        "",
        "시간은 초. A4 한도는 180초.",
        "",
        "| 실행 | HW 사용 | grab | retrieve | reduce | wait | 패스 | Glass 처리 | SHA-256 | 전체 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for run in runs:
        p = run["pass"]
        sha = f"{run['sha256']:.1f}" + ("" if run["sha256_in_time"] else " (늦음)")
        lines.append(
            f"| {run['name']} | {run['hardware_used']} | {p['grab']:.1f} | {p['retrieve']:.1f} | {p['reduce']:.1f} "
            f"| {p['wait']:.1f} | {p['total']:.1f} | {run['glass_total']:.1f} | {sha} | **{run['total']:.1f}** |"
        )
    lines += [
        "",
        "| 실행 | Glass | context | mean | empty | draft | background | png | png_bytes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for run in runs:
        for g in run["glasses"]:
            lines.append(
                f"| {run['name']} | {g['name']} | {g['context']} | {g['mean']:.3f} | {g['empty']:.0%} "
                f"| {g['draft']:.1f} | {g['background']:.1f} | {g['png']:.1f} | {g['png_bytes']} |"
            )
    lines += ["", f"오류: {'없음' if not errors else len(errors)}"]
    for name, text in errors:
        lines += ["", f"## 오류: {name}", "", "```", text.rstrip(), "```"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--runs", default="software,hardware", help="software, hardware or both, comma-separated")
    parser.add_argument("--out", type=Path, help="the result file (default: a4-timing-<time>.md here)")
    args = parser.parse_args(argv)
    names = [name.strip() for name in args.runs.split(",") if name.strip()]
    if not names or any(name not in RUNS for name in names):
        parser.error(f"--runs takes {', '.join(RUNS)}")
    out = args.out or Path(f"a4-timing-{datetime.now():%Y%m%d-%H%M}.md")
    stages = 2 + len(names)

    print(f"[1/{stages}] PC와 소프트웨어 확인", flush=True)
    recipe = recipe_from_json(args.recipe.read_text(encoding="utf-8"))
    facts = {
        "when": f"{datetime.now():%Y-%m-%d %H:%M}",
        "python": platform.python_version(),
        "opencv": package_version("opencv-python-headless"),
        "numpy": np.__version__,
        "pc": pc_inventory(),
        "video": {"name": args.video.name, "bytes": args.video.stat().st_size, **video_facts(args.video)},
        "recipe": recipe.name,
        "glass_count": len(recipe.glasses),
    }
    pc = facts["pc"]
    print(f"  CPU: {pc['cpu']}, cores={pc['cores']}, logical={pc['logical']}, RAM {pc['ram_gb']} GB", flush=True)

    print(f"[2/{stages}] 소스 확인", flush=True)
    facts["source"] = source_digest()
    print(f"  source={facts['source'][0]} files={facts['source'][1]}", flush=True)

    video = facts["video"]
    settings = AnalysisSettings(0.0, video["frames"] / video["fps"])
    runs, errors = [], []
    for number, name in enumerate(names, start=3):
        print(f"[{number}/{stages}] 분석: {name} 디코딩 (진행 상황은 30초마다 표시)", flush=True)
        try:
            run = one_run(name, args.video, recipe, settings)
        except Exception:  # record it and go on to the next run
            text = traceback.format_exc()
            print(text, flush=True)
            errors.append((name, text))
            continue
        runs.append(run)
        print(f"  끝: 전체 {run['total']:.1f}초", flush=True)

    text = markdown(facts, runs, errors)
    out.write_text(text, encoding="utf-8")
    print("", flush=True)
    print(text, flush=True)
    print(f"결과 파일: {out.resolve()}", flush=True)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
