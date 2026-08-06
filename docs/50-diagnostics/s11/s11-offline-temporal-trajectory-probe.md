# S11 Offline Temporal Trajectory Probe

## Status and authority

This document records the Lane B diagnostic evidence for the S11 offline temporal trajectory question.
It is not production trajectory approval, detector/general-field accuracy approval, S11 completion, or audit approval.

Starting production authority for the probe is:

- repository: `teeeeooo/oil_level_tracker`
- accepted base: `4bb52a2718d176874c59a97b9164453165a90c00`
- current production Oil layer: P0/D4/P2/Spatial single-frame observation plus the accepted serialized S5-B temporal/reducer/projection ownership

The probe does **not** modify `src/`, `TrackingSample`, `AnalysisResult`, CSV/result persistence, Result Review, graph rendering, detector history, or the canonical reducer/projection contract.

Directly inspected owners were:

- `OpenCvPhaseDetector`
- `TemporalTracker`
- `TrackingSample` / `AnalysisResult`
- `tracking_sample_from_detection`
- `CsvExporter` / `ResultBundleReader`
- `ReviewTrackingSample` / `ReviewQueryModel`
- `GraphRenderer`

## Selected estimator and provenance

The selected diagnostic is deliberately the simplest bounded reconstruction that can answer the current question: **single-slot bounded linear bracketing**.

For a target without same-frame accepted Oil, it may publish `estimated` only when:

1. one accepted raw Oil anchor exists on each side,
2. the same target frame is excluded from those anchors,
3. total anchor span is at most `1.0 s` at the `2 Hz` probe cadence,
4. the two anchors differ by no more than the existing Glass `temporal_max_jump_px`,
5. no FULL/EMPTY no-interface state lies at the target or inside the support interval, and
6. no `FOGGED_OR_GLARE` / `DETECTION_LOST` blocker lies at the target or inside support.

The provenance meanings are intentionally separate:

- `observed`: production supplied an accepted numeric raw Oil observation.
- `estimated`: production supplied no usable same-frame Oil to the estimator and the bounded two-sided support rule reconstructed one derived value.
- `unavailable`: evidence did not meet those rules and the estimator abstained.

Ambiguous observations are never numeric support by themselves. Repeated ambiguity is not positive evidence. FULL/EMPTY no-interface is censored state information only and is never converted into an exact Oil Y.

The estimator consumes only immutable diagnostic observation records. It has no detector/tracker argument, writes no production sample, retains no image or temporal state, and cannot feed an estimate back into detector, reducer, `TemporalTracker`, or another estimate.

## Reproducible protocol

Authority is the checked-in `sample/` four-video corpus, frozen `.oilrecipe` files, and existing `.oiltruth` annotations. No private field video and no newly invented dense truth is used.

Two production views are kept distinct:

1. **Truth-anchor baseline**: each of the 13 usable truth frames is passed through the current production `OpenCvPhaseDetector`, matching the existing S11 production truth-frame baseline.
2. **Trajectory input stream**: the current serialized detector path is replayed at `2 Hz`, including production static-artifact learning, over the bounded Recipe qualification windows.

The trajectory input stream contains 299 scheduled detections. The held-out evaluation never injects truth Y into that stream. When a truth frame is already a scheduled production row, every row with that same frame index is excluded as estimator support.

| video | stream samples | observed raw Oil | missing raw Oil | max consecutive missing |
|---|---:|---:|---:|---:|
| `base_sample_1` | 30 | 2 | 28 | 22 |
| `sample2` | 5 | 2 | 3 | 2 |
| `sample3` | 151 | 22 | 129 | 77 |
| `sample4` | 113 | 110 | 3 | 1 |
| **total** | **299** | **136** | **163** | — |

This stream density is not an accuracy score. In particular, sample4 has dense accepted observations but also contains stable wrong-boundary runs.

The direct production truth-anchor baseline remains:

- usable truth denominator: `13`
- normally observed: `9`
- normally missing: `4`
- observed-anchor MAE: `4.888889 px`
- observed-anchor median error: `6.0 px`
- observed-anchor worst error: `11.0 px`

## Held-out reconstruction result

Across all 13 usable truth anchors:

- held-out `estimated`: `3`
- `unavailable` / abstained: `10`
- recoverable coverage: `23.08%`
- abstention rate: `76.92%`
- estimated reconstruction MAE: `14.333333 px`
- estimated median error: `19.5 px`
- material worst error: `20.5 px` at `sample4:900`
- normally missing production anchors recovered: **`0 / 4`**

