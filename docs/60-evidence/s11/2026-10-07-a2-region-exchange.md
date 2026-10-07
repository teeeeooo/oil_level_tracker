# A2 joint temporal region-exchange result

Date: 2026-10-07. Frozen source/design head: `f42c937ca2a805e8fb46fb6ac578260a758ba13b`.
Disposition: **CLOSED WITHOUT PROMOTION**. The fixed model abstains on all 153
candidates, including all seven confirmed targets. Production remains unchanged;
`FIELD FAIL`, O2 and A0Q remain open.

## Physical interpretation and frozen comparison

The user answered **“A:거품·기포가 섞인 유체 , B : 기포가 적은 액체”**.
The [reply receipt](../../50-diagnostics/s11/2026-10-07-sample4-region-context-preflight.json)
records the two displayed scenes f1275/f1320: A contains bubbly/foamy fluid and
B less-bubbly liquid. It does not provide exact masks, other-sector labels,
chemical species, scalar tolerances or a general brightness-to-identity rule.
That human checkpoint is closed.

The [contract](../../20-architecture/s11-interface-observability-witness-architecture.md#a2-temporal-region-exchange--design-preflight)
and offline source were committed before real model evaluation. Raw BGR spatial
arrangement and adjacent-frame change are compared jointly against stationary
step, illumination and finite-ribbon alternatives on common effective/nonglare
pixels. Neighbour cuts are unrestricted within the crop; current candidate
coordinates stay fixed. Native geometry takes precedence where recorded.
Both temporal pairs in every recorded sector must support the moving-partition
model; incomplete geometry, ties, hidden returns and alternative explanations
abstain. Image coefficients use a fixed pixel split, not supervised labels.

The adapter uses all 21 previously pinned frames and all 153 original candidates.
It never passes review labels, source families, authority or tracklets into the
readout. Raw feature/penalty context is retained with absent values still absent,
not recounted as independent evidence. Truth is loaded only after predictions.
The existing W3 evaluator consumes the original immutable target snapshot in
`EXPLORATORY_UNCALIBRATED` mode with no fit partitions. No scalar/local-path
truth is transferred. A +1 native-frame input is offline future context.

## Result and failure interpretation

| W3 regression result | Recorded-selection baseline | Frozen challenger |
|---|---:|---:|
| Supported confirmed targets | 4 / 7 | 0 / 7 |
| Supported reviewed wrong targets | 3 / 3 | 0 / 3 |
| Unresolved confirmed targets | 3 / 7 | 7 / 7 |
| Unresolved candidates, all roles | 146 / 153 | 153 / 153 |
| Supported unreviewed candidates | 0 / 143 | 0 / 143 |

All-abstention is **not** an accuracy improvement. The evaluator's internal
`non_interface` metric bucket here means explicitly reviewed non-target, retaining
the original physical uncertainty. No definite structure/noise label is inferred.

| Frame / candidate | Reviewed target role | Supported pair views / available |
|---|---|---:|
| f1140 / 9 | target | 9 / 10 |
| f1200 / 4 | target | 7 / 10 |
| f1260 / 4 | target | 6 / 10 |
| f1275 / 12 | target | 2 / 10 |
| f1320 / 9 | target | 3 / 10 |
| f1485 / 19 | target | 2 / 10 |
| f1560 / 20 | target | 3 / 10 |
| f1200 / 10 | wrong target | 0 / 8; four native sectors |
| f1260 / 15 | wrong target | 4 / 10 |
| f1320 / 21 | wrong target | 2 / 10 |

These are correlated view counts, not independent trials, confidence or a new
score. The f1260 wrong target has more supporting pairs than several confirmed
targets; f1320 true and wrong targets both support the central sector. Simply
lowering the required count cannot preserve all targets and reject these controls.
The four previously correct production observations would all lose support.

Across candidate-view references: 362 pairs support the partition hypothesis,
751 have a competing explanation, 258 cannot see both ribbon returns, 118 cannot
measure all competitors, and 13 have tied moving-step minima. There are 1,350
unique measurements after geometry caching; 1,502 references are not additional
independent data. All seven target candidates have complete five-sector geometry,
so missing native sectors alone do not explain the positive loss.

Close this particular shared-plane/step/ribbon model and operating point. Do not
rescue it with a sector count, polarity, family, selected seed or reviewed-Y rule.
This is not a rejection of temporal information or every region model. A future
proposal needs a distinct measurement that preserves the observed bubble/texture
arrangement and explains optical counter-controls; reordering these residuals or
transferring the reviewed orange path is insufficient. Independent acceptance and
scalar eligibility remain separate, and no new user review is requested here.

## Verification and preservation

**42 focused tests passed**: 17 new readout controls plus 25 existing region-fit
controls. They cover signed large displacements, both contrast polarities,
stationary/ribbon/exposure collisions, missing masks, numeric equivalence to full
least squares, input immutability, finite serialization, invalid inputs and
sector aggregation. The real adapter completed in about 33 seconds after a
system-Python import failure was resolved by using the existing `.venv` runtime;
that initial attempt did not run inference. No model parameter changed.

Source, original packet/snapshot/labels/mapping, input raster/mask and production
hashes were verified unchanged before/after the run. W3 reports all 153 rows,
zero missing predictions and no automatic acceptance. Focused governance and
whitespace/link checks accompany closeout. No production replay or Windows claim
is made for this offline addition.

The [compact receipt](2026-10-07-a2-region-exchange.json) preserves source/input
pins, all ten reviewed candidate summaries and baseline/W3 results. Full searched
loss curves, predictions, W3 report, original receipt and executable scripts
remain under `sample/output/s11-a2-region-exchange-20261007-001/`. These unique
artifacts and prior worktrees are retained; they are not disposable scratch.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: original confirmed targets lose selection eligibility at `OIL-AUTHORITY`; this offline model additionally loses every target before any production integration.
- Prior mechanisms reviewed: static region competition, gray temporal residuals, ordered-patch correspondence and the closed seed/direction controls.
- Difference from prior failures: compares shared-pixel temporal image-formation alternatives at original candidates, but target discrimination still fails; no appearance minimum is promoted as identity.
- Preserved contracts: generic candidate geometry, exact same-frame provenance, missingness, independent Oil/Foam, separate scalar and Windows acceptance.
- Logic-map impact: NONE — no production imports, control flow, authority or publication changes.
- Failure-registry impact: NONE — existing appearance/motion identity ambiguity is illustrated; no new cause or accepted repair is claimed.
