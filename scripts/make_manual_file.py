"""The user manual as one HTML file, handed out beside the release ZIP (P-2b; user, 2026-11-03).

The app ships the manual as a page in web/manual/ with its styles, script, figures and clips beside
it. Inspectors rarely open it from the help, so it also goes out on its own. This puts everything
inside one file: the styles and the script inline, every figure and clip as a data: URL. It opens
offline with a double click, wherever it is saved.

Usage: python scripts/make_manual_file.py [--out FOLDER]   (default: build/release)
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "src" / "oil_tracker" / "web" / "manual"
RELEASE = ROOT / "build" / "release"
TYPES = {".webp": "image/webp", ".mp4": "video/mp4"}
# what the page loads from files: stylesheets, the script, figures and clips
OUTSIDE = re.compile(r'<link[^>]*href="(?!#)|\b(?:src|poster)="(?!data:)')


def version() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def single_file(manual: Path = MANUAL) -> str:
    """The manual page with everything it loads inside it."""
    page = (manual / "index.html").read_text(encoding="utf-8")
    style = (manual.parent / "tokens.css").read_text(encoding="utf-8") + (manual / "manual.css").read_text(encoding="utf-8")
    script = (manual / "manual.js").read_text(encoding="utf-8")
    page = re.sub(r'<link rel="stylesheet" href="[^"]+">\n', "", page)
    page = page.replace("</head>", f"<style>\n{style}</style>\n</head>", 1)
    # the script ran deferred from its file; inline, it goes last so that the page is there
    page = re.sub(r'<script src="manual\.js" defer></script>\n', "", page)
    page = page.replace("</body>", f"<script>\n{script}</script>\n</body>", 1)

    def embed(found: re.Match[str]) -> str:
        path = manual / found[2]
        return f'{found[1]}="data:{TYPES[path.suffix]};base64,{base64.b64encode(path.read_bytes()).decode("ascii")}"'

    page = re.sub(r'\b(src|poster)="((?:img|clips)/[^"]+)"', embed, page)
    if OUTSIDE.search(page):
        raise ValueError(f"the page still loads a file: {OUTSIDE.search(page)[0]}")
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=RELEASE, help="the folder to write into")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f"OilLevelTracker-{version()}-사용설명서.html"
    target.write_text(single_file(), encoding="utf-8")
    print(f"manual={target} bytes={target.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
