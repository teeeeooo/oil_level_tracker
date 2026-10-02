# S11 O2 unpooled O1 spatial context — Windows run 001 intake

Executed source reported: `514c1a8560f250bd9b173df0d366e2d0c1095800`
(GitHub ZIP; no .git). Scope: existing `spatial-context-001` stored outputs,
new `joint-context-001`, no source-video or detector rerun. This record separates
transferred execution checks from unresolved post-run inspection semantics.

## Execution evidence

| Item | Transferred result / local check |
|---|---|
| Schema / receipt | `s11-o2-joint-context-v1`, COMPLETE, RC=0 reported |
| Joint artifact | `8bf2ba8aa56ff91aaad5dea3f00ea861916831185163bb6d8aee3cc783e11e1b` — independently reconstructed from local source/spec and exactly matches the report |
| Outputs | 13 hashes reported matching; 14 files including receipt |
| Preserved inputs | 32/32 reported before/after equal; 31 old outputs plus receipt |
| BASE | review-002 / frame14386 / revision14 / origin[0,211] / shape[773,578] / 124 points / baseline MATCH 1416 bands |
| Accum | review-003 / frame16280 / revision4 / origin[1199,56] / shape[584,462] / 158 points / baseline MATCH 1012 bands |
| Flags | EXPLORATORY_UNCALIBRATED / NOT_EVALUATED / FIELD FAIL; auto_acceptance=false reported |

The private JSON/NPZ/images and their file hashes were not independently read
locally. Matching the artifact verifies the reported code/spec identity, not those
private bytes or image interpretations. The user relays text through OCR; the
Windows agent itself reads files directly. Do not attribute a discrepancy to
Windows OCR or silently replace source measurements with transferred prose.

Canonical source artifact remains
`6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910`,
previously reconciled against the receipt photograph and code. The latest transfer
spells `4d00cb` instead of `4d08cb`; preserve this as a transfer discrepancy, not a
new canonical value or proven input mutation. The unchanged runner requires exact
source receipt/report/expected equality. No additional manual hash transcription
or rerun is requested solely for that spelling difference.

## Inspection received, not yet a closed same-X result

The Windows agent reports fixed-scale magnitude/vertical PNG inspection and NPZ
statistics, with separate notes outside the original output. Its conclusions were:
BASE native candidates `different appearance`; Accum idx10/idx15 `shared/ambiguous`;
BASE candidate-center idx0/idx20 `shared/ambiguous`. Retain these as attributed
observations, not verified physical separation or a demonstrated failure of all
joint spatial representations. The user's prior idx0/idx20 ambiguity remains.

Three material limits prevent accepting the complete interpretation as written:

1. **Statistics have unspecified, apparently inconsistent domains.** For Accum
   idx10 X[1388,1473], the table labels a +/-60px vertical maximum of 0.008 but
   reports 83/85 columns with vm>0.05. X[1473,1558] similarly lists 0.008 and 75/85.
   If these use the same channel, units, valid pixels and window, a pixel maximum
   below 0.05 implies zero columns containing a pixel above 0.05. Different axes,
   per-column averaging, windows or transcription could explain this, but the
   transfer does not specify which. No cause is established locally. The official
   runner emits neither these maxima nor this column cutoff; they are post-run
   analysis, not proof of a runner calculation bug. The ad hoc 0.05 statistic is
   not a classifier threshold or an accepted discriminator.
2. **BASE native comparison mixes X intervals.** Its three rows are idx8 at
   [130,236], idx9 at [236,343], and idx11 at [343,449]. They cannot establish the
   required within-X comparison of all three candidates. Required source markers:
   [130,236]: idx8 Y397 / idx9 Y382 / idx11 Y901;
   [236,343]: idx8 Y396 / idx9 Y406 / idx11 Y925;
   [343,449]: idx8 Y397 / idx9 Y419 / idx11 Y922.
   No global appearance conclusion follows from the supplied diagonal selection.
