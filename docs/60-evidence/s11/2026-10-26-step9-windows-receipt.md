# Step-9 Windows receipt — 2026-10-26

**Status: RECEIVED / T-1 identity PASS (rows and trace bytes) / CAD-1 C1
FAILS: outcome C by the frozen rule, read with a named limit / Windows timing
recorded.** The reply to the
[step-9 combined request](../../40-operations/s11-current-windows-field-qualification.md#step-9-combined-request)
came back through the user as verbatim stdout, relayed by OCR. It is read
against the
[CAD-1 protocol](../../50-diagnostics/s11/2026-10-26-cadence-diagnostic.md)
frozen before the run. Nothing is tuned. Top-exit, the gate and the
fast-rise association stay default OFF. FIELD FAIL / O2 OPEN and review-006
pending are unchanged.

## Runs and identity

| Run | Run ID | Rate / debug | Rows (BASE, Accum) |
|---|---|---|---|
| SPL4_B_ref (step 7) | `005e0d58-024e-4c38-b5eb-becfc552e0cb` | 2 fps / FULL | 181, 181 |
| T-1 `SPL4_T1_2fps_full` | `b6222009-ecc7-41c9-a286-3dccc153ef97` | 2 fps / FULL | 181, 181 |
| T-2 `SPL4_T2_2fps_none` | `75816269-b3d4-4952-950f-882603f9a3f3` | 2 fps / NONE | 181, 181 |
| C-1 `SPL4_C1_6fps_full` | `e104a258-a010-4173-9566-8f33cec96e45` | 6 fps / FULL | 541, 541 |

- **Version:** every run prints
  `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1+initial-full-observation-v2+top-exit-full-v3`.
- **Source:** four of the six SHA-256 values match exactly.
  - `s11_cadence_field.py` reads `…efa1bf14…8bccb4b9…` against
    `…efa18f14…8ccb4b9…`.
  - `oil_interface_tracklets.py` and `oil_observation_resolver.py` show the
    usual `0`/`8`, `d`/`0` slips.
  - The request said to stop on any mismatch, and every step ran, so these
    are read as OCR errors. That is an inference.
- **Platform:**
  - Python 3.14.3, OpenCV 4.13.0;
  - AMD Ryzen Threadripper PRO 7945WX, 12 cores / 24 threads.
  - The Mac had OpenCV 4.14.0.
- **T-1 identity (C-a): PASS.**
  - Rows: 362/362, 0 unmatched, 0 changed.
  - Trace: 362/362 lines equal once the run ID is normalized, and the index
    is equal.
  - `SPL4_B_ref` was written before B-1 (`914c8e6`), so B-1 keeps the trace
    byte-identical on Windows too.
- **T-2 identity (C-b):** 362/362 rows, 0 changed.

## CAD-1 cadence (C-c)

| Reading | Reference (2 fps) | C-1 (6 fps) |
|---|---|---|
| C1 first BASE FULL in 22.0–27.0 s | none — false | none — **false** |
| C2 hold to 61.0 s | false (no FULL) | false (no FULL) |
| C3 episode end in 61.0–65.0 s | false (no FULL) | false (no FULL) |
| C4 no BASE FULL in 65–90 s | true | true |
| C5 no Accum FULL | true | true |

**Stage readout, trial BASE 20.0–28.0 s (49 rows):**
- **Every row is UNKNOWN_REVIEW with no numeric Oil and no selected Oil
  candidate.**
  - Foam is published at 23.5–25.83 s (Y547 → Y329).
  - At 2 fps the same span had selected owners at Y801–802, Y756 and later.
- **The top-exit reasons, all observed:**
  - `CURRENT_INTERFACE_OR_STATE_RESET` (20.0–21.33 s and later rows): an Oil
    layer exists, but the bounded path chose unknown, and no unselected exit
    row qualifies.
  - `NO_TOP_EXIT_WITNESS` (21.5–22.33 s, 24.0–24.33 s and others): no branch
    applies.
  - `CURRENT_EVIDENCE_RESET` (23.0 s, and most rows from 24.67 s): the raster
    is unusable, empty evidence, or the frame is opposed.
- **Admitted minimum Y:** Y323.0 against the 27 % band end Y437.95.

**Outcome by the frozen rule: C.** C1 fails, and an admitted BASE Oil
candidate lies inside the band.

**The named limit of that reading:**
- **The admitted-minimum measure counts any admitted candidate.** It does
  not show that the candidate belongs to the rising level.
- **Y323 is the height of a near-stationary row** seen at 2 fps (tracklet
  `0042:0034`, Y323–325 at 21.0–24.5 s, `INSUFFICIENT_NET_PROGRESS`).
- **So "association no longer blocks" is not established.**
- **What is established:** at 6 fps no Oil owner is selected anywhere in the
  rise. The barrier is at the bounded path or evidence stage
  (`OIL-SELECTOR` / `OIL-PHASE-FILL`) whether or not association improved.

**Shared 2 fps grid (reported, not scored):**

| Glass, phase s | Rows | Oil ref → trial | Changed |
|---|---:|---:|---:|
| BASE 0–20.5 | 41 | 14 → 2 | 19 |
| BASE 20.5–27 | 13 | 3 → 0 | 6 |
| BASE 27–61 | 68 | 14 → 0 | 32 |
| BASE 61–65 | 8 | 0 → 0 | 6 |
| BASE 65–90 | 51 | 2 → 1 | 17 |
| Accum 0–20.5 | 41 | 1 → 10 | 11 |
| Accum 20.5–27 | 13 | 0 → 0 | 13 |
| Accum 27–61 | 68 | 1 → 8 | 31 |
| Accum 61–65 | 8 | 2 → 0 | 4 |
| Accum 65–90 | 51 | 19 → 2 | 26 |

- **6 fps changes most of the run, not just the rise.** BASE publishes almost
  no numeric Oil at 6 fps.
- **One loss is a gain:** BASE 27–61 s loses the 14 wrong-target rows inside
  the reviewed FULL interval, the rows the held fill-owner gate removes.
- **The other losses are new:** 0–20.5 s goes 14 → 2. Accum gains Oil early
  and loses it late.
- **Inference:** the frame-count constants, three times shorter in time,
  change ownership broadly. The rows were not reviewed.

## Windows timing (Threadripper 7945WX)

| Stage | T-1 2 fps FULL | T-2 2 fps NONE | C-1 6 fps FULL |
|---|---:|---:|---:|
| Wall | 224.9 s | 90.9 s | 638.0 s |
| Per Glass-frame | 0.621 s | 0.251 s | 0.590 s |
| Decode | 15.2 | 12.6 | 29.1 |
| Detect (incl. debug-only) | 108.9 | 63.5 | 331.0 |
| … debug-only diagnostics | 11.1 | 0 | 33.3 |
| Trace write (incl. PNG) | 49.2 | 0 | 148.1 |
| … PNG | 37.9 | 0 | 113.6 |
| Trace finalize | 1.0 | 0 | 3.1 |
| Sequence | 0.7 | 0.7 | 2.5 |
| Bundle (incl. finalize and report frame decoding) | 50.6 | 22.0 | 137.5 |

- **The trace makes FULL 2.5× as long:** 134 s of 225 s.
  - Detect gains 45 s: 11 s of debug-only diagnostics, and about 34 s
    building the debug images and artifacts.
  - The trace write is 49 s, of which PNG encoding is 38 s, about 105 ms per
    record. FULL writes up to 23 images per record, including the full-frame
    overlay.
  - The bundle grows by 29 s. `OutputBundleStore._copy_debug_staging` copies
    the staged trace file by file (`shutil.copy2`, about 0.6 GB here).
- **Without a trace** the run is 91 s for 90 s of video.
  - Detection is 63.5 s of it, 0.175 s per Glass-frame.
  - That is about 2.8× the Mac's sample4 rate. The SPL ellipses are much
    larger than sample4's 104×104 ROI, so this is not read as a CPU
    difference.
- **The rate is linear in frames.** It is about the same per Glass-frame at
  6 fps as at 2 fps.
- **Decode is small** (13–15 s at 2 fps).
- **Not explained:** step-7's SPL#1 took about 2.1 s per Glass-frame, against
  0.62 s here. The SPL#1 conditions were not timed.

## What it decides

- **CAD-1:** outcome C, with the limit above. Denser observation alone does
  not close FULL on SPL#4. It also loses the selected owner through the
  rise, and it changes ownership across the whole run.
  - **For the densification proposal:** a design would need time-based
    frame-count constants first, and a stage diagnosis of why the 6 fps
    path selects no owner.
  - **Not decided:** whether to pursue it. That is the user's choice.
- **Speed (RTP-1):**
  - On Windows the remaining trace cost is PNG encoding (38 s), the staging
    copy into the bundle (29 s) and the debug-image build in detect (about
    45 s).
  - Detection itself is the floor at about 64 s.
  - Decode-ahead (B-3) has little to gain.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PHASE-FILL`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`
- First harmful stage: not claimed. At 6 fps no BASE Oil owner is selected in 20.0–28.0 s (bounded path chooses unknown; then evidence resets), so the top-exit witness never forms; whether association still fails is not established (the admitted-minimum measure does not identify the rising level).
- Existing feature coverage: the step-7 `SPL4_B_ref` session and Recipe snapshot rerun unchanged through the production bundle path with IFO v2 + top-exit v3, at 2 fps FULL, 2 fps NONE and 6 fps FULL; the existing top-exit diagnostics and `OIL_TOP_EXIT_FULL` flag; no detector option added.
- Execution scope: three Windows runs and three comparisons under the user-forwarded step-9 request, relayed by OCR; no Mac run; scored on the Mac against the frozen CAD-1 readings.
- Logic-map impact: NONE — a receipt; no owner or edge changes.
- Failure-registry impact: NONE — no new mechanism; the 6 fps loss of the selected owner is recorded as an observation, not a new failure class.
