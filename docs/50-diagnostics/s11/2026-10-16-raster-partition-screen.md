# CRW-1 — paired current-raster localization / partition screen

## Frozen question and decision boundary

Base: `20d5d4d555e1296959a75f3c2c0eb96b12de6e71` on `main`.
Current authority: [Work Plan](../../00-project/work-plan.md).
This is a diagnostic implementation and a single fixed input-qualification screen,
not a fourth Windows mechanism or a detector/Recipe/model change.
The [preceding geometry screen](2026-10-16-corroboration-geometry-screen.md)
had no pair of two captured native paths. CRW-1 makes new raster observations;
it does not relabel them as the original candidates' native paths.

H1: bounded current-raster localization can supply explicit sector hypotheses
for weak/practically accepted candidates as well as reviewed opposition.
H2: edge-excluded near/far partition evidence can preserve useful interface
contexts without granting the same proposed support to known non-targets.
H3: coincident re-observations from one extractor must be deduplicated, not
counted as two independent candidate votes.
Report context is the goal: evaluate preserved reviewed-frame groups as well
as candidate counts. Eleven accepted approximations are not eleven mandatory
perfect detections or continuous ground truth. No report acceptance is claimed.

## Fixed measurement specification

Reuse the eight prepared rasters, masks, five O1 sectors, original band width,
187-unit roster and exact original candidate/index/frame bindings. Actual kinds
remain 175 Oil / 8 Foam / 4 contexts. Keep all unknowns and practical labels.
A sector with a captured native Y uses it only as an explicitly typed seed;
otherwise use the original candidate Y as a scalar hint. No candidate Y changes.
Search integer rows from floor(seed)-band through ceil(seed)+band, inclusive.
Do not expand this window after seeing real results.

Localize from the gray difference at Y-1/Y+1 using identical valid columns
(minimum two columns and 50% of sector width). Retain every nonzero local
maximum, all exact tied rows and search/missing-neighbor censoring. These are
sector peak sets, not a calibrated uncertainty interval or a continuous contour.
Use the four existing O1 band locations, but intersect all four visibility
masks at matched (offset,column) locations. Require eight matched samples and
50% support, preserving unavailable versus measured values. Edge and band rows
are disjoint. This does not establish independent physical semantics.

For near means A/B and far means FA/FB, let N=B-A, F=FB-FA and
D=max(abs(A-FA),abs(B-FB)). The diagnostic margin is min(abs(N),abs(F))-D
when N and F have the same nonzero sign, otherwise -min(abs(N),abs(F))-D.
Compute its numerator in exact integer pixel sums on common support, avoiding
floating-point positive margins on a linear ramp. No dark-Oil assumption.
A sector's descriptive partition flag requires an uncensored local maximum
with available four-band context and margin > 0. The three-sector summary
reuses the proposed architecture's distributed-support count; it is NOT a
selected operating point, candidate eligibility or material-role judgment.
Compare exact shared partition rows only within the same frame/raster/mask/grid.
Such aliases explicitly supply zero new independent votes. No nearest-Y match,
peer status, label, model, authority or temporal result enters extraction.

## Validation and stop conditions

Synthetic controls: both step polarities, tied/multiple peaks, bounded search,
flat/linear/stripe signals, different-column mask confound, missing context,
fractional/source-coordinate seeds, native-hint distinction, frame/raster
identity, immutability and no authority. Recompute saved real measurements
with separate direct pixel loops; retain failures and complete population.

Do not turn unavailable/unsupported inputs into physical absence. If reviewed
non-targets also have positive partition margins, the proxy does not establish
physical role; do not tune its band/window/count or install a hard gate.
Sample3 quarantine, review-006, all closed Windows comparisons, FULL/Foam
unresolved gates and actual report-only reading retain their existing scope.
No full-video replay, new fit or private Windows pixel access is part of CRW-1.

## Execution result

Executed once at clean frozen `7845f890c52e2c6fab2b4b1a84f2e2139f9ded3e`.
The hypothesis, extractor, direct-loop verifier and 31 new tests were committed
before the real raster run. No outcome-led band/window/count changes followed.
The [machine summary](2026-10-16-raster-partition-screen/summary.json) preserves
all 18 reviewed controls, original label scopes and the complete denominators.

