# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE — post-S10 field diagnosis and acceptance planning`
**Current gate:** `S11-A — Real-field failure attribution and truth/corpus planning`

S10 is closed. S11 is now the P0 successor because a Windows field run on a visually usable compressor video showed severe detector effectiveness failure despite the accepted platform/package baseline. No detector source change is authorized until the failure stage and truth/evidence contract are established.

## Current evidence owners

- Detector/field acceptance: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- S11 diagnostic evidence and plan: [`../30-quality/s11-real-field-detector-effectiveness-plan.md`](../30-quality/s11-real-field-detector-effectiveness-plan.md)
- Benchmark/truth workflow: [`../30-quality/golden-video-regression.md`](../30-quality/golden-video-regression.md)
- S5-B observability/temporal architecture: [`../20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Post-S10 UX authority: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)

## Latest recorded closeout — Post-S10 Windows Qt Platform Bootstrap Maintenance

PR #78 exact base `f52e477e71f562744ccb27846c9248a8b46fb310` / exact head `0805ebf4620b43934198bc16dfb1e49407fe91b2` passed Lane C Fresh Exact-Head Audit and native guarded-squash-merged as `bd6f478699563874439a533a5442b8fb23fdf9f7`. The bounded 10-file packaging/tests/docs repair adds a Windows-only PyInstaller runtime hook that forces native `QT_QPA_PLATFORM=windows` before PySide6 runtime initialization; source-tree GUI, CLI/headless behavior and S11 detector source remain unchanged. Auditor Mac focused validation passed `34` tests; exact-head Windows focused tests passed `14`, the clean one-folder build passed, and both no-env and inherited-`offscreen` packaged launches produced a native visible GUI with normal close/process termination. No S10 milestone reopening or S11 scope change occurred; current gate remains `S11-A — Real-field failure attribution and truth/corpus planning`.

## S11 current diagnosis

- A 1280×720 / 30 fps Windows field video was analyzed over 480–1200 s with two Glasses using identical detector settings.
- Base produced no numeric Oil detections and remained mainly `UNKNOWN_REVIEW`; Accum produced only sparse numeric detections and was dominated by no-interface states.
- At a visually clear Base frame, Canny/hypothesis geometry contained a plausible boundary near the reference line, but boundary evidence lost to ambiguity/no-interface competition and the tracker received `NO_UPDATE`.
- At dark Accum frames, high uniformity/no-interface evidence dominated despite a visually reported Oil boundary; numeric detections appeared only when lighting changed and no-interface evidence collapsed.
- These observations are diagnostic evidence, not authoritative detector-accuracy truth. Exact physical fill labels and coordinate conventions must be reconciled through the existing user-truth workflow before acceptance claims.

## Next action

Start S11-A with the same field video as local/private evidence: freeze representative clear, dark, occluded and successful-detection frames/sequences; establish user-confirmed truth where usable; trace candidate → hypothesis → canonical decision → temporal action; then classify the smallest justified detector repair. Preserve S5-A Foam and S5-B fail-closed contracts unless direct evidence proves a separately authorized architecture change is required. S12 UI/UX refinement remains a separate P1 successor and does not begin inside S11.