# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `VALIDATING`
**Current gate:** `Exact pushed R10 secure-Windows Base/Accum replay`
**Source authority:** `R10 architecture + R9 Windows diagnostic + R10 local evidence`

## Why R9 failed the field gate

The reviewed secure-Windows R9 replay remained Base 0/601 numeric Oil. R9
generated 5,221 initial continuation rows and retained 5,002 after track
opposition, but no calibrated dynamic seed or trajectory formed. Only 288 rows
passed the per-candidate motion-coverage gate and 27 retained local support;
none formed the required six-frame path. At the reviewed Base checkpoints the
nearest R9 candidate errors were 46 px at 540 s, 16 px at 634 s and 84 px at
674 s.

Accum confirmed five real Foam frames and stored them in `tracking.csv`, but
isolated Foam values were invisible in line-only graphs because composed
samples were invalid. Two additional real Foam rows 17 px above selected Oil
were rejected because Foam/Oil identity reused the much wider Oil temporal
jump tolerance. The Artifact editor no longer overlapped video, but its primary
actions were below the initial scroll fold.

## Implemented R10 boundary

R10 remains one generic detector/resolver for Base and Accum. It adds:

- a resizable horizontal **분석 영역 편집** layout with video on the left and
  first-view Artifact explanation/actions/lists on the right;
- a fixed-budget calibration pool that reserves vertically distributed local
  peaks without globally lowering thresholds or consuming ordinary authority;
- calibration-only long-horizon bootstrap using sparse registered-motion
  keyframes and safe continuation members rather than per-row motion coverage;
- path-level minimum span/direction/uniqueness checks, exact same-frame
  provenance and no interpolation;
- signed Oil/Foam composition: a positive `OilY - FoamY` above the small
  identity tolerance preserves both layers, while inverted/near-coincident
  boundaries remain aliases;
- a separate bounded strong-candidate alias screen only while Oil is unresolved;
  and
- visible point markers for every finite stored Foam observation in static and
  interactive graphs, regardless of whole-sample validity.

## Local accepted evidence

The exact R10 uncalibrated four-video replay produced 299 rows and 142 numeric
Oil rows. Checked truth remained numeric at 10/13 points with 5.85 px MAE and
11 px maximum error; every numeric row retained same-frame provenance. Public
Foam remained zero on base/sample2/sample4, while sample3 retained five
reviewed early Foam observations and its unclear/changing-focus 39–90 s span
remained conservatively missing.

User-like sample4 lower-rim calibration changed Oil coverage 76→81/113 while
public Foam stayed zero and checked truth remained 2/5 numeric with 0.5 px
MAE/max error. A 17 px dynamic Foam layer above public Oil survives even when
Oil temporal jump is 64 px, while inverted topology remains rejected. At
980×700 the editor showed all primary Artifact actions without scrolling.

Direct debug-disabled detector timing over the same 113 in-memory sample4
frames was 7.062 s off (62.5 ms/frame) and 7.182 s on (63.6 ms/frame). The R9
local reference was 7.146/7.296 s, so R10 did not add a material per-frame
regression in this local diagnostic.

The full repository regression passed with 1,562 tests in 114.78 s; R10
compile, focused integration and exact replay gates also passed.

## Current executable action

Push the exact final R10 head once, then execute the
[R10 Windows checklist](../40-operations/manual-gui-windows-checklist.md#s11-r10-secure-baseaccum-calibrated-path-and-layer)
on the private Base/Accum videos.

At 100%, 125% and 150% scale, verify the editor first view, resize/maximize,
splitter, selection highlight and reviewed bulk Artifact application. Run both
Glasses with the saved templates and preserve the exact Recipe/video/session
identity.

For Base, reconcile source-frame Oil around 540, 634 and 674 s. Record retained
calibrated rows, path membership, motion-keyframe membership, first numeric
acquisition, coverage and every long missing/wrong-interface run. Require zero
public Foam. A static or wrong path is a failure regardless of coverage.

For Accum, independently inspect Oil rise, Foam onset, the separated Oil/Foam
layer, highest Oil and recovery. Confirm finite confirmed Foam appears in CSV
and graph even when `is_valid=False`. Every alias rejection must expose the
effective identity rule and exact Oil row; Oil temporal jump may not erase a
distinct layer.

Every numeric Oil requires an exact same-frame candidate. Missing Oil remains
missing; the confirmed initial state may continue only as the labeled graph
assumption and must not create CSV Oil, extrema, events or captures. Compare
debug-disabled detector time with R9 on the same Windows machine. Local gates
do not establish private-field or general-field accuracy.

## Authority links

- [R10 architecture](../20-architecture/s11-r10-calibrated-path-and-layer-architecture.md)
- [R10 validation](../30-validation/s11-r10-calibrated-path-and-layer-validation.md)
- [R10 local evidence](../60-evidence/s11/s11-r10-calibrated-path-and-layer.md)
- [R9 Windows root cause](../50-diagnostics/s11/s11-r9-windows-calibrated-observation-diagnostic.md)
- [Durable detector responsibility](../20-architecture/s11-detector-responsibility-architecture.md)
- [Result observation/report architecture](../20-architecture/result-observation-report-architecture.md)
- [Windows field-workflow checklist](../40-operations/manual-gui-windows-checklist.md)
