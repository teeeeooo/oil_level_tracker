# S6-E Bounded Runtime Soak and Resource-Leak Screening Evidence

## Status

- **Feature branch:** `feature/s6-bounded-runtime-soak`
- **Starting production main:** `a13b73b7b48aa6fecc0e7afb71d8dd1080ae5622`
- **Starting commit:** `docs: preserve S6 domain-owner review priorities`
- **Screening result:** `SOAK SCREENING: NO OBVIOUS RESOURCE LEAK`
- **Evidence state:** completed on the feature head and awaiting fresh independent exact-head audit
- **Milestone state:** S6 remains `ACTIVE`; S6-D remains pending; S7 remains `PLANNED`

This result means only that two short source-tree diagnostic runs showed no obvious crash, state accumulation, owned-process leak, open-file accumulation, or post-finalization growth. It is not official long-duration memory acceptance, controlled-idle CPU or throughput acceptance, representative field-duration acceptance, detector accuracy acceptance, Windows acceptance, or packaged-runtime acceptance.

## Scope and invariants

The Worker used unchanged production source, tracked Recipes, detector settings, tests, dependencies, and original MP4 bytes. Local derived videos, helper scripts, telemetry, analyzer logs, and generated result bundles remain under ignored `sample/output/` and are not committed.

No detector threshold was tuned. No Recipe, original MP4, provisional truth, or product `.oiltruth` was edited. Detector outcome labels from the runs are retained only as bundle facts and are not compared with truth or interpreted as accuracy PASS/FAIL evidence. Loop seams and re-encoding artifacts are not treated as physical transitions or detector defects.

The following materially adjacent owners were reviewed before execution:

- production analysis entrypoint: `src/oil_tracker/cli.py`;
- session and video metadata: `src/oil_tracker/domain/session.py` and `OpenCvVideoReader`;
- lifecycle progress and analysis ownership: `AnalysisPipeline` and `AnalysisStage`;
- temporal Oil/Foam state: `OpenCvPhaseDetector`, `TemporalTracker`, `FoamTemporalGate`, and `OilHypothesisPipeline`;
- bundle finalization and cleanup: `OutputBundleStore`;
- result reopening and validation: `ResultBundleReader`.

The production pipeline resets the detector at run start, closes the video reader in `finally`, validates a hidden temporary bundle, atomically renames it to the final directory, and removes incomplete temporary/debug staging on failure. The CLI-created pipeline has no debug sink factory, so both runs produced zero debug records and no debug directory despite the session snapshot retaining the default `basic` level.

## Local evidence identity

Generated evidence root:

```text
sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/
```

This path is ignored and local-only. The principal helper identities are:

| Artifact | SHA-256 |
|---|---|
| `generate_inputs.py` | `7e1a6100c7cce9bf3163eeaf34fc68eb691c19b0ed0c2b6c1146ccd8d908ea62` |
| `run_with_telemetry.py` | `92b6b588116d5b85e6e80ec346d35520fbea760dddf09776b2cc907a947580db` |
| `inspect_soak.py` | `07d68a5369f071d350240fc2ee49410f0e659c9061b3c53902d8d3629a055b9d` |
| `input-manifest.json` | `05db580371d624216ccd3811d02535417ea3b494d4acc64967f72e035a92aaac` |
| `inspection-summary.json` | `38af6b02bf020c6bde3466ae2e13760561ed53e24c17efcc9267ee4fcdd6a5f9` |

## Derived input generation

Exact generation command:

```bash
PYTHONPATH=src .venv/bin/python \
  sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/generate_inputs.py
```

The script used OpenCV random-seek decoding at the same timestamp schedule semantics as production sampling. It decoded the selected source window at 2.0 FPS, verified the decoded frame index, timestamp, and BGR SHA-256 were identical at every repeat position, and wrote an `mp4v` stream at 2.0 FPS. OpenCV reported the reopened codec as `FMP4`. Each output was then reopened and completely sequentially decoded; declared and decoded frame counts matched, timestamps were monotonic, and the full analysis window was usable.

### sample3 transition soak

| Field | Value |
|---|---|
| Source | `sample/sample3.mp4` |
| Source SHA-256 | `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` |
| Recipe | `sample/sample3.oilrecipe` |
| Recipe SHA-256 | `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43` |
| Source window | `30.03–105.0 s` |
| Source-cycle schedule | 151 frames at 2.0 FPS |
| Repeat count | 4 |
| Derived output | `sample3-transition-soak.mp4` |
| Output SHA-256 | `c97f397fba961f99636e344eb32d9885df7d306024ecf68e086e2d46ead29e07` |
| Output size | 6,276,087 bytes |
| Codec / resolution / FPS | `FMP4` / `1280×720` / `2.0` |
| Declared / decoded frames | `604 / 604` |
| Declared duration | `302.0 s` |
| First / last usable frame | `0 @ 0.0 s` / `603 @ 301.5 s` |
| Analysis window | `0.0–301.5 s`, monotonic and fully usable |

