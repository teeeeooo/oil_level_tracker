# S11 steps 8–11 and speed work handoff — 2026-10-26

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state
and authorization. Everything below is committed and pushed to `main`. The
latest commit is `80646aa`.

**Windows is available (user, 2026-10-26).** Two Windows requests are READY
and not yet answered. The Mac judges each reply against rules frozen before
the run.
1. [Step 10](../../40-operations/s11-current-windows-field-qualification.md#step-10-stage-readout-request):
   a read-only stage readout of the 6 fps bundle.
2. [Step 11](../../40-operations/s11-current-windows-field-qualification.md#step-11-speed-timing-request):
   speed timing and identity, run after step 10.

**No production detector default changed.** FIELD FAIL / O2 OPEN and
review-006 pending are unchanged.

**Product-side changes, all byte-identical in output:**
- the trace-cost cut (B-1);
- the staging rename in the bundle store (가);
- background PNG encoding in the analysis writer factory (다).

The parallel-Glass loop (나) is opt-in and default OFF.

**Checks:**
- Full suite at `bc20338`: 3,967 passed, 12 skipped (the sample3 quarantine).
- Managed runs: 128, all clean.
- Governance and catalog checks pass.

## What this session settled

| Item | Outcome | Owner |
|---|---|---|
| Step 8 (Windows) | F: 0 qualifying fast-rise triplets on SPL#4 BASE and Accum. The two geometric BASE triplets each join three near-stationary rows, so there is no SPL#4 run. L: LBT-2 S2 is closed without a design. S2 fails (Oil removed in ENTRY-SPLASH, 4 rows, and in all of ACCUM-DRAIN, 22 rows, mechanism unknown); S3 fails (678.5/679 s change); S4 holds (review-012 C0 A8 B4 → C8 A0 B4); S5 holds | [Step-8 receipt](2026-10-26-step8-windows-receipt.md) |
| Fast fill, option 4 | **Rejected by the user.** Fast fills are common in practice. No successor witness is chosen. Local densification was proposed, bounded by the source fps (30 fps allows 960 px/s against the 32 px cap, about 7× SPL#4) | [FFF-1 decision](../../50-diagnostics/s11/2026-10-23-fast-fill-full-review.md#user-decision--2026-10-26) |
| CAD-1 (SPL#4 at 6 fps) | No FULL at 6 fps. By the frozen rule the outcome is C, but the admitted-minimum measure (Y323) does not identify the rising level. Observed: no BASE Oil owner is selected anywhere in 20–28 s, and 6 fps changes ownership across the whole run (BASE 0–20.5 s numeric Oil 14 → 2) | [Step-9 receipt](2026-10-26-step9-windows-receipt.md), [CAD-1](../../50-diagnostics/s11/2026-10-26-cadence-diagnostic.md) |
| Run-time profile (RTP-1) | On the Mac the trace is about 60 % of a BASIC/FULL run. The finalize rewrite only copies resolver decisions into the trace; it is not the retrospective correction, which runs in memory in `resolve_completed_window`. Windows (Threadripper 7945WX, SPL#4 2 fps): NONE 90.9 s, FULL 224.9 s. The FULL extra is PNG 38 s, the staging copy 29 s and the debug-image build about 45 s | [RTP-1](../../50-diagnostics/s11/2026-10-26-run-time-profile.md) |
| B-1, trace cost | Implemented. The finalize appends the `sequence` member, and `_json_safe` has fast paths. Byte-identical on the Mac and on Windows (step-9 T-1: 362/362 trace lines). sample4 BASIC 29.1 → 22.5 s | [Write-cost design](../../20-architecture/s11-debug-trace-write-cost-design.md) |
| (가) staging rename | Implemented. The staging is renamed into the bundle and falls back to the copy on another volume. Byte-identical (2,601 files). Mac 7.1 → 6.2 s; the Windows saving is unmeasured | same |
| (나) parallel Glasses | Implemented as an **opt-in, default OFF**. One spawned worker per Glass; the parent consumes the results in the sequential order. Byte-identical. Two-Glass sample4 FULL 54.4 → 31.9 s (Mac). Not enabled in the packaged app: it needs `freeze_support()`, and the bootstrap's lambda reader factory keeps the app sequential | [Parallel-Glass design](../../20-architecture/s11-parallel-glass-detection-design.md) |
| (다) background PNG | Implemented in the analysis factory. Four threads; records are written in order, with at most 8 waiting. Byte-identical. Single-Glass FULL 22.5 → 19.2 s; the two-Glass parallel run is now bound by its workers (the parent waited 12.1 s of 19.9 s) | [Write-cost design](../../20-architecture/s11-debug-trace-write-cost-design.md#background-png-encoding-implemented-2026-10-26-speed-step-다) |

**User statements recorded this session (verbatim where they decide):**
- The step-8 shape: "1번 보고 해당사항 없으면 2,3,4를 안하는거지?", then
  "그렇게 진행하자."
- Option 4 rejected: "빠른 충전도 실무에서 충분히 자주 나오는 케이스라 이걸
  unknown으로 닫아버리면 지금 이 프로젝트를 하는 의미가 많이 상실되지.
  샘플링 속도를 올리는건 좋은 생각이지만, 이번보다 더 빠르게 차오르는
  케이스라면? … 끝이 없어질 것 같아".
- Speed raised: "디텍터 검출 속도를 개선 할 여지가 있나? 지금은 90초짜리
  영상 한번 돌리는데도 시간이 꽤 걸리고있거든?"
- The trace rewrite question: the user asked whether it is the post-detection
  correction. It is not.
- The agreed order: "응 순서에 동의함. 진행하자". The order:
  1. record the decisions;
  2. B-1;
  3. freeze CAD-1;
  4. the step-9 request;
  5. by the results;
  6. revisit the gate and top-exit promotions;
  7. LBT-2 and the open limits;
  8. WP09 → WP10.
- After step 9: "1-(a)로 진행하고. 2는 가,나,다 순으로 하나씩 해보자".

## Next (the user decides each step)

1. **The step-10 reply.** Read it against the
   [stage follow-up](../../50-diagnostics/s11/2026-10-26-cadence-diagnostic.md#stage-follow-up-frozen-2026-10-26-before-its-output).
   - **Rising chain:** one tracklet whose admitted rows fall at least 27.2 px
     over consecutive frames in 20.5–25.5 s.
   - **S-A, a chain exists:** the first Q-2 path stage that no longer holds
     the chain's row names where it is dropped.
     - The allowed set excludes it: phase.
     - The best path chooses unknown or another row: the bounded path.
     - A later stage changes it: that stage.
   - **S-B, no chain:** admission still fails at 6 fps.
   - Compare with the 2 fps Q-3 readout. Then the user decides the fast-fill
     direction. Densification would also need time-based frame-count
     constants.
2. **The step-11 reply.**
   - All three runs (S-1 FULL sequential, P-1 FULL parallel, P-2 NONE
     parallel) must reproduce `SPL4_B_ref`: rows for all three, trace bytes
     for S-1 and P-1.
   - P-1 and P-2 must print `used True`.
   - Timing is reported against T-1 224.9 s and T-2 90.9 s, with the parent
     wait.
   - Then the user decides whether to enable (나) in the product. That needs
     `freeze_support()` and a picklable reader factory in `bootstrap.py`.
3. **Then the agreed order resumes:**
   - revisit the fill-owner gate (HELD) and IFO v2 + top-exit v3 default ON
     (OFF), both tied to SPL#4;
   - the LBT-2 successor (optional) and the open limits, one at a time;
   - WP09 → WP10.

**Notes for reading replies:**
- **OCR slips:** Windows replies come by OCR, and hash characters slip
  (`0`/`8`, `a`/`e`, `d`/`0`, `8f`/`bf`). Every step ran under
  "stop on mismatch", so the slips are read as OCR errors. Identify runs by
  run ID and counts.
- **The step-10 hash for `s11_cadence_field.py`:** the request now lists
  `986bd037…`. A ZIP taken at `c9c22ba` has `2b092561…`, which is also valid.
  The `stages` function is the same in both.
- **Timer limit in parallel mode:** the runner's stage timers measure the
  parent, so detect, debug-only and static read 0 there.

**Open, not scheduled:**
- the LBT-2 drain-removal mechanism (the operations JSON stays on Windows);
- the debug-image build cost in detect (about 45 s on Windows). Reducing it
  would change what is captured;
- detector-internal vectorization (B-4);
- review-006 pending. The next free review ID is review-015.

**Tools added this session (diagnostics only):**
- `tests/diagnostics/s11_fast_rise_readout.py`;
- `tests/diagnostics/s11_layer_bottom_topology_2_field.py`;
- `tests/diagnostics/s11_cadence_field.py`, with `run`, `identity`,
  `cadence` and `stages`; `run` takes `--sampling-fps`, `--debug` and
  `--parallel-glasses`.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PHASE-FILL`, `SEQUENCE-COMPOSITION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F10`
- First harmful stage: per the linked records. Fast fill: SPL#4 at 2 fps stops at `OIL-TRACKLET` association (inferred); at 6 fps no owner is selected through the rise (stage under the step-10 readout).
- Existing feature coverage: per the linked records; no detector option is added this session except the default-OFF parallel-Glass loop, which changes scheduling only.
- Execution scope: a handoff summary of committed records; no new run.
- Logic-map impact: NONE — a handoff; the speed changes keep every node's inputs, outputs and order.
- Failure-registry impact: NONE — no new mechanism or failure.