| case | production | held-out result | support / reason | estimate error |
|---|---|---|---|---:|
| `base_sample_1:144` | observed `395` | unavailable | no right observed anchor | — |
| `base_sample_1:156` | unavailable | unavailable | no right observed anchor | — |
| `base_sample_1:240` | unavailable | unavailable | no right observed anchor | — |
| `sample2:0` | unavailable | unavailable | no left observed anchor | — |
| `sample2:30` | observed `599` | unavailable | no left observed anchor after hold-out | — |
| `sample2:60` | observed `598` | unavailable | no right observed anchor after hold-out | — |
| `sample3:900` | unavailable | unavailable | no left observed anchor | — |
| `sample3:1035` | observed `245` | unavailable | `33.033@272` → `43.043@222.5`, `10.01 s` unsupported gap | — |
| `sample4:0` | observed `861` | unavailable | no left observed anchor | — |
| `sample4:450` | observed `853` | estimated `849.5` | `14.5@849` → `15.5@850` | `3.0` |
| `sample4:900` | observed `848` | estimated `869.0` | `29.5@869` → `30.5@869` | `20.5` |
| `sample4:1470` | observed `866` | estimated `874.5` | `48.5@883` → `49.5@866` | `19.5` |
| `sample4:1680` | observed `866` | unavailable | no right observed anchor | — |

## Material interpretation

The current difficult production misses are `base_sample_1:156`, `base_sample_1:240`, `sample2:0`, and `sample3:900`. None gains sufficient two-sided support, so this estimator recovers **zero residual detector misses**.

The strongest negative evidence is `sample4:900`. Its held-out immediate anchors are both accepted at `869 px`, so temporal continuity looks exceptionally strong, yet the existing truth is `848.5 px`. A trajectory model that only rewards continuity would therefore reinforce a persistent wrong boundary and produce a `20.5 px` error.

`sample4:1470` supplies the second material failure: bounded bracketing produces `874.5 px` against truth `855 px`. Dense observations therefore do not imply trustworthy physical trajectory when the observation owner can remain on a wrong structural path.

The estimator creates no continuity across unsupported long gaps. `sample3:1035` has two numeric anchors but their `10.01 s` span exceeds the `1.0 s` bound, so the result remains unavailable.

The natural four-video stream contains no FULL/EMPTY no-interface rows in the selected qualification windows. The diagnostic contract is nevertheless locked by development tests: no-interface at the target or inside support is censored and forces abstention; it is never an exact Oil measurement. Synthetic tests also lock abstention for occlusion/detection-loss blockers, repeated ambiguity across a long gap, and contradictory anchor jumps.

## Resource and feedback boundary

- decoded production-stream observations: `299`
- maximum single-video stream scanned for one held-out query: `151` rows
- numeric anchors retained in an estimate: exactly `2`
- estimator-owned temporal state: `0`
- retained images: `0`
- detector/tracker feedback calls: `0`
- first full corpus probe runtime on the current local environment: `113.96 s` (informational, not fingerprinted)

## Conclusion and next contract boundary

**Conclusion: `insufficient trajectory evidence`.**

The bounded estimator demonstrates that offline look-ahead can fill a few isolated points, but it does not recover any current residual production miss and it materially amplifies wrong accepted anchors in two of the three reconstructed truth cases. The evidence therefore does not justify production result-layer integration from this probe.

If a later gate nevertheless elects to expose an estimated trajectory, that is a new derived result responsibility rather than a detector observation. The Orchestrator must explicitly decide where `observed / estimated / unavailable` provenance lives and reassess the Lane before any mutation to `TrackingSample`, CSV/result persistence, HTML/Review, or `GraphRenderer`. None of those contracts is changed here.

Reproducible machine evidence is checked in at:

- `docs/50-diagnostics/s11/s11-offline-temporal-trajectory-probe-manifest.json`
- fingerprint: `8b6a7790bf008e7679f63e4ff6bc5d164f9cc5574099bfbe16456cc6c1bf3d6a`

## Validation boundary

Development checks cover same-frame hold-out exclusion, censored no-interface, occlusion/detection-loss, unsupported long gaps, repeated ambiguity, contradictory anchors, and deterministic corpus evidence.

The final Worker validation is intentionally limited to one relevant targeted suite plus `git diff --check`. Full canonical/E2E, Windows packaging, private field-video validation, and the historical pre-P2 P2×Spatial stale assertion are outside this task's acceptance boundary.

Next gate: **Lane B Orchestrator exact-head bounded review**.
