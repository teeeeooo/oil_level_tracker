# S11 Subtractive Detector Simplification Architecture

**Status:** `HISTORICAL PRE-R6 — A–D EVIDENCE PROVENANCE`

## Purpose

This document preserves the completed S11 A–D design for improving current-frame
Oil-boundary effectiveness by **removing redundant authority before adding new
detector mechanisms**. Its runtime routing and final-analysis publication
boundary are historical and are superseded by the active
[`S11-R6 Optics-Aware Observation Architecture`](s11-r6-optics-aware-observation-architecture.md).
Its proposal simplification, negative families and fail-closed lessons remain
validation provenance; they do not restore a pre-R6 owner.

The design is corpus-wide. It is not a `sample3` repair and MUST NOT introduce video-, frame-, Recipe-, truth- or sample-identity branches.

## Evidence that reopened detector source work

A fresh read-only review on synchronized `main` at `ce9f37f2e5a25888f48ebd69f8c24fdd6071e5e4` reproduced low detector effectiveness across all four repository-local real videos. In the fixed-geometry 2 FPS replay windows, numeric Oil remained a minority outcome while ambiguity dominated; positive no-interface was not the primary loss class.

The same review found that difficult frames commonly retain material current-frame hypotheses near user-confirmed Oil. The dominant problem is therefore not simply missing image primitives: bounded proposal competition and repeated semantic opposition can suppress already-observed evidence.

Initial subtractive ablation suggested that `REGION_STEP` alone could preserve the available-corpus representation surface. Slice A then expanded retained positive/negative evidence and disproved the stronger removal hypothesis: ordinary Sobel, Canny and Hough each retained a distinct competing-proposal responsibility, while distributed-Sobel supplemental authority had no remaining required production responsibility and was removed.

The bright-plateau artifact heuristic is a second demonstrated overreach. On real user-confirmed sample2/sample4 Oil hypotheses it can dominate artifact likelihood even when direct broad/narrow glare overlap is zero. Removing it globally is not yet safe: a retained `foam-clipped-glare` negative family can become false Oil. That negative family, however, carries direct glare/collision evidence, so plateau authority should be narrowed to proven collision support rather than remain generic opposition for every hypothesis.

Existing Spatial evidence is also underused rather than absent. Some remaining truth-near ambiguous candidates already satisfy the bounded cross-ROI phase path, but route-specific scalar eligibility prevents that independent corroboration from receiving authority.

The existing offline trajectory probe remains negative evidence against solving this problem downstream: it recovered none of the residual detector misses and can reinforce a persistent wrong accepted boundary. Temporal/result interpolation is therefore outside this redesign.

## Design principles

1. **Subtract before adding.** No new CV primitive, dependency, ML model, optical flow or raster history is justified while removing redundant authority preserves or improves evidence coverage.
2. **Primary representation with only proven competitors.** Region/phase-transition evidence is the primary Oil Y-proposal responsibility. Ordinary Sobel, Canny and Hough may retain bounded competing proposal evidence only where retained failures prove a distinct current responsibility; supplemental proposal families without such proof should be removed.
3. **Keep only demonstrated hard invalidity hard.** At the A–D design point,
   accepted no-interface, unavailable evidence, severe glare/exclusion/border
   conflict and authoritative Foam topology remained fail-closed. R6 later
   removed Foam topology from Oil authority; that replacement controls current
   runtime behavior.
4. **Compose soft semantics once.** Boundary, artifact, morphology, polarity and ambiguity evidence must not repeatedly veto the same candidate through multiple correlated routes.
5. **Use Spatial as independent proof.** The existing bounded cross-ROI path may corroborate a hard-safe weak candidate when scalar uniqueness is insufficient; it must not become another duplicate stack of the same semantic thresholds.
6. **Preserve one current-frame numeric owner and one serialized online owner.**
   Only a canonical accepted boundary may publish current-frame Oil. The current
   completed-analysis owner is R6 and may publish only an eligible same-frame
   candidate.

## Product optimization objective

The detector is optimized for **usable observed trajectory**, not pixel-perfect frame localization. A coarse current-frame Oil boundary may be more valuable than abstention when it still represents the same physical Oil interface and helps the final graph communicate rise, fall, hold, minimum and recovery behavior.

Accordingly, later slices may trade a modest increase in pixel error for materially higher usable numeric coverage and better time-axis observation distribution. That trade is not allowed to create persistent gross wrong-interface tracking of glass structure, reflection, glare or another unrelated feature, and it never authorizes synthetic numeric values where current-frame evidence is absent.

## Ordered source slices

### Slice A — Proposal Authority Consolidation — ACCEPTED

Slice A removed the distributed-Sobel supplemental producer and its separate raw/proposal/semantic capacity policy. Ordinary Region, Sobel, Canny and Hough proposal evidence remains because retained failure evidence demonstrated distinct current responsibilities. Canonical publication behavior was preserved.

