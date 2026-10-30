import hashlib
import importlib.util
import os
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from oil_tracker.adapters.storage.inspection_files import InspectionFolders
from oil_tracker.adapters.storage.recipe_files import RecipeFolder
from oil_tracker.application.ports import GlassImages
from oil_tracker.domain.edits import Decision, Edits, GlassEdits, Memo, Stretch, empty_line
from oil_tracker.domain.enums import InspectionState, SampleOrigin, Verdict
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import Analysis, AnalysisSettings, GlassDraft, Inspection, ReportHeader, SourceVideo
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame
from oil_tracker.domain.version import GlassVerdict, Version

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("inspection_summary", ROOT / "scripts" / "inspection_summary.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)

RECIPE = Recipe(
    "r1", "SPL#4 냉각", ReferenceFrame(1920, 1080, "SPL#4.mp4", 0.0, b"jpeg"),
    (Glass("g-base", "BASE", Ellipse(640, 360, 80, 200), 380), Glass("g-acc", "Accum", Ellipse(900, 400, 60, 120), 420)),
    "2026-10-29T01:00:00+00:00", "2026-10-29T02:00:00+00:00",
)
CREATED = "2026-10-29T05:00:00+00:00"


def test_summary_lines(tmp_path, capsys):
    RecipeFolder(tmp_path / "Recipes").save(RECIPE)
    video = tmp_path / "SPL#4.mp4"
    video.write_bytes(b"video bytes")
    source = SourceVideo(str(video), video.name, 11, 1920, 1080, 30.0, 7800, hashlib.sha256(b"video bytes").hexdigest())
    moved = replace(RECIPE.glasses[1], ellipse=Ellipse(901, 400, 60, 120), zero_line_y=418)
    copy = replace(RECIPE, glasses=(RECIPE.glasses[0], moved))
    folders = InspectionFolders(tmp_path / "Inspections")

    analysed = Inspection("i1", CREATED, source, copy, AnalysisSettings(0.0, 260.0, 12.3), InspectionState.ANALYSED, name="1차 냉각",
                          header=ReportHeader("GB-2", None))
    name = folders.create(analysed)
    oil = Line((400.0, None, None, 402.0), (SampleOrigin.DRAFT,) * 4)
    analysis = Analysis((0.0, 0.5, 1.0, 1.5), (GlassDraft("g-base", oil), GlassDraft("g-acc", oil)), "2026-10-29T05:00:52+00:00")
    folders.save_analysis("i1", analysis, [
        GlassImages("g-base", 160, 400, (b"a", b"b"), (b"c", b"d")),
        GlassImages("g-acc", 280, 240, (b"e",), (b"f",)),
    ])
    (tmp_path / "Inspections" / name / "cache" / "g-base" / "background-001.png").unlink()
    written = datetime.fromisoformat(CREATED).timestamp() + 52.4
    os.utime(tmp_path / "Inspections" / name / "cache" / "analysis.json", (written, written))
    D, E, W = SampleOrigin.DRAFT, SampleOrigin.EDITED, SampleOrigin.DRAWN
    edited = GlassEdits("g-base", Line((400.0, None, 401.0, 402.0), (D, E, W, W)), empty_line(4),
                        Line((380.0,) * 4, (W,) * 4), (Stretch(1.4, 1.6),), (Memo("m1", 0.5, None, "거품"),),
                        Decision(Verdict.FAIL, "거품이 가림", "2026-10-29T05:09:00+00:00"))
    edits = Edits(analysis.times, (edited, GlassEdits("g-acc", oil, empty_line(4), empty_line(4))), 20.5)
    checked = "2026-10-29T05:09:00+00:00"
    version = Version(1, "2026-10-29T05:09:30+00:00", (
        GlassVerdict("g-base", Verdict.FAIL, Verdict.PASS, "자동", Verdict.FAIL, "거품이 가림", checked),
        GlassVerdict("g-acc", Verdict.REVIEW, Verdict.REVIEW, "자동", None, "", checked),
    ))
    folders.submit(analysed, edits, version, "<html>12345</html>")
    folders.save_edits("i1", edits, "2026-10-29T05:10:00+00:00")  # v2 being edited

    later = replace(analysed, id="i2", name=None, created_at="2026-10-29T06:00:00+00:00", recipe=replace(copy, id="gone"),
                    settings=AnalysisSettings(10.0, 20.0), state=InspectionState.NOT_ANALYSED)
    folders.create(later)
    (tmp_path / "Inspections" / "broken").mkdir()

    assert script.main(["--data", str(tmp_path)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"folder={tmp_path / 'Inspections'}"
    assert lines[1] == "inspections=2 unreadable=1"
    assert lines[2].startswith('unreadable folder="broken" reason=')
    assert lines[3] == (
        'inspection folder="1차 냉각" name="1차 냉각" state=ANALYSED failure="" video="SPL#4.mp4" bytes=11 frames=7800 fps=30.000 '
        f'range=0.0-260.0 compressor=12.3 recipe="SPL#4 냉각" created_at={CREATED} '
        "recipe_updated_at=2026-10-29T02:00:00+00:00"
    )
    assert lines.pop(4) == '  header compressor_model="GB-2" test_type=""'
    assert lines[4] == '  glass name="BASE" cx=640 cy=360 rx=80 ry=200 zero=380 mode=RECOVERY recipe_diff="none"'
    assert lines[5] == '  glass name="Accum" cx=901 cy=400 rx=60 ry=120 zero=418 mode=RECOVERY recipe_diff="cx +1 zero -2"'
    assert lines[6] == (
        "  analysis finished_at=2026-10-29T05:00:52+00:00 seconds=52 cache_written=52.4 times=4 partial=no "
        f"sha256={source.sha256[:12]} sha256_check=same"
    )
    assert lines[7] == '  cache glass name="BASE" y0=160 rows=400 pieces=2 files=3/4 empty=50.0%'
    assert lines[8] == '  cache glass name="Accum" y0=280 rows=240 pieces=1 files=2/2 empty=50.0%'
    assert lines.pop(9) == "  version v=1 submitted_at=2026-10-29T05:09:30+00:00 report_bytes=18"
    assert lines.pop(9) == ('  version glass name="BASE" verdict=FAIL computed=PASS override=FAIL reason_chars=6 '
                            f"checked_at={checked}")
    assert lines.pop(9) == f'  version glass name="Accum" verdict=REVIEW computed=REVIEW override=- reason_chars=0 checked_at={checked}'
    assert lines[9] == "  edits saved_at=2026-10-29T05:10:00+00:00 times=4 compressor=20.5"
    assert lines[10] == ('  edits glass name="BASE" oil=1/1/2/1 foam=4/0/0/4 reference=0/0/4/0 '
                         "cannot_judge=1 empty=1 cannot=1 valid=50.0% memos=1 override=FAIL reason_chars=6 checked=yes")  # 1.5 s is "cannot judge"
    assert lines[11] == ('  edits glass name="Accum" oil=4/0/0/2 foam=4/0/0/4 reference=4/0/0/4 '
                         "cannot_judge=0 empty=2 cannot=0 valid=50.0% memos=0 override=- reason_chars=0 checked=no")
    assert ' name="" state=NOT_ANALYSED ' in lines[12]
    assert lines[12].endswith('compressor=- recipe="SPL#4 냉각" created_at=2026-10-29T06:00:00+00:00 recipe_updated_at=-')
    assert lines.pop(13) == '  header compressor_model="GB-2" test_type=""'  # copied from the first
    assert lines[13].endswith('recipe_diff="recipe_missing"')
    assert lines[15] == "  analysis none partial=no"
