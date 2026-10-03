---
name: oil-docs-maintenance
description: Apply Oil Level Tracker's owners and S11 checks during docs structure changes, audits, archiving, or work-plan compaction. Use with docs-management when available; not for routine prose or detector implementation.
---

# Oil Documentation Maintenance

This Skill supplies Oil-specific routing. Use the available `docs-management` Skill for the common structure, lifecycle, inventory, preservation and verification method. Apply its existing-project path to Oil's established document owners and layout. If it is absent on another host, use the repository rules below and existing tools; do not install a global Skill or block the user's task merely to satisfy this dependency.

## Read the responsible owners

- [Documentation map and lifecycle](../../../docs/README.md): classification, authority, date catalog, archive layout and closeout rules. Keep these rules there rather than copying them into this Skill.
- [Execution policy](../../../docs/00-project/execution-policy.md): proportional verification and formal completion. A docs-only check cannot change field acceptance.
- For current-state compaction, read the [Work Plan](../../../docs/00-project/work-plan.md), then the relevant [roadmap](../../../docs/00-project/roadmap.md) and [retained commitments](../../../docs/00-project/retained-commitments.md). Preserve their distinct ownership; do not store milestone or candidate status in this Skill.
- Use [recall routing](../../../docs/00-project/recall-index.md) for an unclear past decision. Do not scan all detector revisions merely because a document belongs to S11.

## Apply Oil's boundaries

- `60-evidence` is the normal home for completed proof and `50-diagnostics` for causal records. Completion alone does not call for moving them into `90-archive`.
- Archive only after the current obligation owner is established. Use the existing archive layout in the documentation router and update the [date catalog](../../../docs/catalog-by-created-date.md) in the same change. The catalog is navigation, not a list of live dependencies.
- Keep current procedure paths/anchors, canonical reviewed truth and code-consumed manifests usable. Honor byte-preservation requirements on supplied audit originals and machine artifacts; a documentation move is not permission to regenerate a fingerprint.
- During Work Plan cleanup, retain the actual field disposition, current behavior/diagnostic baseline distinction, authorized next transition, named unknowns and deferred work. Completed experiments remain closed at their recorded scope. The roadmap changes only for milestone meaning or correction of demonstrably stale routing.
- Keep routine closeout proportional: replacing one resolved Work Plan item with its evidence link does not require a fresh full-tree inventory or a new per-turn report.

## S11 governance and verification

For S11 design, validation, diagnostic or evidence changes, use the [detector-change Skill](../s11-detector-change/SKILL.md) and the [governance contract](../../../docs/30-validation/s11-detector-change-governance.md). Apply the required History Review / Detector Governance fields to the actual changed responsibility; do not weaken the checker for document moves.

Run `python3 scripts/check_detector_governance.py --base-ref <starting-ref> --include-worktree` from the repository root when that contract applies, together with the relevant link/anchor/content checks and `git diff --check`.

The checker can require a companion design when historical validation documents move. Record the real archival/succession impact in the relevant existing design owner; [repository routing design](../../../docs/20-architecture/s11-agent-harness-v2-routing-design.md) covers process-only routing changes. Do not manufacture detector changes to satisfy the check.

Use the [Windows qualification Skill](../windows-qualification/SKILL.md) only if deliberate field qualification is separately in scope. Document maintenance does not request a private-video replay or establish field PASS.
