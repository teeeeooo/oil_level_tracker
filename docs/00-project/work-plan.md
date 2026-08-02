# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S7 / Phase 2C-4 — Annotated MP4 Export`
**Milestone status:** `ACTIVE`
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
**Current S7 result:** `IMPLEMENTATION + DECODED-TIMELINE COVERAGE REPAIR COMPLETE ON FEATURE BRANCH — AWAITING FRESH EXACT-HEAD RE-AUDIT`
**Current gate:** `S7 / Phase 2C-4 Annotated MP4 Export Decoded-Timeline Repair Fresh Exact-Head Re-Auditor`
**Successor milestone:** `S8 — Repeated-Test Workflow & Result Management`

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6 is closed against the real-video/runtime scope actually completed: the audited available-corpus detector repair materially improves the frozen four-video D3 corpus while preserving fail-closed structural behavior in the controlled full-/partial-Foam regressions, and the bounded soak plus one-hour macOS source-tree evidence remain accepted. Missing real-video categories remain residual `not_evaluated` risk and no category-balanced or general-field detector-accuracy PASS is claimed. Windows/manual GUI and PyInstaller one-folder validation were not run or inferred; those obligations remain pending as the final Windows and packaging release gate after the product feature sequence. The bounded S7 annotated-MP4 implementation and decoded-timeline coverage repairs are complete on the same feature branch, remain unmerged, and now require the fresh exact-head decoded-timeline repair Re-Auditor gate before roadmap Close or successor work.

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

## Latest recorded closeout — S6-D4

| Item | Current state |
|---|---|
| Audit target | PR #67; base `e04ce64384b31643795448fb6b16e47564a3b7c3`; audited head `f18f78c3cf0058b809965fcaac3d3b449c2678b7`; exactly 9 changed files |
| Latest detector source/test commit | `6b2ea43e8ae62773d4ae6ce17754477d810c78c6`; audited-head tail to `f18f78c…` was documentation-only |
| Preserved D3 baseline | `current-sample-official-baseline.json` SHA-256 `fbfc7aa34e00eeb002098f5d79a0f83288bd06aec014ecae3ebd9f177e207692`; `15 total / 13 usable / 2 unusable` |
| Latest feature evidence | `current-sample-feature.json` SHA-256 `b098a070927ffcf9230a57cd94827a8fe8eedec9a08f591591404c29271cf70c`; all four component comparisons `comparable` |
| Accuracy result | raw/smoothed Oil `0/13 → 7/13`; matched Oil MAE `4.428571 px`; FillState `0/13 → 6/13`; review/unknown `6/13 → 4/13` |
| Foam result | precision `1.000`; recall `0.700`; matched-front MAE unchanged at `47.285714 px` |
| Structural false-Oil disposition | prior full-Foam and partial-Foam defect families are fail-closed across broad independent band, paired-line, narrow-Foam and sector-local probes; accepted Foam alone did not publish numeric Oil |
| Positive Oil preservation | Foam-absent sample1 recovery remains; all five frozen sample4 Oil+Foam frames remain numeric and truth-near; sample3 frame 1035 remains additional recovery |
| Ownership/resource boundary | S5-A retains Foam authority; accepted Foam component mask is current-frame readonly command evidence only; no Foam raster/history is retained in S5-B temporal state; canonical serialized S5-B remains sole numeric Oil owner |
| Fresh audit validation | detector-focused exact-head suite `559 passed, 2 deselected, 1 warning`; the two deselected UI-editor tests require unavailable local pytest-qt fixtures and are not detector failures; broad production-path safety probes and frozen sample4 replay also passed |
| Merge | PR #67 Ready and native exact-base/head guarded-squash-merged as `a046519f28765d69a591dc204e407fbf4298d9be` |
| Synchronization | registered primary checkout synchronized cleanly to `main @ a046519f28765d69a591dc204e407fbf4298d9be` before this documentation Close |
| Claim boundary | bounded available-corpus improvement only; unavailable field categories remain `not_evaluated`; no category-balanced/general-field PASS |
| Gate recorded at D4 close (historical) | `S6 Windows and Packaging Gate`; product sequencing was reconciled later without changing the D4 evidence |

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

- `P0`: S7 annotated MP4 export is the current next implementation work.
- `P1`: S8 repeated-test workflow and result management follows S7.
- `P2`: after S8, select operational recovery and UX improvements based on observed user effect.
- `P3`: lower-priority geometry/Wizard/Workbench polish remains backlog unless explicitly promoted.
- Final release: S10 Windows/manual GUI and one-folder packaging validation remains mandatory after the required product feature set.

## Retained contracts and risks

- Product `.oiltruth`, frozen D3 datasets/baseline evidence, original MP4s, provisional truth and Recipe snapshots remain immutable validation inputs.
- No filename, hash, Recipe ID, frame number or sample identity may become detector logic.
- Missing scratch/surface-defect, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive-motion, structural rim/paired-line field scenes, clean full/empty no-interface, dropout/reacquisition and broader field-video categories remain `not_evaluated` where authoritative denominators are absent.
- S6-F is accepted only for its exact one-hour macOS source-tree workload; it does not establish Windows, packaging, multi-Glass scaling or infinite-duration stability.
- S7 remains `ACTIVE`: annotated-video encoding and both bounded decoded-timeline publication repairs are implemented on PR #68, but fresh exact-head repair re-audit and merge/Close are still pending.
- S9 is a selection/UX milestone: its P2 candidates are not all precommitted, and P3 backlog items are not mandatory release prerequisites unless explicitly promoted.

## Intentional non-runs retained from the S6-D4 close

The D4 Auditor did not rerun the accepted one-hour soak, Windows/manual GUI acceptance, packaging/PyInstaller acceptance or an unrelated canonical suite. The frozen D3 baseline was not regenerated because its preserved SHA-256 and source ancestry remained valid. This reconciliation changes only product sequencing: Windows/manual and packaging work remains pending as the final release gate and is not inferred from macOS evidence.
