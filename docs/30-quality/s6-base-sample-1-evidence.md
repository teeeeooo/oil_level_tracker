# S6-A Repository Supporting Sample Qualification Evidence

**Verdict:** `S6-A SAMPLE QUALIFICATION: PASS`
**Milestone:** `S6 — Real-video and Windows validation gate` remains `ACTIVE`
**Worker branch:** `feature/s6-base-sample-qualification`
**Initial starting main:** `2d085423d63c4ecd716ed47deef41293a9e69e5c` (`docs: close S5-C and activate S6`)
**Initial qualification evidence commit:** `6b78b398de0cc87e3384ab6f1fe854c698468648`
**Resume repaired main:** `8b37ff81c5d0aa55bf0449f1dbf07d9377b61cd4` (`fix: handle optional CLI lifecycle progress fields`)
**Resume branch-update merge:** `c3b3598` (`Merge branch 'main' into feature/s6-base-sample-qualification`)
**Resume qualification evidence commit:** `098ee55ea6e0d54cd621d511ce6bb0a1500b51ce`
**Scope:** macOS source-tree, short repository supporting sample only

This document preserves the pre-repair CLI failure, the pre-repair diagnostic execution and the repaired-main official CLI rerun as separate evidence. It records engineering behavior, not detector truth accuracy. The sample has no user-confirmed `.oiltruth`; therefore MAE, precision, recall, false-positive/false-negative truth and physical correctness are not evaluated.

## Exact sample and Recipe identity

| Item | Exact value |
|---|---|
| Video | `sample/base_sample_1.mp4` |
| Video SHA-256 | `96cb3339cb90e8f5e7c4f71f5e5890cb12caa8996a432977413e15fe214b2c7e` |
| Video size | `12,408,143 bytes` |
| Resolution | `1280 × 720` |
| Frame count | `434` |
| OpenCV FPS | `30.059287442513345` |
| Calculated duration | `14.438133333333333 sec` |
| OpenCV codec | `h264` |
| Recipe | `sample/base_sample_1.oilrecipe` |
| Recipe SHA-256 | `4e0a0ad729562dac0bc1e75fbdee0c80ff51aaeda0e07d450f15ff878a637ca7` |
| Recipe schema | `1` |
| Recipe ID | `71f5f146-cb3f-57a8-8075-31a2ba18165f` |
| Glass ID | `1a188c16-6295-56a7-bd61-61a78b7ef058` |
| Deterministic timestamps | `2026-07-30T00:00:00+00:00` |

The on-screen context identifies the clip as “TechTip: Checking Oil Level - Bitzer Compressors.” The qualification does not establish redistribution rights or canonical physical truth.

## Execution environment

- Host: macOS `26.5.2`, Apple arm64
- Python: repository `.venv`, `3.14.4`
- Execution path: `PYTHONPATH=src .venv/bin/python`
- OpenCV source reader: repository `OpenCvVideoReader`
- Detector: `opencv-phase-detector-s5b-typed-production-v1`
- Initial repository state: local `main == origin/main == 2d085423…`, upstream `origin/main`, clean worktree
- Resume repository state: local `main == origin/main == 8b37ff81…`, primary checkout on `main`, clean worktree
- Branch update: non-rewriting merge of repaired `main` into the existing feature branch; original qualification commits remain ancestors
- Environment mutation: none; no install, editable-install, dependency or packaging change

## Representative visual inspection and geometry

Frames `0`, `120`, `150`, `151`, `152`, `240` and `433` were decoded and inspected directly.

The deterministic Recipe defines one inner sight-glass region:

- ellipse center `(696.0, 366.0)`;
- ellipse radii `(145.0, 148.0)`;
- zero line `y=366.0`;
- margin ratio `0.08`;
- no exclusion zones;
- `AUTO` initial state;
- `mm_per_pixel=null`;
- exact production-default `DetectorSettings`.

The ellipse excludes the external subtitle/logo/equipment-label regions while retaining the explanatory overlay. The zero line is the reproducible ellipse centerline and is not a calibrated physical datum.

A horizontal red/green run check established the known transition:

| Frame | Approx. time | Max red run | Max green run | Overlay |
|---:|---:|---:|---:|---|
| 0 | `0.000000 s` | `5 px` | `12 px` | absent |
| 120 | `3.992111 s` | `5 px` | `31 px` | absent |
| 150 | `4.990138 s` | `5 px` | `24 px` | absent |
| 151 | `5.023406 s` | `244 px` | `241 px` | first present |
| 152 | `5.056673 s` | `244 px` | `241 px` | present |
| 240 | `7.984221 s` | `246 px` | `244 px` | present |
| 433 | `14.404866 s` | `246 px` | `244 px` | present |

