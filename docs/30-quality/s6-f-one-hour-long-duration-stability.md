# S6-F One-Hour Long-Duration Resource-Stability Evidence

## Status

- **Task-start production main:** `bcac3d66e383dc6e60457bc173d90502fd45878d`
- **Task-start parent:** `170d71798526aa7592c2db9cb9c37e4559f5ed9a`
- **Feature branch:** `feature/s6-f-one-hour-long-duration-stability`
- **Worker classification:** `ONE-HOUR LONG-DURATION STABILITY: PASS-CANDIDATE`
- **Evidence state:** completed exact local run recovered; source-completing documentation awaiting fresh independent exact-head audit
- **External pending checkpoint:** `S6-D1 Domain-Owner Mobile Review`
- **Next technical gate:** `S6-F One-Hour Long-Duration Resource-Stability Fresh Exact-Head Auditor`
- **Milestone state:** S6 remains `ACTIVE`; S7 remains `PLANNED`

This evidence evaluates one already-completed, detached production CLI analyzer process. No new soak was started during result collection. The classification is a feature-head candidate for independent audit, not merged acceptance and not a universal memory specification.

The result is limited to macOS source-tree resource stability for this exact derived sample3 workload. It does not establish detector accuracy, controlled-idle CPU throughput, Windows or packaged-runtime stability, representative field-duration accuracy, or S6 final acceptance.

## Exact recovered run identity

The recovered ignored local evidence root is:

```text
sample/output/s6-f-one-hour-long-duration/launch-bcac3d6-20260801T053400Z/
```

Persisted launch, state and completion records agree on all required recovery fields:

| Field | Recovered value |
|---|---|
| Repository main | `bcac3d66e383dc6e60457bc173d90502fd45878d` |
| Launch UTC | `2026-08-01T05:47:19.046944+00:00` |
| Completion UTC | `2026-08-01T06:51:47.281421+00:00` |
| Analyzer PID | `63060` |
| Detached runner PID | `63055` |
| `caffeinate` PID | `63061` |
| Exit code | `0` |
| Wall runtime | `3868.206149 s` (`64 min 28.206 s`) |
| Telemetry rows | `374` |
| Final output | `1617 files / 687,497,078 bytes` |
| Remaining owned PIDs | none |
| Final bundle | `output/oil_level_analysis_20260801_154656` |

The completion marker is explicit; completion was not inferred from process absence. Fresh `ps` and `lsof` checks also found analyzer, runner and sleep-prevention PIDs absent with zero open-file rows.

Exact production command:

```bash
/Users/sunjaekim/Developer/oil_level_tracker/.venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/sample3.oilrecipe \
  --video /Users/sunjaekim/Developer/oil_level_tracker/sample/output/s6-f-one-hour-long-duration/launch-bcac3d6-20260801T053400Z/sample3-one-hour-soak.mp4 \
  --output /Users/sunjaekim/Developer/oil_level_tracker/sample/output/s6-f-one-hour-long-duration/launch-bcac3d6-20260801T053400Z/output \
  --start 0 \
  --end 12079.5 \
  --compressor-start 0 \
  --sampling-fps 2.0
```

## Derived input identity

| Field | Value |
|---|---|
| Source | `sample/sample3.mp4` |
| Source SHA-256 | `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` |
| Recipe | `sample/sample3.oilrecipe` |
| Recipe SHA-256 | `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43` |
| Derived video SHA-256 | `68a4cfd9cbf4f077df8972db4775ad1833456cc953e43327488e476a5ef4d97f` |
| Derived size | `238,779,192 bytes` |
| Resolution / FPS | `1280×720 / 2.0 FPS` |
| Cycles / frames | `160 / 24,160` |
| Declared duration | `12,080.0 s` |
| Sequential decode | `24,160 / 24,160`, complete |
| Generation helper SHA-256 | `4d967398d7cca3f3a8fa98dd6c6600276baa062f591bc291752a8da0f2148a64` |

The input is runtime-only evidence derived from the accepted sample3 fixed-geometry window. Loop seams, source blur and re-encoding artifacts are not physical accuracy evidence and were not used for tuning.

## Lifecycle and finalization

The analyzer log completed all six production lifecycle stages. Video analysis reached `24,160/24,160`, event/judgment calculation completed, and result image generation completed `1,607/1,607` event captures.
CSV/snapshot persistence completed `5/5`, graph/report generation completed, and bundle finalization completed `4/4` through temporary-bundle validation and atomic commit. The CLI ended with bundle label `REVIEW_REQUIRED` and exit code `0`.

