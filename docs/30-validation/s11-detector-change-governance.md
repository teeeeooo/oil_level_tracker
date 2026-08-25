# S11 Detector Change Governance

**Status:** current validation/process contract for S11 detector design, implementation, and field evidence.

This contract prevents a new detector mechanism or field result from silently bypassing the current implementation map and durable failure history. It is a review gate, not a reason to create meaningless documentation edits.

## Scope

Use this contract before design or implementation, and before recording or changing S11 detector diagnostics/evidence, including Windows field records. It applies to:

- S11 detector vision/control-flow/publication code in the trigger surface named by [`s11-current-detector-logic-map.md`](../20-architecture/s11-current-detector-logic-map.md), including completed-window and publication boundaries;
- S11 detector architecture/design documents; and
- S11 detector diagnostics and evidence, including Windows field records.

It does not turn broad application/UI changes, unrelated documentation, or presentation-only work into detector changes. The current map is the implementation owner; the [failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md) is the durable causal-history owner. Current architecture, validation, and reviewed-truth documents remain authoritative for their own responsibilities. This contract routes those authorities together; it does not replace them.

## Mandatory order

1. Read [`docs/README.md`](../README.md) and classify the work.
2. Read/scan the [logic-map quick start / design index](../20-architecture/s11-current-detector-logic-map.md#quick-start--design-index) and [failure quick index](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md#quick-failure-index-f01f10) completely.
3. Use the indexes to identify every affected logic-map node, owner boundary, and referenced prior failure ID. Then read the full detail for every affected node and referenced failure entry; do not skip relevant detail because the index summarizes it.
4. Read the relevant current architecture/design, validation, and reviewed-truth authority. Do not use historical evidence or diagnostics as a substitute for a current owner.
5. Record the matching block below in the changed architecture/design document or field diagnostic/evidence record. Use semantic node IDs from the map and failure IDs from the registry.
6. Run `python3 scripts/check_detector_governance.py --base-ref <base-ref> --include-worktree` while editing and resolve every finding before review. The pre-push hook and CI invoke the same checker on committed ranges.

If the logic map or failure registry itself changes, explain the owner impact in the matching block and change that owner in the same change. If an owner is unchanged, write `NONE — <meaningful reason>`; “not applicable”, “N/A”, or a blank is not a reason. `UPDATED` is permitted only when that owner file is actually changed. Do not edit an owner only to manufacture a passing diff: a documentation change must express a real contract, causal-history, or evidence change.

## History Review

Architecture/design documents must include one completed block with these fields. Keep the heading and field labels so the checker can validate it.

```markdown
## History Review

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`
- Failure-registry entries: `S11-F08`, `S11-F10`
- Prior mechanisms reviewed: <specific prior mechanisms and the evidence/diagnostics reviewed>
- Prior mechanisms rejected: <mechanisms rejected and why they do not recur here>
- Preserved contracts: <current architecture/validation/truth contracts preserved>
- Difference from prior failures: <specific difference, or why this is a constrained non-change>
- Logic-map impact: NONE — <meaningful reason the current implementation owner map is unchanged>
- Failure-registry impact: NONE — <meaningful reason no causal mechanism entry changes>
```

`UPDATED — <reason>` may be used for either impact when the corresponding owner file is part of the same change. Every referenced node must exist in the current map, and every referenced failure entry must exist in the registry.

## Detector Governance

S11 detector diagnostics/evidence must include one completed block. It ties an observation to the earliest harmful stage rather than treating a coverage number as a diagnosis.

```markdown
## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F07`, `S11-F08`
- First harmful stage: <earliest supported node/stage, or explicitly unknown with the missing evidence>
- Logic-map impact: NONE — <meaningful reason the current implementation owner map is unchanged>
- Failure-registry impact: NONE — <meaningful reason no causal mechanism entry changes>
```

`UPDATED — <reason>` may be used for either impact when the corresponding owner file is part of the same change. Every referenced node and failure entry must exist in the current owners. A field record must distinguish observed facts, inference, and named unknowns, and must identify the relevant current validation/truth authority.

## Source of authority and review standard

The logic map names what code currently executes. The failure registry records mechanisms that have already failed or remain guarded. The current architecture and validation contracts define intended responsibility and acceptance; reviewed-truth documents define accepted field truth. A governance block is valid only when its references and impact statements are specific enough for a reviewer to follow those sources. It is not valid to add an unrelated link, copy a historical count without causal relevance, or touch the map/registry only to avoid a `NONE` explanation.
