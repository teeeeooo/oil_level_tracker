# S11 HPA-1 — history / phase amplification handoff

## Current disposition

**HPA-1 COMPLETE / CLOSED WITHOUT PRODUCTION PROMOTION.** S11 ACTIVE, O2 OPEN,
Windows FIELD FAIL. Default R22 + R22-3/O1 and all experiment flags stay unchanged.
The purpose is readable Oil/Foam movement context, not perfect detection or
universal point-local invariance. [Work Plan](../../00-project/work-plan.md) remains
the only current-state/authorization owner.

Start with the [study and results](../../50-diagnostics/s11/2026-10-17-history-phase-amplification.md)
and [compact summary](../../50-diagnostics/s11/2026-10-17-history-phase-amplification/summary.json).
Prior SOI-1 closeout was dirty at entry; all seven paths were preserved and made
durable in `b795e40`. Its one wording correction was the governance marker
`Failure-registry impact: UPDATED`. No prior experiment, control, source media or
production code was overwritten. HPA data used base `bdcad30f1d343ceb9adaaa04a8e0e8b2272ed4d1`
plus explicitly hashed diagnostic code; a later documentation commit does not
change those source/input pins.

## What is now established

| Round | Execution | Result and disposition |
|---|---|---|
| H1, recurrence scalars | Four exact original replays + six scalar transplants | The primary 42.5 s loss is not caused by its 18 scalar changes. Whole-Oil loss is different: its 584 changes can alter later selection/report metadata. No global irrelevance or usable baseline-donor rule. |
| H2, row-feature factorial | All eight geometry/quality/motion combinations with fresh histories | Internal Y restoration alone removes the long gap; without it all four arms keep the gap. It uses the lost observation's original information, so it is diagnostic only. |
| H3, input-local terminal-veto quarantine | Baseline + all 245 original withdrawals | Four conditions activate, seven frames are quarantined, three conditions change Oil coordinates. More numerics expose an unassessed 52 s selection or new late extrema. No adoption; Foam coupling remains. |

The previously unexplained primary amplification is now localized:
`missing selected member → row median/association branch → changed inherited owner → fill-span material veto → persistent filled barrier`.
The internal filled barrier is **not observed physical FULL**. Tracklet ID
renumbering alone was not used to identify a change; exact same-frame members,
association costs, confirmation witnesses and qualifying fill chains were captured.
The existing reciprocal-swap safety contract is deliberate and was not bypassed.

For the primary loss, ordinary/trial Oil counts are 84/103 and 44–56 s numerical
coverage is 0/19 of 25 samples. Nevertheless, 52 s is Y862 (unassessed) instead of
the existing accepted Y833, and the report minimum moves to 51.5 s. In whole-Oil
losses at 52/52.5 s, 96→99 numerics bring a new +45 px maximum at 54.5 s and +39 px
last value at 56 s. Neither count gain establishes the correct motion story.
All four activated conditions, including the metadata-only change, have paired
ordinary/trial CSVs and graphs retained. No successful-looking case was selected
in isolation.

## Repository implementation

Diagnostic code only:

- `tests/diagnostics/s11_history_phase_amplification.py`: scalar necessity/sufficiency and actual owner-stage capture.
- `tests/diagnostics/s11_history_phase_factorial.py`: complete eight-arm internal-feature factorial and actual publications.
- `tests/diagnostics/s11_terminal_veto_quarantine.py`: reversible, input-local trial; current contradicted frame fails closed, no competing completion gains priority.
- `tests/diagnostics/s11_history_phase_publication.py`: exact replay of every activated policy condition and its control.
- `tests/diagnostics/s11_history_phase_verify.py`: separately implemented saved-output, intervention, source, event and CSV verifier.

Three new unit-test modules cover scalar/group scope, corrupt ledgers/provenance,
clean/contradicted terminal evidence, initial FULL/EMPTY and later clean evidence.
No product detector, Recipe, enabled option, truth packet or GUI behavior was changed.

## Validation receipt

264 stored conditions / 29,832 rows; 26,414 Oil source joins; 6,803 Foam same-frame
memberships; 7,657 event joins; 1,204 scalar edits; 2,486 CSV rows; eight factorial
masks and eight paired publication replays: **zero mismatches**, again after
artifact closeout. There were 278 resolver executions / 31,414 sampled rows when
14 publication replays are included. These are repeated conditions on one saved
sample4 input, not 278 independent videos.

Full `tests/unit`: **2,300 passed**. Focused added tests: **33 passed**. Existing
phase tests under the wrapper: 89 passed, but no new-predicate activations; do not
misstate their scope. No new physical accuracy, independent human report reading
or Windows acceptance was measured.

## Evidence retained locally

All paths below are relative to `/Users/sunjaekim/Developer/oil_level_tracker`.

| Closed managed run | Principal evidence |
|---|---|
| `sample/output/s11-history-phase-20261017-001/evidence` | H1 readout, all four owner-stage captures, comparison, frozen protocol |
| `sample/output/s11-history-phase-factorial-20261017-001/evidence` | H2 complete factorial, actual publications and hash-bound publication index |
| `sample/output/s11-terminal-veto-20261017-001/evidence` | Complete 246-condition population, all paired activations, reports, verification/test receipts, source inventory |

