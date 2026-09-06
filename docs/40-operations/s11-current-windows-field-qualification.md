# S11 Current Windows Field Qualification

**Status:** `ACTIVE PROCEDURE` — candidate-current, revision-neutral.

This document is the executable target-Windows field procedure for whichever S11 detector candidate the current Work Plan names. It intentionally does not hard-code R7–R12 or any future revision number. A candidate becomes the subject of this procedure only when `docs/00-project/work-plan.md` and the user's granted scope make Windows qualification current.

## 1. Preconditions and identity

Before running private media:

1. Confirm Windows qualification is authorized and identify the candidate from `docs/00-project/work-plan.md`.
2. Record the exact pushed source SHA being qualified. Do not qualify an unpushed or subsequently mutated head as though it were the reviewed candidate.
3. Read the candidate's current architecture and validation/work specification linked by the Work Plan. Record expected detector/resolver/schema identities from those owners rather than from historical checklists.
4. Read `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` and `docs/30-validation/windows_sample1_heating_coldstart.reviewed-truth.json` completely enough to enumerate all nine `WS1-*` segments.
5. Run the `windows-qualification` and `s11-detector-change` Skill contracts. Resolve any required governance/history owner before interpreting results.

If source, candidate identity, or reviewed-truth authority is ambiguous, stop before execution rather than blending revision evidence.

## 2. Private source identity

For `windows_sample1_heating_coldstart`, record without exposing the real filename:

- SHA-256;
- byte size;
- width and height;
- FPS;
- duration; and
- Recipe/Glass/ROI settings used for the run.

Use the operator alias only. The source fingerprint strengthens identity; it does not redefine the reviewed timeline.

## 3. Execute the supported production path

Run the current supported Windows production workflow with the candidate named by the Work Plan. Preserve the normal detector, completed-window resolver, publication/report path, and same-frame provenance owners.

Do not:

- tune thresholds or add case-specific configuration during qualification;
- use detector proposals, overlays, prior row counts, graph bridges, or an old bundle as physical truth;
- interpolate/carry a missing numeric observation;
- replay a historical R7–R12 procedure instead of the current candidate contract; or
- convert a diagnostic-only trace field into publication authority.

Collect the current validation contract's required runtime/performance/provenance evidence. General GUI scaling and packaging obligations remain in `manual-gui-windows-checklist.md` when those surfaces are part of the current qualification scope.

## 4. Reconcile all reviewed segments

Report every segment from the reviewed-truth owner individually:

- `WS1-BASE-FULL-PREFIX`
- `WS1-BASE-DRAIN`
- `WS1-BASE-RAPID-REFILL`
- `WS1-BASE-FULL-SUFFIX`
- `WS1-ACCUM-EMPTY`
- `WS1-ACCUM-ENTRY-SPLASH`
- `WS1-ACCUM-FOAM-LAYERED`
- `WS1-ACCUM-POST-FOAM`
- `WS1-ACCUM-DRAIN`

For each segment record sampled coverage, Oil/Foam numeric runs, selected source-Y range/direction where physically reviewable, longest missing/wrong-interface run, relevant lifecycle/owner transitions when available, and `PASS`, `FAIL`, or `NOT_EVALUATED`.

Exact coordinate accuracy is `NOT_EVALUATED` where no reviewed source-Y anchor exists. Presence/absence, material identity, ordering, direction, false-boundary rejection, and same-frame provenance remain valid acceptance dimensions without exact Y anchors.

## 5. Field disposition

A run is not `FIELD PASS` merely because local/canonical tests passed or aggregate coverage improved. Apply the current candidate validation contract plus canonical reviewed truth.

Any supported failure must identify the earliest harmful stage that the available evidence can establish. If the stage cannot be established, record the missing evidence and keep it unknown rather than inventing a causal mechanism.

A field `FAIL` does not authorize another detector revision automatically. Any follow-on behavior change starts from the newly observed failing stage and the current failure registry/logic map under a separately authorized detector task.

## 6. Evidence and closeout

Store completed field measurements under the current `docs/60-evidence/s11/` owner; causal investigation belongs under `docs/50-diagnostics/s11/`. Include the required `## Detector Governance` block from `docs/30-validation/s11-detector-change-governance.md`.

Update `docs/00-project/work-plan.md` only when field disposition, accepted baseline, named blocker/unknown, or next transition changes. Update the Roadmap only if formal milestone state changes. Do not rewrite archived R7–R12 procedures or older field evidence to match the new result.