## Recipe validation

Repository `JsonRecipeRepository` load and save paths were used.

- schema version: `1`;
- load succeeded;
- in-memory round-trip `to_dict()` equality: `True`;
- ellipse, zero line, margin and empty exclusions preserved;
- loaded detector settings equal `DetectorSettings()` production defaults: `True`;
- `mm_per_pixel is None`: `True`;
- Git allowlist resolves specifically to `sample/base_sample_1.oilrecipe`.

## Pre-repair controlled CLI failure evidence

All three requested runs used the same Recipe and `5.0 FPS`. Each command was started in a fresh process before the CLI formatting repair reached `main`.

| Run | Range | Intended purpose | Actual CLI result |
|---|---|---|---|
| A — pre-overlay | `0.0–4.990138249 s` | weak pre-overlay behavior | exit `2`; no bundle |
| B — full | `0.0–14.438133333 s` | pre/post temporal behavior | exit `2`; no bundle |
| C — post-overlay fresh | `5.023405837–14.438133333 s` | overlay without prior detector history | exit `2`; no bundle |

Every CLI run failed after frame analysis entered a later lifecycle stage:

```text
error: unsupported format string passed to NoneType.__format__
```

The exact traceback is:

```text
src/oil_tracker/cli.py:81
f"{progress.completed}/{progress.total} {progress.timestamp_sec:.3f}s {progress.glass_name}"
TypeError: unsupported format string passed to NoneType.__format__
```

`AnalysisPipeline` legitimately emits non-frame lifecycle progress with `timestamp_sec=None`; the CLI progress lambda formats it unconditionally as a float. This is a reproducible source defect in the real CLI analysis path. It prevents CLI completion and bundle generation for all three controlled runs.

### Minimal reproduction

```bash
PYTHONPATH=src .venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/base_sample_1.oilrecipe \
  --video sample/base_sample_1.mp4 \
  --output sample/output/s6-base-sample-1/run-b-full \
  --start 0 \
  --end 14.438133333 \
  --compressor-start 0 \
  --sampling-fps 5.0
```

This Worker did not repair the defect. A separately classified bounded source-repair task is required, including focused CLI progress tests for both frame-bearing and lifecycle-only progress updates.

## Diagnostic core-pipeline execution

To determine whether the failure extended into detector or bundle ownership, the same current-source `AnalysisPipeline`, `OpenCvPhaseDetector` and `OutputBundleStore` were run in fresh processes with `progress=None`. No source or settings were changed. These diagnostic runs do **not** replace the failed CLI acceptance.

| Run | Result | Samples | Events | Wall | User CPU | Max RSS | Bundle |
|---|---|---:|---:|---:|---:|---:|---|
| A | `REVIEW_REQUIRED` | 26 | 10 | `16.30 s` | `22.70 s` | `200,261,632 B` | `run-a-pre-overlay/.../oil_level_analysis_20260730_074330` |
| B | `REVIEW_REQUIRED` | 73 | 10 | `34.73 s` | `50.02 s` | `201,129,984 B` | `run-b-full/.../oil_level_analysis_20260730_074418` |
| C | `REVIEW_REQUIRED` | 48 | 7 | `27.40 s` | `34.25 s` | `200,294,400 B` | `run-c-post-overlay-fresh/.../oil_level_analysis_20260730_074506` |

The timing is a short-run diagnostic only. It is not a long-duration memory result, accepted CPU baseline or Windows performance result.

## Post-repair official CLI resume execution

The repaired authoritative base is `main @ 8b37ff81c5d0aa55bf0449f1dbf07d9377b61cd4`. The existing feature branch was updated by merge commit `c3b3598`; no qualification history was rewritten. Each official run used the real CLI entrypoint in a fresh process and a fresh output root:

```bash
PYTHONPATH=src .venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/base_sample_1.oilrecipe \
  --video sample/base_sample_1.mp4 \
  --output <run-output-root> \
  --start <run-start> --end <run-end> \
  --compressor-start 0 --sampling-fps 5.0
```

| Run | Exact range | Exit | Progress | Status | Samples | Events | Review events / flagged rows | Wall | Peak RSS |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| A — pre-overlay | `0–4.990138249 s` | `0` | `[1/6]` through `[6/6]`; no `None` | `REVIEW_REQUIRED` | 26 | 10 | `3 / 8` | `16.37 s` | `201,031,680 B` |
| B — full | `0–14.438133333 s` | `0` | `[1/6]` through `[6/6]`; no `None` | `REVIEW_REQUIRED` | 73 | 10 | `3 / 55` | `35.16 s` | `202,309,632 B` |
| C — post-overlay fresh | `5.023405837–14.438133333 s` | `0` | `[1/6]` through `[6/6]`; no `None` | `REVIEW_REQUIRED` | 48 | 7 | `2 / 48` | `37.73 s` | `201,506,816 B` |

