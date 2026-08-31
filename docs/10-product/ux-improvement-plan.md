# UX Improvement Plan

## Authority and purpose

This document owns the user-facing workflow and acceptance contract for Workbench, preflight and follow-up UX improvements. It does not own project status or the current next action.

- Long-term milestone status: [project roadmap](../00-project/roadmap.md)
- Active gate and next action: [current work plan](../00-project/work-plan.md)
- Result Review detail: [Result Review Viewer plan](result-review-viewer-plan.md)
- Manual Windows obligations: [manual GUI and Windows checklist](../40-operations/manual-gui-windows-checklist.md)

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
- exclusion regions.

Advanced mode retains geometry coordinates, margin and detector settings. Workbench no longer exposes real-length/mm-per-pixel configuration. Existing `.oilrecipe` values remain readable for compatibility and historical result interpretation, but are not a current editing surface.

### Focused analysis-area editing

- Edit ellipse, reference line and exclusion regions in a large focused view.
- Editing one geometry target mutates only that target: dragging or resizing an exclusion must not change the selected Glass ellipse geometry unless the ellipse itself is intentionally manipulated.
- Keep the source profile unchanged until Apply.
- Cancel restores the original state.
- Apply creates one undo operation.
- Geometry remains in source-frame coordinates and inside the frame.

### Detector-proposed artifact editing

- Artifact proposals appear in a scrollable settings pane below a resizable
  source-video pane; controls must not overlap the image on supported Windows
  display scales.
- Selecting one or several proposal rows highlights the exact matching
  point/line/region on the video so list state is visually unambiguous.
- Users may select all proposals and explicitly apply the selected set as
  Artifacts in one action. Select-all is only an editing shortcut: proposals
  still require visual review because a real Oil boundary may be proposed.
- Proposal selection/highlight is transient presentation state. Only explicit
  Artifact apply mutates normalized Recipe templates and participates in the
  existing Apply/Cancel and undo contract.
- Detector proposal generation and raster interpretation remain outside the Qt
  presentation layer.

### Fixed execution area and validation

The execution area remains visible and exposes setup status, validation, profile save and analysis execution. Field-level errors use adjacent Korean guidance and route the user to the affected Glass/input. Analysis remains disabled while readiness errors exist.

### Undo and redo

Ellipse, reference line, exclusion region and supported settings changes participate in `Ctrl+Z`/`Ctrl+Y`. A multi-target settings copy is one atomic operation and no-op changes do not dirty the document.

## Pre-analysis readiness contract

### Run-scoped initial-state confirmation

Final analysis requires an explicit current-run initial-state confirmation for every enabled Glass. The selected Recipe value and the current-run confirmation are separate concepts: a default, pre-populated, loaded or copied `initial_state` must never masquerade as fresh user confirmation.

Current-run confirmation records the user's direct visual assessment for the current video and analysis-start context. `AUTO` cannot satisfy final-analysis readiness. An explicitly confirmed `UNKNOWN_REVIEW` may satisfy readiness when the user genuinely cannot determine the initial state, but it grants no retrospective FULL/EMPTY authority.

Confirmation becomes stale when the material observation context changes, including:

- video replacement, including same-Profile new-video preparation;
- analysis-start change;
- initial-state value change;
- a new or newly enabled Glass that lacks confirmation;
- establishment of a new analysis session.

Confirmation remains valid when the user changes analysis end, compressor-start
time, sampling FPS, detector settings or other presentation/execution options
that do not replace the video, move analysis start, change the selected initial
state, or introduce an unconfirmed enabled Glass. These changes may invalidate
preflight or analysis output independently; they must not force the user to
repeat the same initial-scene assessment.

The confirmation dialog and settings surface use the same user-facing Korean
state labels. Serialized enum names such as `FULL_NO_INTERFACE` are never the
visible confirmation question.

Freshly confirming an unchanged selected initial state does not by itself dirty the reusable Profile. Preflight may run while initial state remains unresolved, but it must not silently establish confirmation. GUI and programmatic/headless final-analysis entry paths must enforce the same confirmation authority.

### Glass readiness

