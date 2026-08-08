# S11 Subtractive Detector Simplification Architecture

**Status:** `ACTIVE DESIGN — implementation pending`

## Purpose

This document owns the active S11 design for improving general Oil-boundary effectiveness by **removing redundant authority before adding new detector mechanisms**. It does not supersede the accepted S5-B/S11 safety contracts until each source slice is implemented, independently accepted at its assigned lane, and reconciled into the durable baseline.

The design is corpus-wide. It is not a `sample3` repair and MUST NOT introduce video-, frame-, Recipe-, truth- or sample-identity branches.

## Evidence that reopened detector source work

A fresh read-only review on synchronized `main` at `ce9f37f2e5a25888f48ebd69f8c24fdd6071e5e4` reproduced low detector effectiveness across all four repository-local real videos. In the fixed-geometry 2 FPS replay windows, numeric Oil remained a minority outcome while ambiguity dominated; positive no-interface was not the primary loss class.

The same review found that difficult frames commonly retain material current-frame hypotheses near user-confirmed Oil. The dominant problem is therefore not simply missing image primitives: bounded proposal competition and repeated semantic opposition can suppress already-observed evidence.

Subtractive ablation also showed that `REGION_STEP` alone preserved the blind-visible representation coverage of the full observation stack while improving user-confirmed truth representation and roughly halving raw observation load. Sobel/Canny/Hough-derived proposal ownership therefore has no demonstrated corpus-wide necessity at the current baseline.

The bright-plateau artifact heuristic is a second demonstrated overreach. On real user-confirmed sample2/sample4 Oil hypotheses it can dominate artifact likelihood even when direct broad/narrow glare overlap is zero. Removing it globally is not yet safe: a retained `foam-clipped-glare` negative family can become false Oil. That negative family, however, carries direct glare/collision evidence, so plateau authority should be narrowed to proven collision support rather than remain generic opposition for every hypothesis.

Existing Spatial evidence is also underused rather than absent. Some remaining truth-near ambiguous candidates already satisfy the bounded cross-ROI phase path, but route-specific scalar eligibility prevents that independent corroboration from receiving authority.

The existing offline trajectory probe remains negative evidence against solving this problem downstream: it recovered none of the residual detector misses and can reinforce a persistent wrong accepted boundary. Temporal/result interpolation is therefore outside this redesign.

## Design principles

1. **Subtract before adding.** No new CV primitive, dependency, ML model, optical flow or raster history is justified while removing redundant authority preserves or improves evidence coverage.
2. **One primary Y-proposal responsibility.** Current evidence supports region/phase-transition representation as the primary bounded Oil proposal owner. Edge primitives may remain corroborating features without independently consuming proposal capacity.
3. **Keep only demonstrated hard invalidity hard.** Accepted no-interface, unavailable evidence, severe glare/exclusion/border conflict and authoritative Foam topology remain fail-closed.
4. **Compose soft semantics once.** Boundary, artifact, morphology, polarity and ambiguity evidence must not repeatedly veto the same candidate through multiple correlated routes.
5. **Use Spatial as independent proof.** The existing bounded cross-ROI path may corroborate a hard-safe weak candidate when scalar uniqueness is insufficient; it must not become another duplicate stack of the same semantic thresholds.
6. **Preserve one numeric-publication owner and one serialized temporal owner.** Only a canonical accepted boundary may publish numeric Oil; temporal confirmation semantics remain downstream and unchanged.

## Ordered source slices

### Slice A — Proposal Authority Consolidation

Make region/phase-transition evidence the primary Oil Y-proposal owner inside the existing S5-B current-frame pipeline. Sobel, Canny, Hough and distributed-Sobel evidence may remain available as local corroborating measurements where still useful, but they must not independently consume bounded proposal slots unless the Worker proves a retained failure family that requires that ownership.

Acceptance is not “fewer lines.” The slice must preserve or improve truth-near representation across the four-video corpus, preserve blind-visible representation, retain current numeric-publication safety, and reduce redundant proposal competition without changing temporal, Foam, result or persisted contracts.

### Slice B — Scoped Plateau / Collision Authority

After Slice A is accepted, remove bright-plateau evidence from unconditional generic artifact opposition. Retain only the smallest directly evidenced collision responsibility needed to protect real glare/foam-glare failures. Do not replace the removed broad authority with new appearance carve-outs or sample-specific thresholds.

### Slice C — Unified Spatial Corroboration

After the scalar current-frame owner is simplified, allow the existing bounded Spatial phase path to corroborate hard-safe weak candidates without requiring them to pass a second near-duplicate scalar eligibility stack. Spatial must still abstain on direct glare/exclusion/border/Foam-topology invalidity, insufficient residual sectors, local authority ties and unsupported geometry.

### Slice D — Effectiveness Reconciliation

Replay the complete four-video corpus and retained negative populations on the accepted simplified baseline. Only if a material, general failure class remains should another detector mechanism be proposed. Final Windows field-workflow validation resumes after this reconciliation accepts the source baseline.

## Validation authority

The decision-bearing evidence surface is the existing repository-local corpus and retained controlled regressions: user-confirmed `.oiltruth`, blind `.provisional-truth.json`, four-video replay under the matching Recipes, collision/glare/structure/Foam/no-interface controls and bounded temporal regressions.
Acceptance must report coverage together with truth-near error and false-positive/abstention behavior; a higher numeric publication count alone is insufficient. The four samples are one corpus and no single sample may become the tuning objective.

The first three slices are source changes to the accepted S5-B observability responsibility and therefore require one focused branch/PR each unless a Worker proves they are inseparable in the same owner. The Orchestrator must classify actual blast radius at handoff; architecture/semantic authority movement is expected to require fresh independent review.

## Preserved boundaries

This design does not authorize changes to:

- S5-A Foam publication or Foam temporal-gate semantics;
- positive no-interface meaning established by P2;
- Recipe, truth, result, CSV, debug or persisted public schemas;
- Initial-State Retrospective FULL/EMPTY reconstruction;
- Result Review observed-anchor presentation semantics;
- the one serialized S5-B temporal owner or two-real-boundary reacquisition contract;
- offline interpolation, estimated trajectory publication or hidden temporal state;
- detector behavior keyed to repository sample identity.

If subtractive simplification violates a retained negative family, the correct response is to identify the smallest real safety responsibility that was lost. Do not restore the entire removed stack or add a new heuristic merely to recover a benchmark count.

## Current executable gate

The first executable source gate is **Slice A — Proposal Authority Consolidation**. Slice B and Slice C remain ordered successors and are not pre-authorized implementation scope for the Slice A Worker.
