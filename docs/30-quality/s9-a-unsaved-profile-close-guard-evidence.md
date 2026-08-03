# S9-A Unsaved Profile Change Tracking & Close Confirmation — Worker Evidence

**Status:** `IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT AUDIT`

- Starting exact `main`: `d5fb35f072613b07949fd83ffb67c93783028be9`
- Worker branch: `feature/s9-a-unsaved-profile-close-guard`
- Lane: `C — Independent Review`
- Next gate: `S9-A Unsaved Profile Change Tracking & Close Confirmation Fresh Exact-Head Auditor`

## Profile persistence owner

`WorkbenchState` remains the readiness/analysis workflow state and is not reused as Profile persistence dirtiness. `WorkbenchController.profile_has_unsaved_changes` instead compares the current `InspectionRecipe.to_dict()` with a deep-copied safe close baseline.

The initial empty application document has a safe baseline. An explicit new Profile clears that baseline because closing would discard newly authored Profile content. Successful Profile load and save establish the current serialized Recipe as the new safe baseline. Recipe edits compare dirty, while restoring the exact serialized content through undo compares clean again.

Current-test-only `AnalysisSession` changes are outside this comparison. Video/session edits may continue to drive the existing Workbench state to `DRAFT` or `DRAFT_DIRTY` for readiness semantics without creating an unsaved-Profile warning.

## Save and close boundary

`MainWindow.closeEvent()` evaluates Profile-specific dirtiness before `close_video()`. Clean Profile close performs the existing teardown without a prompt. Dirty close provides Save, Discard and Cancel choices.

Save calls the existing `MainWindow.save_recipe()` path, which continues through `WorkbenchController.save()` → `SaveRecipeUseCase` → `JsonRecipeRepository`. Existing paths are reused; new paths still use the established file dialog and repository `.oilrecipe` suffix normalization. Save-As cancellation and save failure ignore the close event and leave the reader and Workbench active.

Discard does not serialize or overwrite the current Profile. Cancel does not mutate Recipe, session, reader or UI state. `SaveRecipeUseCase` restores the previous `updated_at` if repository publication fails, so a failed save cannot mutate the in-memory Recipe or establish a false clean baseline.

## Special transitions

The same-Profile new-video workflow continues to deep-copy the authoritative Recipe snapshot from the finalized result bundle. Commit establishes that safely persisted snapshot as the close baseline even though `recipe_path=None`, preventing a prompt caused solely by the copied result snapshot. A subsequent user Recipe edit becomes dirty normally.

S8-C2 Profile/current-test presentation remains unchanged: Profile identity still derives from Recipe/`recipe_path`, while video, `run_name`, range, compressor start and sampling remain current-test session state.

## Worker validation

Narrow dirty/save/close coverage after final save-failure repair:

`QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/unit/test_profile_dirty_tracking.py tests/gui/test_unsaved_profile_close_guard.py`

Result: `15 passed in 3.67s`.

Focused Workbench compatibility after stabilization covered S9-A dirty/close behavior, S8-C2 ownership presentation, recent Profile access, same-Profile GUI/unit contracts, Recipe storage, UI import boundaries and Qt lifecycle.

Result: `53 passed in 6.80s`.

A development run that combined new close behavior with an older dirty-window GUI fixture blocked during pytest-qt teardown because the real modal close guard correctly awaited user choice. The owned test process was terminated, and only that existing test helper was updated to choose Discard during teardown; no test-only production bypass was introduced.

Detector benchmarks, soak/long-duration workloads, Windows/manual GUI acceptance, PyInstaller and unrelated canonical suites were intentionally not run. No autosave/recovery, Windows/DPI or packaging PASS is inferred.
