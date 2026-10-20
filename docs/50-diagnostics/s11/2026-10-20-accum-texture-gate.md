# Accum texture-gate extraction (ATG-1) — 2026-10-20

**Status: CLOSED — SAME MECHANISM IN THE CLEAR FOAM LAYER, PLUS A SECOND BLOCKER.**
At 673/675/677 s, every reviewed top-K boundary candidate loses ordered-lower
authority to AAT-1's texture exclusion. At 678.5 s (and the 679 s transition),
texture no longer blocks. The boundary instead loses to the nearest-ordered-lower
demotion under an upper anchor, the field analogue of TPA-1's second layer. The
texture/authority direction therefore has field relevance, and repairing support
alone is not sufficient. The [Work Plan](../../00-project/work-plan.md) owns the
next choice. No detector change follows from this record.

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

## Boundary-row results (table D, relayed)

Run `a9ccece3-…`, `trace=full`, Accum. Only review-009 interface candidates were
read. `ol` = ordered-lower. `sup*` = support if texture-only peer exclusions were
lifted.

| Frame / s | idx: Y source | top-K | Authority / identity [failed] | ol | sup → sup* | Conflict / terminal / row | Tracklet | Pattern |
|---|---|---|---|---:|---|---|---|---|
| f16136 / 673.0 | 26: Y490 phase_transition | Y | CONT / CONT [olX] | 1 | 0.00 → 0.82 | 0.75 / 1.00 / 1.00 | 1 / GLOBAL_PATH_OR_RUN_BOUND | TEX0 |
| | 10: Y493 material_path | **N** | — | — | 0.00 → 0.73 (recomputed) | 0.75 / 1.00 / (1.00†) | pruned | NOT_TOPK |
| f16184 / 675.0 | 22: Y496 calibrated_high_recall | Y | CONT / CONT [olX] | 1 | 0.00 → 0.88 | 0.75 / 1.00 / 1.00 | 1 / GLOBAL_PATH_OR_RUN_BOUND | TEX0 |
| | 10: Y497 material_path | Y | CAND `material_layer_terminal` / CONT [olX] | 1 | 0.00 → 0.90 | 0.75 / 1.00 / 1.00 | 0 / CANDIDATE_ONLY | TEX0 |
| | 25: Y498 phase_transition | Y | CONT / CONT [olX] | 1 | 0.00 → 0.88 | 0.75 / 1.00 / 1.00 | 1 / GLOBAL_PATH_OR_RUN_BOUND | TEX0 |
| f16232 / 677.0 | 25: Y444 phase_transition | Y | CONT / CONT [olX] | 1 | 0.00 → 0.75 | 0.77 / 0.91 / 1.00 | 1 / GLOBAL_PATH_OR_RUN_BOUND | TEX0 |
| | 23: Y449 calibrated_high_recall | Y | CONT / CONT [olX] | 1 | 0.00 → 0.84 | 0.73 / 1.00 / 0.97 | 1 / GLOBAL_PATH_OR_RUN_BOUND | TEX0 |
| | 10: Y451 material_path | **N** | — | — | 0.78 (recomputed) | 0.66 / 1.00 / 0.88 | pruned | NOT_TOPK |
| | 26: Y453 phase_transition | Y | CONT / CONT [olX] | 1 | 0.00 → 0.84 | 0.60 / 1.00 / 0.79 | 1 / GLOBAL_PATH_OR_RUN_BOUND | TEX0 |
| f16268 / 678.5 | 12: Y415 material_path | Y | CONT / CONT [nearest] | 1 | 0.59 | 0.53 / 0.00 / 0.53 | 1 / GLOBAL_PATH_OR_RUN_BOUND | GATE_OTHER |
| | 24: Y415 calibrated_high_recall | Y | CONT / CONT [nearest] | 1 | 0.81 | 0.53 / 0.00 / 0.53 | 1 / GLOBAL_PATH_OR_RUN_BOUND | GATE_OTHER |
| f16280 / 679.0‡ | 25: Y412 / 11: Y414 / 20: Y416 | Y | CONT / CONT [nearest] | 1 | 0.79 / 0.74 / 0.79 | 0.45–0.58 / 0.00 / 0.45–0.58 | 1 / GLOBAL_PATH_OR_RUN_BOUND | GATE_OTHER |