| Question | Fixed observation | Disposition |
|---|---|---|
| H1 localization | 10/11 accepted candidates have at least three uncensored localized sectors; 6/7 opposed candidates also do | Measurable sector hypotheses, not physical-role or continuous-contour qualification |
| H2 partition | 8/11 accepted and 1/7 opposed candidates have at least three partition sectors | Useful partial input; not a standalone discriminator or chosen detector operating point |
| Reviewed-frame preservation | An accepted candidate has this partition flag in 7/8 reviewed frames | Sparse context-preservation screen, not continuous-motion/report acceptance |
| H3 shared extraction | 33/85 directed peer relations share any positive partition rows; 7/85 share at least three sectors | Exact extraction aliases; no new independent support votes |
| Arithmetic | 6,133 gradient references and 1,244 four-band references, zero direct-loop mismatches | Measurement implementation reproduced, not detector accuracy |
| Tests | 123 passed / 0 failed in 7.17 s: 31 new and 92 related cases | Synthetic contracts and diagnostic regression only |

The public frame keeps two of its four practically accepted alternatives. This
is one represented frame, not a requirement to recover all four approximations.
The f1140 accepted material candidate retains three partition sectors while all
three reviewed rims have fewer. These are useful bounded observations; residual
errors do not make all of this information worthless.

However, f1200's opposed idx10/Y865.5 has four partition sectors versus three
for accepted idx4/Y841. A monotone count threshold that retains the accepted
candidate also admits this opposition; picking the largest count is wrong there.
At f1320, accepted idx9/Y844 and opposed idx21/Y822 both have two. Changing the
count cutoff cannot separate that tie. These controls disqualify count-only
physical authority, not every possible use of the measured input. No actual
selected-output change, false-extremum repair or report benefit was measured.
All 157 unassessed Oil candidates, eight Foam candidates and four contexts remain
unassessed at their original roles. Six historical physical correspondences and
five practical acceptances remain distinct within the eleven accepted Oil units.

The actual raster extraction took 1.329 s; this is not end-to-end detector
performance. Inputs were hash-checked before and after the run. Direct visual
inspection covered the saved f1140/f1275/f1485 source crops; numerical extraction
covered all eight frozen rasters. Windows evidence was reused from the
[received checkpoint](../../60-evidence/s11/2026-10-16-windows-comparison-checkpoint.md),
not newly executed or independently re-extracted from private video.

Full output remains local at
`sample/output/s11-raster-partition-20261016-001/evidence/readout.json.gz`
(371,355 bytes; SHA-256
`5458e62d198a821056996fabe736b9510d4b699571cd5497f88006c67a4723fc`).
The compact Git summary carries the direct-loop result and source hashes;
full profiles and all censored/alternative rows remain in that managed readout.
The [handoff](../../60-evidence/s11/2026-10-16-raster-partition-handoff.md)
owns reproduction and the bounded continuation checkpoint.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the private 721 s false anchor is established, but its raw peer/optical cause remains unknown. This study addresses local measurement availability and shared derivation before authority; it cannot identify that private cause.
- Existing feature coverage: saved sample4 and public current rasters and effective/glare visibility are reused with original Recipe-derived sectors. Sample4 has no user Artifact templates/exclusions in its retained Recipe; existing static/Artifact outcomes stay in original captures. No static learning, Recipe construction or Artifact rejection is rerun. Experimental switches, Local XY, model inference, initial-FULL and completed resolution are bypassed by this offline read-only measurement entry; their closed results are not invalidated.
- Execution scope: `tests/diagnostics/s11_raster_partition_screen.py` measures the frozen 187-unit roster, actual Oil candidates only, and the 85 existing directed peer relations; tests exercise synthetic pixels. New descriptive hypotheses have no production consumer, no native/path truth and no final Oil/Foam/report outputs. Original labels and bytes remain unchanged.
- Logic-map impact: NONE — diagnostic helpers only; production defaults, ownership, extraction and publication are unchanged.
- Failure-registry impact: NONE — current identity/provenance/threshold warnings already cover this hypothesis; no new physical mechanism is promoted.
