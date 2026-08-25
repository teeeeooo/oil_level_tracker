# S11-R17 Windows Phase and Episode Diagnostic

## Disposition

The R17 private-Windows replay failed detector effectiveness while its
completed-window provenance contract passed. This diagnostic freezes the
code-supported causal boundary for the successor design and explicitly
withdraws the extraction and interpretation errors found during review.

The authoritative run identity, exact counts and segment results are in the
[R17 Windows field result](../../60-evidence/s11/s11-r17-secure-windows-field-result.md).
Physical truth is owned by the
[`windows_sample1_heating_coldstart` review](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).

## Corrected gate contract

Top-level trace positions and candidates are current-frame proposals. Nested
`sequence` contains completed-window resolution and is the source projected to
CSV. Absence of a selected Oil candidate is therefore
`NO_SELECTED_OIL`, not proof that no Oil proposal existed.

Initial EMPTY has two distinct layers of behavior. Its state node is a soft
proposal, while material-phase ownership is a hard gate: when
`empty_entrance_motion_enabled=True` and there is no dynamic fill owner,
`allowed=frozenset()` causes `_constrain_layer()` to remove every Oil node.
`FILL_EVIDENCE_ACCUMULATING` describes chain state; it does not make the layer
unconstrained. This hard gate remains active for Accum with or without
provisional fill chains until a dynamic owner exists.

Initial FULL has no equivalent empty allowed-set gate. In the no-dynamic-owner
branch, Base uses `allowed=None`. This is a code-proven structural asymmetry,
but the bundle does not serialize `oil_no_interface_full_likelihood`, so the
first Base 480 s runtime failure remains split between state proposal and
ownership.

## Base phase failure boundary

Base remains OPEN for all 601 rows. It never enters FILLING, FILLED_BARRIER or
DRAINING, and its fill-confirmation profile is `none` throughout.

### Full prefix

The 480--550 s reviewed segment has no visible interface but publishes 45 Oil
rows. The bundle proves that an Oil path wins while the lifecycle is OPEN and
the Base no-owner layer is unconstrained. It cannot prove whether a competing
FULL state node was absent or merely lost because the required full-likelihood
metric is not serialized. The earliest failure is therefore:

`state/no-interface proposal OR material-phase ownership — NOT_PROVEN`.

### Real drain

The initial-FULL real drain at 550--662 s never receives a DRAINING owner.
DRAINING is reachable only after a generated FILLED_BARRIER and confirmed
drain release; initial FULL does not establish that predecessor lifecycle.
Normal interface and lower/glare tracklets consequently remain in an OPEN
selection space. The observed 201 numeric rows across 11 runs include source-Y
363--908 and fail the reviewed identity contract.

This is a material-phase ownership boundary. It does not authorize a global
selector penalty or threshold change.

### Rapid refill and full suffix

The 662--663.6 s refill remains OPEN with
`FILL_EVIDENCE_ACCUMULATING`, `fill_confirmation_profile=none` and no filled
barrier. The exact failed fill-chain subcondition is not serialized and is not
invented from final publication row counts.

Because no barrier closes the material lifecycle, the later full/no-interface
suffix remains OPEN and publishes 91 false Oil rows. The code and trace prove
the missing phase closure; they do not prove which unrecorded fill-chain
measurement failed first.

## Accum phase failure boundary

The 480--653 s initial EMPTY segment passes with zero Oil and zero Foam. This is
direct evidence that the hard initial-EMPTY gate must be preserved.

Accum later enters FILLING for 41 rows but never reaches FILLED_BARRIER or
DRAINING. Near 695.49--698.99 s it has provisional fill evidence without a
dynamic owner; near 699.49--704.50 s it has no chain. Both cases use
`allowed=frozenset()` because the fixed Accum policy keeps
`empty_entrance_motion_enabled=True`.

The real post-700 s descending interface is therefore phase-blocked whenever
no dynamic fill owner exists, while the lifecycle has no partial-fill reversal
path into DRAINING. The first demonstrated failure for the 160-row drain is
material-phase ownership, not a proven drain-reentry distance failure.
`_drain_phase_reentry()` is not implicated because DRAINING never exists in the
bundle.

The apparent 733/754 s Oil detections are also corrected: final Oil is absent.
Those intervals contain unselected current-frame Oil proposals and seven final
false-Foam rows. They are not evidence of unconstrained Accum Oil selection.

## Layered Oil/Foam boundary

`ObservationSequenceResolver.resolve()` runs Oil resolution once and then
passes its detections to `FoamEpisodeResolver`. The code has no second Oil pass
after final Foam confirmation. Oil alias opposition is bounded and soft, and
Foam material identity applies only inside its bounded match distance.

These are structural facts. In the 672--680 s reviewed Foam interval:

- final Oil exists in eight rows and final Foam in 13;
- four simultaneous rows satisfy the required ordering `foam_y < oil_y`;
- selected Oil alias penalty and Foam material identity are zero in the
  reviewed 675--677 s rows; and
- individual coordinate accuracy is not evaluated because no frame-exact
  source-Y anchors exist.

Therefore Oil-before-Foam ordering and absence of a correction pass are a
**strong causal inference**, not a proven counterfactual cause. The report does
not call any candidate Y the physical lower interface and does not claim that
a selected ordered-lower Oil row is necessarily the Foam top.

## Foam episode failure boundary

Every final Foam row has exact same-frame selected-candidate and CSV equality.
The failure is upstream episode discrimination, not projection.

- Entry splash: 16 final Foam rows occur before reviewed Foam onset.
- Foam-present interval: 13 rows establish segment-level recall; individual Y
  accuracy remains not evaluated.
- Post-Foam: eight Y80 rows are false Foam.
- Drain: 62 rows at Y80--525 are false Foam over seven runs.

The nested selected-Foam set, episode-confirmed flag set and CSV-valid set are
identical at 99 frames. False current-frame candidates become harmful when
episode association/confirmation accepts them; high-recall candidate creation
alone is not a publication failure.

All eligible Foam evidence is coherent under the actual
`foam_layer_coherent` path. Static opposition is zero because exact, tolerant
and reciprocal static evidence contribute no opposition. This proves that the
current static evidence did not reject the false regions, not that the static
logic did not execute or that a static map was absent.

## Root-cause boundary

| Problem | First demonstrated harmful stage | Evidence strength |
|---|---|---|
| Base full-prefix Oil | state proposal or phase ownership | named unknown between the two |
| Base drain identity competition | material-phase ownership | code and runtime confirmed |
| Base refill closure/full suffix | material-phase ownership | missing barrier confirmed; failed subcondition unknown |
| Accum entry false Foam | episode association/confirmation | final false episode confirmed |
| Accum layered identity | selector/resolver ordering risk | strong inference, not counterfactual proof |
| Accum post-Foam false Foam | episode association/confirmation | final false episode confirmed |
| Accum real drain miss | material-phase ownership | hard gate plus absent drain phase confirmed |
| Accum drain false Foam | episode association/confirmation | final false episode confirmed |

## Retained non-regression contracts

A successor design must preserve the evidence-backed behavior, without
reintroducing failed S11 approaches:

- Accum initial-EMPTY suppression;
- real lower-entry admission;
- exact selected-candidate, sequence and CSV equality;
- independent publication of real Foam when Oil is unresolved;
- calibrated Artifact rejection and fail-closed ambiguity;
- separation of state proposal, physical observation, material phase and final
  publication responsibilities; and
- no private-video coordinates/timestamps, global threshold relaxation or
  Recipe retuning as production logic.

This diagnostic authorizes no implementation. Algorithms, ownership changes
and their validation fixtures belong to the successor design.
