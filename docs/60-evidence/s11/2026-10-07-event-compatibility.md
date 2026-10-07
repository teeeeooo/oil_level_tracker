# Legacy Oil event compatibility — 2026-10-07

## Result and boundary

Base `c9a61ce`; Work Plan step 4 is locally verified. The exact Oil flag/anchor
predicate now lives beside the existing sample domain in `domain/results.py`.
Events, report and retrospective reconstruction use it. Modern Oil is no longer
misclassified as legacy Oil merely because unrelated R7 Foam flags coexist.
Actual legacy anchor/continuation protection and event thresholds remain.
The [design](../../20-architecture/s11-oil-compatibility-design.md) and updated
retrospective architecture/validation record this shared responsibility.

Initial reconstruction is deliberately included: the broad predicate also
suppressed modern Oil evidence and selected a different barrier regime. Modern
streams now retain canonical entrance/hard-barrier handling. Confirmed FULL/EMPTY
outcomes can change accordingly; actual legacy Oil keeps its previous behavior.
Observed tracking is never projected back into detector history or CSV.

## Verification

Six new regression cases failed before implementation; 35 existing/control cases
passed. After repair, 117 focused event/judgment/initial-state/report/Review-reader/
application/bundle cases passed, including six shared outcome-assembler cases
covering official analysis, full redetection and interval redetection with both
FULL and EMPTY priors. Source samples are unchanged by derivation.

Four fresh official pipeline→bundle runs passed on the existing fixed windows,
2 FPS and UNKNOWN prior. All 299 tracking rows match the preceding report-adoption
runs except run ID. Series, flags/validity, truth comparisons, recipe and provenance
match. Foam events and sample judgments are unchanged. The persisted Review event
delta exactly matches a before/after computation over the fixed CSV rows:

| Sample | Rows | Added extrema | Other added Oil events | Removed |
|---|---:|---:|---:|---:|
| Base | 30 | 0 | 0 | 0 |
| sample2 | 5 | 2 | 0 | 0 |
| sample3 | 151 | 2 | 0 | 0 |
| sample4 | 113 | 2 | 10 | 0 |

sample4's ten non-extrema additions are crossings at 7, 12, 13, 15, 18, 20.5 and
23 seconds plus stable-recovery spans 18–19.5, 20.5–22 and 23–39. There is no new
40–44-second crossing/recovery event: unavailable intervening rows and the existing
debounce rules still apply. Its restored minimum at 42 seconds/f1260 and maximum
at 44 seconds/f1320 are the stored values that the user identified as incorrect
Oil tracking. Event restoration is therefore compatibility success, not physical
accuracy; these false physical extrema remain the selected A1/A2 investigation.
No provided review establishes the correctness of the earlier crossing events.

The [receipt](2026-10-07-event-compatibility-verification.json) preserves exact
commands, source/input pins, event additions and JUnit hashes. Full logs/bundles
and the fixed-row comparator remain local in
`sample/output/s11-event-compatibility-20261007-001`. All twelve inputs and source
hashes were unchanged across replay. The four UNKNOWN-prior replays do not qualify
FULL/EMPTY field behavior; focused confirmed-prior controls cover that boundary.

No O2, A0Q or Windows gate is promoted. Revert the logical compatibility commit
as a unit to roll back; old bundles preserve their historical event lists.

## Detector Governance

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: PUBLICATION-PROVENANCE — the broad R7 namespace incorrectly applied legacy Oil restrictions/barrier semantics to modern Oil with Foam flags. Wrong physical sample4 Oil observations originate upstream and remain untraced.
- Logic-map impact: NONE — existing event/reconstruction/report owners retain their roles; one compatibility predicate is shared through the existing sample domain.
- Failure-registry impact: NONE — F09/F10 guards remain; no physical detector failure is retired.
