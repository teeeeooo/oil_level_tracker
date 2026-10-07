# Report context adoption — 2026-10-07

## Namespace and wording repair

Base: `0333a08ee5b4dbf5c78261c3bd8b39b25be488d7`, clean main. The user authorized
sequential Work Plan implementation, verification, logical commits and push
until a decision needs their judgment. This record covers the first report-only
unit, not detector or field promotion.

The namespace/wording portion of the third-audit prototype is implemented in
the existing report builder. Modern Oil extrema no longer depend on Foam-only
R7 flags. Legacy anchor protection applies to both narrative and landmarks,
including no-anchor legacy inputs. Endpoint comparisons do not imply whole-window
steadiness; single observations do not establish movement. Foam labels describe
observation start/interruption and distinguish state-only evidence from a numeric
front. Episode membership, event timestamps/types and source-event bindings stay
unchanged. No gap cap, graph connectivity or Review/event compatibility change
is included in this unit.

The existing report architecture/validation own the updated contract; the
[S11 design](../../20-architecture/s11-report-context-presentation-design.md)
records its scope and prior failure review.

## Verification

- Before the repair: the extended report-presentation suite reproduced twelve
  failures while its nine existing cases passed.
- After the repair: 31 focused report/graph/capture/application integration cases
  passed, including all twelve new cases; zero failures or skips.
- Four fresh official `AnalysisPipeline` → `OutputBundleStore` runs used the
  existing recipes, fixed windows, 2 FPS and explicit UNKNOWN initial state.
  The saved third-audit baseline is applicable: `a48124c:src` and pre-change
  `0333a08:src` are identical. It was not rerun or presented as fresh evidence.

| Sample | Rows | Oil numbers | Extrema before → after | Captures before → after |
|---|---:|---:|---:|---:|
| Base | 30 | 28 | 2 → 2 | 3 → 3 |
| sample2 | 5 | 4 | 0 → 2 | 1 → 3 |
| sample3 | 151 | 29 | 0 → 2 | 5 → 7 |
| sample4 | 113 | 101 | 0 → 2 | 3 → 5 |

All 299 tracking CSV rows match the baseline in every column except run ID.
Event CSV contents match except run IDs and capture paths; event tuples, truth
comparisons, series values/states/flags/validity, executed recipes and same-frame
provenance summaries match exactly. All twelve input pins and replay source hashes
remain unchanged. These extrema describe stored observations, not newly certified
physical truth.

The [verification receipt](2026-10-07-report-context-verification.json) records
source/helper/test hashes, exact replay commands, comparisons and JUnit identities.
Full logs, results and bundles remain in ignored local
`sample/output/s11-report-wording-adoption-20261007-001`.
The sample3/sample4 generated detail graphs were inspected: recovered extrema and
observation labels are visible; long dashed gaps and crowded early Foam labels
remain existing presentation limitations for the next bounded unit.

No full canonical suite was repeated for this bounded report repair after focused
integration and required four-video checks passed. A0Q, O2 and FIELD FAIL remain
unchanged. Source–report physical context and user understanding are not yet
validated.

## Detector Governance

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: RESULT-PRESENTATION; unrelated Foam flags suppressed Oil extrema, endpoint wording implied continuous steadiness, and non-observation was described as Foam disappearance.
- Logic-map impact: NONE — existing report owner repaired; numeric publication, detector and event owners remain unchanged.
- Failure-registry impact: NONE — existing provenance and no-shortcut guards preserved; no field failure is retired.
