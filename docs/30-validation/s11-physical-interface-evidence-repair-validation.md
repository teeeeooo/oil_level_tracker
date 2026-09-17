# S11 Physical Interface Evidence Repair Validation

**Contract status:** proposed acceptance for the
[physical-interface design](../20-architecture/s11-physical-interface-evidence-repair-design.md).
The cases below are required future checks, not completed PASS results.

## Validation layers

1. Exercise raster-derived witnesses before authority. Tests which directly
   inject `representation_support` or a success enum cannot validate extraction
   or independent support. Such helpers remain appropriate for isolated state
   transition tests only.
2. Compose witness → authority → tracklet → lifecycle → selector → projection.
   Check the selected physical structure and exact provenance, not numeric
   count alone. Include multiple candidate competitors and permutations.
3. Run the relevant existing R22/R21 controls and public-video truth/replays.
   Record the implementation baseline, candidate identity and runtime. Any
   changed tracking fingerprint requires row-level physical explanation; do not
   replace truth/goldens merely to obtain PASS.
4. Qualify the implemented candidate on target Windows separately. Human-reviewed
   checkpoints and complete canonical segments remain field acceptance input.

## Required two-sided controls

| ID | Positive case | Negative / invariant | Required observation |
|---|---|---|---|
| E1 | Textured Oil/Foam interface, both proposal peers high in broad texture | Internal stripe/residue with similar scalar texture and boundary scores | Only the interface receives positive local partition evidence |
| E2 | Clean direct interface, curved or low-contrast distributed boundary | Glare, wall boundary, homogeneous opaque FULL, single-sector edge | Usable sectors, opposition and availability explain each decision |
| E3 | Independent edge and region evidence on the same contour | Duplicate candidates, renamed same-source descendants, disjoint contours at nearby median Y | Independence cannot be manufactured by candidate count or family aliases |
| E4 | Valid support with one weak representation retained as raw peer | Hard-invalid peer; missing mask/context/provenance; unavailable texture | Missing and hard-invalid evidence never grants the new high-texture route |
| E5 | High broad texture with complete positive interface witnesses through authority, phase and selection | A contradictory member/history edge mixed into the same row/tracklet | Typed material compatibility is consumed consistently; raw scalar values remain intact and true contradictions cannot be averaged away |
| T1 | Genuine rapid movement with matching distributed structure | Wrong stationary stripe replaced by actual stationary interface within the old jump bound | True motion retains identity; false-to-real association splits or abstains and does not contribute displacement |
| T2 | Genuine reversal, curved contour, photometric change with supported identity | Competing branches, ambiguous registration, incompatible partitions | Direction uses only certified edges; ambiguity stays UNKNOWN |
| T3 | Bounded loss and same-interface reacquisition | Unresolved predecessor followed by strong current anchors | Fresh confirmation cannot authorize a false prefix or inherit its progress/lease |
| H1 | Established fill loses its row; unique independently identified compatible successor | Continuation-only successor or merely near-Y candidate | Committed transfer updates the allowed owner for subsequent frames without copying ID/history |
| H2 | Independently verified non-material and material representations of the same boundary | Old valid owner still competes; multiple successors; expired snapshot | Family label is not a privilege; ambiguity remains fail-closed |
| H3 | Positively contradicted predecessor with unique fresh interface | Predecessor merely absent or unavailable | Owner correction creates a fresh direction-neutral episode only with the required positive evidence |
| V1 | Initially FULL, newly visible stationary interface with strong partition witness | Stationary reflection, internal stripe, uniform opaque FULL, unverified anchor corridor | New observed-interface route selects the real current row and never labels stationarity as drainage |
| V2 | Observed interface later drains, rises rapidly or closes as FULL | Upward/no-progress data forced through drain release; missing current row | Existing directional gates govern motion state; loss yields no numeric value immediately |
| V3 | Established fill stabilizes then reverses | Initial EMPTY static lower structure; stale owner reopening OPEN | Initial EMPTY safety and constrained loss context remain intact |
| P1 | Numeric output through each new transition | Candidate missing, invalid, contradicted or from another frame | Selected candidate source Y equals sequence and CSV raw Y; Oil/Foam validity stays independent |
| D1 | Basic/detailed trace, one-shot/incremental execution and candidate permutation | Diagnostic recomputation, pre-sort offset treated as serialized index | Output equality; stable provenance; trace reports actual gates and chain-specific causes |

