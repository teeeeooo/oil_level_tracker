# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `IMPLEMENTING`
**Current gate:** `R11 detector architecture reset, then Base/Accum repair`
**Source authority:** `R11 architecture + R10 Windows diagnostic`

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

## Current executable action

Complete the structural reset through independently verifiable logical commits,
run the R10 preservation gate, then implement and locally validate R11. Update
completed evidence and push once after the full exact-head gate. The next field
action is secure-Windows replay of that exact pushed R11 head.

## Authority links

- [R11 architecture](../20-architecture/s11-r11-detector-architecture-reset.md)
- [R11 validation](../30-validation/s11-r11-detector-architecture-reset-validation.md)
- [R10 Windows diagnostic](../50-diagnostics/s11/s11-r10-windows-path-and-residue-diagnostic.md)
- [Durable detector responsibilities](../20-architecture/s11-detector-responsibility-architecture.md)
- [Structural maintainability assessment](../50-diagnostics/post-s11-structural-maintainability-assessment.md)
- [Windows checklist](../40-operations/manual-gui-windows-checklist.md)
