import json
from dataclasses import replace
from datetime import datetime

import pytest

from oil_tracker.adapters.storage.inspection_files import (
    InspectionFolders,
    UnreadableInspection,
    analysis_from_json,
    analysis_to_json,
    folder_name_for,
    inspection_from_json,
    inspection_to_json,
)
from oil_tracker.adapters.storage.recipe_files import recipe_to_json
from oil_tracker.application.ports import GlassImages, InspectionNotFound, UnreadableAnalysis
from oil_tracker.domain.enums import InspectionState, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import Analysis, AnalysisSettings, GlassDraft, Inspection, SourceVideo
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

RECIPE = Recipe(
    "r1", "2호기 냉각", ReferenceFrame(1280, 720, "SPL#4.mp4", 12.5, b"\xff\xd8jpeg"),
    (Glass("0b7c-base", "BASE", Ellipse(640, 360, 80, 200), 380),), "c", "u",
)
VIDEO = SourceVideo("C:/videos/SPL#4: 냉각.mp4", "SPL#4: 냉각.mp4", 53_165_455, 1280, 720, 30.0, 7800)


def make_inspection(inspection_id="i1", created_at="2026-10-29T05:06:07+00:00") -> Inspection:
    return Inspection(inspection_id, created_at, VIDEO, RECIPE, AnalysisSettings(0.0, 259.9, 31.5))


def make_analysis(glass_id="0b7c-base") -> tuple[Analysis, list[GlassImages]]:
    oil = Line((400.0, None, 402.0), (SampleOrigin.DRAFT,) * 3)
    analysis = Analysis((0.0, 0.5, 1.0), (GlassDraft(glass_id, oil),), "2026-10-29T05:10:00+00:00")
    images = [GlassImages(glass_id, 160, 400, (b"png-a", b"png-b"), (b"bg-a", b"bg-b"))]
    return analysis, images


def test_the_folder_name_is_local_time_and_a_safe_video_name():
    local = datetime.fromisoformat("2026-10-29T05:06:07+00:00").astimezone()
    assert folder_name_for(make_inspection()) == f"{local:%Y%m%d-%H%M}_SPL#4_ 냉각"


def test_create_list_load_and_save(tmp_path):
    folders = InspectionFolders(tmp_path / "Inspections")
    first = folders.create(make_inspection("i1"))
    second = folders.create(make_inspection("i2"))  # same minute, same video
    assert second == first + "_2"
    folders.create(make_inspection("i3", created_at="2026-10-30T00:00:00+00:00"))

    listing = folders.list_inspections()
    assert [entry.inspection.id for entry in listing.inspections] == ["i3", "i1", "i2"]  # newest first
    assert listing.unreadable == ()
    loaded = folders.load("i1")
    assert loaded == make_inspection("i1")
    assert (tmp_path / "Inspections" / first / "recipe.json").read_text(encoding="utf-8") == recipe_to_json(RECIPE)

    moved = replace(RECIPE.glasses[0], ellipse=Ellipse(646, 364, 80, 200))
    folders.save(replace(loaded, recipe=replace(RECIPE, glasses=(moved,)), state=InspectionState.FAILED, failure="x"))
    again = folders.load("i1")
    assert again.recipe.glasses[0].ellipse.center_x == 646  # the copy only
    assert (again.state, again.failure) == (InspectionState.FAILED, "x")
    with pytest.raises(InspectionNotFound):
        folders.load("nope")


def test_unreadable_and_duplicate_folders_are_reported(tmp_path):
    folders = InspectionFolders(tmp_path)
    name = folders.create(make_inspection("i1"))
    (tmp_path / "copy").mkdir()
    for file in ("inspection.json", "recipe.json"):
        (tmp_path / "copy" / file).write_bytes((tmp_path / name / file).read_bytes())
    (tmp_path / "broken").mkdir()
    (tmp_path / "broken" / "inspection.json").write_text("{", encoding="utf-8")
    (tmp_path / "empty").mkdir()
    (tmp_path / ".hidden").mkdir()
    listing = folders.list_inspections()
    assert [entry.folder_name for entry in listing.inspections] == [name]
    reasons = dict(listing.unreadable)
    assert set(reasons) == {"copy", "broken", "empty"}
    assert reasons["copy"] == "다른 폴더와 검사 ID가 같습니다."
    assert reasons["broken"] == "JSON 형식이 아닙니다."


def test_the_formats_refuse_other_files_and_versions():
    recipe = recipe_to_json(RECIPE)
    data = json.loads(inspection_to_json(make_inspection()))
    assert inspection_from_json(json.dumps(data), recipe) == make_inspection()
    for change in ({"format": "x"}, {"schema_version": 2}):
        with pytest.raises(UnreadableInspection):
            inspection_from_json(json.dumps({**data, **change}), recipe)
    with pytest.raises(UnreadableInspection):
        inspection_from_json(json.dumps({**data, "state": "SUBMITTED"}), recipe)
    analysis, images = make_analysis()
    stored = json.loads(analysis_to_json(analysis, images))
    with pytest.raises(UnreadableAnalysis):
        analysis_from_json(json.dumps({**stored, "schema_version": 2}))


def test_the_analysis_is_replaced_as_a_whole(tmp_path):
    folders = InspectionFolders(tmp_path)
    name = folders.create(make_inspection())
    assert folders.load_analysis("i1") is None
    analysis, images = make_analysis()
    folders.save_analysis("i1", analysis, images)
    stored = folders.load_analysis("i1")
    assert stored.analysis == analysis
    assert [(i.glass_id, i.y0, i.rows, i.pieces) for i in stored.images] == [("0b7c-base", 160, 400, 2)]
    assert folders.image_piece("i1", "0b7c-base", "context", 1) == b"png-b"
    assert folders.image_piece("i1", "0b7c-base", "background", 0) == b"bg-a"

    smaller = GlassImages("0b7c-base", 160, 400, (b"new",), (b"new-bg",))
    folders.save_analysis("i1", analysis, [smaller])
    assert folders.load_analysis("i1").images[0].pieces == 1
    with pytest.raises(InspectionNotFound):
        folders.image_piece("i1", "0b7c-base", "context", 1)  # the old piece is gone
    assert sorted(p.name for p in (tmp_path / name).iterdir()) == ["cache", "inspection.json", "recipe.json"]

    folders.clear_analysis("i1")
    assert folders.load_analysis("i1") is None


@pytest.mark.parametrize(("glass_id", "kind", "index"), [("../x", "context", 0), ("0b7c-base", "jpeg", 0), ("0b7c-base", "context", -1)])
def test_image_pieces_are_only_read_from_the_cache(tmp_path, glass_id, kind, index):
    folders = InspectionFolders(tmp_path)
    folders.create(make_inspection())
    folders.save_analysis("i1", *make_analysis())
    with pytest.raises(InspectionNotFound):
        folders.image_piece("i1", glass_id, kind, index)


def test_every_analysed_glass_needs_its_images(tmp_path):
    folders = InspectionFolders(tmp_path)
    folders.create(make_inspection())
    analysis, _ = make_analysis()
    with pytest.raises(ValueError):
        folders.save_analysis("i1", analysis, [])
