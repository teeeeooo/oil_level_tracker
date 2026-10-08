"""Saved detector inputs retain their identity before counterfactual replay."""
from copy import deepcopy
from dataclasses import asdict
import json

import pytest

from tests.diagnostics.s11_saved_detection_replay import encode, restore
from tests.unit.test_oil_observation_resolver import _candidate, _detection


def saved_rows():
    return json.loads(json.dumps(
        [asdict(_detection(i, _candidate(40 + i))) for i in range(2)],
        default=encode,
    ))


def test_restore_preserves_every_saved_field_without_mutating_input():
    rows = saved_rows()
    before = deepcopy(rows)
    restored = restore(rows)
    assert json.loads(json.dumps([asdict(d) for d in restored], default=encode)) == before
    assert rows == before


@pytest.mark.parametrize("fault", ["empty", "glass", "frame", "time", "nonfinite", "candidate_nan", "missing_field"])
def test_invalid_or_incomplete_saved_identity_is_rejected(fault):
    rows = saved_rows()
    if fault == "empty":
        rows = []
    elif fault == "glass":
        rows[1]["glass_id"] = "another-glass"
    elif fault == "frame":
        rows[1]["frame_index"] = rows[0]["frame_index"]
    elif fault == "time":
        rows[1]["time_sec"] = rows[0]["time_sec"]
    elif fault == "nonfinite":
        rows[1]["time_sec"] = float("inf")
    elif fault == "candidate_nan":
        rows[1]["candidates"][0]["y"] = float("nan")
    else:
        del rows[0]["visibility_confidence"]
    with pytest.raises(ValueError):
        restore(rows)