`REVIEW_REQUIRED` is retained only as a detector/result-bundle fact. It is not a physical-truth judgment and does not constitute detector accuracy failure.

## Raw telemetry analysis

Telemetry was reparsed directly from all `374` JSONL rows. `373` rows observed the analyzer alive; the final row recorded analyzer exit. The first ten minutes are treated as warm-up/context, leaving `315` live post-warm-up rows.

Sampling continuity was regular:

| Interval metric | Value |
|---|---:|
| Minimum | `9.682825 s` |
| Median | `10.375328 s` |
| P95 | `10.456764 s` |
| Maximum | `10.826923 s` |
| Gaps > 15 s | `0` |
| Gaps > 20 s | `0` |

Post-warm-up owned-process RSS statistics were:

| Metric | Value |
|---|---:|
| Minimum | `163.625 MiB` |
| Median | `169.625 MiB` |
| Maximum | `466.734 MiB` |
| `10–20 min` median | `164.836 MiB` |
| Final-10-min median | `174.367 MiB` |
| Stable-to-final median delta | `+9.531 MiB / +5.782%` |
| Post-warm-up linear slope | `+0.024368 MiB/s` (`+1.462 MiB/min`) |
| Final-20-min linear slope | `+0.145808 MiB/s` (`+8.748 MiB/min`) |

The combined `64 MiB` and `25%` diagnostic review signal was not met. The aggregate slopes above include the late bundle-output phase and therefore are not interpreted alone as detector-state leakage.

During the analysis-only post-warm-up period before any output file appeared, RSS rose slowly from the mid-160 MiB range toward the mid-170 MiB range. Ten-minute medians were `164.836`, `167.164`, `169.172`, `171.211`, and `173.453 MiB`; the post-warm-up pre-output slope was approximately `+0.213 MiB/min`.

This is a small duration-scaled retention trend rather than a flat plateau. Source review shows that detector temporal smoothing/gating state is bounded and reset per run, while `AnalysisPipeline` retains the run's `TrackingSample` result history for later events, CSV, graphs and reporting. The trend remains an explicit residual limitation for longer or denser workloads.

## Finalization peak interpretation

The first output growth appeared at elapsed `3577.216 s`. Output then grew over about `281.103 s` from zero to the completed bundle.

During event capture creation, output grew through approximately `1,613` files while RSS remained near `175–177 MiB`. Graph/report and final bundle work then produced a transient RSS rise to approximately `454.9–466.7 MiB`.

The last high-memory samples stayed in a narrow band near `463–467 MiB` rather than continuing in repeated large upward steps, and the process exited immediately after finalization. The terminal telemetry row then reported owned RSS `0`, owned open files `0`, no child processes and exit code `0`.

The large peak is therefore classified as bounded finalization/report-generation memory for this event-heavy bundle, not as evidence of a post-exit leak. It remains a reason to avoid extrapolating this result to substantially larger event sets without additional evidence.

## Open files, children and output growth

Post-warm-up owned open-file count was `148 / 148 / 151` for min/median/max. The `10–20 min` and final-10-min medians were both `148`; the short increase to `151` occurred during bundle finalization.
Owned child-process count was `0` in every live telemetry row. The separate `caffeinate -i -w 63060` helper was launcher-owned sleep prevention, not an analyzer child; fresh post-run process checks found it absent together with analyzer and runner.

Output progression was confined to result construction near the end of the run. Two fresh post-exit observations one second apart both measured exactly `1,617 files / 687,497,078 bytes`, confirming no continuing output mutation.

## Completed bundle integrity

Production `ResultBundleReader` freshly reopened:

```text
sample/output/s6-f-one-hour-long-duration/launch-bcac3d6-20260801T053400Z/output/oil_level_analysis_20260801_154656/
```

Recovered bundle facts:

| Item | Value |
|---|---|
| Run ID | `09c5467b-2007-4332-84ec-d8542bcb65ed` |
| Tracking rows | `24,160` |
| Event rows | `1,607` |
| Detector/result label | `REVIEW_REQUIRED` |
| Bundle files | `1,617` |
| Bundle bytes | `687,497,078` |
| PNG files decoded | `1,609 / 1,609` |
| Report-local refs resolved | `1,609 / 1,609` |

Required manifest, tracking/events CSV, Recipe/session snapshots, review index, combined graph, report and analysis log were present. All JSON and CSV objects parsed successfully.
The Recipe snapshot bytes exactly matched tracked `sample/sample3.oilrecipe` at SHA-256 `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43`. Its canonical stable Recipe hash `55d23d0e53326e063a9f7712ae696dffb4b527bad0540886af18af50437694fa` matched `analysis_manifest.json`.

