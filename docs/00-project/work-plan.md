# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `IN PROGRESS`
**Current gate:** `R7 authority replacement and local direct-image validation`
**Source authority:** `R6 secure-Windows failure + R7 architecture/validation`

## Field result that reopened implementation

The secure-Windows Base/Accum replay rejected R6:

- Base published only `121/601` valid samples, remained `UNKNOWN_REVIEW` for
  `79.9%`, selected weak ambiguous shadows at wrong rows and still produced
  false Foam although direct review found none;
- Accum published only `19/601` valid samples, remained `UNKNOWN_REVIEW` for
  `96.8%`, created a false draining path while empty and missed the visible
  rising cycle until the later high; and
- R6 correctly stopped prior-only detector coverage but also disabled the
  required retrospective interpretation of the leading confirmed FULL/EMPTY
  state.

Source inspection found two coupled authority defects: old current-frame
`selected` candidates can become final anchors without an ambiguity ceiling,
while non-anchor same-frame paths are removed by a fixed small horizon. Foam
episodes can also be confirmed from one dynamic disturbance.

The exact causal record is the
[R6 field-failure diagnostic](../50-diagnostics/s11/s11-r6-secure-windows-field-failure.md).

## Current executable action

Implement the
[R7 Evidence-Tiered Trajectory Architecture](../20-architecture/s11-r7-evidence-tiered-trajectory-architecture.md)
under its [validation contract](../30-validation/s11-r7-evidence-tiered-trajectory-validation.md):

1. remove all old current-frame temporal selection fields from final anchor
   authority;
2. classify hypotheses as hard-invalid, candidate-only,
   continuation-eligible or anchor-eligible;
3. construct independent anchor clusters and retain same-frame continuation only
   inside a supported trajectory;
4. restore leading FULL/EMPTY retrospective interpretation without changing raw
   samples or observed coverage;
5. require multi-frame registered Foam onset/material evolution; and
6. restrict extrema and lifecycle events to anchor-supported evidence.

Run focused tests after each responsibility change, then the complete suite and
the deterministic four-video replay. Directly inspect every changed anchor,
Foam episode, long continuation and extremum against source frames. Exact R6
counts/fingerprints are not golden truth.

## Local acceptance boundary

Local PASS requires:

- current-frame `selected` identity has no effect on R7 output;
- no weak ambiguous path starts/reacquires or creates an extremum;
- sample2 stationary Oil remains observable;
- sample3 `30–60 s` communicates EMPTY/inflow/Foam/full without the fixed cap;
- sample4's annotated Foam-absent interval remains Foam-free;
- every numeric coordinate retains same-frame provenance;
- leading-state inference is separately persisted and visible in the report; and
- full regression and bounded runtime checks pass.

If direct images show the true interface missing from the raw candidate lattice
in clear frames, stop score work and classify representation/acquisition as the
blocker.

## Next field gate

After local acceptance, push the exact R7 head and replay it on the private
Base/Accum workflow.

- Base must have zero public Foam, a separately inferred leading FULL interval,
  and a correct descending/low/recovery trajectory without the fixed glare or
  zero-line shadow.
- Accum must have a separately inferred leading EMPTY interval, no empty-glass
  Oil path, timely rising-boundary acquisition, bounded real Foam and correct
  high/fall landmarks.

Any false Base Foam, empty-Accum trajectory, ambiguous-only reacquisition or
gross wrong extremum is a field failure independent of coverage.

## Authority links

- [R7 architecture](../20-architecture/s11-r7-evidence-tiered-trajectory-architecture.md)
- [R7 validation contract](../30-validation/s11-r7-evidence-tiered-trajectory-validation.md)
- [R6 private field failure](../50-diagnostics/s11/s11-r6-secure-windows-field-failure.md)
- [R6 historical architecture](../20-architecture/s11-r6-optics-aware-observation-architecture.md)
- [Windows field-workflow checklist](../40-operations/manual-gui-windows-checklist.md)
