# Oil Level Tracker Repository Overlay

The deployed user-level Codex `AGENTS.md` owns generic execution behavior. This file keeps only repository-specific routing and invariants.

## Current owners

- Current milestone, accepted baseline, field disposition, and next transition: `docs/00-project/work-plan.md`.
- Broader milestone order/state: `docs/00-project/roadmap.md`.
- Exact-head review, proportional verification, publication, and formal closeout semantics: `docs/00-project/execution-policy.md`.
- Documentation classification/authority: `docs/README.md` when creating, moving, renaming, or changing document ownership.
- Compact past-dependent routing: `docs/00-project/recall-index.md`.

## Task Skills

- S11 detector behavior/design/validation/diagnostics/evidence: `.agents/skills/s11-detector-change/SKILL.md`.
- Deliberate target-Windows field qualification: `.agents/skills/windows-qualification/SKILL.md`.

Do not duplicate their reading sequences here. Repository history is evidence, not current authority.

## Implementation discovery routes

These are starting points, not exhaustive search boundaries. Follow current imports, callers, and registrations for the affected responsibility.

- Application entry points: `[project.scripts]` in `pyproject.toml`, `src/oil_tracker/__main__.py`, `src/oil_tracker/cli.py`, and `src/oil_tracker/bootstrap.py`.
- Existing implementation: relevant modules under `src/oil_tracker/`, operational helpers under `scripts/`, and their callers and tests.
- Detector ownership and control flow: use the S11 skill and current logic map already routed above.

## Repository boundaries

- Current source/owner documents outrank historical revision prose.
- Preserve the current field disposition until its acceptance owner is actually satisfied.
- Merge/release/publication and destructive or irreversible repository actions require authority covering that action; preparing and validating a branch does not.
