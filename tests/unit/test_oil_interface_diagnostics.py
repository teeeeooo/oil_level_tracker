from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_interface_diagnostics import measure_oil_interfaces
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.session import DebugTraceLevel
from tests.test_oil_detector_integration import glass, oil_frame, uniform_frame


def _measure(gray, candidates=None, *, origin=(0, 0), mask=None, glare=None, material=None):
    return measure_oil_interfaces(
        candidates or [BoundaryCandidate("test", BoundaryKind.OIL_AIR, 100 + origin[1])],
        gray=gray,
        effective_mask=np.ones_like(gray) if mask is None else mask,
        glare_mask=np.zeros_like(gray) if glare is None else glare,
        material_map=np.full(gray.shape, 0.8) if material is None else material,
        static_map=None,
        crop_origin=origin,
        frame_index=27,
    )


def test_two_sided_context_distinguishes_step_from_internal_stripe():
    step = np.full((200, 200), 180, dtype=np.uint8)
    step[100:] = 80
    stripe = np.full_like(step, 180)
    stripe[100:106] = 80
    step.setflags(write=False)
    stripe.setflags(write=False)
    a, b = _measure(step), _measure(stripe)
    assert a["classification"] == b["classification"] == "not_evaluated"
    for actual, internal in zip(a["candidates"][0]["sectors"], b["candidates"][0]["sectors"]):
        assert actual["near_signed_contrast"] == pytest.approx(-100 / 255)
        assert internal["near_signed_contrast"] == pytest.approx(-100 / 255)
        assert actual["far_signed_contrast"] == pytest.approx(-100 / 255)
        assert internal["far_signed_contrast"] == pytest.approx(0)
        assert actual["bands"]["near_above"]["material_mean"] == pytest.approx(0.8)
        assert actual["bands"]["near_above"]["static_overlap"] is None


def test_uniform_and_inverse_polarity_do_not_invent_edge_or_oil_identity():
    uniform = np.full((200, 200), 120, dtype=np.uint8)
    result = _measure(uniform)
    assert all(s["peak_source_y"] is None for s in result["candidates"][0]["sectors"])
    uniform[100:] = 220
    result = _measure(uniform)
    assert result["candidates"][0]["median_near_signed_contrast"] == pytest.approx(100 / 255)


def test_per_sector_peak_keeps_curved_boundary_and_source_offset():
    gray = np.full((200, 200), 180, dtype=np.uint8)
    heights = [98, 99, 100, 101, 102]
    for i, y in enumerate(heights):
        gray[y:, i * 40:(i + 1) * 40] = 80
    result = _measure(gray, origin=(11, 73))
    row = result["candidates"][0]
    assert row["canonical_y"] == 173
    assert row["local_y"] == 100
    for i, sector in enumerate(row["sectors"]):
        assert sector["source_x_range"] == [11 + i * 40, 11 + (i + 1) * 40]
        assert abs(sector["peak_source_y"] - (heights[i] + 73)) <= 1


@pytest.mark.parametrize("missing", ["mask", "glare", "material", "edge"])
def test_missing_or_clipped_evidence_is_explicit_and_finite(missing):
    gray = np.full((200, 200), 120, dtype=np.uint8)
    kwargs = {}
    if missing == "mask": kwargs["mask"] = np.zeros_like(gray)
    if missing == "glare": kwargs["glare"] = np.ones_like(gray)
    if missing == "material": kwargs["material"] = np.full(gray.shape, np.nan)
    if missing == "edge": kwargs["candidates"] = [BoundaryCandidate("test", BoundaryKind.OIL_AIR, 0)]
    result = _measure(gray, **kwargs)
    band = result["candidates"][0]["sectors"][0]["bands"]["near_above"]
    if missing == "material":
        assert band["available"] is True
        assert band["material_mean"] is None
    else:
        assert band["available"] is False
        assert band["gray_mean"] is None
    json.dumps(result, allow_nan=False)


def test_rejected_duplicate_and_outside_candidates_are_not_filtered_or_changed():
    candidates = [
        BoundaryCandidate("same", BoundaryKind.OIL_AIR, 100, rejected=True),
        BoundaryCandidate("same", BoundaryKind.OIL_AIR, 100),
        BoundaryCandidate("foam", BoundaryKind.FOAM_FRONT, 80),
        BoundaryCandidate("outside", BoundaryKind.OIL_AIR, -5),
        BoundaryCandidate("bad", BoundaryKind.OIL_AIR, float("inf")),
    ]
    before = [asdict(c) for c in candidates]
    result = _measure(np.full((200, 200), 100, dtype=np.uint8), candidates)
    assert [r["candidate_input_index"] for r in result["candidates"]] == [0, 1, 3, 4]
    assert result["candidates"][-1]["measurement_status"] == "candidate_outside_raster"
    assert before == [asdict(c) for c in candidates]
    json.dumps(result, allow_nan=False)


def test_debug_measurements_cannot_change_candidates_or_completed_sequence():
    config = glass()
    detectors = [OpenCvPhaseDetector(), OpenCvPhaseDetector()]
    runs = [[], []]
    for i, frame in enumerate([oil_frame(130), oil_frame(128), uniform_frame(135), oil_frame(125)]):
        for j, detector in enumerate(detectors):
            detection, artifacts = detector.detect(frame, config, i, i / 2, debug=bool(j))
            runs[j].append(detection)
            if j:
                assert "oil_interface_diagnostics" in artifacts.state
                assert "oil_interface_diagnostics" not in detection.debug_metrics
    for run_a, run_b in (runs, [d.resolve_sequence(r, config).detections for d, r in zip(detectors, runs)]):
        for a, b in zip(run_a, run_b):
            a, b = asdict(a), asdict(b)
            a.pop("debug_metrics")
            b.pop("debug_metrics")
            assert a == b


@pytest.mark.parametrize("level", [DebugTraceLevel.BASIC, DebugTraceLevel.FULL])
def test_trace_keeps_raw_index_join_after_score_sort_and_sequence_annotation(tmp_path, level):
    config = glass()
    detector = OpenCvPhaseDetector()
    detection, artifacts = detector.detect(oil_frame(130), config, 42, 1.75, debug=True)
    writer = JsonlDebugTraceWriter("r22-1-test", level, staging_parent=tmp_path)
    writer.write(config, detection, artifacts, DebugCaptureDecision(True, (DebugCaptureReason.FIRST_SAMPLE,)))
    writer.annotate_sequence(config, detector.resolve_sequence([detection], config).detections)
    completion = writer.finalize()
    record = json.loads((Path(completion.staging_directory) / "debug_trace.jsonl").read_text(encoding="utf-8"))
    diagnostic = record["state"]["oil_interface_diagnostics"]
    assert diagnostic["source_frame_index"] == record["frame_index"] == 42
    by_index = {c["candidate_input_index"]: c for c in record["candidates"]}
    assert diagnostic["oil_candidate_count"] > 0
    for row in diagnostic["candidates"]:
        original = by_index[row["candidate_input_index"]]
        assert (row["source"], row["canonical_y"]) == (original["source"], original["canonical_y"])
    assert record["sequence"]["state"]["sequence_resolver_version"] == "r22-oil-ownership-evidence-replacement-v1"
