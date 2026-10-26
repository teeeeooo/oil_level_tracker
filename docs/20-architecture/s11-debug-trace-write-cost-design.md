# S11 debug-trace write cost

**Status: B-1 IMPLEMENTED (2026-10-26).** The measurements, the identity check
and the remaining candidates are in
[RTP-1](../50-diagnostics/s11/2026-10-26-run-time-profile.md). This document
owns the contract that a write-cost change must keep.

## Purpose

On the Mac, a BASIC or FULL debug trace makes an analysis run about 2.6× as
long as the same run without a trace. That is about 60 % of the run. The
tracking output is identical at every level, so the trace is a pure
observer. This design reduces the cost of writing it without changing what
is written.

## Contract

`JsonlDebugTraceWriter` (`TRACE-PUBLICATION`) keeps its responsibilities:
- one compact JSON record per captured detection;
- that record's PNG images at fixed paths;
- the resolver's final decision as a `sequence` member, added at finalize;
- an index with the byte offset and length of each record.

A write-cost change must keep all of the following:
- **Byte-identical output.** Every file in the staging tree is byte-identical
  for the same run ID, input and code path. It is checked on the BASIC and
  FULL traces of sample4 with a fixed run ID.
- **No feedback into the run.** No detector, resolver or publication input
  changes. The trace stays non-authoritative, and the tracking output keeps
  its fingerprint.
- **The same failures.** The existing `OSError`s and image-encode warnings,
  in the same record order.

## B-1 (implemented)

- **Finalize appends instead of re-encoding.**
  - `write` stores each record as compact, JSON-safe JSON with no
    `sequence` member.
  - So `_with_sequence_member` appends `,"sequence":<annotation>` before the
    closing brace. That equals decoding the record, setting the member and
    encoding it again, and the full record is no longer decoded.
- **`_json_safe` has exact-type fast paths** for float, str, int, None, dict,
  list and tuple. Every subclass takes the unchanged general path. That
  covers bool, enums and NumPy scalars, which are subclasses of float or int.

## Staging publication (implemented 2026-10-26, speed step (가))

`OutputBundleStore` used to copy the finalized staging into the bundle file
by file (`shutil.copy2`). On Windows that took about 29 s of a 225 s SPL#4
FULL run, for about 0.6 GB
([step-9 timing](../60-evidence/s11/2026-10-26-step9-windows-receipt.md#windows-timing-threadripper-7945wx)).
- **What `_move_debug_staging` does:**
  - It checks the staging as before: it must exist and hold no symbolic
    link.
  - It removes the empty bundle `debug` directory and renames the staging
    into its place.
- **The fallback:** a rename on another volume, or any other rename failure,
  falls back to the unchanged copy.
- **Nothing else changes:**
  - the staging is discarded after publication as before;
  - failure cleanup, validation and the atomic bundle commit are unchanged.
- **Byte identity:** sample4 FULL with a fixed run ID, before vs after. The
  bundle `debug` tree (2,601 files) and the CSVs are equal.
  - On the Mac the bundle step went from 7.1 s to 6.2 s, because APFS copies
    are already cheap.
  - The Windows effect is measured on the next Windows run.
- **Tests:**
  - the bundle bytes are equal by rename and by the copy fallback;
  - a symbolic link in the staging is still rejected.

## Not adopted, and open candidates

- **Concurrent encoding of one record's images:** reverted. One full-frame
  `overlay` dominates, so it saved about 1 %.
- **One ordered background worker for PNG encoding and file writing (B-1b):**
  - It would keep byte identity only if the work stays in submission order.
  - Encode errors would have to reach the record before it is written.
  - Readers of the trace before finalize would have to wait for the worker.
  - It waits for the Windows timing breakdown.

## History Review

- Logic-map nodes: `TRACE-PUBLICATION`, `SEQUENCE-COMPOSITION`, `CSV-PUBLICATION`
- Failure-registry entries: `S11-F10`
- Prior mechanisms reviewed: the R18 and R21 trace contracts (additive, JSON-safe, non-authoritative `sequence` diagnostics attached without rerunning detection), the R9 performance boundary (sequence annotation is finalization-time I/O), and the completed-window resolution that owns the retrospective correction in memory.
- Prior mechanisms rejected: dropping or shrinking trace content, changing the PNG encoding, skipping the `sequence` member, and moving resolver work into the trace; each would change the published trace or its consumers.
- Preserved contracts: byte-identical trace files, independent tracking output (fingerprint unchanged at NONE/BASIC/FULL), record order and index offsets, the existing error and warning behavior, and the `sequence` member read by the review UI and the diagnostics.
- Existing feature coverage: the production `AnalysisPipeline` with IFO v2 + top-exit v3 on sample4 at BASIC and FULL with a fixed run ID, the existing debug-trace unit and integration suites, and two added unit tests (the splice equals decode-and-re-encode; the fast paths equal the general conversion).
- Execution scope: one storage-adapter change; local timing, profiling and byte-identity runs of sample4 in the session scratchpad; the B-1 identity confirmed on Windows by the step-9 T-1 run. Staging publication (2026-10-26): one `OutputBundleStore` change with two integration tests and a before/after byte-identity run of the sample4 FULL bundle in the scratchpad (the old code from a temporary worktree of HEAD).
- Difference from prior failures: no detector mechanism changes; the change is an equivalent encoding of the same bytes, so it cannot repeat a selection, authority or publication failure.
- Logic-map impact: NONE — `TRACE-PUBLICATION` keeps the same inputs, outputs and invariants; only the cost of producing the same bytes changes.
- Failure-registry impact: NONE — no runtime detector mechanism changes; the trace stays non-authoritative under the `S11-F10` boundary.
