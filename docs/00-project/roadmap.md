# Project Roadmap

**Status:** `ACTIVE`

This document is the long-term milestone SSOT. It owns milestone order, scope and state. Exact branch progress, findings and immediate next action belong only in the [current work plan](./work-plan.md).

The roadmap is a bounded current-state document, not a cumulative journal. Keep exactly one current entry per milestone and update that entry in place. Historical status transitions and detailed change history belong to Git history.

## Status rules

Allowed values are `PLANNED`, `ACTIVE`, `BLOCKED`, `VALIDATING`, `DONE`, `DEFERRED` and `SUPERSEDED`. `DONE` means implementation, required validation and merge are complete.

## Replacement and compaction rules

- Maintain one current item per milestone; replace its status, major result and next gate in place.
- Do not add Worker or Auditor commits, individual closeouts, test counts, temporary findings or validation logs.
- Compress completed milestones to purpose, formal status, major result, maintenance gate and detail links.
- Remove obsolete wording when a milestone changes instead of preserving prior states below the current item.
- Use architecture, quality or product documents for detailed contracts and evidence; use Git history for past roadmap text.
- Do not create a roadmap history section.

## Milestones

### Phase 1 — Guided Workbench UX

- **Purpose:** Reduce setup complexity and make geometry/configuration edits recoverable.
- **Status:** `DONE`
- **Major result:** Basic/advanced settings separation, focused analysis-area editing, fixed execution controls, undo/redo and field-level validation.
- **Next gate:** Retain compatibility while later UX stabilization changes are made.
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### Phase 2A — Pre-analysis readiness

- **Purpose:** Establish configuration readiness, multi-frame preflight and reusable Glass settings.
- **Status:** `DONE`
- **Major result:** Readiness feedback, representative-timestamp checks and atomic settings copy.
- **Next gate:** Preserve readiness and preflight behavior through detector changes.
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### Phase 2B — Result Review Viewer

