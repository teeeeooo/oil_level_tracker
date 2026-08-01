# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-D1 result:** `S6-D1 DOMAIN-OWNER RESPONSE: RECEIVED FOR 15 EXACT REVIEW FRAMES`
**Current S6-D2 result:** `S6-D2 USER-CONFIRMED PRODUCT TRUTH: AUDITED AND ACCEPTED`
**Current S6-D3 result:** `CURRENT-SAMPLE OFFICIAL BASELINE AND AVAILABLE-CORPUS POLICY: AUDITED AND ACCEPTED`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — REPRESENTATIVE THROUGHPUT RECORDED`
**Current gate:** `S6-D4 Available-Corpus Detector Accuracy Repair`
**S6-F host-use context:** `user-confirmed idle representative run`; not a telemetry-proven controlled-idle benchmark
**Product truth state:** four bundle-bound `.oiltruth` files with 15 reviewed frames are audited and merged on `main`; `13 corrected + 2 unusable`, `0 confirmed_correct`
**Available-corpus constraint:** the current four real videos are the representative real-video corpus available at this stage; further representative acquisition is externally infeasible and is not an executable S6 gate
**Pending accuracy gate:** `S6-D4 Available-Corpus Detector Accuracy Repair` against the frozen audited D3 dataset/catalog/settings/runtime environment; unavailable categories remain residual risk
**Pending runtime scope:** Windows/package runtime gates remain pending; any stricter CPU-regression comparison is a separate bounded comparison, not a duplicate one-hour soak
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Audited S6-D3 feature head:** `049d0eb49222b904c688686267acb01bf95374a9` over base `47a5516e49872bcb6ffcd9c8147b2dcaa8640218`
**Merged S6-D3 PR/main:** `#66` / `0a3cf34b8d4e0fbd9725a2de24612e62da910e50`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
**S6-D1 evidence:** [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
**S6-D2 evidence:** [`../30-quality/s6-d2-user-confirmed-product-truth.md`](../30-quality/s6-d2-user-confirmed-product-truth.md)
**S6-D3 evidence:** [`../30-quality/s6-d3-official-accuracy-baseline.md`](../30-quality/s6-d3-official-accuracy-baseline.md)
**S6-F feature evidence:** [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-D3 preserves an official current-sample production-detector baseline from all 15 audited S6-D2 truths while excluding the 2 unusable frames from accuracy denominators. Fresh independent audit passed at exact feature head `049d0eb49222b904c688686267acb01bf95374a9`, and PR #66 was native guarded-squash-merged as `main @ 0a3cf34b8d4e0fbd9725a2de24612e62da910e50`. The current four-video set remains non-category-balanced, and missing categories remain explicit `not_evaluated`/unavailable residual validation risk. Further representative acquisition is externally infeasible at this stage, so the current executable gate is bounded available-corpus detector repair against the same frozen D3 evidence; this Close does not start that repair.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Exact audit target | PR #66; base `47a5516e49872bcb6ffcd9c8147b2dcaa8640218`; feature head `049d0eb49222b904c688686267acb01bf95374a9`; exact four-document scope |
| Preserved baseline | `current-sample-official-baseline.json` SHA-256 `fbfc7aa34e00eeb002098f5d79a0f83288bd06aec014ecae3ebd9f177e207692`; `15 total / 13 usable / 2 unusable` |
| Truth and metric audit | All four exported datasets reproduce audited D2 `.oiltruth` annotations exactly; production summaries reproduce exactly. Oil raw/smoothed coverage `0/13`, fill-state accuracy `0/13`, Foam precision `7/7`, recall `7/10`; Oil position, no-interface, shimmer and event metrics remain `not_evaluated` where authoritative denominators are absent |
| Available-corpus policy | Missing categories remain explicit residual risk; synthetic/current-frame substitutes cannot satisfy them. D4 may claim improvement only on the frozen available corpus using identical dataset bytes, catalog, settings and runtime environment, never category-balanced/general-field PASS |
| Reproducibility | Four preserved baseline outputs and four same-dataset `--baseline` reruns are `comparable`; dataset/settings/run fingerprints, complete cases, category summaries and micro/macro aggregates reproduce exactly |
| Fresh audit validation | benchmark/export/reader/metric/CLI suite `67 passed in 8.03s`; changed-document Markdown check `41` relative links with no missing target; audited-head `git diff --check` passed |
| Merge | PR #66 marked Ready and native exact-base/head guarded-squash-merged as `0a3cf34b8d4e0fbd9725a2de24612e62da910e50` |
| Current gate | `S6-D4 Available-Corpus Detector Accuracy Repair`; not started by this Close |

## Domain-owner priorities retained

1. Separate Oil–Foam and Foam–Gas boundaries when both phases coexist.
2. Suppress fluorescent reflection, glare and bright bands.
3. Suppress Glass rim, fixed structure and paired horizontal lines.
4. Suppress scratches, stains, fogging and other fixed surface artifacts.
5. Track oscillating real Oil level through fill and drain with bounded temporal reasoning.
6. Keep severe blur, focus loss and camera motion as a lower-priority robustness category.

sample4 remains the primary Oil-under-Foam separation diagnostic. sample3 remains a compound-state and lower-priority poor-image robustness reference; it must not become the primary threshold-tuning target. S6-D2 now records exact user-confirmed frame truth for sample1 and sample2 as well as the selected sample3/sample4 frames.

## Accepted meaning and limitations

- S6-D1 itself remains review material only; S6-D2 is the separate product-truth materialization layer driven by the explicit user response.
- Clean D1 images contain no detector or candidate boundary line; comparison images render official detector and agent candidates with different styles.
- The selected 15 frames have exact bundle-bound user truth and now support an official current-sample production-detector baseline, but this narrow set is not category-balanced S6 acceptance evidence.
- Foam presence does not justify automatic Oil `null`; the reviewed sample2/sample3/sample4 dual-boundary frames preserve both Oil and Foam truth where user-confirmed.
- The former sample2 possible no-interface candidate is not promoted; the reviewed sample2 frames are user-confirmed as `FOAMING_VISIBLE` with explicit Oil and Foam coordinates.
- S6-D3 reports only metrics with authoritative denominators. Oil detection coverage, fill-state accuracy and Foam metrics are evaluated; Oil position errors, no-interface false-boundary, shimmer false-positive and event metrics remain `not_evaluated` where required.
- No category-balanced detector physical-accuracy PASS is claimed.
- S6-F is accepted only for the exact one-hour macOS source-tree workload. The same run now records representative throughput under user-confirmed idle host use, but not telemetry-proven controlled-idle conditions; it does not establish Windows, packaging, multi-Glass scaling or infinite-duration stability, and the mild analysis-period retention plus event-heavy finalization plateau remain explicit limitations.
- S6 remains `ACTIVE`; S7 remains `PLANNED`.

## Pending S6 scope

Still pending and not accepted:

- `S6-D4 Available-Corpus Detector Accuracy Repair` against the exact frozen D3 dataset/catalog/settings/runtime environment;
- unavailable categories remain residual validation gaps: scratch/surface defects, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive motion, structural rim/paired lines, clean full/empty no-interface, dropout/reacquisition transitions and broader independent field-video coverage;
- category-balanced/general-field official detector-accuracy evidence remains desirable but cannot be claimed from the available corpus; absent-category metrics remain `not_evaluated` unless future external evidence becomes feasible;
- any stricter CPU regression or host-controlled comparison later required by the validation plan, as a separate bounded base/feature comparison rather than a repeated one-hour soak;
- Windows GUI, manual workflow, DPI and applicable canonical-suite validation;
- PyInstaller one-folder build, relocation and clean Windows PC execution;
- Unicode/long paths, Windows file locking, cancellation and close behavior;
- final independent S6 acceptance and formal Close.

## Retained contracts

- Repository/local samples and blind provisional annotations remain supporting evidence, not canonical truth.
- Agent candidate manifests remain candidate/provenance input only; only explicit user-approved/corrected semantics may be materialized through the product truth contract.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- User confirmation cannot be inferred or delegated to a coding agent.
- Local bundles, images, manifests, questionnaires, ZIPs and scripts remain ignored and uncommitted.
- Detector repair or threshold tuning requires explicit separate authority and user-confirmed truth. If further representative acquisition is externally infeasible, bounded available-corpus repair must use the same frozen D3 dataset/settings/environment and must retain unavailable categories as residual `not_evaluated` risk rather than claiming category-balanced/general-field PASS.

## Intentional non-runs

The S6-D3 Worker produced the preserved benchmark evidence described above, and the fresh Auditor consumed that evidence read-only. The Auditor did not run a new full analyzer or detector benchmark, tune or repair detector source/thresholds/settings, modify Recipes, original MP4s, `.oiltruth`, provisional truth or local D3 evidence bytes, synthesize missing categories, or run Windows/packaging/GUI/long-duration acceptance. Fresh work was limited to benchmark-contract tests, direct evidence/metric recomputation, documentation validation and the authorized merge/Close. S6 remains open and D4 is not started by this Close.
