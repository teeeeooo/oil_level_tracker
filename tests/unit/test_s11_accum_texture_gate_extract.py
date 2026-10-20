from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidenceIndex
from oil_tracker.adapters.vision.oil_observation_resolver import OilObservationResolver
from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import DebugTraceLevel
from tests.diagnostics import s11_accum_texture_gate_extract as extract
from tests.unit.test_oil_observation_resolver import (
    _calibrated_candidate,
    _detection,
    _foam_candidate,
    _material_candidate,
    _with_artifact_calibration,
)


def _candidate(source, y, *, conflict, material_path=False):
    features = {
        "sequence_eligible": 1.0,
        "boundary_likelihood": 0.8,
        "artifact_likelihood": 0.1,
        "narrow_horizontal_coverage": 0.8,
        "raw_material_row_support": 0.9,
        "material_texture_conflict": conflict,
        "material_terminal_partition_support": 1.0,
        "material_texture_evidence_available": 1.0,
    }
    if material_path:
        features["material_path"] = 1.0
    return BoundaryCandidate(source, BoundaryKind.OIL_AIR, y, features=features, feature_score=0.8)


def _classify(candidate, peers):
    oil = (candidate, *peers)
    index = OilCandidateEvidenceIndex()
    for item in oil:
        index.register(item)
    glass = InspectionRecipe.default_glass(320, 240, 1)
    counts, texture_only = extract.peer_reasons(candidate, oil, glass, index)
    return counts, extract.support_without_texture(candidate, oil, glass, index, texture_only)


SEQ = {"ordered_lower": 1.0, "phase_identity": "continuation_only",
       "phase_identity_failed_gates": "ordered_lower_cross_representation"}


def test_texture_excluded_peer_is_tex0_and_counterfactual_restores_support():
    candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75)
    peer = _candidate("material_path", 834.0, conflict=0.75, material_path=True)
    counts, counterfactual = _classify(candidate, (peer,))
    assert counts == {"tex": 1}
    assert counterfactual >= extract.CROSS_MIN
    assert extract.pattern(SEQ, counts, counterfactual) == "TEX0"


def test_missing_or_same_family_peer_is_nopeer_and_other_gates_stay_separate():
    candidate = _candidate("phase_transition_scan", 833.0, conflict=0.75)
    same = _candidate("other_scan", 834.0, conflict=0.2)
    far = _candidate("material_path", 900.0, conflict=0.2, material_path=True)
    counts, counterfactual = _classify(candidate, (same, far))
    assert counts == {"same": 1}
    assert extract.pattern(SEQ, counts, counterfactual) == "NOPEER"
    other = dict(SEQ, phase_identity_failed_gates="boundary;ordered_lower_cross_representation")
    assert extract.pattern(other, {"tex": 1}, 0.5) == "GATE_OTHER"
    assert extract.pattern(dict(SEQ, ordered_lower=0.0), {"tex": 1}, 0.5) == "-"


def _real_trace(tmp_path):
    """Real resolver output serialized by the real trace writer."""
    detections = tuple(
        _detection(
            index,
            *((_foam_candidate(218.0),) if index == 0 else ()),
            _material_candidate(218.0 + min(index, 3)),
            _material_candidate(450.0 + (index % 2), material_texture_conflict=0.75, terminal_support=1.0),
            _calibrated_candidate(450.0 + (index % 2), motion=0.05, motion_coverage=0.0),
            ambiguity=0.20,
        )
        for index in range(8)
    )
    glass = _with_artifact_calibration()
    glass.id = "glass-1"
    resolved = OilObservationResolver().resolve(detections, glass).detections
    writer = JsonlDebugTraceWriter("run-1", DebugTraceLevel.BASIC, staging_parent=tmp_path)
    decision = DebugCaptureDecision(True, (DebugCaptureReason.FOAM,))
    for detection in detections:
        writer.write(glass, detection, SimpleNamespace(images={}, state={}), decision)
    writer.annotate_sequence(glass, resolved)
    staging = Path(writer.finalize().staging_directory)
    return glass, staging


def test_saved_writer_records_recompute_stored_support_exactly(tmp_path):
    glass, staging = _real_trace(tmp_path)
    lines = (staging / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()
    frames = [extract.analyze(json.loads(line), glass) for line in lines]
    assert all(frame["sequence"] for frame in frames)
    assert sum(frame["check_total"] for frame in frames) > 0
    assert all(frame["check_ok"] == frame["check_total"] for frame in frames)
    assert any(row.get("conflict") == 0.75 for frame in frames for row in frame["rows"])
    assert all(isinstance(row.get("idx"), int) for frame in frames for row in frame["rows"])


def test_report_prints_short_tables_and_marks_uncaptured_targets(tmp_path, capsys):
    glass, staging = _real_trace(tmp_path)
    index = json.loads((staging / "debug_index.json").read_text(encoding="utf-8"))
    summaries = [SimpleNamespace(**{key: item[key] for key in ("record_id", "timestamp_sec", "byte_offset", "byte_length")})
                 for item in index["records"]]
    bundle = SimpleNamespace(root=staging, debug_trace_path="debug_trace.jsonl", run_id="run-1",
                             debug_trace_level="basic")
    extract.SUMMARY = (0.0, 4.0)
    try:
        extract.report(bundle, summaries, glass, (0.0, 1.0, 50.0))
    finally:
        extract.SUMMARY = (671.0, 681.0)
    out = capsys.readouterr().out
    assert "[A]" in out and "[B]" in out and "[C]" in out
    assert "NOT_CAPTURED" in out
    assert "recompute_mismatch=0" in out
    assert len(out.splitlines()) < 40


def test_requested_rows_include_top_k_pruned_candidates(tmp_path, capsys, monkeypatch):
    original = _with_artifact_calibration

    def narrow_glass():
        glass = original()
        glass.detector_settings.candidate_top_k = 1
        return glass

    monkeypatch.setitem(globals(), "_with_artifact_calibration", narrow_glass)
    glass, staging = _real_trace(tmp_path)
    index = json.loads((staging / "debug_index.json").read_text(encoding="utf-8"))
    summaries = [SimpleNamespace(**{key: item[key] for key in
                                    ("record_id", "timestamp_sec", "byte_offset", "byte_length", "frame_index")})
                 for item in index["records"]]
    bundle = SimpleNamespace(root=staging, debug_trace_path="debug_trace.jsonl", run_id="run-1",
                             debug_trace_level="basic")
    assert extract.parse_rows("0:1,2,3; 99:1") == {0: {1, 2, 3}, 99: {1}}
    extract.report_requested(bundle, summaries, glass, {0: {1, 2, 3}, 99: {1}})
    lines = capsys.readouterr().out.splitlines()
    assert any(" | 1 | " in line and "| N |" in line and line.endswith("NOT_TOPK") for line in lines)
    assert any(" | 3 | " in line and "| Y |" in line for line in lines)
    assert "f99 | NOT_CAPTURED" in lines
