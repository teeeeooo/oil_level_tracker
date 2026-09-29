# S11 O2 fixed-score Windows run 001

Evidence source: user-supplied Windows execution summary received 2026-09-29.
Private packets, labels and output files were not available on this checkout;
counts and input/output preservation below are reported, not independently replayed.
Current gate: [work plan](../../00-project/work-plan.md).
Method: [fixed-score contract](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md).
Acceptance: [witness validation](../../30-validation/s11-interface-observability-witness-validation.md).

## Execution identity and completion

- Spec: `two-sided-localized-edge-ranking-v1`.
- Artifact SHA-256: `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9`.
- Independently recomputed artifact at repository commit `29ec2f92bd48909e4857fc7cc9654be1b6a2e081` matches exactly. This confirms the fingerprinted code/spec, not the entire Windows checkout or private inputs.
- Reported environment: Python 3.14.3 / Windows 11.
- Current v2 labels: review-001 revision 3; review-002 revision 14; review-003 revision 4. The third uses `labels.json`; the first two use `labels-v2.json`.
- Reported completion receipt: COMPLETE, output hashes verified; six input files unchanged by before/after byte hash.
- Output hash prefixes only supplied: experiment JSON `66454721...`, summary `c5583d1a...`; full output hashes not independently verified here.
- EXPLORATORY_UNCALIBRATED; auto_acceptance=false; FIELD FAIL unchanged.

## Reported per-task outcomes

Each cell is correct / reversed / tie / unscorable. Methods use common scale/point support.

| Review / task | Pairs / common | Contrast | Alignment | Combined |
|---|---|---|---|---|
| 002 identity | 12 / 12 | 6/6/0/0 | 0/12/0/0 | 5/7/0/0 |
| 002 interface native location, all X | 40 / 30 | 13/17/0/10 | 24/6/0/10 | 16/14/0/10 |
| 002 interface native location, same X | 8 / 7 | 6/1/0/1 | 7/0/0/1 | 5/2/0/1 |
| 002 native identity-negative control, same X | 9 / 7 | 5/2/0/2 | 4/3/0/2 | 5/2/0/2 |
| 003 identity | 2 / 2 | 1/1/0/0 | 2/0/0/0 | 2/0/0/0 |
| 003 native identity-negative control, same X | 5 / 5 | 4/1/0/0 | 5/0/0/0 | 5/0/0/0 |

Review-001 contains 23 non_interface identities and no positive identity target;
identity pairs=0 for all methods. Ranked negatives are not emitted positive decisions.
No abstention threshold or all-negative rejection performance was tested.

| Review / task | Combined vs contrast improved / regressed | Combined vs alignment improved / regressed |
|---|---|---|
| 002 identity | 0 / 1 | 5 / 0 |
| 002 native location, all X | 5 / 2 | 4 / 12 |
| 002 native location, same X | 0 / 1 | 0 / 2 |
| 002 native identity-negative control | 0 / 0 | 3 / 2 |
| 003 identity | 1 / 0 | 0 / 0 |
| 003 native identity-negative control | 1 / 0 | 0 / 0 |

Do not use the reported all-task improvement totals as a success metric: same-X
location pairs are a subset of all-X pairs, and different tasks reuse candidates
and observations. These are neither disjoint trials nor independent samples.

## Named failures and interpretation limits

1. BASE idx0 interface versus idx11 non_interface is reversed for all methods;
   the report also names idx0/20 and idx16/11,20. Exact component scores and support
   are not supplied. Candidate-center and native geometry can differ; inspect
   the actual preferred geometry and common points before assigning a cause.
2. BASE idx8 near at Y397 versus idx10 off at Y378, X=[130,236], is correct for
   both baselines and reversed for combined. This is a concrete regression on
   the same-X task. The combined locality term and scale aggregation are causal
   hypotheses to inspect, not an established explanation from this summary.
3. Combined's reported top candidates idx1/15 in review-002 are unreviewed.
   Their correctness is unknown; do not count them as false positives or claim
   an incorrect winner merely because reviewed interfaces rank below them.

Review-002 has 15 unreviewed identities; review-003 has 24. The reported
review-002 `partial=15` means 15 candidates have some but not all preferred
geometry **points** with common usable evidence. It does not mean merely that
some scales are missing. Scale-level availability is separately recorded.
Ten unscorable all-X location pairs do not imply ten distinct missing points;
identify the unique points and missing fields in the stored output.

The combined hypothesis has mixed results and does not support promotion over
both baselines. Accum success against its one reviewed negative does not repair
BASE identity failures or establish generalization. Identity and location need
separate assessment; no production integration, threshold selection or field PASS
follows. All labels remain regression, and their existing human judgments stand.

## Next bounded investigation

Use the saved experiment JSON only, without new labels, detector runs or changed
scores. Windows should automatically extract two controls: idx8/idx10 at exact
X=[130,236] for localization, and candidate idx0/idx11 for identity. For each,
retain exact basis/X/Y, stored C/A/L/combined scores, scale widths, common support,
and the actual medians. Verify the stored formula/aggregation on these rows.
Separate scale-level reversal from reversal introduced by median aggregation;
do not infer locality alone caused the regression from median baseline ranks.
Also count unique unscorable points and their unavailable/missing/null fields.
Return a compact generated summary, with the input JSON hash unchanged. No new
source or output-file export is required. This evidence determines whether the
local-context term or candidate aggregation needs the next experiment; it does
not justify selecting a new threshold from these regression labels.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: offline score ordering demonstrably reverses reviewed pairs; the component cause is unknown until stored per-scale evidence and aggregation are inspected. No production decision was emitted.
- Logic-map impact: NONE — records an offline Windows score experiment; detector and publication behavior are unchanged.
- Failure-registry impact: NONE — preserves correlated-evidence and identity/location boundaries; no new production failure mechanism is established.
