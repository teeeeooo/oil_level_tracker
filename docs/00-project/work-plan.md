# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11 — Windows canonical rerun on portability-repaired baseline`

S10 is closed. S11 remains the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. The P2 no-interface semantics repair, its FULL/EMPTY preservation correction and the conservative Spatial positive-evidence fallback are merged. The Offline Temporal Trajectory probe remains closed without production interpolation. The local-corpus canonical portability repair is now merged; the next gate is a fresh Windows canonical rerun on that repaired baseline before any controlled field re-validation.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- S11 Offline Temporal Trajectory probe: [`../30-quality/s11-offline-temporal-trajectory-probe.md`](../30-quality/s11-offline-temporal-trajectory-probe.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11 Local-Corpus Canonical Portability Repair

PR #86 exact base `b0a5da3805d50faba524d874e97c616136e3c6c1` / exact head `1caa4f36fd1e35de70dbb469047356612f6ab549` passed the Lane B Orchestrator exact-head gate and native guarded-squash-merged as `7ec3cc8eaf46214c73d52dcfa908e1feb949e452`. The test/diagnostic-only repair changes no production source: missing ignored MP4 corpus is now explicit `SKIPPED / NOT AVAILABLE`, any present wrong-hash MP4 hard-fails before decode or aggregation using the checked-in S11-A manifest as identity authority, and hash-correct decode failure remains hard failure. Historical P0/P1/P2 diagnostic semantics are frozen independently from later Spatial production, removing the obsolete P0-production parity coupling while preserving current Spatial production ownership. Worker exact-head evidence recorded `37 passed` on the complete correct local corpus, an isolated no-corpus checkout at `21 passed / 16 skipped / exit 0`, and explicit wrong-identity hard failure. No Windows canonical or detector/general-field accuracy PASS is inferred.

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

Rerun the full Windows canonical suite on the current synchronized main after the local-corpus portability repair. Record exact main identity, Python/platform context, terminal summary, all skips and any remaining failures. Missing ignored S11 MP4s should now appear only as explicit corpus-dependent skips; wrong local MP4 identity must remain a hard failure. Only after Windows canonical is green should the original 480–1200 s Windows field workload be revalidated against the recorded pre-S11 Base/Accum baseline. S12 UI/UX refinement remains separate.