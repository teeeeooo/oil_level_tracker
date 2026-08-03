# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S9 — Operational Recovery & UX Polish`
**Milestone status:** `ACTIVE — S9-A and S9-B closed; S9-C selected next`
**Current S9-A result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #74`
**Current S9-B result:** `ORCHESTRATOR EXACT-HEAD GATE PASS; NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #75 @ 4138763db5d6b0f25d1f69b058815825662a1d94`
**Current gate:** `S9-C — Field ↔ Overlay Interaction Polish Worker`
**Successor milestone:** `S10 — Windows and Packaging Final Release Gate`

This document owns the current execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S9-A remains closed against its accepted Profile dirty/save/close lifecycle. S9-B passed the Lane B Orchestrator exact-head gate and merged through PR #75; Workbench Fit/zoom/pan/100% is presentation-only view state, canonical Recipe geometry remains source-frame / `QGraphicsScene` state, same-context frame changes preserve manual view state, and actual video/Profile context replacement resets to Fit. Shared ROI editor and preview consumers retain their established ownership. S9-C is the selected final S9 slice. Autosave/abnormal-exit recovery remains deferred to post-S10 reassessment. Windows/manual GUI, Windows DPI and PyInstaller acceptance remain pending and unclaimed until S10.

## Current evidence owners

- Product UX contract: [`../10-product/ux-improvement-plan.md`](../10-product/ux-improvement-plan.md)
- S9-A close-guard evidence: [`../30-quality/s9-a-unsaved-profile-close-guard-evidence.md`](../30-quality/s9-a-unsaved-profile-close-guard-evidence.md)
- S9-B zoom/pan/fit evidence: [`../30-quality/s9-b-workbench-zoom-pan-fit-evidence.md`](../30-quality/s9-b-workbench-zoom-pan-fit-evidence.md)
- Windows/manual acceptance: [`../30-quality/manual-gui-windows-checklist.md`](../30-quality/manual-gui-windows-checklist.md)
- Retained real-world validation obligations: [`../30-quality/real-world-validation-plan.md`](../30-quality/real-world-validation-plan.md)

## Latest recorded closeout — S9-B Workbench Analysis-Area Zoom, Pan & Fit

| Item | Current state |
|---|---|
| Gate target | PR #75; exact base `80b65298b1ac7948cd3d6c54fa77396afb9d7857`; exact feature head `662ea73f4f6c9813909cc1fa487b41357bf03bbc`; 1 commit / exactly 11 changed files; Lane B |
| View-state authority | Fit/zoom/pan/100% is ephemeral `VideoOverlayCanvas` presentation state only. `InspectionRecipe`, `AnalysisSession`, `.oilrecipe`, Result Bundle, Profile dirty truth, undo/redo, readiness/preflight and detector state remain unchanged. |
| Interaction contract | Explicit `확대`/`축소`/`맞춤`/`100%`, canvas `Ctrl`+wheel zoom and middle-button pan coexist with existing left-button geometry editing. Fit follows viewport resizing; manual view state survives same-context frame and viewport changes. |
| Context boundary | Normal video replacement, new/load/placeholder transitions and same-Profile new-video replacement reset to Fit. Shared preview resets for a new video while retaining manual view across frames of the same video. |
| Geometry/shared-consumer preservation | Ellipse move/eight-direction resize, zero line, exclusion geometry and Glass selection remain scene-coordinate operations. Focused ROI editor private-copy semantics and shared preview behavior remain intact; no Result Review zoom architecture was introduced. |
| Fresh Orchestrator gate | Exact-head targeted S9-B/shared-consumer/UI-boundary suite: `29 passed in 4.65s`, exit code 0; complete branch `git diff --check` passed. |
| Merge / synchronization | PR #75 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `4138763db5d6b0f25d1f69b058815825662a1d94`; registered primary checkout synchronized cleanly to `main` at that SHA before this documentation Close. |
| Claim boundary | Detector benchmarks, soak/long-duration, Windows/manual GUI, Windows DPI, PyInstaller, unrelated canonical/E2E, Result Review zoom, S9-C highlight/ellipse-handle polish and autosave/recovery remain unclaimed. |
| Next gate | `S9-C — Field ↔ Overlay Interaction Polish Worker`. |

## Current S9-C contract

S9-C reduces ambiguity about what the user is editing while preserving existing Profile/session and geometry authorities.

- Field → overlay: geometry fields highlight the ellipse; zero-line fields highlight the zero line; margin fields highlight the inner margin; exclusion fields highlight the corresponding exclusion overlay.
- Overlay → field: ellipse, zero-line and exclusion interaction highlights the corresponding field/group and makes the relevant exclusion editor visible when necessary.
- Selected-Glass state and active editing-target highlight remain visually distinct.
- Ellipse visual polish keeps axis-aligned eight-direction resize, minimum size and frame bounds, but replaces the visually heavy always-prominent square-handle treatment with restrained context-sensitive affordances while preserving practical hit targets and resize usability.
- S9-C must not turn highlight state into persisted Recipe/session data or create a second geometry authority.

## Current risks and final release obligation

- Autosave/abnormal-exit recovery is deferred to post-S10 reassessment and is not an S9 release prerequisite.
- Existing real-video category gaps and accepted S6 runtime claim boundaries remain governed by the linked real-world validation plan; no broader detector-accuracy or runtime claim is added by S9-B.
- S10 remains mandatory after S9-C: run the Windows Python 3.14 canonical suite, supported-DPI manual Workbench/preflight/analysis/Result Review flow, PyInstaller one-folder build/relocation, clean-PC execution, Korean font/resource checks, Unicode/long paths, cancellation/application close and file-handle release checks.
- Do not infer Windows/manual/package PASS from macOS or source-tree evidence.

## Next action

Start a focused `S9-C — Field ↔ Overlay Interaction Polish Worker` handoff from authoritative synchronized `main`. S9-C is the final selected S9 slice; after its accepted merge and Close, transition to S10 rather than automatically reopening autosave/recovery.
