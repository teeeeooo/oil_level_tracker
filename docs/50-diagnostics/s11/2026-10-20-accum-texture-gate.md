# Accum texture-gate extraction (ATG-1) — 2026-10-20

**Status: FIRST RETURN RECEIVED / BOUNDARY ROWS PENDING.** The first return
confirms the bundle and the tool's reconstruction, and adds human-reviewed
boundary candidates (review-009). It does **not** yet show the gate state of
those candidates: table B's row cap dropped every one of them. A bounded
follow-up asks for exactly those rows. The direction decision from the
[handoff](../../60-evidence/s11/2026-10-20-texture-authority-handoff.md#decided-next-step-user-2026-10-20)
stays open. [Work Plan](../../00-project/work-plan.md) is unchanged.

Procedure and request text are in the
[Accum texture-gate extraction](../../40-operations/s11-current-windows-field-qualification.md#accum-texture-gate-extraction).
All values below were relayed from the Windows work PC. No private bundle,
image or label file was inspected locally.

## Received

**Identity.** Run `a9ccece3-…`, `trace=full`, Accum 601 records, tolerance
12.0 px, resolver `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2`.
This is ④. Every target frame was captured with a sequence snapshot.

**Reconstruction check.** Recomputed cross-representation support equals the
stored value for all top-K Oil refs: 102/102 at the six target frames, and zero
mismatches over all 20 captured frames in 671–681 s. Per-peer attribution from
saved features is therefore valid for this bundle.

**Table A (frame-level).**

| Frame / s | Eligible Foam Y | Selected Oil | Anchors | top-K / raw |
|---|---|---|---:|---|
| f16136 / 673.0 | 306 | none | 0 | 16/27 |
| f16184 / 675.0 | 246 | Y317 `continuation` | 0 | 17/26 |
| f16232 / 677.0 | 210 | Y269 `continuation` | 1 | 17/27 |
| f16268 / 678.5 | none | Y238 `continuation` | 1 | 17/28 |
| f16280 / 679.0 | 80 | none | 2 | 18/27 |
| f16400 / 684.0 | none | none | 1 | 17/28 |

**Review-009 (user replies recorded with the existing O2 `record` workflow).**

| Frame / s | Visibility | Interface candidates (`candidate_input_index`) | Reported boundary Y |
|---|---|---|---|
| f16136 / 673.0 | visible | 10, 26 | not stated |
| f16184 / 675.0 | visible | 10, 22, 25 | 496–498 |
| f16232 / 677.0 | visible | 10, 23, 25, 26 | 444–453 |
| f16268 / 678.5 | visible | 12, 24 | 415 |
| f16280 / 679.0 | visible | 11, 20, 25 | 412–416 |
| f16400 / 684.0 | reply "안 보임" (not visible) | none | — |

Multiple acceptable candidates are kept as in review-004. Unnamed candidates stay
`unreviewed`. Review-006 was not opened. The agent regenerated the idx-guide
images to remove overlapping labels; packet idx/Y were unchanged.

## Analysis

1. **No reviewed boundary candidate appears in table B.** Table B keeps at most
   five rows per frame: the selected row, anchors, then ordered-lower rows by
   ascending Y. That keeps the upper rows and drops the deeper reviewed
   boundary. Table C's `TEX0=20` and `GATE_OTHER=20` describe those upper rows
   only. They are mechanical pattern counts and say nothing yet about the
   boundary. *(Tool defect, fixed in `125af54` by `--rows`.)*

2. **Published Accum Oil is far above the reviewed boundary.** At 675/677/678.5 s
   the selected rows are Y317/269/238. The reviewed boundary is Y496–498/444–453/415,
   which is 177–184 px lower. At 673 and 679 s nothing is published although the
   boundary is visible. This is observed final output against reviewed truth.
   Whether the selected rows are Foam-layer texture or another structure is
   not reviewed here.

3. **Upper rows match the texture-exclusion pattern.** Every printed row between
   the Foam front and the reviewed boundary is ordered-lower, continuation-only
   and fails `ordered_lower_cross_representation`, with support 0.00 and `sup*`
   0.40–0.89. Unlike sample4, their terminal partition support is mostly 0.00
   (conflict 0.58–1.00). Excluding these rows is not obviously harmful, because
   they are not the reviewed boundary.

4. **Near-boundary anchors lose to an upper anchor (inference).** At 678.5 s, the
   upper Y229 `raster_material_path` row is the anchor. Y392/403 fail only
   `nearest_ordered_lower_interface` (`_demote_non_nearest_ordered_lower_anchors`)
   despite support 0.63/0.45. At 679.0 s, Y391/392 are anchors 20–25 px above
   the reviewed Y412–416, but their tracklets are not admitted
   (`INSUFFICIENT_NET_PROGRESS`). This resembles TPA-1's "owner above the Foam
   front stays selectable" more than AAT-1's zero support. It is unconfirmed
   until the reviewed rows themselves are read.

## User clarification of the Foam-collapse frames (2026-10-20)

The two disagreements below came from the physical scene, not from recording
errors. This is the user's direct explanation. It is recorded beside both earlier
answers and replaces neither.

- **f16280 / 679.0 s has two boundaries.** Foam is collapsing into liquid at this
  moment. Near **Y213** there is an **air–liquid** boundary. Near **Y412–416** a
  faint **liquid–liquid** layer is visible: the collapsed Foam liquid lies on the
  Oil before it mixes in. Both layers are transparent, so the user found the
  layer hard to call. The R22 answer (Y213) and the review-009 answer (Y412–416)
  name these two different boundaries. Neither is a mislabel of the other.
- **f16400 / 684.0 s.** Foam is gone, and two transparent liquid layers remain,
  separated only by a slight color difference. The user answered "not visible"
  because a detector would hardly separate them. Close inspection can
  distinguish them by color. The answer is a practical detectability judgment,
  not physical absence. The stored-value check in the follow-up only confirms
  what was recorded.

Consequences for ATG-1:

- **Decision frames are 673–678.5 s**, where a Foam layer clearly sits over Oil.
  679 and 684 s are **Foam-collapse transition** cases. They are reported but
  do not decide "same / different mechanism" by themselves.
- At 684 s the stored anchor Y205 (`material_path`, admitted, not selected) lies
  near the earlier air–liquid Y213 at 679 s. This is a neighbouring-frame
  coincidence; no air–liquid Y was reviewed at 684 s.
- **Oil target during collapse — decided by the user** and recorded in the
  [reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#accum-foam-collapse-target--2026-10-20):
  the best case separates the air–liquid top and the liquid–liquid layer; the
  fallback is the air–liquid top. This does not change the 673–678.5 s
  decision frames of ATG-1.
- **Transcription gap.** The first table B row (673.0 s, Y367, idx25) has four
  numeric columns instead of five. That row is not a reviewed candidate and is not
  used above.

## Follow-up requested

The bounded `--rows` extraction for the reviewed candidates only. It prints table D
with stored gates where top-K, and `NOT_TOPK` with recomputed support and raw
texture features otherwise. The decision rule from the handoff applies on receipt, judged on the 673–678.5 s
decision frames:
- reviewed candidates ordered-lower, continuation-only, failing only
  `ordered_lower_cross_representation` with texture-only exclusions → same
  mechanism as AAT-1;
- otherwise (top-K pruning, nearest-anchor demotion, admission or other gates) →
  a different first harmful stage. Stop sample4-only texture work.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-EPISODE`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: unknown for the reviewed Windows Accum boundary; the first return omits those candidates. Upper non-boundary rows show texture-excluded support, and near-boundary anchors show nearest-anchor demotion or non-admission (relayed values).
- Existing feature coverage: the ④ FULL+ON v2 bundle (commit `4c72ebb`, spatial Artifact templates as recorded for ④, cost-first/RGB/Local XY/top-exit OFF), full trace with sequence snapshot. The saved features reproduce every stored cross-representation support value.
- Execution scope: read-only extraction by `tests/diagnostics/s11_accum_texture_gate_extract.py` on the saved trace, plus the user's direct review-009 replies on Windows. No detector, resolver or pipeline run; no local access to private files.
- Logic-map impact: NONE — diagnostic reading; ownership and control flow unchanged.
- Failure-registry impact: NONE — pending the boundary-row follow-up; no new failure mechanism is established yet.
