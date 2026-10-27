from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from tests.diagnostics import s11_partition_contradiction_readout as fpc

RECIPE = Path("sample/sample2.oilrecipe")


def _oil(y, *, initial=2, post=1, opposition=0.8, texture=0.7, ordered_lower=0.0, identity="continuation_only",
         penalties=None, **features):
    return {"kind": "oil_air", "canonical_y": y, "feature_score": 0.5, "penalties": penalties or {},
            "features": {"sequence_initial_authority_tier": initial, "sequence_post_track_authority_tier": post,
                         "sequence_track_opposition": opposition, "material_texture_conflict": texture,
                         "sequence_ordered_lower": ordered_lower, "sequence_phase_identity": identity, **features}}


def _foam(y, eligible=1.0):
    return {"kind": "foam_front", "canonical_y": y, "features": {"sequence_foam_eligible": eligible}}


def test_only_eligible_rows_demoted_after_tracking_are_read():
    frame = fpc.frame_rows(1.0, 30, [
        _oil(500.0),
        _oil(510.0, initial=1),  # never eligible
        _oil(520.0, post=2),  # not demoted
        _oil(530.0, opposition=0.5),  # below the reject opposition
        _foam(400.0),
    ])
    assert [row["y"] for row in frame["demoted"]] == [500.0]


def test_texture_only_needs_texture_and_no_other_contradiction():
    rows = fpc.frame_rows(1.0, 30, [
        _oil(500.0),
        _oil(510.0, texture=0.5),
        _oil(520.0, identity="opposed_material"),
        _oil(530.0, penalties={"optics_conflict": 0.5}),
    ])["demoted"]
    assert [(row["y"], row["texture_only"]) for row in rows] == [
        (500.0, True), (510.0, False), (520.0, False), (530.0, False)]
    assert rows[3]["optics"] == 0.5


def test_scope_a_is_the_ordered_lower_flag_and_scope_b_an_eligible_foam_front_above():
    rows = fpc.frame_rows(1.0, 30, [
        _oil(500.0, ordered_lower=1.0),
        _oil(450.0),
        _oil(600.0, texture=0.5, ordered_lower=1.0),  # not texture-only: neither scope
        _foam(470.0), _foam(300.0, eligible=0.0),
    ])["demoted"]
    by_y = {row["y"]: row for row in rows}
    assert (by_y[500.0]["scope_a"], by_y[500.0]["scope_b"], by_y[500.0]["foam_above"]) == (True, True, 470.0)
    assert (by_y[450.0]["scope_a"], by_y[450.0]["scope_b"], by_y[450.0]["foam_above"]) == (False, False, None)
    assert (by_y[600.0]["scope_a"], by_y[600.0]["scope_b"]) == (False, False)


def test_structural_partition_peers_are_material_paths_with_terminal_support_and_separation():
    peer = _oil(700.0, initial=3, post=3, opposition=0.0, texture=0.1, material_path=1.0,
                material_terminal_partition_support=0.9, sequence_tracklet_id="t")
    near = _oil(505.0, initial=3, post=3, opposition=0.0, texture=0.1, material_path=1.0,
                material_terminal_partition_support=0.9)
    layered = _oil(800.0, initial=3, post=3, opposition=0.0, texture=0.1, material_path=1.0,
                   material_terminal_partition_support=0.9, sequence_material_layer_topology=0.6)
    (row,) = fpc.frame_rows(1.0, 30, [_oil(500.0), peer, near, layered])["demoted"]
    assert row["peers"] == [(700.0, "t")]


def test_summary_counts_rows_and_frames():
    frames = [fpc.frame_rows(0.0, 0, [_oil(500.0, ordered_lower=1.0), _foam(400.0)]),
              fpc.frame_rows(0.5, 15, [_oil(500.0), _oil(510.0, texture=0.2)])]
    assert fpc.summary(frames) == {"frames": 2, "demoted": 3, "texture_only": 2, "scope_a": 1, "scope_b": 1,
                                   "frames_with_scope_a": 1, "frames_with_scope_b": 1}


def test_bundle_source_reads_the_window_from_the_trace(tmp_path):
    bundle = tmp_path / "bundle"
    (bundle / "debug").mkdir(parents=True)
    shutil.copy(RECIPE, bundle / "recipe_snapshot.oilrecipe")
    glass = json.loads(RECIPE.read_text(encoding="utf-8"))["glasses"][0]
    with (bundle / "tracking_data.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["glass_id", "frame_index", "timestamp_sec"])
        writer.writeheader()
        writer.writerows([{"glass_id": glass["id"], "frame_index": f, "timestamp_sec": f / 30} for f in (0, 15, 30)])
    records = [{"glass_name": glass["name"], "frame_index": f, "run_id": "r", "candidates": [_oil(500.0)]}
               for f in (0, 15, 30)]
    (bundle / "debug" / "debug_trace.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    frames, run_ids = fpc.from_bundle(bundle, glass["name"], (0.4, 1.0))
    assert ([f["frame"] for f in frames], run_ids) == ([15, 30], ["r"])
    assert frames[0]["time"] == 0.5 and frames[0]["demoted"][0]["texture_only"]


def test_printing_lists_frames_and_the_rows_near_each_mark(capsys):
    frames = [fpc.frame_rows(0.0, 0, [_oil(500.0, ordered_lower=1.0), _oil(600.0), _foam(450.0)])]
    for frame in frames:
        frame["time"] = 1.0
    result = {"summary": fpc.summary(frames), "frames": frames}
    fpc.print_result("x", result, marks=fpc.parse_marks("1.0:505,3.0:500"), near=10.0, frame_lines=True)
    out = capsys.readouterr().out.splitlines()
    assert "1.000 | 2 | 2 | 450 | 500 | 500;600" in out
    assert any(line.startswith("1.000 | 505.0 | 500.0 |") for line in out)
    assert "3.000 | 500.0 | no frame" in out
    assert not any(line.startswith("1.000 | 505.0 | 600.0") for line in out)
