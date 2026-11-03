import base64
import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("make_manual_file", ROOT / "scripts" / "make_manual_file.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)


@pytest.fixture(scope="module")
def page():
    return script.single_file()


def test_the_manual_file_loads_nothing_from_beside_it(page):
    original = (script.MANUAL / "index.html").read_text(encoding="utf-8")
    assert script.OUTSIDE.search(page) is None
    assert "<link" not in page and "--brand:" in page and ".toc a.on" in page  # tokens.css and manual.css
    # every figure and clip is still there, as data
    assert len(re.findall(r"<img ", page)) == len(re.findall(r"<img ", original))
    assert len(re.findall(r'src="data:image/webp;base64,', page)) == len(re.findall(r'src="img/', original))
    assert len(re.findall(r'src="data:video/mp4;base64,', page)) == len(re.findall(r'src="clips/', original))


def test_the_figures_are_the_shipped_bytes(page):
    found = re.search(r'<img src="data:image/webp;base64,([^"]+)" alt="[^"]*"', page)
    first = re.search(r'<img src="(img/[^"]+)"', (script.MANUAL / "index.html").read_text(encoding="utf-8"))[1]
    assert base64.b64decode(found[1]) == (script.MANUAL / first).read_bytes()


def test_the_script_runs_after_the_page(page):
    # it ran deferred from its file; inline, it must come after the elements it wires
    script_at = page.index("<script>\n")
    assert page.index('<dialog id="zoom"') < script_at < page.index("</body>")
    assert "manual.js" not in page


def test_it_writes_the_versioned_file(tmp_path, capsys):
    assert script.main(["--out", str(tmp_path)]) == 0
    target = tmp_path / f"OilLevelTracker-{script.version()}-사용설명서.html"
    assert target.is_file() and f"manual={target}" in capsys.readouterr().out
