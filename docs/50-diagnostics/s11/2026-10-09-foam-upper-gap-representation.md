# Visible Foam upper surface and ordered-gap representation — 2026-10-09

Base: `98466befb24c6b8777c9b12cd45219144a3b49a7`.
The [Work Plan](../../00-project/work-plan.md) owns current state.
This investigation changes an offline diagnostic helper, not production behavior.

## Human visibility checkpoint closed

User: **“아주 약간의 빈공간이 있어서 윗경계가 보임”**.
The [attributed reply](2026-10-09-foam-upper-visibility-reply.json) pins the
unchanged [review image](2026-10-09-foam-upper-visibility-review.png) and three
originals. It establishes a narrow space above Foam and a visible physical upper
surface at the displayed 54/55.5/56 s times. It does not establish exact coordinates,
full-width visibility, an air mask, any current candidate, or a reply at 54.5 s.
No further visibility question or pixel marking is needed for these scenes.

The earlier cyan lines remain internal Foam texture. The lower Foam/Oil boundary
remains the separate Oil target. Foam height is therefore a meaningful local
goal here; the previous missing-height case cannot be explained as a user-confirmed
invisible upper surface. This still does not make the old rejected texture fronts
correct measurements or justify relaxing their episode gates.

## Hypothesis 1: did support cleanup erase the narrow gap?

Before measurement, a new preflight froze the same three late frames, unreviewed
54.5 s, and existing 14/15/16 s positive/mixed/rim controls. Instrument only the
actual `_clean_support_mask` calls in the unchanged Foam owner. Preserve the
raw white membership, cleaned membership and every fully observed vertical
raw-support gap filled by cleanup. Compute actual raw-component parent joins.

All seven Foam replays, 24 retained component records and label rasters exactly
match the saved capture. These are isolated Foam-owner executions, without video
decode, Oil, sequence resolution, settings changes or production changes.

| Time | Raw / cleaned white components in whole ROI | Raw components contributing to selected component | Added pixels in selected component | Fully observed raw vertical gaps filled, whole ROI |
|---|---:|---:|---:|---:|
| 54 s | 8 / 3 | 2 | 139 | 37 |
| 54.5 s | 10 / 3 | 1 | 119 | 15 |
| 55.5 s | 8 / 2 | 1 | 126 | 7 |
| 56 s | 14 / 2 | 1 | 208 | 12 |

Those gaps are membership holes, **not labeled air**. The original/raw/clean
comparison does not support the claim that cleanup alone destroyed the visible
upper space. Much of the upper outline is already present before cleanup and
retained afterward; lower texture holes are also filled. In particular the latter
two selected components already come from a single raw parent. No per-pixel
physical loss rate can be assigned from the regional reply. The cleanup hypothesis
is not adopted as a repair; morphology parameters stay unchanged.

## Hypothesis 2: retain both sides of a narrow photometric gap

