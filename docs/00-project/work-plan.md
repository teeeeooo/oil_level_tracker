# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-D1 result:** `S6-D1 REVIEW PACK: AUDITED AND PREPARED — USER CONFIRMATION PENDING`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — EXACT macOS SOURCE-TREE WORKLOAD`
**External pending gate:** `S6-D1 Domain-Owner Mobile Review`
**Current technical gate:** `Controlled-Idle Representative-Duration CPU Throughput Evidence`
**Product truth state:** no product `.oiltruth` exists or was created; user dispositions remain pending
**Pending accuracy gate:** user review, later S6-D2 product truth creation and category-balanced official detector-accuracy evidence
**Pending runtime gate:** controlled-idle representative-duration CPU throughput; Windows/package runtime gates remain pending
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Audited feature head:** `457e946398885a5d8918d279b2b6975b0f381981` over parent `bcac3d66e383dc6e60457bc173d90502fd45878d`
**Merged PR/main:** `#64` / `abe1cae14cb488fd61a4da94f1f11aeddc6a5c38`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
**S6-D1 evidence:** [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
**S6-F feature evidence:** [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-F passed fresh exact-head audit and was guarded-squash-merged. Its acceptance is limited to this exact one-hour macOS source-tree workload. S6-D1 remains an independent external user-review stream, and controlled-idle CPU throughput is the current technical gate.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Exact S6-F run | Recovered ignored root `sample/output/s6-f-one-hour-long-duration/launch-bcac3d6-20260801T053400Z/`; no new soak started |
| Continuous runtime | Analyzer PID `63060` ran `3868.206149 s` (`64 min 28.206 s`), exited `0`, and completed lifecycle `1/6–6/6` plus finalization `4/4` |
| Telemetry | `374` rows with no material interval gaps; post-warm-up RSS `163.625 / 169.625 / 466.734 MiB` min/median/max |
| Memory comparison | `10–20 min` median `164.836 MiB` versus final-10-min `174.367 MiB`: `+9.531 MiB / +5.782%`; existing combined `64 MiB + 25%` diagnostic signal not met |
| Finalization peak | Event-capture/report phase produced a bounded high-memory plateau near `463–467 MiB`, followed by clean process exit; analysis-only pre-output slope remained about `+0.213 MiB/min` |
| Handles/processes | Open-file medians `148 → 148`; analyzer child count stayed `0`; analyzer, runner and `caffeinate` PIDs absent after completion |
| Bundle | `1,617 files / 687,497,078 bytes`; `24,160` tracking rows, `1,607` events, `1,609` PNG decodes and report-local refs all passed fresh inspection |
| Fresh audit | Raw telemetry was independently recomputed; bundle/source/Recipe integrity, owned-process cleanup and two-point post-exit output stability passed without starting another soak |
| Accepted limitation | Analysis-only RSS retained about `+0.213 MiB/min`; finalization held about `463–467 MiB` before exit. Neither is extrapolated to infinite duration or larger event sets |
| Targeted tests | Fresh Auditor result `24 passed in 3.51s`; documentation links, exact diff, evidence hashes and clean-worktree checks exited `0` |
| Merge | PR #64 guarded-squash-merged as `abe1cae14cb488fd61a4da94f1f11aeddc6a5c38` |
| Independent streams | External `S6-D1 Domain-Owner Mobile Review` remains pending; technical next gate is controlled-idle representative-duration CPU throughput evidence |

## Domain-owner priorities retained

1. Separate Oil–Foam and Foam–Gas boundaries when both phases coexist.
2. Suppress fluorescent reflection, glare and bright bands.
3. Suppress Glass rim, fixed structure and paired horizontal lines.
4. Suppress scratches, stains, fogging and other fixed surface artifacts.
5. Track oscillating real Oil level through fill and drain with bounded temporal reasoning.
6. Keep severe blur, focus loss and camera motion as a lower-priority robustness category.

sample4 remains the primary Oil-under-Foam separation diagnostic. sample3 remains a compound-state and lower-priority poor-image robustness reference; it must not become the primary threshold-tuning target. sample1 and sample2 have not previously received user confirmation.

## Accepted meaning and limitations

- S6-D1 prepares review material only. It does not establish product truth.
- Clean images contain no detector or candidate boundary line; comparison images render official detector and agent candidates with different styles.
- Existing sample3/sample4 domain-owner statements have physical interpretation authority but not exact pixel or exact bundle confirmation.
- Foam presence does not justify automatic Oil `null`.
- A possible sample2 no-interface state remains unconfirmed and is not counted as accepted no-interface evidence.
- No official MAE, precision, recall, false-positive/negative rate, calibrated level or detector physical-accuracy PASS is claimed.
- S6-F is accepted only for the exact one-hour macOS source-tree workload. It does not establish controlled-idle CPU throughput, Windows, packaging or infinite-duration stability; the mild analysis-period retention and event-heavy finalization plateau remain explicit limitations.
- S6 remains `ACTIVE`; S7 remains `PLANNED`.

## Pending S6 scope

Still pending and not accepted:

- external S6-D1 domain-owner mobile review and explicit per-ID responses;
- S6-D2 bundle-bound product `.oiltruth` creation from only explicitly approved/corrected frames;
- representative scratch, fogging/stain, clean rim-adjacent boundary, high-quality field fill/drain and clean full/empty no-interface videos;
- category-balanced official detector-accuracy evidence;
- controlled-idle representative-duration CPU throughput evidence;
- Windows GUI, manual workflow, DPI and applicable canonical-suite validation;
- PyInstaller one-folder build, relocation and clean Windows PC execution;
- Unicode/long paths, Windows file locking, cancellation and close behavior;
- final independent S6 acceptance and formal Close.

## Retained contracts

- Repository/local samples and blind provisional annotations remain supporting evidence, not canonical truth.
- Agent candidate manifests must not be loaded or represented as product truth.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- User confirmation cannot be inferred or delegated to a coding agent.
- Local bundles, images, manifests, questionnaires, ZIPs and scripts remain ignored and uncommitted.
- Source repair or threshold tuning requires later category-balanced evidence and separate authority.

## Intentional non-runs

The Worker and Auditor did not start another soak, create or edit product `.oiltruth`, modify provisional truth, Recipes, original MP4s, detector source, tests, dependencies, settings, thresholds or preserved runtime/mobile evidence, or assign a user disposition. They did not calculate detector-accuracy metrics, claim controlled-idle CPU throughput, run Windows/packaging/GUI acceptance, close S6 or start S7. Ignored S6-F raw evidence and S6-D1 mobile-review evidence remain preserved.