This accepted slice is the simplified baseline for later coverage work; removed distributed-Sobel authority must not be restored merely to increase a benchmark count.

### Slice B — Scoped Plateau / Collision Authority — ACCEPTED

Slice B removed bright-plateau appearance as independent generic artifact opposition and retained it only as a multiplier on existing current-frame collision evidence. The accepted exact-head replay increased corpus numeric coverage from 67/299 to 71/299 without reducing another sample, and reduced sample4 longest missing span from 35.5 s to 12.5 s while newly recovered observations remained on the same physical Oil interface.

Retained glare/collision/structure/Foam/no-interface populations remained fail-closed. This accepted scoped plateau composition is the scalar baseline for Slice C and must not be broadened back into generic appearance authority merely to suppress new Spatial candidates.

### Slice C — Unified Spatial Corroboration — ACCEPTED

Slice C preserved the existing scalar-supported Spatial route and added fallback-only full-path corroboration for hard-safe weak candidates. Weak recovery requires stronger 5/5 cross-ROI proof, retains local-authority-tie rejection and hard current-frame safety, and still resolves through the existing typed/canonical publication and serialized temporal owners. The accepted replay increased corpus numeric coverage from `71/299` to `109/299` with no removed production numerics; sample4 improved from `26/113` to `62/113` and its longest missing span fell from `12.5 s` to `3.5 s`.

### Slice D — Effectiveness Reconciliation — ACCEPTED

The accepted A–C baseline was replayed across the complete four-video qualification windows and retained collision/glare/structure/Foam/no-interface populations. The Slice-D baseline coverage was `109/299`; user-confirmed truth coverage was `8/13` with `5.4375 px` MAE. The retained current-frame preservation suite passed `356` tests.

Residual long gaps did not form one material hard-safe general detector failure class under the Slice-D evidence: the base-sample long gap was dominated by a static explanatory overlay, while the then-reviewed sample3 gap coincided with no-interface/strong motion-reframing blur/unclear evidence. Later direct sequence review disproved some exact sample3 outputs and is owned by the separate [`S11-R3 Sequence Observability Integrity Architecture`](s11-sequence-observability-integrity-architecture.md). Slice D remains the accepted subtractive responsibility baseline, not current exact-output authority.

### S11-R2 successor boundary

Later direct Glass-ROI review isolated a narrower composition defect that Slice D's aggregate reconciliation did not authorize or test: in authoritative accepted-Foam context, an artifact-dominant numeric incumbent can block an already-existing full-path Spatial candidate, and path-invalid preliminary evidence can terminate that existing search. This is not a new detector mechanism or a reopening of global Spatial thresholds. Its accepted authority is the separate [`S11 Foam/Spatial Authority Repair Architecture`](s11-foam-spatial-authority-repair-architecture.md).

## Validation authority

The decision-bearing evidence surface is the existing repository-local corpus and retained controlled regressions: user-confirmed `.oiltruth`, blind `.provisional-truth.json`, four-video replay under the matching Recipes, collision/glare/structure/Foam/no-interface controls and bounded temporal regressions.
Acceptance must report coverage together with truth-near error and false-positive/abstention behavior; a higher numeric publication count alone is insufficient. The four samples are one corpus and no single sample may become the tuning objective.

The first three slices are source changes to the accepted S5-B observability responsibility and therefore require one focused branch/PR each unless a Worker proves they are inseparable in the same owner. The Orchestrator must classify actual blast radius at handoff; architecture/semantic authority movement is expected to require fresh independent review.

## Historical slice boundaries

For the A–D source slices, this design did not authorize changes to the following
then-current responsibilities. The active R6 architecture supersedes any
conflicting Foam/Oil or final-analysis routing below:

- S5-A current-frame Foam classification/publication or online Foam temporal-gate semantics;
- positive no-interface meaning established by P2;
- Recipe, truth, result, CSV, debug or persisted public schemas;
- Initial-State Retrospective FULL/EMPTY reconstruction;
- Result Review observed-anchor presentation semantics;
- the one serialized current-frame S5-B temporal owner or two-real-boundary reacquisition contract;
- offline interpolation, estimated trajectory publication or hidden temporal state;
- detector behavior keyed to repository sample identity.

If subtractive simplification violates a retained negative family, the correct response is to identify the smallest real safety responsibility that was lost. Do not restore the entire removed stack or add a new heuristic merely to recover a benchmark count.

## Current executable gate

There is no remaining subtractive detector source gate. Slices A–D and the R2–R4
repairs remain accepted as historical evidence/fixture surfaces, not as active
owner topology. R6 owns current Oil/state, independent Foam and final composition
responsibility. All other detector mechanisms still require new evidence and are
not pre-authorized by this architecture. The exact current gate belongs to the
[work plan](../00-project/work-plan.md).
