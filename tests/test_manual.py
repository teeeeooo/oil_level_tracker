"""The user manual (web/manual/, DESIGN.md §5): every file it uses ships beside it, every figure it
holds is used, and its table of contents leads somewhere."""

import re
from html.parser import HTMLParser
from pathlib import Path

MANUAL = Path(__file__).resolve().parents[1] / "src" / "oil_tracker" / "web" / "manual"


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.files: set[str] = set()
        self.ids: set[str] = set()
        self.anchors: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("src", "href"):
            value = attrs.get(key)
            if not value or value.startswith(("http:", "https:")):
                continue
            if value.startswith("#"):
                self.anchors.append(value[1:])
            else:
                self.files.add(value)


def page() -> Page:
    parsed = Page()
    parsed.feed((MANUAL / "index.html").read_text(encoding="utf-8"))
    return parsed


def test_every_file_the_manual_uses_is_there():
    missing = [name for name in sorted(page().files) if not (MANUAL / name).resolve().is_file()]
    assert missing == []


def test_every_figure_and_clip_is_used():
    used = page().files
    shipped = {f"{folder}/{path.name}" for folder in ("img", "clips") for path in (MANUAL / folder).iterdir()}
    assert shipped - used == set()


def test_every_link_inside_the_manual_has_its_target():
    parsed = page()
    assert parsed.anchors
    assert [anchor for anchor in parsed.anchors if anchor not in parsed.ids] == []


def test_it_works_from_a_file():
    """The page opens from disk in the browser: no module scripts (blocked there), nothing fetched."""
    text = (MANUAL / "index.html").read_text(encoding="utf-8") + (MANUAL / "manual.js").read_text(encoding="utf-8")
    assert 'type="module"' not in text
    assert not re.search(r"\bfetch\(|\bimport\b", text)
