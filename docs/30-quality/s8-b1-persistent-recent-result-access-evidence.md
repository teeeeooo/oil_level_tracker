# S8-B1 Persistent Recent Result Access — Worker Evidence

**Status:** `IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT AUDIT`

## Scope and identity

- Repository: `teeeeooo/oil_level_tracker`
- Registered checkout: `/Users/sunjaekim/Developer/oil_level_tracker`
- Starting branch: `main`
- Starting exact `HEAD == origin/main`: `90caa9936a99edb91b1fc34dde58dfda17ceabf5`
- Worker branch: `feature/s8-b-recent-result-access`
- Next gate: `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor`

S8 remains `ACTIVE`. S8-A remains independently audited, merged and closed. This slice implements only persistent recent-result access; recent Profile management and the remaining S8 work are unstarted.

## Persistence ownership

`RecentResultHistory` owns schema-versioned recent-result metadata in the existing application [`user_data_dir()`](../20-architecture/implementation-decisions.md) boundary. The default registry is `recent_results.json`, with a default maximum of eight entries. Official result bundles are never used as history storage and are never mutated by registration, ordering, deduplication or stale-entry handling.

Entries cache only the bundle root path plus display hints already available from an authoritative `ReviewBundle`: current-test `run_name`, Profile name and source-video basename. They are application/user state, not analysis truth.

## Registration and authority

A successfully finalized analysis first commits normal `ANALYZED` state and `last_result_path`, then the completion coordinator re-reads the finalized output through `ResultBundleReader` before it becomes recent. History failure is non-fatal and cannot revoke successful analysis completion.

A result successfully opened through the Workbench Result Review chooser may also become recent. After `viewer.load_bundle()` succeeds, cached display metadata is refreshed only from the Viewer-owned authoritative `ReviewBundle`. Selecting history therefore never bypasses the existing Result Review reader, schema checks, CSV parsing, bundle-path protections or source-video resolution contracts.

## Ordering, deduplication and failure behavior

- insertion is deterministic newest-first;
- re-registering the same normalized path moves that entry to the front and refreshes its display cache;
- history is bounded and does not scan result directories;
- Unicode paths and normal Windows-style source-video paths are retained;
- missing history is a normal first-run condition;
- malformed, unreadable or unsupported history fails safe as an empty history;
- a stale/deleted/moved bundle path disables only that row in the chooser;
- writes use a same-directory unique temporary file, flush/fsync and `os.replace`; replacement failure cleans the temporary file and preserves the previous valid registry.

The Result Review chooser shows several persisted entries, keeps `다른 결과 폴더 선택`, and keeps the current-session `last_result_path` as a fallback row when it is not yet in persistent history. Manual/history review does not assign `last_result_path`; that pointer remains owned by current completion/report actions.

## Result-bundle immutability evidence

The storage unit coverage records a bundle containing an immutable marker, writes recent history, and verifies the marker bytes and bundle directory contents remain unchanged. The history file is created only at the separately supplied user-state location. Deleting the bundle afterward changes only availability reporting; no cleanup write is attempted inside the former bundle path.

This preserves the [Result Review Viewer](../10-product/result-review-viewer-plan.md) rule that official bundles remain read-only review truth and the [S8 UX contract](../10-product/ux-improvement-plan.md) separation between Profile/current-test/result-history ownership.

## Fresh validation

Narrow registry/completion/chooser validation passed:

`17 passed in 4.83s`

Targeted S8-B1 / Result Review compatibility validation passed:

`89 passed in 14.24s`

The targeted suite covered recent-history storage, authoritative `ResultBundleReader`, analysis completion, persistent chooser/restart behavior, Result Review coordinator/workbench/window/enhancement flows, same-profile compatibility, result-bundle output, S7 annotated-MP4 controller/exporter compatibility and UI import boundaries.

Architecture/import checks in that suite passed. Documentation validation checked 58 applicable relative links across the changed authoritative/evidence documents with no missing targets, and `git diff --check` passed.

## Intentional non-runs and deferred work

The Worker did not run detector benchmarks, S6 soak/long-duration workloads, Windows/manual GUI validation, PyInstaller/one-folder packaging, unrelated canonical suites or broad field-video accuracy work. No PASS is inferred for those gates.

The following remain intentionally unimplemented: recent Profile history, favorites/pinning/tags, search/filter/database, result moving/deletion, result comparison, final-run summary redesign, autosave/recovery and batch analysis. No filesystem-wide result discovery or database was introduced.

## Source-completing documents

- [Project roadmap](../00-project/roadmap.md)
- [Current work plan](../00-project/work-plan.md)
- [UX improvement plan](../10-product/ux-improvement-plan.md)
- [Result Review Viewer plan](../10-product/result-review-viewer-plan.md)

Exact successor: `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor`.
