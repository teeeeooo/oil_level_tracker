# Sample3 visible-Oil reappearance: source reply and release causality

Date: 2026-10-10. Base head: `52598f021f05a380ea7cd3714dde6efae9650000`.
Follow-up to the [bounded source inspection](2026-10-10-sample3-gap-source.md).
The [machine archive](2026-10-10-sample3-reappearance-causality.json.gz) retains
the frozen inputs, observer scripts, saved-input comparison, native measurements,
actual release traces and verification. This is a causal investigation with no
production or legacy-truth changes.

## User source-role reply — closed

The [bound reply](2026-10-10-sample3-gap-source-reply.json) preserves the user's
words and [red-marked attachment](2026-10-10-sample3-gap-user-marking.png):

> 내가 빨간색으로 점찍어놨어 그 라인이 유면이야. 정확한 픽셀이 여기라는 의미는 아니야. 그 라인 부근이라는거지

Both A/f2249 at 75.041633s and B/f2339 at 78.044633s have Oil near the marked
upper yellow/brown-to-dark boundary. The attachment is byte-for-byte preserved
(SHA-256 `6afaba042c834ad3f1b1f36adc13752cc99c5ed6efb3fe7f3409504783583e36`).
The original clean image and frozen question remain unchanged.

This closes the physical role/visibility question for **these two views**.
Their missing final Oil observations are relevant positive cases. The marks do
not define a scalar Y, uncertainty interval, pixel tolerance, fitted polyline,
all-sector candidate identity, continuous visibility between views, or an
entire confirmed track. No painted-pixel extraction or fitting was performed.
The older 95/105s unusable judgments remain closed; all seven videos remain
exposed development/regression material.

## Actual baseline gate and its limits

