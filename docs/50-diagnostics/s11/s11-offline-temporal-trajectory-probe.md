# S11 Offline Temporal Trajectory Probe

## Status and authority

This document records the Lane B diagnostic evidence for the S11 offline temporal trajectory question.
It is not production trajectory approval, detector/general-field accuracy approval, S11 completion, or audit approval.

Starting production authority for the probe is:

- repository: `teeeeooo/oil_level_tracker`
- estimator design base: `4bb52a2718d176874c59a97b9164453165a90c00`
- reconciled production-stream baseline: `745c6c923bb7e640ae0895f88c6bdf300198914a`
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

Manifest schema v2 preserves the original estimator design authority while identifying the
later accepted S11-R4 production stream used for this reconciliation. The original v1 probe
payload remains available in Git history; the figures below describe the reconciled stream and
must not be attributed to the earlier design-base detector output.

The trajectory input stream contains 299 scheduled detections. The held-out evaluation never injects truth Y into that stream. When a truth frame is already a scheduled production row, every row with that same frame index is excluded as estimator support.

| video | stream samples | observed raw Oil | missing raw Oil | max consecutive missing |
|---|---:|---:|---:|---:|
| `base_sample_1` | 30 | 2 | 28 | 19 |
| `sample2` | 5 | 2 | 3 | 2 |
| `sample3` | 151 | 21 | 130 | 97 |
| `sample4` | 113 | 64 | 49 | 8 |
| **total** | **299** | **89** | **210** | — |

This stream density is not an accuracy score. R3 removed sample3 full-state cap observations and false Foam authority; R4 preserves the same numeric Oil stream while changing Foam publication responsibility. The longer censored span is evidence correction rather than a coverage regression. Sample4 remains useful negative evidence for trajectory-only reconstruction because dense local continuity can still disagree with physical truth.

The direct production truth-anchor baseline remains:

- usable truth denominator: `13`
- normally observed: `8`
- normally missing: `5`
- observed-anchor MAE: `5.4375 px`
- observed-anchor median error: `6.5 px`
- observed-anchor worst error: `11.0 px`

## Held-out reconstruction result

Across all 13 usable truth anchors:

- held-out `estimated`: `3`
- `unavailable` / abstained: `10`
- recoverable coverage: `23.08%`
- abstention rate: `76.92%`
- estimated reconstruction MAE: `7.333333 px`
- estimated median error: `8.5 px`
- material worst error: `11.5 px` at `sample4:1470`
- normally missing production anchors recovered: **`0 / 5`**

| case | production | held-out result | support / reason | estimate error |
|---|---|---|---|---:|
| `base_sample_1:144` | observed `395` | unavailable | `3.5035@368` → `5.005@395`, `1.5015 s` unsupported gap | — |
| `base_sample_1:156` | unavailable | unavailable | no right observed anchor | — |
| `base_sample_1:240` | unavailable | unavailable | no right observed anchor | — |
| `sample2:0` | unavailable | unavailable | no left observed anchor | — |
| `sample2:30` | observed `599` | unavailable | no left observed anchor after hold-out | — |
| `sample2:60` | observed `598` | unavailable | no right observed anchor after hold-out | — |
| `sample3:900` | unavailable | unavailable | no left observed anchor | — |
| `sample3:1035` | observed `245` | unavailable | `33.033@294` → `35.035@240`, `2.002 s` unsupported gap | — |
| `sample4:0` | unavailable | unavailable | no left observed anchor | — |
| `sample4:450` | observed `853` | estimated `850.5` | `14.5@850` → `15.5@851` | `2.0` |
| `sample4:900` | observed `848` | estimated `840.0` | `29.5@838` → `30.5@842` | `8.5` |
| `sample4:1470` | observed `866` | estimated `866.5` | `48.5@867` → `49.5@866` | `11.5` |
| `sample4:1680` | observed `866` | unavailable | no right observed anchor | — |

## Material interpretation

The current difficult production misses are `base_sample_1:156`, `base_sample_1:240`, `sample2:0`, `sample3:900`, and `sample4:0`. None gains sufficient two-sided support, so this estimator recovers **zero residual detector misses**.

`sample4:900` remains negative evidence: its bounded held-out anchors yield `840 px` against the existing `848.5 px` truth. A trajectory model that only rewards local continuity can therefore still reinforce a wrong boundary and produce an `8.5 px` error.

`sample4:1470` is the material worst case: bounded bracketing produces `866.5 px` against truth `855 px`. Dense observations therefore do not imply trustworthy physical trajectory when the observation owner can remain on a wrong structural path.

The estimator creates no continuity across unsupported long gaps. `sample3:1035` has two numeric anchors but their `2.002 s` span exceeds the `1.0 s` bound, so the result remains unavailable.

The natural four-video stream contains no FULL/EMPTY no-interface rows in the selected qualification windows. The diagnostic contract is nevertheless locked by development tests: no-interface at the target or inside support is censored and forces abstention; it is never an exact Oil measurement. Synthetic tests also lock abstention for occlusion/detection-loss blockers, repeated ambiguity across a long gap, and contradictory anchor jumps.

## Resource and feedback boundary

- decoded production-stream observations: `299`
- maximum single-video stream scanned for one held-out query: `151` rows
- numeric anchors retained in an estimate: exactly `2`
- estimator-owned temporal state: `0`
- retained images: `0`
- detector/tracker feedback calls: `0`
- latest R4 manifest regeneration runtime on the current local environment: approximately `30.4 s` (informational, not fingerprinted)

## Conclusion and next contract boundary

**Conclusion: `insufficient trajectory evidence`.**

The bounded estimator demonstrates that offline look-ahead can fill a few isolated points, but it does not recover any current residual production miss and it materially amplifies wrong accepted anchors in two of the three reconstructed truth cases. The evidence therefore does not justify production result-layer integration from this probe.

If a later gate nevertheless elects to expose an estimated trajectory, that is a new derived result responsibility rather than a detector observation. The Orchestrator must explicitly decide where `observed / estimated / unavailable` provenance lives and reassess the Lane before any mutation to `TrackingSample`, CSV/result persistence, HTML/Review, or `GraphRenderer`. None of those contracts is changed here.

Reproducible machine evidence is checked in at:

- `docs/50-diagnostics/s11/s11-offline-temporal-trajectory-probe-manifest.json`
- fingerprint: `61a88c4d618219287443971ab606ea4c58494b09359ece93f78ea45c84a30237`

## Validation boundary

Development checks cover same-frame hold-out exclusion, censored no-interface, occlusion/detection-loss, unsupported long gaps, repeated ambiguity, contradictory anchors, and deterministic corpus evidence.

The R4 source-tree validation independently reruns this diagnostic inside the complete canonical suite. Windows packaging and private field-video validation remain outside this local diagnostic's authority.
