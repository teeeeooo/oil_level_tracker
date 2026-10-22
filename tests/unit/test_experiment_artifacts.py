from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts.experiment_artifacts import MARKER, ROOT, check, finish, start


def git(repo, *args):
    return subprocess.check_output(["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=",
                                    "-C", str(repo), *args], stdin=subprocess.DEVNULL,
                                   text=True, encoding="utf-8").strip()


@pytest.fixture
def repository(tmp_path):
    repo = tmp_path / "repo with spaces"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Artifact Test")
    git(repo, "config", "user.email", "artifact-test@example.invalid")
    (repo / "probe.py").write_text("print('probe')\n", encoding="utf-8")
    (repo / "input.dat").write_bytes(b"immutable input")
    git(repo, "add", "probe.py", "input.dat")
    git(repo, "commit", "-qm", "fixture baseline")
    plan = dict(purpose="Test a bounded hypothesis", parameters={"condition": "fixed"},
                sources=["probe.py"], inputs=["input.dat"],
                scratch_budget_bytes=100_000, retain_budget_bytes=20_000)
    return repo, plan


def selection(*paths, reuse=()):
    return dict(verdict="CLOSED WITHOUT PROMOTION: retain the counterexample",
                keep=[dict(path=p, reason="Required comparison evidence") for p in paths],
                reuse=list(reuse), discard_reason="Recomputable intermediate files",
                retention_review=dict(
                    decision_use="Prevent retrying the rejected hypothesis without a new mechanism",
                    loss_if_removed="The frozen negative comparison would be lost",
                    reproduction="Source exists; rerunning is unnecessary for this small evidence",
                    minimality="Keep the comparison summary; discard dense intermediates",
                    review_when="Reassess when a successor replaces this counterexample"))


def test_value_review_required_before_delete_and_checked_on_closed_runs(repository):
    repo, plan = repository
    name = "sample/output/value-review"
    work = Path(start(repo, name, plan)["work"])
    (work / "summary.json").write_bytes(b'{"negative":true}\n')
    (work / "scratch.txt").write_bytes(b"still needed until reviewed")
    chosen = selection("summary.json")
    chosen.pop("retention_review")
    with pytest.raises(ValueError, match="decision_use"):
        finish(repo, name, chosen)
    assert (work / "scratch.txt").exists()
    chosen = selection("summary.json")
    chosen["retention_review"]["minimality"] = " "
    with pytest.raises(ValueError, match="minimality"):
        finish(repo, name, chosen)
    assert (work / "scratch.txt").exists()
    finish(repo, name, selection("summary.json"))
    marker = repo / name / MARKER
    data = json.loads(marker.read_text(encoding="utf-8"))
    data.pop("retention_review")
    marker.write_text(json.dumps(data), encoding="utf-8")
    assert "Retention value review" in check(repo)["errors"][0]


def test_cli_from_other_cwd_closes_run_and_removes_only_owned_intermediates(repository, tmp_path):
    repo, plan = repository
    name = "sample/output/trial-001"
    plan_file, keep_file = tmp_path / "plan.json", tmp_path / "keep.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")
    keep_file.write_text(json.dumps(selection("결과/summary.json")), encoding="utf-8")
    command = [sys.executable, str(ROOT / "scripts/experiment_artifacts.py"), "--repo", str(repo)]

    def cli(*args):
        return subprocess.run(command + list(args), cwd=tmp_path, capture_output=True,
                              stdin=subprocess.DEVNULL, text=True, encoding="utf-8", check=True)

    work = Path(json.loads(cli("start", "--run", name, "--plan", str(plan_file)).stdout)["work"])
    (work / "결과").mkdir()
    (work / "결과/summary.json").write_bytes(b'{"failed":true}\n')
    (work / "trace.jsonl").write_bytes(b"temporary trace\n" * 100)
    unrelated = repo / "sample/output/legacy"
    unrelated.mkdir()
    (unrelated / "keep.txt").write_bytes(b"not owned")
    cli("finish", "--run", name, "--selection", str(keep_file))
    assert json.loads(cli("check").stdout) == {"managed_runs": 1, "errors": []}
    assert not work.exists()
    assert (repo / name / "evidence/결과/summary.json").read_bytes() == b'{"failed":true}\n'
    assert not (repo / name / "evidence/trace.jsonl").exists()
    assert (unrelated / "keep.txt").read_bytes() == b"not owned"
    data = json.loads((repo / name / MARKER).read_text(encoding="utf-8"))
    assert data["discarded_files"] == 1 and data["inputs"][0]["path"] == "input.dat"
    assert (repo / "input.dat").read_bytes() == b"immutable input"
    with pytest.raises(ValueError, match="already closed"):
        finish(repo, name, selection())


