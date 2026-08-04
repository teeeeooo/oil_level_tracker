# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — production detector recovery`
**Current gate:** `S11-B — P2 no-interface production repair`

S10 is closed. S11 is now the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. No detector source change is authorized until the failure stage and truth/evidence contract are established.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — Post-S10 Windows Qt Platform Bootstrap Maintenance

PR #78 exact base `f52e477e71f562744ccb27846c9248a8b46fb310` / exact head `0805ebf4620b43934198bc16dfb1e49407fe91b2` passed Lane C Fresh Exact-Head Audit and native guarded-squash-merged as `bd6f478699563874439a533a5442b8fb23fdf9f7`. The bounded 10-file packaging/tests/docs repair adds a Windows-only PyInstaller runtime hook that forces native `QT_QPA_PLATFORM=windows` before PySide6 runtime initialization; source-tree GUI, CLI/headless behavior and S11 detector source remain unchanged. Auditor Mac focused validation passed `34` tests; exact-head Windows focused tests passed `14`, the clean one-folder build passed, and both no-env and inherited-`offscreen` packaged launches produced a native visible GUI with normal close/process termination. No S10 milestone reopening or S11 scope change occurred. The S11-A P0/P1/P2/P3 evidence probe is now merged. It rejected P1/P3 because they violate the retained S5-B observational-equivalence collision contract, retained P2 as a separate no-interface production repair candidate, and advanced the current gate to a spatial current-frame consistency probe.

## S11 current diagnosis

- A 1280×720 / 30 fps Windows field video was analyzed over 480–1200 s with two Glasses using identical detector settings.
- Base produced no numeric Oil detections and remained mainly `UNKNOWN_REVIEW`; Accum produced only sparse numeric detections and was dominated by no-interface states.
- At a visually clear Base frame, Canny/hypothesis geometry contained a plausible boundary near the reference line, but boundary evidence lost to ambiguity/no-interface competition and the tracker received `NO_UPDATE`.
- At dark Accum frames, high uniformity/no-interface evidence dominated despite a visually reported Oil boundary; numeric detections appeared only when lighting changed and no-interface evidence collapsed.
- These observations are diagnostic evidence, not authoritative detector-accuracy truth. Source inspection resolved the detector/product source-frame Y convention, and the private field video is not a repeatable S11 development corpus.
- Repository-local truth-positive frames reproduce the same exposure-sensitivity class under controlled brightness changes: valid Oil can become ambiguous or false no-interface as absolute photometric evidence weakens.
- The completed P0/P1/P2/P3 probe showed that stronger scalar relative phase can recover some Oil but creates unsafe collision false Oil; P2 safely reduces exposure-driven false no-interface without recovering numeric Oil.
- The merged Spatial Path probe recovered two additional native Oil rows while preserving the retained collision/glare/structure/Foam protections in targeted evidence, establishing cross-ROI spatial information as a useful bounded positive-evidence direction.
- The spatial probe remains conservative and is not itself a production cutover: its non-degenerate-path gate must not be treated as a universal physical Oil discriminator, especially for valid near-horizontal surfaces.
- The merged P2 × Spatial interaction probe found no material numeric-recovery interaction: P2 converts known exposure-driven false no-interface to ambiguity, but those rescued frames expose no additional accepted Spatial candidate in the current reproducible evidence.
- P2 and Spatial therefore remain independent production candidates rather than one coupled recovery mechanism. P2 has the strongest direct field-failure justification; Spatial remains a conservative secondary positive-evidence fallback with a known near-horizontal-path limitation.
- Offline temporal trajectory estimation remains a separate result-estimation successor after the single-frame production observation layer is stabilized; S12 stays separate.

## Next action

Start S11 production recovery with the separate P2 no-interface repair under Lane C independent review. After P2 is accepted, design the conservative Spatial positive-evidence production fallback as a separate mutation, preserving P0-first acceptance and the fact that a flat/near-horizontal path is not physically invalid Oil. Once the single-frame production observation layer is stabilized, run the offline temporal trajectory probe for observed/estimated/unavailable result reconstruction. S12 UI/UX refinement remains separate.