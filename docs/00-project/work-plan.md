# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: FAIL`
**Authoritative qualification base:** `main @ 2d085423d63c4ecd716ed47deef41293a9e69e5c`
**Worker branch:** `feature/s6-base-sample-qualification`
**Qualification evidence head:** `PENDING_FIRST_EVIDENCE_COMMIT`
**Durable evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)

This document owns the active execution state. Milestone order and completion state remain governed by [`roadmap.md`](./roadmap.md). S6 remains active; this finding does not close S6 or authorize S7.

## Current gate

The repository supporting sample and deterministic Recipe are qualified as reproducible inputs, but the required source-tree CLI workflow is blocked by a material lifecycle-progress defect.

All three controlled CLI attempts fail with exit code `2` before bundle finalization:

```text
TypeError: unsupported format string passed to NoneType.__format__
```

The fault is in `src/oil_tracker/cli.py`: lifecycle progress may have `timestamp_sec=None`, while the CLI progress callback unconditionally applies `:.3f` formatting.

This S6-A Worker did not modify production source or tests. The next source mutation must be a separately classified bounded repair with focused regression coverage.

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

The video remains Git-ignored. Only the exact Recipe is allowlisted from `sample/*.oilrecipe`.

## Controlled execution status

| Run | Range | CLI acceptance | Diagnostic core/bundle evidence |
|---|---|---|---|
| A — pre-overlay | `0–4.990138249 s`, `5.0 FPS` | `FAIL`, exit `2`, no CLI bundle | `REVIEW_REQUIRED`, 26 samples, bundle complete |
| B — full | `0–14.438133333 s`, `5.0 FPS` | `FAIL`, exit `2`, no CLI bundle | `REVIEW_REQUIRED`, 73 samples, bundle complete |
| C — post-overlay fresh | `5.023405837–14.438133333 s`, `5.0 FPS` | `FAIL`, exit `2`, no CLI bundle | `REVIEW_REQUIRED`, 48 samples, bundle complete |

The diagnostic runs used the same current-source pipeline and bundle store with `progress=None` to isolate the CLI presentation defect. They are supporting evidence only and do not substitute for successful CLI completion.

## Engineering behavior recorded

- No controlled or representative diagnostic frame publishes raw or smoothed numeric oil.
- Frame `0` returns typed no-interface with numeric oil `null`.
- Frame `120` retains oil ambiguity while independently publishing a Foam result; Foam truth is not evaluated.
- The frame `151` explanatory `High / 1/3 / Low` overlay creates strong horizontal oil candidates near `y≈319`, `397–411` and `475`.
- Full-history and fresh post-overlay sequences both retain `ambiguous`, `NO_UPDATE`, `PRESERVE`, no selected oil hypothesis and numeric oil `null` at frames `151`, `152`, `240` and `433`.
- No overlay-induced numeric lock or stale smoothing was observed.
- Diagnostic bundles finalize atomically, have no broken local references, preserve blank full/no-interface numeric CSV fields and leave no video/output handle after process exit.
- Representative temporal/resource counts stay within the accepted S5-B bounds.

These are engineering outputs without `.oiltruth`; detector accuracy is not evaluated.

## Required repair handoff

Create a separate bounded source-repair task that:

1. preserves lifecycle progress where `timestamp_sec` and `glass_name` may be absent;
2. makes CLI progress formatting safe for both lifecycle-only and frame-bearing updates;
3. adds focused tests that execute `_run_analyze` or equivalent real CLI progress wiring;
4. changes no detector threshold, Recipe schema, output schema, dependency or Oil/Foam meaning;
5. obtains the required independent review before merge.

After that repair reaches authoritative `main`, rerun this exact S6-A sample qualification from a fresh branch using the same video and Recipe hashes.

## Retained contracts

- Repository samples are supporting evidence, not canonical truth.
- No MAE, precision, recall or truth-accuracy claim without user-confirmed `.oiltruth`.
- No video filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- Ambiguous/conflicting evidence remains reviewable rather than forced numeric output.
- S5-A Foam independence remains intact.
- S5-B typed observability, canonical ambiguity and serialized temporal ownership remain intact.
- S5-C canonical/Qt lifecycle and headless import boundaries remain intact.
- Production source, tests, thresholds, schemas and dependencies are unchanged by the S6-A qualification Worker.

## Pending S6 scope

Still pending and not accepted:

- repaired three-run CLI reproduction;
- representative user-confirmed real compressor videos and `.oiltruth`;
- Windows GUI/manual/DPI/canonical-suite validation;
- stable long-duration CPU and memory behavior;
- PyInstaller one-folder build;
- relocated package and clean Windows PC qualification;
- Unicode/long Windows path and file-lock behavior;
- final S6 independent acceptance and Close.

## Next authorized sequence

```text
S6-A evidence PR and fresh independent audit
→ bounded CLI progress repair task
→ repair audit/merge/synchronization
→ fresh S6-A rerun on repaired exact main
→ remaining Windows / long-duration / packaging gates
→ S6 Close only after all acceptance evidence
```

`S7` must not start while S6 remains active.

## Intentional non-runs

This qualification did not run or claim:

- complete canonical suite repetition;
- detector source repair or threshold tuning;
- Windows execution;
- long-duration qualification;
- PyInstaller or one-folder packaging;
- relocated/clean-PC execution;
- user-truth accuracy metrics;
- merge, audit approval or S6 Close.
