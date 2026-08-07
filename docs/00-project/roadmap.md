# Project Roadmap

**Status:** `ACTIVE`

This document is the long-term milestone SSOT. It owns milestone order, scope and state. Exact branch progress, findings and immediate next action belong only in the [current work plan](work-plan.md).

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
- **Detail:** [Golden video regression](../30-validation/golden-video-regression.md)

### S2 — UI raster boundary architecture

- **Purpose:** Remove direct raster-library ownership from the Qt presentation layer.
- **Status:** `DONE`
- **Major result:** Raster conversion/rendering responsibilities moved behind presentation and adapter boundaries; temporary allowlist removed.
- **Next gate:** Maintain the import boundary in all subsequent UI work.
- **Detail:** [Historical implementation decision record](../90-archive/implementation-decisions.md)

### S3 — Workbench usability stabilization

- **Purpose:** Resolve real-use layout, terminology, wheel-input and preflight usability issues.
- **Status:** `DONE`
- **Major result:** Stable progress layout, larger video workspace, consistent Glass/analysis-area wording, wheel-safe controls and modeless preflight.
- **Next gate:** Preserve the accepted Workbench usability behavior in any post-S10 successor UI work.
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S4 — Analysis lifecycle and result visualization

- **Purpose:** Make long analysis progress and result graphs accurate and understandable.
- **Status:** `DONE`
- **Major result:** Stage-based progress, Korean Matplotlib font handling, user-facing oil-level terminology and full-analysis-area graph bounds.
- **Next gate:** Preserve the accepted analysis lifecycle, graph and resource-cleanup behavior in any post-S10 successor work.
- **Detail:** [Real-world validation plan](../30-validation/real-world-validation-plan.md)

### S5-A — Foam and shimmer discrimination

- **Purpose:** Separate real bottom-connected Foam from transparent-oil agitation and refractive shimmer.
- **Status:** `DONE`
- **Major result:** Multi-evidence Foam classification, glare handling and bounded temporal persistence without a GPU/model dependency.
- **Next gate:** Preserve Foam/shimmer discrimination as a non-regression contract in any post-S10 detector work.
- **Detail:** [Real-world validation plan](../30-validation/real-world-validation-plan.md), [manual checklist](../40-operations/manual-gui-windows-checklist.md)

### S5-B — Oil-boundary hypothesis architecture

- **Purpose:** Replace brittle candidate/static suppression with typed, evidence-preserving boundary and no-interface hypotheses plus bounded temporal reasoning.
- **Status:** `DONE`
- **Major result:** Typed observability and canonical ambiguity now separate latent physical oil truth from detector-identifiable evidence. One serialized temporal owner preserves atomic state, S5-A Foam independence and external compatibility; final deterministic comparison passed the `1.5×` CPU limit.
- **Next gate:** Preserve the merged observability, temporal and Foam contracts in any post-S10 detector or validation work.
- **Detail:** [Current work plan](work-plan.md), [S5-B architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)

### S5-C — Canonical/Qt validation stabilization

- **Purpose:** Stabilize `QApplication` / `QCoreApplication` ownership, isolate GUI fixtures, slim duplicate GUI/canonical coverage and preserve the non-GUI/headless validation contract.
- **Status:** `DONE`
- **Major result:** One session-owned pytest-qt `QApplication`, temporary offscreen platform injection, bounded Qt-state verification and explicit source-tree headless subprocess isolation now keep canonical and focused validation deterministic without changing production or detector behavior.
- **Next gate:** Preserve the accepted lifecycle/headless boundaries and S10 portability refinements in any post-S10 validation work.
- **Detail:** [Current work plan](work-plan.md), [Real-world validation plan](../30-validation/real-world-validation-plan.md)

### S6 — Real-video and runtime validation

- **Purpose:** Qualify the stabilized detector and application against the available real-video corpus and bounded/long-duration source-tree runtime evidence.
- **Status:** `DONE`
- **Major result:** Real-video qualification, user-confirmed truth, the audited S6-D4 available-corpus accuracy repair, bounded soak screening and one-hour macOS runtime stability are accepted. Missing field categories remain residual `not_evaluated` risk; no category-balanced or general-field detector-accuracy PASS is claimed.
- **Next gate:** Preserve the accepted real-video/runtime evidence and residual `not_evaluated` category boundary in any post-S10 detector work.
- **Detail:** [Current work plan](work-plan.md), [Real-world validation plan](../30-validation/real-world-validation-plan.md)

### S7 / Phase 2C-4 — Annotated MP4 Export

