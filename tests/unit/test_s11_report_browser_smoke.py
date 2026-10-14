"""Rendered-frame regression controls; existing Mac Chrome only, no installation."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tests/diagnostics/s11_report_browser_smoke.mjs"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(
    not CHROME.is_file() or NODE is None,
    reason="Requires existing Mac Chrome and Node; not a Windows qualification",
)


def synthetic_report(directory: Path, fault: str = "none") -> Path:
    """Real product control code with synthetic frame pixels, never human truth."""
    directory.mkdir(parents=True)
    image = Image.new("RGB", (181 * 4, 4))
    for index in range(181):
        image.paste((index, (17 * index) % 256, (71 * index + 23) % 256),
                    (4 * index, 0, 4 * index + 4, 4))
    image.save(directory / "sprite.png")
    frames = [{"status": "AVAILABLE", "frame_index": 1200 + i,
               "requested_time_sec": 40 + i / 30, "actual_time_sec": 40 + i / 30,
               "page_path": "sprite.png", "tile_xy": [4 * i, 0]}
              for i in range(181)]
    data = json.dumps({"frames": frames, "tile_size": 4})
    card = ('<article class="source-sequence"><canvas width="192" height="192" hidden '
            'style="width:192px;height:192px;background:#111"></canvas>'
            '<div class="sequence-controls" hidden><button data-step="-1">prev</button>'
            '<button data-step="1">next</button><input type="range" min="0" max="180" value="0">'
            '<p class="sequence-time"></p></div><script class="sequence-data" '
            'type="application/json">' + data + '</script></article>')
    script = (ROOT / "src/oil_tracker/adapters/reporting/templates/source_sequences.js.j2").read_text()
    draw = ('ctx.drawImage(image, frame.tile_xy[0], frame.tile_xy[1], data.tile_size, data.tile_size,\n'
            '                      0, 0, canvas.width, canvas.height);')
    assert script.count(draw) == 1
    if fault == "stale":
        script = script.replace(draw, 'ctx.drawImage(image, 0, 0, data.tile_size, data.tile_size,\n'
                               '                      0, 0, canvas.width, canvas.height);')
    elif fault == "blank":
        script = script.replace(draw, 'void image; // fault: labels advance, no canvas draw')
    elif fault not in {"none", "styled"}:
        raise ValueError("unknown synthetic fault")
    if fault == "styled":
        card = card.replace('width:192px;height:192px', 'width:360px;height:360px')
        card = '<div style="padding-top:18.40625px">' + card + '</div>'
    report = directory / "report.html"
    report.write_text('<!doctype html><meta charset="utf-8">' + card * 3 + script)
    return report


@pytest.mark.parametrize("fault", ["none", "stale", "blank", "styled"])
def test_browser_checks_rendered_frame_not_only_label(tmp_path, fault):
    report = synthetic_report(tmp_path / "report", fault)
    original = report.read_bytes()
    output = tmp_path / "output"
    output.mkdir()
    completed = subprocess.run([NODE, str(SCRIPT), str(report), str(output)],
                               capture_output=True, text=True, timeout=90)
    message = completed.stdout + completed.stderr
    assert report.read_bytes() == original
    assert not list(output.glob("chrome-profile-*")), message
    if fault in {"none", "styled"}:
        assert completed.returncode == 0, message
        result = json.loads((output / "browser.json").read_text())
        assert len(result["canvas_checks"]) == 8
        assert all(c["equal"] and c["pixels_restored"] and
                   c["observed_png_sha256"] == c["reference_png_sha256"] == c["restored_png_sha256"]
                   for c in result["canvas_checks"])
        assert result["human_comprehension"] == "NOT_EVALUATED"
        assert result["original_report_changed"] is False
    else:
        assert completed.returncode != 0, "A stale/blank canvas was incorrectly accepted"
        assert "Canvas pixel mismatch" in message
        assert not (output / "browser.json").exists()
