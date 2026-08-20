# S11-R13 Secure-Windows Field Result

## Disposition

R13 failed the private Base/Accum effectiveness gate. Final publication
integrity remained sound, but published Oil did not match any of the eight
reviewed truth points. This evidence closes R13 as a failed field baseline and
authorizes the R14 replacement described by the current work plan.

The final-numeric definition is `sequence_resolved_kind == "oil"` with a
finite `sequence_resolved_source_y`. Intermediate `candidate.selected` is not a
publication count.

## Publication integrity

| Glass | records | final numeric Oil | CSV finite Oil | reviewed truth |
|---|---:|---:|---:|---:|
| Base | 601 | 345 | 345 | 0/3 |
| Accum | 601 | 102 | 102 | 0/5 |

For both Glasses, completed-fill Oil, final resolved Oil and CSV finite Oil
counts agree. All 447 numeric rows have exactly one selected same-frame
candidate at the published Y.

## Field failure

Base published long paths across unrelated components. A lower rim/bracket row
at Y929 entered as `DIRECT_INTERFACE`; later Y367--411 rows supplied 90 selected
anchors. At the same first numeric frame, reviewed-Oil-near Y351--352 rows had
the same phase identity and trajectory support but lost through stronger track
opposition and the global path. Final truth was `None`, `None`, and Y908 for
reviewed Y437, Y360 and Y435.

Accum published Foam/residue and structural rows while reviewed Oil remained
near Y288--318. Its longest run moved through Y352, Y498, Y455, Y246 and Y203.
The Y498/Y455 rows were `ORDERED_LOWER_INTERFACE` anchors despite
material-texture conflict of 0.921/1.000. Reviewed-Oil-near rows had materially
lower conflict, but were candidate-only or track-opposed. Final reviewed-point
errors were 49, 193, 167, 62 and 115 px.

## Artifact calibration audit

Artifact calibration was active: Base contained 12 templates and Accum 14,
stored under `glasses[*].geometry.artifact_templates`. Candidate-local matching
rejected 6--12 candidates at inspected frames. The failure was not a missing
template reader.

The audit did reveal an ownership defect: merely having templates also enabled
and enlarged calibrated high-recall and phase-transition proposal generators.
Templates therefore acted as both rejection data and a proposal-policy switch.
R14 separates those responsibilities.

## Full-pipeline counterfactuals

All counterfactual counts below are from complete detector/resolver reruns and
use final publication, not intermediate selection.

| Glass | R13 | texture gate | direct corroboration | distance split prototype | generators off |
|---|---:|---:|---:|---:|---:|
| Base numeric | 345 | 345 | 340 | 43 | 0 |
| Accum numeric | 102 | 63 | 80 | 57 | 91 |

Every scenario remained 0/3 Base and 0/5 Accum truth. The texture gate removed
some high-conflict Accum anchors but substituted other wrong rows. Direct
corroboration reduced Base's lower wrong band but did not recover truth. The
distance split prototype suppressed nearly all Base publication and was not a
component-identity implementation. Disabling the generators removed Base Oil
entirely. Consequently R14 retains a bounded proposal lane, replaces identity
and component ownership, and does not tune the failed prototype.

## Accepted carry-forward facts

- candidate generation recall and publication authority are separate metrics;
- calibration templates reject matching geometry only;
- a high-conflict ordered-lower row cannot anchor from stale material identity;
  the bounded recent direct-Foam composition is evaluated separately;
- recurrence alone cannot hard-demote a low-conflict direct candidate; and
- trajectory/run continuity must be owned by an explicit compatible component.
