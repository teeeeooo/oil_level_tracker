# RTP-1 — analysis run-time profile and debug-trace cost

**Status: MAC PROFILE COMPLETE; B-1 (trace cost, output byte-identical)
IMPLEMENTED and byte-identical on Windows. The Windows timing breakdown is
RECEIVED ([step-9 receipt](../../60-evidence/s11/2026-10-26-step9-windows-receipt.md#windows-timing-threadripper-7945wx)):
PNG encoding, the staging copy and the debug-image build lead the trace cost;
detection is the floor. Speed step (가), staging rename instead of copy, is
IMPLEMENTED byte-identical ([design](../../20-architecture/s11-debug-trace-write-cost-design.md#staging-publication-implemented-2026-10-26-speed-step-가)).
Speed step (나), the parallel-Glass frame loop, is IMPLEMENTED as an opt-in,
default OFF ([design](../../20-architecture/s11-parallel-glass-detection-design.md)):
byte-identical, and a two-Glass sample4 FULL run goes from 54.4 s to 31.9 s
on the Mac.** The
user asked whether detection speed can improve ("90초짜리 영상 한번 돌리는데도
시간이 꽤 걸리고있거든?", 2026-10-26) and agreed the order: record the
decisions, reduce the trace cost with unchanged output, then freeze the
cadence diagnostic ("응 순서에 동의함. 진행하자"). Speed work was earlier
planned for after the detector work. B-1 changes no detector output, so it
does not conflict with that plan.

## Question

Where does an analysis run spend its time, and which part can be reduced
without changing any output?

## Measurements (Mac)

**Setup:**
- Apple M1 (8 cores), OpenCV 4.14.0, Python 3.14.
- sample4, 0–56 s, one Glass, 2 fps (113 frames).
- IFO v2 + top-exit v3.
- Every glass is confirmed `UNKNOWN_REVIEW`, as in
  `s11_report_observability_replay._session`.
- Scripts and outputs were kept in the session scratchpad only. No managed
  run and no repository output.

| Debug level | Wall | Per Glass-frame | Trace output |
|---|---:|---:|---|
| NONE | 11.2 s | 0.10 s | — |
| BASIC (session default) | 29.1 s | 0.26 s | JSONL 180 MB, about 392 MB with PNGs |
| FULL | 29.5 s | 0.26 s | JSONL 181 MB, 2,601 files |

- **The tracking output is identical at every level.** The
  `_tracking_fingerprint` is `e447626b…` for NONE and BASIC alike. The trace
  is a pure observer.
- **The time is linear in frames.** NONE at 2/4/8 fps (113/225/449 frames)
  takes 0.100/0.100/0.102 s per Glass-frame. BASIC at 4 fps takes 0.263 s.
- **The records are large.** About 1.6 MB per record, the same ratio as the
  SPL#1 FULL trace (about 1.9 GB for 1,202 records).

**BASIC breakdown (cProfile, 58.5 s profiled):**

| Part | Share | Notes |
|---|---:|---|
| Per-record trace write | 26 % | `_json_safe`: 16.5 M recursive calls |
| `finalize` rewrite | 22 % | rereads every record, sanitizes it again, re-encodes it |
| Debug-only interface diagnostics | 14 % | `measure_oil_interfaces`, `build_interface_witness` |
| PNG encoding | 7 % | almost all in `overlay`, see below |
| Video seek | 6 % | `CAP_PROP_POS_MSEC` per sample |
| Detection | the rest | — |

The NONE profile splits 75 % detection and 20 % seek.

## The finalize rewrite is not the retrospective correction

The user asked whether the rewrite is the post-detection correction, which
links a lost rising level after reading the whole trace. It is not.
- **Where the correction runs:** `DetectionRunCoordinator` keeps each
  frame's detection and candidates in memory (artifacts dropped). After the
  last frame, `resolve_completed_window` resolves the whole window
  (`SEQUENCE-COMPOSITION`).
  - Tracklet association and confirmation, R20 delayed reacquisition and
    the default-OFF fast-rise association all run there (`OIL-TRACKLET`,
    lifecycle owners).
  - The initial-state reconstruction runs downstream on `TrackingSample`.
  - None of these reads the trace.
- **What the rewrite does:** `annotate_sequence` then
  `_apply_sequence_annotations` copy the resolver's final decision into each
  captured record as a `sequence` member. Data flows one way, from the
  resolver to the trace.
- **The owners say the same:**
  - logic map `TRACE-PUBLICATION` and invariant 7: debug is
    non-authoritative and cannot alter the official output;
  - R9 performance boundary: the annotation is finalization-time I/O;
  - R21: the witness is attached without rerunning detection.
- **The NONE result confirms it:** a run with no trace has the same
  tracking fingerprint.
- **The member is still needed.** The review UI and the diagnostics read it.
  `s11_fast_rise_readout` reads `record['sequence']`. Only its cost is
  reduced.

## B-1 change (implemented)

The contract is owned by the [write-cost design](../../20-architecture/s11-debug-trace-write-cost-design.md).

`src/oil_tracker/adapters/storage/jsonl_debug_trace_writer.py`:
- **The rewrite splices instead of re-encoding.**
  - Each stored line is compact JSON that `write` already made JSON-safe,
    and it has no `sequence` member.
  - So `_with_sequence_member` appends `,"sequence":<annotation>` before the
    closing brace. That equals decoding the line, setting the member and
    encoding it again.
- **`_json_safe` gains exact-type fast paths** for float, str, int, None,
  dict, list and tuple. Subclasses, such as bool, enums and NumPy scalars,
  take the unchanged general path.
- **Tried and reverted:** encoding a record's images concurrently. It saved
  about 1 % because a single image dominates.

**Identity check:** sample4 0–56 s with a fixed `run_id`, before vs after.

| Level | Trace tree hash | JSONL | Index | Tracking | Wall |
|---|---|---|---|---|---|
| BASIC | `f54be313…` = | `f59dd8f2…` = | `362d8455…` = | `e447626b…` = | 29.1 s → 22.5 s |
| FULL | `8549ce82…` = | `962bdc10…` = | `1e6df049…` = | `e447626b…` = | 29.5 s → 22.7 s |

- Every file in the staging tree is byte-identical. The unchanged code gave
  the same hashes on two runs.
- The finalize step went from 12.7 s to 0.26 s (profiled).
- **Tests:**
  - added `test_sequence_annotation_equals_decoding_and_reencoding_the_record`;
  - added `test_json_safe_fast_paths_match_the_general_conversion`;
  - the debug-trace suites pass (67 tests).

## What remains (not changed)

Timed without the profiler, after B-1 (BASIC):

| Part | Time |
|---|---:|
| Trace write per record (total) | 8.0 s |
| … of which PNG | 3.8 s |
| Seek | 3.9 s |
| Debug-only `measure_oil_interfaces` | 2.2 s |

- **The `overlay` image dominates PNG time.** It is the full frame
  (1234×1080×3, about 1.86 MB as PNG), 32 ms per record. All the other images
  are 104×104 crops under 0.05 s in total.
  - With two Glasses, every frame stores two full-frame overlays.
- **Candidates, not started.** Each needs evidence and its own identity
  check:
  - **B-1b:** move PNG encoding and file writing to one ordered background
    worker. Encoding releases the GIL, so it overlaps detection.
    - Errors would surface at the next write or at finalize.
    - Readers of the trace before finalize would have to wait.
  - **B-2:** process Glasses in parallel. The temporal state is per Glass.
  - **B-3:** decode ahead in a thread.
  - **B-4:** detector-internal vectorization. It is the riskiest, because
    the output must stay bit-identical.
- **Windows is the open question.** SPL#1 FULL took about 2.1 s per
  Glass-frame (42–44 min / 1,202), about 8× this Mac's BASIC rate.
  - The cause is unknown. It could be the CPU, the per-file cost on NTFS
    (about 12k files, including antivirus scanning) or seek on a long field
    video.
  - The next Windows request carries a timing breakdown of the same parts.
    That decides between B-1b, B-2 and B-3.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `SEQUENCE-COMPOSITION`
- Failure-registry entries: `S11-F10`
- First harmful stage: not applicable — a run-time profile; no detection loss is examined.
- Existing feature coverage: the production `AnalysisPipeline` with `OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)`, the existing `JsonlDebugTraceWriterFactory` at NONE/BASIC/FULL, the session `sampling_fps`, and the existing `_tracking_fingerprint`; sample4 only (sample3 is quarantined and was not used).
- Execution scope: local timing and cProfile runs of sample4 with outputs in the session scratchpad (deleted after hashing); one storage-adapter change with two unit tests and a byte-identity check of BASIC and FULL traces; no detector, Recipe, session or truth change; no Windows run.
- Logic-map impact: NONE — `TRACE-PUBLICATION` keeps its inputs, outputs and invariants; the annotation bytes are unchanged.
- Failure-registry impact: NONE — no detector mechanism changes; the trace stays non-authoritative (`S11-F10` boundary unchanged).