Each Glass displays one of: ready, review required, correction required or excluded, with the most important reason. Global session issues are not duplicated as every Glass's error.

The user can jump to the first error, otherwise the first warning. Selection, canvas, settings panel and focused field remain synchronized.

### Current-scene summary

The general UI shows only the final current-scene interpretation:

- normal, review-required or failed status;
- observed fill state;
- Oil level relative to the reference line, with optional mm value; and
- at most one plain-language action when user input is actually required.

Generic two-line narratives such as `핵심 내용` / `다음 행동` are not shown.
When no Oil boundary is observed, the action must identify a concrete user
decision or control to use; it must not merely tell the user to inspect Foam
without explaining what that inspection changes.

Candidate internals and scoring remain in debug surfaces.

### Multi-frame preflight

Representative timestamps include analysis start, compressor-start vicinity, interval quartiles and analysis end. The modeless window reports Glass/timestamp status, minimum confidence, missing candidate, abnormal jump and Foam/review evidence.

Selecting a row seeks the Workbench to that Glass/timestamp. Recipe, video, analysis-range, Glass or detector-setting changes mark prior results stale. Run/cancel/rerun and Workbench close must not leak signals, processes or file handles.

### Observation-window settings copy

- One source and multiple targets are supported.
- Identity, name, inclusion, center, reference line and exclusions remain target-owned.
- Judgment, detector, margin and initial state are copied by default.
- ellipse size is an explicit option.
- Mutable settings are deep-copied.
- Geometry compatibility is checked before any target changes.
- The full multi-target change is atomic and undoable.

## Result Review UX contract

After analysis, the user can open the source video and official bundle together, inspect the selected Glass overlay, navigate events/review intervals and synchronize video with the tracking graph. The Viewer remains read-only and uses result-bundle snapshots rather than current Workbench state.

General review hides candidate and score internals. Debug mode, partial re-detection, user truth and regression export follow the detailed [Result Review Viewer plan](result-review-viewer-plan.md).

The shared video transport uses a two-row precision layout: primary playback,
frame-step, ±5/±10-second, direct-time and speed controls remain compact while a
full-width slider occupies its own row. Empty slider clicks seek immediately;
drag seeking is bounded/throttled and flushes the final release position.

## Real-use Workbench stabilization contract

- Progress-step text remains single-line and unclipped at supported Windows DPI settings.
- The center video remains the primary Workbench area; transport controls never overlap it.
- Long metadata and setting rows may wrap vertically instead of clipping or
  forcing the center video narrower. The visible source-video identity uses a
  concise filename while the full path remains available as secondary detail.
- Initial-state controls and confirmation text remain fully readable at the
  minimum supported window size and Windows 100%, 125% and 150% scaling.
- User-facing `ROI` becomes `분석 영역`; `관찰창` becomes `Glass`; `oil-air` becomes `유면` or `유면 경계`; general UI uses `거품` for Foam.
- The current-scene card and Glass list share the left area without shrinking the video unnecessarily.
- Basic settings avoid awkward wrapped coordinate summaries.
- Wheel events scroll the settings panel instead of changing spin/combo values; keyboard/direct controls still edit values.
- Real-length conversion is absent from Workbench and settings-copy UI; new
  setup remains px-based while legacy `.oilrecipe` values stay readable.
- Foam guidance separates detector interpretation from recommended user action and never mutates initial state automatically. A future S12 candidate may make the post-confirmation action guidance more explicit when the current recommendation stops at confirming whether Foam is real; this remains a copy/actionability refinement candidate, not an authorized implementation slice.
- Multi-frame preflight is a modeless resizable window rather than a central-area-shrinking dock.

These requirements are verified through automated geometry/import tests where practical and the manual Windows checklist where platform interaction matters. Source-tree/offscreen regression does not establish a Windows DPI result; the changed Workbench and Result Review layouts remain pending until the proportional Windows checklist is executed.

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

## S8 repeated-test productivity scope

The roadmap prioritizes the following as the P1 repeated-test workflow and result-management scope after S7:

- repeated analysis of multiple test videos with one Profile;
- improved output naming;
- recent profile and recent result management;
- final run summary with clear completion actions;
- clearer visual separation between profile-owned settings and current-test settings.

