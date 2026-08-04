# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11-B — Spatial positive-evidence production fallback fresh exact-head audit`

S10 is closed. S11 remains the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. The P2 no-interface semantics repair is now merged; any further detector mutation remains separately scoped and must preserve the accepted S5-A Foam and S5-B fail-closed observability contracts.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- S11-B Spatial production fallback: [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11-B P2 No-Interface Production Repair

PR #82 exact base `a38ee44f68cac519c5e90cbf3150d963b7da13eb` / exact head `d3204d90a04fbe7496808e77034ac268e92f477c` passed fresh Lane C exact-head audit and native guarded-squash-merged as `ebabcf9dd35bf3ec88be37c29ebadbeaac46144a`. The bounded four-file repair removes absolute raw brightness from positive interface-absence evidence, measures no-interface uniformity on the normalized raster, and retains current-frame visibility in adjacent identifiability reliability while preserving raw FULL/EMPTY appearance only for typed fill-state distinction. Auditor exact-head focused validation passed `154` tests with `git diff --check` clean; an independent 1,323-case controlled/collision/texture/geometry counterfactual probe found zero acceptance sign flips from the visibility seam. This closes only the P2 semantics repair: no detector/general-field accuracy PASS or S11 completion is inferred.

## Current focused feature — S11-B Spatial Positive-Evidence Production Fallback

The focused feature starts from exact main `1e83aac0643b0734fa1d67dfa30b88da6f3bd31e` and is pending fresh Lane C exact-head audit. The production route is P0/D4-first and runs only after the complete current-frame path remains ambiguous. Relative broad phase may form a candidate, but numeric Oil still requires a bounded five-sector cross-ROI path proving additional x-resolved information; scalar relative phase alone cannot publish. The path-span non-degeneracy condition is a conservative fallback abstention rule, not a claim that valid Oil must slope or curve. Actual production native evidence is `7/13 → 9/13` with recoveries at `sample2:30` and `sample2:60`, zero existing-anchor changes, collision/glare/structure/Foam protections retained in the focused suite, no new temporal owner/state and no settings/schema/dependency expansion. See [`../30-quality/s11-b-spatial-positive-evidence-production.md`](../30-quality/s11-b-spatial-positive-evidence-production.md).

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
- The focused production feature now reproduces those two native recoveries through the canonical S5-B owner while retaining the original seven numeric anchors and the targeted collision/glare/structure/Foam protections; it remains unaccepted until fresh exact-head audit.
- Its non-degenerate path span is only a proof of additional x-resolved fallback information, not a universal physical Oil discriminator; valid flat/near-horizontal Oil can remain ambiguous without being classified invalid.
- The merged P2 × Spatial interaction probe found no material numeric-recovery interaction, so Spatial remains a separate secondary positive-evidence fallback rather than a P2-coupled recovery mechanism.
- Offline temporal trajectory estimation remains a separate result-estimation successor after the single-frame production observation layer is stabilized; S12 stays separate.

## Next action

Run a fresh Lane C Independent Auditor exact-head review of the focused Spatial production feature. Only after `AUDIT: PASS` may the Auditor mark the Draft PR Ready, guarded-merge it, synchronize main and record bounded Close evidence. If accepted, the next separately owned detector gate is the offline temporal trajectory probe for observed/estimated/unavailable result reconstruction. S12 UI/UX refinement remains separate.