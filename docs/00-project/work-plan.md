# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** `R6 optics-aware current-frame evidence and bounded temporal observation replacement`
**Source authority:** `R5 secure-Windows field failure; R5 local acceptance withdrawn`

## Why R6 is active

The synchronized private Base/Accum replay disproved R5's local acceptance. R5 increased nominal valid coverage to `98.8–99.8%`, but most of that coverage was not image-supported:

- Base visually contains no Foam, while `490/601` frames became `FULL_WITH_FOAM`; fixed vertical light streaks, glare and caustic reflection were published as Foam.
- Accum remained `EMPTY_NO_INTERFACE` for `555/601` frames and missed the visible rise/Foam/high/fall cycle until roughly `52 s` after the visual maximum.
- an initial FULL/EMPTY prior was reused as recurring state evidence, and raw Foam candidates could regain final publication authority after current-frame rejection.
- Oil and Foam sequence selection consumed candidate scores produced from the same weak saturation-only glare model; a smoother path therefore amplified incorrect evidence instead of repairing detection.

R5 remains historical evidence for a failed approach. It is not the production acceptance baseline and must not be tuned with additional threshold exceptions.

## Active owners

- Architecture: [S11-R6 Optics-Aware Observation Architecture](../20-architecture/s11-r6-optics-aware-observation-architecture.md)
- Validation: [S11-R6 Optics-Aware Observation Validation](../30-validation/s11-r6-optics-aware-observation-validation.md)
- Field root cause: [S11-R5 Secure-Windows Field Failure](../50-diagnostics/s11/s11-r5-secure-windows-field-failure.md)
- Historical R5 evidence: [S11-R5 Sequence-First Observation Evidence](../60-evidence/s11/s11-r5-sequence-first-observation.md)

## Executable sequence

1. replace the R5 sequence/publication seam rather than stacking an R6 branch on it;
2. make Oil proposal generation independent of unconfirmed Foam and expose explicit candidate eligibility/provenance;
3. replace saturation-only glare with bounded optics-aware opposition and exposure-compensated temporal evidence;
4. resolve Oil, affirmative no-interface state and Foam independently, then compose one public observation;
5. validate directly against checked-in source images, truth/provisional annotations and controlled negatives;
6. run the same build on the private Windows Base/Accum holdout; and
7. reconnect event/report acceptance only after detector observations pass the field gate.

## Cleanup boundary

R6 is a vertical replacement, not an additional reducer:

- remove R5's `SequenceTrajectoryResolver` and `SequenceFoamEpisodeResolver` after their replacement tests migrate;
- do not infer state evidence from a previously projected `fill_state`;
- do not count prior-only FULL/EMPTY as valid detector coverage;
- do not let a raw/rejected Foam candidate mask Oil or become public Foam;
- keep current-frame preview and completed-analysis publication under one evidence vocabulary; and
- retain debug traces and historical documents, but remove obsolete runtime owners and compatibility branches once no caller remains.

## Acceptance boundary

Aggregate valid coverage is not an acceptance measure. R6 is evaluated with:

- observed Oil coverage only on visually supportable intervals;
- image-supported FULL/EMPTY duration, reported separately from prior-only context;
- gross wrong-interface duration and longest wrong-track run;
- false published Foam frames/episodes on Foam-absent intervals;
- acquisition latency after a visually supportable boundary appears;
- Oil coordinate error at checked-in truth anchors; and
- event timing only after the underlying observation track is visually accepted.

Local samples cannot close the private field defect. The exact R6 head must produce synchronized overlays and detector/report output on Windows. A Base Foam false episode, an Accum initial-state lock-in through the visible rise, or a long fixed-glare Oil track fails the gate even if aggregate coverage increases.
