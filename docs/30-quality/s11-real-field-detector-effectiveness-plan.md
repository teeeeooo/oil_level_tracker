# S11 Real-Field Detector Effectiveness Recovery

## Authority and status

This document owns the S11 real-field detector diagnosis, evidence plan and acceptance boundaries. Milestone state and current next action remain owned by the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md). The agreed S11-A reproducible-corpus and detector-direction decision is recorded in [S11-A Detector Direction and Experiment Plan](s11-a-detector-direction-and-experiment-plan.md). The completed forensic diagnostic contract is [S11-C Full-Video Production Replay and Visual Forensic Attribution](s11-c-full-video-production-replay-visual-forensic-diagnostic.md). The accepted D1 repair record is [S11-D1 Foam Structural/Refractive Discrimination and Oil Context Safety](s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md). The accepted D2 Class-A repair record and remaining Class-B split are [S11-D2 Sample3 Positive-Evidence Recovery](s11-d2-sample3-positive-evidence-recovery.md). The active Class-B source gate is [S11-D2 Class-B Observation/Proposal Representation Recovery](s11-d2-class-b-observation-proposal-representation.md).

**Status:** `ACTIVE — S11-D1 and D2 Class-A accepted; S11-D2 Class-B representation recovery next`

S11 starts after the accepted S10 Windows/package gate. The immediate product risk is detector effectiveness on field-representative sight-glass video, not packaging or UI-platform viability.

## Objective

Recover reliable Oil-boundary detection and tracking when usable real-field evidence exists, while preserving accepted S5-A Foam behavior, S5-B fail-closed ambiguity semantics, glare/structure protection, no-interface safety, persisted/public schemas and bounded resource ownership unless a separately authorized architecture change is proven necessary.

S11 does not begin by lowering thresholds. First establish where usable evidence is lost between preprocessing, proposal/hypothesis construction, canonical decision and temporal action.

## Initial Windows field diagnostic

Private/local video characteristics reported by the user:

- 1280×720, 30 fps, duration 3567 s;
- analyzed interval 480–1200 s;
- Base and Accum Glasses use identical detector settings;
- Base recipe: center `(265.7, 431.0)`, radius `(131.0, 129.8)`, zero-line Y `423.7`, initial state `PARTIAL_VISIBLE`;
- Accum recipe: center `(996.7, 404.1)`, radius `(110.2, 110.2)`, zero-line Y `325.7`, initial state `EMPTY_NO_INTERFACE`.

### Aggregate behavior

- Base: 0 Oil-Y detections across 1440 analyzed frames; dominant state `UNKNOWN_REVIEW`.
- Accum: 41 Oil-Y detections across 1441 analyzed frames, about 2.8%; dominant states `FULL_NO_INTERFACE` / `EMPTY_NO_INTERFACE`.
- Lighting changes materially during the interval. Base becomes very dark around 700 s; Accum is clearly visible in some segments and occluded by a hand around 913 s.

User/LVLM visual review reported a clearly visible Base boundary around 480 s and 913 s. Accum also showed a visible boundary in at least the 480 s review, but the narrative used both `full` and `partially filled` wording. These field descriptions remain diagnostic observations only and are not an S11 user-truth or repeatable development corpus.

Source inspection resolved the coordinate convention. Detector `projected_source_y` is source-frame Y (`roi_local_y + crop_origin_y`), and product `.oiltruth` also owns `source_frame_y` as the authoritative coordinate with ROI-local and zero-line values derived from it. Any future copied field Y note must therefore be interpreted only after confirming the original source-frame convention.

## Load-bearing debug observations

### Base frame 14400 / 480 s

Reported visual condition: very clear Oil boundary.

