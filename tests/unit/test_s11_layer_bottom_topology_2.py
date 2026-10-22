from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.foam_material_identity import foam_material_identity_tolerance
from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilFillConfirmationProfile,
    OilMaterialPhaseLifecycleOwner,
)
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_layer_bottom_topology_2 as lbt2

GLASS = InspectionRecipe.default_glass(320, 240, 1)
SEPARATION = foam_material_identity_tolerance(GLASS) + 2.0
ANCHORED = OilFillConfirmationProfile.UNKNOWN_FILL_ANCHORED


class _Identity:
    def __init__(self, row=100.0, age=1.0):
        self._row, self._age = row, age

    def row(self, frame):
        return self._row

    def seed_age_seconds(self, frame):
        return self._age


def _chain(y, frame=7):
    return SimpleNamespace(last=SimpleNamespace(frame=frame, y=y))


def _guarded(identity, y, *, original=ANCHORED, enabled=True):
    """Run the patched profile for one chain after one resolver pass tracked `identity`."""
    with patch.object(resolver, "track_foam_material_identity", lambda *args, **kwargs: identity), \
            patch.object(OilMaterialPhaseLifecycleOwner, "_fill_confirmation_profile",
                         lambda self, chain: original):
        with lbt2.fill_guard(enabled=enabled) as operations:
            resolver.track_foam_material_identity((), GLASS, evidence_index=None)
            profile = OilMaterialPhaseLifecycleOwner._fill_confirmation_profile(None, _chain(y))
    return profile, operations


def test_fill_is_withheld_under_a_recent_foam_row():
    # sample4 54.5 s shape: last row Y820 under the Foam row Y808.
    profile, operations = _guarded(_Identity(row=808.0), 808.0 + SEPARATION)
    assert profile is OilFillConfirmationProfile.NONE
    assert [(op["consumer"], op["withheld"]) for op in operations] == [("F", ANCHORED.value)]


@pytest.mark.parametrize("identity, y", [
    (_Identity(row=None), 900.0),                  # no Foam material row
    (_Identity(age=3.5), 900.0),                   # Foam seeded too long ago
    (_Identity(age=None), 900.0),                  # seed age unknown
    (_Identity(row=808.0), 808.0 + SEPARATION - 0.5),  # last row not below the Foam row by the separation
])
def test_fill_confirms_as_before_without_a_recent_foam_row_above(identity, y):
    profile, operations = _guarded(identity, y)
    assert profile is ANCHORED
    assert operations == []


def test_guard_never_changes_a_profile_that_did_not_confirm():
    profile, operations = _guarded(_Identity(row=808.0), 900.0, original=OilFillConfirmationProfile.NONE)
    assert profile is OilFillConfirmationProfile.NONE
    assert operations == []


def test_disabled_guard_is_the_original_profile():
    profile, operations = _guarded(_Identity(row=808.0), 900.0, enabled=False)
    assert profile is ANCHORED
    assert operations == []


def test_guard_restores_both_patched_owners():
    track = resolver.track_foam_material_identity
    method = OilMaterialPhaseLifecycleOwner._fill_confirmation_profile
    with lbt2.changes():
        assert resolver.track_foam_material_identity is not track
        assert OilMaterialPhaseLifecycleOwner._fill_confirmation_profile is not method
    assert resolver.track_foam_material_identity is track
    assert OilMaterialPhaseLifecycleOwner._fill_confirmation_profile is method


# --- pre-registered evaluation N ------------------------------------------------------

REPLY = {"q2_reading": {"frames": [{"frame_index": 1635, "y_range": [849.4, 859.1]}]}}
CONTROLS = [
    {"frame": 1560, "y": 833.0, "review_label": "ACCEPTED"},
    {"frame": 1200, "y": 865.5, "review_label": "OPPOSED"},
]