def test_existing_directories_and_unsafe_run_paths_cannot_be_adopted(repository):
    repo, plan = repository
    legacy = repo / "sample/output/legacy"
    legacy.mkdir(parents=True)
    (legacy / "evidence.bin").write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        start(repo, "sample/output/legacy", plan)
    for name in ("sample/output", "sample/output/../../escape", "/absolute", "sample/output/C:bad"):
        with pytest.raises(ValueError):
            start(repo, name, plan)
    start(repo, "sample/output/new", plan)
    with pytest.raises(ValueError, match="Nested"):
        start(repo, "sample/output/new/work/nested", plan)
    assert (legacy / "evidence.bin").read_bytes() == b"keep"


def test_budget_and_duplicate_failures_happen_before_deletion(repository):
    repo, plan = repository
    name = "sample/output/run"
    work = Path(start(repo, name, plan)["work"])
    (work / "large.bin").write_bytes(b"x" * 25_000)
    (work / "discard.txt").write_bytes(b"untouched on failed preflight")
    with pytest.raises(ValueError, match="retain budget"):
        finish(repo, name, selection("large.bin"))
    assert (work / "discard.txt").exists()
    (work / "input-copy.dat").write_bytes((repo / "input.dat").read_bytes())
    with pytest.raises(ValueError, match="Duplicate payload"):
        finish(repo, name, selection("input-copy.dat"))
    (work / "a.txt").write_bytes(b"identical output")
    (work / "b.txt").write_bytes(b"identical output")
    with pytest.raises(ValueError, match="Duplicate payload"):
        finish(repo, name, selection("a.txt", "b.txt"))
    assert (work / "discard.txt").exists()


def test_repeated_output_must_reference_previous_run_and_references_are_checked(repository):
    repo, plan = repository
    first, second = "sample/output/one", "sample/output/two"
    work1 = Path(start(repo, first, plan)["work"])
    (work1 / "counterexample.txt").write_bytes(b"negative evidence")
    finish(repo, first, selection("counterexample.txt"))
    # A documentation-only HEAD change does not invalidate the relevant input identity.
    (repo / "note.md").write_text("new note", encoding="utf-8")
    git(repo, "add", "note.md")
    git(repo, "commit", "-qm", "document only")
    started = start(repo, second, plan)
    assert started["matching_closed_runs"] == [first]
    work2 = Path(started["work"])
    (work2 / "copy.txt").write_bytes(b"negative evidence")
    with pytest.raises(ValueError, match="Duplicate payload"):
        finish(repo, second, selection("copy.txt"))
    reuse = dict(path=f"{first}/evidence/counterexample.txt", reason="Same counterexample")
    finish(repo, second, selection(reuse=[reuse]))
    assert not check(repo)["errors"]
    assert not (repo / second / "evidence/copy.txt").exists()
    (repo / first / "evidence/counterexample.txt").write_bytes(b"changed")
    assert len(check(repo)["errors"]) == 2


def test_unfinished_other_run_cannot_become_a_reused_dependency(repository):
    repo, plan = repository
    one, two = "sample/output/one", "sample/output/two"
    work = Path(start(repo, one, plan)["work"])
    (work / "temporary.txt").write_bytes(b"not frozen")
    start(repo, two, plan)
    with pytest.raises(ValueError, match="unfinished or temporary"):
        finish(repo, two, selection(reuse=[dict(path=f"{one}/work/temporary.txt", reason="unsafe")]))
    assert (work / "temporary.txt").read_bytes() == b"not frozen"


