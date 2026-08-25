# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** `R18 Windows operator check FAIL; bundle/trace causal audit pending before R19 design`
**Source authority:** `main at locally accepted R18; no field-qualified detector`
**Task-start exact head:** `8d43d7510eccdea7a0da95a490c4c42785a80d8e`
**Task-start exact parent:** `12b4820b1c5bcc0f4c1d3a0074b36039acdb4d03`

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

## R13 local result

R13 replaced the remaining R12 authority leak with one phase-identity decision
shared by authority and trajectory. Stale semantic-direct, terminal-fallback,
track-promotion, duplicate dynamic-material and no-reader diagnostic paths were
removed. Bounded calibrated phase proposals do not receive proposal or motion
authority. Per-series graph validity is enforced.

Local replay processed 299 rows with 121 numeric Oil, 9/13 checked truth,
5.28 px MAE, 11 px maximum error and complete same-frame provenance. The
sample3 completed-fill internal-material interval remains non-numeric.
User-like Artifact replay produced 97/113 sample4 numeric Oil, zero Foam and
complete provenance. Full regression is 1,537 passed. Direct total timing is
69.5 ms/frame versus the documented R12 72.6 ms/frame.

## R13 field disposition

The secure-Windows replay failed. Final publication integrity was exact
(Base 345, Accum 102), but reviewed truth was 0/3 and 0/5. R13 converted local
phase appearance and broad-mask ordering into identity, permitted high-conflict
ordered-lower anchors, and connected unrelated rows through a component-free
trajectory/run. Artifact templates were active, but their count also enabled
and enlarged proposal generators. Complete pipeline counterfactuals showed that
texture/corroboration gates reduce some wrong rows without recovering truth,
the distance-split prototype over-suppresses, and disabling generators removes
Base Oil entirely.

## R14 field disposition

The exact pushed R14 head failed private-Windows acceptance. Base recovered
real Oil for the first time but lost anchor-free same-component tails. Accum
published four stationary lower-structure runs during confirmed EMPTY. A real
dynamic Foam group was rejected because signed inverted Oil topology and
pre-publication Oil proposals were treated as same-material authority. Later
dynamic-onset Foam publication remained internally consistent.

## Current executable action

Freeze the R18 operator-reported failure, then audit its Windows bundle and
debug trace before authorizing R19 design. The R17 bundle remains frozen
historical evidence and cannot prove R18 field behavior. Do not reuse old
counts as acceptance targets or convert named unknowns into facts.

The locally accepted R18 implementation starts confirmed FULL behind a phase
barrier, permits an established partial fill to reverse into one bounded drain
owner and replaces broad Foam extent confirmation with bounded front-formation
witnesses. It retains initial-EMPTY suppression, Oil/Foam same-frame/CSV
provenance, Artifact handling, checked-truth authority and resolver ordering.

Use the [R18 architecture](../20-architecture/s11-r18-lifecycle-closure-architecture.md),
[R18 validation](../30-validation/s11-r18-lifecycle-closure-validation.md),
[local evidence](../60-evidence/s11/s11-r18-lifecycle-closure.md),
[operator-reported field result](../60-evidence/s11/s11-r18-secure-windows-field-result.md)
and [canonical private-Windows truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).
The field result is `FAIL`, while its code-level cause remains unaudited until
the R18 bundle/trace is available.

## R16 field disposition

The private-Windows R16 holdout failed. Base published 0/601 Oil and five false
Foam rows. Accum suppressed the prior initial-EMPTY false Oil runs and admitted
a real lower-entry tracklet, but published only 31/601 Oil rows, had large
reviewed-Y errors at 684/689 s and remained non-numeric after 702 s. Accum
published 97 Foam rows. Their former 52-real/45-false classification is
superseded by the later canonical segment truth, which establishes Foam only
from about 672--680 s and does not make detector-row cohorts a truth target.

Completed-window integrity passed: every one of the 31 Oil rows and all 102
Foam rows had exactly one equal-Y selected same-frame candidate and equal CSV
raw Y. Preliminary contrary findings came from reading top-level current-frame
trace fields instead of nested completed-window fields.

The corrected diagnostic narrows Base to mixed proposal/confirmation failure,
Accum to upstream truth-row loss plus absent safe mid-glass filling-owner
reacquisition, and Foam to episode-level discrimination. It explicitly does
not treat unconfirmed tracklet default-zero metrics as measured witness values,
does not infer that the static map was absent, and preserves Foam publication
independence from Oil.

## Local R14 result

R14 decouples Artifact templates from fixed proposal budgets, replaces local
phase promotion with recent-Foam composition and explicit component ownership,
and bounds completed-fill reopening to upper-entry directional drain evidence.
Confirmed Artifact templates now support Shift/Ctrl/Cmd multi-selection,
select-all, clear-selection, simultaneous overlay highlight and bulk deletion.

The exact four-video replay processed 299 rows with 187 numeric Oil and complete
same-frame provenance. Checked truth is 10/13, MAE 8.5 px and maximum error
26 px. The sample3 completed-fill internal cap has zero numeric Oil, late drain
has 18 numeric rows, and sample4 has eight strict reviewed-range matches. Direct
runtime is 96.8 ms/frame against the 104.25 ms/frame ceiling. Private-Windows
Base/Accum effectiveness remains unproven.

