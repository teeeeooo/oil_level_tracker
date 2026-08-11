# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `VALIDATING`
**Current gate:** `Exact pushed R7 secure-Windows Base/Accum holdout`
**Source authority:** `R7 architecture + local evidence + Windows checklist`

## Accepted local implementation

The earlier secure-Windows Base/Accum replay rejected R6:

- Base published only `121/601` valid samples, remained `UNKNOWN_REVIEW` for
  `79.9%`, selected weak ambiguous shadows at wrong rows and still produced
  false Foam although direct review found none;
- Accum published only `19/601` valid samples, remained `UNKNOWN_REVIEW` for
  `96.8%`, created a false draining path while empty and missed the visible
  rising cycle until the later high; and
- R6 correctly stopped prior-only detector coverage but also disabled the
  required retrospective interpretation of the leading confirmed FULL/EMPTY
  state.

R7 has replaced those owners in production. The completed-window resolver now
assigns typed candidate authority, ignores old current-frame temporal selection,
publishes only same-frame Oil coordinates, confirms Foam from multi-frame
registered material evolution and restricts event/report authority to trusted
anchors. Confirmed initial FULL/EMPTY is interpreted only in a separate leading
prefix after two direction-compatible R7 anchors; it never changes raw samples,
observed coverage or numeric Oil.

Local repository regression and the isolated four-video replay passed. The
checked corpus retained 108 numeric observations across 299 sampled rows; this
is publication density, not accuracy. Checked truth was numeric at 9/13 points
with 5.28 px detected-point MAE and 11 px maximum error. Every numeric row has
same-frame provenance, Foam-absent sample controls publish no Foam, and directly
rejected sample4 rim/texture partitions remain non-numeric.

The accepted measurements and limits are in the
[R7 local evidence](../60-evidence/s11/s11-r7-evidence-tiered-trajectory.md).
Sample3's difficult middle interval and late sample4 reacquisition remain
conservative gaps; no general-field accuracy claim is made.

## Current executable action

Record the exact pushed `main` SHA and replay it on the private Base/Accum
workflow using the
[S11-R7 Windows checklist](../40-operations/manual-gui-windows-checklist.md#s11-r7-secure-baseaccum-holdout).
Preserve the private video/Recipe identity, initial confirmations, cadence,
tracking CSV, events, report, debug overlay and representative source captures.
Do not compare only aggregate coverage or state distribution.

Required field outcomes:

- Base must have zero public Foam, a separately inferred leading FULL interval,
  and a correct descending/low/recovery trajectory without the fixed glare or
  zero-line shadow.
- Accum must have a separately inferred leading EMPTY interval, no empty-glass
  Oil path, timely rising-boundary acquisition, bounded real Foam and correct
  high/fall landmarks.

Any false Base Foam, empty-Accum trajectory, ambiguous-only reacquisition or
gross wrong extremum is a field failure independent of coverage.

If direct images show a true interface present in the raw candidate lattice but
R7 selects another row or stays UNKNOWN, reopen final authority/scoring. If the
true interface is absent from the raw lattice in clear frames, stop score tuning
and classify representation/acquisition as the blocker. Report smoothing,
initial-state inference and event post-processing may not be used to conceal
either failure.

## Authority links

- [R7 architecture](../20-architecture/s11-r7-evidence-tiered-trajectory-architecture.md)
- [R7 validation contract](../30-validation/s11-r7-evidence-tiered-trajectory-validation.md)
- [R7 local evidence](../60-evidence/s11/s11-r7-evidence-tiered-trajectory.md)
- [R7 checked-video diagnostic](../50-diagnostics/s11/s11-r7-checked-video-direct-image-reconciliation.md)
- [R6 private field failure](../50-diagnostics/s11/s11-r6-secure-windows-field-failure.md)
- [R6 historical architecture](../20-architecture/s11-r6-optics-aware-observation-architecture.md)
- [Windows field-workflow checklist](../40-operations/manual-gui-windows-checklist.md)
