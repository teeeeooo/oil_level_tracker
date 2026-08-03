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

S8-C2 owns only normal-Workbench visual separation of existing ownership. A compact read-only Profile strip renders the active Recipe name and actual `recipe_path`, and the Glass list/settings panels are explicitly labeled as reusable `.oilrecipe` Profile content. The existing test-video, `run_name`, analysis range, compressor-start and sampling controls remain backed by `AnalysisSession` and are grouped as current-test-only state that is not Profile content. These labels refresh through existing Workbench new/load/save/video/same-Profile transitions and introduce no duplicate Profile/session model, persistence field, dirty-state rule or workflow owner. S8-C2 remains presentation-only Lane B pending its Orchestrator exact-head gate.

Profile favorites/pinning/tags/search, Profile duplication/templates, result moving/deletion/comparison, multi-run comparison, autosave/recovery, filesystem-wide Profile discovery and batch/queue execution remain outside S8-C2. Exact milestone status and the audit gate belong only to the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md).

## S9 operational recovery and UX selection

After S8, select P2 work based on observed user effect rather than treating every candidate as mandatory:

- autosave and abnormal-exit recovery;
- unsaved-change confirmation on close;
- analysis-area zoom, pan and fit;
- bidirectional highlight between fields and overlay items.

S9-A owns only unsaved Profile change tracking and application-close confirmation. Profile persistence dirtiness is independent from `WorkbenchState`: `WorkbenchController` compares the current serialized `InspectionRecipe` with a safe close baseline. Successful Profile load and save establish that baseline, while an explicit new Profile has no safe baseline until it is saved. Recipe-owned edits make the Profile dirty, and undoing back to the exact baseline makes it clean. Test-video, `run_name`, analysis range, compressor start, sampling and other `AnalysisSession`-only changes do not make the Profile dirty even when existing readiness/analysis state transitions mark the Workbench `DRAFT` or `DRAFT_DIRTY`.

A same-Profile new-video replacement starts from the authoritative Recipe snapshot already stored in the finalized result bundle, so that copied snapshot is a safe close baseline even though `recipe_path` is intentionally `None`; subsequent user Recipe edits are dirty. This avoids a save warning caused only by copying a safely persisted result snapshot. S8-C2 continues to display Profile and current-test ownership from the existing Recipe/`recipe_path` and session owners.

Application close checks Profile-specific dirtiness before video-reader teardown. A dirty Profile offers Save, Discard and Cancel. Save reuses the established Profile save workflow and normalized `.oilrecipe` path behavior; Save-As cancellation or save failure cancels close and preserves the current Workbench. Rejected close also preserves application-owned secondary lifecycle state such as Result Review, the completion dialog, prepared same-Profile work and preflight; those owners tear down only after `MainWindow` has accepted the application close. Discard closes without writing or overwriting the Profile file. Cancel leaves Recipe, session, reader and UI state intact. A failed repository write restores the pre-save Recipe `updated_at`, so an unsuccessful save attempt cannot mutate the in-memory Profile or establish a clean baseline.

S9-A does not add autosave, crash/abnormal-exit recovery, recovery files, session recovery or prompts on every new/load transition. Autosave/recovery, analysis-area zoom/pan/fit and field↔overlay highlight remain unstarted unless separately authorized.

The following remain P3 lower-priority backlog unless explicitly promoted:

- enlarged reference-line drag guide;
- 1 px arrow and 5 px `Shift`+arrow movement;
- resize tooltip and modifier-based geometry editing;
- further Wizard/Workbench simplification.

S9 is a selection boundary, not a promise that every P2 or P3 candidate ships before release. Windows/manual GUI and packaging validation remains a separate final release obligation governed by the [roadmap](../00-project/roadmap.md) and [real-world validation plan](../30-quality/real-world-validation-plan.md).

## Implementation principles

1. Preserve domain and persisted-schema compatibility unless an approved design explicitly changes it.
2. Keep general-user and developer-debug information separated.
3. Prefer reviewable, reversible user control over uncertain automation.
4. Keep Qt presentation free of direct raster-processing ownership.
5. Complete automated regression obligations and record manual Windows/real-video obligations separately.
6. Do not declare milestone state or current next work here; link to the roadmap and work plan.
