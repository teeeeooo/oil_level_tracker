# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-D1 result:** `S6-D1 DOMAIN-OWNER RESPONSE: RECEIVED FOR 15 EXACT REVIEW FRAMES`
**Current S6-D2 result:** `S6-D2 USER-CONFIRMED PRODUCT TRUTH: AUDITED AND ACCEPTED`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — REPRESENTATIVE THROUGHPUT RECORDED`
**Current gate:** `Category-Balanced Official Detector-Accuracy Evidence`
**S6-F host-use context:** `user-confirmed idle representative run`; not a telemetry-proven controlled-idle benchmark
**Product truth state:** four bundle-bound `.oiltruth` files with 15 reviewed frames are audited and merged on `main`; `13 corrected + 2 unusable`, `0 confirmed_correct`
**Pending accuracy gate:** category-balanced official detector-accuracy evidence
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
**S6-F feature evidence:** [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). The domain owner's 15 exact S6-D1 frame decisions are now materialized as four product-owned, exact-bundle-bound `.oiltruth` files. Fresh independent audit passed at exact feature head `f35f2abfc98511cdfaba85ce23374882819b8e30`, and PR #65 was guarded-squash-merged as `main @ 1e593364c36a5a30117e86816b1b94cfd52531f5`. The current executable gate is category-balanced official detector-accuracy evidence; this Close does not start that comparison or detector tuning.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Exact audit target | PR #65; base `e261e7b4f4b31c5af89faaac3bfc9ccc35ae1bcc`; feature head `f35f2abfc98511cdfaba85ce23374882819b8e30`; exact eight-file scope |
| D1 provenance | User-reviewed derivative ZIP `8aefcf78beac62be7166d9bfd3338a5e3f1c3054990c857159f2c3d6bb7d2c10`; after macOS metadata exclusion only `review-response-template.md` differs from the preserved root; all other `38` review payload members and all `149` non-ZIP original manifest entries reproduce exactly |
| Product truth | Four `.oiltruth` files; `3 / 3 / 4 / 5` annotations; `13 corrected + 2 unusable + 0 confirmed_correct`; ruler-derived sample2/S3-02 coordinates reproduce exactly and unusable frames retain no numeric truth |
| Bundle validation | All four preserved D1 production bundles reopen through `ResultBundleReader`; all truth files load through `JsonTruthRepository` with exact run/Recipe/snapshot/Glass/frame/timestamp identity, coordinate round-trip and official snapshot reference equality |
| Fresh validation | `64 passed in 6.22s`; changed-document Markdown check `37` relative links with no missing target; `git diff --check` passed; audited worktree remained clean |
| Merge | PR #65 marked Ready and native exact-base/head guarded-squash-merged as `1e593364c36a5a30117e86816b1b94cfd52531f5` |
| Acceptance boundary | Product-truth artifact accepted only; no category-balanced detector metric, accuracy PASS, Windows/package acceptance or new analyzer run claimed |
| Current gate | `Category-Balanced Official Detector-Accuracy Evidence`; not started by this Close |

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
- The selected 15 frames now have exact bundle-bound user truth, but this narrow set is not category-balanced official accuracy evidence.
- Foam presence does not justify automatic Oil `null`; the reviewed sample2/sample3/sample4 dual-boundary frames preserve both Oil and Foam truth where user-confirmed.
- The former sample2 possible no-interface candidate is not promoted; the reviewed sample2 frames are user-confirmed as `FOAMING_VISIBLE` with explicit Oil and Foam coordinates.
- No official MAE, precision, recall, false-positive/negative rate, calibrated level or detector physical-accuracy PASS is claimed.
- S6-F is accepted only for the exact one-hour macOS source-tree workload. The same run now records representative throughput under user-confirmed idle host use, but not telemetry-proven controlled-idle conditions; it does not establish Windows, packaging, multi-Glass scaling or infinite-duration stability, and the mild analysis-period retention plus event-heavy finalization plateau remain explicit limitations.
- S6 remains `ACTIVE`; S7 remains `PLANNED`.

## Pending S6 scope

Still pending and not accepted:

- representative scratch, fogging/stain, clean rim-adjacent boundary, high-quality field fill/drain and clean full/empty no-interface videos;
- category-balanced official detector-accuracy evidence;
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

The S6-D2 Worker and fresh Auditor did not start an analyzer, repeat the one-hour soak, tune detector thresholds, modify provisional truth, Recipes, original MP4s, detector source, tests, dependencies or settings, or generate a detector-accuracy benchmark. The Auditor consumed the preserved D1 bundles and user-reviewed derivative ZIP read-only, ran only focused truth/bundle/source validation, and did not run Windows, packaging, GUI or new long-duration acceptance. This Close records the accepted artifact and next gate only; it does not close S6 or start S7.
