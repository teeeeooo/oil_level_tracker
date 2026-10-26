# S11 parallel-Glass frame loop (opt-in)

**Status: IMPLEMENTED 2026-10-26 as an opt-in, default OFF. Disposition
(user, 2026-10-26): kept as a development aid, default OFF and not enabled in
the product.** The packaged product carries no debug trace, so its case is the
NONE run, where the Windows gain is only 13 %. The FULL development runs gain
31 %. Revisit at production packaging, after measuring why the NONE gain is
small (per-worker time, OpenCV thread count).

It was speed step (나) of the order the user chose ("2는 가,나,다 순으로 하나씩 해보자"). The
measurements behind it are in
[RTP-1](../50-diagnostics/s11/2026-10-26-run-time-profile.md) and the
[step-9 timing](../60-evidence/s11/2026-10-26-step9-windows-receipt.md#windows-timing-threadripper-7945wx):
detection is about 64 s of a 91 s SPL#4 run without a trace. The product
default stays sequential. Turning it on in the packaged app is a separate
user decision.

## Why processes, not threads

`OilHypothesisPipeline` serializes every call through one ordered dispatch
(a sequence number under a lock), whatever the Glass. Much of the detector
is also Python-level work on small NumPy arrays, which holds the GIL. Threads
would therefore not overlap. Each Glass gets its own process instead.

## Why it can be exact

- **The detector keeps its state per Glass.**
  - Keyed by Glass ID: trackers, static maps, the Foam gate, the motion
    trackers and the Oil pipeline store.
  - The capture policy compares each detection with the same Glass's
    previous one.
- **Checked directly:** on sample4 with its Glass duplicated (0–20 s, FULL),
  each Glass run alone gives the same rows and the same trace records,
  byte for byte, as it does next to the other Glass.

## Contract

- **Opt-in.** `DetectionRunPolicy.parallel_glasses` (default False),
  reached through `AnalysisPipeline(parallel_glasses=...)`.
- **When it applies.** All of these must hold:
  - two or more Glasses;
  - no static-decode reuse;
  - the detector offers `worker_factory()`;
  - the factory and the video reader factory can be pickled.

  Otherwise the run is sequential. `last_run_parallel` says which path ran.
- **Workers.** One spawned process per Glass. Each one:
  - builds an identically configured detector
    (`OpenCvPhaseDetector.worker_factory`, its constructor options) and its
    own reader;
  - learns that Glass's static artifacts on the same schedule;
  - detects every target.
- **The parent keeps the sequential loop.**
  - It reads the workers' results strictly in the sequential order: target
    by target, Glass by Glass.
  - So every callback, progress count, consecutive-failure count, trace
    record and the completed-window resolution happen in the same order with
    the same values.
- **Decodes are compared.** The first Glass's decode stands for the target,
  as the shared decode did. A Glass whose own decode reports another frame
  index or timestamp stops the run with `GlassWorkerError`; it never
  publishes silently.
  - A decode error in the first Glass is the target's decode failure, as
    before.
- **Bounded memory.** Each worker can run at most 4 results ahead.
- **Stops.** Cancellation, an error or the end of the run terminates the
  workers. A worker that ends early is reported as `GlassWorkerError`.

## Checks

- **Unit (`tests/unit/test_parallel_glass_detection.py`):**
  - the parallel run equals the sequential run in every observation,
    callback and progress event, including a decode error and a detect
    error;
  - the completed-window resolution is reproduced;
  - the same consecutive-failure stop (2.0 s, count 2);
  - the fallback to sequential for an unpicklable reader factory or one
    Glass.
- **End to end:** managed run `sample/output/s11-parallel-glass-check-20261026-001`.
  - Setup: a two-Glass sample4 session, FULL, through the cadence field
    runner.
  - The parallel rerun reproduces the sequential source in 226/226 rows and
    226/226 trace lines, and the index is equal.
  - Wall time on the Mac: 31.9 s against 54.4 s.
- **A timer limit:** the runner's stage timers measure the parent. In
  parallel mode, detection runs in the workers and reads 0 there.

## Not covered yet

- **The packaged Windows app.** The PyInstaller entry would need
  `multiprocessing.freeze_support()`. The bootstrap passes a lambda reader
  factory, which keeps the app sequential today. Both belong to the
  default-ON decision.
- **The Windows timing: measured 2026-10-26** (step 11,
  [receipt](../60-evidence/s11/2026-10-26-step10-11-windows-receipt.md#step-11--speed-timing-and-identity)).
  - Rows and trace bytes are identical.
  - SPL#4 FULL: 160.1 → 110.3 s. The parent waited 65.7 s, so the run is
    worker-bound.
  - NONE: 90.9 → 79.5 s.

## History Review

- Logic-map nodes: `SEQUENCE-COMPOSITION`, `TRACE-PUBLICATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F10`
- Prior mechanisms reviewed: the sequential `DetectionRunCoordinator` loop (shared decode, per-Glass detect, consecutive-failure policy, completed-window resolution), the per-Glass detector state and capture policy, the serialized `OilHypothesisPipeline` dispatch, and the B-1/staging trace contract.
- Prior mechanisms rejected: thread parallelism (serialized dispatch and GIL-bound work), detecting frames out of order, and merging per-worker traces after the run (record order and offsets would need rebuilding).
- Preserved contracts: identical rows, events and trace bytes; the sequential callback, progress and failure order; per-frame fail-closed behavior; the completed-window resolution in the parent; the sequential default.
- Existing feature coverage: the production `AnalysisPipeline`, `OpenCvPhaseDetector` with IFO v2 + top-exit v3, the JSONL trace writer and bundle store, the cadence field runner, and a duplicated-Glass sample4 session; no Recipe or session change.
- Execution scope: one new application module, a policy field, a detector factory method and a pipeline option, with unit tests, a direct independence check and one closed local managed run; no Windows run yet.
- Difference from prior failures: a scheduling change that consumes the same per-Glass results in the same order; it adds no detector mechanism and cannot change a selection, authority or publication.
- Logic-map impact: NONE — every node keeps its inputs, outputs and order; only where a Glass's frame loop executes changes, behind an opt-in.
- Failure-registry impact: NONE — no runtime detector mechanism changes; the trace stays non-authoritative under `S11-F10`.
