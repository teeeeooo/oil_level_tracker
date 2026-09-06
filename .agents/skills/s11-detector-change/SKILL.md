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

## Change contract

- Preserve one generic detector across Glass identities; no private timestamp, Glass identity, reviewed coordinate, or case-specific branch enters production control flow.
- Numeric Oil/Foam observations remain same-frame selected candidates with exact provenance.
- Oil/Foam ownership remains independent through their defined composition point.
- Ambiguous, unavailable, lost, or hard-invalid evidence fails closed; downstream interpolation/carry/report repair is not a detector fix.
- A new mechanism must state how it differs from the relevant failure-registry entries and which current logic-map owner changes.

## Governance and validation

When the task changes detector code, S11 detector design/validation, or S11 diagnostics/evidence, follow `docs/30-validation/s11-detector-change-governance.md` for the required History Review / Detector Governance block and checker contract.

Run `python3 scripts/check_detector_governance.py --base-ref <base-ref> --include-worktree` while editing. Then use the narrowest validation owned by the current architecture/validation contract; local PASS never implies Windows field PASS.
