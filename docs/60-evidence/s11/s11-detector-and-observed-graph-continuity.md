# S11 Detector and Observed-Graph Continuity Repair Evidence

Date: 2026-08-08

Comparison base: `0ce1419` (`main` before this repair)

Status: source implementation and macOS/local-corpus validation complete; final Windows field-workflow validation not run

## Objective

Improve the usefulness of real-video analysis without converting ambiguity into invented detector truth. The concrete product outcome is:

- preserve real current-frame Oil evidence through bounded temporal reacquisition when it follows the same motion already allowed for ordinary continuity;
- reject a narrow class of weak structural-tail false positives without lowering global thresholds;
- display stored observed Oil anchors as one readable trend line while preserving every missing sample and state/review indication.

This repair does not claim 100% detector accuracy or general-field accuracy PASS.

## Reproduced defects

### Pending-only motion seam

The serialized reducer already allowed a real accepted boundary to move within `4 × maximum_proposal_diameter_px` (`24 px` with the current bound), but pending-path compatibility used only `2 ×` (`12 px`). In sample3, the sequence `245 px real boundary → 240 px compatible ambiguity → 258 px real boundary` therefore restarted reacquisition at the final step even though the `13 px` real-boundary movement was inside ordinary continuity.

### Comparative structural-tail borrowing

Three controlled paired-pulse perturbations could select a low-boundary-likelihood tail around source Y `129` because independent texture around the stronger neighboring structure was effectively available to the weaker candidate while the neighbor's artifact opposition stayed with the neighbor. Exact base `0ce1419` reproduced all three failures: `brightness-+4`, `contrast-1.08` and `noise-211`.

### Broken Oil graph

The result model correctly retained missing values as `None`, but both Result Review and static report rendering converted each missing Oil value into Matplotlib `NaN`. Matplotlib consequently split one observed trajectory into disconnected segments and points, making the overall sight-glass movement difficult to read.

## Accepted design

### Detector

1. One `_boundary_motion_envelope()` now owns the existing bounded per-observation Oil motion limit for ordinary accepted continuity, real-boundary pending consistency and ambiguity compatibility.
2. Compatible ambiguity still preserves pending state only. It does not increment confirmation, update pending motion or publish numeric Oil. A second compatible real boundary remains mandatory.
3. Outside authoritative accepted-Foam context, D3 keeps the existing ordinary `0.48` boundary floor. Only a selected candidate below that floor is rejected as a borrowed structural tail, and only when a local neighbor has at least as much boundary likelihood, greater artifact likelihood and at least twice the direct narrow response. The check cannot promote the neighbor; accepted-Foam scenes retain D5 residual/topology ownership.
4. Hard no-interface, visibility, glare/exclusion/border, structure and authoritative-Foam safety remain unchanged.

### Graph

1. Stored finite Oil values are filtered into timestamp-ordered vertices and drawn as one presentation polyline.
2. No missing timestamp receives a numeric TrackingSample, CSV value, cursor/overlay value or detector-history value.
3. `UNKNOWN_REVIEW` and no-interface bands remain visible across connected anchors, exposing the evidence status behind the visual trend.
4. An all-missing Oil series stays empty. Foam remains gap-preserving because Foam absence is meaningful.
5. Retrospective FULL/EMPTY cannot add an Oil vertex. This graph-only connection does not activate trajectory-estimation authority.

## Implementation ownership

- `oil_shadow_observations.py`: bounded D3 structural-neighborhood integrity check.
- `oil_shadow_pipeline.py`: shared Oil motion envelope and compatible pending-path recovery.
- `application/services/graph_series.py`: pure finite observed-anchor selection.
- `result_review_graph.py`: interactive Oil polyline; Foam keeps gaps.
- `graph_renderer.py`: static combined/detail Oil polyline; Foam keeps gaps.

## Real-video comparison

The checked local `sample3.mp4` and tracked `sample3.oilrecipe` were replayed through the official `AnalysisPipeline` over `0.0–140.073266667 s` at `2.0 Hz`, including official static-artifact preparation. Base and repair used the same input, Recipe and schedule.

| Measure | Base `0ce1419` | Repair | Delta |
| --- | ---: | ---: | ---: |
| scheduled rows | 281 | 281 | 0 |
| rows with numeric raw Oil | 62 | 64 | +2 |
| base numeric anchors retained | 62/62 | 62/62 | 0 lost |
| `is_valid` rows | 73 | 69 | -4 |
| `UNKNOWN_REVIEW` | 199 | 204 | +5 |
| `FULL_WITH_FOAM` | 37 | 32 | -5 |

New numeric publications are frame `1064 → 258 px` and frame `1094 → 244 px`. The existing curved/diagonal-boundary anchor at frame `2607 → 296 px` remains retained. The new points remain review-gated by existing downstream state/confidence semantics; this slice does not inflate confidence or optimize `is_valid` coverage. The shift from `FULL_WITH_FOAM` to `UNKNOWN_REVIEW` around the recovered temporal path is therefore recorded explicitly rather than presented as a coverage gain. Windows field review must assess the combined line and state-band presentation.

## Graph visual check

The repaired sample3 detail graph was rendered at `12 × 5.5 in`, `140 dpi` from the same 281-row result and inspected directly:

- Oil appears as one connected blue line from the first through the last finite observed anchor;
- long and short evidence gaps remain visible through hatched `UNKNOWN_REVIEW` and state bands;
- the orange Foam series remains broken where Foam is absent;
- no line is drawn before the first or after the last Oil anchor;
- zero and analysis-boundary lines remain unchanged.

Generated review images are temporary validation artifacts and are not tracked as golden files.

## Automated evidence

Focused and expanded results on the repair source:

- graph, Result Review, static-renderer, reporting integration and temporal regressions: `63 passed`;
- current detector preservation bundle spanning production cutover, typed evidence, single-frame observability, Spatial, controlled benchmark, margin regression and sample3 temporal continuity: `419 passed`;
- structural-tail controls plus preserved historical Spatial anchors: the three paired-pulse perturbations and both Spatial aggregate assertions pass;
- full sample3 official replay: `281` rows, `64` numeric Oil anchors, no loss among the base `62` anchors.

The complete local canonical suite collected `1,436` tests and finished `1,426 passed, 10 failed` in `98.12 s`. A detached exact-base `0ce1419` comparison reproduced all ten failures in the same files/assertions: one stale inline-readiness assertion, seven historical S11 diagnostic aggregate/transition expectations activated by the ignored local MP4 corpus, one legacy fill-state assertion and one legacy Foam assertion. They are outside the changed graph/temporal owners and are not relabeled as PASS. Exact base also failed the three paired-pulse controls fixed by this repair; those controls pass on the repair source.

No new canonical failure remains relative to exact base. The focused `63` and detector `419` changed-owner suites are green.

## Claim boundary and next gate

This evidence accepts the bounded source behavior on the local/macOS validation environment only. It does not claim Windows execution, packaged-app behavior, category-balanced detector accuracy or safe numeric interpolation between anchors. The remaining S11 gate is the final Windows field-workflow checklist, including connected Oil anchors, visible state bands, missing overlay values, Foam gaps and sustained graph layout.
