# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S10 — Windows and Packaging Final Release Gate`
**Milestone status:** `ACTIVE — product feature work through S9 is closed; final platform/package acceptance pending`
**Current S9 result:** `DONE — S9-A/S9-B/S9-C accepted and merged through PR #74–#76`
**Current gate:** `S10 — Windows and Packaging Final Release Gate`

This document owns the current execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S9 is complete: S9-A protects unsaved Profile changes on accepted application close, S9-B provides presentation-only Fit/zoom/pan/100% view state, and S9-C provides bidirectional field↔overlay active-target feedback plus restrained ellipse resize affordances. Profile/session persistence, canonical source-scene geometry, S9-B view transforms and the eight-direction resize contract remain unchanged.

S10 is validation/packaging work, not a claim that Windows acceptance has already occurred. Windows canonical tests, supported-DPI manual GUI, PyInstaller one-folder build/relocation, clean-PC execution, resource/font resolution, Unicode/long-path handling and cancellation/application-close file-handle cleanup remain pending until directly exercised on Windows.

## Current evidence owners

- Product/UX contract: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)
- S9-C implementation evidence: [`../30-quality/s9-c-field-overlay-interaction-polish-evidence.md`](../30-quality/s9-c-field-overlay-interaction-polish-evidence.md)
- Final platform contract: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)
- Manual Windows/DPI procedure: [`../30-quality/manual-gui-windows-checklist.md`](../30-quality/manual-gui-windows-checklist.md)
- Packaging procedure/entry points remain repository-owned and must be inspected before execution.

## Latest recorded closeout — S9-C Field ↔ Overlay Interaction Polish

| Item | Current state |
|---|---|
| Gate target | PR #76; exact base `9b2f4b79a1f24fb379b256bef66554dca56af915`; exact feature head `2bff8819a9b4e337cdbeb66f4220e9552316b69a`; 1 commit / exactly 10 changed files; Lane B |
| Interaction authority | `MainWindow` owns transient selected-Glass + target-kind + optional exclusion-id presentation state. It is not Recipe/session/result/dirty/undo/readiness/detector authority. |
| Bidirectional contract | Settings geometry/zero-line/margin/exclusion context highlights the matching overlay; ellipse/zero-line/exclusion interaction reveals the corresponding field/group with exact exclusion identity. |
| Visual polish | Selected ellipse keeps all eight resize directions, minimum size, frame bounds and source-scene accuracy while using smaller circular markers with a larger transform-independent hit target and stronger active-handle feedback. || Validation coexistence | Existing validation-state styling/routing remains independent from interaction-target styling. Rebuild/reconciliation preserves valid active targets and clears stale Glass/exclusion context. |
| Fresh Orchestrator gate | Exact-head S9-C/UI/shared-canvas targeted suite: `33 passed in 5.82s`, exit code 0; changed-document relative links `41/41` passed; complete-PR `git diff --check` passed. |
| Merge / synchronization | PR #76 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `953200a7641115a3f2eddcb9b4a7f9ac6cc21b0b`; registered primary checkout synchronized cleanly to `main` at that SHA before this documentation Close. |
| Claim boundary | Windows/manual GUI, Windows DPI, PyInstaller, clean-PC packaging, detector benchmark, soak/long-duration, unrelated canonical/E2E and autosave/recovery remain unclaimed. |
| Next gate | `S10 — Windows and Packaging Final Release Gate`. |

## S10 acceptance contract

S10 must directly prove, on the target Windows environment:

- the repository canonical suite passes on supported Windows Python 3.14;
- Workbench, preflight, analysis and Result Review complete the manual checklist at 100%, 125% and 150% DPI;
- S9-B zoom/pan/fit and S9-C field↔overlay/handle behavior remain usable at those DPI settings;
- the PyInstaller one-folder distribution builds successfully and runs after relocation;
- a clean Windows PC without Python or separately bundled font files can run the packaged workflow;
- Jinja, Qt, OpenCV and Matplotlib resources resolve after relocation and Korean UI/graph fonts behave correctly;
- Unicode/long paths and active file-locking conditions are exercised;
- cancellation and application close release video/output/debug handles without orphaned work.

Every item not directly executed remains `PENDING`/`NOT RUN`; no result may be inferred from macOS/source-tree evidence.

## Current risks

- Existing residual real-video category gaps remain governed by the real-world validation plan and are not reopened automatically by S10.
- Autosave/abnormal-exit recovery remains deferred to post-S10 reassessment and is not a release prerequisite for S10.
- Any source defect discovered by Windows/package validation returns to the appropriate bounded source lane; validation must not silently repair source and continue claiming the same evidence chain.

## Next action

Start the S10 Windows/platform validation handoff from authoritative synchronized `main`. The validation owner must first inspect repository-owned packaging and Windows procedures, fix exact release-candidate identity, then execute only the platform/package acceptance available on the actual Windows environment. If the required Windows/clean-PC environment is unavailable, report the exact unavailable evidence rather than substituting macOS results.