- **Purpose:** Review stored analysis results against the source video without mutating the official bundle.
- **Status:** `DONE`
- **Major result:** Viewer MVP, interactive graph, review filters, safe asset actions and same-profile follow-up workflow.
- **Next gate:** Preserve bundle compatibility and review lifecycle during later changes.
- **Detail:** [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

### Phase 2C-1 to 2C-3 — Debug, re-detection and truth

- **Purpose:** Make detector failures inspectable, comparable and exportable as regression truth.
- **Status:** `DONE`
- **Major result:** Debug Viewer, partial re-detection, settings comparison, external user truth and deterministic fixture export.
- **Next gate:** Use the resulting evidence path for detector stabilization and validation.
- **Detail:** [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

### S1 — Detector benchmark foundation

- **Purpose:** Evaluate the current detector repeatably against exported regression fixtures.
- **Status:** `DONE`
- **Major result:** Safe dataset reader, headless benchmark runner, category metrics, fingerprints and baseline comparison.
- **Next gate:** Reuse the same dataset and metric semantics for detector deltas.
- **Detail:** [Golden video regression](../30-quality/golden-video-regression.md)

### S2 — UI raster boundary architecture

- **Purpose:** Remove direct raster-library ownership from the Qt presentation layer.
- **Status:** `DONE`
- **Major result:** Raster conversion/rendering responsibilities moved behind presentation and adapter boundaries; temporary allowlist removed.
- **Next gate:** Maintain the import boundary in all subsequent UI work.
- **Detail:** [Implementation decisions](../20-architecture/implementation-decisions.md)

### S3 — Workbench usability stabilization

- **Purpose:** Resolve real-use layout, terminology, wheel-input and preflight usability issues.
- **Status:** `DONE`
- **Major result:** Stable progress layout, larger video workspace, consistent Glass/analysis-area wording, wheel-safe controls and modeless preflight.
- **Next gate:** Confirm the behavior in the final Windows/manual release gate after the product feature sequence is complete.
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S4 — Analysis lifecycle and result visualization

- **Purpose:** Make long analysis progress and result graphs accurate and understandable.
- **Status:** `DONE`
- **Major result:** Stage-based progress, Korean Matplotlib font handling, user-facing oil-level terminology and full-analysis-area graph bounds.
- **Next gate:** Preserve the accepted real-video/runtime evidence and revalidate lifecycle, graph, DPI and resource cleanup in the final Windows/manual release gate.
- **Detail:** [Real-world validation plan](../30-quality/real-world-validation-plan.md)

### S5-A — Foam and shimmer discrimination

- **Purpose:** Separate real bottom-connected Foam from transparent-oil agitation and refractive shimmer.
- **Status:** `DONE`
- **Major result:** Multi-evidence Foam classification, glare handling and bounded temporal persistence without a GPU/model dependency.
- **Next gate:** Preserve Foam non-regression while replacing the oil-boundary architecture.
- **Detail:** [Real-world validation plan](../30-quality/real-world-validation-plan.md), [manual checklist](../30-quality/manual-gui-windows-checklist.md)

### S5-B — Oil-boundary hypothesis architecture

- **Purpose:** Replace brittle candidate/static suppression with typed, evidence-preserving boundary and no-interface hypotheses plus bounded temporal reasoning.
- **Status:** `DONE`
- **Major result:** Typed observability and canonical ambiguity now separate latent physical oil truth from detector-identifiable evidence. One serialized temporal owner preserves atomic state, S5-A Foam independence and external compatibility; final deterministic comparison passed the `1.5×` CPU limit.
- **Next gate:** Preserve the merged observability, temporal and Foam contracts through S5-C stabilization, accepted S6 real-video/runtime validation and the later final Windows release gate.
- **Detail:** [Current work plan](./work-plan.md), [S5-B architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)

### S5-C — Canonical/Qt validation stabilization

- **Purpose:** Stabilize `QApplication` / `QCoreApplication` ownership, isolate GUI fixtures, slim duplicate GUI/canonical coverage and preserve the non-GUI/headless validation contract.
- **Status:** `DONE`
- **Major result:** One session-owned pytest-qt `QApplication`, temporary offscreen platform injection, bounded Qt-state verification and explicit source-tree headless subprocess isolation now keep canonical and focused validation deterministic without changing production or detector behavior.
- **Next gate:** Preserve the accepted lifecycle and headless boundaries through S6 real-video/runtime validation, subsequent product work and the final Windows/packaging release gate.
- **Detail:** [Current work plan](./work-plan.md), [Real-world validation plan](../30-quality/real-world-validation-plan.md)

### S6 — Real-video and runtime validation

- **Purpose:** Qualify the stabilized detector and application against the available real-video corpus and bounded/long-duration source-tree runtime evidence.
- **Status:** `DONE`
- **Major result:** Real-video qualification, user-confirmed truth, the audited S6-D4 available-corpus accuracy repair, bounded soak screening and one-hour macOS runtime stability are accepted. Missing field categories remain residual `not_evaluated` risk; no category-balanced or general-field detector-accuracy PASS is claimed.
- **Next gate:** `S7 / Phase 2C-4 — Annotated MP4 Export`. Windows/manual GUI and one-folder packaging validation remain mandatory but move to the final release gate after the product feature sequence.
- **Detail:** [Current work plan](./work-plan.md), [Real-world validation plan](../30-quality/real-world-validation-plan.md)

### S7 / Phase 2C-4 — Annotated MP4 Export

- **Purpose:** Render approved Result Review overlays onto the source video and export a shareable annotated MP4, with a general-user preset and an option to include debug information.
- **Status:** `DONE`
- **Major result:** PR #68 was fresh exact-head audited and native guarded-squash-merged as `8846c272842df099f5849ea71686c3370248fc03`. Selected-Glass MP4 export reuses official saved Result Review query/overlay semantics, fails closed when the saved interval lacks cadence-plausible sequential decoded coverage, keeps optional debug trace subordinate to official truth, and publishes only finalized temporary output through atomic replacement with bounded cancellation/resource cleanup.
- **Next gate:** Preserve the accepted S7 stored-result, decoded-timeline, derivative-publication, lifecycle and UI raster-boundary contracts through successor work and the final S10 Windows/packaging release gate.
- **Priority:** `P0 — completed`
- **Detail:** [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

### S8 — Repeated-Test Workflow & Result Management

- **Purpose:** Reduce repeated compressor-test effort and operational mistakes when one Profile is reused across multiple test videos.
- **Status:** `PLANNED`
- **Major result:** The P1 candidate scope is prioritized: repeated analysis with one Profile, improved output naming, recent profile/result management, final run summary and completion actions, and clearer visual separation of profile-owned versus current-test settings. Implementation has not started.
- **Next gate:** Select and authorize one bounded S8 implementation slice from this P1 scope; implementation remains not started until that handoff.
- **Priority:** `P1 — repeated-test productivity / current next gate`
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S9 — Operational Recovery & UX Polish

- **Purpose:** Select recovery and interaction improvements after S8 based on observed user impact rather than committing every candidate to release scope.
- **Status:** `PLANNED`
- **Major result:** P2 selection candidates are autosave/abnormal-exit recovery, unsaved-change confirmation on close, analysis-area zoom/pan/fit, and field↔overlay bidirectional highlight. P3 remains a lower-priority backlog for enlarged reference-line drag guidance, keyboard geometry nudging, resize/modifier guidance and further Wizard/Workbench simplification.
- **Next gate:** After S8, select only the P2 work justified by real-use effect; P3 is not a mandatory release prerequisite unless explicitly promoted later.
- **Priority:** `P2 selection gate / P3 backlog`
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S10 — Windows and Packaging Final Release Gate

- **Purpose:** Validate the completed product feature set on the target Windows environment and prove the relocatable one-folder distribution before release.
- **Status:** `PLANNED`
- **Major result:** Obligation is preserved and pending; no Windows/manual GUI/PyInstaller one-folder PASS is currently claimed.
- **Next gate:** After the required product feature work, run the Windows Python 3.14 canonical suite, supported-DPI manual Workbench/preflight/analysis/Result Review flow, Windows PyInstaller one-folder build, clean-PC execution without Python or separately bundled fonts, relocated Jinja/Qt/OpenCV/Matplotlib resource checks, Korean font behavior, Unicode/long paths, active file locking, cancellation/application close and video/output/debug handle-release checks.
- **Detail:** [Real-world validation plan](../30-quality/real-world-validation-plan.md), [manual checklist](../30-quality/manual-gui-windows-checklist.md)

## Current sequence

`S6 DONE` → `S7 / Phase 2C-4 DONE` → `S8 repeated-test workflow/result management` → `S9 selection/UX work` → `S10 final Windows & Packaging release gate`.
