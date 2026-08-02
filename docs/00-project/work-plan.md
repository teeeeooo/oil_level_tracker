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
**Current S6-D4 result:** `PARTIAL-FOAM STRUCTURAL FALSE-OIL REPAIR: WORKER COMPLETE — FRESH INDEPENDENT EXACT-HEAD RE-AUDIT REQUIRED`
**Current S6-F result:** `ONE-HOUR LONG-DURATION STABILITY: AUDITED AND ACCEPTED — REPRESENTATIVE THROUGHPUT RECORDED`
**Current gate:** `S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit`
**S6-F host-use context:** `user-confirmed idle representative run`; not a telemetry-proven controlled-idle benchmark
**Product truth state:** four bundle-bound `.oiltruth` files with 15 reviewed frames are audited and merged on `main`; `13 corrected + 2 unusable`, `0 confirmed_correct`
**Available-corpus constraint:** the current four real videos are the representative real-video corpus available at this stage; further representative acquisition is externally infeasible and is not an executable S6 gate
**Pending accuracy gate:** `S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit`; the repaired Worker head is unmerged and unavailable categories remain residual risk
**Pending runtime scope:** Windows/package runtime gates remain pending; any stricter CPU-regression comparison is a separate bounded comparison, not a duplicate one-hour soak
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Audited S6-D3 feature head:** `049d0eb49222b904c688686267acb01bf95374a9` over base `47a5516e49872bcb6ffcd9c8147b2dcaa8640218`
**Merged S6-D3 PR/main:** `#66` / `0a3cf34b8d4e0fbd9725a2de24612e62da910e50`
**S6-D4 first Auditor-failed PR head:** `71af3205e4e1242ccc1a323e3cac174296366210`
**S6-D4 second-repair starting / Auditor-failed PR head:** `2dc14a13cf3ae1d25b9941c3b9026cc8a224525f`
**S6-D4 starting main / latest repaired detector commit:** `e04ce64384b31643795448fb6b16e47564a3b7c3` / `6b2ea43e8ae62773d4ae6ce17754477d810c78c6`
**S6-D4 latest feature evidence:** `current-sample-feature.json` SHA-256 `b098a070927ffcf9230a57cd94827a8fe8eedec9a08f591591404c29271cf70c`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
**S6-D1 evidence:** [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)
**S6-D2 evidence:** [`../30-quality/s6-d2-user-confirmed-product-truth.md`](../30-quality/s6-d2-user-confirmed-product-truth.md)
**S6-D3 evidence:** [`../30-quality/s6-d3-official-accuracy-baseline.md`](../30-quality/s6-d3-official-accuracy-baseline.md)
**S6-D4 feature evidence:** [`../30-quality/s6-d4-available-corpus-detector-repair.md`](../30-quality/s6-d4-available-corpus-detector-repair.md)
**S6-F feature evidence:** [`../30-quality/s6-f-one-hour-long-duration-stability.md`](../30-quality/s6-f-one-hour-long-duration-stability.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-D3 preserves the audited frozen current-sample baseline from all 15 S6-D2 truths with 13 usable and 2 unusable cases. S6-D4 has now received two independent structural false-Oil FAIL findings: the first showed that a Foam-front coordinate alone could promote structural evidence, and the second showed that the first repair's one-dimensional `< 0.50` per-row Foam occupancy guard still failed on accepted partial Foam. The latest source commit `6b2ea43e8ae62773d4ae6ce17754477d810c78c6` retires that scalar occupancy gate and requires repeated outer-phase evidence across independent horizontal sectors after accepted Foam/glare and the local S5-B pulse neighborhood are removed. Controlled partial-Foam neighborhoods, narrow-partial cases and the prior full-Foam structural negative now remain Oil-null/ambiguous, while the frozen D3 feature result preserves raw/smoothed Oil `7/13`, FillState `6/13`, review/unknown `4/13`, Foam precision `1.000`, recall `0.700` and matched-front MAE `47.285714 px`. The result remains non-category-balanced; all missing field categories remain explicit `not_evaluated`/residual risk. The exact current gate is fresh independent exact-head D4 **re-audit**; the Worker has no merge authority.

## Current S6-D4 Worker handoff

| Item | Current state |
|---|---|
| Starting main | `e04ce64384b31643795448fb6b16e47564a3b7c3`; clean and equal to `origin/main` at Worker start |
| Auditor FAIL chronology | first failed head `71af3205e4e1242ccc1a323e3cac174296366210` exposed Foam-front-only authorization; second-repair starting head `2dc14a13cf3ae1d25b9941c3b9026cc8a224525f` exposed partial-Foam structural false Oil through the `< 0.50` row-occupancy repair |
| Latest repaired detector source/test commit | `6b2ea43e8ae62773d4ae6ce17754477d810c78c6` |
| Frozen D3 baseline | composite SHA-256 `fbfc7aa34e00eeb002098f5d79a0f83288bd06aec014ecae3ebd9f177e207692`; dataset composite `a6845fcf225c99bae8032ae55003aadbd37352b62153395bb9d406450909d92b` |
| Superseded feature evidence | first failed feature `6f7e374… / 42e7a3a8…`; first repair `c2c58fc… / b2995711…`; neither is the current acceptance target |
| Latest feature evidence | local ignored `current-sample-feature.json` SHA-256 `b098a070927ffcf9230a57cd94827a8fe8eedec9a08f591591404c29271cf70c`; all four component comparisons `comparable` |
| Partial-Foam structural regression | six position/height cases plus two narrow-partial cases preserve accepted Foam while Oil stays `None`/ambiguous and never becomes false `FOAMING_VISIBLE`; broader starting-head diagnostic had `60 + 8` false numeric cases and the new discriminator rejected all `68/68` |
| Full-Foam structural regression | prior accepted white-Foam structural negative remains fail-closed with Oil `None` |
| Oil | raw/smoothed `0/13 → 7/13`; 7 matched MAE `4.428571 px`, median `2.0 px`, P90 `9.8 px`, P95 `10.4 px` |
| FillState | `0/13 → 6/13` correct |
| Foam | precision `1.000 → 1.000`; recall `0.700 → 0.700`; matched-front MAE `47.285714 → 47.285714 px` on the same seven matches |
| Review/unknown | `6/13 → 4/13` |
| Cross-video scope | Foam-absent sample1 recovered; all five sample4 Oil+Foam frames recovered; sample3 frame 1035 is an additional non-primary Oil recovery |
| Focused validation | D4 focused `53 passed`; affected-owner S5-A/S5-B/serialized-owner/resource set `470 passed`; benchmark-contract set `67 passed` |
| Claim boundary | available-corpus improvement only; missing categories remain `not_evaluated`; no category-balanced/general-field accuracy PASS |
| Next gate | `S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit` |

## Latest audited closeout (S6-D3)

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

- fresh independent exact-head **re-audit** of the repaired `S6-D4 Available-Corpus Detector Accuracy Repair` branch against the exact frozen D3 dataset/catalog/settings/runtime environment;
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

S6-D4 reused the accepted D3 base rather than rerunning it because direct Git verification proved there was no `src/oil_tracker` change between D3 source revision `47a5516e49872bcb6ffcd9c8147b2dcaa8640218` and starting `main @ e04ce64384b31643795448fb6b16e47564a3b7c3`, and the preserved D3 composite SHA-256 remained exact. After the Auditor structural-false-Oil finding, the Worker regenerated only the repaired feature side on the same four frozen D3 datasets and ran the focused S5-A/S5-B/resource plus controlled Oil/benchmark-contract suites. It did not rerun the one-hour soak, Windows/manual GUI, packaging/PyInstaller or unrelated canonical acceptance suites. Recipe snapshots, original MP4s, product `.oiltruth`, provisional truth and D3 baseline evidence remained read-only. S6 remains open until fresh independent D4 re-audit and the remaining platform/acceptance gates complete.
