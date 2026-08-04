# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — spatial current-frame detector architecture probing`
**Current gate:** `S11-A — Spatial Path / cross-ROI consistency probe`

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
- The next selected detection question is whether cross-ROI spatial path/curve consistency supplies genuinely new positive current-frame evidence while preserving S5-B collision, glare, structure and Foam protections.
- Offline temporal trajectory estimation remains a separate result-estimation successor after spatial observation recovery; S12 stays separate.

## Next action

Run the bounded S11-A Spatial Path / cross-ROI consistency probe defined by [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md). Test whether current-frame spatial coherence can recover residual Oil misses without weakening S5-B fail-closed collision semantics, glare/structure/Foam protection or bounded resources. Keep P2 as a separate Lane C production no-interface repair candidate and keep offline temporal trajectory estimation as a later result-estimation probe. S12 UI/UX refinement remains separate.