- `oil_boundary_score = 0.232`
- `oil_artifact_score = 0.279`
- `oil_ambiguity_score = 0.583`
- `oil_no_interface_score = 0.558`
- `oil_decision_confidence = 0.412`
- `oil_decision_margin = 0.276`
- decision: `ambiguous`
- reason: `competing_boundary_artifact_or_no_interface_evidence`
- `tracker_action = NO_UPDATE`
- `raw_oil_y = null`
- `projected_source_y = 415.0` versus zero-line Y `423.7`
- eight hypotheses were generated but none selected.
Canny/edge review reportedly shows a strong horizontal cluster at the visual Oil boundary and normal masking. The diagnostic contradiction is therefore not simply “no candidate exists”: a plausible boundary location is present, yet canonical acceptance loses to ambiguity/no-interface competition and temporal state receives no update.

### Accum frame 14400 / 480 s

Reported condition: dark Glass with a visually reported Oil boundary.

- `oil_boundary_score = 0.297`
- `oil_artifact_score = 0.0`
- `oil_ambiguity_score = 0.0`
- `oil_no_interface_score = 0.583`
- `oil_no_interface_uniformity = 0.792`
- `oil_no_interface_full_likelihood = 0.792`
- `oil_no_interface_weak_boundary = 0.408`
- decision: `no_interface_accepted`
- reason: `positive_uniform_full_or_empty_evidence`
- `raw_oil_y = null`

The working diagnosis is that darkness and low contrast can make the interior appear uniformly full/empty even when a usable boundary exists. The 41 accepted Accum detections occur only in lighting intervals where no-interface evidence drops; examples include 504.5 s, 505.5 s and 528.0 s.

## Provisional failure hypotheses

These are investigation hypotheses, not accepted root-cause claims:

1. Real horizontal boundary evidence may be underweighted after proposal construction even when edge geometry is plausible.
2. No-interface evidence may be overconfident under dark/low-dynamic-range illumination.
3. Ambiguity and no-interface competitors may jointly suppress an otherwise usable Base candidate before temporal tracking can accumulate positive motion/history evidence.
4. Current identical detector settings may not adequately model the markedly different photometric conditions of the two Glasses, but per-video/fixture tuning is not an acceptable repair by itself.
5. Initial state may influence downstream behavior and must be measured, but it must not be blamed without controlled evidence.

## S11-A required evidence

Before production detector mutation:

- retain the private Windows observations as diagnostic failure-class evidence only; repeated private-video extraction is not an S11 development dependency;
- use the repository-local four-video S6 corpus, frozen Recipes, `13` usable user-confirmed truth cases and existing structural/Foam/glare regressions as the reproducible authority;
- preserve the resolved source-frame Y convention when interpreting any copied field coordinate;
- use controlled brightness/gamma/contrast transformations of truth-positive local frames as metamorphic probes for exposure sensitivity without creating new truth labels;
- compare `P0` current behavior with `P1` relative/local photometric phase evidence, `P2` exposure-decoupled no-interface evidence and `P3` combined behavior before selecting production source repair;
- capture the path from preprocessing/edge evidence through proposals, semantic hypotheses, no-interface evidence, canonical outcome and temporal action for representative native and transformed cases;
- preserve dataset/video/settings identity for controlled base/feature comparison and retain S5-A/S5-B negative protection.

The detailed experiment and design decision is owned by [S11-A Detector Direction and Experiment Plan](s11-a-detector-direction-and-experiment-plan.md). The source task begins with a provisional Lane C assumption because the leading direction may change no-interface/positive-evidence semantics; it may narrow to Lane B only if the probe proves a materially smaller existing-owner defect with the S5-B contract unchanged.

## S11-B P2 no-interface production contract

The merged S11-B P2 repair applies the selected P2 diagnostic semantics inside the canonical S5-B current-frame no-interface owner. Absolute raw brightness may still describe whether an accepted no-interface scene looks more FULL-like or EMPTY-like, but that appearance no longer adds positive weight to interface absence. Positive no-interface likelihood remains a bounded fusion of weak-boundary evidence, normalized-frame spatial uniformity, current visibility, glare conflict and competing-boundary evidence.

Uniformity is evaluated from the existing CLAHE-normalized current frame, while `full_likelihood`, `empty_likelihood`, raw mean intensity and raw texture remain diagnostic/fill-state evidence. This preserves the existing FULL/EMPTY downstream distinction without using either appearance likelihood as a hidden absence-score channel. No new detector setting, schema, dependency, temporal history or numeric Oil recovery path is introduced.

