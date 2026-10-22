# S11 Mac-only steps handoff — 2026-10-22

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state and
authorization. Everything below is committed and pushed (head `bbfe246`).

Windows is unavailable, so the session followed the user's Mac-only order
(1 legend fix, 2 FOA-1, 3 DSR-1, 4 E3, 5 B, 6 fast-fill FULL and stale owner,
7 one combined Windows request). The user moved step 6's stale-owner half ahead
of E3 and B.

**Changes this session:**
- **Always-on report change (`b49ed07`):** per-sample state-band cells. Detector
  output and CSV are unchanged.
- **Opt-in detector change (`2cb0b52`):** the contested fill-owner gate behind
  default-OFF `fill_owner_contest` / `--oil-fill-owner-contest`
  (`+fill-owner-contest-v1`). The default detector is unchanged.

**Checks:**
- **Full suite:** 3,846 passed, 12 skipped (sample3 quarantine).
- **Managed runs:** all 114 check clean.

## What this session settled

| Step | Outcome | Owner |
|---|---|---|
| 1 Legend fix | Per-sample band cells, frozen `0b5d234`, implemented `b49ed07`; local PASS; Windows confirmation on the next report | [Band cells](2026-10-21-initial-state-report-local.md#per-sample-band-cells--2026-10-22) |
| 2 FOA-1 | sample5/sample7 reproduce `FILL_OWNER_AMBIGUOUS`; sample5 publishes wrong-target Oil; SPL#4's unadmitted fast rise is not reproduced | [FOA-1](../../50-diagnostics/s11/2026-10-22-fill-owner-ambiguity-local.md) |
| 3 DSR-1 | Accum gaps mapped (entry, post-Foam association, drain release); option 1 first | [DSR-1](../../50-diagnostics/s11/2026-10-22-d-scope-review.md) |
| 6 (나) | Desk reading: low owners rise in parallel, so motion validity fails; wrong rows come from an ambiguity survivor. Contested fill-owner gate frozen `8386b45`, implemented `2cb0b52`, local checks PASS (`bbfe246`) | [Design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-contested-fill-owner-gate), [evidence](2026-10-22-fill-owner-contest-local.md) |

**Gate result:**
- sample4, base_sample_1 and sample2 are unchanged.
- sample5 loses exactly the 17 predicted wrong rows. Its 4 remaining wrong rows
  come from a fresh lower-entrance chain (not addressed).
- sample7 loses 20 correct rows, a cost the user accepted before the run.

**User statements recorded this session:**
- sample5 and sample7 start EMPTY and never become full.
- sample7: 0016's published Y is correct. 0016 and 0006/0013 are the front and
  back arcs of one surface seen slightly from above.
- Product videos are mostly shot head-on, like local sample4 (a round sight
  glass).

## Next (the user decides each step)

1. **Step 4, E3:** Accum reconstruction protection design plus synthetic tests.
2. **Step 5, B (LBT-2):** local development on sample4 (its baseline did not
   move).
3. **Step 6 (가):** fast-fill FULL; SPL#4 is its only case.
4. **Step 7, one Windows request** when Windows returns:
   - band cells and E2 on the next report;
   - SPL#4 `temporal_max_jump_px` and a frame review;
   - fill-owner readouts at SPL#4 27.5–34 s and SPL#1 Accum 653–682 s;
   - Accum 680–700 s contested hypotheses and `AMBIGUOUS_BRANCH` ends;
   - Accum 700–780 s DRAIN release evaluations and a human check of the 22 rows;
   - review-012 / S2 for B; SPL#1 after 780 s;
   - **gate comparison:** SPL#4 0–90 s and SPL#1 under ⑩ conditions,
     reference (IFO v2 + top-exit v3) vs + gate. Predicted: SPL#4's 14 rows at
     27.5–34.0 s become UNKNOWN; every changed row listed with reason and owner.

**Open, not scheduled:** the fresh low start (sample5, 4 rows); post-Foam
association and drain release (need Windows readouts first).

## Constraints to preserve

- **Standing user rule:** no detector change, flag change, rerun, Windows
  execution or tuning until the user decides; proceed one step at a time.
  Conversation in Korean.
- **Windows workflow:** private media and bundles stay on Windows. Requests are
  Korean text; results come back by OCR. Identify runs by run ID, version and
  counts.
- **Unchanged states:** review-006 pending; FIELD FAIL / O2 OPEN; the 723/771 s
  protections; sample3 quarantined; top-exit and the gate default OFF.
- **Next free review ID:** review-012.
- **Process:** freeze rule, tests and controls before execution; no tuning or
  rule change after results.

## Reproduce locally

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests
.venv/bin/python scripts/check_detector_governance.py --base-ref HEAD --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
```

The gate's controls reproduce through
`tests.diagnostics.s11_initial_full_comparison --fill-owner-contest-comparison`.
Commands and the scoring script are in managed run
`sample/output/s11-fill-owner-contest-local-20261022-001`.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`.
- First harmful stage: for the stale owner, `OIL-PHASE-FILL` (a `FILL_OWNER_AMBIGUOUS` survivor wins by attrition; gated by the opt-in gate); for Accum, per segment as in DSR-1; for the legend, `RESULT-PRESENTATION` (fixed at `b49ed07`).
- Existing feature coverage: the linked records; six local controls with IFO v2 and top-exit v3; synthetic unit tests. No Windows data was read this session beyond earlier receipts.
- Execution scope: handoff only; no runtime exercised beyond the linked records.
- Logic-map impact: NONE — handoff document; ownership and control flow unchanged.
- Failure-registry impact: NONE — pointers are in the linked records.
