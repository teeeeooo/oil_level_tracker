# S8-A Repeated-Test Run Identity + Output Naming Evidence

**Status:** `IMPLEMENTED — awaiting fresh exact-head audit`

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
- CLI `analyze` remains compatible and accepts optional `--run-name` for the same metadata/naming contract.

## Focused validation

Final targeted source-tree suite:

- session/current-test serialization and old-session compatibility;
- output naming, fallback, unsafe filename handling and deterministic collision behavior;
- same-profile Workbench preparation/commit plus debug-trace reset compatibility;
- official result-bundle finalization, debug bundle output and pre-S8 Result Review reading;
- analysis pipeline/reporting integration and CLI compatibility;
- Workbench UI, same-profile coordinator, completion dialog/coordinator and Result Review GUI compatibility;
- UI import-boundary guard.

Result: `97 passed`.

Documentation relative-link validation passed for all 50 applicable links across the S8-A authoritative/evidence documents, and complete feature `git diff --check` passed.

## Explicit non-scope and non-runs

S8-A does not implement recent-profile/history UI, recent-result history, final-run summary redesign, broad Profile/current-test visual redesign, autosave/recovery, batch/queue analysis, detector changes or Result Review overlay changes. S6 detector benchmarks, soak/long-duration validation, Windows/manual GUI acceptance and PyInstaller packaging are intentionally not run or inferred from this source-tree slice.

## Next gate

`S8-A Repeated-Test Run Identity + Output Naming Fresh Exact-Head Auditor`