- **Purpose:** Render approved Result Review overlays onto the source video and export a shareable annotated MP4, with a general-user preset and an option to include debug information.
- **Status:** `DONE`
- **Major result:** PR #68 was fresh exact-head audited and native guarded-squash-merged as `8846c272842df099f5849ea71686c3370248fc03`. Selected-Glass MP4 export reuses official saved Result Review query/overlay semantics, fails closed when the saved interval lacks cadence-plausible sequential decoded coverage, keeps optional debug trace subordinate to official truth, and publishes only finalized temporary output through atomic replacement with bounded cancellation/resource cleanup.
- **Next gate:** Preserve the accepted S7 stored-result, decoded-timeline, derivative-publication, lifecycle and UI raster-boundary contracts in any post-S10 successor work.
- **Priority:** `P0 — completed`
- **Detail:** [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

### S8 — Repeated-Test Workflow & Result Management

- **Purpose:** Reduce repeated compressor-test effort and operational mistakes when one Profile is reused across multiple test videos.
- **Status:** `DONE`
- **Major result:** S8-A/B1/B2/C1 are accepted and merged through PR #69–#72, and presentation-only S8-C2 passed its Lane B Orchestrator exact-head gate and native guarded-squash-merged through PR #73 as `e90310a63faad2a20561ba0d5221432cc1e1c4fb`. Repeated same-Profile use now has explicit run identity/output naming, persistent recent Result/Profile access, finalized-run completion summary/actions, and clear Workbench separation of reusable Profile settings from current-test session settings without changing their established authorities.
- **Next gate:** Preserve the accepted S8 Profile/Result workflow authorities in any post-S10 successor work.
- **Priority:** `P1 — completed`
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S9 — Operational Recovery & UX Polish

- **Purpose:** Complete the selected high-impact Workbench interaction improvements after the S9-A data-loss guard while deferring lower-value recovery work.
- **Status:** `DONE`
- **Major result:** S9-A protects unsaved Profile changes on application close; S9-B adds presentation-only Fit/zoom/pan/100% while preserving canonical scene geometry; S9-C adds bidirectional field↔overlay active-target feedback and restrained ellipse resize affordances without changing Profile/session persistence or the axis-aligned eight-direction resize contract. Autosave/abnormal-exit recovery remains `DEFERRED`, is routed through [retained commitments](retained-commitments.md), and is not the current gate.
- **Next gate:** Preserve the accepted S9 interaction and persistence boundaries in any post-S10 successor work.
- **Priority:** `P2 — completed`
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S10 — Windows and Packaging Final Release Gate

- **Purpose:** Validate the completed product feature set on the target Windows environment and prove the relocatable one-folder distribution before release.
- **Status:** `DONE`
- **Major result:** Exact-head Windows canonical validation passed with only privilege-limited symlink cases unavailable, and the supported-DPI GUI, one-folder build/relocation, clean-PC, resources/fonts, Unicode/long-path and lifecycle/file-lock package obligations were completed. The post-S10 Qt platform bootstrap repair is also accepted maintenance evidence.
- **Next gate:** Preserve the accepted platform/package baseline while S11 addresses detector effectiveness.
- **Detail:** [Real-world validation plan](../30-validation/real-world-validation-plan.md), [manual Windows checklist](../40-operations/manual-gui-windows-checklist.md), [S10 evidence](../60-evidence/s10/)

### S11 — Real-Field Detector Effectiveness Recovery

- **Purpose:** Recover reliable Oil-boundary detection and tracking on field-representative sight-glass video where a human can identify usable Oil evidence, without weakening accepted glare/structure/Foam/no-interface safety contracts.
- **Status:** `ACTIVE`
- **Major result:** The accepted S11 current-frame and serialized temporal detector baseline is stable for sequencing purposes. S11-B, D1–D5, comparative-anchor authority repair and bounded ambiguity-gated reacquisition preserve the accepted fail-closed detector contracts; further detector source tuning is no longer the current gate.
- **Next gate:** **Lane C — Initial-State Retrospective FULL/EMPTY Reconstruction implementation** from the documented sequence-level architecture and validation contract. This responsibility changes shared analysis workflow, official event/judgment/coverage semantics and versioned result compatibility while remaining downstream of immutable detector observation. Final Windows field-workflow validation remains later, and S11 closure remains unapproved.
- **Priority:** `P0`
- **Detail:** [current work plan](work-plan.md), [durable S11 detector architecture](../20-architecture/s11-detector-responsibility-architecture.md), [retrospective reconstruction architecture](../20-architecture/initial-state-retrospective-reconstruction-architecture.md), [retrospective validation contract](../30-validation/initial-state-retrospective-reconstruction-validation.md)

### S12 — Post-S10 UI/UX Refinement

- **Purpose:** Address remaining real-use Workbench/setup/review friction after detector effectiveness is restored, while preserving established Profile/session/result and S9 interaction authorities.
- **Status:** `PLANNED`
- **Major result:** Scope is intentionally not fixed yet; real-use friction and the existing P3 UX backlog remain candidate inputs rather than authorized implementation slices.
- **Next gate:** Reclassify and slice UI/UX work only after the active S11 retrospective reconstruction responsibility and later field-workflow closure gate have completed, so S11 official result semantics are stable.
- **Priority:** `P1`
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

## Current sequence

`S6 DONE` → `S7 / Phase 2C-4 DONE` → `S8 DONE` → `S9 DONE` → `S10 DONE` → `S11 ACTIVE` → `S12 PLANNED`.

Affirmatively retained but non-current work, including autosave/abnormal-exit recovery, evidence-gated trajectory provenance responsibility and the final post-reconstruction Windows field-workflow check, is routed only through [`retained-commitments.md`](retained-commitments.md). Initial-State Retrospective FULL/EMPTY Reconstruction is active S11 work and is therefore not retained here.
