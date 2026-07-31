# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E feature-head result:** `SOAK SCREENING: NO OBVIOUS RESOURCE LEAK`
**Current gate:** `S6-E Bounded Runtime Soak and Resource-Leak Screening Fresh Exact-Head Auditor`
**Pending accuracy gate:** `S6-D User-Confirmed Truth and Category-Balanced Detector-Accuracy Evidence`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Task-start exact head:** `a13b73b7b48aa6fecc0e7afb71d8dd1080ae5622`
**Task-start exact parent:** `dc6d24448c30e30e1f3e016b397d8522ec17bd05`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-E has completed a bounded feature-head screening, but the result remains unmerged and awaiting fresh independent exact-head audit. It does not replace S6-D accuracy evidence or the later controlled-idle, official long-duration, Windows and packaged-runtime gates.

## Latest feature-head state

| Item | Current state |
|---|---|
| S6-E execution | Two sequential production CLI runs completed against local-only repeated sample3 and sample4 inputs |
| Screening result | `SOAK SCREENING: NO OBVIOUS RESOURCE LEAK` on the feature head; not yet independently audited or merged |
| Runtime observations | Both analyzers exited `0`, completed lifecycle `1/6–6/6`, finalized readable bundles, left no owned process, and stopped output growth after finalization |
| RSS criterion | Post-warm-up last-quarter median increase was `0.56 MiB / 0.35%` for sample3 and `0.46 MiB / 0.27%` for sample4; neither approached the `64 MiB` and `25%` combined review threshold |
| File/resource cleanup | Open-file quarter medians remained `148 → 148`; terminal owned open-file count was zero; no hidden staging, `.tmp`, `.part`, or debug artifact remained |
| Evidence location | Tracked source-completing evidence is linked above; derived videos, telemetry, scripts and bundles remain ignored under `sample/output/` |
| Accuracy status | S6-D product `.oiltruth`, category-balanced evidence and official metrics remain pending; no detector accuracy PASS is recorded |
| Performance limitation | Current Mac workload prevents precise CPU-throughput acceptance; controlled-idle representative-duration and official long-duration gates remain pending |
| Current executable action | Fresh independent exact-head audit of S6-E evidence and generated local artifacts |

## Domain-owner priorities retained

1. Separate Oil–Foam and Foam–Gas boundaries when both phases coexist.
2. Suppress fluorescent reflection, glare and bright bands.
3. Suppress Glass rim, fixed structure and paired horizontal lines.
4. Suppress scratches, stains, fogging and other fixed surface artifacts.
5. Track oscillating real Oil level through fill and drain with bounded temporal reasoning.
6. Keep severe blur, focus loss and camera motion as a lower-priority robustness category.

sample4 is the primary Oil-under-Foam separation diagnostic. sample3 remains a compound-state reference and lower-priority poor-image robustness challenge; it must not drive aggressive weakening of artifact rejection. The looped soak inputs are runtime diagnostics only, and loop seams or re-encoding artifacts are not physical-transition or accuracy evidence.

## Accepted meaning and limitations

- `NO OBVIOUS RESOURCE LEAK` means only that these two short source-tree runs showed no obvious crash, accumulating open files, owned-process residue, threshold-level quarter-median RSS growth, or incomplete bundle finalization.
- Detector result labels stored in the bundles are not truth comparisons and have no accuracy PASS/FAIL meaning for S6-E.
- Domain-owner review has greater physical interpretation authority than the blind provisional annotations, but is not yet bundle-bound product `.oiltruth`.
- Oil level and Foam upper front may coexist as separate physical boundaries. Foam presence must not imply automatic Oil `null`.
- No official MAE, precision, recall, false-positive/negative rate, calibrated level, detector physical-accuracy PASS, CPU throughput, long-duration memory acceptance, Windows acceptance, or packaged-runtime acceptance is claimed.
- S6 remains `ACTIVE`; S7 remains `PLANNED` and must not start until the complete S6 gate passes.

## Pending S6 scope

Still pending and not accepted:

- fresh independent exact-head audit and merge of the S6-E feature-head evidence;
- S6-D user-confirmed product `.oiltruth` and category-balanced official accuracy evidence;
- controlled-idle representative-duration performance and official long-duration CPU/memory stability;
- Windows GUI, manual workflow, DPI and applicable canonical-suite validation;
- PyInstaller one-folder build, relocation and clean Windows PC execution;
- Unicode/long paths, Windows file locking, cancellation and close behavior;
- final independent S6 acceptance and formal Close.

## Retained contracts

- Repository/local samples and blind provisional annotations remain supporting evidence, not canonical truth.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- Field-priority input and soak output do not authorize source repair or threshold tuning without category-balanced evidence.
- Local derived videos, telemetry scripts, telemetry logs and generated bundles remain ignored and must not be committed.
- S5-A Foam independence, S5-B typed observability/temporal ownership and S5-C Qt/headless boundaries remain intact.

## Intentional non-runs

This feature-head work did not run or claim official long-duration, controlled-idle CPU/throughput, Windows, packaging, clean-PC, GUI, DPI, cancellation, Windows file-lock or detector-accuracy acceptance. It did not create or edit product `.oiltruth`, provisional truth, Recipes, original MP4s, source, tests, dependencies, detector settings or thresholds. It did not merge, synchronize the registered checkout, close S6, start S7, or perform existing branch/worktree hygiene.
