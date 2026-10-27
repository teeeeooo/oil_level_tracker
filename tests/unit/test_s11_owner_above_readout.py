from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from tests.diagnostics import s11_owner_above_readout as oar

RECIPE = Path("sample/sample2.oilrecipe")


def _frame(published, *candidates, reason="FILL_MOTION_OWNER", allowed=("own",), chain=()):
    return dict(time=1.0, frame=30, fill="FILLING_VISIBLE", published_y=published, reason=reason,
                allowed=list(allowed), owner_chain=list(chain),
                candidates=[dict(y=y, tracklet=t, admitted=a) for y, t, a in candidates])


def test_an_admitted_non_owner_more_than_one_step_above_every_owner_row_is_a_hit():
    (hit,) = oar.hits([_frame(700.0, (700.0, "own", True), (690.0, "own", True), (657.0, "other", True))], 32.0)
    assert (hit["owner_top_y"], hit["above"]) == (690.0, [{"y": 657.0, "tracklet": "other", "gap_px": 33.0}])


def test_within_one_step_unadmitted_untracked_or_chain_members_are_not_hits():
    frames = [
        _frame(700.0, (700.0, "own", True), (668.0, "other", True)),  # exactly one step
        _frame(700.0, (700.0, "own", True), (500.0, "other", False)),
        _frame(700.0, (700.0, "own", True), (500.0, "", True)),
        _frame(700.0, (700.0, "own", True), (500.0, "old", True), chain=("old", "own")),
    ]
    assert oar.hits(frames, 32.0) == []


def test_only_published_single_owner_frames_are_read():
    above = ((700.0, "own", True), (500.0, "other", True))
    frames = [
        _frame(None, *above),
        _frame(700.0, *above, reason="FILL_SPAN_CONFIRMED"),
        _frame(700.0, *above, reason="FILL_OWNER_AMBIGUOUS", allowed=()),
        _frame(700.0, (500.0, "other", True)),  # the owner has no observation in the frame
    ]
    assert oar.hits(frames, 32.0) == []
    assert len(oar.hits([_frame(700.0, *above, reason="FILL_OWNER_COLOCATED", allowed=("own", "b"))], 32.0)) == 1


def test_comparison_and_bundle_sources_give_the_same_frames(tmp_path):
    readout = {"reason": "FILL_MOTION_OWNER", "allowed_tracklet_ids": ["own"], "owner_chain": "old;own",
               "oil_candidates": [{"y": 700.0, "sequence_tracklet_id": "own", "sequence_tracklet_admitted": 1.0},
                                  {"y": 600.0, "sequence_tracklet_id": "other", "sequence_tracklet_admitted": 1.0},
                                  {"y": 550.0, "sequence_tracklet_id": None, "sequence_tracklet_admitted": None}]}
    rows = [{"glass_id": "", "frame_index": 30, "timestamp_sec": 1.0, "fill_state": "FILLING_VISIBLE",
             "raw_oil_air_level_y": 700.0}]
    comparison = tmp_path / "comparison.json"
    comparison.write_text(json.dumps({"variants": {"top_exit": {"rows": rows, "owner_readout": [readout]}}}), encoding="utf-8")
    local = oar.from_comparison(comparison, "top_exit")

    bundle = tmp_path / "bundle"
    (bundle / "debug").mkdir(parents=True)
    shutil.copy(RECIPE, bundle / "recipe_snapshot.oilrecipe")
    recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
    glass = recipe["glasses"][0]
    with (bundle / "tracking_data.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerow({**rows[0], "glass_id": glass["id"]})
    sequence = {"state": {"sequence_material_phase_reason": "FILL_MOTION_OWNER",
                          "sequence_material_phase_owner_chain": "old;own",
                          "sequence_material_phase_diagnostics": {"allowed_tracklet_ids": ["own"]}},
                "candidates": [{"kind": "oil_air", "canonical_y": c["y"], "tracklet_id": c["sequence_tracklet_id"],
                                "tracklet_admitted": c["sequence_tracklet_admitted"]}
                               for c in readout["oil_candidates"]] + [{"kind": "foam_front", "canonical_y": 1.0}]}
    record = {"glass_name": glass["name"], "frame_index": 30, "run_id": "r", "sequence": sequence}
    (bundle / "debug" / "debug_trace.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    traced, step, run_ids = oar.from_bundle(bundle, glass["name"], (0.0, 10.0))

    assert traced == local
    assert (step, run_ids) == (float(glass["detector_settings"]["temporal_max_jump_px"]), ["r"])
    assert oar.summary(local, step)["hit_count"] == 1


def test_context_lists_every_admitted_candidate_in_the_window_with_its_owner_role():
    frames = [_frame(700.0, (700.0, "own", True), (690.0, "near", True), (500.0, "x", False), chain=("own",)),
              {**_frame(None, (600.0, "late", True)), "time": 5.0}]
    (row,) = oar.summary(frames, 32.0, (0.0, 2.0))["context"]
    assert row["admitted"] == [(690.0, "near", False), (700.0, "own", True)]
    assert oar.summary(frames, 32.0)["context"] == []
