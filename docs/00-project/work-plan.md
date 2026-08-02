# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S8 — Repeated-Test Workflow & Result Management`
**Milestone status:** `PLANNED — not started`
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
**Current gate:** `S8 — Repeated-Test Workflow & Result Management: select and authorize one bounded implementation slice; implementation not started`
**Successor milestone:** `S9 — Operational Recovery & UX Polish`

This document owns the current execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6 remains closed against the accepted real-video/runtime scope, including the bounded available-corpus accuracy claim and residual `not_evaluated` field categories. S7 is now independently audited, merged and closed: the accepted annotated-MP4 path preserves official stored-result authority, fail-closed decoded-timeline coverage, derivative publication safety, bounded lifecycle/resource ownership and the Qt raster boundary. Windows/manual GUI, PyInstaller one-folder validation and audio preservation were not run or inferred and remain pending/unclaimed. S8 is the exact successor gate but implementation has not started; the next action is to select and authorize one bounded repeated-test workflow/result-management slice.

## Evidence owners

- S6-A: [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
- S6-B: [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
- S6-C: [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
- Domain-owner addendum: [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
- S6-D1: [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
- S6-D2: [`../30-quality/s6-d2-user-confirmed-product-truth.md`](../30-quality/s6-d2-user-confirmed-product-truth.md)
- S6-D3: [`../30-quality/s6-d3-official-accuracy-baseline.md`](../30-quality/s6-d3-official-accuracy-baseline.md)
- S7 Worker evidence: [`../30-quality/s7-annotated-mp4-export-evidence.md`](../30-quality/s7-annotated-mp4-export-evidence.md)
- S6-D4: [`../30-quality/s6-d4-available-corpus-detector-repair.md`](../30-quality/s6-d4-available-corpus-detector-repair.md)
- S6-E: [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
- S6-F: [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

## Latest recorded closeout — S7 / Phase 2C-4

| Item | Current state |
|---|---|
| Audit target | PR #68; exact base `3f8b8672509fb14eb047cc0360fcb05c50c9b1d8`; exact final audit head `00e7007ca3aafb2bf38f46bd740a3a12fc81637b`; 4 commits / exactly 15 complete-PR changed files |
| Documentation-only tail | `b3e2ebd8af3506c66c517565bf164795561cb655 → 00e7007ca3aafb2bf38f46bd740a3a12fc81637b` changed exactly four documentation files and no `src/` or `tests/` files |
| Product/source contract | Official stored Result Review state remains the only general-export truth; missing Oil/Foam is not fabricated; debug trace is subordinate; decoded start/internal/end coverage is fail-closed under the `1.5×` nominal-frame-period contract while adjacent valid boundaries and bounded jitter remain usable |
| Publication/lifecycle boundary | Source MP4 and official bundle remain immutable; failed/cancelled export cannot publish a partial final or replace an approved destination; temporary output is atomically published only after verification; reader/writer/debug resources and Qt worker lifecycle remain bounded; UI retains no direct NumPy/OpenCV raster ownership |
| Reused validation | Unchanged source/test tree preserved the authoritative S7/Result Review/export/lifecycle/raster focused `97 passed` and source-video resolver compatibility `7 passed`; rerun was intentionally unnecessary because the final tail was documentation-only and did not invalidate the validation contract |
| Fresh audit checks | Authoritative S7 documentation semantics passed; 46 applicable relative links passed; complete-PR `git diff --check` passed |
| Merge | PR #68 was marked Ready and native exact-base/head `guarded_merge` squash-merged as `8846c272842df099f5849ea71686c3370248fc03` |
| Synchronization | Registered primary checkout synchronized cleanly to `main @ 8846c272842df099f5849ea71686c3370248fc03` before this documentation Close |
| Claim boundary | No Windows/manual GUI/PyInstaller/audio-preservation PASS is inferred; replacement-video duration mismatch remains a warning distinct from MP4 publication completeness |
| Next gate | `S8 — Repeated-Test Workflow & Result Management`: select and authorize one bounded implementation slice; implementation has not started |

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
- `P1 current next gate`: S8 repeated-test workflow and result management; select and authorize one bounded implementation slice before implementation starts.
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
