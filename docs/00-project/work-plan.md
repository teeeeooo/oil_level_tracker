# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Authoritative qualification base:** `main @ 8b37ff81c5d0aa55bf0449f1dbf07d9377b61cd4`
**Worker branch:** `feature/s6-base-sample-qualification`
**Initial qualification evidence commit:** `6b78b398de0cc87e3384ab6f1fe854c698468648`
**Resume branch-update merge:** `c3b3598`
**Resume qualification evidence commit:** `PENDING_RESUME_EVIDENCE_COMMIT`
**Durable evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**Current gate:** `PR #58 S6-A Qualification Fresh Exact-Head Auditor`

This document owns the active execution state. Milestone order and completion state remain governed by [`roadmap.md`](./roadmap.md). S6 remains active; this supporting-sample result does not close S6 or authorize S7.

## S6-A repository sample identity

| Item | Exact value |
|---|---|
| Video | `sample/base_sample_1.mp4` |
| Video SHA-256 | `96cb3339cb90e8f5e7c4f71f5e5890cb12caa8996a432977413e15fe214b2c7e` |
| Video metadata | `1280×720`, `434` frames, `30.059287442513345 FPS`, `14.438133333333333 s`, `12,408,143 B` |
| Known overlay transition | frame `151`, approximately `5.023405837 s` |
| Recipe | `sample/base_sample_1.oilrecipe` |
| Recipe SHA-256 | `4e0a0ad729562dac0bc1e75fbdee0c80ff51aaeda0e07d450f15ff878a637ca7` |
| Recipe geometry | ellipse `(696,366)`, radii `(145,148)`, zero `y=366`, margin `0.08`, no exclusions |
| Detector settings | production defaults |
| Calibration | `mm_per_pixel=null` |

The video and generated output remain Git-ignored. Only the deterministic Recipe is allowlisted from `sample/*.oilrecipe`.

## Repaired-main official CLI result

The existing feature branch was updated without history rewrite by merging repaired `main @ 8b37ff81…`. All three official runs used the real CLI entrypoint, the same Recipe and `5.0 FPS`, with fresh output roots.

| Run | Range | Exit / progress | Status | Samples | Events | Review events / flagged rows |
|---|---|---|---|---:|---:|---:|
| A — pre-overlay | `0–4.990138249 s` | `0`; `[1/6]` through `[6/6]`; no `None` | `REVIEW_REQUIRED` | 26 | 10 | `3 / 8` |
| B — full | `0–14.438133333 s` | `0`; `[1/6]` through `[6/6]`; no `None` | `REVIEW_REQUIRED` | 73 | 10 | `3 / 55` |
| C — post-overlay fresh | `5.023405837–14.438133333 s` | `0`; `[1/6]` through `[6/6]`; no `None` | `REVIEW_REQUIRED` | 48 | 7 | `2 / 48` |

Each bundle contains one review-index Glass with `result_status=REVIEW_REQUIRED`. Repository `ResultBundleReader` reopened all outputs. Required manifest, report, CSV, Recipe/session snapshot, review index, graphs, captures and analysis log exist and parse; report references and PNGs are valid; no staging artifact or process handle remains.

Official bundle roots are recorded in the durable evidence document under:

```text
sample/output/s6-base-sample-1/
└─ resume-official-8b37ff81-20260730T1016/
```

## Preserved failure and diagnostic evidence

The initial qualification on `main @ 2d085423…` remains preserved:

- real CLI A/B/C each exited `2` before bundle finalization because a lifecycle-only progress update had `timestamp_sec=None`;
- source-identical diagnostic runs with `progress=None` completed as `REVIEW_REQUIRED` with 26/73/48 samples and 10/10/7 events;
- repaired-main official runs now complete with the same status, sample count and event count.

The repair is owned by authoritative `main`, not by this qualification PR. Against current `main`, PR #58 contains no production source, test, detector, threshold, schema, dependency or packaging diff.

## Engineering interpretation

- `REVIEW_REQUIRED` is a valid reviewable engineering outcome, not an execution failure.
- Raw and smoothed numeric oil remain `null` in the reviewed sample behavior.
- The known `High / 1/3 / Low` overlay produces strong horizontal candidates, but the recorded outcome remains ambiguous with no selected numeric oil boundary.
- Pre-overlay Foam output remains independently observable from oil ambiguity; Foam physical truth is not evaluated.
- The repository sample is supporting smoke evidence only and has no user-confirmed `.oiltruth`.
- No MAE, precision, recall, false-positive/false-negative truth, physical calibration or detector accuracy PASS is claimed.
- Short-run wall time and peak memory are diagnostics, not accepted CPU or long-duration baselines.

## PR scope and next gate

PR #58 remains Draft. Its diff against current `main` is limited to:

- `.gitignore`;
- `docs/00-project/work-plan.md`;
- `docs/30-quality/s6-base-sample-1-evidence.md`;
- `sample/README.md`;
- `sample/base_sample_1.oilrecipe`.

The next owner is a fresh Worker-independent exact-head Auditor. The Auditor must verify base/head identity, sample and Recipe hashes, preserved pre-repair evidence, official A/B/C reproduction, bundle integrity, truth limitations, ignored sample2/3/4 preservation and bounded PR scope.

Only after `AUDIT: PASS` may that Auditor perform the authorized guarded merge and registered-checkout synchronization. PR Ready transition, merge and S6 Close are not Worker-owned actions.

## Retained contracts

- Repository samples are supporting evidence, never canonical truth.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- Ambiguous/conflicting evidence remains reviewable rather than forced numeric output.
- S5-A Foam independence remains intact.
- S5-B typed observability, canonical ambiguity and serialized temporal ownership remain intact.
- S5-C canonical/Qt lifecycle and headless import boundaries remain intact.

## Pending S6 scope

Still pending and not accepted:

- representative user-confirmed real compressor videos and `.oiltruth`;
- Windows GUI/manual/DPI/canonical-suite validation;
- stable long-duration CPU and memory behavior;
- PyInstaller one-folder build;
- relocated package and clean Windows PC qualification;
- Unicode/long Windows path and file-lock behavior;
- final S6 independent acceptance and Close.

`S7` must not start while S6 remains active.

## Intentional non-runs

This resume qualification did not run or claim detector tuning, new sample2/3/4 qualification, Windows execution, long-duration qualification, packaging, relocated/clean-PC execution, user-truth accuracy metrics, PR Ready transition, merge, audit approval, S6 Close or S7 start.
