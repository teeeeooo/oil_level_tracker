"""Partial-role and source-isolation guards; no model or physical accuracy tests."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_semantic_role_preflight as role


def example(sid="p", *, source="source-a", labels=("EXTERNAL_FOAM_UPPER",), available=True):
    target = ("EXTERNAL_SURFACE" if any("UPPER" in s for s in labels)
              else labels[0] if labels else None)
    unit = dict(id=sid, qualification={"path": "role.json", "sha256": "q"} if labels else None,
                review_role=target, subject_sha256="subject" if labels else None,
                source_recording={"path": source + ".mp4", "sha256": source}, frame=10,
                path_sha256=sid, availability="AVAILABLE_PARTIAL_CONTEXT" if available else
                "UNRESOLVED_PATH_ORIENTATION",
                sides={s: {"shape": [2, 7, 7, 3]} for s in ("upper", "lower")} if available else {})
    subject = dict(id=sid, subject_sha256="subject", capability_target=target,
                   source_recording=unit["source_recording"], frame=10,
                   scope="DISPLAYED_FRAGMENT_ROLE_ONLY", dense_labels=False,
                   side_material_labels=None, allowed_interpretations=list(labels)) if labels else None
    upper = dict(prompt_patch_means=[[.1, .7, .3], [.3, .9, .5]], prompt_means=[.2, .8, .4])
    lower = dict(prompt_patch_means=[[.8, .1, .2], [.6, .3, .4]], prompt_means=[.7, .2, .3])
    saved = dict(id=sid, frame_key=source + ":10", role=target, availability=unit["availability"],
                 sides={"upper": upper, "lower": lower} if available else {},
                 order_score=.01 if available else None)
    return unit, saved, subject


def bound(*examples):
    return role.bind_rows([e[0] for e in examples], [e[1] for e in examples],
                          {e[0]["id"]: e[2] for e in examples if e[2] is not None})


def test_disjunctive_external_role_does_not_become_foam_or_liquid_truth():
    e = example(labels=("EXTERNAL_FOAM_UPPER", "OSCILLATING_LIQUID_UPPER"))
    original = deepcopy(e)
    rows = bound(e)
    assert e == original
    assert rows[0]["allowed_boundary_roles"] == ["FOAM_UPPER", "LIQUID_UPPER"]
    assert rows[0]["certain_boundary_role"] is None
    assert rows[0]["review_state"] == "QUALIFIED_DISJUNCTION"
    for key in ("FOAM_UPPER", "LIQUID_UPPER"):
        assert role.coverage(rows)[key]["certain_paths"] == []
        assert role.coverage(rows)[key]["compatible_disjunctions"] == ["p"]


def test_known_oppositions_keep_their_distinct_roles():
    rows = bound(example("internal", labels=("INTERNAL_FOAM_CHANGE",)),
                 example("rim", labels=("STRUCTURE_BOUNDARY",)))
    assert [r["certain_boundary_role"] for r in rows] == ["INTERNAL_FOAM_CHANGE", "STRUCTURE_BOUNDARY"]
    assert all(r["physical_decision"] is None and not r["pure_side_material_truth"] for r in rows)


def test_three_supports_survive_without_union_or_physical_label():
    row, = bound(example(labels=()))
    assert row["support"] == {"upper": {"foam": .2, "liquid": .8, "glass rim": .4},
                              "lower": {"foam": .7, "liquid": .2, "glass rim": .3}}
    assert row["review_state"] == "UNREVIEWED"
    assert row["allowed_boundary_roles"] == [] and row["physical_decision"] is None


def test_unavailable_positive_does_not_supply_observation_or_source_coverage():
    rows = bound(example(available=False))
    summary = role.coverage(rows)["FOAM_UPPER"]
    assert summary["certain_paths"] == ["p"]
    assert summary["available_certain_paths"] == summary["available_certain_sources"] == []
    assert rows[0]["support"] == {}


@pytest.mark.parametrize("field,value", [("id", "q"), ("subject_sha256", "other"),
    ("frame", 11), ("source_recording", {"path": "different", "sha256": "other"}),
    ("capability_target", "STRUCTURE_BOUNDARY"), ("scope", "WHOLE_FRAME"),
    ("dense_labels", True), ("side_material_labels", {"lower": "foam"}),
    ("allowed_interpretations", []), ("allowed_interpretations", ["LIQUID_PIXEL"]),
    ("allowed_interpretations", ["EXTERNAL_FOAM_UPPER", "EXTERNAL_FOAM_UPPER"])])
def test_role_scope_and_identity_cannot_be_widened(field, value):
    unit, saved, subject = example()
    subject[field] = value
    with pytest.raises(ValueError):
        role.bind_rows([unit], [saved], {unit["id"]: subject})


@pytest.mark.parametrize("field,value", [("frame_key", "other:10"),
    ("role", "STRUCTURE_BOUNDARY"), ("availability", "UNAVAILABLE_SIDE_CONTEXT")])
def test_saved_vector_must_match_exact_subject(field, value):
    unit, saved, subject = example()
    saved[field] = value
    with pytest.raises(ValueError, match="binding changed"):
        role.bind_rows([unit], [saved], {unit["id"]: subject})


@pytest.mark.parametrize("fault", ["duplicate", "missing", "reorder", "same_path", "source_conflict"])
def test_population_and_physical_denominator_are_preserved(fault):
    a, b = example("a"), example("b")
    units, rows = [a[0], b[0]], [a[1], b[1]]
    if fault == "duplicate": rows[1] = deepcopy(rows[0])
    if fault == "missing": rows.pop()
    if fault == "reorder": rows.reverse()
    if fault == "same_path": units[1]["path_sha256"] = units[0]["path_sha256"]
    if fault == "source_conflict": units[1]["source_recording"]["sha256"] = "different"
    with pytest.raises(ValueError):
        role.bind_rows(units, rows, {"a": a[2], "b": b[2]})


@pytest.mark.parametrize("fault", ["nan", "inf", "range", "mean", "shape", "count", "bool"])
def test_invalid_support_is_not_a_clean_or_negative_observation(fault):
    _, saved, _ = example()
    side = saved["sides"]["upper"]
    if fault in ("nan", "inf", "range", "bool"):
        side["prompt_patch_means"][0][0] = {"nan": float("nan"), "inf": float("inf"),
                                           "range": -0.1, "bool": True}[fault]
    if fault == "mean": side["prompt_means"][0] = .9
    if fault == "shape": side["prompt_patch_means"][0].pop()
    if fault == "count": side["prompt_patch_means"].pop()
    with pytest.raises(ValueError): role.side_support(side, 2)


def test_source_aliases_and_different_frames_stay_in_one_fold():
    a = example("a", source="a")
    b = example("b", source="a")
    b[0]["source_recording"]["path"] = "derivative.mp4"
    b[2]["source_recording"] = b[0]["source_recording"]
    b[0]["frame"] = b[2]["frame"] = 20
    b[1]["frame_key"] = "a:20"
    c = example("c", source="b", labels=("STRUCTURE_BOUNDARY",))
    folds = role.grouped_folds(bound(a, b, c))
    assert len(folds) == 2
    for fold in folds:
        assert fold["held_out_source"] not in fold["fitting_source_candidates"]
        assert not set(fold["held_out_subjects"]) & set(fold["fitting_subject_candidates"])
        assert not fold["untouched_holdout"] and not fold["evaluation_executed"]
    assert folds[0]["held_out_subjects"] == ["a", "b"]
    assert folds[0]["certain_available_counts"]["LIQUID_UPPER"] == {"fit": 0, "held_out": 0}


def test_cli_import_and_overwrite_refusal_outside_repository(tmp_path):
    script = Path(role.__file__).resolve()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    def invoke(*args):
        return subprocess.run([sys.executable, "-B", str(script), *args], cwd=tmp_path,
            env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert invoke("--help").returncode == 0
    output = tmp_path / "기존 결과.json"
    output.write_bytes(b"preserve")
    result = invoke("--plan", "missing.json", "--output", str(output))
    assert result.returncode != 0 and "refuse overwrite" in result.stderr
    assert output.read_bytes() == b"preserve"
