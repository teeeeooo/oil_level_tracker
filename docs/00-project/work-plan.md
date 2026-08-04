# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11-B — conservative Spatial positive-evidence production fallback`

S10 is closed. S11 remains the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. The P2 no-interface semantics repair is now merged; any further detector mutation remains separately scoped and must preserve the accepted S5-A Foam and S5-B fail-closed observability contracts.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — S11-B P2 No-Interface Production Repair

PR #82 exact base `a38ee44f68cac519c5e90cbf3150d963b7da13eb` / exact head `d3204d90a04fbe7496808e77034ac268e92f477c` passed fresh Lane C exact-head audit and native guarded-squash-merged as `ebabcf9dd35bf3ec88be37c29ebadbeaac46144a`. The bounded four-file repair removes absolute raw brightness from positive interface-absence evidence, measures no-interface uniformity on the normalized raster, and retains current-frame visibility in adjacent identifiability reliability while preserving raw FULL/EMPTY appearance only for typed fill-state distinction. Auditor exact-head focused validation passed `154` tests with `git diff --check` clean; an independent 1,323-case controlled/collision/texture/geometry counterfactual probe found zero acceptance sign flips from the visibility seam. This closes only the P2 semantics repair: no detector/general-field accuracy PASS or S11 completion is inferred, and the current gate advances to the separate conservative Spatial positive-evidence production fallback.

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
- The spatial probe remains conservative and is not itself a production cutover: its non-degenerate-path gate must not be treated as a universal physical Oil discriminator, especially for valid near-horizontal surfaces.
- The merged P2 × Spatial interaction probe found no material numeric-recovery interaction, so Spatial remains a separate secondary positive-evidence fallback rather than a P2-coupled recovery mechanism.
- Offline temporal trajectory estimation remains a separate result-estimation successor after the single-frame production observation layer is stabilized; S12 stays separate.

## Next action

Design and classify the conservative Spatial positive-evidence production fallback as a separate mutation, preserving P0-first acceptance, retained collision/glare/structure/Foam protections and the fact that a flat/near-horizontal path is not physically invalid Oil. Do not couple Spatial to the merged P2 semantics unless new interaction evidence requires it. Once the single-frame production observation layer is stabilized, run the separately owned offline temporal trajectory probe for observed/estimated/unavailable result reconstruction. S12 UI/UX refinement remains separate.