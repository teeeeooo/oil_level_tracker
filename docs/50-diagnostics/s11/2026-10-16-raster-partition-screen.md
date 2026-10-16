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

Not executed at draft freeze. The result will be recorded here after the
single managed run; source and hypothesis must be committed before real input.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the private 721 s false anchor is established, but its raw peer/optical cause remains unknown. This study addresses local measurement availability and shared derivation before authority; it cannot identify that private cause.
- Existing feature coverage: saved sample4 and public current rasters and effective/glare visibility are reused with original Recipe-derived sectors. Sample4 has no user Artifact templates/exclusions in its retained Recipe; existing static/Artifact outcomes stay in original captures. No static learning, Recipe construction or Artifact rejection is rerun. Experimental switches, Local XY, model inference, initial-FULL and completed resolution are bypassed by this offline read-only measurement entry; their closed results are not invalidated.
- Execution scope: `tests/diagnostics/s11_raster_partition_screen.py` measures the frozen 187-unit roster, actual Oil candidates only, and the 85 existing directed peer relations; tests exercise synthetic pixels. New descriptive hypotheses have no production consumer, no native/path truth and no final Oil/Foam/report outputs. Original labels and bytes remain unchanged.
- Logic-map impact: NONE — diagnostic helpers only; production defaults, ownership, extraction and publication are unchanged.
- Failure-registry impact: NONE — current identity/provenance/threshold warnings already cover this hypothesis; no new physical mechanism is promoted.
