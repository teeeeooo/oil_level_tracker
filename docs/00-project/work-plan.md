# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current S6-E result:** `S6-E BOUNDED SOAK SCREENING: ACCEPTED — NO OBVIOUS RESOURCE LEAK`
**Current S6-D1 result:** `S6-D1 REVIEW PACK: AUDITED AND PREPARED — USER CONFIRMATION PENDING`
**Current gate:** `S6-D1 Domain-Owner Mobile Review`
**Product truth state:** no product `.oiltruth` exists or was created; user dispositions remain pending
**Pending accuracy gate:** user review, later S6-D2 product truth creation and category-balanced official detector-accuracy evidence
**Pending runtime gates:** controlled-idle representative-duration performance and official long-duration CPU/memory stability
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Audited feature head:** `e8a4fe8ed4bac01b8700289a15f6ae6b5a70ced4` over parent `0f0bf705795ebedc9210c9731e486b194ecded09`
**Merged PR/main:** `#63` / `170d71798526aa7592c2db9cb9c37e4559f5ed9a`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)
**S6-E evidence:** [`../30-quality/s6-bounded-runtime-soak-evidence.md`](../30-quality/s6-bounded-runtime-soak-evidence.md)
**S6-D1 evidence:** [`../30-quality/s6-d1-mobile-truth-review-pack.md`](../30-quality/s6-d1-mobile-truth-review-pack.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). PR #63 passed fresh exact-head audit and was guarded-squash-merged. The bundle-bound candidate pack is ready for explicit user review, but candidate coordinates remain unconfirmed and do not satisfy S6-D accuracy acceptance.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Review pack | 15 exact frames prepared across sample1/sample2/sample3/sample4 with counts `3/3/4/5` |
| Fresh baseline | Four production CLI runs exited `0`, completed lifecycle `1/6–6/6`, reopened with `ResultBundleReader`, and preserved exact bundle/run/Recipe/source identity |
| Mobile assets | 30 individual clean/comparison PNGs, four contact sheets, questionnaire, response template, candidate manifest and optional ZIP |
| Candidate authority | Official detector context, new agent visual candidate, frozen provisional evidence, existing domain-owner statement and future user confirmation remain separate |
| Product truth | `.oiltruth` absent; no `confirmed_correct`, `corrected` or `unusable` disposition was assigned |
| Fresh audit | Complete manifest rehash, four bundle reopens, 15 fresh source decodes, coordinate/range checks, 30 individual-image and four contact-sheet pixel reproductions, ZIP inspection and product-truth boundary passed |
| Targeted tests | `64 passed in 6.99s`; Markdown links, `git diff --check`, ignored-evidence and clean-worktree checks exited `0` |
| Merge | PR #63 guarded-squash-merged as `170d71798526aa7592c2db9cb9c37e4559f5ed9a` |
| Local evidence | Ignored root `sample/output/s6-d1-mobile-truth-review-pack/worker-0f0bf70-20260731T151330Z/` and mobile ZIP preserved |
| Current action / owner | User performs `S6-D1 Domain-Owner Mobile Review`; coding ownership resumes only after explicit responses for a separate S6-D2 Worker |

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
- S6 remains `ACTIVE`; S7 remains `PLANNED`.

## Pending S6 scope

Still pending and not accepted:

- external S6-D1 domain-owner mobile review and explicit per-ID responses;
- S6-D2 bundle-bound product `.oiltruth` creation from only explicitly approved/corrected frames;
- representative scratch, fogging/stain, clean rim-adjacent boundary, high-quality field fill/drain and clean full/empty no-interface videos;
- category-balanced official detector-accuracy evidence;
- controlled-idle representative-duration performance and official long-duration CPU/memory stability;
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

The audit and closeout did not create or edit product `.oiltruth`, provisional truth, Recipes, original MP4s, source, tests, dependencies, settings, thresholds or local review-pack artifacts. It did not assign a user disposition, calculate detector-accuracy metrics, run Windows, packaging, performance, long-duration or GUI acceptance, close S6, or start S7. Hygiene is limited to the Auditor-owned validation worktree; the source branch, unrelated worktrees and ignored review evidence remain subject to eligibility and preservation rules.
