# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — reproducible-corpus detector architecture probing`
**Current gate:** `S11-A — OpenCV evidence redesign and controlled experiment planning`

S10 is closed. S11 is now the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. No detector source change is authorized until the failure stage and truth/evidence contract are established.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- S11-A detector direction/experiment decision: [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — Post-S10 Windows Qt Platform Bootstrap Maintenance

PR #78 exact base `f52e477e71f562744ccb27846c9248a8b46fb310` / exact head `0805ebf4620b43934198bc16dfb1e49407fe91b2` passed Lane C Fresh Exact-Head Audit and native guarded-squash-merged as `bd6f478699563874439a533a5442b8fb23fdf9f7`. The bounded 10-file packaging/tests/docs repair adds a Windows-only PyInstaller runtime hook that forces native `QT_QPA_PLATFORM=windows` before PySide6 runtime initialization; source-tree GUI, CLI/headless behavior and S11 detector source remain unchanged. Auditor Mac focused validation passed `34` tests; exact-head Windows focused tests passed `14`, the clean one-folder build passed, and both no-env and inherited-`offscreen` packaged launches produced a native visible GUI with normal close/process termination. No S10 milestone reopening or S11 scope change occurred. The current gate has since advanced to `S11-A — OpenCV evidence redesign and controlled experiment planning` after the post-S10 field diagnosis was reproduced as a general exposure-sensitivity failure class on the local S6 corpus.

## S11 current diagnosis

- A 1280×720 / 30 fps Windows field video was analyzed over 480–1200 s with two Glasses using identical detector settings.
- Base produced no numeric Oil detections and remained mainly `UNKNOWN_REVIEW`; Accum produced only sparse numeric detections and was dominated by no-interface states.
- At a visually clear Base frame, Canny/hypothesis geometry contained a plausible boundary near the reference line, but boundary evidence lost to ambiguity/no-interface competition and the tracker received `NO_UPDATE`.
- At dark Accum frames, high uniformity/no-interface evidence dominated despite a visually reported Oil boundary; numeric detections appeared only when lighting changed and no-interface evidence collapsed.
- These observations are diagnostic evidence, not authoritative detector-accuracy truth. Source inspection resolved the detector/product source-frame Y convention, and the private field video is not a repeatable S11 development corpus.
- Repository-local truth-positive frames reproduce the same exposure-sensitivity class under controlled brightness changes: valid Oil can become ambiguous or false no-interface as absolute photometric evidence weakens.
- External transparent-vessel vision literature and local probes support relative/local photometric phase evidence as the first redesign target; OpenCV remains the selected production primitive stack.

## Next action

Run the S11-A architecture probe defined in [`../30-quality/s11-a-detector-direction-and-experiment-plan.md`](../30-quality/s11-a-detector-direction-and-experiment-plan.md): compare `P0` current behavior against `P1` relative/local phase evidence, `P2` exposure-decoupled no-interface evidence and `P3` combined behavior on the frozen S6 truth plus controlled brightness/gamma/contrast variants. Preserve S5-A Foam, S5-B fail-closed ambiguity, structural/rim/glare negatives and bounded resources. Select the smallest sufficient source repair only after that comparison; provisional source classification is Lane C. S12 UI/UX refinement remains a separate P1 successor.