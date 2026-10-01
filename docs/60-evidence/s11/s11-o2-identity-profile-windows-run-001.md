# S11 O2 identity profile — first Windows result

Source: user-transferred Windows summary at commit `2bce8ea`. Private packets,
labels and output JSON were not read on this checkout. Execution, counts, receipts
and input preservation below are reported, not independently reproduced here.
Current acceptance belongs to [work plan](../../00-project/work-plan.md) and
[witness validation](../../30-validation/s11-interface-observability-witness-validation.md).
The [fixed experiment specification](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md)
and [October audit W0/W1](../../50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md)
provide the decision context.

## Identity and completion

- Code commit reported: `2bce8ea`; label revisions 3 / 14 / 4.
- Scorer hash locally verified: `8cbb501faae75db588b7fe97027244f2bac6040a2e7a576122b73b6d2241f3a5`.
  The reported Windows prefix/suffix agree; a full Windows hash was not supplied.
- Local profile artifact: `776c8639cd2ac39a7ed7c9a5833348c6339a390d95fc1a5830a0967b481f6519`;
  reported prefix/suffix agree with the prior local record.
- Profile spec: `two-region-versus-ramp-excursion-v1`.
- Reference artifact: reported `655689e19d6fa323...67f9cf9`, original fixed-score v1.
- Reported reference inputs/scores/evaluation equality: true.
- Receipt: `s11-o2-identity-profile-v1`, COMPLETE. Output hash prefixes:
  experiment `1e852e0e...`, summary `c2473f9c...`; Windows receipt checks passed.
- Seven inputs preserved before/after; EXPLORATORY_UNCALIBRATED,
  auto_acceptance=false and FIELD FAIL remain unchanged.

## Candidate identity outcomes

Common support intersects availability of all five methods, including the new
four-mean/range inputs. It is not defined by C/A/L availability alone.
Counts below are correct / reversed / tie / unscorable.

| Review | Pairs | Contrast | Alignment | Combined | Without locality | Profile |
|---|---|---|---|---|---|---|
| 001 | 0 | 0/0/0/0 | 0/0/0/0 | 0/0/0/0 | 0/0/0/0 | 0/0/0/0 |
| 002 | 12 | 6/6/0/0 | 0/12/0/0 | 5/7/0/0 | 3/9/0/0 | 2/10/0/0 |
| 003 | 2 | 1/1/0/0 | 2/0/0/0 | 2/0/0/0 | 2/0/0/0 | 1/1/0/0 |

| Review | Profile improved/regressed vs combined | vs without locality |
|---|---|---|
| 002 | 0 / 3 | 0 / 1 |
| 003 | 0 / 1 | 0 / 1 |

The reported prose that profile is worse than *every* method is too broad:
002 alignment has 12 reversed versus profile's 10; 003 contrast ties profile's
aggregate 1/1 outcome. Profile is worse than combined and without-locality in
both reviewed positive/negative cases. No statistical independence or population
accuracy follows from these pairs. Review-001 has no positive pair and no tested
abstention operating point. Path localization was not evaluated in this mode.

## Availability and support changes

| Review | Total candidates | Profile-available candidates (reported) | Preferred scales | Profile-available scales | Ratio |
|---|---|---|---|---|---|
| 001 | 23 | 20 | 354 | 122 | 34.5% |
| 002 | 23 | 22 | 372 | 222 | 59.7% |
| 003 | 27 | 23 | 474 | 326 | 68.8% |

The candidate availability summary was supplied without a precise view key;
retain it as reported, not as proof of identical per-view footprints. Preferred
geometry may be native_path or candidate_center. Scales are correlated and these
ratios are not frame coverage or detection rates. Reported unavailable-profile
reasons include all four bands; far_below counts are 176 / 106 / 49 (reasons can
overlap). The profile reason combines band availability, mean and range inputs;
these counts alone do not isolate the physical cause of a missing measurement.

Profile-supported identity outcomes remain 002=2/10/0/0 and 003=1/1/0/0.
Support transitions: 002 retained_same_order=12, 003=2; newly_scorable,
retained_changed_order and still_unscorable are zero. Review-001 has zero pairs.
This establishes no additional scorable identity pairs or changed pair outcomes;
it does not prove that the two views use identical scales/points or scores.

## Named failures and causal limits

Common-support 002 idx0 (interface) versus idx11 (non_interface):

| Method | idx0 | idx11 | Outcome |
|---|---|---|---|
| Contrast | .2427 | .2606 | reversed |
| Alignment | .7712 | .8034 | reversed |
| Combined | .3284 | .3882 | reversed |
| Without locality | .5542 | .5938 | reversed |
| Profile | -.3291 | -.1101 | reversed |

New combined-correct to profile-reversed pairs against idx11 (-.1101):
idx9=-.5031, idx10=-.4585, idx12=-.4756. The additional review-003 regression's
candidate pair was not supplied; do not invent it. Exact top-rank identities and
per-model residual decompositions were not supplied either.

Higher profile score does not establish a smaller step SSE: it is a normalized
*difference* between best competing-model SSE and step SSE, then aggregated by
scale/point medians. A negative per-scale score favors a competitor, and a negative
candidate aggregate is not evidence of absolute step fit. The report's claim
that idx11 has a smaller step SSE is therefore an unverified explanation.
Structural shape collision remains a known possible limitation, not a diagnosed
cause of these private failures. Pooling, geometry, missingness and shape cues
remain distinct possibilities. No extra report is needed merely to reject this
candidate-level experiment; request decompositions only for a named next test.

## Decision and next boundary

Close audit W0 as executed, without promoting profile to candidate identity or
production. Neither a weight/template sweep nor a switch to max pooling follows.
Preserve the outputs and labels; FIELD FAIL and calibrated O2 gates remain open.

Proceed with W1 semantics: holistic candidate identity, exact local path support
and final scalar eligibility have distinct targets. Partial interface paths can
be valid identity positives, but isolated glare cannot certify a negative
candidate either. A rank failure cannot alone distinguish pooling mismatch from
insufficient identity cues. Define the two-sided expectations and unresolved
cases before selecting one challenger. No immediate new Windows label/video
request, freeze, detector run or reference regeneration is required.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: offline candidate identity ranking worsens against the combined baseline; raw residual/geometry/pooling causes are not established by the transferred aggregate scores.
- Logic-map impact: NONE — records reported offline outcomes without changing production control flow or scorer behavior.
- Failure-registry impact: NONE — constrains promotion and causal interpretation of regression evidence; no new private physical cause or accepted field repair is asserted.