S8-A owns only the first run-identity/output-naming seam. One optional `run_name` is current-test/session state, not Recipe/Profile state. The Workbench exposes it as `현재 시험 이름`; changing it must not rename or dirty serialized Profile content. New bundles persist the original human-readable value in `session.json`, `review_index.json` and `analysis_manifest.json`, while the folder name uses a filesystem-safe form plus the existing timestamp and deterministic collision suffixes. Empty or filename-unusable values retain the timestamp-only fallback, and older sessions/bundles without `run_name` remain readable. Both the same-profile new-video path and a successful normal Workbench video replacement reset the previous test name. Normal replacement is transactional across reader acquisition and metadata preparation: reader-factory or metadata failure preserves the existing active reader, complete session/state including `run_name`, and Recipe/Profile state, and closes any acquired failed candidate reader; only after preparation succeeds is the candidate installed and the previous reader closed. File-dialog cancellation remains a no-op. The same-profile deep-copy and atomic prepare/confirm/commit contract remains unchanged.

S8-B1 owns only persistent recent-result access. A bounded schema-versioned recent-result registry lives in the existing application user-data directory and never inside an official result bundle. Entries are deterministic newest-first, duplicate bundle paths move to the front, and the default history limit is eight. Cached `run_name`, Profile name, source-video basename and path exist only to distinguish rows in the chooser; a selected result is still opened and validated through the existing Result Review bundle reader, so history metadata never becomes analysis truth. Successfully finalized analyses are re-read through `ResultBundleReader` before registration, and successfully opened bundles may refresh cached display metadata from the authoritative `ReviewBundle`. Missing history is normal on first run, malformed/unreadable history fails safely, stale or moved result paths are isolated instead of breaking the list, and history writes use temporary-file plus atomic replacement so a failed write does not partially replace prior valid state. The `다른 결과 폴더 선택` workflow remains available, and opening a historical/manual result does not replace `last_result_path`, which remains the current Workbench completion/report pointer.

S8-B2 owns only persistent recent-Profile access. A separate schema-versioned `recent_profiles.json` registry lives in the same application user-data boundary as other application navigation state, remains bounded to eight entries by default, and stores only normalized `.oilrecipe` path plus Profile name. Entries are deterministic newest-first and duplicate normalized paths move to the front. Successful normal manual Profile load and successful Profile save register only after the existing Workbench repository/use-case operation succeeds; save registration uses the actual extension-normalized saved `.oilrecipe` path. History read/write failure is non-fatal to the successful Profile operation, malformed/unreadable storage fails safely, stale/moved/deleted paths disable only their recent action, and atomic replacement preserves prior valid history on write failure.

Recent Profile selection re-enters the existing `프로필 열기` action and `WorkbenchController.load()` / `LoadRecipeUseCase` authority instead of creating a second loader. Cached names are display hints only and refresh from the successfully loaded Recipe. History operations never write to or mutate the referenced `.oilrecipe`. The `다른 프로필 파일 선택…` path remains available alongside the recent list. `run_name`, current video/session state and S8-B1 recent-result metadata remain separate and are not promoted into Profile identity.

S8-C1 owns only the finalized-run completion summary and its established completion actions. After `ANALYZED` and `last_result_path` are committed, the completion coordinator reads the finalized result through `ResultBundleReader` for display-only current-test `run_name`, Profile name and source-video identity. Overall/Glass judgments plus warning/error counts remain sourced from the just-completed `AnalysisResult`; the committed output path remains the completion/result-action target. Empty `run_name` is displayed explicitly as unnamed rather than borrowing Profile or video identity. If finalized bundle metadata cannot be read, the dialog keeps the completed judgment/output baseline and marks richer identity fields unavailable without revoking successful analysis.

Completion Review/report/folder actions remain bound to the completed output path. Same-Profile continuation still reloads that finalized bundle and enters the existing transactional replacement workflow; the summary never supplies Recipe truth. Recent-result/Profile caches remain navigation state only, official bundles remain immutable, and duplicate-action/close protection remains owned by the existing completion coordinator.

