# S11 texture-authority handoff — 2026-10-20

## Current disposition

S11 ACTIVE / O2 OPEN / Windows FIELD FAIL. Default R22 + R22-3/O1 and every
experiment flag stay unchanged. [Work Plan](../../00-project/work-plan.md) is
the only current-state and authorization owner. Everything below is committed
and pushed; all 98 managed runs check clean.

## What this session settled

| Item | Outcome | Owner |
|---|---|---|
| Evaluation bounds | User-adopted P0 C1–C5: ±5% Glass diameter, isolated single samples, 2 s/5 s gaps, ±2 s events. Also supported-extremum report rule and net baseline/candidate comparison. | [P0 contract](../../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20) |
| Report extrema | Implemented: a landmark needs a same-series neighbor within 1 s and the C1 band. | `report_presentation._extrema_samples` |
| Test debt | Five HEAD failures fixed: R16 trace exclusion, `top_exit_full` allowlist, top-exit moved to `oil_top_exit_full.py`, encoding/stdin policy. Full suite 3,727 pass. | commits `4619409`, `2dea033`, `ba937a0` |
| CAF-1 | Closed. Clean-anchor fill restores the 44–56 s trajectory, but the user confirmed a false 51–52 s Y862. | [CAF-1](../../50-diagnostics/s11/2026-10-20-clean-anchor-fill.md#results-and-decision) |
| AAT-1 | Root cause traced (below). | [AAT-1](../../50-diagnostics/s11/2026-10-20-anchor-authority-trace.md#findings) |
| TPA-1 | Closed. Authority restored at 42 s, but a mature owner above the Foam front (Y805) wins, and three conditions merge Foam episodes. | [TPA-1](../../50-diagnostics/s11/2026-10-20-terminal-partition-support.md#results-and-decision) |

## Mechanism found on sample4

- **Who must corroborate:** after Foam appears, every Oil candidate is
  ordered-lower. R14's `ORDERED_LOWER_INTERFACE` then needs
  `cross_representation_support >= 0.12`.
- **Why the boundary gets none:** `_cross_representation_support` drops peers
  with `material_texture_conflict >= 0.60`. The Oil/Foam boundary sits under
  textured Foam (conflict 0.60–0.75), so its candidates cannot support each
  other and stay continuation-only. Lower vessel structure keeps support and
  anchors: the 42 s Y868 wrong target, HPA-1's fill chain, CAF-1's Y862.
- **What separates the roles:** `material_terminal_partition_support` is 1.00
  on all accepted controls and 0.00 on the 40/42/44 s/Y862 wrong targets. It is
  also 1.00 on the 38 s lower opposed rows, so it is not a complete
  discriminator.
- **What remains after restoring authority (TPA-1):** a new provisional
  tracklet is not admitted; an Oil owner above the current Foam front stays
  selectable; fill-chain ambiguity suppresses output while that owner matures.

These are separate owners. More sample4-only stacking was judged an overfitting
risk.

## Decided next step (user, 2026-10-20)

**Check on Windows whether the same gate blocks the Accum layered-Foam
boundary** (`WS1-ACCUM-FOAM-LAYERED`, about 672–680 s, with
`WS1-ACCUM-ENTRY-SPLASH` / `WS1-ACCUM-POST-FOAM` as context). The R22 reviewed
findings already record a visible Accum boundary whose independent
representation support is blocked by broad texture conflict. Per-candidate
gate evidence, as in AAT-1, has not been extracted.

The answer decides the direction:
- same mechanism → the texture/authority direction has field relevance;
- different mechanism → stop sample4-only work on it.

## First tasks for the next session

1. **Prefer saved-trace extraction, not a rerun.** The
   [721 s investigation](../../40-operations/s11-current-windows-field-qualification.md#721-second-identity-investigation)
   read `phase_identity`, `cross_representation_support`, authority reasons and
   raw features from the existing ④ FULL+ON v2 bundle trace. Confirm from
   source/schema which of these the saved trace holds for each Accum candidate:
   - `material_texture_conflict`, `material_terminal_partition_support`,
     `raw_material_row_support`;
   - Foam material row and seed age, `phase_identity` / failed gates,
     cross-representation support;
   - authority tier/reason, tracklet admission and selection.

   If enough is saved, write a short Korean extraction request in the
   721 s style: bounded frames, small tables, stop after returning. If not,
   package the minimum read-only tool (reuse
   `tests/diagnostics/s11_anchor_authority_trace.py` logic) for the user's
   isolated Windows host, which uses source ZIPs without Git.
2. **Keep the request bounded.** Use a few reviewed Accum frames in the layered
   interval plus one post-Foam frame. Return a gate table only: no full
   JSON/CSV, no rerun of comparisons, no tuning.
3. **On receipt,** compare with AAT-1 and record the result under `50-diagnostics/`.
   Update the work plan only if the direction changes.

## Constraints to preserve

- Private Windows media and images stay on Windows. Distinguish relayed reports
  from local verification.
- Reuse the ④ bundle and review-004/005 allowances. Keep the 721 s false
  anchor, the 723/771 s protections, review-006 unreviewed and FULL CONDITION
  FAILED / ⑧ NOT RUN. Sample3 stays quarantined.
- The [Windows truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
  nine segments are the oracle. Detector output is not truth.
- No detector change, flag or Windows comparison run is implied by the
  extraction.

## Reproduce locally

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests --ignore=tests/diagnostics
.venv/bin/python scripts/check_detector_governance.py --base-ref HEAD --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
```

The AAT-1 trace re-runs with
`.venv/bin/python -m tests.diagnostics.s11_anchor_authority_trace --output <new managed work dir>`.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: on sample4, `OIL-AUTHORITY` cross-representation support excludes texture-conflicted boundary peers (AAT-1); after that, `OIL-TRACKLET` admission and selection (TPA-1). Windows Accum stage is unknown pending extraction.
- Existing feature coverage: saved sample4 P5 NONE raw/Recipe, all options OFF; the Windows ④ FULL+ON v2 bundle is the intended reuse source, and its trace field coverage is unverified.
- Execution scope: handoff only; no runtime exercised beyond the linked studies.
- Logic-map impact: NONE — handoff document; ownership and control flow unchanged.
- Failure-registry impact: NONE — pointers were added by the linked studies.
