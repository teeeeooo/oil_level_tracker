# A2 preparation: uncertainty-preserving target binding

Date: 2026-10-07. Source head: `2d63a2e6a858c882f1da2a4968c599c034cbc9f5`.
Scope: offline W3 truth binding and recorded-selection baseline; no A2 predictor
or production detector behavior is adopted. Field disposition remains `FIELD FAIL`.

## Implemented repair

The [preflight](../../50-diagnostics/s11/2026-10-07-sample4-a2-control-preflight.json)
contains seven confirmed Oil correspondences and three definite wrong Oil targets.
The latter have uncertain physical identity: one unresolved and two tentative
artifact interpretations. Previously, target binding required physical
`non_interface` for `other_non_target`, forcing either loss of the known target
error or an unjustified physical label.

The existing `tests/diagnostics/s11_target_truth.py` owner now also accepts
physical `uncertain` for an explicitly indexed `other_non_target` candidate.
Bulk inheritance still requires physical `non_interface`; unreviewed candidates
cannot become negatives, and uncertain candidates cannot become positive targets.
Original physical labels, input bytes, old valid projections and schema remain
unchanged. No artifact subtype is inferred from notes.

## Real binding and baseline evaluation

The existing O2 extraction, review-record transactions, target snapshot and W3
evaluator were used over all 153 saved Oil candidates in seven frames. The
record/run IDs are **derived import identifiers**, not original indexed bundle
identifiers. This execution asserts exact saved-capture correspondence, not
original trace-bundle link verification. The attribution imports prior human
replies and does not claim a new human review.

| Truth or output | Count |
|---|---:|
| Physical interface / target | 7 |
| Physical uncertain / explicit non-target | 3 |
| Unreviewed / unreviewed | 143 |
| Recorded selected candidates supporting target | 7 |
| Correct target support | 4 |
| Wrong-target support | 3 |
| Confirmed targets left unresolved | 3 |

The baseline projects only the recorded completed-selection candidate as
`INTERFACE_SUPPORTED`; every other candidate is `UNRESOLVED`, not a negative.
This is a comparison baseline, not a newly fitted identity classifier. Its
operating point is unchanged, fit partitions are empty, and the evaluator reports
`EXPLORATORY_UNCALIBRATED`. Precision/recall of 4/7 describe only these exposed
reviewed observations, not field accuracy. Overall abstention includes 143
unreviewed candidates and is not evidence of good discrimination.

Local path, scalar, contour and physical entity truth remain absent. All scalar
decisions are `NOT_EVALUATED`. No recording-independent calibration or holdout is
created. The existing Mac corpus remains usable for authorized bounded local
exploration; this preparation does not require obtaining another video first.

## Verification and preservation

- Target truth and shadow evaluation tests: 58 passed.
- Review records, review semantics, shadow targets and aggregation contracts:
  115 passed. Total: **173 focused tests**.
- The actual `bind-target` CLI is covered from a foreign working directory;
  source labels remain byte-identical and target errors retain physical uncertainty.
- Source, prior reply, saved candidate and new artifact hashes were checked.
  No production source or runtime output changes, so prior A1 runtime equality
  evidence is not rerun or extended to a new behavior claim.

The [compact receipt](2026-10-07-a2-target-binding.json) pins sources, all inputs,
full local artifacts, test logs and summarized evaluator output. Full packet,
labels and review history, mapping, immutable snapshot, baseline predictions,
report and helper are retained under
`sample/output/s11-a2-target-binding-20261007-001/`. The original receipt captured
`bind.log` while it was open; the compact receipt also pins its final bytes.

## Joint static and temporal context

The user's direct answer, **“두 가지를 함께 봐야 구분 가능”**, is preserved in the
[attributed reply and review manifest](../../50-diagnostics/s11/2026-10-07-sample4-temporal-context-human-reply.json).
It establishes the need to consider static boundary/layer context together with
video changes; it does not label cross-frame entity continuity.

The original 40–45 s recording was decoded as 151 lossless context crops at
30 fps. Four reviewed frames match the prior saved detector ROI pixels exactly.
The local `sample/output/s11-a2-temporal-context-20261007-001/review.html` offers
playback, frame stepping and optional guides only at previously reviewed frames.
No intermediate boundary is generated or interpolated. Browser checks verified
frame jumps, progression to the final frame, and guide hiding on unreviewed frames.

The pending question asks whether the already confirmed actual Oil boundary at
42.5 s is visibly continuous with the actual Oil boundary at 44 s, or whether
occlusion/replacement/uncertainty prevents that relation. The existing tracklet
mixes correct and incorrect selections and cannot supply this truth. Existing
registered-motion summaries and past boundary-residual measurements describe
change but do not independently identify a physical boundary. A new readout must
jointly examine candidate-local spatial context and temporal correspondence;
this record does not freeze or claim implementation of that hypothesis.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: existing captured Oil alternatives lose eligibility at `OIL-AUTHORITY`; the optical cause remains unresolved. This change repairs an offline target-binding representational gap, not detector authority.
- Logic-map impact: NONE — only offline truth binding and evaluation preparation change; production control flow and accepted A1 diagnostic ownership stay unchanged.
- Failure-registry impact: NONE — no new detector mechanism is adopted; candidate-family, whole-track and motion-only shortcuts remain excluded and uncertain physical labels are preserved.
