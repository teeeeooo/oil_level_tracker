"""Candidate scope, complete native footprints, fractional variants and leakage."""
from copy import deepcopy

import numpy as np
import pytest

from tests.diagnostics import s11_candidate_rgb_trial as trial


def test_complete_native_patch_footprint_and_excluded_middle_gap():
    rgb = np.arange(41*43*3, dtype=np.uint8).reshape(41, 43, 3)
    mask = np.ones((41, 43), dtype=bool)
    first = trial.context(rgb, mask, [21, 20])
    assert first["status"] == "AVAILABLE"
    assert [first["sides"][s]["patches"] for s in ("upper", "lower")] == [95, 95]
    changed = rgb.copy()
    changed[19:22] ^= 255
    changed[:8] ^= 255
    assert trial.context(changed, mask, [21, 20]) == first
    changed[8, 9] ^= 255
    assert trial.context(changed, mask, [21, 20])["sides"]["upper"]["uint8_sha256"] != first["sides"]["upper"]["uint8_sha256"]


def test_masked_patches_stay_missing_without_padding_or_zero_features():
    rgb = np.zeros((41, 43, 3), dtype=np.uint8)
    mask = np.ones((41, 43), dtype=bool)
    assert trial.context(rgb, mask, [11, 20])["status"] == "UNAVAILABLE_CROP"
    mask[8:19] = False
    result = trial.context(rgb, mask, [21, 20])
    assert result["status"] == "UNAVAILABLE_SIDE"
    assert result["sides"]["upper"]["uint8_sha256"] is None
    assert result["sides"]["lower"]["patches"] == 95


@pytest.mark.parametrize("values,expected", [([[2, 1]], trial.CLASSES[0]),
    ([[2, 1], [1, 2]], "UNKNOWN"), ([[2, 1], [1, 1]], "UNKNOWN"),
    ([[1, 2], [0, 2]], trial.CLASSES[1])])
def test_every_variant_must_agree(values, expected):
    assert trial.decision(values) == expected


@pytest.mark.parametrize("values", [[], [[float("nan"), 0]], [[1, 2, 3]], [1, 2]])
def test_bad_logits_are_not_predictions(values):
    with pytest.raises(ValueError):
        trial.decision(values)


def test_at_least_one_accepted_transfer_and_opposition_both_required():
    rows = [dict(partition="fit", target=0, decision=trial.CLASSES[0]),
            dict(partition="fit", target=1, decision=trial.CLASSES[1]),
            dict(partition="transfer", target=0, decision=trial.CLASSES[0]),
            dict(partition="transfer", target=0, decision="UNKNOWN"),
            dict(partition="transfer", target=1, decision=trial.CLASSES[1])]
    assert trial.summarize(rows)["required_capability"]
    all_reject = deepcopy(rows)
    all_reject[2]["decision"] = trial.CLASSES[1]
    assert not trial.summarize(all_reject)["required_capability"]
    rows[-1]["decision"] = "UNKNOWN"
    assert not trial.summarize(rows)["required_capability"]


def fixture():
    units = []
    for i, (group, partition, target) in enumerate((("a", "fit", 0), ("a", "fit", 1), ("b", "transfer", 0))):
        query = {"id": str(i), "frame": 1, "candidate_index": i, "source_xy": [10, 20]}
        units.append(dict(id=str(i), query=query, query_sha256=trial.o2.fingerprint_json(query), group=group,
                          source_recording={"sha256": group}, partition=partition, target=target, is_oil_candidate=True))
    plan = {"sources_by_group": {k: {"sha256": k} for k in ("a", "b")},
            "controls": {u["id"]: {k:u[k] for k in ("target", "partition")} for u in units},
            "population_sha256": trial.o2.fingerprint_json([{k:u[k] for k in ("id", "query_sha256", "group", "is_oil_candidate")} for u in units])}
    return units, plan


@pytest.mark.parametrize("change", ["valid", "source", "target", "partition", "query", "population"])
def test_candidate_labels_and_source_split_cannot_drift(change):
    units, plan = fixture()
    if change == "valid":
        trial.validate_units(units, plan)
        return
    if change == "source":
        units[-1]["source_recording"] = plan["sources_by_group"]["b"] = {"sha256": "a"}
    elif change == "target": units[0]["target"] = 1
    elif change == "partition": units[-1]["partition"] = "fit"
    elif change == "query": units[0]["query"]["source_xy"][1] = 21
    else: units.pop()
    with pytest.raises(ValueError):
        trial.validate_units(units, plan)
