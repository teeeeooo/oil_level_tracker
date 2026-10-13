# S11 Detector Change Governance

**Status:** current mechanical/evidence contract for S11 detector changes.

The `s11-detector-change` Skill owns task routing and bounded history recall. This document owns the durable History Review / Detector Governance record shape and the checker contract.

## Applicability

Apply this contract when changing S11 detector vision/control-flow/publication code, S11 detector architecture/validation, or S11 diagnostics/evidence including Windows field records. It does not make unrelated UI/application work a detector change.

Current implementation truth is owned by `docs/20-architecture/s11-current-detector-logic-map.md`; durable failed-mechanism history is owned by `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`. Current architecture/validation/reviewed-truth owners retain their own authority.

### Source-only cosmetic exception

For ref-based checks, an existing detector Python file at the same path does not require a companion design update when its before/after AST and regular-file mode are identical. This covers ordinary comments and formatting without changing executable nodes, docstrings, constants, or type comments. Comparison uses the actual Git merge base and the checked head (or requested worktree content), never a worktree substitute for missing baseline evidence.

New/deleted/renamed files, mode/encoding/shebang changes, syntax failures, unavailable baseline text, and changed ASTs retain the existing gate. The path-only checker API has no exemption without before/after evidence. This is a narrow companion-document exemption, not proof of runtime/field acceptance or permission to change other contracts.

Validation/design/evidence Markdown still follows its existing contract: arbitrary typo, link, or acceptance prose changes cannot safely be classified by AST equality. No self-declared editorial bypass is supported.

## Existing-system review before execution

Before selecting a new detector hypothesis or running a new comparison, use the
[existing-feature map](../20-architecture/s11-current-detector-logic-map.md#existing-features-and-run-coverage)
to connect user setup, the actual experiment input, the executing owner and the
claimed output. The mandatory fields below belong in the existing design/evidence
block and may link to exact fields in an existing pinned preflight; do not create
a parallel manifest or a new document solely for this check.

- **Existing feature coverage:** identify relevant existing capabilities and their
  actual or planned input state, with Recipe/session/constructor/source evidence.
  Distinguish configured, empty/OFF, bypassed and unknown. Explain deliberate
  exclusions and the applicable prior result; feature presence in code is not
  evidence of use or failure. For Artifact/mask work, follow D2 through the later
  Local XY results in the recall index rather than stopping at an earlier proposal.
- **Execution scope:** name the entry path and which setup, frame, completed-sequence
  and publication stages are exercised or omitted, with the resulting claim limit.
  A raw feature probe may remain a raw feature probe; no full replay is required
  merely to fill this field. Planning-only or process/document changes explicitly
  state that no runtime was exercised and which responsibility is being reviewed.

Resolve missing input state only when it bears on the proposed conclusion; otherwise
record unknown and bound the claim. This is not a new user-approval gate. Historical
results and original artifacts remain frozen; reuse their recorded scope without
rerunning them. Check the changed draft before a new experiment as well as before
publication. The checker rejects absent/placeholder fields, but does not certify
the factual coverage or scientific sufficiency of their text.

## Architecture/design History Review

A changed S11 architecture/design document must contain one completed block:

```markdown
## History Review

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`
- Failure-registry entries: `S11-F08`, `S11-F10`
- Prior mechanisms reviewed: <specific relevant mechanisms/evidence>
- Prior mechanisms rejected: <what is not being repeated and why>
- Preserved contracts: <current contracts preserved>
- Existing feature coverage: <relevant existing capabilities, actual/planned input state and evidence>
- Execution scope: <entry path, exercised/omitted stages and claim limit, or explicit no-run scope>
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
- Existing feature coverage: <relevant existing capabilities, actual input state and evidence>
- Execution scope: <entry path, exercised/omitted stages and claim limit, or explicit no-run scope>
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
