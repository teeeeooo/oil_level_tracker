"""Own a fresh experiment directory; retain an explicit subset and check closeout.

This is a local research-storage tool, not a detector runner or application writer.
Only directories created by ``start`` can be cleaned by ``finish``.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import uuid


ROOT = Path(__file__).resolve().parents[1]
MARKER = ".artifact-run.json"
SCHEMA = "oil-experiment-artifacts-v1"


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def relative(value: str) -> Path:
    path = PurePosixPath(value)
    if (not path.parts or path.is_absolute() or ".." in path.parts
            or "\\" in value or ":" in value or path.as_posix() != value):
        raise ValueError(f"Expected a canonical relative path: {value}")
    return Path(*path.parts)


def contained(base: Path, value: str) -> Path:
    path = base / relative(value)
    for part in (path, *path.parents):
        if part == base:
            break
        if part.is_symlink():
            raise ValueError(f"Symlinks are not managed: {part}")
    return path


def run_path(repo: Path, value: str) -> Path:
    path = contained(repo, value)
    if relative(value).parts[:2] != ("sample", "output") or len(relative(value).parts) < 3:
        raise ValueError("A run must be a new directory below sample/output")
    for parent in path.parents:
        if parent == repo:
            break
        if (parent / MARKER).exists():
            raise ValueError("Nested managed runs are not allowed")
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def encoded(data: dict) -> bytes:
    return (json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def save(run: Path, data: dict) -> None:
    # Atomic metadata replacement. An interrupted write remains visible to check.
    pending = run / (MARKER + ".pending")
    with pending.open("xb") as handle:
        handle.write(encoded(data))
    os.replace(pending, run / MARKER)


def pin(repo: Path, value: str) -> dict:
    path = contained(repo, value)
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"Expected a regular file: {value}")
    return {"path": value, "bytes": path.stat().st_size, "sha256": digest(path)}


def inventory(base: Path) -> dict[str, dict]:
    if not base.is_dir() or base.is_symlink():
        raise ValueError(f"Missing or linked payload directory: {base}")
    result = {}
    for directory, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise ValueError(f"Only regular files may be managed: {path}")
            value = path.relative_to(base).as_posix()
            relative(value)
            result[value] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    return result


def load(repo: Path, value: str) -> tuple[Path, dict]:
    run = run_path(repo, value)
    marker = contained(run, MARKER)
    data = read_json(marker)
    if data.get("schema") != SCHEMA or data.get("run") != value or not data.get("id"):
        raise ValueError(f"Missing/mismatched ownership marker: {value}")
    expected = {MARKER, "work", "evidence"}
    if any(p.name not in expected for p in run.iterdir()):
        raise ValueError(f"Unclassified files at run root: {value}")
    return run, data


def manifests(repo: Path):
    for directory, dirs, files in os.walk(repo / "sample/output", followlinks=False):
        if MARKER in files or MARKER in dirs:
            dirs[:] = []
            yield Path(directory).relative_to(repo).as_posix()
        else:
            dirs[:] = [name for name in dirs if name not in {".git", ".venv"}
                       and not (Path(directory) / name).is_symlink()]


def start(repo: Path, value: str, plan: dict) -> dict:
    run = run_path(repo, value)
    if run.exists():
        raise FileExistsError(f"Existing directories cannot be adopted: {value}")
    if not isinstance(plan.get("purpose"), str) or not plan["purpose"].strip():
        raise ValueError("A purpose is required")
    if not isinstance(plan.get("parameters"), dict) or not plan.get("sources"):
        raise ValueError("Record parameters and the relevant source file paths")
    for key in ("scratch_budget_bytes", "retain_budget_bytes"):
        if type(plan.get(key)) is not int or plan[key] <= 0:
            raise ValueError(f"A positive explicit {key} is required")
    if plan["retain_budget_bytes"] > plan["scratch_budget_bytes"]:
        raise ValueError("Retained budget cannot exceed scratch budget")
    inputs = [pin(repo, p) for p in plan["inputs"]]
    sources = [pin(repo, p) for p in plan["sources"]]
    reuse_key = hashlib.sha256(json.dumps(
        {"inputs": sorted(inputs, key=lambda p: p["path"]),
         "sources": sorted(sources, key=lambda p: p["path"]), "parameters": plan["parameters"]},
        sort_keys=True, ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")).hexdigest()
    matches = []
    for other in manifests(repo):
        _, previous = load(repo, other)
        if previous["state"] == "closed" and previous.get("reuse_key") == reuse_key:
            matches.append(other)
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                   stdin=subprocess.DEVNULL, text=True, encoding="utf-8").strip()
    data = {"schema": SCHEMA, "id": str(uuid.uuid4()), "run": value, "state": "open",
            "started_utc": datetime.now(timezone.utc).isoformat(), "head": head,
            "purpose": plan["purpose"], "parameters": plan["parameters"],
            "inputs": inputs, "sources": sources, "reuse_key": reuse_key,
            "scratch_budget_bytes": plan["scratch_budget_bytes"],
            "retain_budget_bytes": plan["retain_budget_bytes"]}
    if len(encoded(data)) > data["scratch_budget_bytes"]:
        raise ValueError("Plan metadata already exceeds scratch budget")
    run.mkdir(parents=True, exist_ok=False)
    (run / "work").mkdir()
    save(run, data)
    return {"run": value, "work": str(run / "work"), "matching_closed_runs": matches}


def other_kept(repo: Path, current: str) -> dict[str, str]:
    result = {}
    for value in manifests(repo):
        if value == current:
            continue
        _, data = load(repo, value)
        if data["state"] == "closed":
            for path, item in data["kept"].items():
                result[item["sha256"]] = f"{value}/evidence/{path}"
    return result


def finish(repo: Path, value: str, selection: dict | None = None) -> dict:
    run, data = load(repo, value)
    if data["state"] == "closed":
        raise ValueError("Run already closed; frozen evidence cannot be overwritten")
    if data["state"] == "open":
        if (run / "evidence").exists():
            raise ValueError("Unexpected evidence directory in open run")
        if not selection or not str(selection.get("verdict", "")).strip():
            raise ValueError("A verdict (including failed/rejected/aborted) is required")
        if not str(selection.get("discard_reason", "")).strip():
            raise ValueError("Explain why the unselected intermediates can be discarded")
        files = inventory(run / "work")
        kept = {}
        known = other_kept(repo, value)
        known.update({p["sha256"]: p["path"] for p in data["inputs"] + data["sources"]})
        reuse = []
        for item in selection.get("reuse", []):
            entry = pin(repo, item["path"])
            reused = repo / relative(item["path"])
            if reused.is_relative_to(run):
                raise ValueError("Reused evidence must be outside this run")
            for parent in reused.parents:
                if parent == repo:
                    break
                if (parent / MARKER).exists():
                    _, owner = load(repo, parent.relative_to(repo).as_posix())
                    if owner["state"] != "closed" or not reused.is_relative_to(parent / "evidence"):
                        raise ValueError("Cannot reuse another run's unfinished or temporary files")
                    break
            if not str(item.get("reason", "")).strip():
                raise ValueError("Every reused file needs a retention reason")
            entry["reason"] = item["reason"]
            reuse.append(entry)
            known[entry["sha256"]] = entry["path"]
        for item in selection["keep"]:
            path = relative(item["path"]).as_posix()
            if path not in files or path in kept or not str(item.get("reason", "")).strip():
                raise ValueError(f"Missing/duplicate keep path or retention reason: {path}")
            sha = files[path]["sha256"]
            if sha in known:
                raise ValueError(f"Duplicate payload: {path}; reuse {known[sha]} instead")
            known[sha] = f"{value}/evidence/{path}"
            kept[path] = {**files[path], "reason": item["reason"]}
        discarded = {p: item for p, item in files.items() if p not in kept}
        data.update(state="closing", kept=kept, reuse=reuse,
                    verdict=selection["verdict"], discard_reason=selection["discard_reason"],
                    discarded_files=len(discarded),
                    discarded_bytes=sum(item["bytes"] for item in discarded.values()),
                    observed_work_bytes=sum(item["bytes"] for item in files.values()),
                    closed_utc=datetime.now(timezone.utc).isoformat())
        # Preflight the final size before deleting anything. No duplicate copy is made.
        final = {**data, "state": "closed"}
        if sum(item["bytes"] for item in kept.values()) + len(encoded(final)) > data["retain_budget_bytes"]:
            raise ValueError("Retained evidence and metadata exceed retain budget")
        data["discard_pending"] = discarded
        save(run, data)  # Durable intent allows an interrupted finish to resume.
    elif data["state"] != "closing":
        raise ValueError("Unknown run state")
    elif selection is not None:
        raise ValueError("Resume the recorded closing intent without --selection")

    work, evidence = run / "work", run / "evidence"
    if work.exists() and evidence.exists():
        raise ValueError("Both work and evidence exist; no automatic cleanup is safe")
    payload = work if work.exists() else evidence
    files = inventory(payload)
    kept = {p: {k: item[k] for k in ("bytes", "sha256")} for p, item in data["kept"].items()}
    allowed = {**data["discard_pending"], **kept} if payload == work else kept
    if any(p not in allowed or item != allowed[p] for p, item in files.items()):
        raise ValueError("Payload changed after closeout intent; nothing further removed")
    if any(files.get(p) != item for p, item in kept.items()):
        raise ValueError("Required retained evidence is missing or changed")
    if payload == work:
        for path, item in data["discard_pending"].items():
            target = contained(work, path)
            if target.exists():
                if digest(target) != item["sha256"]:
                    raise ValueError(f"Intermediate changed before deletion: {path}")
                target.unlink()
        for directory, _, _ in os.walk(work, topdown=False):
            if Path(directory) != work:
                try:
                    Path(directory).rmdir()
                except OSError:
                    pass
        work.rename(evidence)
    data.pop("discard_pending")
    data["state"] = "closed"
    save(run, data)
    return {"run": value, "kept_files": len(kept), "discarded_files": data["discarded_files"]}


def check(repo: Path, *, allow_open: bool = False) -> dict:
    errors, seen, count = [], {}, 0
    checked_reuse = {}
    for value in manifests(repo):
        count += 1
        try:
            run, data = load(repo, value)
            if data["state"] == "closed":
                if (run / "work").exists():
                    raise ValueError("Scratch remains after closeout")
                files = inventory(run / "evidence")
                expected = {p: {k: item[k] for k in ("bytes", "sha256")} for p, item in data["kept"].items()}
                if files != expected:
                    raise ValueError("Missing, changed or unclassified retained files")
                for item in data["reuse"]:
                    if item["path"] not in checked_reuse:
                        checked_reuse[item["path"]] = pin(repo, item["path"])
                    actual = checked_reuse[item["path"]]
                    if any(actual[k] != item[k] for k in ("bytes", "sha256")):
                        raise ValueError(f"Reused evidence changed: {item['path']}")
                for path, item in files.items():
                    sha = item["sha256"]
                    if sha in seen:
                        raise ValueError(f"Duplicate retained payload: {path} and {seen[sha]}")
                    full_path = f"{value}/evidence/{path}"
                    seen[sha] = full_path
                    checked_reuse[full_path] = {"path": full_path, **item}
                budget = data["retain_budget_bytes"]
            elif data["state"] == "open" and allow_open:
                if (run / "evidence").exists():
                    raise ValueError("Unexpected evidence directory in open run")
                files = inventory(run / "work")
                budget = data["scratch_budget_bytes"]
            else:
                raise ValueError(f"Unfinished run ({data['state']}); inspect then finish")
            total = sum(item["bytes"] for item in files.values()) + (run / MARKER).stat().st_size
            if total > budget:
                raise ValueError(f"Budget exceeded: {total} > {budget} bytes")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{value}: {exc}")
    return {"managed_runs": count, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    begin = commands.add_parser("start", help="Create a fresh owned run; never adopt an existing directory")
    begin.add_argument("--run", required=True)
    begin.add_argument("--plan", type=Path, required=True)
    close = commands.add_parser("finish", help="Keep selected evidence, remove this run's intermediates")
    close.add_argument("--run", required=True)
    close.add_argument("--selection", type=Path, help="Omit only to resume interrupted closing intent")
    verify = commands.add_parser("check", help="Read-only closeout check for managed runs")
    verify.add_argument("--allow-open", action="store_true", help="During execution, check observed scratch budgets")
    args = parser.parse_args()
    try:
        repo = args.repo.resolve()
        if args.command == "start":
            result = start(repo, args.run, read_json(args.plan))
        elif args.command == "finish":
            result = finish(repo, args.run, read_json(args.selection) if args.selection else None)
        else:
            result = check(repo, allow_open=args.allow_open)
        print(json.dumps(result, ensure_ascii=False))
        if result.get("errors"):
            raise SystemExit(1)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Artifact storage: {exc}\n")


if __name__ == "__main__":
    main()