def test_references_hold_every_user_judgment():
    refs = lbt2.references(CONTROLS, REPLY)
    assert refs[1560] == {"accepted": [833.0], "wrong": [862.0], "band": None}
    assert refs[1200]["wrong"] == [865.5]
    assert refs[1275]["wrong"] == [805.0]
    assert refs[1680]["wrong"] == [838.0]
    assert refs[1635]["band"] == [844.2, 864.3]


@pytest.mark.parametrize("y, expected", [
    (835.0, "C"),    # within C1 of the accepted Y833
    (862.0, "A"),    # the user-confirmed wrong Y862
    (845.0, "U"),    # neither
    (None, "B"),     # missing at an accepted frame
])
def test_outcome_at_an_accepted_frame(y, expected):
    assert lbt2.outcome(y, lbt2.references(CONTROLS, REPLY)[1560]) == expected


@pytest.mark.parametrize("y, expected", [(851.0, "C"), (864.3, "C"), (829.0, "A"), (None, "B")])
def test_outcome_at_a_review_013_frame(y, expected):
    assert lbt2.outcome(y, lbt2.references(CONTROLS, REPLY)[1635]) == expected


def test_no_value_at_a_wrong_only_frame_is_not_scored():
    assert lbt2.outcome(None, lbt2.references(CONTROLS, REPLY)[1620]) is None


@pytest.mark.parametrize("ordinary, trial, expected", [
    ("C", "A", "worse"), ("B", "A", "worse"), ("U", "A", "worse"), (None, "A", "worse"),
    ("C", "B", "worse"), ("C", "U", "worse"),
    ("A", "C", "better"), ("A", "B", "better"), ("A", "U", "better"), ("B", "C", "better"), ("U", "C", "better"),
    ("A", "A", "same"), ("B", "U", "same"), ("C", "C", "same"),
])
def test_transition_classes(ordinary, trial, expected):
    assert lbt2.transition(ordinary, trial) == expected


@pytest.mark.parametrize("ordinary, trial, time_sec, expected", [
    (None, 812.0, 45.0, "right"), (812.0, None, 45.0, "wrong"), (812.0, 815.0, 45.0, "U"),
    (None, 812.0, 30.0, "U"), (812.0, 812.0, 45.0, None),
])
def test_foam_change_against_review_013_q1(ordinary, trial, time_sec, expected):
    assert lbt2.foam_change(ordinary, trial, time_sec) == expected


def _record(case_id, ordinary_oil, trial_oil, ordinary_foam=None, trial_foam=None):
    """Every reference frame present; only 54.5 s (frame 1635) carries values."""
    def rows(oil, foam):
        return [{"frame_index": frame, "time_sec": frame / 30.0, "selected": None,
                 "oil_y": oil if frame == 1635 else None, "foam_y": foam if frame == 1635 else None,
                 "phase": {"value": "open", "reason": "R"}}
                for frame in sorted(lbt2.references([], REPLY))]
    return {"ordinary": {"id": case_id, "rows": rows(ordinary_oil, ordinary_foam)},
            "trial": {"id": case_id, "rows": rows(trial_oil, trial_foam)}}


def test_baseline_gaining_an_a_stops():
    refs = lbt2.references([], REPLY)
    result = lbt2.evaluate([_record("baseline", 851.0, 829.0), _record("c1", 829.0, 851.0)], refs)
    assert result["baseline"]["new_a"][0]["time"] == 54.5
    assert result["stops"] == ["the baseline gains an A"]


def test_population_net_and_foam_rules():
    refs = lbt2.references([], REPLY)
    records = [_record("baseline", 851.0, 851.0),
               _record("c1", 829.0, 851.0, None, 812.0),
               _record("c2", None, 852.0),
               _record("c3", 852.0, None, 812.0, None)]
    result = lbt2.evaluate(records, refs)
    assert result["units"] == {"better": 2, "worse": 1}
    assert result["foam"] == {"right": 1, "wrong": 1}
    assert result["stops"] == ["wrong Foam changes are not outweighed by right ones"]
