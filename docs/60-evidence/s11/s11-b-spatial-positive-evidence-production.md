# S11-B Spatial Positive-Evidence Production Fallback

> **Historical evidence record.** Status, audit and “next gate” wording below is contemporaneous provenance, not current project authority. See [`../../00-project/work-plan.md`](../../00-project/work-plan.md).


## Status

This document records the focused S11-B production implementation on top of exact main `1e83aac0643b0734fa1d67dfa30b88da6f3bd31e`. The change remains subject to fresh Lane C exact-head audit. It does not declare detector/general-field accuracy PASS or S11 completion.

## Production responsibility

The Spatial route is a secondary current-frame positive-evidence fallback inside the existing serialized S5-B `OilHypothesisPipeline` owner. The ordinary production raw observations, bounded proposals, semantic hypotheses and typed current observation run first, including the accepted S6-D4 routes and the merged P2 no-interface semantics. Spatial is considered only when that complete current-frame route returns `ShadowAmbiguousObservation`.

The fallback does not inject numeric Oil after the owner. If Spatial accepts, it returns a normal `SuccessfulPipelineFrame` whose selected evidence is still a typed `ShadowBoundaryObservation`. That frame passes through the existing Phase-A canonical evidence-graph validation, fixed serialized reducer, `AcceptedBoundaryOutcome` and one-way production projection. If Spatial cannot prove added information, the original ambiguity is retained. Existing no-interface and unavailable observations are not overridden.

## Candidate and cross-ROI evidence

The candidate stage reuses the diagnostic relative-phase idea without promoting scalar relative contrast into production authority. Existing non-`REGION_STEP` observations are retained. Only the broad region-step observation family is rebuilt with exposure-relative signed phase

`2 * (above - below) / (abs(above) + abs(below))`,

bounded to `[-1, 1]` and subject to the same availability, raw-observation, proposal, semantic-hypothesis, static-prior, glare/exclusion and canonical graph limits as the ordinary S5-B route. The current production P2 no-interface evaluator and accepted S5-A Foam context are reused; no separate P2×Spatial combined mechanism exists.

A relative candidate is still insufficient. Around the candidate, the current visible ROI is divided into five deterministic horizontal sectors after glare and any independently accepted current-frame Foam component are removed. Each sector independently searches at most `±12 px` around the candidate. At each row it compares robust outer-phase medians above and below the local gap and requires the phase difference to exceed both that sector's MAD noise and raster quantization. Production acceptance requires:

- at least three consecutive sectors with the same strong phase direction;
- a path median within the existing `12 px` narrow search radius of the candidate;
- adjacent path jumps no larger than `2 ×` the existing `6 px` proposal diameter; and
- path-row span greater than `1 px`, used only as a conservative proof that the x-resolved sectors add information beyond the existing scalar/row evidence.

The last condition is **not** a physical rule that Oil must slope or curve. A valid flat or near-horizontal Oil surface may remain ambiguous under this fallback and can require a later separately authorized positive-evidence route. The implementation makes no claim that such a surface is invalid Oil.

## Exact-main baseline and focused production result

Before mutation, actual production `OpenCvPhaseDetector → OilHypothesisPipeline → reducer → projection` was rerun on all 13 usable native truth rows at exact main `1e83aac0643b0734fa1d67dfa30b88da6f3bd31e`:

- numeric Oil coverage: `7/13`;
- numeric Oil MAE: `31/7 = 4.428571 px`;
- existing numeric rows: `base_sample_1:144`, `sample3:1035`, `sample4:0`, `sample4:450`, `sample4:900`, `sample4:1470`, `sample4:1680`.

With the focused Spatial fallback enabled:

- numeric Oil coverage: `9/13`;
- numeric Oil MAE: `44/9 = 4.888889 px`;
- recovered `sample2:30`: `599 px` vs truth `592 px` (`7 px` error);
- recovered `sample2:60`: `598 px` vs truth `592 px` (`6 px` error);
- existing numeric anchor regressions: `0/7`;
- remaining native misses: `base_sample_1:156`, `base_sample_1:240`, `sample2:0`, `sample3:900`.

The two recovered rows reproduce the S11-A diagnostic result inside the actual production owner. Their accepted x-resolved local path rows are respectively `(277, 273, 267)` and `(283, 279, 272)` across the first three sectors.

## Protection evidence

Production-focused tests independently rerun the retained safety sets through `OpenCvPhaseDetector`:

- observational-equivalence Oil/glare collisions: scalar relative phase is numeric on `14/16`, while production Spatial publishes numeric Oil on `0/16`;
- historical glare negatives: numeric Oil `0/21`;
- structural/Foam stress frames: numeric Oil `0/9`, with S5-A Foam still published on `9/9`;
- known P2 false-no-interface semantic-rescue transforms remain ambiguous and non-numeric;
- the `sample4:450` brightness `0.60` and `0.45` known false-boundary warning remains non-numeric because the candidate lacks the symmetric spatial window.

The native fallback performs no temporal retention. Its path search is statically bounded to five sectors times at most 25 candidate rows, or 125 sector-row evaluations for one fallback candidate. It adds no dependency, persisted detector setting, Recipe field, truth/result/CSV/debug public schema, optical flow, retained raster history or post-owner reconstruction.

## Scope boundary and next gate

This change is only a conservative single-frame positive-evidence production fallback. It does not redesign P2, estimate offline temporal trajectories, interpolate result graphs, add ML/segmentation, change S5-A Foam authority, or use private company field video as tuning truth.

The next gate is **fresh Lane C Independent Auditor exact-head review**. Only an Auditor may declare `AUDIT: PASS`, mark the Draft PR Ready, perform a native guarded merge, synchronize main and record bounded Close evidence.