def test_check_detects_abandoned_runs_budget_overrun_and_extra_closed_files(repository):
    repo, plan = repository
    name = "sample/output/run"
    work = Path(start(repo, name, plan)["work"])
    assert "Unfinished" in check(repo)["errors"][0]
    assert not check(repo, allow_open=True)["errors"]
    (work / "huge.tmp").write_bytes(b"x" * 100_000)
    assert "Budget exceeded" in check(repo, allow_open=True)["errors"][0]
    # Even a failed/aborted run can discard its own intermediates and close.
    finish(repo, name, selection())
    assert not check(repo)["errors"]
    (repo / name / "evidence/unclassified.txt").write_bytes(b"extra")
    assert "unclassified" in check(repo)["errors"][0]


def test_interrupted_closeout_resumes_but_refuses_new_or_changed_files(repository, monkeypatch):
    repo, plan = repository
    name = "sample/output/run"
    work = Path(start(repo, name, plan)["work"])
    (work / "keep.txt").write_bytes(b"verdict evidence")
    (work / "discard.txt").write_bytes(b"temporary")
    original = Path.unlink

    def interrupted(path, *args, **kwargs):
        original(path, *args, **kwargs)
        if path == work / "discard.txt":
            raise OSError("simulated interrupted deletion")

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", interrupted)
        with pytest.raises(OSError, match="interrupted"):
            finish(repo, name, selection("keep.txt"))
    assert "closing" in check(repo)["errors"][0]
    (work / "late.txt").write_bytes(b"new writer still running")
    with pytest.raises(ValueError, match="changed after closeout"):
        finish(repo, name)
    assert (work / "late.txt").exists() and (work / "keep.txt").exists()
    (work / "late.txt").unlink()
    finish(repo, name)
    assert not check(repo)["errors"]


def test_symlink_payload_or_parent_cannot_expand_cleanup_scope(repository, tmp_path):
    repo, plan = repository
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_bytes(b"outside evidence")
    output = repo / "sample/output"
    output.mkdir(parents=True)
    try:
        (output / "linked").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"Host does not allow symlink creation: {exc}")
    with pytest.raises(ValueError, match="Symlinks"):
        start(repo, "sample/output/linked/run", plan)
    work = Path(start(repo, "sample/output/run", plan)["work"])
    (work / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="regular files"):
        finish(repo, "sample/output/run", selection())
    assert (outside / "keep.txt").read_bytes() == b"outside evidence"


def test_real_pre_push_hook_blocks_open_run_then_accepts_closed_run(repository):
    if shutil.which("bash") is None:
        pytest.skip("Repository shell hook requires bash")
    repo, plan = repository
    (repo / "scripts").mkdir()
    for name in ("experiment_artifacts.py", "check_detector_governance.py", "check_docs_catalog.py"):
        shutil.copyfile(ROOT / "scripts" / name, repo / "scripts" / name)
    # The hook also checks the docs date catalog; a catalog that lists itself passes.
    (repo / "docs").mkdir()
    (repo / "docs" / "catalog-by-created-date.md").write_text(
        "| [catalog](catalog-by-created-date.md) |\n", encoding="utf-8")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "ordinary.txt").write_text("unrelated code change", encoding="utf-8")
    git(repo, "add", "ordinary.txt", "docs/catalog-by-created-date.md")
    git(repo, "commit", "-qm", "ordinary change")
    head = git(repo, "rev-parse", "HEAD")
    name = "sample/output/run"
    start(repo, name, plan)

    def hook():
        return subprocess.run(["bash", str(ROOT / ".githooks/pre-push"), "origin"], cwd=repo,
                              input=f"refs/heads/main {head} refs/heads/main {base}\n",
                              capture_output=True, text=True, encoding="utf-8")

    blocked = hook()
    assert blocked.returncode != 0 and "Unfinished" in blocked.stdout, blocked.stderr
    finish(repo, name, selection())
    accepted = hook()
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
