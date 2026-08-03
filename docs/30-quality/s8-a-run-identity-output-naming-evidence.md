# S8-A Repeated-Test Run Identity + Output Naming Evidence

**Status:** `IMPLEMENTED + NORMAL-OPEN TRANSACTION REPAIR — awaiting fresh exact-head audit`

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
- Normal Workbench video replacement now prepares the candidate reader and metadata before any active-reader/session commit. Reader-factory failure leaves the existing Workbench untouched; metadata failure closes the acquired candidate and preserves the previous active reader open, along with the complete session/state including `run_name` and Recipe/Profile state. After preparation succeeds, the candidate becomes active, `run_name` resets to `""`, session video fields are updated, and only then is the previous reader closed. MainWindow success synchronization therefore displays a blank `현재 시험 이름`, while failure leaves the prior UI/session identity intact.
- CLI `analyze` remains compatible and accepts optional `--run-name` for the same metadata/naming contract.

## Focused validation

The original S8-A implementation recorded a `97 passed` targeted source-tree suite, and the preceding successful-open identity repair recorded a `26 passed` exact-head targeted suite. Those results remain historical evidence for unchanged output naming, persistence and run-identity ownership contracts.

This transaction defect was independently reproduced at exact starting head `96adc21f781f654c9104d52624143270b66cd5d3`. On metadata failure, the candidate reader had already become active, the previous reader had been closed, and the failed candidate remained open; session/state/`run_name`/Recipe had not yet changed. Strengthened controller/UI regressions failed on exactly those ownership assertions before the source repair (`2 failed, 15 passed`).

Current transaction-repair validation:

- invalidated Workbench + MainWindow lifecycle files: `17 passed`;
- targeted S8-A suite covering session ownership, normal-open success/failure/cancel transaction behavior, same-profile reset/non-regression, MainWindow synchronization and CLI compatibility: `23 passed`;
- direct post-repair reproduction confirmed metadata failure keeps the previous reader active and open, closes the candidate, and preserves session/state/`run_name`/Recipe; successful open installs the candidate, closes the previous reader and resets `run_name` to `""`.

The broader output-naming, persisted-bundle compatibility, S7 export, detector, soak/long-duration, Windows/manual GUI and PyInstaller evidence was not rerun because this repair changes only normal Workbench reader/metadata commit ordering.

Repair documentation validation checked 50 applicable relative links across the authoritative S8-A/current-state documents with no missing targets, and `git diff --check` passed.

## Explicit non-scope and non-runs

S8-A does not implement recent-profile/history UI, recent-result history, final-run summary redesign, broad Profile/current-test visual redesign, autosave/recovery, batch/queue analysis, detector changes or Result Review overlay changes. S6 detector benchmarks, soak/long-duration validation, Windows/manual GUI acceptance and PyInstaller packaging are intentionally not run or inferred from this source-tree slice.

## Next gate

`S8-A Repeated-Test Run Identity + Output Naming Fresh Exact-Head Auditor`
