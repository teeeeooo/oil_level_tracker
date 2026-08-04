# S11 Real-Field Detector Effectiveness Recovery

## Authority and status

This document owns the S11 real-field detector diagnosis, evidence plan and acceptance boundaries. Milestone state and current next action remain owned by the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md).

**Status:** `ACTIVE — S11-A diagnosis/truth planning`

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

User/LVLM visual review reported a clearly visible Base boundary around 480 s and 913 s. Accum also showed a visible boundary in at least the 480 s review, but the narrative used both `full` and `partially filled` wording. S11 must resolve that physical label through user-confirmed truth rather than treating the LVLM description as authoritative fill-state truth.

Coordinate conventions also require reconciliation: the visual-review Y values were reported in a different apparent frame/crop convention than detector `projected_source_y`. This does not invalidate the diagnostic observation that the detector produced a plausible source-space boundary near the configured Base reference line.

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

Before detector mutation:

- freeze representative clear-boundary, dark/low-contrast, occluded/unusable and successful-detection frames or short sequences from the same private video;
- record user-confirmed/corrected `.oiltruth` for usable observations rather than promoting LVLM labels to product truth;
- reconcile source-frame, ROI/crop and zero-line coordinate conventions;
- capture the complete path from preprocessing/edge evidence through proposals, semantic hypotheses, canonical outcome and temporal action;
- compare the failed Base candidate with nearby accepted/failed Accum frames under the same detector settings;
- establish whether no-interface confidence is primarily brightness/dynamic-range driven or reflects a separate evidence owner;
- preserve dataset/video bytes and settings identity for controlled base/feature comparison.

Only after this attribution should Orchestrator classify the smallest justified source lane. A bounded existing-owner defect may remain Lane B; any change to S5-B observability, temporal positive evidence, shared detector contract or validation architecture is Lane C.

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