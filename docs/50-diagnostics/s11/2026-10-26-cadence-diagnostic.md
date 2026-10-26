# CAD-1 — SPL#4 cadence diagnostic (6 fps) and Windows timing

**Status: FROZEN 2026-10-26, before any 6 fps output on SPL#4 exists. The run
waits in the
[step-9 request](../../40-operations/s11-current-windows-field-qualification.md#step-9-combined-request).**
- **Why:** this is step 3 of the order the user agreed ("응 순서에 동의함.
  진행하자").
- **Proposal it serves:**
  [local densification](2026-10-23-fast-fill-full-review.md#user-decision--2026-10-26),
  made after the user rejected accepting UNKNOWN on fast fills.
- **It also carries** the Windows timing breakdown that
  [RTP-1](2026-10-26-run-time-profile.md) needs.
- **Not a design:** no detector, Recipe, truth or default changes. Only the
  session's sampling rate and debug level differ between runs.

## Question

1. **Cadence:** with denser observation alone, is the fast rise on SPL#4 BASE
   admitted, and does FULL close inside the user's window? Is FULL then
   released at the drain?
2. **Timing:** where does a Windows run spend its time?

## Why 6 fps

- **Per-step move:** the rise is inferred at about 70 px per 0.5 s. At 6 fps
  that is about 23 px per step, inside the 32 px association cap
  (`temporal_max_jump_px`).
- **Frame alignment:** 30 fps / 6 = 5 source frames per step, an exact
  frame. Every 2 fps sample (every 15 frames) is also a 6 fps sample.
- **Constants that shorten in time:** the frame-count constants are three
  times shorter at 6 fps.
  - the 6-frame confirmation window lasts 1 s;
  - 2 lost frames last 0.33 s;
  - top-exit's next-frame confirmation comes after 0.17 s.

  These changes are part of what the run shows. They are not corrected here.

## Runs

All runs repeat the step-7 `SPL4_B_ref` session (0–90 s, IFO v2 + top-exit
v3, fill-owner gate OFF, compressor start 10.0 s) through
`tests/diagnostics/s11_cadence_field.py run`.

| Run | Rate | Debug | Purpose |
|---|---|---|---|
| T-1 | 2 fps | FULL | identity with `SPL4_B_ref` (rows and trace bytes); FULL timing |
| T-2 | 2 fps | NONE | timing without a trace; row identity |
| C-1 | 6 fps | FULL | the cadence trial |

- **T-1 checks B-1 on Windows.** `SPL4_B_ref` was written before B-1. Its
  trace must equal T-1's line for line once the run ID is normalized.
- **Each run prints** its wall time, the time per Glass-frame and the stage
  totals: decode, static artifacts, detect (including the debug-only
  diagnostics), trace write (including PNG), trace finalize, sequence and
  bundle.

**Local check, PASS** (managed run
`sample/output/s11-cadence-field-check-20261026-001`, sample4 0–56 s, FULL
debug, IFO v2 + top-exit v3, the Glass renamed BASE):
- **A same-rate rerun reproduces its source:** 0 changed rows. All 113 trace
  lines and the index are equal once the run ID is normalized.
- **A NONE rerun:** 0 changed rows; no trace to compare.
- **A 6 fps rerun runs end to end:** 337 rows. The cadence comparison prints
  C1–C5, the stage readout and the shared-grid counts. sample4 never becomes
  FULL, so C1–C3 are false there as expected.
- **Timing lines** print for every run. On the Mac the rate per Glass-frame
  is the same at 6 fps as at 2 fps (0.264 vs 0.267 s).
- **Nesting:** `bundle` includes the report's source-frame decoding, which
  `decode` also counts.
- **Reported only:** sample4's own rows are cadence-sensitive. On the shared
  2 fps grid, 35 of 41 rows change in 0–20.5 s, and numeric Oil in 27–56 s
  falls from 50 to 25. A densification design would have to account for this
  inside a densified span.

## Readings for C-1, fixed before the run

The windows are the
[SPL#4 entry conditions](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22),
frozen 2026-10-22 from the user's timeline. No new truth is added. FULL means
`FULL_NO_INTERFACE` or `FULL_WITH_FOAM`. Both Glasses start EMPTY, so any
FULL is the top-exit route.

| Reading | Definition | Holds when |
|---|---|---|
| C1 | the first BASE FULL row | it lies in 22.0–27.0 s (so none is earlier) |
| C2 | from that row through 61.0 s | every row is FULL or UNKNOWN with no numeric Oil |
| C3 | episode end: the first later row that is neither FULL nor UNKNOWN-without-Oil | it lies in 61.0–65.0 s |
| C4 | BASE 65.0–90.0 s | no FULL row |
| C5 | Accum 0–90 s | no FULL row |

**Stage readout, for the outcome split:** the trial's BASE rows in 20–28 s,
each with:
- its selected Oil candidate: Y, tracklet, lifecycle, admitted;
- its top-exit reason;
- the smallest Y of any admitted Oil candidate in the window, against the
  27 % band end (`OilObservationResolverConfig.entrance_band_ratio`, computed
  from the Recipe ellipse; Y437.95 on SPL#4).

**Reported, not scored:**
- On the shared 2 fps grid, per Glass and phase (0–20.5, 20.5–27, 27–61,
  61–65 and 65–90 s): rows, numeric Oil in both arms and changed rows. This
  shows what the shorter frame-count constants change.
- The timing of the three runs.

## Outcomes

| Outcome | Condition | Meaning |
|---|---|---|
| **A** | C1–C5 hold | Denser observation alone closes and releases FULL on SPL#4. A densification design may be proposed; it is the user's decision and must answer the frame-count constants |
| **B** | C1 holds; any of C2–C5 fails | FULL arrives, with the listed failures. A design would have to answer each one |
| **C** | C1 fails; an admitted BASE Oil candidate reaches the band (admitted min Y ≤ band end) | Association no longer blocks; the barrier is at top-exit or phase. Densification alone is not enough; the top-exit reasons locate the stage |
| **D** | C1 fails; no admitted candidate reaches the band | Association still blocks at 6 fps. Densification alone does not fix SPL#4; the cause search reopens |

For every outcome:
- **Unchanged:** no tuning and no new rate. FIELD FAIL / O2 OPEN stays.
  Top-exit, the gate and the fast-rise association stay default OFF.
- **Identity first:** T-1's identity must hold before C-1 is read. If T-1
  differs, the differences are listed and C-1 is read against T-1 instead.

**Expected, recorded before the run (inference, not a prediction class):**
- **The likely outcome is A or C.** FFF-1's cause check showed the cap is the
  mechanism on local fills, in both directions.
- **The risk is C.** At 2 fps top-exit reported `TOP_EXIT_NOT_PROVEN` with
  `independent_anchor` false. SPL#4's rows are rarely anchor-eligible: 7 of
  40 in the readout.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`
- First harmful stage: unchanged from FFF-1 — `OIL-TRACKLET` association (confirmed locally, inferred on SPL#4); this diagnostic tests whether denser observation removes it.
- Existing feature coverage: the step-7 `SPL4_B_ref` session and Recipe snapshot unchanged (IFO v2 + top-exit v3, gate OFF, compressor start 10.0 s), the existing session `sampling_fps` and debug level, the production bundle path, the existing `OIL_TOP_EXIT_FULL` flag and top-exit diagnostics, and the frozen SPL#4 windows; no detector option is added.
- Execution scope: the field runner `s11_cadence_field.py` with unit tests and one closed local managed run (sample4); the three Windows runs and two comparisons wait in the step-9 request.
- Logic-map impact: NONE — a diagnostic runner under tests/diagnostics; no production owner or edge changes.
- Failure-registry impact: NONE — a diagnostic with no runtime mechanism; its outcomes map to existing entries (`S11-F02` admission, `S11-F04` identity risk avoided by real observations).
