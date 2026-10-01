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
| O2 partial-path pooling versus holistic identity; proposed W0–W7 follow-up | [W1 source review and executable counter-controls](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md) | October audit §A01 / W1; current work plan; witness review semantics; existing score/evaluation owners |
| W3 separated targets and existing packet/decision audit | [W3 local evidence](../60-evidence/s11/s11-o2-w3-target-evaluation-local.md) | Prediction v2/report v3 compatibility; scalar truth remains absent; [Windows audit](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md) verifies context availability; row admission is not final selection; W4 discrimination remains open |
| W4 paired-scale local-position experiment | [Local evidence](../60-evidence/s11/s11-o2-w4-paired-scale-local.md) | Pair differences before reducing scales; identical joint support; can regress/cycle, no total rank or identity repair; [Windows result](../60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md): primary +1/0, no control regression; one-scale controls cannot distinguish reducers, two support-only gains excluded; follow-up shows residual reversal in all scales and missing joint support; inspection complete, no promotion |
| Candidate-identity context semantics / local sampling extent | [Source audit and raster controls](../60-evidence/s11/s11-o2-identity-context-source-audit.md) | material is raw appearance, static is persistence; distinct wider rasters can share a candidate witness; [Windows reconciliation](../60-evidence/s11/s11-o2-identity-context-windows-review-001.md) closes geometry/OCR checks; human reports idx0/idx20 ambiguity even with approximately +/-5 s of formation/motion context; preserve labels/scores with truth-uncertainty qualification; no repeat clip requested |
| Human truth uncertainty versus model abstention | [Evaluation audit and controls](../60-evidence/s11/s11-o2-reference-uncertainty-evaluation-audit.md) | Existing uncertain/unreviewed labels differ from model UNRESOLVED/UNOBSERVABLE and missing predictions; note text does not relabel; changing truth can remove a reversed pair without a scoring gain; original outputs stay pinned |
| Structure-negative context omitted by O1/score projections | [Recorded-context local evidence](../60-evidence/s11/s11-o2-structure-context-audit-local.md) | Existing raw candidate features/penalties and recipe artifact templates; missing is not zero, unavailable fitting geometry does not imply no templates, registered matches are not identity truth; no gate replay; [Windows report](../60-evidence/s11/s11-o2-structure-context-audit-windows-run-001.md) reports 12/14 templates and code/artifact match; numeric follow-up constrains simple vetoes; typed texture uses max(features, penalties), missing template match is not zero; schema transcription resolved by reported True/111; investigation closed without promotion |
| Ordered full-height spatial-context hypothesis | [Local measurement prototype](../60-evidence/s11/s11-o2-spatial-context-prototype-local.md) | Reuses masked row means, records exact ordered rows/support outside O1 bands; remote return is new information but not identity; masked/identical/horizontal-permutation collisions remain; [source adapter and local entry controls](../60-evidence/s11/s11-o2-spatial-context-source-adapter-local.md) verified; original two-frame Windows measurement pending |
| Canonical private-Windows truth | `../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | JSON companion + current field procedure |
| Target-Windows qualification | `../../.agents/skills/windows-qualification/SKILL.md` | `../40-operations/s11-current-windows-field-qualification.md` |
| Retained but non-current work | `retained-commitments.md` | linked design/validation owner |
| Milestone sequencing | `roadmap.md` | work plan for exact current gate |

## Memory write rule

Add durable memory only when it prevents a likely repeated mistake, preserves a non-obvious architecture/rejected-alternative decision, records an expensive-to-rediscover owner relationship, or gives a long-horizon resume clue. Prefer the existing logic map/failure registry/current owner over creating another record when they already own the lesson.
