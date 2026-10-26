# Steps 10 and 11 Windows receipt — 2026-10-26

**Status: RECEIVED.**
- **Step 10 (stage readout):** S-A by the letter of the frozen rule, dropped
  at phase (`OIL-PHASE-FILL`), read with a named limit.
- **Step 11 (speed):** identity PASS on all three runs. The timing is
  recorded.

Both replies came back through the user as verbatim stdout, relayed by OCR.
They are read against rules frozen before the runs:
- the [stage follow-up](../../50-diagnostics/s11/2026-10-26-cadence-diagnostic.md#stage-follow-up-frozen-2026-10-26-before-its-output)
  for step 10;
- the [step-11 request](../../40-operations/s11-current-windows-field-qualification.md#step-11-speed-timing-request)
  for step 11.

Nothing is tuned and no default changes. FIELD FAIL / O2 OPEN and review-006
pending are unchanged.

## Source identity

**Every SHA-256 value matches the Mac's `main`** (`7bf386b`) apart from OCR
slips:
- **Exact:**
  - `s11_layer_bottom_topology_2_field.py`;
  - `parallel_glass_detection.py`, `detection_run.py`;
  - `output_bundle_store.py`.
- **`0`/`8` and `a`/`e` slips:**
  - `s11_cadence_field.py` (`986bd037…`, the hash the step-10 request
    lists);
  - `analysis_pipeline.py`, `jsonl_debug_trace_writer.py`,
    `opencv_phase_detector.py`.
- **`s11_fast_rise_readout.py`:** the relayed value has 65 characters, with
  one `0` inserted, so it cannot be a real hash.

Both requests said to stop on any mismatch, and every step ran. The slips
are therefore read as OCR errors. That is an inference.

**Version:**
- Step-11 runs print
  `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1+initial-full-observation-v2+top-exit-full-v3`.
- The fast-rise readout prints the Oil pipeline version
  `r22-oil-ownership-evidence-replacement-v1+…`, as in step 8.

## Step 10 — stage readout

**Bundles:**
- C-1: `SPL4_C1_6fps_full`, run `e104a258-a010-4173-9566-8f33cec96e45`.
- `SPL4_B_ref`: run `005e0d58-024e-4c38-b5eb-becfc552e0cb`.

### Q-1, fast-rise readout (C-1 BASE 20.5–25.5 s)

**Counts:** 31 frames, 787 Oil candidates, 116 rows, of which:
- 21 anchor, 79 physical, 40 motion, 14 witnessed;
- 7 upward steps beyond the cap;
- 4 constant-velocity triplets, 0 qualifying.

**The 4 triplets each join three tracklets.** Each one stitches a
near-stationary row near Y800 to rows near Y750 and Y703–708. This is the
step-8 pattern again.

**Rising-chain reading** (admitted rows of one tracklet falling at least
27.2 px over consecutive frames). Every admitted run in the window, listed
by hand from the relayed rows:

| Tracklet | Consecutive admitted rows | Fall | Chain |
|---|---|---:|---|
| `000113:0057` | 20.5–21.33 s: Y379, 356, 325, 324, 323, 323 | 56 px | **yes** |
| `000085:0039` | 20.5–21.0 s: Y801, 801, 800, 802 | 0 | no |
| `000085:0039` | 22.5–23.83 s: Y785, 753, 756, 758, 757, 769, 765, 760.5, 764 | 32 px (one step, 22.5 → 22.67 s) | **yes** |
| `000117:0062` | 20.5–20.83 s: Y420, 398, 398.25 | 22 px | no |
| `000119:0066` | 22.5–22.67 s and 23.17–23.67 s: Y703.5, 703; Y714, 742, 742, 772 | moves down | no |
| `000142:0077` | 24.5–25.5 s: Y717 … 705.5 … 716.5 | 11.5 px | no |
| `000147:0084` | 24.5 s: Y758 | one row | no |

Two tracklets meet the rule, so the reading is **S-A**.

### Q-2, stages (C-1 BASE 20.0–28.0 s, 49 rows)

**Every row is UNKNOWN_REVIEW with no numeric Oil.** The best path and every
later stage are `unknown` in all 49 rows.

| Time s | Phase / reason | Owner chain | Allowed |
|---|---|---|---|
| 20.0–21.5 | open / `FILL_EVIDENCE_ACCUMULATING` | `0062` | hard gate, none |
| 21.67–23.5 | open / `INITIAL_EMPTY_ENTRY_PENDING` | – | hard gate, none |
| 23.67 | draining / `PARTIAL_FILL_DRAIN_RELEASE_CONFIRMED` | `0027;0035;0066` | owner-bounded, `0066` only |
| 23.83–24.33 | draining / `DRAIN_OWNER_LOST` | same | hard gate, none |
| 24.5–28.0 | draining / `DRAIN_OWNER_TERMINATED` | same | hard gate, none |

**S-A, the first stage that drops each chain:**
- `0057` (20.5–21.33 s): the allowed set is empty. The stage is phase.
- `0039` (22.5–23.83 s): the allowed set is empty, except at 23.67 s, where
  it holds only `0066`. The stage is phase.

**So both chains are dropped at phase (`OIL-PHASE-FILL`),** before the
bounded path. Step 9 placed the barrier at `OIL-SELECTOR` or `OIL-PHASE-FILL`.
This readout narrows it to `OIL-PHASE-FILL`. An empty allowed set leaves the
bounded path only `unknown`, which is the top-exit reason step 9 recorded
(`CURRENT_INTERFACE_OR_STATE_RESET`).

### Q-3, stages (`SPL4_B_ref` BASE 20.0–28.0 s, 17 rows, 2 fps)

| Time s | Phase / reason | Allowed | Output |
|---|---|---|---|
| 20.0–21.5 | filling / `FILL_MOTION_OWNER` | `0025:0018` | Y801–802 (21.5 s unknown) |
| 22.0 | filling / `FILL_MOTION_OWNER` | `0042:0035` | Y756 |
| 22.5–27.0 | filling / `FILL_OWNER_AMBIGUOUS` | hard gate, none | unknown |
| 27.5–28.0 | filling / `FILL_MOTION_OWNER` | `0025:0018` | Y721, Y704 |

At 2 fps the phase is filling, but its owners are the near-stationary rows
from step 8. The span 22.5–27.0 s is hard-gated by owner ambiguity.

### The named limit

The frozen chain rule counts any tracklet that falls far enough. It does not
show that the tracklet is the rising level. Neither chain is shown to be.
- **`0057` contradicts the frozen timeline (inference).**
  - It starts at Y379, inside the top band (band end Y437.95).
  - It is already at Y379 at 20.5 s, but the SPL#4 timeline puts BASE FULL
    in 22–27 s.
  - It then stays at Y323–331. This is the height step 9 named as a
    near-stationary row.
- **`0039` does not follow the expected rise (inference).**
  - It makes one 32 px step, then holds at Y753–769 for 1.2 s.
  - CAD-1 inferred about 23 px per 6 fps step, sustained.

**What is established** does not depend on what the chains are:
- At 6 fps, `OIL-PHASE-FILL` blocks 48 of the 49 rows outright. In the
  remaining row (23.67 s) it allows only `0066`. That tracklet is moving
  down the Glass (Y703 → Y772), and the phase reads it as a drain owner.
- The phase never enters filling in 20–28 s. It goes from open (fill
  evidence accumulating, then initial empty-entry pending) to a confirmed
  partial-fill drain during a fill.
- **At both rates the rise is hard-gated at phase,** with different reasons.
  - 2 fps: `FILL_OWNER_AMBIGUOUS` between stationary owners.
  - 6 fps: no fill phase, then a false drain.
- **Unknown:** why the 6 fps phase starts 20 s in open rather than filling.
  The readout starts at 20.0 s. The shorter frame-count constants are a
  candidate cause; that is an inference, not tested.

### What step 10 decides

- **Densification alone is not a path to FULL on SPL#4.** At 6 fps the phase
  stage adds a false drain inside the fill. It also changes ownership across
  the whole run (step 9) and costs three times the run time.
- **Admission is not the only barrier.** At 2 fps the rising level is not
  admitted (FFF-1, the association cap). Even an admitted rise would still
  meet phase-level owner handling during a fast fill, at either rate.
- **The fast-fill direction goes back to the user.** No design is frozen
  here.
- **User decision (2026-10-26): "빠른 충전은 너의 의견에 동의".**
  - Densification as a standalone fix is not pursued.
  - Fast-rise phase-owner handling joins the fill-owner gate revisit, the
    next step of the agreed order. It is reviewed at 2 fps and covers the
    admission failure (FFF-1) as well.

## Step 11 — speed timing and identity

**Runs** (SPL#4 0–90 s, the step-7 session, 2 fps):

| Run | Run ID | Debug / loop | Wall s | Per Glass-frame s | Parent waited s |
|---|---|---|---:|---:|---:|
| T-1 (step 9) | `b6222009-…` | FULL / sequential | 224.9 | 0.621 | – |
| **S-1** `SPL4_S1_2fps_full_seq` | `927202b5-cad9-41ef-b092-2cfea30785fb` | FULL / sequential | **160.13** | 0.442 | – |
| **P-1** `SPL4_P1_2fps_full_par` | `35209826-8097-4c9a-ae51-36679b875061` | FULL / parallel | **110.31** | 0.305 | 65.65 |
| T-2 (step 9) | `75816269-…` | NONE / sequential | 90.9 | 0.251 | – |
| **P-2** `SPL4_P2_2fps_none_par` | `68b8c6bd-66e5-4340-9d65-c0bc50fe724a` | NONE / parallel | **79.46** | 0.220 | 54.04 |

**Identity: PASS on every pre-registered item.**
- **Rows:** 362/362 for S-1, P-1 and P-2, with 0 unmatched and 0 changed.
- **Trace:** S-1 and P-1 match 362/362 lines, with no first difference, 0
  trailing bytes and an equal index.
- **Parallel path:** P-1 and P-2 print `used True`.

**Stage totals:**

| Stage s | T-1 | S-1 | P-1 | T-2 | P-2 |
|---|---:|---:|---:|---:|---:|
| Decode | 15.2 | 15.14 | 10.35 | 12.6 | 9.68 |
| Detect (incl. debug-only) | 108.9 | 111.11 | 0 † | 63.5 | 0 † |
| Trace write (parent) | 49.2 | 12.91 | 14.04 | 0 | 0 |
| PNG | 37.9 | 82.7 ‡ | 89.24 ‡ | 0 | 0 |
| Trace finalize | 1.0 | 1.16 | 1.05 | 0 | 0 |
| Sequence | 0.7 | 1.02 | 0.78 | 0.7 | 0.83 |
| Bundle | 50.6 | 27.79 | 27.4 | 22.0 | 23.71 |

- † **Parallel mode:** detection runs in the workers, and the parent's
  timers read 0 (the limit already recorded).
- ‡ **A new timer limit:** with background PNG (다), the PNG timer adds up
  the time of four encoding threads. It is not wall time and no longer nests
  inside the trace write. The parent's own trace-write time is the wall
  figure.

**Reading (timing is reported, not scored):**
- **(가) + (다), S-1 against T-1: −64.8 s (−29 %).**
  - The parent's trace write falls from 49.2 to 12.9 s.
  - The bundle falls from 50.6 to 27.8 s. NONE's bundle is 22.0 s, so the
    staging step is down from about 29 s to about 5 s.
  - Detect is unchanged (108.9 → 111.1 s).
- **(나) with FULL, P-1 against S-1: −49.8 s (−31 %).** Against T-1 it is
  −114.6 s (−51 %).
  - The parent waited 65.7 s, 60 % of the wall time.
  - So the workers are the critical path, as on the Mac.
- **(나) with NONE, P-2 against T-2: −11.4 s (−13 %).**
  - The parent waited 54.0 s. Sequential detection of both Glasses took
    63.5 s in T-2.
  - **Not separable from this data:**
    - the Glasses may differ in cost;
    - each worker may run slower in parallel, with both processes' OpenCV
      thread pools on the same cores;
    - worker start-up may add time.

    Per-worker time is not measured.
- **What remains in NONE:** detection about 54 s, and the bundle 23.7 s.
  About 9.7 s of the bundle is the report's source-frame decoding: P-2's
  parent decode, which only the report does in parallel mode.

### What step 11 decides

- **(가), (나) and (다) keep the output byte-identical on Windows,** in the
  rows and in the trace.
- **The production output scope (user, 2026-10-26).** The packaged product
  will not include FULL debug or the ordinary debug trace. Those exist for
  detector debugging during development. The product's goal is a working
  detector plus the minimum output the report needs. The product case is
  therefore the NONE run: −13 % with (나).
- **User decision (2026-10-26): (나) stays a development aid**, default OFF
  and not enabled in the product ("동의함"). It is revisited at production
  packaging, after measuring why the NONE gain is small (per-worker time,
  OpenCV thread count). The bundle's 22–24 s without a trace, about 10 s of
  it report frame decoding, is the other production-side item.
- **What the decision weighed:** whether to enable (나) in the product.
  - Gains: −31 % with FULL and −13 % with NONE, on two Glasses.
  - Enabling it needs `multiprocessing.freeze_support()` in the packaged
    entry and a picklable reader factory in `bootstrap.py`. It then needs a
    packaged-app check on Windows.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F10`
- First harmful stage: at 6 fps, `OIL-PHASE-FILL` (observed: an empty allowed set in 48 of 49 BASE rows in 20–28 s and a partial-fill drain confirmed during the fill); at 2 fps, `OIL-TRACKLET` association (FFF-1, inferred on SPL#4), then `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` through 22.5–27.0 s. Whether either 6 fps chain is the rising level is not established.
- Existing feature coverage: the step-7 `SPL4_B_ref` session and Recipe snapshot (IFO v2 + top-exit v3, gate OFF, compressor start 10.0 s) through the production bundle path; the step-9 C-1 bundle read without a rerun; the existing fast-rise readout and `stages` subcommand; the opt-in parallel-Glass loop, the staging rename and background PNG at their committed sources; no detector option added.
- Execution scope: step 10, three read-only readouts of two existing bundles; step 11, three Windows runs and three identity comparisons under the user-forwarded requests, relayed by OCR; no Mac run; scored on the Mac against the frozen readings.
- Logic-map impact: NONE — a receipt; no owner or edge changes.
- Failure-registry impact: NONE — the 6 fps phase readings are observations under existing entries (`S11-F04` owner identity, `S11-F05` material-phase ownership, `S11-F08` the drain owner lost and terminated); no new mechanism.
