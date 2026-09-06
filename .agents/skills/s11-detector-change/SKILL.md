---
name: s11-detector-change
description: Use for Oil Level Tracker S11 detector code, detector architecture/design, detector validation, diagnostics, or field evidence. Routes current implementation, prior failure history, acceptance owners, and governance checks without broad historical scanning.
---

# S11 Detector Change

Use this skill for S11 detector behavior, detector ownership, detector validation, or field evidence. The current prompt and repository owners outrank historical revision documents.

## Bounded recall and routing

1. Read `docs/00-project/work-plan.md` for the current gate and candidate status.
2. Read the quick-start/design index in `docs/20-architecture/s11-current-detector-logic-map.md` and the quick failure index in `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`.
3. Identify the affected semantic node IDs and failure IDs, then read only their full entries plus the current architecture/validation owner needed for the task.
4. For Windows field work, also read the canonical reviewed truth and use the `windows-qualification` Skill.
5. Stop recall once the current owner, relevant prior failure, and required acceptance are known. Do not walk revision history R1→R20 unless a focused pointer requires it.

## Optional Graphify topology aid

Use Graphify only when the task benefits from code-topology, caller, dependency, or blast-radius discovery. It is a derived local cache, never an architecture/current-state/failure authority.

- If `graphify` is installed, run `scripts/update_graphify_s11.sh` before the first graph query in a source-changing or topology-dependent task. If it is unavailable or refresh fails, fall back to the logic map plus source search; Graphify must not block the task.
- The bounded pilot scope is owned by `.graphifyignore`; generated `graphify-out/` state is local and ignored by Git.
- Use `rg`/source search for exact symbol or literal lookup; it is materially faster. Use `graphify explain`, `path`, and `affected` when the question is relational or transitive. Treat broad natural-language `query` output as discovery only.
- Verify `INFERRED` edges and any surprising relationship against current source before using it in a design or acceptance claim. When Graphify and the current logic map disagree, inspect source and correct the stale/incorrect derived surface rather than overriding the owner document.
- Do not run or install Graphify Git hooks as a prerequisite. For a long source-editing task, Main may start `graphify watch .` in a background process and must stop it when the task ends; ordinary tasks use the one-shot refresh above.

## Change contract

- Preserve one generic detector across Glass identities; no private timestamp, Glass identity, reviewed coordinate, or case-specific branch enters production control flow.
- Numeric Oil/Foam observations remain same-frame selected candidates with exact provenance.
- Oil/Foam ownership remains independent through their defined composition point.
- Ambiguous, unavailable, lost, or hard-invalid evidence fails closed; downstream interpolation/carry/report repair is not a detector fix.
- A new mechanism must state how it differs from the relevant failure-registry entries and which current logic-map owner changes.

## Governance and validation

When the task changes detector code, S11 detector design/validation, or S11 diagnostics/evidence, follow `docs/30-validation/s11-detector-change-governance.md` for the required History Review / Detector Governance block and checker contract.

Run `python3 scripts/check_detector_governance.py --base-ref <base-ref> --include-worktree` while editing. Then use the narrowest validation owned by the current architecture/validation contract; local PASS never implies Windows field PASS.
