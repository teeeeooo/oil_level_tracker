"""Build the one-folder package with PyInstaller and check it (Product SSOT §2 A8, §8; V2-5).

Steps: build from packaging/OilLevelTracker.spec into build/dist/OilLevelTracker; report its size
against A8's limit; start the built app without a window on a free port and a temporary data folder;
check that it serves its pages (the frozen web/ folder) and its report drawing module; stop it; check
that nothing in the package folder was added or changed (Product SSOT §8). The last line is
"package=PASS" or "package=FAIL".

Usage: python scripts/build_package.py [--skip-build]
"""

from __future__ import annotations

import argparse
import hashlib
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "packaging" / "OilLevelTracker.spec"
DIST = ROOT / "build" / "dist"
WORK = ROOT / "build" / "pyinstaller"
NAME = "OilLevelTracker"
A8_LIMIT_MB = 200
PAGES = ("/web/index.html", "/web/render.js", "/web/video.html", "/web/report.css")
START_SEC = 60.0


def build() -> None:
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
         "--distpath", str(DIST), "--workpath", str(WORK), str(SPEC)],
        cwd=ROOT, check=True,
    )


def folder_state(folder: Path) -> dict[str, str]:
    """Every file under folder, by its path, with its content's hash. Links (a macOS framework's) are
    left out, so nothing is counted twice."""
    return {
        path.relative_to(folder).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(folder.rglob("*")) if path.is_file() and not path.is_symlink()
    }


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def fetch(url: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as failure:
        return failure.code, b""


def run_check(package: Path) -> list[str]:
    """Start the built app, ask for its pages, stop it. The problems found."""
    exe = package / (NAME + ".exe" if sys.platform == "win32" else NAME)
    port = free_port()
    problems = []
    with tempfile.TemporaryDirectory() as data:
        app = subprocess.Popen(
            [str(exe), "--no-window", "--port", str(port), "--data-folder", data],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            started = time.perf_counter()
            while True:
                try:
                    status, _ = fetch(f"http://127.0.0.1:{port}{PAGES[0]}")
                    break
                except OSError:
                    if app.poll() is not None or time.perf_counter() - started > START_SEC:
                        return [f"the app did not start (exit code {app.poll()})"]
                    time.sleep(0.25)
            print(f"start_sec={time.perf_counter() - started:.1f}")
            for page in PAGES:
                status, body = fetch(f"http://127.0.0.1:{port}{page}")
                print(f"page {page} status={status} bytes={len(body)}")
                if status != 200 or not body:
                    problems.append(f"{page} answered {status}")
        finally:
            app.terminate()
            app.wait(timeout=30)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-build", action="store_true", help="check the package already built")
    args = parser.parse_args(argv)
    if not args.skip_build:
        build()
    package = DIST / NAME
    before = folder_state(package)
    size_mb = sum((package / name).stat().st_size for name in before) / 1_000_000
    print(f"folder={package}")
    print(f"files={len(before)} size_mb={size_mb:.1f} limit_mb={A8_LIMIT_MB}")
    problems = [] if size_mb <= A8_LIMIT_MB else [f"{size_mb:.1f} MB is over {A8_LIMIT_MB} MB (A8)"]
    problems += run_check(package)
    after = folder_state(package)
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    print(f"package_files_changed={len(changed)}")
    problems += [f"written inside the package: {name}" for name in changed]
    for problem in problems:
        print(f"PROBLEM {problem}")
    print("package=" + ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
