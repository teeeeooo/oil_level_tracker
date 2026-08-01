# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-D1 result:** `S6-D1 DOMAIN-OWNER RESPONSE: RECEIVED FOR 15 EXACT REVIEW FRAMES`
**Current S6-D2 result:** `S6-D2 USER-CONFIRMED PRODUCT TRUTH: AUDITED AND ACCEPTED`
**Current S6-D3 result:** `CURRENT-SAMPLE OFFICIAL BASELINE PRODUCED — CATEGORY-BALANCED GATE UNSATISFIED`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — REPRESENTATIVE THROUGHPUT RECORDED`
**Current gate:** `S6 Missing-Category Real-Video Acquisition and User-Truth Extension`
**S6-F host-use context:** `user-confirmed idle representative run`; not a telemetry-proven controlled-idle benchmark
**Product truth state:** four bundle-bound `.oiltruth` files with 15 reviewed frames are audited and merged on `main`; `13 corrected + 2 unusable`, `0 confirmed_correct`
**Pending accuracy gate:** acquire missing representative categories and extend audited user truth before category-balanced official detector-accuracy evidence
**Pending runtime scope:** Windows/package runtime gates remain pending; any stricter CPU-regression comparison is a separate bounded comparison, not a duplicate one-hour soak
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Audited S6-D2 feature head:** `f35f2abfc98511cdfaba85ce23374882819b8e30` over base `e261e7b4f4b31c5af89faaac3bfc9ccc35ae1bcc`
**Merged S6-D2 PR/main:** `#65` / `1e593364c36a5a30117e86816b1b94cfd52531f5`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
**S6-D1 evidence:** [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
**S6-D2 evidence:** [`../30-quality/s6-d2-user-confirmed-product-truth.md`](../30-quality/s6-d2-user-confirmed-product-truth.md)
**S6-D3 evidence:** [`../30-quality/s6-d3-official-accuracy-baseline.md`](../30-quality/s6-d3-official-accuracy-baseline.md)
**S6-F feature evidence:** [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-D3 now preserves an official current-sample production-detector baseline from all 15 audited S6-D2 truths while excluding the 2 unusable frames from accuracy denominators. The current four-video set is not category-balanced, so the executable gate moves to missing-category real-video acquisition and user-truth extension rather than detector tuning or an accuracy PASS.

## Latest recorded closeout

| Item | Current state |
|---|---|
| S6-D3 exact base | `main @ 47a5516e49872bcb6ffcd9c8147b2dcaa8640218`; production detector `opencv-phase-detector-s5b-typed-production-v1` |
| Local evidence | `sample/output/s6-d3-official-accuracy-baseline/worker-47a5516-20260801T160903Z/`; composite dataset fingerprint `a6845fcf225c99bae8032ae55003aadbd37352b62153395bb9d406450909d92b` |
| Denominator | `15 total / 13 usable / 2 unusable`; unusable S3 focus-loss frames retained only as provenance/reason evidence |
| Oil baseline | raw/smoothed detection coverage `0/13`; all usable Oil truth positions are missed, so Oil position MAE/percentiles are `not_evaluated` rather than assigned a fabricated penalty |
| Fill/Foam baseline | fill-state accuracy `0/13`; Foam precision `7/7 = 1.000`, recall `7/10 = 0.700`; matched Foam-front MAE `47.285714 px` |
| Review ambiguity | `6/13 = 0.461538` usable cases are `UNKNOWN_REVIEW` and/or carry `REVIEW_REQUIRED` |
| Missing denominators | no-interface false-boundary, shimmer Foam false-positive and event truth metrics remain `not_evaluated` |
| Reproducibility | four production CLI runs and four same-dataset `--baseline` reruns exited `0`; dataset/settings/run fingerprints, cases and micro/macro summaries reproduced exactly |
| Focused validation | benchmark/export/reader/metric/CLI suite `67 passed in 7.93s` |
| Gate decision | current-sample official baseline is preserved; category-balanced accuracy eligibility is false because clear, shimmer, structural/rim, rapid fill/drain, full/empty no-interface, transition and broader independent field-video evidence remain missing |

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

- missing-category real-video acquisition and user-truth extension for scratch/surface defects, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive motion, structural rim/paired lines, clean full/empty no-interface and dropout/reacquisition transitions;
- broader independent field-video coverage beyond the current four-video set;
- category-balanced official detector-accuracy evidence after the extended truth set is independently accepted;
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
- Source repair or threshold tuning requires later category-balanced evidence and separate authority.

## Intentional non-runs

The S6-D3 Worker ran only the existing regression-fixture export and headless detector-benchmark path against the audited current sample truth. It did not run a new full analyzer/result-bundle job, tune or repair detector source/thresholds/settings, modify Recipes, original MP4s, `.oiltruth` or provisional truth, synthesize missing categories, or promote unusable frames into accuracy denominators. It did not run Windows, packaging, GUI, canonical-suite or long-duration acceptance. The current-sample baseline is preserved without declaring category-balanced accuracy PASS, closing S6 or starting S7.