The first selected source frame was source frame 900 at 30.03 s; the final selected frame was source frame 3147 at 105.0049 s. Repeated source-frame identity was exact for all four cycles.

### sample4 Foam-path soak

| Field | Value |
|---|---|
| Source | `sample/sample4.mp4` |
| Source SHA-256 | `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` |
| Recipe | `sample/sample4.oilrecipe` |
| Recipe SHA-256 | `53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849` |
| Source window | `0.0–56.0 s` |
| Source-cycle schedule | 113 frames at 2.0 FPS |
| Repeat count | 6 |
| Derived output | `sample4-foam-path-soak.mp4` |
| Output SHA-256 | `c3d1e5cd642bb77a0c9019d2b8ac731480e61fbe8a01c4fbc53e20e4cbe3d1fd` |
| Output size | 28,774,920 bytes |
| Codec / resolution / FPS | `FMP4` / `1080×1234` / `2.0` |
| Declared / decoded frames | `678 / 678` |
| Declared duration | `339.0 s` |
| First / last usable frame | `0 @ 0.0 s` / `677 @ 338.5 s` |
| Analysis window | `0.0–338.5 s`, monotonic and fully usable |

The first selected source frame was frame 0 at 0.0 s; the final selected frame was frame 1680 at 56.0 s. Repeated source-frame identity was exact for all six cycles.

## Sequential production CLI execution

The runs were executed sequentially and never overlapped.

### Run 1 — sample3 transition

```bash
.venv/bin/python \
  sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/run_with_telemetry.py \
  --name sample3-transition \
  --output-root sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/sample3-output \
  -- \
  .venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/sample3.oilrecipe \
  --video sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/sample3-transition-soak.mp4 \
  --output sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/sample3-output \
  --start 0 \
  --end 301.5 \
  --compressor-start 0 \
  --sampling-fps 2.0
```

- analyzer PID: `66185`;
- process exit: `0`;
- diagnostic wall time: `111.402487 s`;
- terminal process CPU time reported by macOS: `2:31.25`;
- lifecycle: complete `1/6` through `6/6`, including `604/604` detections and finalization `4/4`;
- final bundle: `sample3-output/oil_level_analysis_20260731_184016`;
- detector result stored by the bundle: `REVIEW_REQUIRED` — recorded without accuracy interpretation.

### Run 2 — sample4 Foam path

```bash
.venv/bin/python \
  sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/run_with_telemetry.py \
  --name sample4-foam-path \
  --output-root sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/sample4-output \
  -- \
  .venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/sample4.oilrecipe \
  --video sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/sample4-foam-path-soak.mp4 \
  --output sample/output/s6-bounded-runtime-soak/worker-a13b73b-20260731T092905Z/sample4-output \
  --start 0 \
  --end 338.5 \
  --compressor-start 0 \
  --sampling-fps 2.0
```

- analyzer PID: `67358`;
- process exit: `0`;
- diagnostic wall time: `101.849343 s`;
- terminal process CPU time reported by macOS: `3:33.11`;
- lifecycle: complete `1/6` through `6/6`, including `678/678` detections and finalization `4/4`;
- final bundle: `sample4-output/oil_level_analysis_20260731_184209`;
- detector result stored by the bundle: `FAIL` — recorded without truth comparison or accuracy interpretation.

## Telemetry method

One local recorder process launched one analyzer process per run. The recorder sampled approximately every five seconds directly into ignored JSONL. It captured UTC timestamp, elapsed time, analyzer PID/RSS/CPU time/state/open-file count, recursively owned child PID/RSS/open files when present, owned-process totals, output-directory file count/bytes, and process exit status. It also recorded host `uptime`, `memory_pressure -Q`, and `vm_stat` only at run start and end.

The agent did not poll telemetry every five seconds. It collected terminal completion and inspected the completed files. No unrelated process inventory was taken and no other workload was stopped or terminated.

Both runs observed only their analyzer PID and no owned child process. Start/end system-wide free-memory percentage was 68% for both runs. Host load varied during the runs, so wall and CPU values are diagnostic context only.

## Resource screening statistics

The initial 20% of each live telemetry interval was excluded as warm-up/context. RSS values below are analyzer plus owned-child totals; no child RSS was present.

| Metric | sample3 transition | sample4 Foam path |
|---|---:|---:|
| Telemetry rows / live rows | 22 / 21 | 20 / 19 |
| Post-warm-up samples | 17 | 15 |
| Post-warm-up RSS min | 162.56 MiB | 167.86 MiB |
| Post-warm-up RSS median | 163.05 MiB | 168.08 MiB |
| Post-warm-up RSS max | 186.00 MiB | 170.81 MiB |
| First post-warm-up quarter median | 162.81 MiB | 167.93 MiB |
| Last quarter median | 163.38 MiB | 168.39 MiB |
| Quarter-median delta | +0.56 MiB / +0.35% | +0.46 MiB / +0.27% |
| Simple post-warm-up slope | +0.098 MiB/s | +0.018 MiB/s |
| Open-file range | 148–151 | 148–149 |
| First / last-quarter open-file median | 148 / 148 | 148 / 148 |
| Terminal analyzer/open-file state | exited / 0 | exited / 0 |
| Remaining owned processes | none | none |

