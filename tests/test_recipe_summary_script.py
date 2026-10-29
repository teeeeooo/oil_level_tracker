import importlib.util
from pathlib import Path

from oil_tracker.adapters.storage.recipe_files import RecipeFolder
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("recipe_summary", ROOT / "scripts" / "recipe_summary.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)


def test_summary_lines(tmp_path, capsys):
    recipe = Recipe(
        "r1", "SPL#4 냉각", ReferenceFrame(1280, 720, "SPL#4.mp4", 12.5, b"jpeg"),
        (Glass("g1", "BASE", Ellipse(640, 360, 80, 200), 380),), "c", "u",
    )
    RecipeFolder(tmp_path).save(recipe)
    (tmp_path / "bad.recipe.json").write_text("{", encoding="utf-8")
    missing = tmp_path / "missing.mp4"
    missing.write_bytes(b"x")
    assert script.main(["--folder", str(tmp_path), "--video", str(missing)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"folder={tmp_path}"
    assert lines[1] == "recipes=1 unreadable=1"
    assert lines[2].startswith('unreadable file="bad.recipe.json"')
    assert lines[3].startswith('recipe name="SPL#4 냉각" file="SPL#4 냉각.recipe.json" bytes=')
    assert lines[3].endswith('frame=1280x720 source="SPL#4.mp4" t=12.500 jpeg=4 glasses=1 problems=0')
    assert lines[4] == (
        '  glass name="BASE" cx=640 cy=360 rx=80 ry=200 zero=380 mode=RECOVERY '
        "limit=120 hold=5 cov=0.7 allowed_sec=5 allowed_px=0"
    )
    assert lines[5].startswith('video name="missing.mp4" error=')
