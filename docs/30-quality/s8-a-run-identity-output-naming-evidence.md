# S8-A Repeated-Test Run Identity + Output Naming Evidence

**Status:** `IMPLEMENTED + NORMAL-OPEN IDENTITY REPAIR — awaiting fresh exact-head re-audit`

## Scope

S8-A is the first bounded repeated-test workflow slice. It adds one human-readable current-test identity without changing reusable Profile/Recipe persistence, detector behavior, Result Review overlay authority or S7 annotated-MP4 contracts.

## Implemented contract

- `AnalysisSession.run_name` is optional session/current-test state; the UUID analysis `run_id` remains the technical execution identity.
- Workbench exposes `현재 시험 이름` beside current video/session controls and explicitly states that the value is not stored in the Profile.
- Result bundle folders use `oil_level_analysis_<safe-run-name>_<timestamp>` when a useful name exists and retain the legacy timestamp-only form otherwise.
- Filename composition preserves usable Unicode, replaces path separators, platform-reserved filename punctuation and Unicode control/format characters, bounds the UTF-8 component length and never treats user input as a path component hierarchy.
- Existing `_2`, `_3`, ... collision suffix semantics remain deterministic and do not overwrite an existing bundle.
- The original human-readable `run_name` is persisted in `session.json`, `review_index.json` schema v1 and `analysis_manifest.json` so later result management does not need to parse folder names.
- Pre-S8 sessions, indexes, manifests and bundles without `run_name` remain readable; no persisted schema version was bumped.
- Same-profile follow-up deep-copies the Recipe snapshot as before but creates the replacement session with an empty `run_name`, preventing prior test identity leakage.
- Successful normal Workbench video replacement now clears the previous `run_name` only after the candidate video metadata has been acquired; file-dialog cancellation, reader-open failure and metadata failure before that success boundary preserve the existing current-test identity. MainWindow session-field synchronization therefore displays a blank `현재 시험 이름` for the successfully replaced video without mutating Recipe/Profile state.
- CLI `analyze` remains compatible and accepts optional `--run-name` for the same metadata/naming contract.

## Focused validation

The original S8-A implementation recorded a `97 passed` targeted source-tree suite before this repair. The normal-open defect was then independently reproduced at exact head `45ee966da4b8ed31085a4405f240321322bfce7f`: successful `WorkbenchController.open_video()` retained the previous `run_name`, while reader-open failure preserved it. Added controller/UI regressions failed exactly on the two successful-replacement assertions (`2 failed, 13 passed`) before the source fix.

Current repair validation:

- invalidated Workbench + MainWindow regression files: `16 passed`;
- targeted S8-A/Workbench suite covering session ownership, normal-open reset/failure/cancel behavior, same-profile reset/debug-trace compatibility, MainWindow synchronization and CLI compatibility: `26 passed`.

The broader output-naming, persisted-bundle compatibility, S7 export, detector, soak/long-duration, Windows/manual GUI and PyInstaller evidence was not rerun because this repair changes only the normal Workbench `run_name` lifecycle after successful candidate metadata acquisition.

Repair documentation validation checked 50 applicable relative links across the authoritative S8-A/current-state documents with no missing targets, and `git diff --check` passed.

## Explicit non-scope and non-runs

S8-A does not implement recent-profile/history UI, recent-result history, final-run summary redesign, broad Profile/current-test visual redesign, autosave/recovery, batch/queue analysis, detector changes or Result Review overlay changes. S6 detector benchmarks, soak/long-duration validation, Windows/manual GUI acceptance and PyInstaller packaging are intentionally not run or inferred from this source-tree slice.

## Next gate

`S8-A Repeated-Test Run Identity + Output Naming Repair Fresh Exact-Head Auditor`
