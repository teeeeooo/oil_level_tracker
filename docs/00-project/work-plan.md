# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S8 — Repeated-Test Workflow & Result Management`
**Milestone status:** `ACTIVE — S8-A audited, merged and closed; S8-B1 implementation complete / awaiting audit`
**S6 status:** `DONE — accepted real-video/runtime scope`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-D1 result:** `S6-D1 DOMAIN-OWNER RESPONSE: RECEIVED FOR 15 EXACT REVIEW FRAMES`
**Current S6-D2 result:** `S6-D2 USER-CONFIRMED PRODUCT TRUTH: AUDITED AND ACCEPTED`
**Current S6-D3 result:** `CURRENT-SAMPLE OFFICIAL BASELINE AND AVAILABLE-CORPUS POLICY: AUDITED AND ACCEPTED`
**Current S6-D4 result:** `AVAILABLE-CORPUS DETECTOR ACCURACY REPAIR: AUDITED, ACCEPTED AND MERGED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — REPRESENTATIVE THROUGHPUT RECORDED`
**Current S7 result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #68 @ 8846c272842df099f5849ea71686c3370248fc03`
**Current S8-A result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #69 @ c8164f00c6f1080f9fc8a3829b3991acc9c7a90b`
**Current S8-B1 result:** `PERSISTENT RECENT RESULT ACCESS IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT AUDIT`
**Current gate:** `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor`
**Successor milestone:** `S9 — Operational Recovery & UX Polish`

This document owns the current execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6 remains closed against the accepted real-video/runtime scope, and S7 remains independently audited, merged and closed with its stored-result, decoded-timeline, derivative-publication, lifecycle and Qt raster-boundary contracts unchanged. S8 remains active: S8-A is independently audited, accepted, native guarded-squash-merged and closed through PR #69. S8-B1 now implements only persistent recent-result access: a bounded newest-first registry lives in application user data, never inside result bundles; successful analysis completion re-reads the finalized bundle through `ResultBundleReader` before registration; successful Result Review opens refresh cached display metadata from the Viewer-owned authoritative `ReviewBundle`; stale/moved paths are disabled without blocking other entries; missing/corrupt history is a normal fail-safe condition; and atomic replacement protects previously valid history from partial writes. `last_result_path` remains the current-workbench completion/report pointer and is not replaced by manually reviewed history. Recent Profile management, final-run summary redesign, broader Profile/current-test visual redesign, autosave/recovery and batch execution remain unstarted. The exact next gate is `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor`. Windows/manual GUI, PyInstaller one-folder validation and audio preservation were not run or inferred and remain pending/unclaimed.

## Evidence owners