S8-C2 owns only normal-Workbench visual separation of existing ownership. A compact read-only Profile strip renders the active Recipe name and actual `recipe_path`, and the Glass list/settings panels are explicitly labeled as reusable `.oilrecipe` Profile content. The existing test-video, `run_name`, analysis range, compressor-start and sampling controls remain backed by `AnalysisSession` and are grouped as current-test-only state that is not Profile content. These labels refresh through existing Workbench new/load/save/video/same-Profile transitions and introduce no duplicate Profile/session model, persistence field, dirty-state rule or workflow owner. This presentation contract is accepted; current milestone status is intentionally not repeated here.

Profile favorites/pinning/tags/search, Profile duplication/templates, result moving/deletion/comparison, multi-run comparison, autosave/recovery, filesystem-wide Profile discovery and batch/queue execution remain outside S8-C2. Exact milestone status and the audit gate belong only to the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md).

## S9 operational recovery and UX polish

S9 slice sequence and current gate are owned by the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md). This section defines the user-facing contracts for the selected S9 interaction slices while preserving S9-A behavior and existing SSOT geometry authority.

S9-A owns only unsaved Profile change tracking and application-close confirmation. Profile persistence dirtiness is independent from `WorkbenchState`: `WorkbenchController` compares user Profile state with a safe close baseline and intentionally excludes save-generated `InspectionRecipe.updated_at` bookkeeping from that comparison. Successful Profile load and save establish the baseline, while an explicit new Profile has no safe baseline until it is saved. Recipe-owned edits make the Profile dirty; undo away from the persisted Profile remains dirty, while redo back to the same persisted Profile content becomes clean even if the restored undo snapshot carries an older `updated_at`. Test-video, `run_name`, analysis range, compressor start, sampling and other `AnalysisSession`-only changes do not make the Profile dirty even when existing readiness/analysis state transitions mark the Workbench `DRAFT` or `DRAFT_DIRTY`.

A same-Profile new-video replacement starts from the authoritative Recipe snapshot already stored in the finalized result bundle, so that copied snapshot is a safe close baseline even though `recipe_path` is intentionally `None`; subsequent user Recipe edits are dirty. This avoids a save warning caused only by copying a safely persisted result snapshot. S8-C2 continues to display Profile and current-test ownership from the existing Recipe/`recipe_path` and session owners.

Application close checks Profile-specific dirtiness before video-reader teardown. A dirty Profile offers Save, Discard and Cancel. Save reuses the established Profile save workflow and normalized `.oilrecipe` path behavior; Save-As cancellation or save failure cancels close and preserves the current Workbench. Rejected close also preserves application-owned secondary lifecycle state such as Result Review, the completion dialog, prepared same-Profile work and preflight; those owners tear down only after `MainWindow` has accepted the application close. Discard closes without writing or overwriting the Profile file. Cancel leaves Recipe, session, reader and UI state intact. A failed repository write restores the pre-save Recipe `updated_at`, so an unsuccessful save attempt cannot mutate the in-memory Profile or establish a clean baseline.

S9-A does not add autosave, crash/abnormal-exit recovery, recovery files, session recovery or prompts on every new/load transition. Its accepted dirty/save/close lifecycle remains the compatibility boundary for later S9 interaction work.

### S9-B — Workbench Analysis-Area Zoom, Pan & Fit

S9-B improves precision editing for small sight-glass regions without changing Recipe geometry authority.

