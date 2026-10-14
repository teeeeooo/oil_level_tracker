"""Protect contact-role precision and the immutable saved-observation population."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_native_liquid_reply as liquid


def fixture():
    subject = dict(id="fragment-1", source_path_xy=[[10, 20], [11, 20]])
    digest = liquid.o2.fingerprint_json(subject)
    display = dict(path="review.png", sha256="display")
    proposal = dict(subjects=[subject], display=display)
    checked = dict(id=subject["id"], subject_sha256=digest,
                   source_recording={"path": "source.mp4", "sha256": "source"}, frame=5,
                   scope="DISPLAYED_FRAGMENT_ROLE_ONLY", dense_labels=False, side_material_labels=None,
                   proposed_context={"status": "AVAILABLE_PARTIAL_CONTEXT"})
    inspection = dict(subjects=[checked], status="PROPOSAL_VERIFIED_PENDING_REVIEW", qualified_units=0)
    reply = dict(schema=liquid.SCHEMA, proposal={"path": "proposal.json", "sha256": "proposal"},
                 display=display, response_ko="foam 최하단임 유체랑 경계면", answers=[dict(
                     id=subject["id"], subject_sha256=digest, statement_ko="foam 최하단임 유체랑 경계면",
                     role="FOAM_LOWER_LIQUID_INTERFACE", scope="DISPLAYED_FRAGMENT_ROLE_ONLY")])
    row = dict(id=subject["id"], source_recording=checked["source_recording"], frame=5,
               path_sha256=liquid.o2.fingerprint_json(subject["source_path_xy"]),
               review_state="UNREVIEWED", qualification=None, allowed_boundary_roles=[],
               certain_boundary_role=None, availability="AVAILABLE_PARTIAL_CONTEXT",
               support={"upper": {"foam": .7}, "lower": {"foam": .4}})
    before = dict(rows=[row], counts=dict(total=1, available=1, qualified=0, unknown=1, recordings=1, frames=1, pairs=0))
    return reply, proposal, inspection, before


@pytest.mark.parametrize("role", list(liquid.RELATIONS))
def test_contact_does_not_assert_motion_or_pure_side_material(role):
    reply, proposal, inspection, _ = fixture()
    reply["answers"][0]["role"] = role
    original = deepcopy((reply, proposal, inspection))
    result, = liquid.bind_subjects(reply, proposal, inspection)
    assert (reply, proposal, inspection) == original
    assert result["capability_target"] == "LIQUID_UPPER"
    assert result["allowed_interpretations"] == [role]
    assert result["side_material_labels"] is None
    assert not result["motion_qualified"] and not result["scalar_qualified"] and not result["dense_labels"]


@pytest.mark.parametrize("fault", ["subject", "scope", "display", "statement", "motion", "foam_upper", "extra", "missing", "duplicate"])
def test_reply_cannot_silently_expand_or_rebind_truth(fault):
    reply, proposal, inspection, _ = fixture()
    answer = reply["answers"][0]
    if fault == "subject": answer["subject_sha256"] = "other"
    if fault == "scope": answer["scope"] = "WHOLE_LAYER"
    if fault == "display": reply["display"] = {"path": "other.png", "sha256": "other"}
    if fault == "statement": answer["statement_ko"] = "새로운 판정"
    if fault == "motion": answer["role"] = "OSCILLATING_LIQUID_UPPER"
    if fault == "foam_upper": answer["role"] = "EXTERNAL_FOAM_UPPER"
    if fault == "extra": answer["side_material_labels"] = {"upper": "foam"}
    if fault == "missing": reply["answers"] = []
    if fault == "duplicate": reply["answers"].append(deepcopy(answer))
    with pytest.raises(ValueError): liquid.bind_subjects(reply, proposal, inspection)


def test_one_new_liquid_source_is_not_source_disjoint_fit_readiness():
    reply, proposal, inspection, before = fixture()
    subjects = liquid.bind_subjects(reply, proposal, inspection)
    original = deepcopy(before)
    result = liquid.merge_coverage(before, subjects)
    assert before == original
    assert result["population_counts"]["qualified"] == 1 and result["population_counts"]["unknown"] == 0
    assert result["role_coverage"]["LIQUID_UPPER"]["available_certain_sources"] == ["source"]
    assert "LIQUID_UPPER" not in result["missing_single_role_positive"]
    assert "LIQUID_UPPER" in result["missing_disjoint_positive_sources"]
    assert result["status"] == "ROLE_SUPERVISION_INCOMPLETE"
    assert result["source_group_folds"][0]["certain_available_counts"]["LIQUID_UPPER"] == {"fit": 0, "held_out": 1}


@pytest.mark.parametrize("fault", ["path", "source", "frame", "id", "availability", "old_role", "duplicate"])
def test_role_overlay_cannot_change_population_or_existing_qualifications(fault):
    reply, proposal, inspection, before = fixture()
    subjects = liquid.bind_subjects(reply, proposal, inspection)
    row = before["rows"][0]
    if fault == "path": row["path_sha256"] = "other"
    if fault == "source": row["source_recording"] = {"sha256": "other", "path": "other.mp4"}
    if fault == "frame": row["frame"] = 6
    if fault == "id": row["id"] = "alias"
    if fault == "availability": row["availability"] = "UNAVAILABLE"
    if fault == "old_role": row.update(review_state="QUALIFIED_DISJUNCTION", allowed_boundary_roles=["FOAM_UPPER", "LIQUID_UPPER"])
    if fault == "duplicate": subjects.append(deepcopy(subjects[0]))
    with pytest.raises(ValueError): liquid.merge_coverage(before, subjects)


def test_cli_foreign_cwd_and_overwrite_refusal(tmp_path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    def invoke(*args):
        return subprocess.run([sys.executable, "-B", str(Path(liquid.__file__).resolve()), *args],
            cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True,
            text=True, encoding="utf-8", timeout=20)
    assert invoke("--help").returncode == 0
    path = tmp_path / "이미 있는 결과.json"
    path.write_bytes(b"original")
    result = invoke("--reply", "missing.json", "--output", str(path))
    assert result.returncode != 0 and "refuse overwrite" in result.stderr
    assert path.read_bytes() == b"original"