The required review threshold is a last-quarter median increase that exceeds both 64 MiB and 25%. Neither run approached it. During the analysis phase, sample3 RSS moved from 162.56 MiB at the warm-up boundary to 163.38 MiB before output work; its 186.00 MiB maximum was a short finalization/capture/graph peak immediately before exit. sample4 similarly remained near 168 MiB and reached 170.81 MiB only at final output creation. Neither trace showed repeated large upward steps or a late unbounded sequence without termination.

Open-file counts remained at a median of 148 across the first and last post-warm-up quarters. The small maxima occurred during output finalization, after which the analyzer exited and terminal owned open-file count was zero.

## Output growth and cleanup

Observed output growth was confined to final bundle creation:

- sample3: `0 files / 0 bytes` → `23 / 9,883,661` → `53 / 20,416,226` → `57 / 20,581,510`;
- sample4: `0 files / 0 bytes` → `14 / 24,362,932` → `27 / 30,753,070`.

Each recorder sampled the output root twice after analyzer exit. File count and total bytes were identical on both checks. No analyzer or owned child process remained.

Final local bundle identities:

| Bundle | Files | Bytes | Sorted tree SHA-256 |
|---|---:|---:|---|
| sample3 | 57 | 20,581,510 | `f87517366ffc04cbf91548603c0ca7026304cbfdd6636ef84b31853a052bdb14` |
| sample4 | 27 | 30,753,070 | `9f189b5a4afa65a32eaf84545cdfd59ef8a9867682712b54e5d4866b17b8beaf` |

## Bundle integrity inspection

Both bundles passed all of the following checks:

- reopened with production `ResultBundleReader`;
- required manifest, tracking CSV, events CSV, Recipe snapshot, session snapshot, review index, report, combined graph, and analysis log present;
- all JSON objects and CSV rows parsed;
- tracking rows matched the scheduled detections: 604 for sample3 and 678 for sample4;
- event rows parsed: 47 for sample3 and 17 for sample4;
- all report-local `src`/`href` references resolved inside the bundle: 49 for sample3 and 19 for sample4;
- every generated image decoded: 49 for sample3 and 19 for sample4;
- no hidden staging, `.tmp`, `.part`, or debug artifact remained;
- Recipe snapshot semantics matched the unchanged tracked Recipe;
- manifest canonical Recipe snapshot hashes matched (`55d23d0e...` for sample3 and `dfe852d8...` for sample4);
- debug record count was zero and no debug directory existed;
- each derived source video reopened and decoded its first and last usable frames;
- original source videos reopened and retained their pre-run SHA-256 identities;
- generated inputs, source files, Recipes, and bundles remained reopenable after inspection.

macOS cleanup and reopen behavior does not substitute for Windows file-lock acceptance.

## Screening decision

`SOAK SCREENING: NO OBVIOUS RESOURCE LEAK`

No crash, hang, non-zero exit, incomplete lifecycle, unreadable bundle, threshold-level post-warm-up RSS increase, clearly unbounded late RSS sequence, open-file accumulation, owned-process residue, post-exit output growth, incomplete staging, temporary artifact, or insufficient telemetry was found.

This bounded result does not close S6-E until fresh independent exact-head audit and merge. It does not satisfy official long-duration stability, controlled-idle performance, CPU throughput, Windows, packaging, GUI, detector accuracy, or S6 final acceptance.

## Targeted validation

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_cli_analysis_progress.py \
  tests/unit/test_result_bundle_reader.py \
  tests/unit/test_source_video_resolver.py
```

Result: `24 passed in 2.94s`; exit code `0`.

Input/output hashes, complete sequential decode counts, telemetry structure/sample counts, bundle reopening, report assets, image decoding, Recipe snapshot/hash consistency, lifecycle logs, owned-process cleanup, and post-exit output stability were additionally checked by the ignored local scripts identified above.

## Intentional non-runs and next owner

Not run or claimed:

- official long-duration or representative field-duration soak;
- controlled-idle CPU, throughput, or performance acceptance;
- detector accuracy metrics or truth comparison;
- source, test, dependency, Recipe, threshold, MP4, provisional truth, or product `.oiltruth` repair;
- Windows, packaged one-folder, clean-PC, GUI, DPI, cancellation, or file-lock acceptance;
- merge, registered-checkout synchronization, S6 Close, S7 start, branch cleanup, or worktree hygiene.

The next owner is the **S6-E Bounded Runtime Soak and Resource-Leak Screening Fresh Exact-Head Auditor**.
