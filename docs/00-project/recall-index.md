# Project Recall Index

This is the compact routing layer for past-dependent Oil Level Tracker work. It is not a second work plan, architecture owner, or history log.

## Recall gate

Use this index when the task depends on a prior decision, known failed mechanism, paused work, unclear ownership, or the reason an existing mechanism is intentionally constrained.

Read in this order and stop once the needed context is recovered:

1. current state — `work-plan.md`;
2. current owner/source for the affected responsibility;
3. one focused durable failure/decision source below;
4. current validation/truth owner for drift-prone claims;
5. historical diagnostics/evidence only when a focused pointer still leaves a material gap.

Do not scan revision history or all S11 diagnostics by default.

## High-value routes

| Need | Start here | Then only if needed |
|---|---|---|
| Current S11 candidate/gate | `work-plan.md` | current architecture + validation linked there |
| Current detector control flow | `../20-architecture/s11-current-detector-logic-map.md` | affected node detail/source |
| Code topology / caller / blast radius | current logic map + source | optional local Graphify cache after `scripts/update_graphify_s11.sh` |
| Known detector mechanism failures / no-repeat rules | `../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | one referenced diagnostic/evidence record |
| Rejected R23 polarity-only association / latest BASE label correction | `../50-diagnostics/s11/s11-r23-native-polarity-rejection.md` | F04; physical-interface design and acceptance gates |
| Relationship of the September/October specifications, O/W mapping and live stage status | [document routing](../README.md#s11-audit-specifications-and-execution-routing) | [work-item ledger](work-plan.md#s11-work-item-ledger); do not infer live status from dated audits |
| O2 target distinctions / aggregation | [W1 controls](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md) | Partial interface support is not whole-candidate identity; max pooling cannot certify glare. |
| W3 prediction/evaluation compatibility | [W3 evidence](../60-evidence/s11/s11-o2-w3-target-evaluation-local.md) | [Windows audit](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md); row admission is not final selection or scalar truth. |
| Paired-scale comparison and support accounting | [Local controls](../60-evidence/s11/s11-o2-w4-paired-scale-local.md) | [Windows result](../60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md); support-only gains are not discrimination; no promotion. |
| Candidate identity / human temporal-context uncertainty | [Source audit](../60-evidence/s11/s11-o2-identity-context-source-audit.md) | [Human rationale and reconciliation](../60-evidence/s11/s11-o2-identity-context-windows-review-001.md); preserve formal labels, scores and idx0/idx20 ambiguity. |
| Truth uncertainty versus model abstention | [Evaluation audit](../60-evidence/s11/s11-o2-reference-uncertainty-evaluation-audit.md) | Note text does not relabel; changed truth is not a scoring gain; original outputs stay pinned. |
| Structure-context interpretation | [Local context audit](../60-evidence/s11/s11-o2-structure-context-audit-local.md) | [Windows reconciliation](../60-evidence/s11/s11-o2-structure-context-audit-windows-run-001.md); missing is not zero and template matches are not identity. |
| Full-height spatial appearance / exact band union | [Spatial prototype](../60-evidence/s11/s11-o2-spatial-context-prototype-local.md) | [Adapter](../60-evidence/s11/s11-o2-spatial-context-source-adapter-local.md), [Windows geometry](../60-evidence/s11/s11-o2-spatial-context-windows-run-001.md); per-candidate novelty is not packet-wide novelty. |
| Spatial-profile limits / row-column collisions | [Feasibility controls](../60-evidence/s11/s11-o2-spatial-context-feasibility-local.md) | [Lateral prototype](../60-evidence/s11/s11-o2-lateral-context-prototype-local.md); retained appearance is not physical identity. |
| Joint spatial validity / W4-R0 correction and R1 closure | [Joint-context adapter](../60-evidence/s11/s11-o2-joint-context-local.md) | [Windows disposition](../60-evidence/s11/s11-o2-joint-context-windows-run-001.md#w4-r0-correction-received-and-w4-r1-disposition--2026-10-02); censored comparison stays NOT_ASSESSABLE. |
| Existing-material inventory / W2 scene geometry | [R3 inventory](../60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md) | [W2 frame14865 reconciliation](../60-evidence/s11/s11-o2-w2-f14865-scene-review.md); no forced identity or repeated inventory. |
| Candidate-guided chromatic cue / saved-output color measurement | [Color-side evidence](../60-evidence/s11/s11-o2-color-side-local.md) | Same-support BGR/gray and recorded bands; use the work plan for the current Windows handoff. |
| 2026-10-07 audit adoption / next A1 / rejected paired scorer | [adoption checkpoint](../60-evidence/s11/2026-10-07-audit-adoption-checkpoint.md) | Second audit §8: three finite lineage gaps; A0Q remains open; do not rerun the rejected scorer as a repair or overwrite original evidence. |
| Third audit / report context / worktree recovery | [preservation checkpoint](../60-evidence/s11/2026-10-07-audit-adoption-checkpoint.md#third-audit-and-worktree-preservation--2026-10-07) | Third audit §7: report repair can precede A1; report/event/Review scopes differ. Human ROI and report prototype are unadopted; recover source from the preserved ZIPs, full evidence from local snapshots. |
| Canonical private-Windows truth | `../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | JSON companion + current field procedure |
| Target-Windows qualification | `../../.agents/skills/windows-qualification/SKILL.md` | `../40-operations/s11-current-windows-field-qualification.md` |
| Retained but non-current work | `retained-commitments.md` | linked design/validation owner |
| Milestone sequencing | `roadmap.md` | work plan for exact current gate |

## Memory write rule

Add durable memory only when it prevents a likely repeated mistake, preserves a non-obvious architecture/rejected-alternative decision, records an expensive-to-rediscover owner relationship, or gives a long-horizon resume clue. Prefer the existing logic map/failure registry/current owner over creating another record when they already own the lesson.