- S6-A: [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
- S6-B: [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
- S6-C: [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
- Domain-owner addendum: [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
- S6-D1: [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
- S6-D2: [`../30-quality/s6-d2-user-confirmed-product-truth.md`](../30-quality/s6-d2-user-confirmed-product-truth.md)
- S6-D3: [`../30-quality/s6-d3-official-accuracy-baseline.md`](../30-quality/s6-d3-official-accuracy-baseline.md)
- S7 Worker evidence: [`../30-quality/s7-annotated-mp4-export-evidence.md`](../30-quality/s7-annotated-mp4-export-evidence.md)
- S8-A Worker evidence: [`../30-quality/s8-a-run-identity-output-naming-evidence.md`](../30-quality/s8-a-run-identity-output-naming-evidence.md)
- S8-B1 Worker evidence: [`../30-quality/s8-b1-persistent-recent-result-access-evidence.md`](../30-quality/s8-b1-persistent-recent-result-access-evidence.md)
- S6-D4: [`../30-quality/s6-d4-available-corpus-detector-repair.md`](../30-quality/s6-d4-available-corpus-detector-repair.md)
- S6-E: [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
- S6-F: [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

## Current implementation — S8-B1 Persistent Recent Result Access

| Item | Current state |
|---|---|
| Persistence owner | `RecentResultHistory` stores schema-versioned bounded metadata in the existing application `user_data_dir()` owner; result bundle trees are never written or edited for history management. |
| Registration | Finalized analysis results are re-read through `ResultBundleReader` before registration. Successfully opened Result Review bundles refresh history from the Viewer-owned authoritative `ReviewBundle`; cached metadata is display-only. |
| Ordering and failures | Newest-first insertion order is deterministic, duplicate paths move to the front, the default bound is eight entries, stale paths stay isolated/disabled, missing or malformed storage reads as empty, and writes use same-directory temporary files plus atomic replace. |
| Compatibility | Manual folder selection remains available. History opens do not replace `MainWindow.last_result_path`, so current completion/report behavior remains unchanged. S8-A `run_name`, S7 Result Review and annotated-MP4 contracts remain unchanged. |
| Deferred | Recent Profile management, favorites/tags/search, result moving/deletion/comparison, final-run summary redesign, autosave/recovery and batch analysis remain outside S8-B1 and unstarted. |
| Next gate | `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor` |

## Latest merged closeout — S8-A Repeated-Test Run Identity + Output Naming

| Item | Current state |
|---|---|
| Audit target | PR #69; exact base `5f03d2349d871c354b2670543cec96738cd8e729`; exact final audit head `197c86b9e94632c4a01ec3903c871df762b09f36`; 4 commits / exactly 18 complete-PR changed files |
| Final repair scope | `96adc21f781f654c9104d52624143270b66cd5d3 → 197c86b9e94632c4a01ec3903c871df762b09f36` changed exactly seven files and made normal Workbench video-open reader/metadata preparation transactional |
| Accepted identity contract | Human `run_name` is session/current-test state, never Recipe/Profile identity; successful normal or same-profile replacement starts fresh, while dialog cancel and reader-factory/metadata failure preserve the active test identity and Workbench state |
| Reader/resource boundary | Failed acquired candidates are closed without replacing or closing the active reader; successful candidate preparation commits reader/session state before the previous reader is released |
| Output/persistence boundary | Safe Unicode-aware naming, path-separator sanitization, deterministic collision suffixes and temporary→validated→atomic bundle publication remain intact; pre-S8 persisted data remains readable and UUID `run_id` stays the technical identity |
| Fresh validation | Exact-head focused S8-A/Workbench/CLI/Result Review/S7 suite: `104 passed`; independent factory-failure, metadata-failure and successful-commit lifecycle probes passed |
| Fresh documentation checks | Authoritative S8 semantics passed; 50 applicable relative links passed; complete-PR `git diff --check` passed |
| Merge | PR #69 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `c8164f00c6f1080f9fc8a3829b3991acc9c7a90b` |
| Synchronization | Registered primary checkout synchronized cleanly to `main @ c8164f00c6f1080f9fc8a3829b3991acc9c7a90b` before this documentation Close |
| Claim boundary | S7 stored-result/annotated-MP4 authority remains unchanged; no S6 benchmark/soak, Windows/manual GUI, PyInstaller or unrelated later-S8/S9 PASS is inferred |
| Next gate | S8-A remains closed; current project gate is `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor`. |

## Final Windows and packaging release obligation

The following scope is still pending and not accepted. It is no longer an S6 blocker; it is the final release gate after the required product feature work:

- run the Windows canonical suite on the supported Python 3.14 environment;
- complete manual Workbench, preflight, analysis and Result Review acceptance at the required Windows DPI scales;
- build, relocate and execute the PyInstaller one-folder package on a clean Windows PC without Python or separately bundled font files;
- verify relocated Jinja, Qt, OpenCV and Matplotlib resources plus Korean font behavior;
- exercise Unicode/long paths, active file locking, cancellation and application close, proving video/output/debug handles are released;
- preserve missing real-video categories as residual validation gaps unless new authoritative evidence becomes feasible;
- do not infer Windows/manual/package PASS from macOS, source-tree or other-platform evidence.

## Product priority and sequence

- `P0 completed`: S7 annotated MP4 export is audited, merged and closed.
- `P1 current next gate`: `S8-B1 Persistent Recent Result Access Fresh Exact-Head Auditor`; implementation is complete, while recent Profile management and remaining S8 work are still unstarted.
- `P2`: after S8, select operational recovery and UX improvements based on observed user effect.
- `P3`: lower-priority geometry/Wizard/Workbench polish remains backlog unless explicitly promoted.
- Final release: S10 Windows/manual GUI and one-folder packaging validation remains mandatory after the required product feature set.

## Retained contracts and risks

- Product `.oiltruth`, frozen D3 datasets/baseline evidence, original MP4s, provisional truth and Recipe snapshots remain immutable validation inputs.
- No filename, hash, Recipe ID, frame number or sample identity may become detector logic.
- Missing scratch/surface-defect, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive-motion, structural rim/paired-line field scenes, clean full/empty no-interface, dropout/reacquisition and broader field-video categories remain `not_evaluated` where authoritative denominators are absent.
- S6-F is accepted only for its exact one-hour macOS source-tree workload; it does not establish Windows, packaging, multi-Glass scaling or infinite-duration stability.
- S7 is `DONE`: annotated-video encoding and both bounded decoded-timeline publication repairs were fresh exact-head audited and merged through PR #68; preserve those accepted contracts through S8/S9 and the final S10 release gate.
- S9 is a selection/UX milestone: its P2 candidates are not all precommitted, and P3 backlog items are not mandatory release prerequisites unless explicitly promoted.

## Intentional non-runs retained from the S6-D4 close

The D4 Auditor did not rerun the accepted one-hour soak, Windows/manual GUI acceptance, packaging/PyInstaller acceptance or an unrelated canonical suite. The frozen D3 baseline was not regenerated because its preserved SHA-256 and source ancestry remained valid. This reconciliation changes only product sequencing: Windows/manual and packaging work remains pending as the final release gate and is not inferred from macOS evidence.