Production integration also keeps global current-frame visibility in the adjacent single-frame identifiability reliability. The diagnostic P2 probe patched only no-interface evidence, so it did not expose this seam. Once the brightness-derived absence term was removed in production, a glare-threshold transition could otherwise reduce no-interface likelihood and accidentally create a small upward boundary-identifiability margin jump. Feeding the already-owned no-interface visibility into the existing reliability average preserves the prior glare/route-transition fail-closed contract without reintroducing absolute brightness as positive absence evidence.

When the exposure-decoupled evidence is insufficient, the current frame remains ambiguous and cannot publish raw or smoothed numeric Oil. Genuine canonical no-interface still enters the unchanged serialized S5-B absence-stability path, including bounded stale-Oil clearing after stable absence. S5-A Foam, D4 positive Oil recovery, observational-equivalence collision protection, canonical projection and legacy-fallback prohibition remain separate and unchanged.

The four S11-A metamorphic rescue anchors remain direct production acceptance evidence: `brightness 0.60 × sample3:900`, plus `brightness 0.45 × base_sample_1:144`, `sample3:900` and `sample3:1035`. Their required transition is false no-interface to fail-closed ambiguity, not numeric Oil recovery. The P2 repair is merged on the current baseline and does not establish detector/general-field accuracy PASS.

### P2 FULL/EMPTY preservation correction

Windows canonical validation exposed a preservation regression after the accepted P2 cutover: the two basic synthetic FULL/EMPTY cases and ten controlled noisy-uniform FULL/EMPTY cases no longer reached typed no-interface and instead failed closed as `UNKNOWN_REVIEW`. Direct current-main reproduction showed the normalized-raster uniformity and visibility evidence remained strong; the regression came from score scale contraction. P2 correctly removed the former `0.17 × FULL/EMPTY appearance` positive term but left the remaining positive coefficients summing to `0.83` while preserving the canonical `0.58` acceptance threshold and negative conflict penalties.

The bounded correction transfers the removed `0.17` positive weight to the already accepted exposure-decoupled normalized-raster uniformity channel, changing uniformity from `0.27` to `0.44` while leaving weak-boundary `0.36`, visibility `0.20`, the canonical threshold, and glare/competing-boundary penalties unchanged. This targets genuinely uniform absence evidence instead of globally lifting weak or merely visible frames. Absolute raw brightness, `full_likelihood` and `empty_likelihood` do not contribute to no-interface acceptance and remain downstream appearance evidence only. The correction therefore restores genuine FULL/EMPTY typed no-interface without numeric Oil while the four low-exposure rescue anchors must remain ambiguous/non-numeric. Collision, glare/structure, Foam, Spatial, serialized absence clearing and canonical projection remain preservation obligations.

The P2 FULL/EMPTY preservation correction passed fresh Lane C exact-head audit and is merged. S11 does not return directly to field re-validation: the separate local-corpus canonical portability blocker is repaired as Lane B first, Windows canonical is then rerun, and only after that gate is green does controlled Windows field re-validation resume. Milestone state and exact next action remain owned by the roadmap and work plan.

## S11 local-corpus canonical portability contract

S11's four MP4s remain ignored local supporting media; they are not packaging or repository-distributed
inputs. The checked-in S11-A evidence manifest owns their authoritative SHA-256 identities, while the
tracked Recipes and `.oiltruth` artifacts remain repository authority. Corpus-dependent diagnostic
and production-regression tests must validate all present required MP4 identities before decoding or
aggregating any rows. A wrong present identity is a hard corpus failure even if another required MP4
is absent. If identities of all present files are correct but one or more required MP4s are absent,
the corpus-dependent test reports `SKIPPED / NOT AVAILABLE`; corpus-independent S11 synthetic tests
continue normally and no partial 13-row aggregate is produced. Correct identity followed by decode
failure remains a test failure, not an availability skip.