† One numeric column was missing in transcription. The value follows from
`conflict = row × (1 − 0.25 × terminal)`. ‡ Transition frame: the liquid–liquid
layer, not a decision frame. `[nearest]` = `nearest_ordered_lower_interface`.

Record checks: review-009 stores f16400 as `visible` with no interface candidate.
Given the user's clarification (the liquid–liquid layer exists but is hard to
detect), this is kept as stored and not edited. The first table B row
(673.0 s Y367 idx25) reads sup 0.00 / sup* 0.80 / conflict 0.84 / terminal 0.00 /
row 0.84 from the original output. The earlier four-column version was a
transcription gap.

## Decision

1. **673–677 s: same mechanism as AAT-1.** Every reviewed top-K boundary
   candidate is ordered-lower, continuation-only and fails only
   `ordered_lower_cross_representation`, with support 0.00. Its own conflict is
   0.60–0.77 because the raw row support is about 1.0. The terminal term's
   maximum 25 % reduction leaves 0.75, exactly as on sample4. Its peers are
   excluded only by texture. Keeping them would give 0.73–0.90, far above 0.12.
2. **The terminal-partition feature transfers.** It is 0.91–1.00 on all nine
   reviewed boundary rows in 673–677 s. It is 0.00 on most upper rows in table B
   (inside the Foam layer, between the Foam front and the boundary). Exceptions
   are the 678.5 s upper anchor Y229 (0.68) and the 679 s upper rows (0.36–0.52),
   so it is again not a complete discriminator.
3. **A second blocker follows at 677–679 s.** At 677 s an upper anchor (Y235
   `material_path`, `ordered_lower_interface`) already sits between the Foam front
   (Y210) and the boundary. By `_demote_non_nearest_ordered_lower_anchors`, the
   boundary would lose the anchor role even with support restored (inference).
   At 678.5 s the boundary has support but fails only the nearest-anchor gate
   under upper anchor Y229. Published Oil follows upper rows Y317/269/238, 177–184 px
   above the reviewed boundary. This matches TPA-1's "Oil owner above the Foam
   front" layer. With no upper anchor (673/675 s, zero anchors), support repair
   alone could make the boundary anchor-eligible; selection beyond that is
   untested.
4. **Top-K pruning is a separate, smaller seam.** The `material_path` member at
   673 and 677 s is pruned before gating, although at 677 s its recomputed
   support is 0.78. Other families at the same boundary remain in top-K, so this
   does not explain the loss by itself.

The handoff's rule is met: **same mechanism → the texture/authority direction has
field relevance.** This record also shows that a repair limited to support would
reproduce TPA-1's next failure on Windows. A successor must address both:
support for a terminal boundary under textured Foam, and the role of an upper
ordered-lower owner between the Foam front and that boundary. No successor is
selected here.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-EPISODE`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` cross-representation support excludes texture-conflicted peers of the reviewed Accum boundary at 673–677 s (same as sample4 AAT-1). At 677–679 s, `OIL-AUTHORITY`'s nearest-ordered-lower demotion under an upper anchor follows, and `OIL-SELECTOR` publishes upper rows (relayed values).
- Existing feature coverage: the ④ FULL+ON v2 bundle (commit `4c72ebb`, spatial Artifact templates as recorded for ④, cost-first/RGB/Local XY/top-exit OFF), full trace with sequence snapshot. The saved features reproduce every stored cross-representation support value.
- Execution scope: read-only extraction by `tests/diagnostics/s11_accum_texture_gate_extract.py` on the saved trace, plus the user's direct review-009 replies on Windows. No detector, resolver or pipeline run; no local access to private files.
- Logic-map impact: NONE — diagnostic reading; ownership and control flow unchanged.
- Failure-registry impact: NONE — the field result corroborates the existing AAT-1/TPA-1 mechanisms already pointed to by S11-F04/F05/F06/F10; no new mechanism class.
