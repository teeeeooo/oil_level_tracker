"""web/tokens.css is a copy of the DESIGN.md §2 tokens."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def design_tokens() -> dict[str, str]:
    text = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
    section = text.split("## 2. Color Palette & Roles", 1)[1].split("## 3.", 1)[0]
    tokens: dict[str, str] = {}
    for row in re.finditer(r"^\| `(--[a-z0-9-]+)` \| ([^|]+)\| ([^|]+)\|", section, re.MULTILINE):
        name, first, second = row.group(1), row.group(2).strip(), row.group(3).strip()
        tokens[name] = first.strip("`")
        if second.startswith("`#"):  # §2.4: text colour, then background
            tokens[name + "-bg"] = second.strip("`")
    return tokens


def css_tokens() -> dict[str, str]:
    text = (ROOT / "src" / "oil_tracker" / "web" / "tokens.css").read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[a-z0-9-]+):\s*([^;]+);", text)}


def test_every_design_colour_is_copied_exactly():
    design, css = design_tokens(), css_tokens()
    assert len(design) > 40
    assert {name: css.get(name) for name in design} == design


def test_tokens_css_adds_only_the_font_stacks():
    assert set(css_tokens()) - set(design_tokens()) == {"--font", "--mono"}
