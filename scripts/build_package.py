"""Build the one-folder package with PyInstaller and check it (Product SSOT §2 A8, §8; V2-5).

Steps: build from packaging/OilLevelTracker.spec into build/dist/OilLevelTracker; report its size
against A8's limit; start the built app without a window on a free port and a temporary data folder;
check that it serves its pages (the frozen web/ folder) and its report drawing module; stop it; check
that nothing in the package folder was added or changed (Product SSOT §8). With --release, a package
that passed also goes into build/release/OilLevelTracker-<version>.zip beside the install guide
(P-2b): the ZIP that inspectors copy from the shared folder. The last line is "package=PASS" or
"package=FAIL".

Usage: python scripts/build_package.py [--skip-build] [--release]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import socket
import subprocess
import sys
import tempfile
import time
import tomllib
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "packaging" / "OilLevelTracker.spec"
DIST = ROOT / "build" / "dist"
WORK = ROOT / "build" / "pyinstaller"
NAME = "OilLevelTracker"
RELEASE = ROOT / "build" / "release"
WEB = ROOT / "src" / "oil_tracker" / "web"
GUIDE = ROOT / "packaging" / "install-guide.html"
GUIDE_NAME = "설치 안내.html"
MANUAL_IN_PACKAGE = "_internal/oil_tracker/web/manual/index.html"  # the guide links to it
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


def version() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def install_guide(app_version: str, web: Path = WEB) -> str:
    """The install guide as one file: the manual's styles inlined, the version filled in."""
    parts = {
        "STYLE": (web / "tokens.css").read_text(encoding="utf-8") + (web / "manual" / "manual.css").read_text(encoding="utf-8"),
        "VERSION": app_version,
    }
    return re.sub(r"<!--(STYLE|VERSION)-->", lambda m: parts[m[1]], GUIDE.read_text(encoding="utf-8"))


def release_zip(package: Path, app_version: str, folder: Path = RELEASE, web: Path = WEB) -> Path:
    """OilLevelTracker-<version>.zip: the install guide and the package folder side by side, so that
    "모두 압축 풀기" puts both where the inspector chooses (P-2b)."""
    if not (package / MANUAL_IN_PACKAGE).is_file():
        raise FileNotFoundError(f"the guide's manual link has no target: {MANUAL_IN_PACKAGE}")
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{NAME}-{app_version}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(GUIDE_NAME, install_guide(app_version, web))  # a non-ASCII name: stored as UTF-8
        for path in sorted(package.rglob("*")):
            if path.is_file() and not path.is_symlink():
                archive.write(path, f"{NAME}/{path.relative_to(package).as_posix()}")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-build", action="store_true", help="check the package already built")
    parser.add_argument("--release", action="store_true", help="also make the release ZIP when it passes")
    args = parser.parse_args(argv)
    print(f"version={version()}")
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
    if args.release and not problems:
        archive = release_zip(package, version())
        with zipfile.ZipFile(archive) as opened:
            entries = len(opened.namelist())
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        print(f"zip={archive} zip_entries={entries} zip_bytes={archive.stat().st_size} zip_sha256={digest}")
    for problem in problems:
        print(f"PROBLEM {problem}")
    print("package=" + ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
