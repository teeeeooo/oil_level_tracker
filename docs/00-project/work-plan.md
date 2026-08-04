# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11 — Offline Temporal Trajectory probe`

S10 is closed. S11 remains the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. The P2 no-interface semantics repair and conservative Spatial positive-evidence fallback are now merged. The single-frame production observation layer is stable enough for the separately owned Offline Temporal Trajectory diagnostic gate; any later production result/schema integration remains separately classified.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11-B Spatial Positive-Evidence Production Fallback

PR #83 exact base `1e83aac0643b0734fa1d67dfa30b88da6f3bd31e` / exact head `7378207b31f1a83cc0472adafa376a5b09aa14f6` passed fresh Lane C exact-head audit and native guarded-squash-merged as `1a4381c6be87068a083b26b72ca332a9e8baf9b0`. The bounded eight-file feature keeps ordinary P0/S6-D4/P2 evaluation first, runs Spatial only after genuine `ShadowAmbiguousObservation`, requires a five-sector non-degenerate current-frame path before relative-phase recovery can publish, and still routes accepted evidence through Phase-A, the single serialized reducer, canonical outcome and production projection. Auditor focused validation passed `170` tests with `git diff --check` clean; independent same-source timing measured native-case median `126.35 → 150.94 ms` with recovered rows near `458–460 ms`, consistent with the static `5 × 25` path-search bound and the supported offline lifecycle. The historical P2×Spatial diagnostic assertion expecting pre-P2 `P0=no_interface` remains a pre-existing stale test contract and is not a PR #83 regression. S11 remains `ACTIVE`; no general detector-accuracy PASS is claimed.

## Accepted single-frame production state

P2 and Spatial are now separate accepted S11-B production responsibilities. The ordinary P0/D4/P2 route remains authoritative; Spatial is a conservative ambiguity-only current-frame fallback and cannot override accepted no-interface or unavailable outcomes. Relative broad phase alone cannot publish numeric Oil: the five-sector path must add genuinely x-resolved information, while flat/near-horizontal Oil is allowed to remain ambiguous rather than being classified invalid. Spatial retains no history/state and introduces no setting, schema, dependency or post-owner numeric reconstruction. Detailed evidence remains in [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md).

## S11 current diagnosis

- A 1280×720 / 30 fps Windows field video was analyzed over 480–1200 s with two Glasses using identical detector settings.
- Base produced no numeric Oil detections and remained mainly `UNKNOWN_REVIEW`; Accum produced only sparse numeric detections and was dominated by no-interface states.
- At a visually clear Base frame, Canny/hypothesis geometry contained a plausible boundary near the reference line, but boundary evidence lost to ambiguity/no-interface competition and the tracker received `NO_UPDATE`.
- At dark Accum frames, high uniformity/no-interface evidence dominated despite a visually reported Oil boundary; numeric detections appeared only when lighting changed and no-interface evidence collapsed.
- These observations are diagnostic evidence, not authoritative detector-accuracy truth. Source inspection resolved the detector/product source-frame Y convention, and the private field video is not a repeatable S11 development corpus.
- Repository-local truth-positive frames reproduce the same exposure-sensitivity class under controlled brightness changes: valid Oil can become ambiguous or false no-interface as absolute photometric evidence weakens.
- The completed P0/P1/P2/P3 probe showed that stronger scalar relative phase can recover some Oil but creates unsafe collision false Oil; the selected P2 semantics repair safely reduces exposure-driven false no-interface without recovering numeric Oil.
- PR #82 has now merged that P2 repair into the canonical S5-B owner, retaining raw FULL/EMPTY appearance only for typed fill-state distinction and preserving fail-closed ambiguity, glare/structure protection, S5-A Foam independence and serialized temporal ownership.
- The merged Spatial Path probe recovered two additional native Oil rows while preserving the retained collision/glare/structure/Foam protections in targeted evidence, establishing cross-ROI spatial information as a useful bounded positive-evidence direction.
- PR #83 now carries those two native Spatial recoveries through the canonical S5-B owner while retaining the original seven numeric anchors and the targeted collision/glare/structure/Foam/P2 protections.
- Its non-degenerate path span is only a proof of additional x-resolved fallback information, not a universal physical Oil discriminator; valid flat/near-horizontal Oil can remain ambiguous without being classified invalid.
- The merged P2 × Spatial interaction probe found no material numeric-recovery interaction, so Spatial remains a separate secondary positive-evidence fallback rather than a P2-coupled recovery mechanism.
- Offline temporal trajectory estimation remains a separate result-estimation successor after the single-frame production observation layer is stabilized; S12 stays separate.

## Next action

Run the separately owned Offline Temporal Trajectory probe against the stabilized single-frame observation stream. Preserve raw accepted/ambiguous/no-interface observations and evaluate an explicit `observed` / `estimated` / `unavailable` trajectory with abstention across unsupported gaps. This next gate is diagnostic evidence work only until its owner independently classifies any production result fields, persisted/exported provenance, graph reconstruction or detector feedback. S12 UI/UX refinement remains separate.