# S11 O2 locality ablation — first Windows result

Source: user-supplied summary for commit `6bb0206`, received after the locality
ablation handoff. Private JSON was not available on this checkout; execution,
counts and file preservation are user-reported. Current acceptance is owned by
[work plan](../../00-project/work-plan.md) and [witness validation](../../30-validation/s11-interface-observability-witness-validation.md).
Method: [fixed-score experiment / ablation](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md).
Reference: [first three-method run](s11-o2-fixed-score-windows-run-001.md).

## Identity and completion

- Reported commit: `6bb0206`.
- Locally recomputed full ablation artifact: `e4be7939fc608a68647604f68e2d5a6a6eaf6408052d3df08a530bb1d314ba28`.
  The supplied prefix/suffix agree; a full Windows artifact hash was not supplied.
- Reference artifact reported as `655689e19d6fa323...67f9cf9`, consistent with the earlier run.
- Reported reference.inputs_scores_evaluation_equal=true; COMPLETE receipt with schema `s11-o2-locality-ablation-v1`.
- Reported output hash prefixes: experiment `ebcad14a55db2c15...`, summary `17f392b29ba663d4...`; receipt checks passed locally on Windows.
- Seven input hashes preserved (three labels, three packets, one reference).
- EXPLORATORY_UNCALIBRATED, auto_acceptance=false, FIELD FAIL unchanged.

## Common-support outcomes

Without-locality (WL) keeps the cube-root exponent and both median stages.
This view fixes all scales/points to the original three-method support.

| Review / task | Improved vs combined | Regressed vs combined | Pair inventory / scorable |
|---|---|---|---|
| 002 native interface location, same X | 2 | 0 | 8 / 7 |
| 002 native interface location, all X | 3 | 4 | 40 / 30 |
| 002 native identity-negative control, same X | 0 | 2 | 9 / 7 |
| 002 candidate identity | 0 | 2 | 12 / 12 |
| 003 candidate identity | 0 | 0 | 2 / 2 |
| 003 native identity-negative control, same X | 0 | 0 | 5 / 5 |

Review-001 has no positive identity target and zero pairs. Review-003 is valid
identity/control evidence even though its outcomes did not change. It is not an
invalid data case. These tasks overlap and their gain/loss counts must not be
pooled. The user's `same` complement includes unscorable pairs; it is not a count
of unchanged, correctly evaluated comparisons.

Combining the reported transitions with the reference counts gives the following
**derived**, not directly inspected, WL counts (correct/reversed/tie/unscorable):
002 identity=3/9/0/0; all-X location=15/15/0/10; same-X location=7/0/0/1;
same-X negative control=3/4/0/2. No independent-frame accuracy is implied.

## C/A-supported view

This view adds evidence where C/A are available without requiring far-band L.

| Review-002 task | Newly scorable | Still unscorable | Retained same order | Retained changed order |
|---|---|---|---|---|
| candidate identity | 0 | 0 | 11 | 1 |
| native interface location, all X | 10 | 0 | 29 | 1 |
| native interface location, same X | 1 | 0 | 7 | 0 |
| native identity-negative control, same X | 0 | 2 | 5 | 2 |

The newly usable off point idx8 X=[449,555], Y405 creates ten all-X comparisons:
three correct and seven reversed. Its one same-X comparison against idx9 Y417 is
reversed. Availability gain is not evidence of accurate localization.
Idx11 X=[343,449], Y922 still lacks C/A evidence and leaves two negative controls
unscorable. Reported retained-order changes all turn correct into reversed:
identity idx9/idx11; location idx9 Y417/idx10 Y378; controls idx8 Y397/idx11 Y901
and idx9 Y406/idx11 Y925. These are support/median changes within WL, not the
common-support effect of removing L.

## Named controls and limits on causal prose

- BASE same-X idx8 near Y397 versus idx10 off Y378: combined .448 < .460;
  WL .644 > .581 on both views. The known reversal is corrected locally.
- BASE identity idx0 versus idx11: common-support combined .328 < .388 and
  WL .554 < .594; C/A-supported WL .554 < .650. Identity ordering still fails.
- Reported new common-support identity failures include idx10/idx11 and
  idx12/idx11; negative controls include idx9 Y382/idx11 Y901 and
  idx12 Y381/idx11 Y901. Locality had helped these particular pair orderings.
- The narrative says idx0 points were added to idx11's median. Source inspection
  contradicts this: ablation_scores aggregates only each candidate's own points
  and scales. Support expansion within idx11 can change its median; there is no
  cross-candidate pooling. Exact added widths/points were not supplied, so no
  more specific provenance is inferred.
- A point's WL score is median((C_s*A_s)^(1/3)), not generally
  (median(C_s)*median(A_s))^(1/3). The reported explanatory C/A medians must not be
  substituted for the actual per-scale computation.
- The four all-X regression descriptions are not complete unique geometry keys
  (one idx9 description conflates three X positions). Preserve aggregate counts
  as reported; do not fabricate exact pair provenance from that prose.

## Decision / next engineering boundary

Do not promote either scalar combination. Locality removal repairs two observed
same-X location orders but degrades candidate identity and negative controls;
expanded support also admits mostly reversed comparisons for the newly usable
point. This is not a universal result for all imagery. Locality can help some
pairs and harm others; these observations do not establish an additive weighting
rule or justify tuning a weight/threshold on the regression cases.

The fixed-score and locality ablation investigations can close at this scope.
Next engineering work should specify candidate identity evidence separately from
path localization, using the existing implementation/measurement definitions to
identify what would distinguish a real interface from strong structural edges.
Contrast/alignment strength and the current locality ratio alone have not met
that purpose. This does not prove the captured features or raw image lack useful
information. A new combination requires a stated mechanism and two-sided controls,
not another weight search on the same pairs. No additional Windows reporting,
labeling, video exploration, split change or detector rerun is required merely to
accept this experiment result. Exact support details are needed only if a later
mechanism depends on them. Operating-point and field acceptance remain open.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: offline scoring fails reviewed identity and some location orders despite a targeted same-X improvement; no production decision is emitted. Partial support and pooled task counts must not be promoted to detector accuracy.
- Logic-map impact: NONE — records a reported offline ablation and leaves runtime ownership unchanged.
- Failure-registry impact: NONE — constrains conclusions from regression evidence; no new production mechanism or successful field repair is established.