## Acceptance gates and operating points

The [rejected R23 experiment](../50-diagnostics/s11/s11-r23-native-polarity-rejection.md)
adds four raster-to-tracklet positive controls in
`test_real_curve_can_move_and_reverse_photometric_polarity_before_confirmation`.
A true curved interface may translate while contrast polarity and exposure
change; both movement directions and initial polarities must remain supported.
Three common sectors with opposite signs are not enough for an identity veto.
Keep positional uncertainty separate from a confirmed different-structure
label, and preserve assignment ambiguity when testing negative evidence.
The BASE f14362 sector 2 human review is a localization-mismatch label only;
it must not be used as a certified material/structure negative.

**A — Evidence:** choose and document normalized partition, similarity and
registration operating points using labeled public/synthetic rasters with
held-out negatives. Record which cases were used to select values and which
were held out. Include resolution, crop offset, tilt, texture and exposure
variation. A score change without improved identity discrimination does not
satisfy this gate.

**B — Association and handoff:** all relevant E/T/H controls pass end to end,
including the compound high-texture-peer plus successor-owner case. The
synthetic motion probe from the R22 investigation is a trigger pattern, not
sufficient physical truth by itself. Use explicitly constructed different
image structures and an equally fast genuine-motion positive control.

**C — Initial-FULL extension:** all V controls pass with extraction enabled,
especially the stationary interface versus internal-structure pair. Do not
activate the proposed phase if those images are not distinguishable using the
implemented witnesses. Unknown on insufficient evidence is preferable to a
fake drain or false FULL-prefix measurement. Failure here does not justify
loosening existing release predicates.

**D — Candidate acceptance:** preserve relevant protected R22/R21 truth,
including initial EMPTY absence, FULL prefix/suffix absence, rapid refill,
bounded lease/expiry, contradiction reset, delayed attempt semantics and
independent Foam. Use the current canonical test/replay owner for final scope.
Measure runtime and peak memory on identical public inputs because evidence
extraction and descriptor history add work. Descriptor count and history length
must have explicit fixed bounds; no unbounded frame retention or all-history
matching. Report regressions and throughput impact, not an unsupported speedup.

The unchanged R22 stationary *drain release* negatives remain required. Add
separate tests for the proposed visible-interface observation state; do not
rename old failing inputs as real interfaces to make them pass. Any protected
expectation needing change must first have independently reviewed physical
evidence and an explicit acceptance decision.

## Target-Windows checkpoints

Follow the [current Windows procedure](../40-operations/s11-current-windows-field-qualification.md)
and [canonical reviewed truth](windows-sample1-heating-coldstart-reviewed-truth.md).
Inspect one bounded question per operator request. The
[transferred checkpoint record](../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md)
identifies the existing guide-reviewed frames; recheck frame and source-Y
mapping for a new run rather than assuming candidate IDs survive a revision.

- BASE: show that the false predecessor is not published as Oil and cannot
  create the real boundary's motion history; then inspect visible-interface
  admission separately from drain admission.
- Accum: verify actual-boundary witness, independent peers, authority, committed
  owner and final selected boundary through the first missing transition.
- Then evaluate every canonical segment, including early entry and late drain
  not explained by the checkpoint investigation. Do not replace segment truth
  with the current detector's shape or numeric row count.

Require current-frame coordinates and user-reviewed physical identity for
changed rows. If an interval's visibility is disputed, obtain explicit human
review before amending its canonical truth; LVLM-only estimates do not suffice.
Local gate completion never changes FIELD FAIL to field-qualified.

## Design-only verification

For this documentation change, run the detector governance checker against the
pre-change head, local link checks and `git diff --check`. Detector test/replay
execution is not required to validate prose and is not claimed as implementation
acceptance. On implementation, use the staged gates above and proportionate
focused tests before the broader candidate suite.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: BASE association across a reviewed location mismatch and Accum boundary-owner exclusion are distinct targets; private physical-identity continuity remains unresolved. The local polarity-only association prototype failed protected truth and photometric positive controls.
- Logic-map impact: NONE — this is acceptance for proposed changes, not a change to the executing R22 map.
- Failure-registry impact: UPDATED — F04 records the failed polarity-only association attempt; these controls prevent repetition without weakening protected truth or enabling the initial-FULL extension.
