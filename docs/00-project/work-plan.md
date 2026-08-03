# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S8 — Repeated-Test Workflow & Result Management`
**Milestone status:** `ACTIVE — S8-A/B1/B2 audited, merged and closed; S8-C1 implementation complete, awaiting audit; S8-C2 unstarted`
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
**Current S8-B1 result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #70 @ 1704c71b72b8851c09a669badda60b14ddecd1ef`
**Current S8-B2 result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #71 @ 067e599bb8fa727e94df360be30560cf73d8a599`
**Current S8-C1 result:** `IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT AUDIT`
**Current S8-C2 result:** `UNSTARTED — PROFILE/CURRENT-TEST VISUAL SEPARATION DEFERRED TO ITS OWN SLICE`
**Current gate:** `S8-C1 Final Run Summary & Completion Actions Fresh Exact-Head Auditor`
**Successor milestone:** `S9 — Operational Recovery & UX Polish`

This document owns the current execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6 remains closed against the accepted real-video/runtime scope, and S7 remains independently audited, merged and closed with its stored-result, decoded-timeline, derivative-publication, lifecycle and Qt raster-boundary contracts unchanged. S8 remains active: S8-A, S8-B1 and S8-B2 are independently audited, accepted and merged through PR #69, PR #70 and PR #71. S8-C1 is now implementation-complete on its focused Worker branch and awaiting independent audit. Its completion presentation snapshots current-test `run_name`, Profile name and source-video identity only from the finalized `ResultBundleReader` bundle; overall/Glass judgment and warning/error counts remain sourced from the completed `AnalysisResult`, and result location remains the committed output path. Optional bundle-summary read failure is non-fatal and falls back to explicit unavailable identity fields without changing `ANALYZED` or `last_result_path`. Review/report/folder actions remain bound to the completed output, and same-Profile continuation still reloads that saved bundle before the existing transactional replacement workflow. S8-B1/B2 navigation caches remain non-authoritative. Broader Workbench Profile/current-test visual separation is explicitly deferred to unstarted `S8-C2`. Autosave/recovery remains S9 scope and batch execution is not introduced. The exact next gate is `S8-C1 Final Run Summary & Completion Actions Fresh Exact-Head Auditor`. Windows/manual GUI, PyInstaller one-folder validation and audio preservation were not run or inferred and remain pending/unclaimed.

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
- S8-B2 Worker evidence: [`../30-quality/s8-b2-persistent-recent-profile-access-evidence.md`](../30-quality/s8-b2-persistent-recent-profile-access-evidence.md)
- S8-C1 Worker evidence: [`../30-quality/s8-c1-final-run-summary-evidence.md`](../30-quality/s8-c1-final-run-summary-evidence.md)
- S6-D4: [`../30-quality/s6-d4-available-corpus-detector-repair.md`](../30-quality/s6-d4-available-corpus-detector-repair.md)
- S6-E: [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
- S6-F: [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

## Latest merged closeout — S8-B2 Persistent Recent Profile Access

| Item | Current state |
|---|---|
| Audit target | PR #71; exact base `789d2646e3355f4486ef902d93565205265ecd39`; exact audited head `c1ffd79bc66f56eb11493156bc86780c33d2876b`; 1 commit / exactly 10 complete-PR changed files |
| Profile authority | `RecentProfileHistory` stores only navigation/display metadata in application user data. Recent and manual access both enter `WorkbenchController.load()` → `LoadRecipeUseCase` → `JsonRecipeRepository.load()`, so the loaded `.oilrecipe` remains authoritative and cached names cannot override Recipe truth. |
| Persistence/failure boundary | History is bounded newest-first, deduplicated by normalized path, stale/corrupt/unsupported/unreadable state is isolated, and same-directory temporary + atomic replacement preserves prior valid user-state on write failure without mutating Profile files. |
| Registration/menu lifecycle | Successful load/save registers only after the authoritative operation succeeds; failed load is not promoted; history failure is non-fatal; the pending recent path is consumed before loading so failure cannot carry into a later manual selection. |
| Fresh validation | Exact-head focused Profile persistence/Workbench/same-profile/S8-A/S8-B1/S7 suite: `100 passed`; independent authoritative-name/pending-path and atomic/non-mutation probes passed |
| Fresh documentation checks | Authoritative S8-B2 semantics passed; 56 applicable relative links passed; complete-PR `git diff --check` passed |
| Merge | PR #71 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `067e599bb8fa727e94df360be30560cf73d8a599` |
| Synchronization | Registered primary checkout synchronized cleanly to `main @ 067e599bb8fa727e94df360be30560cf73d8a599` before this documentation Close |
| Claim boundary | S8-B1 result history, S8-A current-test identity, same-profile and S7 stored-result/annotated-MP4 contracts remain unchanged; no detector/soak, Windows/manual GUI, PyInstaller or S9 PASS is inferred |
| Next gate | S8-B2 remains closed; current project gate is `S8-C1 Final Run Summary & Completion Actions Fresh Exact-Head Auditor`. |

## Latest merged closeout — S8-B1 Persistent Recent Result Access

| Item | Current state |
|---|---|
| Audit target | PR #70; exact base `90caa9936a99edb91b1fc34dde58dfda17ceabf5`; exact audited head `1c68d00a8398d140dc0f6338517e2f92c473eae8`; 1 commit / exactly 12 complete-PR changed files |
| Persistence and authority | `RecentResultHistory` stores bounded schema-versioned display/navigation metadata only in application user data. Finalized/manual-opened results are validated through authoritative Result Review loading before cache refresh; official result bundles remain immutable. |
| Failure and workflow boundary | Missing/malformed/unsupported/unreadable history fails safely, stale paths are isolated, atomic replacement preserves prior valid history on write failure, and history failure cannot revoke successful analysis. Manual folder selection remains available and historical review does not replace `MainWindow.last_result_path`. |
| Fresh validation | Exact-head focused recent-history/completion/Result Review/same-profile/S8-A/S7 suite: `119 passed`; independent read-failure and atomic-immutability probes passed |
| Fresh documentation checks | Authoritative S8-B1 semantics passed; 58 applicable relative links passed; complete-PR `git diff --check` passed |
| Merge | PR #70 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `1704c71b72b8851c09a669badda60b14ddecd1ef` |
| Synchronization | Registered primary checkout synchronized cleanly to `main @ 1704c71b72b8851c09a669badda60b14ddecd1ef` before this documentation Close |
| Claim boundary | S8-A run identity/output naming and S7 stored-result/annotated-MP4 authority remain unchanged; no detector/soak, Windows/manual GUI, PyInstaller or later-S8/S9 PASS is inferred |
| Next gate | S8-B1 remains closed; current project gate is `S8-C1 Final Run Summary & Completion Actions Fresh Exact-Head Auditor`. |

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
| Next gate | S8-A remains closed; current project gate is `S8-C1 Final Run Summary & Completion Actions Fresh Exact-Head Auditor`. |

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
- `P1 current next gate`: `S8-C1 Final Run Summary & Completion Actions Fresh Exact-Head Auditor`; S8-C1 is implementation-complete and S8-C2 Profile/current-test visual separation remains unstarted.
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
