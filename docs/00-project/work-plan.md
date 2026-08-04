# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11 — Windows field re-validation of accepted P2 + Spatial production detector`

S10 is closed. S11 remains the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. The P2 no-interface semantics repair and conservative Spatial positive-evidence fallback are merged. The Offline Temporal Trajectory probe is also complete and does not justify result-layer interpolation: held-out accepted-anchor reconstruction recovered none of the four residual production misses and materially amplified persistent wrong-boundary anchors. The next gate returns to the original Windows field video for controlled re-validation of the accepted production detector.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- S11 Offline Temporal Trajectory probe: [`../30-quality/s11-offline-temporal-trajectory-probe.md`](../30-quality/s11-offline-temporal-trajectory-probe.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11 Offline Temporal Trajectory Probe

PR #84 exact base `4bb52a2718d176874c59a97b9164453165a90c00` / exact head `3948ce3ba8f04c0d01a7a3ffe17fc68b635b6302` passed the Lane B Orchestrator exact-head gate and native guarded-squash-merged as `40cccd59e34f854cc748020f3ff50d4349ee2e05`. The diagnostic-only probe changed no production source or result schema. Held-out reconstruction estimated `3/13` truth anchors, recovered `0/4` current residual production misses, and produced material `19.5–20.5 px` errors on two reconstructed anchors; `sample4:900` showed that stable accepted anchors can consistently support the wrong boundary. Production trajectory/result interpolation is therefore not selected. S11 remains `ACTIVE`; the next gate is controlled field re-validation of the accepted P2 + Spatial detector.

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
- The Offline Temporal Trajectory probe found insufficient evidence for result-layer interpolation: it recovered none of the four residual production misses and demonstrated that temporally consistent accepted anchors can reinforce a persistent wrong boundary. Production trajectory integration is not selected from this evidence; S12 stays separate.

## Next action

Re-run the original Windows field workload with the current accepted production detector under the same 480–1200 s interval, Base/Accum Recipe geometry, sampling policy and detector settings where reproducible. Compare against the recorded pre-S11 field baseline (`Base 0/1440` numeric Oil; `Accum 41/1441`, about `2.8%`) and visually review representative visible-boundary, dark/lighting-change and occlusion intervals so higher numeric coverage is not mistaken for correctness. This gate may establish bounded field improvement, but it does not by itself establish category-balanced/general-field detector accuracy. If material residual failure remains, classify the next repair from the observed failure class rather than resuming open-ended temporal interpolation research. S12 UI/UX refinement remains separate.