# S9-A Unsaved Profile Change Tracking & Close Confirmation — Worker Evidence

**Status:** `IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT AUDIT`

- Starting exact `main`: `d5fb35f072613b07949fd83ffb67c93783028be9`
- Rejected-close repair starting head: `aa7f10ec33e67cf8ae6b44a32609ce191b8e5cc2`
- Persistence-metadata dirty-semantics repair starting head: `ffef828ddc1febc72841b7b1a103624797d21c83`
- Worker branch: `feature/s9-a-unsaved-profile-close-guard`
- Lane: `C — Independent Review`
- Next gate: `S9-A Unsaved Profile Change Tracking & Close Confirmation Fresh Exact-Head Auditor`

## Profile persistence owner

`WorkbenchState` remains the readiness/analysis workflow state and is not reused as Profile persistence dirtiness. `WorkbenchController.profile_has_unsaved_changes` compares user Profile state with a deep-copied safe close baseline and intentionally removes save-generated `InspectionRecipe.updated_at` bookkeeping from that comparison.

The initial empty application document has a safe baseline. An explicit new Profile clears that baseline because closing would discard newly authored Profile content. Successful Profile load and save establish the current Profile state as the new safe baseline. Recipe-owned edits compare dirty. After `edit → save`, undo away from the persisted Profile compares dirty; redo back to the persisted Profile content compares clean even though the restored undo snapshot still carries its pre-save `updated_at`. The save use case itself is unchanged and still persists a fresh `updated_at` on success.

Current-test-only `AnalysisSession` changes are outside this comparison. Video/session edits may continue to drive the existing Workbench state to `DRAFT` or `DRAFT_DIRTY` for readiness semantics without creating an unsaved-Profile warning.

## Save and close boundary

`MainWindow.closeEvent()` evaluates Profile-specific dirtiness before any close-success-dependent teardown. Clean Profile close performs the existing teardown without a prompt. Dirty close provides Save, Discard and Cancel choices.

Save calls the existing `MainWindow.save_recipe()` path, which continues through `WorkbenchController.save()` → `SaveRecipeUseCase` → `JsonRecipeRepository`. Existing paths are reused; new paths still use the established file dialog and repository `.oilrecipe` suffix normalization. Save-As cancellation and save failure ignore the close event and leave the reader and Workbench active.

The rejected-close repair removes lifecycle teardown from raw `QEvent.Close` event filters. `MainWindow` now emits `applicationCloseAccepted` only after its close guard and the base close event have accepted the request. Result Review, analysis completion, prepared same-Profile work and preflight subscribe to that accepted-close boundary and retain their existing cleanup ownership. A rejected close therefore cannot destroy those secondary lifecycles before the user returns to the Workbench; an accepted close cleans them before the Workbench video reader is closed.

Discard does not serialize or overwrite the current Profile. Cancel does not mutate Recipe, session, reader or UI state. `SaveRecipeUseCase` restores the previous `updated_at` if repository publication fails, so a failed save cannot mutate the in-memory Recipe or establish a false clean baseline.

## Special transitions

The same-Profile new-video workflow continues to deep-copy the authoritative Recipe snapshot from the finalized result bundle. Commit establishes that safely persisted snapshot as the close baseline even though `recipe_path=None`, preventing a prompt caused solely by the copied result snapshot. A subsequent user Recipe edit becomes dirty normally.

S8-C2 Profile/current-test presentation remains unchanged: Profile identity still derives from Recipe/`recipe_path`, while video, `run_name`, range, compressor start and sampling remain current-test session state.

## Worker validation

Narrow dirty/save/close coverage, including `edit → save → undo → redo → clean`, close from that clean redo state without an unsaved prompt, successful save `updated_at` persistence, save-failure rollback, and real `window.close()` assertions for rejected and accepted secondary lifecycle behavior:

`QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/unit/test_profile_dirty_tracking.py tests/gui/test_unsaved_profile_close_guard.py`

Result: `16 passed in 5.31s`.

Adjacent compatibility covered Result Review and recent-result access, analysis completion, same-Profile workflow, S8-C2 Profile/current-test presentation, preflight, Qt lifecycle and UI import boundaries:

`QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/gui/test_result_review_coordinator_factory.py tests/gui/test_analysis_completion_coordinator.py tests/gui/test_same_profile_analysis_coordinator.py tests/gui/test_profile_current_test_separation.py tests/gui/test_preflight_check.py tests/gui/test_recent_result_review_access.py tests/test_qt_lifecycle.py tests/test_ui_import_boundaries.py`

Result: `39 passed in 7.72s`.

Two development runs blocked after already-passed GUI test bodies because pytest-qt teardown attempted to close an intentionally dirty test MainWindow and the real modal guard correctly awaited a user choice. The owned processes were terminated. The affected preflight fixture now chooses Discard only for its teardown close; lifecycle regression tests still exercise the production close sequencing directly and do not bypass or mock the event-filter defect.

Detector benchmarks, soak/long-duration workloads, Windows/manual GUI acceptance, Windows DPI, PyInstaller and unrelated canonical suites were intentionally not run. No autosave/recovery or packaging PASS is inferred.
