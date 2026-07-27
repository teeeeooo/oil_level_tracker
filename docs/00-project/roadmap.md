# Project Roadmap

**Status:** `ACTIVE`

This document is the long-term milestone SSOT. It owns milestone order, scope and state. Exact branch progress, findings and immediate next action belong only in the [current work plan](./work-plan.md).

## Status rules

Allowed values are `PLANNED`, `ACTIVE`, `BLOCKED`, `VALIDATING`, `DONE`, `DEFERRED` and `SUPERSEDED`. `DONE` means implementation, required validation and merge are complete.

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
- **Next gate:** Confirm the behavior in the later Windows/manual validation gate.
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

### S4 — Analysis lifecycle and result visualization

- **Purpose:** Make long analysis progress and result graphs accurate and understandable.
- **Status:** `DONE`
- **Major result:** Stage-based progress, Korean Matplotlib font handling, user-facing oil-level terminology and full-analysis-area graph bounds.
- **Next gate:** Revalidate lifecycle, graph and resource cleanup with real video on Windows.
- **Detail:** [Real-world validation plan](../30-quality/real-world-validation-plan.md)

### S5-A — Foam and shimmer discrimination

- **Purpose:** Separate real bottom-connected Foam from transparent-oil agitation and refractive shimmer.
- **Status:** `DONE`
- **Major result:** Multi-evidence Foam classification, glare handling and bounded temporal persistence without a GPU/model dependency.
- **Next gate:** Preserve Foam non-regression while replacing the oil-boundary architecture.
- **Detail:** [Real-world validation plan](../30-quality/real-world-validation-plan.md), [manual checklist](../30-quality/manual-gui-windows-checklist.md)

### S5-B — Oil-boundary hypothesis architecture

- **Purpose:** Replace brittle candidate/static suppression with typed, evidence-preserving boundary and no-interface hypotheses plus bounded temporal reasoning.
- **Status:** `ACTIVE`
- **Major result:** Not yet complete. Prior narrow candidate/static suppression repairs exposed an architectural mismatch and are not completion evidence.
- **Next gate:** Pass an independent documentation and planning audit, then begin the S5-B1 shadow hypothesis pipeline.
- **Detail:** [Current work plan](./work-plan.md), [S5-B architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)

### S6 — Real-video and Windows validation gate

- **Purpose:** Qualify the stabilized detector and application on representative real video and the target Windows environment.
- **Status:** `PLANNED`
- **Major result:** None yet; this gate begins only after S5-B is complete.
- **Next gate:** Controlled benchmark comparison, real-video review, long-duration CPU/memory checks and one-folder validation must all pass.
- **Detail:** [Real-world validation plan](../30-quality/real-world-validation-plan.md), [manual checklist](../30-quality/manual-gui-windows-checklist.md)

### S7 / Phase 2C-4 — Annotated MP4 export

- **Purpose:** Export a shareable result video with approved overlays and optional debug information.
- **Status:** `PLANNED`
- **Major result:** Product and Viewer prerequisites exist; encoding work has not started.
- **Next gate:** Start only after the S6 validation gate passes.
- **Detail:** [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

### Phase 2D — Repeated-test operations and recovery

- **Purpose:** Reassess autosave, crash recovery, recent-work management and repeated-test workflow after real operational use.
- **Status:** `DEFERRED`
- **Major result:** Candidate scope is recorded but not committed to the active sequence.
- **Next gate:** Re-evaluate after S7 and sufficient real-use feedback; promote to `PLANNED` only through an explicit roadmap decision.
- **Detail:** [UX improvement plan](../10-product/ux-improvement-plan.md)

## Current sequence

`S5-B` → `S6` → `S7 / Phase 2C-4` → Phase 2D reassessment.