from __future__ import annotations

import csv
from dataclasses import replace
from types import SimpleNamespace

import pytest

from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detection_processing import tracking_sample_from_detection
from oil_tracker.domain.enums import FillState, InitialObservationState
from tests.fixtures.synthetic import glass_config
from tests.unit.test_oil_observation_resolver import _candidate, _detection


def _inputs(ys=(52., 47., 42., 37., 32., 27., 22., 20.), blanks=4):
    glass = glass_config()
    detections = tuple(
        replace(_detection(
            i, *(() if y is None else (_candidate(y, boundary=.85, broad=.85),)),
            ambiguity=.1, photometric=(120., 20., 90.),
        ), glass_id=glass.id)
        for i, y in enumerate((*ys, *([None] * blanks)))
    )
    return glass, detections


def _resolve(glass, detections, enabled=True, initial=InitialObservationState.FULL_NO_INTERFACE):
    return OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=enabled).resolve_sequence(
        detections, glass, initial,
    )


def test_selected_rise_to_top_closes_as_coordinate_free_full_and_exports(tmp_path):
    glass, detections = _inputs()
    baseline = _resolve(glass, detections, False)
    result = _resolve(glass, detections)
    assert [d.raw_oil_air_level_y for d in result.detections] == [
        d.raw_oil_air_level_y for d in baseline.detections
    ]
    assert all(d.fill_state is FillState.UNKNOWN_REVIEW for d in baseline.detections[8:])
    assert all(d.fill_state is FillState.FULL_NO_INTERFACE for d in result.detections[8:])
    assert result.diagnostics.full_frame_count == 4
    for d in result.detections[8:]:
        assert d.raw_oil_air_level_y is d.smoothed_oil_air_level_y is None
        assert "OIL_TOP_EXIT_FULL" in d.flags
        assert "R17_IMAGE_SUPPORTED_STATE" not in d.flags
        assert d.debug_metrics["oil_no_interface_full_likelihood"] == 0.
        assert d.debug_metrics["sequence_state_image_evidence"] == 0.
        witness = d.debug_metrics["sequence_decision_witness"]
        assert witness["selection"] == {
            "resolved_kind": "full", "selected_candidate": None, "state_evidence_source": "top_exit",
        }
        proof = d.debug_metrics["sequence_material_phase_diagnostics"]["top_exit_full"]
        assert proof["confirmation_frame_index"] == 8
        assert proof["witness"][-1]["frame_index"] == 7
        assert proof["witness"][-1]["y"] == 20.
    samples = [tracking_sample_from_detection("test", glass, d) for d in result.detections]
    assert all(s.oil_is_valid for s in samples[8:])
    assert all(not s.foam_is_valid for s in samples[8:])
    CsvExporter().export(SimpleNamespace(glass_results=[SimpleNamespace(samples=samples, events=[])]),
                         tmp_path / "tracking.csv", tmp_path / "events.csv")
    with (tmp_path / "tracking.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert all(row["fill_state"] == "FULL_NO_INTERFACE" and row["raw_oil_air_level_y"] == ""
               and row["oil_is_valid"] == "True" for row in rows[8:])


@pytest.mark.parametrize("ys", [
    (152., 147., 142., 137., 132., 127., 122., 120.),  # loss mid-Glass
    (20.,) * 8,  # stationary structure at the top
    (20., 22., 27., 32., 37., 42., 47., 52.),  # downward
    (52., 47., 42., 37., 32., 27., 22., 26.),  # reversal before loss
    (52., 47., 42., 37., 32., 27., 24., 24.),  # broad entrance is not top exit
    (22., 20.),  # unconfirmed short track
])
def test_missing_interface_without_qualified_top_exit_stays_unknown(ys):
    glass, detections = _inputs(ys)
    assert all(d.fill_state is not FillState.FULL_NO_INTERFACE
               for d in _resolve(glass, detections).detections)


@pytest.mark.parametrize("failure", ["FRAME_UNAVAILABLE", "FOGGED_OR_GLARE", "black", "quality_missing", "empty", "time_gap"])
def test_bad_disappearance_frame_cannot_close_or_resume_stale_full(failure):
    glass, detections = _inputs()
    rows = list(detections)
    if failure in {"FRAME_UNAVAILABLE", "FOGGED_OR_GLARE"}:
        rows[8] = replace(rows[8], flags=[failure])
    elif failure == "black":
        rows[8] = replace(rows[8], debug_metrics={**rows[8].debug_metrics,
            "effective_gray_mean": 0., "effective_gray_std": 0., "effective_gray_dynamic_range": 0.})
    elif failure == "quality_missing":
        rows[8] = replace(rows[8], debug_metrics={k: v for k, v in rows[8].debug_metrics.items()
                                               if not k.startswith("effective_gray_")})
    elif failure == "empty":
        rows[8] = replace(rows[8], debug_metrics={**rows[8].debug_metrics, "oil_no_interface_empty_likelihood": .9})
    else:
        rows[8:] = [replace(row, time_sec=row.time_sec + 100.) for row in rows[8:]]
    assert all(d.fill_state is not FillState.FULL_NO_INTERFACE
               for d in _resolve(glass, tuple(rows)).detections[8:])