3. **Validity and display do not establish absence or continuity.** Fixed-scale
   black can include a small positive gradient rounded to zero display intensity;
   an invalid endpoint cannot establish where an edge physically terminates.
   Separate sector views do not by themselves prove a contour extends without
   breaks. Bright appearance is not a measured glare exclusion unless its mask
   is checked. Do not upgrade shared counts into identical intensity distributions
   or physical equivalence. Existing evidence already warns against these uses.

For idx0/idx20 specifically, equal reported `cols>0.05` counts do not prove equal
strength: the table itself gives different means/maxima. The correct retained
statement is that the reported visual inspection did not resolve human ambiguity.
No relabeling or forced distinction is requested.

## Preview interpretation erratum — W4 audit intake

The [W4 progress audit, F09](../../50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md)
corrects item 3 above. Under the current uint8 central-difference operator, the
smallest nonzero derivative is 1/510. With vertical scale 0.5 and magnitude scale
sqrt(0.5), it rounds to a nonzero display byte in both previews. Thus valid
nonzero gradients do not round to PNG byte zero in this domain. Visually dark
nonzero bytes, exact valid zero derivatives and invalid magenta must be separated.
A zero derivative still does not establish uniform pixels or physical absence
(central-difference aliases remain). The original intake wording above is retained
with this explicit correction; no runtime change or Windows rerun is implied.

## Bounded next action

Use the existing outputs and existing analysis note/code. No checkout update,
experiment rerun, decoder, detector, new score or human verdict is needed.

- Reconcile **one** problematic row: Accum native idx10 X[1388,1473], sourceY217.
  Return the original statistic definitions/code (NPZ key, source/local slice,
  validity mask, units, reduction axes) and a machine-generated check from the
  same arrays. A precisely defined +/-60 inclusive-row window is local [101,222)
  or source [157,278), X local [189,274), after origin [1199,56]. Compute maximum
  only over gradient_valid pixels, and columns containing any valid vm>0.05 over
  the very same slice. If the old table measured a different quantity, label it
  correctly; do not adjust a threshold to reproduce the old count. Reconcile
  other affected rows with that same existing extraction logic once the cause is
  known; do not manually patch numbers. Report unresolved if the code is absent.
- Complete **three** BASE comparison rows, grouping idx8/9/11 on the same X using
  the coordinates above. Describe visible arrangement and censored portions;
  separate `different appearance` from `not assessable` when masked support
  prevents comparison. These are the originally requested targets, not new cases.
- Qualify global continuity/absence statements accordingly. Preserve raw outputs,
  put corrected notes separately, and retain the human ambiguity control. No
  physical identity conclusion or production promotion follows from this check.