Each `review_index.json` contains one Glass with `result_status=REVIEW_REQUIRED`. No run printed `None`, traceback or CLI error. Exact bundles:

- A: `sample/output/s6-base-sample-1/resume-official-8b37ff81-20260730T1016/run-a-pre-overlay/oil_level_analysis_20260730_102008`
- B: `sample/output/s6-base-sample-1/resume-official-8b37ff81-20260730T1016/run-b-full/oil_level_analysis_20260730_102101`
- C: `sample/output/s6-base-sample-1/resume-official-8b37ff81-20260730T1016/run-c-post-overlay-fresh/oil_level_analysis_20260730_102206`

Repository `ResultBundleReader` reopened all three bundles. Required manifests, CSV files, Recipe/session snapshots, review indexes, reports, graphs, captures and analysis logs exist and parse. All local report references resolve; PNGs decode; no hidden temporary/staging artifact remains; the Recipe snapshot SHA-256 equals the tracked Recipe hash; full/empty numeric oil CSV fields remain blank; no video or output handle remained after process exit.

The official CLI status, sample count and event count exactly match the corresponding pre-repair diagnostic execution. The repaired progress presentation changes lifecycle completion only; this evidence shows no detector-result or bundle-content divergence attributable to the repair. These short-run timings remain diagnostics, not accepted long-duration or Windows performance evidence.

## Detector engineering findings

### Aggregate behavior

| Run/segment | Rows | Raw oil numeric | Smoothed oil numeric | Raw Foam numeric | Main states |
|---|---:|---:|---:|---:|---|
| A pre-overlay | 26 | 0 | 0 | 16 | 2 `FULL_NO_INTERFACE`, 15 `FULL_WITH_FOAM`, 9 `UNKNOWN_REVIEW` |
| B full | 73 | 0 | 0 | 16 | 2 `FULL_NO_INTERFACE`, 15 `FULL_WITH_FOAM`, 56 `UNKNOWN_REVIEW` |
| B post-overlay only | 47 | 0 | 0 | 0 | 47 `UNKNOWN_REVIEW` |
| C post-overlay fresh | 48 | 0 | 0 | 0 | 48 `UNKNOWN_REVIEW` |

These are detector outputs, not verified physical labels. In particular, pre-overlay Foam publications are unconfirmed engineering behavior, not a claim that real Foam exists.

### Representative frames

| Frame | Canonical oil family | Raw/smoothed oil | Tracker / smoothing | Fill state | Foam behavior |
|---:|---|---|---|---|---|
| 0 | `no_interface`, accepted | `null / null` | `NO_UPDATE / PRESERVE` | `FULL_NO_INTERFACE` | no evidence |
| 120 | `ambiguous` | `null / null` | `NO_UPDATE / PRESERVE` | `FULL_WITH_FOAM` | strong Foam publication at `y≈430`; truth not evaluated |
| 150 | `ambiguous` | `null / null` | `NO_UPDATE / PRESERVE` | `UNKNOWN_REVIEW` | weak/rejected |
| 151 | `ambiguous` | `null / null` | `NO_UPDATE / PRESERVE` | `UNKNOWN_REVIEW` | weak/rejected |
| 152 | `ambiguous` | `null / null` | `NO_UPDATE / PRESERVE` | `UNKNOWN_REVIEW` | weak/rejected |
| 240 | `ambiguous` | `null / null` | `NO_UPDATE / PRESERVE` | `UNKNOWN_REVIEW` | weak/rejected |
| 433 | `ambiguous` | `null / null` | `NO_UPDATE / PRESERVE` | `UNKNOWN_REVIEW` | weak/rejected |

At frame `151`, the new explanatory lines create high-support oil hypotheses near:

- `y≈319` — High overlay region;
- `y≈397–411` — 1/3 overlay region;
- `y≈475` — Low overlay region and highest boundary-likelihood candidate (`≈0.486`).

All are rejected as `typed_ambiguous_observation`; no oil candidate is selected and no raw or smoothed numeric oil value is published. The same outcome persists at frames `152`, `240` and `433`.

The full-history and fresh post-overlay sequences agree at frames `151`, `152`, `240` and `433`: `ambiguous`, `NO_UPDATE`, `PRESERVE`, no selected hypothesis and no numeric oil. Therefore this sample did not show stale smoothing, permanent numeric lock or a temporal-history-dependent promotion of the explanatory lines.

Foam processing remained independently observable: pre-overlay frames could publish Foam while oil remained ambiguous, whereas post-overlay frames rejected Foam and kept oil ambiguous. This establishes output-path independence only; it does not establish Foam truth accuracy.

