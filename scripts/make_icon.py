"""Make the app icon file, packaging/OilLevelTracker.ico, from its two drawings (DESIGN.md §4,
"App icon"). Run it on the development Mac after changing a drawing; the build only reads the .ico.

Each size is drawn by Chrome straight from the SVG (no scaling of a large picture): sizes up to
SMALL_MAX from app-icon-small.svg, the rest from app-icon.svg. The .ico holds one PNG per size.

Usage: python scripts/make_icon.py
"""

from __future__ import annotations

import base64
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "packaging"
OUT = FOLDER / "OilLevelTracker.ico"
SIZES = (16, 20, 24, 32, 40, 48, 64, 256)  # what Windows asks for, across display scales
SMALL_MAX = 24


def ico(pngs: dict[int, bytes]) -> bytes:
    """An .ico of PNG images, one per size."""
    head = struct.pack("<HHH", 0, 1, len(pngs))
    entries, data = b"", b""
    offset = len(head) + 16 * len(pngs)
    for size, png in sorted(pngs.items()):
        side = 0 if size >= 256 else size  # 0 means 256
        entries += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(png), offset + len(data))
        data += png
    return head + entries + data


def render(svg: Path, size: int, page) -> bytes:
    source = "data:image/svg+xml;base64," + base64.b64encode(svg.read_bytes()).decode()
    page.set_content(f'<body style="margin:0"><img id="i" src="{source}" width="{size}" height="{size}"></body>')
    page.wait_for_function("document.getElementById('i').complete")
    return page.locator("#i").screenshot(omit_background=True)


def main() -> int:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        page = browser.new_page(device_scale_factor=1)
        pngs = {
            size: render(FOLDER / ("app-icon-small.svg" if size <= SMALL_MAX else "app-icon.svg"), size, page)
            for size in SIZES
        }
        browser.close()
    OUT.write_bytes(ico(pngs))
    print(f"{OUT.relative_to(ROOT)}: {', '.join(map(str, SIZES))} px, {OUT.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