Historical S11-A P0/P1/P2/P3 outputs retain their original diagnostic responsibility and are not
rewritten to match later production architecture. Since accepted Spatial fallback, current production
adds the cross-ROI recoveries `sample2:30=599` and `sample2:60=598` after the ordinary route remains
ambiguous. The historical probe therefore no longer asserts P0 equality with current production;
its frozen diagnostic aggregates remain self-owned, while the existing Spatial production fallback
tests remain authority for current `9/13` production coverage and those two recoveries. This bounded
portability repair changes no detector source, P2/Spatial semantics, truth meaning, schema, setting,
dependency, runtime behavior or MP4 redistribution policy.

## S11-B Spatial positive-evidence production contract

The focused Spatial feature is a separate P0/D4-first fallback inside the existing S5-B current-frame owner. It runs only after the complete ordinary route remains `ShadowAmbiguousObservation`; it does not override accepted no-interface/unavailable outcomes and does not couple recovery to P2. Exposure-relative broad phase can create a candidate, but scalar/row evidence cannot publish numeric Oil without a same-frame five-sector cross-ROI path proving additional x-resolved information against sector-local MAD and quantization noise.

The production non-degeneracy requirement `path span > 1 px` is a conservative proof of added spatial information, not a physical rule for Oil shape. Flat or near-horizontal Oil may remain ambiguous. Accepted fallback evidence is rebuilt into the normal canonical raw/proposal/hypothesis graph and a typed `ShadowBoundaryObservation`, then passes through unchanged Phase-A validation, the one serialized reducer, `AcceptedBoundaryOutcome` and production projection. No fallback state survives the command.

On exact main `1e83aac0643b0734fa1d67dfa30b88da6f3bd31e`, actual production native Oil was `7/13` at `4.428571 px` MAE. The focused feature reproduces the diagnostic Spatial recoveries `sample2:30=599` and `sample2:60=598`, producing `9/13` at `4.888889 px` MAE with zero changes to the prior seven numeric anchors. Focused production tests retain collision/glare/structure/Foam protection and the P2 low-exposure rescue/warning boundaries. Detailed feature evidence is recorded in [S11-B Spatial Positive-Evidence Production Fallback](s11-b-spatial-positive-evidence-production.md). The feature has passed its fresh Lane C exact-head audit and remains accepted production behavior.

## Post-portability evidence and S11-C direction

The portability gate is closed. Windows canonical re-validation on the current authoritative source tree completed with `1321 passed, 0 failed, 23 explicit skips`, no unexpected skip family, material warning, hang or crash. The `16` S11 corpus-dependent skips are the expected absent-local-MP4 behavior and the other `7` are Windows symlink privilege limitations.

Controlled field re-validation still demonstrates severe BASE failure after accepted P2/FULL-EMPTY/Spatial production changes. Across `1441` rows, fill state is `UNKNOWN_REVIEW` on every row, only `2` raw Oil boundaries are accepted, `1436` decisions are ambiguous and `10,730` candidates produce only `4` selected candidates. User/LVLM visual review reports a clear Oil boundary at multiple times. Mean field scores are boundary `0.278`, artifact `0.341`, ambiguity `0.530` and no-interface `0.421`. This strengthens the earlier diagnosis that proposals can exist while canonical positive-boundary evidence remains too weak relative to competing evidence.

The frozen 68-frame blind silver comparison provides a separate local visual reference. Current production publishes numeric Oil on `15/22` visible rows but only `7/22` are inside the frozen visual point/range; sample3 remains `0/6`, whereas sample4 is `15/16` numeric with eight out-of-range results. Foam also remains inconsistent with the frozen visual evidence, especially sample4. Silver/user-confirmed truth conflict on some sample2 rows means Spatial cannot be globally labeled false-positive from those rows. The combined evidence therefore supports multiple residual failure modes and does not justify a single global threshold repair.

