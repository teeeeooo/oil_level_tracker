# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `VALIDATING`
**Current gate:** `Exact pushed R8 secure-Windows Base/Accum replay`
**Source authority:** `R8 architecture + R7 Windows diagnostic + R8 local evidence`

## Accepted R8 implementation

The secure-Windows R7 replay failed: Base published 0/601 numeric Oil and Accum
37/601. Base had real-boundary candidates but almost no anchor/trajectory graph;
Accum lost 99 frames to Foam-derived texture conflict and also hit an overly
short pre-anchor continuation bound. Real Accum Foam was confirmed internally
but dropped from public output.

R8 replaces those responsibilities with one generic detector:

- Foam texture no longer vetoes independent Oil;
- dynamic material paths can become bounded continuation, never motion-only
  anchors;
- raster-only and distributed-Sobel high-recall proposals are additive and
  bounded;
- confirmed Foam is preserved through unavailable Oil/state unless the Foam
  track aliases a very strong Oil boundary;
- the ellipse editor lets a user select detector-proposed point/line/region
  artifacts in normalized geometry, while excluded candidates stay traceable
  and do not consume the ordinary proposal budget;
- if no Oil is ever observed, confirmed initial FULL/EMPTY is shown through the
  graph as an explicit state assumption without numeric Oil; and
- repeated raster/sector loops are vectorized.

The local four-video replay passed with 299 rows and 142 numeric Oil samples.
Checked truth was numeric at 10/13 points with 5.85 px MAE and 11 px maximum
error. All numeric Oil has same-frame provenance; Base/sample2/sample4 public
Foam is zero and sample3 retains the reviewed early Foam episodes. A user-like
sample4 lower-rim calibration improved Oil coverage 76→81 without changing
truth error or introducing Foam. Profiling reduced sample4 detector cumulative
time 27.31→14.63 s.

## Current executable action

Push the exact final R8 head, then execute the
[R8 Windows checklist](../40-operations/manual-gui-windows-checklist.md#s11-r8-secure-baseaccum-observation-recovery)
on the private Base/Accum videos. For each Glass record calibration-off and
user-calibrated runs. The operator must review and select proposals; do not
automatically accept every detector suggestion.

Base must publish zero Foam and recover the reviewed descent/low/recovery
trajectory without following selected glare/rim/scratch geometry. Accum must
acquire the rise, preserve the real Foam episode and high/fall behavior, and
must not retain empty state through a visible boundary. Every numeric coordinate
must retain same-frame provenance. Initial-state graph hold must remain visibly
labeled and must not change raw CSV Oil or observed coverage.

Measure debug-disabled Windows frame time against the same R7 machine/workflow.
Any false Base Foam, long artifact Oil track, missing real Accum Foam, or
calibration that suppresses actual Oil is a field failure regardless of nominal
coverage.

## Authority links

- [R8 architecture](../20-architecture/s11-r8-observation-recovery-architecture.md)
- [R8 validation](../30-validation/s11-r8-observation-recovery-validation.md)
- [R8 local evidence](../60-evidence/s11/s11-r8-observation-recovery.md)
- [R7 Windows root cause](../50-diagnostics/s11/s11-r7-windows-observation-recovery-diagnostic.md)
- [R7 historical architecture](../20-architecture/s11-r7-evidence-tiered-trajectory-architecture.md)
- [Windows field-workflow checklist](../40-operations/manual-gui-windows-checklist.md)