def test_unavailable_frame_ends_confirmed_full_episode_without_resuming():
    glass, detections = _inputs()
    rows = list(detections)
    rows[9] = replace(rows[9], flags=["FRAME_UNAVAILABLE"])
    result = _resolve(glass, rows)
    assert result.detections[8].fill_state is FillState.FULL_NO_INTERFACE
    assert all(d.fill_state is FillState.UNKNOWN_REVIEW for d in result.detections[9:])


def test_full_prior_without_visible_owner_cannot_create_top_exit_state():
    glass, detections = _inputs(ys=())
    assert all(d.fill_state is FillState.UNKNOWN_REVIEW for d in _resolve(glass, detections).detections)


def test_new_numeric_interface_ends_full_and_never_gets_censored():
    glass, detections = _inputs(blanks=2)
    added = tuple(replace(_detection(i, _candidate(150.+i, boundary=.85, broad=.85),
                                    ambiguity=.1, photometric=(120.,20.,90.)), glass_id=glass.id)
                  for i in range(10,18))
    _, blanks = _inputs(ys=(), blanks=2)
    rows = detections + added + tuple(replace(d, glass_id=glass.id, frame_index=18+i,
                                            time_sec=(18+i)*.5) for i,d in enumerate(blanks))
    baseline, result = (_resolve(glass, rows, enabled) for enabled in (False,True))
    assert any(d.raw_oil_air_level_y is not None for d in result.detections[10:18])
    assert [d.raw_oil_air_level_y for d in baseline.detections] == [d.raw_oil_air_level_y for d in result.detections]
    assert all(d.fill_state is FillState.UNKNOWN_REVIEW for d in result.detections[-2:])


def test_candidate_order_and_bounded_suffix_do_not_rewrite_closure():
    glass, detections = _inputs()
    result = _resolve(glass, detections)
    permuted = tuple(replace(d,candidates=list(reversed(d.candidates))) for d in detections)
    assert _resolve(glass, permuted).detections == result.detections
    assert _resolve(glass, detections[:10]).detections == result.detections[:10]


def test_top_exit_composes_with_independently_confirmed_foam():
    from tests.unit.test_foam_episode_resolver import _foam_candidate

    glass, detections = _inputs()
    rows = list(detections)
    for index, y in ((8, 180.), (9, 174.)):
        rows[index] = replace(rows[index], candidates=[_foam_candidate(y, dynamic=.2)])
    baseline, result = (_resolve(glass, rows, enabled) for enabled in (False, True))
    assert result.diagnostics.foam_confirmed_frame_count == baseline.diagnostics.foam_confirmed_frame_count == 2
    assert [d.raw_foam_front_y for d in result.detections] == [d.raw_foam_front_y for d in baseline.detections]
    assert all(d.fill_state is FillState.FULL_WITH_FOAM for d in result.detections[8:10])
    assert all(tracking_sample_from_detection("test", glass, d).foam_is_valid
               for d in result.detections[8:10])


@pytest.mark.parametrize("change", ["switch", "provisional", "opposed", "competitor", "unselected"])
def test_phase_admission_and_actual_selected_identity_cannot_be_bypassed(change):
    from oil_tracker.adapters.vision.oil_observation_resolver import OilPathLifecycleOwner, OilObservationResolverConfig
    from oil_tracker.adapters.vision.oil_phase_identity import OilPhaseIdentity
    from oil_tracker.adapters.vision.oil_sequence_types import TrackletLifecycle
    from tests.unit.test_oil_phase_lifecycle import _node

    glass, detections = _inputs()
    refs = [(() if i >= 8 else (replace(_node(
        i, "rising", y, direction=-1, progress=32.,
        phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
    ).candidate_ref, trajectory_support=1., cluster_support=1.),))
            for i,y in enumerate((52.,47.,42.,37.,32.,27.,22.,20.,None,None,None,None))]
    if change in {"switch", "provisional", "opposed"}:
        edits = ({"tracklet_id": "fresh"} if change == "switch" else
                 {"tracklet_lifecycle": TrackletLifecycle.PROVISIONAL} if change == "provisional" else
                 {"tracklet_material_conflict": .9})
        refs[7] = (replace(refs[7][0], **edits),)
    else:
        competitor = replace(_node(8 if change == "unselected" else 7, "other", 50., direction=-1,
                                  progress=30., phase_identity=OilPhaseIdentity.DIRECT_INTERFACE).candidate_ref,
                             trajectory_support=0. if change == "unselected" else 1., cluster_support=1.)
        index = 8 if change == "unselected" else 7
        refs[index] = (*refs[index], competitor)
    owner = OilPathLifecycleOwner(OilObservationResolverConfig(
        initial_full_observation_enabled=True, top_exit_full_enabled=True))
    result = owner.resolve(detections, tuple(refs), glass, InitialObservationState.FULL_NO_INTERFACE)
    assert all(node.kind != "full" for node in result.path)
    if change == "unselected":
        assert result.path[8].kind == "unknown"
        assert result.material_phase_diagnostics[8]["top_exit_full"]["reason"] == "CURRENT_INTERFACE_OR_STATE_RESET"


@pytest.mark.parametrize("other", [{"cost_first_assignment": True}, {"candidate_rgb": True}])
def test_rejected_mechanisms_cannot_be_stacked_with_top_exit(other):
    with pytest.raises(ValueError, match="Compare top-exit"):
        OpenCvPhaseDetector(top_exit_full=True, **other)