## Local R15 result

R15 removes candidate-only and prior-track Foam alias vetoes, admits initial
EMPTY Oil only through bounded lower-entry upward progress, replaces the fixed
continuation horizon with continuous registered same-component motion and
classifies detached layer/droplet Foam through one material phenotype owner.
Shared Oil optics remain unchanged; bright-droplet recovery is confined to the
Foam detector and still requires registered dynamics for sequence eligibility.

The exact four-video replay processed 299 rows with 187 numeric Oil and complete
same-frame provenance. Checked truth is 10/13, MAE 8.1 px and maximum error
24.5 px. Sample3 completed fill remains non-numeric, late drain has 18 numeric
rows and sample4 has eight strict reviewed-range matches. Fixed fingerprints
passed. Full regression is 1,549 passed; compile and diff checks passed.

## Local R16 candidate

R16 replaces overlapping component, phase and final-selection responsibility
with directed physical tracklets, a forward material lifecycle and a separate
candidate-publishable fixed-lag selector. It preserves exact same-frame
provenance, makes ambiguous or foreign ownership fail closed, and establishes
an 11-sampled-frame end-to-end commitment bound while keeping each individual
confirmation/selection stage bounded to six frames.

The first independent audit found a missing symmetric one-to-many tracklet
ambiguity check, incomplete same-row material vetoes across drain transitions
and an absolute-jump-only backwards re-entry. The repaired candidate terminates
genuine split parents without misclassifying clearly owned children, applies
the complete current-row veto to every drain transition and adds the ordinary
directional reversal tolerance to phase re-entry.

The final follow-up repair removes a separate established/provisional ID
exchange. It corrects only an actual baseline two-edge crossing with two
independently clear physical child proposals. A lone provisional edge or
calibrated-high-recall-only residual cannot redirect the established owner, so
the accepted material barrier and 81--96 s drain witnesses remain unchanged.

The local structural, four-video safety, performance, compilation, focused and
canonical regression gates pass. Exact counts, fingerprints, timing and the
candidate-level explanation for intentional abstentions are owned by the
[R16 evidence record](../60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md)
and [owner audit](../50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md).
The later private-Windows result failed and is owned by the
[R16 Windows field result](../60-evidence/s11/s11-r16-secure-windows-field-result.md)
and [corrected diagnostic](../50-diagnostics/s11/s11-r16-windows-tracklet-and-foam-diagnostic.md).

## Authority links

- [R17 physical observation ownership architecture](../20-architecture/s11-r17-physical-observation-ownership-architecture.md)
- [R17 validation](../30-validation/s11-r17-physical-observation-ownership-validation.md)
- [R17 local evidence](../60-evidence/s11/s11-r17-physical-observation-ownership.md)
- [R17 Windows field result](../60-evidence/s11/s11-r17-secure-windows-field-result.md)
- [R17 Windows diagnostic](../50-diagnostics/s11/s11-r17-windows-phase-and-episode-diagnostic.md)
- [R16 directed tracklet/material lifecycle architecture](../20-architecture/s11-r16-directed-tracklet-material-lifecycle-architecture.md)
- [R16 validation](../30-validation/s11-r16-directed-tracklet-material-lifecycle-validation.md)
- [R16 local evidence](../60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md)
- [R16 owner audit](../50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md)
- [R16 Windows field result](../60-evidence/s11/s11-r16-secure-windows-field-result.md)
- [R16 Windows diagnostic](../50-diagnostics/s11/s11-r16-windows-tracklet-and-foam-diagnostic.md)
- [R15 state-aware material ownership architecture](../20-architecture/s11-r15-state-aware-material-ownership-architecture.md)
- [R15 validation](../30-validation/s11-r15-state-aware-material-ownership-validation.md)
- [R15 local evidence](../60-evidence/s11/s11-r15-state-aware-material-ownership.md)
- [R14 Windows field result](../60-evidence/s11/s11-r14-secure-windows-field-result.md)
- [R14 Windows diagnostic](../50-diagnostics/s11/s11-r14-windows-state-and-foam-ownership-diagnostic.md)
- [R14 phase-component architecture](../20-architecture/s11-r14-phase-component-replacement-architecture.md)
- [R14 validation](../30-validation/s11-r14-phase-component-replacement-validation.md)
- [R14 local evidence](../60-evidence/s11/s11-r14-phase-component-replacement.md)
- [R13 Windows result](../60-evidence/s11/s11-r13-secure-windows-field-result.md)
- [R13 Windows diagnostic](../50-diagnostics/s11/s11-r13-windows-identity-component-diagnostic.md)
- [R13 phase-identity architecture](../20-architecture/s11-r13-phase-identity-recovery-architecture.md)
- [R13 validation](../30-validation/s11-r13-phase-identity-recovery-validation.md)
- [R13 local evidence](../60-evidence/s11/s11-r13-phase-identity-recovery.md)
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
