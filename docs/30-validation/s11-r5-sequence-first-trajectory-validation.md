# S11-R5 Sequence-First Observation Validation Contract

**Status:** `LOCAL_ACCEPTED — SECURE WINDOWS REQUIRED`

## Scope and oracle

This contract validates the [R5 sequence-first architecture](../20-architecture/s11-r5-sequence-first-trajectory-architecture.md). The physical oracle is direct review of the source MP4 inside the configured Glass ROI, supported by checked-in `.oiltruth` and blind provisional annotations. Legacy output fingerprints, aggregate numeric publication and synthetic fixtures are regression evidence, not substitutes for visual truth.

The secure Windows Base/Accum video is unavailable in this checkout. Local acceptance can qualify the mechanism but cannot claim that private field failure is closed.

## Gate 0 — representation sufficiency

Before tuning a path, audit the candidate lattice on visually clear intervals. Record whether at least one hard-safe Oil hypothesis lies in the visually supportable range.

- sample3: empty/inflow/Foam/full transition around `28–40 s`, plus later visible drain material around `85–105 s`;
- sample2: the entire short clip, including the retained stationary real interface;
- sample4: visible movement and genuine Foam intervals; and
- Base sample1: only visually interpretable intervals; built-in overlay/unclear frames are censored.

If most visually clear misses contain no usable hypothesis, stop the resolver implementation and repair proposal representation. A path optimizer cannot create missing visual evidence.

## Gate 1 — deterministic lattice mechanics

Unit tests must prove:

1. a continuous medium-strength material path beats disconnected stronger artifacts;
2. a stationary material-supported real path is retained;
3. a recurring fixed row is opposed only under the conjunctive artifact signature;
4. FULL exposes a boundary only near the top and EMPTY only near the bottom;
5. confirmed FULL/EMPTY persists through ambiguity without producing a number;
6. a compatible edge transition releases the prior into a visible trajectory;
7. hard unavailable/glare frames remain UNKNOWN and contain no carried coordinate;
8. a frame with no Oil candidate cannot receive an interpolated coordinate;
9. tie-breaking and repeated runs are deterministic; and
10. multi-Glass/reset state does not leak.

## Gate 2 — Foam episode mechanics

Prove:

1. constant high-score/static-overlap Foam-like appearance is rejected as an episode;
2. a single strong bubble/component does not start Foam;
3. a sustained coherent layer with spatial evolution/turnover is retained;
4. a bounded one-sample dropout does not fragment an otherwise supported episode, while a longer unsupported span ends it;
5. Foam cannot change a resolved FULL/EMPTY/Oil path by itself;
6. Foam plus visible Oil composes to `FOAMING_VISIBLE`, and Foam plus resolved FULL composes to `FULL_WITH_FOAM`;
7. Foam-only UNKNOWN remains UNKNOWN; and
8. reset and Glass identity isolate adjacent-mask state.

## Gate 3 — analysis integration and provenance

Run the production `AnalysisPipeline` with both an R5-capable detector and a legacy/fake detector. Verify:

- all detections for one Glass are resolved before `TrackingSample`, retrospective, events and judgment are finalized;
- output coordinates are members of that frame's Oil candidate set;
- sequence-selected points carry `SEQUENCE_RESOLVED_OIL`;
- resolved FULL/EMPTY carries state provenance and no coordinate;
- UNKNOWN stays invalid;
- explicit confirmation is passed only for the matching current run;
- R5 leading states are not retrospectively rewritten a second time;
- resolver version/mode is recorded in the manifest; and
- resolver failure aborts instead of silently emitting the legacy stream.

## Gate 4 — real-video visual effectiveness

Generate side-by-side current-baseline and R5 replays, graphs and source-coordinate overlays for all four local videos. Review the images, not only counters.

Primary measures are:

- visible-interval candidate/trajectory coverage;
- gross wrong-interface duration;
- state-interval agreement (`FULL`, `EMPTY`, visible boundary, UNKNOWN);
- direction agreement (rise/hold/fall);
- highest/lowest coordinate plausibility and event timing;
- Foam episode precision/recall; and
- Oil error on visually supportable checked-in truth anchors.

Acceptance requires a materially more understandable sample3 inflow-to-full narrative and no new long fixed-artifact trajectory. The sample2 stationary interface and genuine sample3/sample4 Foam must remain. Base sample1 overlays and visually unclear/no-interface intervals may remain unavailable and must not be forced numeric.

No `50%` aggregate publication target is imposed. Improvement means greater agreement with the visible physical history, not more numbers.

## Gate 5 — negative and compatibility protection

Run the complete repository suite plus focused glare, exclusion, border, structure, no-interface, Foam, serialized-owner, initial-state, report and redetection tests. Existing exact fingerprints may change where they encode the superseded final-analysis owner; every delta must be reconciled by source imagery and candidate provenance.

No accepted controlled negative may become numeric merely because a smooth path is available. No report bridge may appear in CSV, overlay, events, judgment or detector feedback.

## Secure-Windows acceptance

On the same private Base/Accum bundle, record at minimum:

- resolved FULL/EMPTY/visible/UNKNOWN intervals and numeric trajectory coverage;
- selected source Y overlaid on the Glass for every event and representative transition;
- recurring-artifact track diagnostics for the fixed lower Base edge;
- raw versus confirmed Foam episodes, static overlap and temporal turnover;
- initial-state release/contradiction reason;
- visual versus detected rise/drop/high/low/Foam timestamps; and
- report captures and graph continuity.

Expected direction:

- Base remains FULL until an upper boundary visibly enters, then follows the real descent/recovery rather than the fixed lower Foam/artifact row;
- Base emits no Foam episode when visual review shows none;
- Accum remains EMPTY until a lower boundary enters, follows rise/high/fall, and retains only the visually confirmed turbulent Foam interval; and
- a missing observation remains UNKNOWN rather than becoming a fabricated line.

The conflicting prior notes that place Accum Foam onset near both `492 s` and `672 s` must be resolved by direct source review before computing precision/latency. R5 must not be tuned to either timestamp blindly.

## Stop boundary

Stop or narrow implementation if representation Gate 0 fails, if R5 extends a wrong artifact more continuously than R4, if it removes a retained real interface/Foam episode, if it requires video identity or truth at runtime, or if improvements exist only in aggregate coverage without better source-image agreement.

## Local disposition

Gates 0–5 are locally accepted by the [R5 implementation and replay evidence](../60-evidence/s11/s11-r5-sequence-first-observation.md). The acceptance is deliberately limited:

- the four checked-in videos, matching Recipes, blind annotations and user-truth files were replayed through the production pipeline;
- every numeric R5 point retains same-frame candidate provenance;
- direct graph/capture review rejected unsafe high-coverage and over-smoothed variants before accepting the bounded resolver;
- controlled unit and complete repository regression suites pass; and
- known sample3 first/late candidate-selection errors remain recorded rather than hidden by interpolation.

The secure-Windows acceptance section remains open and is the S11 closure gate. Local acceptance does not claim that the private Base/Accum failure has passed.