Open `sample/output/s11-terminal-veto-20261017-001/evidence/context-review.html`
on the repo host for the four paired report comparisons and source crops. It is a
diagnostic comparison, not a newly adopted production report. Its 11 image links
were checked after deduplication. A missing logical CSV/PNG should be resolved via
that run's `publication-index.json`; do not regenerate or silently duplicate it.

Three new runs: **56 unique files / 12,012,683 bytes**. All **94** managed runs
check clean; no new run has a scratch directory. `sample/output` remains Git-ignored
and is **not backed up by a source commit/push**. Preserve these local closed
folders and their manifests. The source videos/legacy retained inputs stay at
existing paths; no raw-video copies or new model were created.

## Scope of Mac and Windows evidence

All nine accessible sample videos have a fresh byte/hash inventory. Actual new
completed-window work reuses sample4 raw/Recipe, 0–56 s at 2 Hz / 113 rows. Original
source sprites and 42.5/44/52 s native crops were inspected; this is not new human
truth, camera-outage simulation or nine-video detector rerun. Sample3 stays
quarantined. Water/beer/milk/public-source roles, practical alternatives, unclear
lower interfaces and prior failed feature/assignment families remain constraints.

The [Windows checkpoint](2026-10-16-windows-comparison-checkpoint.md) and all nine
[canonical segments](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
remain authoritative. Keep 004/005 allowances, 721 s false-anchor evidence,
723/771 s protections, review-006 unreviewed and FULL CONDITION FAILED / ⑧ NOT RUN.
No private Windows pixels were replayed, new field run queued, top-edge surrogate
used or margin lowered. No new user review question is pending from HPA-1.

## Reproduce verification

Use the repository `.venv`, not the environment probe's system Python:

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
.venv/bin/python -m tests.diagnostics.s11_history_phase_verify \
  --first sample/output/s11-history-phase-20261017-001/evidence \
  --second sample/output/s11-history-phase-factorial-20261017-001/evidence \
  --third sample/output/s11-terminal-veto-20261017-001/evidence \
  --output /tmp/hpa-recheck-unique-name.json
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/unit
.venv/bin/python scripts/check_detector_governance.py --base-ref bdcad30 --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
```

The verifier output path is exclusive-create: choose a new filename rather than
overwriting a receipt. For a separately justified rerun, create a **new managed
run** with `scripts/experiment_artifacts.py start`. Derive sources/inputs/parameters
and budgets from the old `.artifact-run.json`, preserving source hashes; use the
checked-in diagnostic CLI with an empty new `work` directory. Never write into
closed evidence. Original parent SOI input:
`sample/output/s11-single-observation-20261016-001/evidence`.
H2's parent is H1's closed evidence. Detailed initial protocols are recoverable
exactly from each `protocol-snapshot.json`; the live study now includes results.

## Next bounded decision — not another retry of these probes

The immediate design entry is input-local physical-role/continuity qualification
at row association and its consumption by phase authority. Start at
`_row_hypotheses`, `_ordered_assignment_pairs`, `_reciprocal_exchange_reservations`
and `_fill_confirmation_profile`, using the captured first divergence and the four
H3 contrary cases. Do not promote original-history/median donors, a Y/source
exception, global cost-first, generic anchor privilege or terminal-veto suppression
alone. A candidate must preserve the existing 52 s Oil correspondence and practical
alternatives without promoting the known wrong 40/42/44 s targets or the newly
exposed late upper excursion. Preserve Foam episode context and real FULL/EMPTY
safety; allow harmless local misses rather than adopting exact pointwise invariance.
No threshold/model/crop or new Windows run is justified merely by this handoff.

## Detector Governance

- Logic-map nodes: OIL-CANDIDATE, OIL-AUTHORITY, OIL-TRACKLET, OIL-PHASE-FILL, OIL-PHASE-DRAIN, OIL-SELECTOR, OIL-PROJECTION, FOAM-IDENTITY, FOAM-EPISODE, SEQUENCE-COMPOSITION, CSV-PUBLICATION, RESULT-PRESENTATION.
- Failure-registry entries: S11-F04, S11-F05, S11-F06, S11-F08, S11-F09, S11-F10.
- First harmful stage: primary row aggregation/association branch, followed by inherited confirmation and durable material-phase barrier; not the scalar recurrence change or Y818 backfill alone.
- Existing feature coverage: original pinned raw/Recipe, current-frame selected candidate joins, zero added exclusions/templates, default options OFF; Mac/Windows truth scope unchanged.
- Execution scope: saved sample4 raw completed resolver, scalar and row-feature diagnostic interventions, all 246 quarantine conditions, actual sample/event/presentation/CSV/graphs and independent source joins; no new extraction, private Windows rerun, physical accuracy or human report-only acceptance.
- Logic-map impact: NONE — no production ownership, flow or behavior changed.
- Failure-registry impact: UPDATED — F05/F06 evidence pointers only; no new failure class or accepted policy.
