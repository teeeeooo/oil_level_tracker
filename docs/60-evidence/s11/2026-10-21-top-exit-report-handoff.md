# S11 top-exit and report handoff — 2026-10-21

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state and
authorization. Everything below is committed and pushed.

**Two kinds of change this session:**
- **Opt-in detector change:** top-exit FULL v3 sits behind the default-OFF
  `top_exit_full` / `--oil-top-exit-full` option (`+top-exit-full-v3`). The
  default detector is unchanged.
- **Always-on downstream change (`139ba87`):**
  - the initial-state continuing-run rule;
  - labelled FULL/EMPTY graph bands;
  - a plain judgment reason.

  These change official report and judgment semantics for any run with a
  confirmed FULL/EMPTY initial state. Detector output and CSV are unchanged.

**Checks:**
- **Full unit suite** (`tests`, excluding `tests/diagnostics`): 3,821 passed,
  12 skipped.
- **Managed runs:** all 106 check clean.

## What this session settled

| Item | Outcome | Owner |
|---|---|---|
| OTR-1 (B review) | Decisions: D1 ellipse = Glass; endpoint inside the existing 27 % band; D2b FULL persistence with per-frame fail-closed; 3a unselected exit row; 6a tracklet-profile anchor; user accepts FULL from about 672 s | [OTR-1](../../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#decision-record--2026-10-21) |
| Top-exit v2, ⑨ | **FAIL.** FULL from 663.0 s, on a refill blank frame that review-004 shows has a visible interface. NOT ADOPTED | [v2 evidence](2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21) |
| Top-exit v3, ⑩ | v2 plus a disappearance confirmed on the next frame. **PASS** on every pre-registered criterion: BASE FULL from 674.0 s; 663.0 s cancelled at 663.5 s; no Accum FULL; pre-closure rows identical; 721 s false anchor now FULL. One Glass on one video; default OFF; not promoted | [v3 evidence](2026-10-21-top-exit-v3-local.md#windows-top-exit-v3-comparison--2026-10-21) |
| ⑩ report receipt | FULL bands at alpha 0.035 with no label. The initial state is blocked by `R17_OBSERVATION_UNAVAILABLE` and by a two-observation direction test (4 px < 7.7 px). BASE `REVIEW_REQUIRED` from 69.2 % coverage; Accum 6.0 % | [Receipt](2026-10-21-top-exit-v3-local.md#report-and-judgment-receipt--2026-10-21) |
| Continuing-run rule (B) and report (A/C) | Frozen at `67f1484`; implemented at `139ba87`. First decisive move (two consecutive boundaries beyond 1 %) toward the prior's direction; no topology gate; source-labelled bands; plain judgment reason | [Local verification](2026-10-21-initial-state-report-local.md) |

## Pending: report confirmation run

The user will forward the
[report confirmation request](../../40-operations/s11-current-windows-field-qualification.md#report-confirmation-run)
to Windows and paste the return into the next session.
- **Run:** one run under ⑩'s conditions, run name
  `22-3_initial_ON_v2_top_exit_v3_report_v2`.
- **Expected values and failure conditions:** written in that section before the
  run.

**What the next session does with the return:**
1. **Check identity:** run ID, run name and the four module hashes. Circled run
   labels may be misread in the user's OCR transcription.
2. **Judge** against the written expectation:
   - **Tracking data:** `tracking_data.csv` equals ⑩'s.
   - **BASE:** `ACCEPTED` v2, interval 479.98–548.006 s, evidence 13151 / 13606 /
     13618, effective coverage ≈ 0.920. Its judgment is decided by the level.
   - **Accum:** `UNRESOLVED` (`AUTHORITATIVE_FOAM`), 6.0 %.
   - **Report:** guidance sentences and the two band labels.
3. **Record** a new receipt section in the
   [local verification](2026-10-21-initial-state-report-local.md) with a verdict.
   Then update:
   - the ops status (no current request);
   - the Work Plan entry;
   - the recall row.

   Commit and push.

## Open choices after that (the user decides)

- **Top-exit v3:** it passed one comparison. Promoting it to default or to an
  integrated candidate needs a defined acceptance scope and more Glass or video
  evidence; use the `windows-qualification` Skill.
- **Paused layered-Foam line (ATG-1 → LBT-1):**
  - the successor LBT-2 uses option (b): a Foam change stops the run only when
    truth or a human review shows it is wrong;
  - LBT-1 outcome G is still open on sample4. Top-exit did not address the 27 %
    fill cap;
  - see the [previous handoff](2026-10-20-full-observable-top-handoff.md#paused-line-layered-foam-resume-after-b).
- **Option C, the 663.0 s `INCOMPATIBLE_BRANCH` exclusion:** a separate
  selection-side repair. It removes one blank frame, not the class.
- **Known limits:**
  - **Top-exit:** a blank of two or more frames inside the band would still
    close.
  - **Reconstruction:** the Accum protection comes from the Foam barrier and the
    continuity bound, not direction.
  - **Graph:** the combined graph has no state bands, and bands from different
    sources share one colour.

## Constraints to preserve

- **Windows workflow:** private media and bundles stay on Windows. Requests are
  Korean text; the user transcribes the results back with OCR. Identify runs by
  run ID, version and counts.
- **Unchanged states:**
  - review-006 is pending and untouched;
  - FIELD FAIL / O2 OPEN;
  - the 723/771 s protections;
  - sample3 is quarantined.
- **Next free review ID:** review-012.
- **Oracle:** the Windows nine-segment truth and the
  [672 s FULL acceptance](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-full-acceptance--2026-10-21).
  Detector output is not truth.
- **Process:** freeze the rule, tests and controls before execution. No tuning
  or rule change after results.

## Reproduce locally

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests --ignore=tests/diagnostics
.venv/bin/python scripts/check_detector_governance.py --base-ref HEAD --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
```

The top-exit local controls reproduce through
`tests.diagnostics.s11_initial_full_comparison --top-exit-comparison`. Their
commands are in managed run `sample/output/s11-top-exit-v3-20261021-001`.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: for top-exit, `OIL-PHASE-FILL` closure on a blank frame in ⑨ (fixed in v3); for the report, the downstream retrospective owner and `RESULT-PRESENTATION` (fixed at `139ba87`, Windows confirmation pending).
- Existing feature coverage: the ④ FULL+ON v2 Windows bundle with ⑨/⑩ comparisons and read-only extractions; four local controls; synthetic unit tests. The report changes are exercised only locally.
- Execution scope: handoff only; no runtime exercised beyond the linked records.
- Logic-map impact: NONE — handoff document; ownership and control flow unchanged.
- Failure-registry impact: NONE — pointers are in the linked records.
