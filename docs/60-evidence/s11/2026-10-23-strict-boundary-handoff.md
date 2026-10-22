# S11 steps 4–5 and strict Oil boundary handoff — 2026-10-23

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state and
authorization. Everything below is committed and pushed (head `f1e3503`).

Windows is still unavailable. Of the Mac-only order (1 legend fix, 2 FOA-1,
3 DSR-1, 4 E3, 5 B, 6 fast-fill FULL and stale owner, 7 one combined Windows
request), steps 1–5 and 6 (나) are done. This session did steps 4 and 5, and
the user then fixed which boundary the Oil output follows inside a Foam layer.

**Changes this session:**
- **Detector change, always on (`55726fd`):** the first-catch position guard
  (L2) in the initial-state continuing-run rule, provenance
  `initial_state_retrospective_v3`. The 24 kept local streams change only
  provenance; no known real output changes.
- **Product and evaluation rule (`56e32d3`):** the strict Oil boundary inside a
  Foam layer, in the product spec, the P0 contract and the Windows reviewed
  truth. No detector code or stored truth file changes.
- **Diagnostics only:** the LBT-2 tool under `tests/diagnostics`; no
  production change.
- **Tooling:** the docs date catalog is complete, and `scripts/check_docs_catalog.py`
  runs in the pre-push hook (`5a20e10`). That change broke one hook test, found
  by this session's full run and fixed in `d82c98a`.

**Checks:**
- **Full suite:** 3,903 passed, 12 skipped (sample3 quarantine) at `f1e3503`.
- **Managed runs:** all 118 check clean; governance and catalog checks pass.

## What this session settled

