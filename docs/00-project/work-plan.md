# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `VALIDATING`
**Current gate:** `Exact pushed R9 secure-Windows Base/Accum replay`
**Source authority:** `R9 architecture + R8 Windows diagnostic + R9 local evidence`

## Accepted R9 implementation

The secure-Windows R8 replay failed with Base 0/601 numeric Oil and Accum
189/601 numeric Oil that did not reliably separate the real Foam layer. Exact
source-frame reconciliation showed that Base lacked a near-boundary candidate
at two of three reviewed checkpoints, while Accum's separated Foam was rejected
through stale alias history. The R8 trace was recorded before final sequence
resolution and therefore omitted the final authority path.

R9 keeps one detector and adds:

- a responsive artifact editor with selected-proposal highlight, multi-select,
  select-all and explicit bulk Artifact apply;
- up to twelve calibration-only high-recall rows that do not consume normal
  proposal capacity or seed ordinary authority;
- a unique registered moving-path bootstrap only when no qualified anchor path
  exists;
- Oil/Foam alias continuation that requires new same-frame coincidence;
- final sequence authority/support/reject-stage annotation inside raw trace; and
- the existing non-numeric confirmed-initial-state graph hold.

An unsafe intermediate calibration reached 112/113 sample4 numeric but drifted
25–47.5 px late in the video. It was rejected. The final isolation boundary
restored the accepted 81/113 calibrated behavior and existing events.

## Local accepted evidence

The uncalibrated four-video replay produced 299 rows and 142 numeric Oil rows.
Checked truth was numeric at 10/13 points with 5.85 px MAE and 11 px maximum
error; every numeric row retained same-frame provenance. Public Foam remained
zero on base/sample2/sample4 and sample3 retained five reviewed early frames.

User-like sample4 lower-rim calibration changed Oil coverage 76→81/113 while
public Foam stayed zero and checked truth remained 2/5 numeric with 0.5 px
MAE/max error. Direct detector time was 7.146 s calibration-off and 7.296 s
calibration-on over 113 frames. The full suite passed with 1,557 tests.

## Current executable action

Push the exact final R9 head once, then execute the
[R9 Windows checklist](../40-operations/manual-gui-windows-checklist.md#s11-r9-secure-baseaccum-calibrated-observation)
on the private Base/Accum videos.

First verify the editor no longer overlaps the video and that single/multiple
proposal selection highlights the exact line or region. Preserve an uncalibrated
reference, then review and apply the persistent artifact proposals. Select-all
is allowed only after review; it is never automatic detector truth.

For Base, use source-frame overlays to re-establish the actual Oil Y near 540,
634 and 674 s. Record near-candidate availability, calibrated generator/seed
flags, first acquisition and wrong-interface/missing runs. Require zero public
Foam. For Accum, verify Oil rise, a distinct Oil/Foam pair near 672 s, the high
near 685 s and later observation. Inspect the final `sequence` trace member;
do not reverse-calculate authority from raw current-frame fields.

Every numeric Oil requires same-frame selection and every public Foam row must
belong to a confirmed dynamic episode. If Base remains all-missing, the graph
may show only the labeled confirmed-initial-state background; CSV Oil and
observed coverage remain empty. Compare debug-disabled detector time with R8 on
the same Windows machine. Any long wrong-interface run, false Base Foam, lost
real Accum Foam or automatic/unreviewed calibration is a field failure.

## Authority links

- [R9 architecture](../20-architecture/s11-r9-calibrated-observation-architecture.md)
- [R9 validation](../30-validation/s11-r9-calibrated-observation-validation.md)
- [R9 local evidence](../60-evidence/s11/s11-r9-calibrated-observation.md)
- [R8 Windows root cause](../50-diagnostics/s11/s11-r8-windows-calibrated-observation-diagnostic.md)
- [Durable detector responsibility](../20-architecture/s11-detector-responsibility-architecture.md)
- [Windows field-workflow checklist](../40-operations/manual-gui-windows-checklist.md)