### Retained resource bounds

Representative debug metrics reported no architecture-bound violation. Observed maxima included:

- raw observations `36 / 48`;
- proposals `10 / 12`;
- hypotheses `10 / 10`;
- temporal beam `3 / 4`;
- temporal history `6 / 6`;
- retained temporal scalars `105` within the published limit;
- debug scalars `74 / 96`;
- oil temporal state count `1` for the one Glass.

No unbounded history is inferred from this short clip. Stable long-duration memory remains untested.

## Bundle and operational evidence

Each diagnostic bundle was structurally inspected:

- `analysis_manifest.json`, `tracking_data.csv`, `events.csv`, `recipe_snapshot.oilrecipe`, `session.json`, `review_index.json`, `report.html`, graphs, captures and log exist;
- JSON and CSV files parse;
- graph and capture PNG files decode;
- every local HTML reference resolves inside the bundle;
- no `.tmp`, `.part` or hidden staging artifact remains;
- Recipe snapshot SHA-256 equals the tracked Recipe SHA-256;
- `FULL_NO_INTERFACE` rows keep raw and smoothed numeric oil fields blank;
- `lsof` found no remaining handle on the video or output tree after process exit.

This demonstrates that the core pipeline and bundle store can finalize when the faulty CLI progress callback is absent. It does not make the CLI run successful.

An OpenCV backend edge was also observed at the exact terminal timestamp: a fresh seek using the truncated decimal `14.438133333` can report frame index `434`, while a clamped/continued sequence reports frame `433`. The source metadata already warns that timestamp seeking is backend/keyframe dependent. Representative inspection therefore uses directly decoded frame `433`; no truth or numeric-boundary conclusion depends on the terminal index report.

## Truth limitations

No `.oiltruth` accompanies this video. Consequently:

- the weak visible boundary is not declared correct or incorrect;
- explanatory-line candidates are described by coincidence with known overlay geometry, not as confirmed false positives;
- pre-overlay Foam output is not declared true or false;
- no MAE, precision, recall, accuracy, physical calibration or millimetre claim is made;
- `REVIEW_REQUIRED` is retained as a reviewable engineering outcome.

## Pending external scope

Not executed and not accepted by this qualification:

- Windows canonical suite or GUI;
- Windows DPI/manual workflow;
- long-duration CPU/memory stability;
- PyInstaller one-folder build;
- relocated or clean-PC execution;
- Unicode/long Windows paths;
- Windows file-lock/cancellation/close behavior;
- representative user-confirmed compressor-video accuracy dataset;
- S6 Close or S7 start.

## Final classification and next gate

`S6-A SAMPLE QUALIFICATION: PASS`

The exact sample and Recipe identities match, the existing qualification history is preserved on repaired `main`, and all three required official CLI executions now exit `0`, emit lifecycle stages `[1/6]` through `[6/6]` without `None` or traceback, atomically finalize complete bundles and retain the reviewable detector behavior recorded before repair. No material qualification blocker remains for this repository supporting sample.

`PASS` means the short supporting-sample CLI and bundle qualification completed. It is not detector accuracy PASS, physical oil truth, Windows acceptance, long-duration acceptance, packaging acceptance, S6 Close or authorization to start S7.

The next gate is `PR #58 S6-A Qualification Fresh Exact-Head Auditor`. A fresh Worker-independent Auditor must verify the updated exact base/head, preserved pre-repair evidence, repaired-main official A/B/C reproduction, bundle integrity, truth limitations, bounded PR diff and continued S6 `ACTIVE` status. Only after `AUDIT: PASS` may that Auditor perform the authorized guarded merge and registered-checkout synchronization.

## Evidence locations

Generated evidence is intentionally ignored by Git under:

```text
sample/output/s6-base-sample-1/
├─ frames/
├─ representative_frame_evidence.json
├─ run-a-pre-overlay/                  # pre-repair diagnostic/failure evidence
├─ run-b-full/
├─ run-c-post-overlay-fresh/
└─ resume-official-8b37ff81-20260730T1016/
   ├─ official-cli-validation-summary.json
   ├─ run-a-pre-overlay/
   ├─ run-b-full/
   └─ run-c-post-overlay-fresh/
```

Tracked reproduction inputs and durable evidence are:

- `sample/base_sample_1.oilrecipe`;
- `sample/README.md`;
- this document;
- `docs/00-project/work-plan.md`.

The repaired source and focused test arrive only through merged `main @ 8b37ff81…`. This resume Worker changed qualification documentation only; the PR diff against current `main` contains no source, test, detector threshold, schema, dependency or packaging change.