Reuse the original 151 current detections from the
[episode audit](../../60-evidence/s11/2026-10-08-episode-source-review-validation.md#sample3-whole-episode-detector-audit).
The full unchanged completed resolution, including diagnostics, reproduces
exactly. An additional original-video run uses the existing debug branch to
capture **all 37 offsets 66–102**, from the implicated track's first appearance
through the first later numeric return. All 151 raw detections and the entire
completed resolution equal the old saved originals. The saved Recipe is unchanged;
the same explicitly confirmed `UNKNOWN_REVIEW` replay state is used.

The actual path is
[`OilMaterialPhaseLifecycleOwner._transition_barrier`](../../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py)
→ `_drain_release_evaluation` → empty allowed-owner set → selector UNKNOWN.
This is a filled barrier reached at offset 14/f1110/37.037s by
`FILL_SPAN_MATERIAL_VETO`, not an initial-FULL configuration. Its old fill owner
snapshot ends at offset 11/Y272; no snapshot coordinate becomes an observation.

| View | Upper-region internal row | Historical direction / progress / agreement | Recent direction / progress / agreement | Actual first failed release predicate |
|---|---|---|---|---|
| A, offset 90 | row 000090:000; track 000066:0063; representative Y217 | upward / 22px / 0.667 | stationary / 0px / 0.8 | `downward_direction` |
| B, offset 96 | row 000096:000; same internal track; representative Y228 | upward / 22px / 0.667 | downward / 11px / 0.8 | `downward_direction` |

The upper row passes the other serialized direct-release predicates in each
baseline view, including material checks. All five/three pre-restriction
publishable rows are excluded by the empty allowed set. This explains the
**mechanical exclusion**, not the correctness of those rows' physical identity.
No hidden selector preference can restore an Oil row after this hard filter.

Source inspection confirms that `_drain_release_evaluation` reads recent
direction/progress/agreement only when `policy.initial_full` is true. A later
filled cap under UNKNOWN uses historical confirmation values. Recovery is
recorded as `not_evaluated` here; the release engine receives no rows for this
non-initial-FULL route. The partial-fill delayed route is not a fallback from
this filled barrier. These are actual branch semantics, not proof that every
branch should be broadened.

**A and B are distinct cases.** Merely reading recent direction still does not
make A a drainage observation. The existing proposed
[direction-neutral interface owner](../../20-architecture/s11-physical-interface-evidence-repair-design.md#4-direction-neutral-visible-interface-ownership)
requires independently validated current interface evidence; internal anchor
status, persistence and a newly visible line cannot satisfy that gate by themselves.

## Spatial evidence does not certify the historical track

All **719** captured diagnostic candidate records join uniquely by source and Y
to the current candidates and then the completed candidates. In this capture
the diagnostic and serialized offsets also agree; this is verified, not assumed.
The [geometry comparison](2026-10-10-sample3-reappearance-candidates.png) shows
discrete native material-path sector rows without connecting them into a contour.

| View | Upper material candidate Y | Native sector rows, source coordinates |
|---|---:|---|
| A | 219 | sector 1: X[769,813), Y234; sector 2: X[813,858), Y216; sector 3: X[858,902), Y219 |
| B | 227 | sector 1: X[769,813), Y236; sector 2: X[813,858), Y227; sector 3: X[858,902), Y225 |

Agent inspection places the central/right measurements near the broad upper
transition and the left sample farther below it. That is not a new exact human
label or a claim that the whole three-sector path follows Oil. Other upper-row
members are scalar proposals without a captured native contour. Neither their
nearby Y nor shared row membership proves they measure the same structure.

The internal track begins at offset 66/f1889/63.029633s, before the substantial
framing/focus change. Its confirmed `ANCHOR_TRAJECTORY` uses four observations
in offsets 70–75 (65.031633–67.534133s), accumulating 22px upward progress.
At offset 75 its only member is `distributed_sobel_path` Y216; earlier members
include phase-scan/calibrated proposals at the bright upper circular region.
The user's later A/B reply cannot certify these earlier objects, the camera's
contribution to displacement, or all intervening association edges.

## One recent-direction attribution probe — closed without promotion

Freeze one counterfactual after inspecting baseline A/B scalar predicates and
before its outcomes: only inside `_drain_release_evaluation`, substitute the
existing recent direction/progress/agreement for historical fields for a
non-initial-FULL policy. Delegate all original predicate logic. Keep configured
initial state, birth-after-filled requirement, thresholds, material/entrance
checks, confirmation, ambiguity, assignment, continuation and selector unchanged.
Run the **entire saved 151-row window**, not an A/B-only restart.

The probe releases track 000066:0063 at offset 82/71.037633s using recent downward
30.5px progress. After loss it hands off to track 000084:0079 at offset 85/72.539133s.
That different owner supplies **Y337 at A and Y339 at B**, near lower internal/rim
structure and clearly separated from the user's upper Oil region. The native
path is shown for A; B's short marker denotes only its scalar phase-scan center.
The lower selections are opposing evidence, not recovered Oil.

| Readout | Baseline | Recent-basis-only probe |
|---|---:|---:|
| Numeric Oil rows | 29 | 41 |
| Changed Oil values | — | 18: 15 newly numeric, 3 former numerics lost |
| A / B | missing / missing | lower structure / lower structure |
| Foam coordinates and confidence | original | all six fields equal on all 151 rows |

All changed rows, including unreviewed alternatives, are retained in the archive.
The 30.03/34.5345s earlier qualitative/ruler checkpoints retain their original
numeric outputs; this does not broaden their truth scope. The lost numerics at
81.014267/83.516767/84.017267s remain unqualified, not automatically true positives.
No label or golden is changed to count the extra values as improvements.

This experiment is **CLOSED WITHOUT PROMOTION**. It isolates a release-basis
asymmetry and demonstrates why repairing that predicate alone is insufficient:
earlier ownership and subsequent handoff can select a different physical object.
Do not add an A/B whitelist, remove the barrier, relax motion/material thresholds,
expand the recovery route or run successive rescue variants from this result.

## Next source judgment

The [C/D source review](2026-10-10-sample3-confirmation-role-review.png) and
[frozen questions](2026-10-10-sample3-confirmation-role-review.json) ask about
the **physical role** near the short cyan marks in the actual confirmation
window: C/f1949/65.031633s and D/f2024/67.534133s. They use unchanged source pixels
at 2× nearest-neighbour scale, with a short candidate-location guide rather than
an inferred contour. Agent inspection cannot certify C's aperture/bright-cap
feature as Oil or D's blurred feature as observable Oil.

The answer distinguishes an earlier different-object/unclear confirmation from
a valid Oil track whose later release basis is stale. A positive answer still
does not certify all association edges. Hold that dependent attribution for the
reply; A/B and 95/105s are not reopened. No Windows work is needed at this boundary.
Any behavior proposal must separately satisfy the current
[physical-interface controls and gates](../../30-validation/s11-physical-interface-evidence-repair-validation.md#required-two-sided-controls).

## Verification

- Source-reply and original attachment hashes bind; clean question/image remain
  unchanged. C/D source and rendering metadata are recorded separately.
- Saved-input baseline equals the entire original resolution; original-video
  debug capture equals all 151 current detections and the entire final resolution.
- Tracking fingerprint remains `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1`.
  A/B and the later-return source rasters equal the prior ordinal captures.
- All source/input hashes are unchanged; runtime observer/counterfactual patches
  are restored. No production, Recipe, truth, public-output or Foam edits.
- Every changed counterfactual row and all 719 unique candidate joins are retained;
  the counterfactual is not a test pass or field-effectiveness result.
- Focused artifact/link checks, detector governance and `git diff --check` cover
  this diagnostic-only change. No broader detector suite is required by a source
  change, since there is none. O2 remains open and field disposition remains FAIL.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: A/B visible Oil with missing output is human-qualified regionally. Baseline upper-region rows are mechanically excluded at `OIL-PHASE-DRAIN`; the earliest physical identity error remains UNKNOWN pending confirmation-window source roles and spatial/temporal ownership. The recent-basis-only probe selects lower opposing structure at both views, so its extra numerics are not a repair.
- Logic-map impact: NONE — existing branches and saved-input attribution only; no production owner or predicate changes.
- Failure-registry impact: NONE — the hard-lock/identity/handoff recurrence is explained by existing F03/F04/F05/F08; no new mechanism is adopted.
