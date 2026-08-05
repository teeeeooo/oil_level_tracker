# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11 — local-corpus canonical portability repair (Lane B)`

S10 is closed. S11 remains the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. The P2 no-interface semantics repair, its FULL/EMPTY preservation correction and the conservative Spatial positive-evidence fallback are merged. The Offline Temporal Trajectory probe remains closed without production interpolation. Before returning to field re-validation, the separate local-corpus canonical portability defect must be repaired as Lane B and Windows canonical rerun on that repaired baseline.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- S11 Offline Temporal Trajectory probe: [`../30-quality/s11-offline-temporal-trajectory-probe.md`](../30-quality/s11-offline-temporal-trajectory-probe.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11 P2 FULL/EMPTY No-Interface Preservation Repair

PR #85 exact base `d46077497f1e54c92f723dd4c846291cce12b901` / exact head `97de6de6d2a60d711790a805eb38dce48dfcd129` passed fresh Lane C exact-head audit and native guarded-squash-merged as `ee07a194f196985864c551e23b5f3091d0c9c343`. The four-file repair preserves P2 exposure-decoupling while restoring genuine FULL/EMPTY no-interface by moving the removed `0.17` positive weight to normalized-raster uniformity (`0.27 → 0.44`); raw intensity and FULL/EMPTY appearance likelihoods remain outside positive absence scoring. Auditor exact-head validation passed `406` tests with one independently proven stale P0-production parity assertion deselected; direct exact-base/head comparison restored the two basic and ten noisy-uniform FULL/EMPTY cases, preserved all `160` repository-owned truth-positive controlled neighborhoods without result changes, retained the four low-exposure P2 rescue anchors as ambiguous/non-numeric, and kept collision/glare/structure/Foam/Spatial/serialized-owner protections. No Windows canonical or general detector-accuracy PASS is inferred.

## Accepted single-frame production state

P2, its FULL/EMPTY preservation correction and Spatial are accepted S11 production responsibilities. The ordinary P0/D4/P2 route remains authoritative; raw FULL/EMPTY appearance remains downstream typed-state evidence only, while Spatial is a conservative ambiguity-only current-frame fallback and cannot override accepted no-interface or unavailable outcomes. Relative broad phase alone cannot publish numeric Oil: the five-sector path must add genuinely x-resolved information, while flat/near-horizontal Oil is allowed to remain ambiguous rather than being classified invalid. Spatial retains no history/state and introduces no setting, schema, dependency or post-owner numeric reconstruction. Detailed evidence remains in [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md).

## S11 current diagnosis

- A 1280×720 / 30 fps Windows field video was analyzed over 480–1200 s with two Glasses using identical detector settings.
- Base produced no numeric Oil detections and remained mainly `UNKNOWN_REVIEW`; Accum produced only sparse numeric detections and was dominated by no-interface states.
- At a visually clear Base frame, Canny/hypothesis geometry contained a plausible boundary near the reference line, but boundary evidence lost to ambiguity/no-interface competition and the tracker received `NO_UPDATE`.
- At dark Accum frames, high uniformity/no-interface evidence dominated despite a visually reported Oil boundary; numeric detections appeared only when lighting changed and no-interface evidence collapsed.
- These observations are diagnostic evidence, not authoritative detector-accuracy truth. Source inspection resolved the detector/product source-frame Y convention, and the private field video is not a repeatable S11 development corpus.
- Repository-local truth-positive frames reproduce the same exposure-sensitivity class under controlled brightness changes: valid Oil can become ambiguous or false no-interface as absolute photometric evidence weakens.
- The completed P0/P1/P2/P3 probe showed that stronger scalar relative phase can recover some Oil but creates unsafe collision false Oil; the selected P2 semantics repair safely reduces exposure-driven false no-interface without recovering numeric Oil.
- PR #82 merged the exposure-decoupled P2 semantics, and PR #85 now preserves genuine FULL/EMPTY no-interface on top of that contract by strengthening normalized-raster uniformity only; raw FULL/EMPTY appearance remains downstream typed-state evidence, with ambiguity, glare/structure protection, S5-A Foam independence and serialized temporal ownership retained.
- The merged Spatial Path probe recovered two additional native Oil rows while preserving the retained collision/glare/structure/Foam protections in targeted evidence, establishing cross-ROI spatial information as a useful bounded positive-evidence direction.
- PR #83 now carries those two native Spatial recoveries through the canonical S5-B owner while retaining the original seven numeric anchors and the targeted collision/glare/structure/Foam/P2 protections.
- Its non-degenerate path span is only a proof of additional x-resolved fallback information, not a universal physical Oil discriminator; valid flat/near-horizontal Oil can remain ambiguous without being classified invalid.
- The merged P2 × Spatial interaction probe found no material numeric-recovery interaction, so Spatial remains a separate secondary positive-evidence fallback rather than a P2-coupled recovery mechanism.
- The Offline Temporal Trajectory probe found insufficient evidence for result-layer interpolation: it recovered none of the four residual production misses and demonstrated that temporally consistent accepted anchors can reinforce a persistent wrong boundary. Production trajectory integration is not selected from this evidence; S12 stays separate.

## Next action

Repair the separate S11 local-corpus canonical portability defect as a bounded Lane B task. The repair must restore clean-checkout/Windows canonical access to the authoritative local corpus without changing detector semantics, truth meaning, or the established MP4 identity contract. After that repair closes, rerun Windows canonical; only after canonical is green should the original 480–1200 s Windows field workload be revalidated against the recorded pre-S11 Base/Accum baseline. S12 UI/UX refinement remains separate.