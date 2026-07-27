# UX Improvement Plan

## Authority and purpose

This document owns the user-facing workflow and acceptance contract for Workbench, preflight and follow-up UX improvements. It does not own project status or the current next action.

- Long-term milestone status: [project roadmap](../00-project/roadmap.md)
- Active gate and next action: [current work plan](../00-project/work-plan.md)
- Result Review detail: [Result Review Viewer plan](./result-review-viewer-plan.md)
- Manual Windows obligations: [manual GUI and Windows checklist](../30-quality/manual-gui-windows-checklist.md)

Historical PR heads and validation counts remain available in Git history rather than being repeated here.

## Product UX goal

A user without video-editing experience should be able to:

1. select a test video;
2. set the analysis time range;
3. configure each Glass and reference line;
4. check setup quality before analysis;
5. run analysis;
6. review report and video-overlay results;
7. inspect or export evidence for a problematic scene.

The experience must build three forms of confidence: setup confidence, pre-analysis confidence and post-analysis confidence.

## Guided Workbench contract

### Basic and advanced settings

Basic mode shows only frequent user decisions:

- Glass name and analysis inclusion;
- initial observation state;
- judgment mode;
- analysis-area editing and reference-line guidance;
- exclusion regions;
- optional real-length conversion.

Advanced mode retains geometry coordinates, mm/pixel details, margin and detector settings. Existing `.oilrecipe` compatibility is required.

### Focused analysis-area editing

- Edit ellipse, reference line and exclusion regions in a large focused view.
- Keep the source profile unchanged until Apply.
- Cancel restores the original state.
- Apply creates one undo operation.
- Geometry remains in source-frame coordinates and inside the frame.

### Fixed execution area and validation

The execution area remains visible and exposes setup status, validation, profile save and analysis execution. Field-level errors use adjacent Korean guidance and route the user to the affected Glass/input. Analysis remains disabled while readiness errors exist.

### Undo and redo

Ellipse, reference line, exclusion region and supported settings changes participate in `Ctrl+Z`/`Ctrl+Y`. A multi-target settings copy is one atomic operation and no-op changes do not dirty the document.

## Pre-analysis readiness contract

### Glass readiness

Each Glass displays one of: ready, review required, correction required or excluded, with the most important reason. Global session issues are not duplicated as every Glass's error.

The user can jump to the first error, otherwise the first warning. Selection, canvas, settings panel and focused field remain synchronized.

### Current-scene summary

The general UI shows only the final current-scene interpretation:

- fill state;
- confidence;
- oil level relative to the reference line;
- optional mm value;
- normal, review-required or failed state.

Candidate internals and scoring remain in debug surfaces.

### Multi-frame preflight

Representative timestamps include analysis start, compressor-start vicinity, interval quartiles and analysis end. The modeless window reports Glass/timestamp status, minimum confidence, missing candidate, abnormal jump and Foam/review evidence.

Selecting a row seeks the Workbench to that Glass/timestamp. Recipe, video, analysis-range, Glass or detector-setting changes mark prior results stale. Run/cancel/rerun and Workbench close must not leak signals, processes or file handles.

### Observation-window settings copy

- One source and multiple targets are supported.
- Identity, name, inclusion, center, reference line and exclusions remain target-owned.
- Judgment, detector, margin and initial state are copied by default.
- mm/pixel and ellipse size are explicit options.
- Mutable settings are deep-copied.
- Geometry compatibility is checked before any target changes.
- The full multi-target change is atomic and undoable.

## Result Review UX contract

After analysis, the user can open the source video and official bundle together, inspect the selected Glass overlay, navigate events/review intervals and synchronize video with the tracking graph. The Viewer remains read-only and uses result-bundle snapshots rather than current Workbench state.

General review hides candidate and score internals. Debug mode, partial re-detection, user truth and regression export follow the detailed [Result Review Viewer plan](./result-review-viewer-plan.md).

## Real-use Workbench stabilization contract

- Progress-step text remains single-line and unclipped at supported Windows DPI settings.
- The center video remains the primary Workbench area; transport controls never overlap it.
- User-facing `ROI` becomes `분석 영역`; `관찰창` becomes `Glass`; `oil-air` becomes `유면` or `유면 경계`; general UI uses `거품` for Foam.
- The current-scene card and Glass list share the left area without shrinking the video unnecessarily.
- Basic settings avoid awkward wrapped coordinate summaries.
- Wheel events scroll the settings panel instead of changing spin/combo values; keyboard/direct controls still edit values.
- Real-length conversion is visibly optional and does not warn when disabled.
- Foam guidance separates detector interpretation from recommended user action and never mutates initial state automatically.
- Multi-frame preflight is a modeless resizable window rather than a central-area-shrinking dock.

These requirements are verified through automated geometry/import tests where practical and the manual Windows checklist where platform interaction matters.

## Phase 2C feature contract

The post-analysis developer workflow supports:

- debug trace levels `none`, `basic` and `full`;
- candidate/evidence inspection without changing the official result;
- bounded current/short/full-range re-detection in temporary workspaces;
- official-versus-rerun comparison;
- explicit application to one/all Glasses or a new profile;
- external user truth separated from official results;
- deterministic regression fixture export;
- safe reproduction-package export outside the official bundle.

## Deferred repeated-test candidates

The following remain candidate product ideas, not active work:

- autosave and abnormal-exit recovery;
- save confirmation on close;
- final run summary;
- clearer progress and completion actions;
- output naming and recent profile/result management;
- repeated analysis with one profile;
- further Wizard/Workbench simplification.

Their status and promotion gate belong only to the [roadmap](../00-project/roadmap.md).

## Additional UX candidates

- enlarged reference-line drag guide;
- 1 px arrow and 5 px `Shift`+arrow movement;
- resize tooltip and modifier-based aspect/center behavior;
- analysis-area zoom, pan and fit;
- bidirectional highlight between fields and overlay items;
- clearer visual separation between profile and current-test settings.

## Implementation principles

1. Preserve domain and persisted-schema compatibility unless an approved design explicitly changes it.
2. Keep general-user and developer-debug information separated.
3. Prefer reviewable, reversible user control over uncertain automation.
4. Keep Qt presentation free of direct raster-processing ownership.
5. Complete automated regression obligations and record manual Windows/real-video obligations separately.
6. Do not declare milestone state or current next work here; link to the roadmap and work plan.