The [operations note](../../40-operations/s11-o2-local-shadow-evaluation.md#unpooled-o1-spatial-context--report-reconciliation)
contains the narrow handoff. If corrected appearance remains shared or censored,
close this appearance-to-identity proposal without promotion rather than treating
another descriptor or collection round as automatic. O2 acceptance remains open.

## W4-R0 correction received and W4-R1 disposition — 2026-10-02

Source of this update: user-transferred Windows completion report. Analysis source
reported as ZIP `14a707b`, no Git metadata; the original joint extraction artifact
above is unchanged. Private corrected note, arrays and images were not read here.
The earlier intake and handoff are retained as history; this section closes that
handoff and does not request another reconciliation run.

### Reported R0 result

Accum review-003/frame16280, native idx10, source X[1388,1473), Y217:
`vertical_magnitude`, units abs(uint8 neighbour difference)/510,
`gradient_valid`, local Y[101,222), X[189,274), shape 121x85.

| Quantity | Transferred correction |
|---|---|
| Raw valid-pixel maximum | 0.192157, replacing the prior approximately 0.008 |
| Columns with any valid value >0.05 | 83/85, unchanged |
| Invalid pixels in the slice | 0; implies 10,285 valid pixels and 85 supported columns |
| Same-domain invariant | True reported; the supplied corrected values are arithmetically compatible |
| Valid-pixel mean | 0.008787 reported; resemblance to the old maximum is not proof of a transcription/reduction cause |
| Origin of old discrepancy | unresolved |

The transfer initially attributes `vm[valid].max()` and unmasked
`vm.max(axis=0)>0.05` to previous inline code, but subsequently states that the
original code was not saved and its exact definition cannot be confirmed. Treat
those historic formula attributions as unverified; the new, specified calculation
is not a demonstrated reproduction of the old calculation. With zero invalid
pixels in this slice, mask omission does not explain the reported discrepancy.
Other old table maxima are not retroactively certified by this one correction.

| BASE source X | idx8 / idx9 / idx11 native Y | Reported appearance | Support limitation |
|---|---|---|---|
| [130,236) | 397 / 382 / 901 | shared_or_ambiguous | idx11 approximately 35% invalid; reported absence of transition applies only to inspected valid support |
| [236,343) | 396 / 406 / 925 | shared_or_ambiguous | idx8/9 share reported 41/107 exceedance count; idx11 approximately 28% invalid with weak transition |
| [343,449) | 397 / 419 / 922 | not_assessable | idx8/9 reported 5/106 versus 1/106; idx11 approximately 52% invalid |

These are transferred bounded observations, not equality of raw arrays, identical
physical objects, verified continuity, or evidence that an invalid endpoint is a
physical termination. The supplied summary does not expose every BASE window and
reduction definition; retain the detail in the private note, without extending
these counts into quantitative cross-candidate efficacy. No automatic metadata
follow-up is required under the R0 completion rule.

Windows reports receipt/report/expected artifact agreement, all 13 output hashes
matching disk and unchanged hashes after rereading the consumed files. This is
reported preservation, not a new independent local hash check. Corrected note:
`joint-context-001-notes/corrected-note-w4-r0.md` (266 lines, 13,722 bytes reported),
with nine comparison PNGs and seven earlier notes images outside the immutable
experiment directory. No detector, source output or label change is reported.

### R1 decision and next entry condition

- Work item: unpooled joint-appearance inspection as a basis for an identity challenger.
- R0: COMPLETE on transferred evidence; historic statistic origin remains unresolved.
- R1 decision: **CLOSED_WITHOUT_PROMOTION** for the present appearance-to-identity
  proposal. The two assessable BASE comparisons are reported shared/ambiguous;
  the third is **NOT_ASSESSABLE**, not a negative classification result. The
  earlier Accum shared-appearance report and corrected positive-point maximum
  do not establish a reproducible positive/structural-negative arrangement rule.
- Not established: identity support gain, a usable opposing control, scalar truth,
  general impossibility of spatial classification, or calibrated O2 acceptance.
  Human idx0/idx20 ambiguity is retained and is not the sole rejection reason.
- R2: entry condition CONTINUE_REUSE_ONLY is not met; do not implement another
  descriptor, tune the 0.05 analysis cutoff or start a classifier from these counts.
- Next action: W4-R3 evidence-gap feasibility, before any W2 collection. Name a
  physically verified positive/structural-negative comparison with adequate valid
  support and explicit input-based expectations. Check availability in existing
  SPL#1 saved material first; current summary does not establish such a control.
  Record unavailable if none is supported. Collection, new labels, source reruns
  and SPL#2/3 activation are not automatic consequences of this closure. Do not
  repeat the same censored arrays or the unresolved idx0/idx20 +/-5 s judgment.
- Production/source/labels changed: no; evidence and current routing only.
- Acceptance owner: [O2 shadow acceptance](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance).
  FIELD FAIL / NOT_EVALUATED preserved; W4 overall and O2 acceptance remain open,
  W5/O3 still gated. This closes one investigation, not the detector project.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: supplied post-run inspection loses consistent X/statistic/validity scope; an upstream private detector cause is not established.
- Preserved contracts: exact geometry and source provenance, missing distinct from zero, unchanged scores/labels, unresolved human identity, separate field acceptance.
- Logic-map impact: NONE — evidence intake and bounded report reconciliation only; no implementation or production change.
- Failure-registry impact: NONE — no new mechanism or field repair is claimed.
