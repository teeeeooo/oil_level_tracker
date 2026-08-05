# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11-D1 — Foam structural/refractive discrimination and Oil context safety`

S10 is closed. S11 remains the P0 successor because field-representative video still shows severe detector effectiveness failure despite the accepted platform/package baseline. P2, its FULL/EMPTY preservation correction, Spatial and local-corpus portability are merged. Windows canonical re-validation is green, and S11-C full-video replay/forensics is complete. S11-C proves multiple residual failure modes and, most importantly, a causal S5-A Foam → S5-B Oil routing defect on structural/refractive sight-glass evidence. The current gate is S11-D1: repair that shared responsibility boundary first, then replay before opening the separate sample3 positive-evidence work.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-C full-video/forensic diagnostic contract: [`../30-quality/s11-c-full-video-production-replay-visual-forensic-diagnostic.md`](../30-quality/s11-c-full-video-production-replay-visual-forensic-diagnostic.md)
- S11-D1 Foam/Oil context repair plan: [`../30-quality/s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md`](../30-quality/s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- S11 Offline Temporal Trajectory probe: [`../30-quality/s11-offline-temporal-trajectory-probe.md`](../30-quality/s11-offline-temporal-trajectory-probe.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11 Local-Corpus Canonical Portability Repair

PR #86 exact base `b0a5da3805d50faba524d874e97c616136e3c6c1` / exact head `1caa4f36fd1e35de70dbb469047356612f6ab549` passed the Lane B Orchestrator exact-head gate and native guarded-squash-merged as `7ec3cc8eaf46214c73d52dcfa908e1feb949e452`. The test/diagnostic-only repair changes no production source: missing ignored MP4 corpus is now explicit `SKIPPED / NOT AVAILABLE`, any present wrong-hash MP4 hard-fails before decode or aggregation using the checked-in S11-A manifest as identity authority, and hash-correct decode failure remains hard failure. Historical P0/P1/P2 diagnostic semantics are frozen independently from later Spatial production, removing the obsolete P0-production parity coupling while preserving current Spatial production ownership. Worker exact-head evidence recorded `37 passed` on the complete correct local corpus, an isolated no-corpus checkout at `21 passed / 16 skipped / exit 0`, and explicit wrong-identity hard failure. No Windows canonical or detector/general-field accuracy PASS is inferred.

## Post-portability validation and field evidence

Windows 11 canonical re-validation passed on the authoritative source tree with `1321 passed, 0 failed, 23 skipped`, where `16` skips were explicit absent-local-corpus cases and `7` were known symlink privilege limitations. The gate is therefore no longer portability/canonical.

Controlled field re-validation remains diagnostic, but BASE already demonstrates the product problem persists after accepted S11 production changes: `1441/1441` rows are `UNKNOWN_REVIEW`, only `2` raw Oil boundaries are accepted, `1436/1441` decisions are ambiguous, and `10,730` proposals collapse to only `4` selected candidates. User/LVLM review reports visible Oil at multiple representative times. The current field score means are boundary `0.278`, artifact `0.341`, ambiguity `0.530` and no-interface `0.421`, so the dominant problem is positive-boundary identifiability/competition rather than proposal absence.

S11-C has now completed the full production-stream replay and bounded visual/candidate attribution. Local replay reproduces the Windows chain `many candidates → weak/competing Oil authority → ambiguity → NO_UPDATE`, while also separating multiple local modes: sample3 contains both correct-Y candidates that remain non-identifiable and visually clear boundaries that never become candidates. The highest-priority causal finding is sample4: Foam is accepted on all `113/113` replay rows, structural/refractive U-shaped support can satisfy the Foam owner, and withholding only accepted Foam context from the Oil owner collapses Oil publication from `110/113` to `0/113`. Spatial remains required for valid sample2 recovery but also owns suspicious sample3 full-like acceptances. A single global threshold repair is therefore rejected.

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

Start S11-D1 as a provisional Lane C source slice. Perform only a bounded external-reference review that can inform the existing S5-A/S5-B owners, then repair the proven structural/refractive Foam → Oil routing authority defect without using a global Foam/Oil threshold shift or sample-specific exception. Preserve genuine Foam, user-confirmed sample2 Spatial recovery, glare/structure/collision and FULL/EMPTY protections. Reuse the ignored S11-C forensic bundle while it remains decision-bearing, then rerun the four-video production replay after D1. Keep the separate sample3 candidate-generation/identifiability repair for S11-D2 and keep initial-state retrospective reconstruction outside this detector slice.
