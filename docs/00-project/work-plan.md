# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `Post-D5 S11 effectiveness reconciliation — read-only Orchestrator`

S10 is closed and S11 remains active. P2/FULL-EMPTY preservation, Spatial, local-corpus portability, S11-D1, both bounded S11-D2 classes, S11-D3 semantic authority slimming, S11-D4 Foam support/classification and S11-D5 accepted-Foam/Oil authority continuity are accepted and merged. D5 preserves existing D2/D3 current-frame Oil authority under authoritative Foam constraints while keeping D1/D4 Foam safety, sample2 Spatial anchors and `FoamTemporalGate` unchanged. The next gate is decision-only: remeasure the remaining field/local blind misses on the accepted D3+D4+D5 baseline before authorizing another source slice, and do not preauthorize temporal redesign.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-C full-video/forensic diagnostic contract: [`../30-quality/s11-c-full-video-production-replay-visual-forensic-diagnostic.md`](../30-quality/s11-c-full-video-production-replay-visual-forensic-diagnostic.md)
- S11-D1 Foam/Oil context repair plan: [`../30-quality/s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md`](../30-quality/s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md)
- S11-D2 sample3 positive-evidence recovery plan: [`../30-quality/s11-d2-sample3-positive-evidence-recovery.md`](../30-quality/s11-d2-sample3-positive-evidence-recovery.md)
- S11-D2 Class-B observation/proposal recovery gate: [`../30-quality/s11-d2-class-b-observation-proposal-representation.md`](../30-quality/s11-d2-class-b-observation-proposal-representation.md)
- S11-D3 current-frame semantic authority slimming: [`../30-quality/s11-d3-current-frame-semantic-authority-slimming.md`](../30-quality/s11-d3-current-frame-semantic-authority-slimming.md)
- S11-D4 Foam support/classification: [`../30-quality/s11-d4-foam-support-structural-classification.md`](../30-quality/s11-d4-foam-support-structural-classification.md)
- S11-D5 accepted-Foam/Oil authority continuity: [`../30-quality/s11-d5-accepted-foam-oil-current-frame-semantic-authority-continuity.md`](../30-quality/s11-d5-accepted-foam-oil-current-frame-semantic-authority-continuity.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- S11 Offline Temporal Trajectory probe: [`../30-quality/s11-offline-temporal-trajectory-probe.md`](../30-quality/s11-offline-temporal-trajectory-probe.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11-D5 Accepted-Foam / Oil Authority Continuity

PR #92 exact base `702d971262d9385671eb42d74cd0a55ed70bf15c` / exact head `4aeb62174ea17b87c958c7ea8ca9df5d8b4a1a66` passed fresh Lane C audit and was native guarded-squash-merged as `2b2ed59d05c82d2ebd447fffa4758a5307660607`. D5 keeps D2/D3 as the current-frame Oil authority while treating authoritative Foam as hard ordering plus component-exclusion context; the prior stricter Foam-separated selector is now auxiliary rather than a replacement stack. Independent real-frame evidence recovered sample3 `929/1034/1094/1124 → 300/245/244/250 px`, while `899/1079` remained fail-closed because residual non-Foam proof was insufficient. Sample2 Spatial `599/598`, D1/D4 sample4 structural/genuine-Foam safety, no-interface/glare protections and `FoamTemporalGate` ownership were retained. The final focused exact-head suite returned `164 passed`; the three paired-pulse perturbation failures were independently reproduced on exact base. This is not a general-field detector-accuracy or S11 completion PASS.

## Accepted D3/D4/D5 current-frame repairs

The detector-blind sample3 `28–40 s` refresh remains the evidence baseline: Oil was clearly/probably visible on `22/23` production-schedule rows with material representation on all `22`, while visible Foam was independently missed on `18/18` blind-positive rows. S11-D3 addressed the dominant current-frame Oil semantic rejection/competition seam without changing raw observation extraction or serialized temporal ownership. S11-D4 then addressed the separate S5-A Foam seam, recovering `12/18` frozen sample3 blind-positive Foam rows while rejecting the actual sample4 structural/refractive family on `0/14` frozen and `0/66` dense negative rows. S11-D5 then repaired the current-frame authority-composition discontinuity exposed when accepted Foam context replaced otherwise valid D2/D3 Oil authority with a stricter separate selector.

Those repairs change the accepted baseline materially enough that the remaining S11 failure distribution must now be measured again before sequencing more source work. The next decision must distinguish residual observation, current-frame semantic authority and genuinely temporal losses using current accepted evidence rather than carrying forward pre-D3/D4/D5 attribution counts as implementation authority.

## Post-portability validation and field evidence

Windows 11 canonical re-validation passed on the authoritative source tree with `1321 passed, 0 failed, 23 skipped`, where `16` skips were explicit absent-local-corpus cases and `7` were known symlink privilege limitations. The gate is therefore no longer portability/canonical.

The recorded Windows field replay remains a diagnostic baseline, but its `1441/1441 UNKNOWN_REVIEW`, `2` raw Oil boundaries and related score means predate the accepted D3/D4/D5 baseline and must not be quoted as current-head effectiveness. The private field video remains non-repeatable repository evidence; the next reconciliation should preferentially use frozen local blind evidence and use any refreshed field run only as diagnostic corroboration.

S11-C remains the causal provenance for the sample4 failure family, but its `113/113` false S5-A Foam publication is no longer current behavior: D4 rejects the frozen structural representatives `14/14` and dense `0–32.5 s` negatives `66/66` while separating later genuine Foam `14/26`. Spatial is still required for valid sample2 recovery, and a single global threshold repair remains rejected. Remaining Oil/Foam losses must be re-attributed on the merged D3+D4+D5 baseline rather than inherited from S11-C counts.

## Accepted single-frame production state

P2, its FULL/EMPTY preservation correction and Spatial are accepted S11 production responsibilities. The ordinary P0/D4/P2 route remains authoritative; raw FULL/EMPTY appearance remains downstream typed-state evidence only, while Spatial is a conservative ambiguity-only current-frame fallback and cannot override accepted no-interface or unavailable outcomes. Relative broad phase alone cannot publish numeric Oil: the five-sector path must add genuinely x-resolved information, while flat/near-horizontal Oil is allowed to remain ambiguous rather than being classified invalid. Spatial retains no history/state and introduces no setting, schema, dependency or post-owner numeric reconstruction. Detailed evidence remains in [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md).

## Retained diagnostic baseline — requires post-D5 remeasurement

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

Run a **read-only post-D5 S11 effectiveness reconciliation** on the accepted `main` baseline. Re-evaluate the frozen sample3 blind Oil/Foam rows, sample4 structural negatives and materially adjacent retained anchors to determine which residual misses are still observation, current-frame semantic-authority, genuinely temporal, or legitimately fail-closed losses after D3+D4+D5. Authorize a new source slice only from that refreshed attribution; temporal redesign remains unselected unless the remaining real application evidence demonstrates that current-frame evidence is already sufficient and the loss is genuinely temporal.