- The analysis-area view has a clear default Fit behavior and an explicit fit-to-view action that presents the source frame within the available viewport while preserving aspect ratio.
- Users can zoom in and out around the analysis area. An explicit actual-pixel/100% view may be provided when it fits the interaction model, but its presence does not replace Fit as the safe default/reset behavior.
- When zoomed, users can pan to inspect and edit small ellipse, zero-line and exclusion details.
- Ordinary frame/timestamp changes within the same video/Profile context do not unnecessarily reset the user's current view transform.
- Replacing the video or Profile context establishes a reasonable Fit/reset so a transform from the previous context is not carried forward blindly.
- Canonical geometry remains source-frame / `QGraphicsScene` coordinates. Zoom and pan are view state only and must not mutate Recipe geometry, source coordinates or persisted data.
- Ellipse movement/resizing, zero-line placement and exclusion editing retain source-coordinate accuracy at every supported zoom level.
- Zoom/pan interaction must coexist with the existing settings-panel wheel-safe behavior; pointer interaction over settings controls must not regress into accidental value changes.
- The Workbench exposes explicit `확대`, `축소`, `맞춤` and `100%` view controls. `Ctrl`+wheel is an equivalent zoom shortcut on the canvas, while middle-button drag pans without competing with the existing left-button ellipse/zero-line/exclusion editing gestures.
- Fit mode follows viewport resizing; once the user enters manual zoom/pan or 100% mode, ordinary viewport resize and same-context frame refresh preserve that manual scale instead of silently returning to Fit.

### S9-C — Field ↔ Overlay Interaction Polish

S9-C reduces ambiguity about what the user is currently editing by coupling settings-panel context and overlay affordances without conflating selection with the active edit target.

Field → Overlay behavior:

- geometry fields or geometry-group focus highlights the selected ellipse;
- zero-line field focus highlights the zero line;
- margin field focus highlights the inner detection margin;
- an exclusion entry/field highlights the corresponding exclusion overlay.

Overlay → Field behavior:

- ellipse interaction highlights the corresponding geometry field/group;
- zero-line interaction highlights the corresponding field;
- exclusion interaction highlights the corresponding exclusion field/group and makes that editor visible when scrolling or expansion is required.

Selection state and active editing-target highlight remain semantically distinct: the selected Glass stays identifiable while the currently edited ellipse, line, margin or exclusion receives a stronger temporary affordance. The implemented Workbench keeps that active target as transient `MainWindow` presentation state (`Glass id + target kind + optional exclusion id`) and lets the settings panel and canvas request/render it; it is not Recipe, session, undo, readiness or detector state. Same-Glass panel/canvas rebuilds rebind the transient target, while Glass changes and deletion of the exact active exclusion clear stale context.

Validation and edit-target presentation coexist rather than replace one another. Existing `validationState` error/warning properties continue to own validation borders and routing, while the independent `interactionTarget` property supplies editing context. `focus_field()` therefore keeps first-issue navigation/focus behavior and may also reveal the matching transient overlay target.

Ellipse visual polish is part of S9-C. The existing axis-aligned eight-direction resize capability remains required, but a normally selected ellipse should not be dominated by eight large square handles. The Workbench renders restrained circular handle markers while preserving a larger transform-independent practical hit area; hover/geometry context strengthens the markers and the active resize handle is visually stronger. Existing minimum size, frame bounds, source-scene coordinates and eight-direction resize behavior remain unchanged. S9-C highlight refresh updates item styling in place and does not reset S9-B Fit/manual zoom or pan state.

Autosave/abnormal-exit recovery remains explicitly `DEFERRED`. Its activation condition and non-current routing are owned only by the [retained commitments](../00-project/retained-commitments.md).

The following remain P3 lower-priority backlog unless explicitly promoted:

- enlarged reference-line drag guide;
- 1 px arrow and 5 px `Shift`+arrow movement;
- resize tooltip and modifier-based geometry editing;
- further Wizard/Workbench simplification.

S9-B and S9-C remain accepted product contracts; unrelated P3 items remain optional unless promoted. S10 Windows/manual GUI and packaging acceptance is completed historical evidence, while any future proportional revalidation is governed by the [roadmap](../00-project/roadmap.md), [real-world validation plan](../30-validation/real-world-validation-plan.md) and [manual Windows procedure](../40-operations/manual-gui-windows-checklist.md).

## Implementation principles

1. Preserve domain and persisted-schema compatibility unless an approved design explicitly changes it.
2. Keep general-user and developer-debug information separated.
3. Prefer reviewable, reversible user control over uncertain automation.
4. Keep Qt presentation free of direct raster-processing ownership.
5. Complete automated regression obligations and record manual Windows/real-video obligations separately.
6. Do not declare milestone state or current next work here; link to the roadmap and work plan.
