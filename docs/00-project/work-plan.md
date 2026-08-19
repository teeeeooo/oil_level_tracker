# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `IMPLEMENTING`
**Current gate:** `R13 phase-identity recovery design and implementation`
**Source authority:** `R12 secure-Windows field result and diagnostic`

## R10 field result

R10 increased private-Windows coverage but failed interface accuracy.

- Base published one incorrect 583-frame run from 480–777.5 s. A calibrated
  lower-rim/texture path had 567 promoted members but only two motion keyframes
  at 750 and 774 s; those future keyframes retroactively anchored the complete
  path. No selected row matched reviewed Oil.
- Accum selected an ordinary `r6_material_path` at Y191–297 that overlays prove
  was Foam/residue. Actual Oil was near Y450. The wrong path retained high
  registered motion after public Foam disappeared, while actual-Oil-near rows
  were usually top-k-pruned.
- Candidate-local material texture conflict was high on several wrong Accum
  anchors but was absent from authority. Current-frame-only conflict is still
  insufficient because a representative residue row had zero conflict after
  the Foam raster disappeared.
- Frame-level `R8_CALIBRATED_ARTIFACT_REJECTED` did not describe the selected
  row; selected Base rows had zero Artifact match.

## Activated structural reset

The prior post-S11 detector-maintainability slice is pulled forward because
architecture debt now blocks correctness work. UI/MainWindow/Result Review
maintainability remains post-S11.

R11 first performs behavior-preserving structural work:

1. retire production-unreachable legacy selectors;
2. introduce typed candidate evidence and explicit authority reasons;
3. separate current-frame evidence, candidate assembly, Artifact filtering and
   debug projection;
4. split admission, authority, track opposition, bootstrap, trajectory, global
   path and final projection responsibilities; and
5. introduce an observation-only Foam material track before applying R11
   behavior.

Structural commits preserve R10 four-video and Artifact replay fingerprints.
They do not claim the known R10 Windows path is correct.

## R11 behavior repair

After structural preservation passes:

- calibrated bootstrap is bounded to locally distributed motion keyframes and
  cannot promote an unbounded prefix/suffix;
- registered dynamic material paths with high texture conflict are demoted,
  with no silent semantic/terminal bypass;
- Foam/residue material identity may oppose reuse of the same upper track as
  Oil without publishing Foam or blocking unrelated Oil; and
- a bounded vertically separated lower candidate is retained so actual Oil is
  not removed before authority evaluation.

Every numeric Oil remains an exact same-frame candidate. No state, Foam,
bootstrap or graph projection may create/interpolate/carry a coordinate.

## Local R11 result

The structural reset, bounded bootstrap and Foam-material identity repair are
implemented and locally validated. The behavior-preserving midpoint retained
all R10 fingerprints. Final R11 replay produced 129/299 numeric Oil with 10/13
checked truth, 5.95 px MAE, 11 px maximum error and complete same-frame
provenance. User-like Artifact replay produced 92/113 sample4 numeric Oil and
3/5 checked truth. Full regression is 1,524 passed; direct detector timing is
43.0 ms/frame off and 44.0 ms/frame on.

## R11 field disposition

The exact pushed R11 head failed secure-Windows Base/Accum effectiveness. R11
removed the R10 unbounded prefix but a later motion-only path still changed
identity between reflection, actual liquid and bracket reflection. Accum's
distinct-lower reserve became generic anchor authority while actual lower Oil
was pruned. Real dynamic Foam was halved by fixed width admission, fragmented
by sequence bounds and then made invalid by a broad material-bottom topology
veto plus shared Oil/Foam graph validity.

Final sequence and CSV ownership remain sound: Base 39 and Accum 418 numeric Oil
rows agree exactly and every numeric row owns one equal-Y same-frame candidate.

## R12 field disposition

The secure-Windows R12 bundle reports the expected sequence resolver version
but no Git SHA or detector version. It fails the field gate. Base publishes no
Oil and has no qualified anchor; at 540 and 674 s the reviewed row is absent
from even the bounded proposal neighborhood. Accum publishes 92 wrong residue
rows at Y190–297. Twenty-five weak ordinary rows bypass material conflict
through `semantic_sequence_anchor`, eight more use corroborated-material
authority, and those 33 anchors support the complete wrong trajectory.

R12's independent Foam validity is retained: confirmed Foam rows at 670.5 and
673 s have `foam_is_valid=True` while Oil and legacy state validity are false.
The Result Review renderer nevertheless plots finite points without applying
their per-series valid bit and must be corrected.

## Current executable action

R11 evidence and the confirmed dead compatibility cleanup are complete. R12
implemented one replacement semantic pipeline, not another R11 policy layer.
It removes motion-only authority, unbounded material identity, distinct-lower
anchoring, material-bottom topology veto and shared series validity.

Local R12 replay processed 299 rows with 133 numeric Oil, 10/13 checked truth,
5.95 px MAE, 11 px maximum error and complete same-frame provenance. Sample3
retains Y245 for the reviewed Y243 rise and publishes five independently valid
Foam points. User-like Artifact replay produced 82/113 sample4 numeric Oil and
zero Foam. Full regression is 1,526 passed. Same-session R11/R12 direct timing
is 70.5/72.6 ms per frame, a 2.9% total increase.

R13 replaces the remaining phase-authority leak instead of adding an R12
threshold layer. First remove stale compatibility control/diagnostic seams.
Then recover bounded non-local Base proposals without proposal-only authority,
introduce one composition-aware lower-Oil identity shared by admission,
authority, trajectory and track opposition, and prevent weak/high-conflict
ordinary semantic rows from anchoring residue. Preserve independent Foam
validity, make basic trace identify the first path-stage mutation and make the
review renderer mask each series by its own validity.

## Authority links

- [R11 architecture](../20-architecture/s11-r11-detector-architecture-reset.md)
- [R11 validation](../30-validation/s11-r11-detector-architecture-reset-validation.md)
- [R10 Windows diagnostic](../50-diagnostics/s11/s11-r10-windows-path-and-residue-diagnostic.md)
- [R11 local evidence](../60-evidence/s11/s11-r11-bounded-bootstrap-and-material-identity.md)
- [R11 Windows result](../60-evidence/s11/s11-r11-secure-windows-field-result.md)
- [R11 Windows diagnostic](../50-diagnostics/s11/s11-r11-windows-bootstrap-composition-diagnostic.md)
- [R12 replacement architecture](../20-architecture/s11-r12-phase-composition-replacement-architecture.md)
- [R12 validation](../30-validation/s11-r12-phase-composition-replacement-validation.md)
- [R12 local evidence](../60-evidence/s11/s11-r12-phase-composition-replacement.md)
- [R12 Windows result](../60-evidence/s11/s11-r12-secure-windows-field-result.md)
- [R12 Windows diagnostic](../50-diagnostics/s11/s11-r12-windows-phase-authority-diagnostic.md)
- [Durable detector responsibilities](../20-architecture/s11-detector-responsibility-architecture.md)
- [Structural maintainability assessment](../50-diagnostics/post-s11-structural-maintainability-assessment.md)
- [Windows checklist](../40-operations/manual-gui-windows-checklist.md)