| Item | Outcome | Owner |
|---|---|---|
| 4 E3 | The user chose L2: FULL needs the first catch in the top band, EMPTY in the bottom band and within one `temporal_max_jump_px` of the effective-mask bottom; otherwise UNRESOLVED. Frozen `875c0f2`, implemented `55726fd`, local PASS | [LCR-1](../../50-diagnostics/s11/2026-10-22-reconstruction-late-catch-review.md), [evidence](2026-10-21-initial-state-report-local.md#first-catch-position-guard-l2--2026-10-22) |
| Docs catalog | 166 missing tracked files added with their own add dates; the rule and the checker are in `docs/README.md` | [Catalog](../../catalog-by-created-date.md), [rule](../../README.md#날짜와-탐색) |
| 5 B, LBT-2 | Outcome P under the frozen net rule N: no new baseline A; the Foam-visible fill guard F removes the false cap at 54.5 s; 800 better against 8 worse (none from F); Foam 12 right against 3 wrong | [LBT-2 result](../../50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md#results-and-decision) |
| 52 s vs 54.5 s | Two boundaries in one scene, not a level change. The sample4 references and the output mix them: the output follows the strict one to 53.5 s and the rough one from 54.5 s | [Answer](../../50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md#user-answer-two-boundaries--2026-10-23) |
| Oil boundary | **Strict:** a bubbly zone between dense Foam and clear Oil is Oil; the Oil target is the bottom of the dense Foam. Rough readings stay but are not Oil references | [Decision](../../50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md#decision--2026-10-23), [P0 contract](../../30-validation/s11-interface-observability-witness-validation.md#oil-reference-boundary-inside-a-foam-layer--2026-10-23) |
| Review-014 | Prepared: one raw x5 zoom of sample4 52.0–56.0 s; waits for the user's reply | [Question](../../50-diagnostics/s11/2026-10-23-review-014-sample4.json) |

**Under the strict rule:**
- **Kept sample4 Oil references:** P0's 38–52 s values (the 38–44 s ones count
  as strict; no rough reading exists there), LBQ-1 and CAF-1's 51–52 s
  rejection.
- **Rough, no longer Oil references:** the official `sample4.oiltruth` Oil
  values, review-013 Q2, and the 2026-10-09 values Y833–838 as wrong Oil.
- **Known error:** both baseline arms publish the rough boundary at 54.5–56 s
  (Y851–852, 18–19 px below Y833). Its first harmful stage is not located.
- **LBT-2's verdict stands.** A read-only recount puts 705 of its 800 better
  units at 40–44 s, 458 of them wrong under either definition.

**User statements recorded this session:**
- E3: L2; the step-7 Accum readout (rows 640–672 s and the Accum geometry).
- LBT-2: F, stop policy N, a pre-run review-013, sample5/sample7 as controls.
- Review-013: a Foam layer is visible above the Oil in all 34 frames of
  39.5–56 s; the dotted surface at 54.5–56 s (now read as the rough boundary).
- "두 판단이 서로 다른 경계를 본 거야": strictly, Foam ends at Y833; roughly,
  at Y857–860.
- "엄격으로 가자".

## Next (the user decides each step)

1. **Review-014 reply:** record it like review-013 (reply JSON with the verbatim
   text, any marked image kept byte for byte, and a source-Y reading per
   frame). 52.0 s should read near Y833; if it does not, ask before using the
   readings. Then add the strict 54.0–56.0 s references to the LBT-2 decision
   and the P0 contract's sample4 list.
2. **Then the user chooses:**
   - the 54 s boundary switch under the strict rule (candidates `S11-F02`, the
     strict row missing, or `S11-F04`, continuation onto the rough row);
   - step 6 (가), fast-fill FULL (SPL#4 is its only case);
   - another step.
3. **Step 7, one Windows request** when Windows returns. The
   [previous list](2026-10-22-mac-only-steps-handoff.md#next-the-user-decides-each-step)
   stands, plus:
   - review-012 (Accum 672–677.5 s) asks for the strict Oil boundary, then a
     separate go for LBT-2's S2;
   - the first-catch guard on the next report, and the Accum readout
     (640–672 s rows and the Accum geometry).

**Open, not scheduled:**
- LBT-2's named limits:
  - 40 s: the lower structure after a withdrawn 39.5 s row;
  - 54.0–56 s: association after a withdrawn 54.0 s row (its Y828–829 lie
    near the strict Y833; re-read after review-014);
  - Foam removals at 41.0/44.5/46.0 s (`S11-F06`);
  - sample2 2.0 s.
- The fresh low start (sample5, 4 rows), post-Foam association and drain
  release.

## Constraints to preserve

- **Standing user rule:** no detector change, flag change, rerun, Windows
  execution or tuning until the user decides; proceed one step at a time.
  Conversation in Korean.
- **Windows workflow:** private media and bundles stay on Windows. Requests are
  Korean text; results come back by OCR. Identify runs by run ID, version and
  counts.
- **Unchanged states:** review-006 pending; FIELD FAIL / O2 OPEN; the 723/771 s
  protections; sample3 quarantined; top-exit and the fill-owner gate default
  OFF.
- **Oil boundary:** strict. A rough reading is kept as recorded, never used as
  an Oil reference.
- **Review IDs:** review-012 is reserved for Windows Accum 672–677.5 s;
  review-014 is pending; the next free ID is review-015.
- **Process:** freeze rule, tests and controls before execution; no tuning or
  rule change after results. Every new `docs/` file enters the date catalog in
  the same change.

## Reproduce locally

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests
.venv/bin/python scripts/check_detector_governance.py --base-ref HEAD --include-worktree
.venv/bin/python scripts/check_docs_catalog.py
.venv/bin/python scripts/experiment_artifacts.py check
```

LBT-2 runs as `.venv/bin/python -m tests.diagnostics.s11_layer_bottom_topology_2
--work <work>` in a managed run; its kept run is
`sample/output/s11-layer-bottom-topology-2-20261022-001`. The review-014
generator and manifest are kept in
`sample/output/s11-review014-sample4-20261023-001`.

## Detector Governance

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`.
- First harmful stage: E3 — `PUBLICATION-PROVENANCE`, a late first catch accepted by the continuing-run rule (guarded by L2); LBT-2 — `OIL-PHASE-FILL`, a fill confirmed under visible Foam (removed by F in the diagnostic); the 54 s boundary switch under the strict rule — not located.
- Existing feature coverage: the linked records; the sample4 SOI population; the descriptive controls base_sample_1, sample2, sample5 and sample7; synthetic unit tests. No Windows data was read this session beyond earlier receipts.
- Execution scope: handoff only; no runtime exercised beyond the linked records.
- Logic-map impact: NONE — handoff document; ownership and control flow unchanged.
- Failure-registry impact: NONE — pointers are in the linked records.
