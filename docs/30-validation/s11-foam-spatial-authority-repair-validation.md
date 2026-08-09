# S11 Foam/Spatial Authority Repair Validation Contract

**Status:** `ACCEPTED — see source-tree/corpus evidence`

Acceptance evidence is [`../60-evidence/s11/s11-r2-foam-spatial-authority-repair.md`](../60-evidence/s11/s11-r2-foam-spatial-authority-repair.md).

## Scope

This contract accepts or rejects the bounded R2 design in [`../20-architecture/s11-foam-spatial-authority-repair-architecture.md`](../20-architecture/s11-foam-spatial-authority-repair-architecture.md). The objective is a more faithful observed Oil trajectory, not a fixed publication percentage.

The comparison baseline is exact head `86937d4f3dd55396b3ecf39efaa4e9a6ec4fb8ab`: `109/299` qualification numerics and `8/13` user-confirmed truth numerics with `5.4375 px` MAE.

## Required evidence

Run the production `OpenCvPhaseDetector` with matching Recipe, static-artifact learning and serialized temporal owner over the complete fixed 2 FPS qualification windows for `base_sample_1`, `sample2`, `sample3` and `sample4`.

Report for each video and the corpus:

- numeric observations and coverage;
- longest missing interval;
- exact added, removed and changed numeric timestamps/frames;
- tracking-stream fingerprint;
- user-confirmed truth numeric count and localization error;
- visual classification of every material stream change against the source Glass ROI.

An increased total count is neither necessary nor sufficient. Removing a gross wrong-interface excursion may justify losing a false numeric; adding anchors is beneficial only when they follow the same visible physical interface.

## Focused acceptance examples

The source implementation must prove:

1. Foam-separated horizontal support below `0.30` cannot acquire D5 boundary authority, while support at or above the floor remains eligible subject to all other rules;
2. under authoritative accepted-Foam context, a path-invalid preliminary relative boundary cannot stop evaluation of a different existing full-path candidate, while the same route remains closed without accepted Foam;
3. an accepted boundary outside authoritative-Foam context cannot be challenged through R2;
4. an incumbent that is not artifact-dominant or that passes its own Spatial path remains unchanged;
5. a challenger without at least `0.08` semantic-margin improvement remains non-authoritative;
6. a qualifying challenger still resolves through canonical current-frame publication and the unchanged serialized reducer.
7. weak-broad/full-width texture remains eligible when spatially separate from the accepted Foam component, but remains non-numeric when the accepted component dominates its row and can explain that same weak texture; established sample3 D5 Oil anchors must remain unchanged.

## Preservation suite

Run the focused Oil/Spatial/Foam tests and the retained detector preservation suite covering:

- positive no-interface and unavailable evidence;
- glare, collision, border and exclusion conflicts;
- structural and explanatory-overlay false lines;
- Foam publication/topology and Oil-below-Foam behavior;
- accepted low-light Foam texture that must not become Oil, paired with component-separated weak-boundary and existing real D5 positive controls;
- current-frame ambiguity, canonical publication and serialized reacquisition;
- existing report observation-stream and display-only bridge invariants.

No retained negative may become numeric merely because its weak Spatial eligibility was broadened; R2 does not authorize such broadening.

## Report-output check

Generate the user observation report from the accepted replay and confirm that:

- direct observed runs, dashed display-only bridges and missing cursor/CSV values retain their existing meaning;
- corrected detector anchors remove any corresponding false highest/lowest landmark rather than being hidden by presentation smoothing;
- highest, lowest and Foam episode captures still reference actual stored observations and source frames;
- detector/debug evidence remains outside the main user narrative.

## Acceptance and stop conditions

Accept R2 only if the changed real-video observations are visually defensible, retained hard-safety tests pass and no unchanged sample acquires a new wrong-interface family. A small or zero net coverage change is acceptable when graph fidelity improves through removal/correction of misleading extrema.

Stop and revert or narrow the repair if it creates overlay/structure numerics, weakens no-interface/visibility/Foam topology, needs identity-specific exceptions, or requires relaxing the accepted Spatial path thresholds. Further detector tuning requires a new diagnosed general failure class and a separate design update.

## Claim boundary

Passing this contract proves improvement only on the available repository corpus and controlled regressions. It does not establish general-field accuracy or replace final target-Windows workflow validation.
