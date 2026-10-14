"""Protect append-only evidence, coordinate mapping and contact-type coverage."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tests.diagnostics import s11_native_role_extension as extension
from tests.unit.test_s11_native_role_corpus import contact, row


def liquid_row(sid, source, relation, frame=1):
    r = row(sid, source, frame=frame, role="LIQUID_UPPER", semantic=False)
    r["original_interpretations"] = [relation]
    return r


def test_contact_types_keep_recordings_together_and_disjunction_out():
    foam = "FOAM_LOWER_LIQUID_INTERFACE"
    air = "LIQUID_AIR_INTERFACE"
    rows = [liquid_row("miso", "miso", foam), liquid_row("sample4", "sample4", foam),
            liquid_row("water-a", "water", air), liquid_row("water-c", "water", air, frame=2)]
    ambiguous = row("N1", "water")
    ambiguous["original_interpretations"] = ["EXTERNAL_FOAM_UPPER", "OSCILLATING_LIQUID_UPPER"]
    rows.append(ambiguous)
    result = extension.contact_coverage(rows)
    assert result[foam]["disjoint_positive_sources_available"]
    assert not result[air]["disjoint_positive_sources_available"]
    held = next(f for f in result[air]["held_source_coverage"] if f["held_source"] == "water")
    assert held["fit_positive_sources"] == []
    assert held["held_positive_paths"] == ["water-a", "water-c"]


def test_native_population_keeps_unknowns_and_maps_original_pixels():
    rgb = np.arange(40*40*3, dtype=np.uint8).reshape(40, 40, 3)
    packet = dict(source_recording=dict(path="test.mp4", sha256="source"), frame=1,
        geometry=dict(origin=[100, 200], shape=[20, 20], scale_xy=[1, 1]), fragments=[
            dict(id="case/one", fragment_id=1, source_path_xy=[[110, 210]], context_support=dict(
                status="AVAILABLE_PARTIAL_CONTEXT", sides={
                    "upper": {"complete_centers_xy": [[10, 5]]},
                    "lower": {"complete_centers_xy": [[10, 15]]}})),
            dict(id="case/two", fragment_id=2, source_path_xy=[[111, 211]],
                 context_support={"status": "UNRESOLVED_PATH_ORIENTATION"})])
    view = dict(source={"path": "source.png"}, image_origin_xy=[95, 195])
    rows, frames = extension.population(packet, view, rgb, {"sha256": "readout"})
    assert len(rows) == 2 and rows[1]["native_sides"] == {}
    assert all(r["review_state"] == "UNREVIEWED" and r["support"] == {} for r in rows)
    upper = rows[0]["native_sides"]["upper"]
    expected = np.ascontiguousarray(rgb[7:14, 12:19].transpose(2, 0, 1)[None])
    assert upper["centers_image_xy"] == [[15, 10]]
    assert upper["uint8_sha256"] == extension.old.array_hash(expected)
    assert frames["source:1"]["roi_sha256"] == extension.old.array_hash(rgb[5:25, 5:25])


def test_join_retains_old_rows_and_never_fills_unknown_or_missing_semantics():
    base_row = liquid_row("old", "old", "LIQUID_AIR_INTERFACE")
    base = dict(rows=[base_row], frames={"old:1": {}})
    known, unknown = row("new", "new", semantic=False), row("other", "new", semantic=False)
    known["original_interpretations"] = unknown["original_interpretations"] = []
    original = deepcopy(base)
    qualified = contact(known)
    qualified["allowed_interpretations"] = ["FOAM_LOWER_LIQUID_INTERFACE"]
    result = extension.join(base, [known, unknown], {"new:1": {}}, {"subjects": [qualified]}, {})
    assert base == original and known["review_state"] == "UNREVIEWED"
    assert result["counts"]["qualified"] == 2 and result["counts"]["unknown"] == 1
    assert result["added_rows"][0]["targets"]["values"] == {"FOAM_UPPER": None, "LIQUID_UPPER": 1}
    assert all(r["support"] == {} for r in result["added_rows"])
    assert result["added_rows"][1]["targets"]["values"] == {"FOAM_UPPER": None, "LIQUID_UPPER": None}
    assert not any(f["training_executed"] for f in result["native_input_coverage"]["source_group_folds"])


@pytest.mark.parametrize("fault", ["frame", "identity", "old_reply"])
def test_join_rejects_duplicate_frame_or_path_and_cannot_edit_base(fault):
    old = row("old", "old")
    base = dict(rows=[old], frames={"old:1": {}})
    added, frames = [row("new", "new")], {"new:1": {}}
    if fault == "frame": frames = {"old:1": {}}
    if fault == "identity": added = [deepcopy(old)]
    subjects = [contact(old)] if fault == "old_reply" else []
    before = deepcopy(base)
    with pytest.raises(ValueError):
        extension.join(base, added, frames, {"subjects": subjects}, {})
    assert base == before


def test_cli_foreign_cwd_preserves_existing_unicode_output(tmp_path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    output = tmp_path / "검증 결과.json"
    output.write_bytes(b"preserve")
    result = subprocess.run([sys.executable, "-B", str(Path(extension.__file__).resolve()),
        "--plan", "missing.json", "--output", str(output)], cwd=tmp_path,
        env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert result.returncode != 0 and "refuse overwrite" in result.stderr
    assert output.read_bytes() == b"preserve"