The user additionally reports that fitting the Recipe ellipse to the low-transparency/whitish field glass already produces about `16%` confidence, a review-needed observation, an "Oil boundary not in frame" interpretation despite a visually central boundary, and a "Foam possible" interpretation despite no visible Foam. S11-C treats this as a focused optical-domain hypothesis: the same glass appearance may create Foam-like support and Oil artifact/ambiguity pressure, but accepted Foam must be distinguished from merely rejected/ambiguous Foam-like evidence before assigning causality.

S11-C now replays the four local videos through the full production stream, including temporal Foam gating and serialized Oil/tracker ownership, then performs bounded direct visual/candidate forensics on representative frames. Generated bundles/debug images remain under the existing ignored `sample/output/` hierarchy and are temporary evidence only. The diagnostic should determine whether the dominant local/field failure arises from proposal construction, true-candidate scoring/ranking, artifact/ambiguity competition, Foam/Oil separation, Spatial selection or canonical identifiability. Detailed scope and regression rules are owned by the S11-C document.

A later repair should promote only the smallest reproducible frames/windows and compact expectations into regression tests; full generated bundles are not tracked as golden artifacts. S12 remains separate until S11 reaches a stable accepted detector baseline.

## S11-C completed attribution and accepted S11-D1 repair

S11-C full production-stream replay met its exit criterion. It reproduced the Windows ambiguity/NO_UPDATE class locally and proved that residual failure is multi-modal rather than a single score-threshold defect. sample3 includes both a correct-Y candidate that remains non-identifiable and a visually clear boundary for which no material candidate is generated. Spatial remains necessary for user-confirmed sample2 Oil recovery but also promotes suspicious full-like sample3 structures.

S11-D1 repaired the first shared-responsibility defect rather than globally retuning Oil/Foam thresholds. Accepted S5-A Foam remains published and continues through its existing temporal/fill-state path, while a stateless handoff policy withholds only the wide, hollow structural/refractive component class from S5-B Oil masking/routing authority.

Fresh exact-head Lane C audit accepted that boundary. Four-video production replay preserved every base/sample2/sample3 Oil/Foam/fill-state signature and retained sample2 `30 → 599` and `60 → 598`. On sample4, Foam remained `113/113`, Oil changed from the preserved S11-C baseline `110/113` to `0/113`, authority was withheld `113/113`, and no alternate numeric Oil route appeared. S11-D2 then accepted only the Class-A candidate-present/non-identifiable repair: current-frame Spatial corroboration recovers sample3 `899 → 320` and frozen `900 → 319`, but the unchanged serialized temporal owner keeps full-stream sample3 Oil at `42/281` and leaves five D2 rows `reacquisition_pending/NO_UPDATE`. The repaired D2 Foam-front gate was independently adversarially verified with a non-empty bottom-connected accepted-Foam mask, while sample4 remains Oil `0/113` / Foam `113/113`. The next source gate is the separate sample3 Class-B observation/proposal representation defect. The ignored S11-C forensic bundle remains temporary non-Git evidence and is not a golden fixture.

## Repair acceptance boundary

A later repair must improve field-representative truth coverage without creating a case-specific exception. Acceptance must retain:

- S5-A Foam/shimmer non-regression;
- S5-B latent-truth versus observable-outcome separation and fail-closed behavior for genuinely unidentifiable collisions;
- structural/rim/glare negatives and no-interface truth cases;
- no fixture/video/file-name branching or one-video threshold tuning;
- existing public/persisted result, Recipe, truth and benchmark contracts unless separately authorized;
- bounded CPU/memory/resource behavior.

The preferred direction is additional positive evidence when available, not indiscriminate rejection weakening. Temporal photometric/component evidence is a candidate architecture direction only if S11-A proves single-frame evidence is usable but repeatedly discarded; it is not preselected implementation.

## Claim boundary and successor

This initial Windows review is diagnostic evidence only. It does not establish detector accuracy PASS/FAIL, exact Oil truth, category-balanced coverage, or a production root cause. The private source video remains outside the repository.

S12 Post-S10 UI/UX Refinement is a separate P1 successor. It must not be mixed into S11 detector repair. Autosave/abnormal-exit recovery remains deferred unless explicitly reclassified.
