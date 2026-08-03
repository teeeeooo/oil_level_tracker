# S8-B2 Persistent Recent Profile Access — Worker Evidence

**Status:** `IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT AUDIT`

## Scope and identity

- Repository: `teeeeooo/oil_level_tracker`
- Registered checkout: `/Users/sunjaekim/Developer/oil_level_tracker`
- Starting branch: `main`
- Starting exact `HEAD == origin/main`: `789d2646e3355f4486ef902d93565205265ecd39`
- Worker branch: `feature/s8-b-recent-profile-access`
- Next gate: `S8-B2 Persistent Recent Profile Access Fresh Exact-Head Auditor`

S8 remains `ACTIVE`. S8-A and S8-B1 remain independently audited, merged and closed. This slice implements only persistent recent-Profile access; remaining S8 workflow work is unstarted.

## Persistence ownership

`RecentProfileHistory` owns schema-versioned recent-Profile navigation metadata in the existing application `user_data_dir()` boundary. The default registry is `recent_profiles.json`, separate from S8-B1 `recent_results.json`, with a default maximum of eight entries.

Each entry stores only an extension-normalized absolute `.oilrecipe` path and Profile name. No Recipe payload, current video, `run_name`, Result identity or analysis state is cached.

## Registration and Profile authority

Successful normal manual Profile load registers only after `WorkbenchController.load()` returns successfully. Successful save registers only after `WorkbenchController.save()` returns, using `workbench.recipe_path`, which already identifies the actual `.oilrecipe` path after repository extension normalization.

Recent selection does not deserialize cached metadata. It stages the selected path and triggers the existing `프로필 열기` QAction, so the same `MainWindow.load_recipe()` → `WorkbenchController.load()` → `LoadRecipeUseCase` → `JsonRecipeRepository.load()` authority used by manual opening remains the only Profile-loading behavior. The cached Profile name is refreshed from the successfully loaded Recipe.

Registration exceptions are logged and swallowed after successful Profile load/save. A failed Profile load never reaches registration. Existing Profile atomic-save behavior is unchanged.

## Ordering, deduplication and failure behavior

- insertion is deterministic newest-first;
- re-registering the same normalized path moves it to the front and refreshes the name;
- history is bounded and performs no filesystem-wide Profile discovery;
- Unicode paths and normal supported OS paths remain plain filesystem paths;
- missing history is a normal first-run condition;
- malformed, unreadable or unsupported history fails safely as empty history;
- malformed individual entries are skipped without blocking valid entries;
- stale/moved/deleted Profile paths disable only that recent menu action;
- the `다른 프로필 파일 선택…` action remains available regardless of history state;
- writes use same-directory unique temporary files, flush/fsync and `os.replace`;
- failed replacement removes the temporary file and preserves prior valid history bytes.

History registration reads only Recipe display metadata and writes only the separate user-data registry. Unit coverage snapshots referenced `.oilrecipe` bytes before registration and verifies they remain unchanged, including after stale-entry handling.

## Workbench and S8 compatibility

Recent and manual opening produce the same Recipe, `recipe_path`, selected Glass and Workbench state because both enter the same load action/use-case path. Existing session/video handling therefore remains whatever the established manual Profile workflow owns; S8-B2 introduces no second lifecycle.

The recent-Profile registry contains neither S8-A `run_name` nor S8-B1 Result metadata. `recent_profiles.json` and `recent_results.json` remain separate owners, and Result Review authority is unchanged.

## Validation

Narrow persistence/Profile validation:

`16 passed in 4.12s`
Targeted S8-B2 Workbench/UI compatibility validation:

`63 passed in 8.28s`

The targeted suite covered recent Profile persistence and Workbench GUI access, Recipe storage, normal Workbench GUI load/save/video behavior, preflight compatibility, same-profile workflow, S8-A run identity, S8-B1 recent-result persistence/chooser behavior and UI import boundaries.

## Intentional non-runs and deferred work

The Worker did not run detector benchmarks, S6 soak/long-duration workloads, Windows/manual GUI validation, PyInstaller/one-folder packaging or unrelated canonical suites. No PASS is inferred for those gates.

The following remain intentionally unimplemented: Profile favorites/pinning/tags/search, Profile duplication/templates, autosave/recovery, unsaved-change workflow redesign, result/Profile unified storage, filesystem-wide Profile discovery, batch execution, final-run summary redesign and broad Profile/current-test visual redesign.

## Source-completing documents

- [Project roadmap](../00-project/roadmap.md)
- [Current work plan](../00-project/work-plan.md)
- [UX improvement plan](../10-product/ux-improvement-plan.md)
- [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

Exact successor: `S8-B2 Persistent Recent Profile Access Fresh Exact-Head Auditor`.
