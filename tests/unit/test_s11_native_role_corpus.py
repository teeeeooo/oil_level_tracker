"""Protect partial roles, unavailable input and whole-recording separation."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_native_role_corpus as corpus


def row(sid="a", source="source", frame=1, role=None, native=True, semantic=True):
    allowed = [role] if role else []
    return dict(id=sid, subject_id=sid, source_recording=dict(path=source+".mp4", sha256=source),
                frame=frame, path_sha256=sid, qualification=None, subject_sha256=None,
                allowed_boundary_roles=allowed, certain_boundary_role=role,
                review_state="QUALIFIED_SINGLE_ROLE" if role else "UNREVIEWED",
                availability="AVAILABLE_PARTIAL_CONTEXT" if native else "UNRESOLVED_PATH_ORIENTATION",
                native_sides={"upper": "pinned", "lower": "pinned"} if native else {},
                support={"upper": {"foam": .3}} if semantic else {})


def contact(r):
    return dict(id=r["subject_id"], source_recording=r["source_recording"], frame=r["frame"],
                path_sha256=r["path_sha256"], subject_sha256="subject", review_status="QUALIFIED_ROLE",
                capability_target="LIQUID_UPPER", allowed_interpretations=["LIQUID_AIR_INTERFACE"],
                dense_labels=False, side_material_labels=None, motion_qualified=False, scalar_qualified=False,
                proposed_context={"status": r["availability"]})


@pytest.mark.parametrize("role,expected", [
    ("FOAM_UPPER", {"FOAM_UPPER": 1, "LIQUID_UPPER": None}),
    ("LIQUID_UPPER", {"FOAM_UPPER": None, "LIQUID_UPPER": 1}),
    ("INTERNAL_FOAM_CHANGE", {"FOAM_UPPER": 0, "LIQUID_UPPER": 0}),
    ("STRUCTURE_BOUNDARY", {"FOAM_UPPER": 0, "LIQUID_UPPER": 0}),
    (None, {"FOAM_UPPER": None, "LIQUID_UPPER": None}),
])
def test_partial_targets_do_not_cross_label_materials(role, expected):
    r = row(role=role)
    assert corpus.targets(r)["values"] == expected
    r["native_sides"] = {}
    assert not any(corpus.targets(r)["native_loss_mask"].values())
    assert corpus.targets(r)["values"] == expected


def test_disjunction_is_neither_two_positives_nor_two_negatives():
    r = row()
    r.update(allowed_boundary_roles=["FOAM_UPPER", "LIQUID_UPPER"], review_state="QUALIFIED_DISJUNCTION")
    result = corpus.targets(r)
    assert result["disjunction"] and result["allowed_roles"] == r["allowed_boundary_roles"]
    assert all(v is None for v in result["values"].values())
    assert not any(result["native_loss_mask"].values())


def test_new_frame_is_not_a_new_source_and_missing_semantics_stay_missing():
    rows = [row("miso", "miso", role="LIQUID_UPPER"),
            row("water-a", "water", frame=1),
            row("water-c", "water", frame=2, role="LIQUID_UPPER", semantic=False),
            row("foam", "third", role="FOAM_UPPER")]
    original = deepcopy(rows)
    native = corpus.input_coverage(rows, "native_sides")
    semantic = corpus.input_coverage(rows, "support")
    assert "LIQUID_UPPER" not in native["missing_disjoint_positive_sources"]
    assert "LIQUID_UPPER" in semantic["missing_disjoint_positive_sources"]
    folds = native["source_group_folds"]
    water = next(f for f in folds if f["held_out_source"] == "water")
    assert water["held_out_subjects"] == ["water-a", "water-c"]
    assert water["certain_available_counts"]["LIQUID_UPPER"] == {"fit": 1, "held_out": 1}
    assert all(not f["untouched_holdout"] and not f["training_executed"] for f in folds)
    assert rows == original


def test_same_source_second_positive_does_not_clear_coverage():
    rows = [row("one", role="LIQUID_UPPER"), row("two", frame=2, role="LIQUID_UPPER")]
    assert "LIQUID_UPPER" in corpus.input_coverage(rows, "native_sides")["missing_disjoint_positive_sources"]


@pytest.mark.parametrize("fault", ["duplicate_id", "duplicate_path", "source_conflict", "unavailable", "fake_semantic"])
def test_roster_identity_and_missing_inputs_fail_closed(fault):
    rows = [row("a"), row("b")]
    if fault == "duplicate_id": rows[1]["id"] = "a"
    if fault == "duplicate_path": rows[1]["path_sha256"] = "a"
    if fault == "source_conflict": rows[1]["source_recording"]["sha256"] = "another"
    if fault == "unavailable": rows[1]["availability"] = "UNRESOLVED_PATH_ORIENTATION"
    if fault == "fake_semantic":
        rows[1].update(native_sides={}, availability="UNRESOLVED_PATH_ORIENTATION")
    with pytest.raises(ValueError): corpus.validate_roster(rows)


def test_contact_overlay_keeps_saved_observations_and_scoped_role():
    r = row(); original = deepcopy(r)
    corpus.apply_contact([r], contact(r), {"reply": "pinned"})
    assert r["support"] == original["support"] and r["native_sides"] == original["native_sides"]
    assert r["original_interpretations"] == ["LIQUID_AIR_INTERFACE"]
    assert r["certain_boundary_role"] == "LIQUID_UPPER"
    assert corpus.targets(r)["values"]["FOAM_UPPER"] is None


@pytest.mark.parametrize("fault", ["source", "frame", "path", "alias", "old_role", "support", "motion", "pure_side", "duplicate"])
def test_contact_cannot_override_or_expand_exact_truth(fault):
    r = row(); subject = contact(r); rows = [r]
    if fault == "source": subject["source_recording"] = dict(path="other", sha256="other")
    if fault == "frame": subject["frame"] = 2
    if fault == "path": subject["path_sha256"] = "other"
    if fault == "alias": subject["id"] = "alias"
    if fault == "old_role": r["review_state"] = "QUALIFIED_SINGLE_ROLE"
    if fault == "support": subject["proposed_context"]["status"] = "UNAVAILABLE"
    if fault == "motion": subject["motion_qualified"] = True
    if fault == "pure_side": subject["side_material_labels"] = {"upper": "air"}
    if fault == "duplicate": rows.append(deepcopy(r))
    with pytest.raises(ValueError): corpus.apply_contact(rows, subject, {})


def test_cli_foreign_cwd_refuses_overwrite_before_reading_inputs(tmp_path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    def invoke(*args):
        return subprocess.run([sys.executable, "-B", str(Path(corpus.__file__).resolve()), *args],
            cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True,
            text=True, encoding="utf-8", timeout=20)
    assert invoke("--help").returncode == 0
    output = tmp_path / "보존 결과.json"
    output.write_bytes(b"original")
    result = invoke("--plan", "absent.json", "--output", str(output))
    assert result.returncode != 0 and "refuse overwrite" in result.stderr
    assert output.read_bytes() == b"original"
