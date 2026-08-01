# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-D1 result:** `S6-D1 DOMAIN-OWNER RESPONSE: RECEIVED FOR 15 EXACT REVIEW FRAMES`
**Current S6-D2 result:** `S6-D2 PRODUCT TRUTH MATERIALIZED — FRESH INDEPENDENT AUDIT PENDING`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — REPRESENTATIVE THROUGHPUT RECORDED`
**Current gate:** `S6-D2 Fresh Independent Exact-Head Product Truth Audit`
**S6-F host-use context:** `user-confirmed idle representative run`; not a telemetry-proven controlled-idle benchmark
**Product truth state:** four bundle-bound `.oiltruth` files with 15 reviewed frames exist on the S6-D2 feature branch; `13 corrected + 2 unusable`; not yet audited or merged
**Pending accuracy gate:** S6-D2 exact-head audit/merge, then category-balanced official detector-accuracy evidence
**Pending runtime scope:** Windows/package runtime gates remain pending; any stricter CPU-regression comparison is a separate bounded comparison, not a duplicate one-hour soak
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**S6-D2 Worker base/main:** `e261e7b4f4b31c5af89faaac3bfc9ccc35ae1bcc`
**S6-D2 Worker branch:** `feature/s6-d2-user-confirmed-product-truth`
**Previous audited S6-F feature head:** `457e946398885a5d8918d279b2b6975b0f381981` over parent `bcac3d66e383dc6e60457bc173d90502fd45878d`
**Previous merged S6-F PR/main:** `#64` / `abe1cae14cb488fd61a4da94f1f11aeddc6a5c38`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
**S6-D1 evidence:** [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
**S6-D2 evidence:** [`../30-quality/s6-d2-user-confirmed-product-truth.md`](../30-quality/s6-d2-user-confirmed-product-truth.md)
**S6-F feature evidence:** [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). The domain owner has now supplied explicit responses for all 15 S6-D1 review IDs, and the S6-D2 Worker has materialized those decisions into four product-owned, exact-bundle-bound `.oiltruth` files without changing detector source, Recipes, videos or provisional truth. The current executable gate is the fresh independent exact-head product-truth audit; detector accuracy comparison follows only after that artifact gate passes.

## Latest recorded closeout

| Item | Current state |
|---|---|
| S6-D2 materialization | Four `.oiltruth` files; `3 / 3 / 4 / 5` annotations; `15` unique frames total |
| Product translation | `13 corrected`, `2 unusable`, `0 confirmed_correct`; FillState `PARTIAL_VISIBLE=3`, `FOAMING_VISIBLE=10`, unusable/null `2` |
| D1 derivative ZIP | Current user-reviewed ZIP `8aefcf78beac62be7166d9bfd3338a5e3f1c3054990c857159f2c3d6bb7d2c10`; non-response review payload unchanged against preserved root after macOS metadata exclusion |
| Bundle validation | All four truth files load through `JsonTruthRepository` and validate against their exact preserved D1 production bundle |
| Targeted suite | `64 passed in 6.97s` |
| Accuracy boundary | Product truth artifact only; no category-balanced detector metric or accuracy PASS claimed |
| Current owner / next gate | independent Auditor / `S6-D2 Fresh Independent Exact-Head Product Truth Audit` |

## Prior S6-F closeout retained

| Item | Current state |
|---|---|
| Accepted S6-F run | Existing audited one-hour run reused read-only from `sample/output/s6-f-one-hour-long-duration/launch-bcac3d6-20260801T053400Z/`; no analyzer or soak rerun |
| Workload | `24,160` sampled frames at `2.0 FPS`, representing `12,080.0 s` of one-Glass source time on Apple M1 / 16 GB / macOS `26.5.2` / Python `3.14.4` |
| End-to-end throughput | `3868.206149 s` wall time → `6.245789 frames/s`, `3.122895×` realtime; one hour of equivalent source time is about `1152.777 s` (`19 min 12.8 s`) |
| Pre-output throughput proxy | First telemetry-observed output growth at `3577.215547 s` → `6.753856 frames/s`; one hour source equivalent about `1066.058 s` (`17 min 46.1 s`) |
| CPU consumption | Last live telemetry recorded `5862.58 CPU-s / 3858.318431 wall-s = 1.519` CPU-core equivalents; pre-output proxy `5474.91 / 3577.215547 = 1.530` core equivalents |
| Output phase | First observed output growth to final live output state covered about `281.103 s`; about `290.991 s` of wall time remained from first growth through process completion |
| Host-use context | User confirms no other Mac work was performed during the run and analyzer was effectively the primary workload; host-wide idle/load telemetry was not separately instrumented |
| Interpretation | This is a `user-confirmed idle representative run`, not a telemetry-proven controlled-idle benchmark; it supports this exact M1 / one-Glass / 2-FPS workload only |
| Duplicate-run decision | The same accepted one-hour run already supplies representative throughput evidence, so another one-hour soak is not required for that purpose; any stricter CPU-regression need is a separate bounded controlled comparison |
| Preservation / next gate | Raw S6-F evidence remains unchanged. The current S6-D1 ZIP is a user-reviewed derivative recorded separately from the preserved root; `S6-D2 Fresh Independent Exact-Head Product Truth Audit` is the current next gate |

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

- fresh independent exact-head audit and guarded merge of the S6-D2 product truth artifact;
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

This S6-D2 Worker created only the four product `.oiltruth` artifacts and source-completing documentation from the explicit user response. It did not start an analyzer, repeat the one-hour soak, modify provisional truth, Recipes, original MP4s, detector source, tests, dependencies, settings, thresholds or preserved D1 bundle/asset/manifest bytes. It did not calculate detector-accuracy metrics, claim detector accuracy PASS, extrapolate one-Glass throughput to multi-Glass or Windows/package performance, run Windows/packaging/GUI acceptance, close S6 or start S7. The current user-reviewed derivative ZIP was consumed read-only and recorded by its exact SHA-256.
