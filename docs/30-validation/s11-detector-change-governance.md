# S11 Detector Change Governance

**Status:** current mechanical/evidence contract for S11 detector changes.

The `s11-detector-change` Skill owns task routing and bounded history recall. This document owns the durable History Review / Detector Governance record shape and the checker contract.

## Applicability

Apply this contract when changing S11 detector vision/control-flow/publication code, S11 detector architecture/validation, or S11 diagnostics/evidence including Windows field records. It does not make unrelated UI/application work a detector change.

Current implementation truth is owned by `docs/20-architecture/s11-current-detector-logic-map.md`; durable failed-mechanism history is owned by `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`. Current architecture/validation/reviewed-truth owners retain their own authority.

## Architecture/design History Review

A changed S11 architecture/design document must contain one completed block:

```markdown
## History Review

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`
- Failure-registry entries: `S11-F08`, `S11-F10`
- Prior mechanisms reviewed: <specific relevant mechanisms/evidence>
- Prior mechanisms rejected: <what is not being repeated and why>
- Preserved contracts: <current contracts preserved>
- Difference from prior failures: <specific difference or constrained non-change>
- Logic-map impact: NONE — <meaningful reason>
- Failure-registry impact: NONE — <meaningful reason>
```

Use `UPDATED — <reason>` only when the corresponding owner file changes in the same change. Every node/failure ID must exist in the current owners. `NONE` requires a real reason; `N/A`, blank, or a placeholder is invalid.

## Diagnostics/evidence Detector Governance

A changed S11 diagnostic/evidence record must contain one completed block:

```markdown
## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F07`, `S11-F08`
- First harmful stage: <earliest supported stage, or explicitly unknown with missing evidence>
- Logic-map impact: NONE — <meaningful reason>
- Failure-registry impact: NONE — <meaningful reason>
```

Field records must distinguish observed facts, inference, and named unknowns and point to the current validation/reviewed-truth authority.

## Checker

During detector work run:

```bash
python3 scripts/check_detector_governance.py --base-ref <base-ref> --include-worktree
```

Resolve every finding before review. Hooks/CI may invoke the same checker on committed ranges. Do not edit the logic map or failure registry merely to manufacture a passing governance block.