Discovery found the existing `s11_foam_front_alternatives.py` owner, which records
all unranked absolute-gradient maxima near component tops, and the existing
O1 raw central-difference operator. Reuse that owner with an **optional**
`include_gap_brackets=True` argument; default observations remain identical.
The [architecture](../../20-architecture/s11-foam-component-diagnostics-architecture.md#optional-ordered-dark-gap-brackets)
defines bounds, coordinates and unavailability.

The new observation retains adjacent falling/rising **signed** peaks and the
intermediate darker raw samples. It searches signs separately: an absolute-
magnitude plateau can merge opposite slopes around a two-pixel trough, whereas
the signed observation preserves both transitions. This differs from strongest,
lowest, nearest, smoothest or blanket-upper selection. Both original inspection
radii, 4 and 8 pixels, remain inspection extents, not fitted acceptance widths.

All tied peak intervals, all minima and all pairs are retained. Invalid stencil
or corridor pixels cannot be bridged; the original window-censoring flag remains.
A partially censored window can still contain a completely observed local pair.
There is no amplitude or gap-width cutoff, rank, smoothed path, scalar, physical
air/Foam label, candidate authority, or integration into the running detector.

The signed-pair rule and complete seven-frame input population were frozen before
their numerical readout. Earlier original images and support masks were already
exposed; this is development evidence, not a held-out efficacy evaluation.

| Case / inspected component | Occupied columns | Columns with pairs at radius 4 | Columns with pairs at radius 8 | Pairs at radius 8 |
|---|---:|---:|---:|---:|
| 14 s, mixed C2 | 50 | 4 | 28 | 37 |
| 15 s, mixed C2 | 48 | 4 | 28 | 36 |
| 16 s, mixed C2 | 41 | 3 | 28 | 32 |
| 16 s, confirmed glass-rim C1 | 46 | 7 | 30 | 30 |
| 54 s, C1 | 67 | 12 | 57 | 73 |
| 54.5 s, C1, unreviewed | 62 | 10 | 55 | 78 |
| 55.5 s, C1 | 65 | 6 | 38 | 44 |
| 56 s, C1 | 67 | 3 | 47 | 54 |

The agent inspected the original/overlay comparison. Some lower rising edges
follow the visible upper-Foam region, while multiple alternatives and glass
features also remain. This is an agent-attributed regional observation, not a
new human-approved contour or numeric accuracy score. At radius 8 the late C1
windows are partially censored in 46/67, 30/65 and 38/67 columns respectively;
only their locally complete pairs are retained, never an extrapolated whole path.

**Decision:** retain the diagnostic representation. Reject gap-pair existence
as a standalone Foam classifier: the confirmed glass rim produces 30 pairs,
and identical synthetic pixels can represent air, internal texture or structure.
Neither a larger window nor more alternatives proves true-front recovery. Do not
promote the lower member of each pair or fit a fraction/strength threshold here.

## Verification and next boundary

- **28 focused tests pass** across the existing front-alternative and new gap
  suites. They cover step/ribbon polarity, one-/two-pixel troughs, plateau ties,
  multiple unequal gaps, mask/glare interruption, clipped windows, unchanged
  inputs, explicit physical ambiguity and opt-in/default equality.
- **Seven real cases / 24 components / 990 occupied columns** compare exactly
  against the helper at base `98466be`: default output is identical, and removing
  the opt-in fields also restores the exact old output.
- All 221 production source pins and frozen input hashes remain unchanged.
  No full detector acceptance, four-sample behavior improvement, O2 pass or
  Windows qualification is claimed from offline measurements.

The next design requirement is candidate-local material and structural identity
for the retained edge alternatives. Join actual side support and independently
attributed structure evidence to each local edge before reducing it to a scalar;
protect the early real-Foam regions and oppose the confirmed glass rim as well as
the late internal texture. Existing scalar/whole-component membership and a
paired dark gap cannot supply that identity. Reuse these results and the closed
human replies rather than re-running visibility, appearance ranking or a window
sweep. No new user judgment or Windows action is needed merely to record this
representation result; a future physical ambiguity must be posed as a distinct
question with its concrete evidence.

Full preflights, scripts, masks, point observations and inspected figures remain
under `sample/output/s11-foam-upper-gap-20261009-001/`. The
[machine record](2026-10-09-foam-upper-gap-representation.json) preserves all hashes,
both preflights, scripts, complete pair records and default-regression results.
Source images, labels and recipe are not edited. FIELD FAIL / O2 OPEN remains.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: confirmed internal-texture fronts are generated by component-extreme selection before episode processing. Cleanup alone is not established as the loss of the newly human-confirmed visible upper surface. Physical selection among the retained alternatives remains unresolved.
- Logic-map impact: NONE — an opt-in offline observation extension has no production caller or authority.
- Failure-registry impact: UPDATED — F07 closes visibility uncertainty and records the signed-gap representation plus confirmed-rim opposition; no threshold, episode or physical-classifier repair is promoted.