`SourceVideoResolver` resolved the derived source without override and validated `1280×720`, `2.0 FPS`, `24,160` frames and `FMP4` without metadata warning. No hidden staging, `.tmp`, `.part` or incomplete artifact remained in the bundle/output tree.

The production CLI did not create a debug sink. The bundle records the session's `basic` debug level with zero debug records; no debug trace/index exists, consistent with the earlier S6-E source-tree CLI behavior.

## Raw evidence preservation

Principal local-only evidence hashes at result collection were:

| Artifact | SHA-256 |
|---|---|
| `launch-manifest.json` | `e15a469581934b91c89447b59f8fb0ab809425ad72e55eba317a59c95c23f574` |
| `run-state.json` | `3530dcbf0a98983251343d4f43ca2c5d34f87f9eb00e0ed5f5d69ffc0c607a0a` |
| `completion-result.json` | `36786a6e96a4cccda64e17546ad8bf82fc65f2e3f3b34fcfa3a8a94b55d9b402` |
| `telemetry.jsonl` | `b4628960be8571639a5156816f0ef3e92746679d8b66737e8dd4ec556102a5ca` |
| `analyzer.log` | `09327d6df11a1300db1ee91cba994a599821af1580cd1ddc2750f7c24e0ab3c8` |
| `runner.log` | `2a6c084afb309bbbc14d748ff62fce86399cc3a773644d601377da50c29b501c` |
| `input-manifest.json` | `cd3bf6f9c27c3622de339e2d5591d25310bee38131c325b391525a857f1edb46` |

The S6-D1 mobile ZIP remained unchanged at SHA-256 `fd06ce5e464f6a9f0ec3a72d4c0c1be047b715721fb28ce0ef93a76ccb350855`. Its user-review checkpoint remains pending.

## Classification

`ONE-HOUR LONG-DURATION STABILITY: PASS-CANDIDATE`

The exact analyzer process ran continuously for more than 60 minutes, exited `0`, completed lifecycle `1/6–6/6`, finalized a readable bundle, accumulated neither file handles nor analyzer children, left no owned process, and produced stable post-exit output.

The stable-window to final-window RSS increase was far below the existing combined diagnostic signal. A slow analysis-period RSS rise and a large but bounded finalization peak are preserved explicitly rather than normalized away. The peak plateaued during report/finalization work and disappeared on process exit; it is not treated as a single-spike leak signal.

This Worker therefore finds no convincing one-hour resource leak for the exact workload. Independent exact-head audit is still required before the result can become accepted project evidence.

## Validation

Targeted source-tree suite:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_cli_analysis_progress.py \
  tests/unit/test_result_bundle_reader.py \
  tests/unit/test_source_video_resolver.py
```

Worker result: `24 passed in 3.19s`; exit code `0`.

Result collection also passed exact launch/completion reconciliation, raw telemetry parsing, interval continuity, production bundle reopening, all bundle PNG decoding, report-local link resolution, Recipe/source consistency, owned-process cleanup, post-exit output stability and ignored-evidence preservation checks.

## Residual limitations and next gate

This evidence does not establish controlled-idle CPU throughput. It does not test Windows, packaged one-folder relocation, clean-PC execution, Windows file locking, GUI/DPI, cancellation or close behavior.

The generated sample3 video is runtime-only repeated/re-encoded evidence. Its loop seams, blur and image quality are not detector-accuracy requirements. No MAE, precision, recall, false-positive/negative rate, calibrated level or physical detector PASS is claimed.
The slow approximately `+0.21 MiB/min` pre-output retention remains a bounded one-hour observation, not proof of an infinite-duration plateau. Longer or substantially denser event workloads may require separate follow-up if future acceptance scope expands.

S6-D1 remains independently blocked on explicit domain-owner mobile review. S6 remains `ACTIVE`, and S7 remains `PLANNED`.

The next technical owner is the **S6-F One-Hour Long-Duration Resource-Stability Fresh Exact-Head Auditor**. That Auditor must independently recompute the raw telemetry and bundle/resource evidence from this exact feature head before any merge or formal acceptance.

## Intentional non-runs

This Worker did not:

- start or repeat a soak;
- modify detector source, tests, dependencies, settings or thresholds;
- modify Recipes, original MP4s, provisional truth or product `.oiltruth`;
- modify or clean the preserved S6-F raw evidence;
- complete or infer the S6-D1 user review;
- judge detector physical accuracy or tune against sample3;
- claim controlled-idle CPU throughput acceptance;
- run Windows, packaging, clean-PC or GUI acceptance;
- merge, approve audit, close S6 or start S7;
- remove existing local evidence.
