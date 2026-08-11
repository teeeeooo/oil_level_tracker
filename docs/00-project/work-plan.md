# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `VALIDATING`
**Current gate:** `Exact-head secure-Windows R6 Base/Accum holdout`
**Source authority:** `R6 local evidence + R5 secure-Windows field failure`

## Local result accepted for field validation

R6 completed the planned vertical replacement and local direct-image gate:

- deleted the R5 trajectory/Foam runtime owners instead of stacking a new
  reducer over them;
- made Oil candidate generation independent of Foam publication;
- added optics-aware caustic/overlay opposition, generic material paths and
  registered exposure-compensated raster evidence;
- limited FULL/EMPTY to image-supported state and initial state to context;
- retained same-frame coordinates only, with UNKNOWN and display-only dashed
  graph gaps where no coordinate is supported; and
- passed `1,502` repository tests plus the deterministic four-video replay.

The local replay publishes `190/299` numeric Oil rows, all with same-frame
provenance. This number is observation density, not accuracy. Direct review and
truth/provisional reconciliation are in the
[R6 evidence](../60-evidence/s11/s11-r6-optics-aware-observation.md) and
[checked-video diagnostic](../50-diagnostics/s11/s11-r6-checked-video-reconciliation.md).

## Current executable action

Run the exact pushed head on the private Windows Base/Accum video using the
existing synchronized workflow and review source frames, overlays, tracking CSV,
events and report together.

Pass requires:

- Base: no published Foam over the visually Foam-absent run; initial FULL stays
  context only; the real top-entering descent, low and recovery are acquired
  without following the fixed glare/caustic;
- Accum: EMPTY is retained only while current image evidence supports it; the
  rising boundary is acquired before the former mid-Glass lock-in; high/fall are
  followed; and only the bounded turbulent Foam episode is published;
- both: every numeric coordinate has a supportable same-frame source candidate,
  and lifecycle captures/timestamps correspond to the accepted observation
  trajectory.

A Base false Foam episode, Accum prior lock-in through visible Oil, or a long
fixed-optics Oil track is a field FAIL independent of aggregate coverage.

## Authority links

- [R6 architecture](../20-architecture/s11-r6-optics-aware-observation-architecture.md)
- [R6 validation contract](../30-validation/s11-r6-optics-aware-observation-validation.md)
- [R6 local evidence](../60-evidence/s11/s11-r6-optics-aware-observation.md)
- [R5 private field failure](../50-diagnostics/s11/s11-r5-secure-windows-field-failure.md)
- [Windows field-workflow checklist](../40-operations/manual-gui-windows-checklist.md)
