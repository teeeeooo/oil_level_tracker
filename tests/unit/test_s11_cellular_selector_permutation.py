"""Selector counterfactual cannot bypass representation or material ownership."""
from copy import deepcopy
from dataclasses import asdict, replace

import pytest

from oil_tracker.adapters.vision.oil_sequence_types import OilSequenceNode
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidence
from tests.diagnostics.s11_cellular_selector_permutation import (
    bind_scores, normalized, paired_replay, permute_emissions,
)
from tests.fixtures.synthetic import glass_config
from tests.unit.test_oil_observation_resolver import _admitted_ref, _candidate, _detection


def layer():
    ca, cb = _candidate(40), _candidate(60)
    a = _admitted_ref(ca, candidate_offset=0, evidence=OilCandidateEvidence.from_candidate(ca))
    b = _admitted_ref(cb, candidate_offset=1, evidence=OilCandidateEvidence.from_candidate(cb))
    return (OilSequenceNode("oil", .8, "first", a),
            OilSequenceNode("oil", .3, "second", b),
            OilSequenceNode("unknown", .5, "unknown"))


def test_reverse_rank_only_swaps_existing_emissions_and_preserves_exact_refs():
    original = layer()
    changed = permute_emissions(original, {0: -2, 1: -1, 99: 100})
    assert [n.emission for n in changed] == [.3, .8, .5]
    assert original[0].emission == .8
    assert changed[2] is original[2]
    for a, b in zip(original, changed, strict=True):
        assert a.candidate_ref is b.candidate_ref
        assert replace(a, emission=b.emission) == b


@pytest.mark.parametrize("scores", [{0: 1}, {0: None, 1: 1}, {0: float("nan"), 1: 1},
                                    {0: 1, 1: float("inf")}, {0: 1, 1: 1 + 1e-13}])
def test_missing_nonfinite_or_tied_rank_is_no_intervention(scores):
    original = layer()
    assert permute_emissions(original, scores) is original


def saved_and_measurements():
    saved = normalized([asdict(_detection(i, _candidate(40 + i), _candidate(60 + i))) for i in range(5)])
    measurements = [dict(glass_id=d["glass_id"], frame_index=d["frame_index"], time_sec=d["time_sec"],
                         rows=[dict(candidate_input_index=i, canonical_y=c["y"], source=c["source"], score=float(i))
                               for i, c in enumerate(d["candidates"])]) for d in saved]
    return saved, measurements


@pytest.mark.parametrize("fault", ["length", "frame", "time", "glass", "y", "source", "duplicate", "offset", "nonfinite"])
def test_join_rejects_wrong_source_or_candidate_identity(fault):
    from tests.diagnostics.s11_saved_detection_replay import restore
    saved, measurements = saved_and_measurements()
    row = measurements[0]
    if fault == "length":
        measurements.pop()
    elif fault in ("frame", "time", "glass"):
        row[{"frame": "frame_index", "time": "time_sec", "glass": "glass_id"}[fault]] = "wrong"
    elif fault == "duplicate":
        row["rows"].append(dict(row["rows"][0]))
    else:
        key, value = {"y": ("canonical_y", 42.1), "source": ("source", "wrong"),
                      "offset": ("candidate_input_index", -1), "nonfinite": ("score", float("nan"))}[fault]
        row["rows"][0][key] = value
    with pytest.raises(ValueError):
        bind_scores(restore(saved), measurements)


def test_real_completed_sequence_entry_restores_patch_and_preserves_lifecycle():
    from oil_tracker.adapters.vision import oil_observation_resolver as owner
    build = owner.build_interface_layers
    saved, measurements = saved_and_measurements()
    before = deepcopy(saved)
    result = paired_replay(saved, measurements, glass_config())
    assert owner.build_interface_layers is build
    assert saved == before
    assert result["summary"]["lifecycle_and_allowed_owners_equal"]
    assert result["summary"]["numeric_provenance_failures"] == []
    assert len(result["layers"]) == 5


def test_cli_from_foreign_cwd_with_unicode_paths_and_no_overwrite(tmp_path):
    import json
    import os
    from pathlib import Path
    import subprocess
    import sys
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    repo = Path(__file__).resolve().parents[2]
    saved, measurements = saved_and_measurements()
    # Use the real recipe serializer's fixture instead of duplicating its schema.
    recipe = repo / "sample/sample2.oilrecipe"
    glass = JsonRecipeRepository().load(recipe).glasses[0]
    for a, b in zip(saved, measurements, strict=True):
        a["glass_id"] = b["glass_id"] = glass.id
    source = tmp_path / "저장 검출.json"
    scores = tmp_path / "측정.json"
    output = tmp_path / "재생 결과"
    source.write_text(json.dumps(saved), encoding="utf-8")
    scores.write_text(json.dumps(measurements), encoding="utf-8")
    command = [sys.executable, "-m", "tests.diagnostics.s11_cellular_selector_permutation",
               "--input", str(source), "--measurements", str(scores), "--recipe", str(recipe),
               "--output", str(output)]
    env = {**os.environ, "PYTHONPATH": os.pathsep.join((str(repo / "src"), str(repo)))}
    def run():
        return subprocess.run(command, cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8", timeout=30)
    first = run()
    assert first.returncode == 0, first.stderr
    receipt = (output / "receipt.json").read_bytes()
    assert json.loads(receipt)["status"] == "COMPLETE"
    assert run().returncode != 0
    assert (output / "receipt.json").read_bytes() == receipt
