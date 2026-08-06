# S8-C2 Profile/Current-Test Visual Separation — Worker Evidence

**Status:** `IMPLEMENTATION COMPLETE — AWAITING ORCHESTRATOR EXACT-HEAD GATE`

## Identity and lane

- Repository: `teeeeooo/oil_level_tracker`
- Starting exact `main == origin/main`: `482158f9ca381271d2824759ceca8f1e253be50f`
- Worker branch: `feature/s8-c-profile-current-test-separation`
- Lane: `B — Bounded Change`
- Exact next gate: `S8-C2 Profile/Current-Test Visual Separation Orchestrator Exact-Head Gate`

S8 remains `ACTIVE`. S8-A/B1/B2/C1 remain audited, merged and closed. This slice does not declare S8 complete.

## Presentation ownership

The Workbench now exposes one compact read-only Profile strip from the existing `InspectionRecipe` plus `WorkbenchController.recipe_path`. It shows the current Recipe name and actual saved `.oilrecipe` location, or an explicit unsaved state when `recipe_path` is `None`.

The Glass list and selected-Glass settings panel are visibly labeled as reusable Profile-owned configuration. No additional Profile cache/model was introduced.

The existing session bar is labeled as current-test-only and states that its video, `run_name`, analysis range, compressor start and sampling fields are not Profile content. Those controls continue to read/write the existing `AnalysisSession`; no second session state exists.

## Transition behavior and invariants

Normal Workbench refresh paths keep the visual context coherent after new/load/save, normal video replacement and same-Profile replacement. Save/load identity uses the authoritative `recipe_path`; normal video replacement refreshes only session presentation and keeps Profile identity; same-Profile replacement displays the saved Recipe snapshot semantics while the new session begins with a fresh `run_name` and new video.

No `.oilrecipe` schema, `AnalysisSession` schema, result bundle, repository/use-case, dirty-state rule, undo/redo, validation, preflight, recent-history, S8-C1 completion or same-Profile workflow owner changed. `run_name` remains absent from Recipe serialization.

The first targeted run intentionally used the system Python and failed before test bodies because `pytest-qt` fixture `qapp_args` was unavailable. Repository evidence identified `.venv` as the project test environment; rerunning there produced valid results.

## Validation

Narrow Profile/current-test, Workbench smoke, same-Profile and recent-Profile GUI suite: `23 passed in 4.90s`.

After a 1280×760 layout regression exposed by the targeted suite, the ownership explanation was compressed into GroupBox titles rather than consuming an extra session row. The final stabilized targeted Workbench suite passed: `60 passed in 7.89s`.

The targeted suite covered the changed ownership presentation, new/save/load Profile identity refresh, current-test video/run/range/compressor-start/sampling presentation, normal video replacement, same-Profile replacement, `run_name` serialization separation, 1280×760 canvas/transport layout, readiness/preflight, recent Profile access, Recipe storage and UI import boundaries.

Detector benchmarks, soak/long-duration workloads, Windows/manual GUI acceptance, PyInstaller and unrelated canonical suites were intentionally not run. No Windows/DPI/package PASS is inferred.
