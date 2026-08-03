# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S9 — Operational Recovery & UX Polish`
**Milestone status:** `ACTIVE — S8 complete; S9-A audited, merged and closed; S9-B selected next; S9-C follows`
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
**Current S8-C1 result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #72 @ b485bf85a4d28c604c4d8ac2579fbe2e2f186857`
**Current S8-C2 result:** `ORCHESTRATOR EXACT-HEAD GATE PASS; NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #73 @ e90310a63faad2a20561ba0d5221432cc1e1c4fb`
**Current S9-A result:** `AUDITED, ACCEPTED, NATIVE GUARDED-SQUASH-MERGED AND CLOSED — PR #74`
**Current gate:** `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`
**Successor S9 slice:** `S9-C — Field ↔ Overlay Interaction Polish`
**Successor milestone:** `S10 — Windows and Packaging Final Release Gate`

This document owns the current execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6 and S7 remain closed against their accepted validation/export contracts, S8 is complete through PR #73, and S9 remains active. S9-A passed fresh exact-head Lane C audit, merged through PR #74 and completed bounded Close; its accepted Profile dirty/save/close lifecycle contract remains unchanged. Based on post-S9-A user impact, `S9-B — Workbench Analysis-Area Zoom, Pan & Fit` is now the selected implementation handoff, followed by `S9-C — Field ↔ Overlay Interaction Polish`, which also owns ellipse resize-handle visual polish without changing the SSOT geometry contract. After S9-B and S9-C, the project proceeds to mandatory `S10 — Windows and Packaging Final Release Gate`. Autosave/abnormal-exit recovery is deferred to post-S10 reassessment and is not an S9 release prerequisite. Windows/manual GUI, Windows DPI and PyInstaller acceptance remain pending/unclaimed until S10; the manual checklist will receive source-completing S9-B/S9-C acceptance updates in their implementation PRs, not in this planning-only reconciliation.

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
- S8-C2 Worker evidence: [`../30-quality/s8-c2-profile-current-test-separation-evidence.md`](../30-quality/s8-c2-profile-current-test-separation-evidence.md)
- S9-A Worker evidence: [`../30-quality/s9-a-unsaved-profile-close-guard-evidence.md`](../30-quality/s9-a-unsaved-profile-close-guard-evidence.md)
- S6-D4: [`../30-quality/s6-d4-available-corpus-detector-repair.md`](../30-quality/s6-d4-available-corpus-detector-repair.md)
- S6-E: [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
- S6-F: [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

## Latest merged closeout — S9-A Unsaved Profile Change Tracking & Close Confirmation

| Item | Current state |
|---|---|
| Audit target | PR #74; exact base `d5fb35f072613b07949fd83ffb67c93783028be9`; exact audited head `205ad12453bb75d94710f7f29a48aa7bcf389953`; 3 commits / exactly 19 complete-PR changed files; Lane C |
| Profile dirty authority | User Profile state is compared independently from `WorkbenchState` and `AnalysisSession`; save-generated `updated_at` is excluded, while other persisted Recipe identity/metadata/content remains part of dirty truth. `edit → save → undo → redo` returns clean only when user Profile content again matches the persisted state. |
| Save / failure boundary | Existing MainWindow → WorkbenchController → SaveRecipeUseCase → repository authority remains intact; successful save persists a fresh `updated_at`, failed publication restores it and does not establish a clean baseline. |
| Close lifecycle | Dirty Save/Discard/Cancel, Save-As cancellation and save failure preserve rejected-close state; Result Review, completion UI, prepared same-Profile work and preflight clean up only after accepted application close. |
| Fresh Auditor validation | Exact-head focused S9-A + adjacent S8/Qt boundary suite: `55 passed`; independent F1 probe passed; 49 applicable relative links and complete-PR `git diff --check` passed. |
| Merge / synchronization | PR #74 passed fresh Lane C audit, was marked Ready, native exact-base/head guarded-squash-merged, and the registered primary checkout was synchronized cleanly to authoritative `main` before this documentation Close. |
| Claim boundary | S9-A did not implement zoom/pan/fit, field↔overlay interaction, ellipse-handle polish, autosave/recovery, detector/soak, Windows/manual GUI, Windows DPI or PyInstaller. S9-B and S9-C are now selected successor slices but remain unimplemented; autosave/recovery is deferred to post-S10 reassessment. |
| Next gate | `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`. |

## Latest merged closeout — S8-C2 Profile/Current-Test Visual Separation

| Item | Current state |
|---|---|
| Gate target | PR #73; exact base `482158f9ca381271d2824759ceca8f1e253be50f`; exact gated head `844d3f600aec2c2f26f0ec04525504167a00db6e`; 1 commit / exactly 10 complete-PR changed files; presentation-only Lane B |
| Ownership presentation | Workbench displays Profile identity from existing `InspectionRecipe`/`recipe_path`, labels Glass list/settings as Profile-owned, and labels video/`run_name`/range/compressor/sampling as current-test `AnalysisSession` state. No duplicate authority was introduced. |
| Compatibility boundary | `.oilrecipe`, session/result persistence, load/save, same-Profile, recent-access, completion and Result Review owners were unchanged. Existing 1280×760 source-tree layout and UI import boundaries remained passing. |
| Fresh Orchestrator gate | Exact-head S8-C2 + Workbench usability + UI import subset: `21 passed`; 54 applicable relative links passed; complete-PR `git diff --check` passed |
| Merge | PR #73 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `e90310a63faad2a20561ba0d5221432cc1e1c4fb` |
| Synchronization | Registered primary checkout synchronized cleanly to `main @ e90310a63faad2a20561ba0d5221432cc1e1c4fb` before this documentation Close |
| Claim boundary | No persisted/workflow responsibility changed and no detector/soak, Windows/manual GUI, Windows DPI or PyInstaller PASS is inferred |
| Next gate | S8 is complete; current project gate is `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`. |

## Latest merged closeout — S8-C1 Final Run Summary & Completion Actions

| Item | Current state |
|---|---|
| Audit target | PR #72; exact base `77298e763185f08b940f73b315e8c36b91ef5538`; exact audited head `741faa1ec979e574e15d2169e3c426645135c9e7`; 1 commit / exactly 11 complete-PR changed files |
| Finalized-run identity | Completion identity snapshots current-test `run_name`, saved Profile name and source-video identity from the finalized `ResultBundleReader` bundle only; later mutable Workbench or source-object changes cannot rewrite the frozen summary. |
| Judgment/fallback boundary | Overall/Glass judgments and warning/error counts remain the completed `AnalysisResult`; committed output remains the action/location authority. Optional bundle-metadata read failure degrades to explicit unavailable identity without revoking `ANALYZED` or `last_result_path`. |
| Completion actions | Review/report/folder remain captured-output-bound; same-Profile independently reloads the finalized bundle and enters the existing transactional replacement path. Duplicate-action/error/close handling remains unchanged. |
| Fresh validation | Exact-head focused completion/Result Review/same-profile/S8-A/S8-B1/B2/S7 suite: `107 passed`; independent frozen-summary and fallback/action-authority probes passed |
| Fresh documentation checks | Authoritative S8-C1 semantics passed; 57 applicable relative links passed; complete-PR `git diff --check` passed |
| Merge | PR #72 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `b485bf85a4d28c604c4d8ac2579fbe2e2f186857` |
| Synchronization | Registered primary checkout synchronized cleanly to `main @ b485bf85a4d28c604c4d8ac2579fbe2e2f186857` before this documentation Close |
| Claim boundary | Official bundles remain immutable; recent-result/Profile caches remain non-authoritative; S7/S8-A/S8-B1/S8-B2 contracts remain unchanged; no detector/soak, Windows/manual GUI, PyInstaller or S9 PASS is inferred |
| Next gate | S8-C1 remains closed; current project gate is `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`. |

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
| Next gate | S8-B2 remains closed; current project gate is `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`. |

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
| Next gate | S8-B1 remains closed; current project gate is `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`. |

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
| Next gate | S8-A remains closed; current project gate is `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`. |

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
- `P1 completed`: S8 repeated-test workflow/result management is merged and closed through S8-C2 / PR #73.
- `P2 current next gate`: `S9-B — Workbench Analysis-Area Zoom, Pan & Fit Worker`; S9-C Field ↔ Overlay Interaction Polish follows S9-B.
- `P3`: lower-priority geometry/Wizard/Workbench polish remains backlog unless explicitly promoted; autosave/abnormal-exit recovery is separately deferred to post-S10 reassessment.
- Final release: S10 Windows/manual GUI and one-folder packaging validation remains mandatory after S9-B and S9-C.

## Retained contracts and risks

- Product `.oiltruth`, frozen D3 datasets/baseline evidence, original MP4s, provisional truth and Recipe snapshots remain immutable validation inputs.
- No filename, hash, Recipe ID, frame number or sample identity may become detector logic.
- Missing scratch/surface-defect, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive-motion, structural rim/paired-line field scenes, clean full/empty no-interface, dropout/reacquisition and broader field-video categories remain `not_evaluated` where authoritative denominators are absent.
- S6-F is accepted only for its exact one-hour macOS source-tree workload; it does not establish Windows, packaging, multi-Glass scaling or infinite-duration stability.
- S7 is `DONE`: annotated-video encoding and both bounded decoded-timeline publication repairs were fresh exact-head audited and merged through PR #68; preserve those accepted contracts through S8/S9 and the final S10 release gate.
- S9's selected remaining release sequence is S9-B then S9-C; autosave/abnormal-exit recovery is deferred to post-S10 reassessment, and unrelated P3 backlog items remain non-prerequisites unless explicitly promoted.

## Intentional non-runs retained from the S6-D4 close

The D4 Auditor did not rerun the accepted one-hour soak, Windows/manual GUI acceptance, packaging/PyInstaller acceptance or an unrelated canonical suite. The frozen D3 baseline was not regenerated because its preserved SHA-256 and source ancestry remained valid. This reconciliation changes only product sequencing: Windows/manual and packaging work remains pending as the final release gate and is not inferred from macOS evidence.
