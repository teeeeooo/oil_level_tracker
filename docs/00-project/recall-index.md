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
| Known detector mechanism failures / no-repeat rules | `../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | one referenced diagnostic/evidence record |
| Canonical private-Windows truth | `../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | JSON companion + current field procedure |
| Target-Windows qualification | `../../.agents/skills/windows-qualification/SKILL.md` | `../40-operations/s11-current-windows-field-qualification.md` |
| Retained but non-current work | `retained-commitments.md` | linked design/validation owner |
| Milestone sequencing | `roadmap.md` | work plan for exact current gate |

## Memory write rule

Add durable memory only when it prevents a likely repeated mistake, preserves a non-obvious architecture/rejected-alternative decision, records an expensive-to-rediscover owner relationship, or gives a long-horizon resume clue. Prefer the existing logic map/failure registry/current owner over creating another record when they already own the lesson.
