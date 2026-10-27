from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from tests.diagnostics import s11_full_evidence_readout as fer

RECIPE = Path("sample/sample2.oilrecipe")


def _metrics(status="no_interface_accepted", *, absence=0.8, boundary=0.3, full=0.7, empty=0.1, mode="unconstrained",
             resolved="full", **extra):
    return {"oil_decision_status": status, "oil_no_interface_score": absence, "oil_boundary_score": boundary,
            "oil_no_interface_full_likelihood": full, "oil_no_interface_empty_likelihood": empty,
            "sequence_material_phase_diagnostics": {"allowed_mode": mode}, "sequence_resolved_kind": resolved,
            **extra}


def _row(metrics, fill="UNKNOWN_REVIEW", candidates=()):
    return fer.frame_row(1.0, 30, fill, None, metrics, list(candidates))


def test_the_first_failing_gate_is_named():
    assert _row(_metrics("ambiguous", absence=0.5, full=0.0))["gate"] == "gate1:absence_low"
    assert _row(_metrics("ambiguous", absence=0.62, boundary=0.6, full=0.0))["gate"] == "gate1:absence_margin"
    assert _row(_metrics("boundary_accepted", absence=0.0, full=0.0))["gate"] == "gate1:boundary_accepted"
    assert _row(_metrics(full=0.5))["gate"] == "gate2:full_below"
    assert _row(_metrics(mode="hard_gate"))["gate"] == "gate3:hard_gate"
    assert _row(_metrics(mode="owner_bounded", resolved="oil"))["gate"] == "selection:oil"
    assert _row(_metrics(mode="owner_bounded"), fill="FULL_NO_INTERFACE")["gate"] == "selected"


def test_the_full_node_is_the_state_threshold_and_the_full_source_is_named():
    assert _row(_metrics(full=0.58))["full_node"] and not _row(_metrics(full=0.579))["full_node"]
    assert _row(_metrics(), fill="FULL_NO_INTERFACE")["full_source"] == "image_node"
    assert _row(_metrics(mode="state_only", full=0.0), fill="FULL_NO_INTERFACE")["full_source"] == "top_exit"
    assert _row(_metrics())["full_source"] is None


def test_foam_fronts_and_admitted_oil_are_read_from_completed_or_snapshot_candidates():
    completed = [{"kind": "foam_front", "y": 300.0, "features": {"sequence_foam_eligible": 1.0}},
                 {"kind": "foam_front", "y": 320.0, "features": {"sequence_foam_eligible": 0.0}},
                 {"kind": "oil_air", "y": 700.0, "features": {"sequence_tracklet_admitted": 1.0}},
                 {"kind": "oil_air", "y": 710.0, "features": {"sequence_tracklet_admitted": 0.0}}]
    snapshot = [{"kind": "foam_front", "canonical_y": 300.0, "sequence_foam_eligible": 1.0},
                {"kind": "oil_air", "canonical_y": 700.0, "tracklet_admitted": True},
                {"kind": "oil_air", "canonical_y": 710.0, "tracklet_admitted": False}]
    for candidates in (completed, snapshot):
        row = _row(_metrics(), candidates=candidates)
        assert (row["foam_fronts"], row["admitted_oil"]) == ([300.0], [700.0])


def test_summary_counts_gates_and_sustained_full_node_runs():
    rows = [_row(_metrics(full=f), candidates=[{"kind": "foam_front", "y": 5.0,
                                                 "features": {"sequence_foam_eligible": 1.0}}] if i == 5 else [])
            for i, f in enumerate([0.7, 0.7, 0.0, 0.7, 0.7, 0.7, 0.1])]
    for index, row in enumerate(rows):
        row["time"] = index * 0.5
    s = fer.summary(rows)
    assert (s["rows"], s["full_node"]) == (7, 5)
    assert s["longest_run"] == {"start": 1.5, "length": 3}
    assert s["sustained_runs"] == [{"start": 1.5, "length": 3, "foam_in_run": True}]
    assert s["gate"] == {"gate2:full_below": 2, "selected": 5}


def test_bundle_source_merges_frame_metrics_and_the_sequence_snapshot(tmp_path):
    bundle = tmp_path / "bundle"
    (bundle / "debug").mkdir(parents=True)
    shutil.copy(RECIPE, bundle / "recipe_snapshot.oilrecipe")
    glass = json.loads(RECIPE.read_text(encoding="utf-8"))["glasses"][0]
    with (bundle / "tracking_data.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["glass_id", "frame_index", "timestamp_sec", "fill_state",
                                                    "raw_oil_air_level_y"])
        writer.writeheader()
        writer.writerows([{"glass_id": glass["id"], "frame_index": f, "timestamp_sec": f / 30,
                           "fill_state": "UNKNOWN_REVIEW", "raw_oil_air_level_y": ""} for f in (0, 15, 30)])
    metrics = _metrics(mode="hard_gate")
    frame_metrics = {k: v for k, v in metrics.items() if k.startswith("oil_")}
    sequence_metrics = {k: v for k, v in metrics.items() if k.startswith("sequence_")}
    records = [{"glass_name": glass["name"], "frame_index": f, "run_id": "r", "state": frame_metrics,
                "sequence": {"state": sequence_metrics,
                             "candidates": [{"kind": "oil_air", "canonical_y": 700.0, "tracklet_admitted": True}]}}
               for f in (0, 15, 30)]
    (bundle / "debug" / "debug_trace.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    rows, run_ids = fer.from_bundle(bundle, glass["name"], (0.4, 1.0))
    assert ([r["frame"] for r in rows], run_ids) == ([15, 30], ["r"])
    assert (rows[0]["time"], rows[0]["gate"], rows[0]["published_y"], rows[0]["admitted_oil"]) == (
        0.5, "gate3:hard_gate", None, [700.0])


def test_printing_lists_the_summary_and_every_frame(capsys):
    rows = [_row(_metrics())]
    fer.print_result("x", {"summary": fer.summary(rows), "frames": rows}, frame_lines=True)
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("full evidence readout x | rows 1 | full node 1 | longest run 1 from 1.000 | runs >= 3: 0")
    assert out[2] == "gate selected=1"
    assert out[-1].startswith("1.000 | UNKNOWN_REVIEW | - | no_interface_accepted | 0.8 | 0.3 | 0.5 |")
