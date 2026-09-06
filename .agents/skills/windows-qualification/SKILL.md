---
name: windows-qualification
description: Use for deliberate target-Windows field qualification of the current Oil Level Tracker candidate, including exact-head identity, canonical reviewed truth, execution evidence, field disposition, and post-run state updates. Do not use for ordinary local detector iteration.
---

# Windows Qualification

Use only for an actual or planned target-Windows qualification task. This skill does not authorize the qualification; it defines the repository procedure once that work is in scope.

## Resolve the current candidate

1. Read `docs/00-project/work-plan.md`. It owns whether Windows qualification is current/authorized and which candidate is being qualified.
2. Read the current architecture/validation owner named there. Do not hard-code an old revision number or reuse an R7–R12 procedure.
3. Read `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` and `docs/30-validation/windows_sample1_heating_coldstart.reviewed-truth.json` before interpreting detector output.
4. Use `docs/40-operations/s11-current-windows-field-qualification.md` as the executable procedure.

## Qualification invariants

- Bind evidence to the exact pushed/qualified source identity and runtime detector/resolver identity.
- Detector output, overlays, historical row counts, and candidate proposals are not truth; reviewed physical truth is the oracle.
- Distinguish observed fact, inference, and named unknown.
- Preserve field `FAIL` until the current acceptance contract is actually satisfied; local/canonical PASS is not field PASS.
- A failed field run diagnoses the earliest supported harmful stage. It does not authorize a new detector revision automatically.
- Do not replay private field media as a routine development dependency.

## Closeout

Write completed measurements/results under the current `60-evidence/` or `50-diagnostics/` owner as appropriate, including the required Detector Governance block. Update `work-plan.md` only when the current field disposition or next transition actually changes.
