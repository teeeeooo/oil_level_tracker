# S11-R18 Windows Causal Closure

**Status:** `R19_DESIGN_INPUT_READY_WITH_NAMED_UNKNOWNS / field FAIL`

## Scope and provenance boundary

This record freezes the final operator-transferred audit of the R18 bundle
`oil_level_analysis_R18개선_add_artifact_modify_#2_20260826_135338`, run ID
`a0e9b034-4f58-4ad5-85be-294ab435015a`, for the private sample identifier
`windows_sample1_heating_coldstart`. The private bundle is not checked into
this repository, so the tables below are transferred evidence rather than a
locally reproducible audit. The run is not a source-exact-head proof.

Canonical segment membership follows the reviewed-truth contract: the first
decoded 479.9795 s sample belongs to the canonical 480 s start. All 1,202 rows
were assigned exactly once: Base 601 and Accum 601, with no duplicate,
unassigned, or boundary-excluded rows (`unassigned=0`, `duplicates=0`). The
compared same-frame fields (selected-candidate, completed-sequence and CSV
values) covered `1,202/1,202` (`1202/1202`) common rows and had zero mismatches.
Exact sequence/CSV publication counts were Oil `26` and Foam `18`.
Segment/row coverage is not per-frame recall; recall requires a reviewed truth
value for every frame.

## Completed causal-observability rerun

The transferred rerun used bundle
`oil_level_analysis_R18개선_add_artifact_modify_#2_20260826_135338`, run
`a0e9b034-4f58-4ad5-85be-294ab435015a`, for
`windows_sample1_heating_coldstart`. The exact canonical membership was:

| Segment | Rows | Oil | Foam |
|---|---:|---:|---:|
| `WS1-BASE-FULL-PREFIX` | 140 | 0 | 0 |
| `WS1-BASE-DRAIN` | 225 | 0 | 0 |
| `WS1-BASE-RAPID-REFILL` | 3 | 0 | 0 |
| `WS1-BASE-FULL-SUFFIX` | 233 | 0 | 0 |
| `WS1-ACCUM-EMPTY` | 347 | 0 | 0 |
| `WS1-ACCUM-ENTRY-SPLASH` | 37 | 17 | 7 |
| `WS1-ACCUM-FOAM-LAYERED` | 16 | 8 | 11 |
| `WS1-ACCUM-POST-FOAM` | 41 | 1 | 0 |
| `WS1-ACCUM-DRAIN` | 160 | 0 | 0 |
| **Total** | **1,202** | **26** | **18** |

Oil counts by segment are Base `0/0/0/0` and Accum `0/17/8/1/0`;
Foam counts are Base `0/0/0/0` and Accum `0/7/11/0/0`.

The rerun confirms Base rapid-refill Oil presence `0` (`FAIL`) with exact Base
Y `NOT_EVALUATED`. The operational `Y <= 800` cohort has 245 release
evaluation rows and zero passed; release evaluations are not raw proposals or
a funnel. The lower `Y > 800` (including `Y876–926`) entrance rejection is
correct safety behavior, not the actual Oil root cause. The actual-interface
earliest harmful stage is before-or-at `OIL-PHASE-DRAIN` and remains
`NOT_PROVEN`.

For Accum, 700–780 s DRAIN-only produced 264 `release_evaluations` (264 eval
rows) and zero passed evaluations. The retained, non-updated
established-snapshot owner is `000388:0265` (`last_y=219`, `last_frame=398`,
sequence offset); its non-update cause and the actual drain candidate
identity/direction remain unknown. `release_evaluations` are evaluation rows,
not raw proposals and not a sequential funnel. The initial EMPTY pre-entry
hard gate is direct behavior; partial-release was evaluated before the later
fail-closed `allowed=frozenset` result. A `release_evaluated=false` trace means
there are no evaluation rows, not proof that the function was not called.

Foam gates are closed by the rerun: top-level eligibility exists under
`candidate.features`, while nested compact fields are separate diagnostics.
At 677.5–678.5 s candidate eligibility fails `layer_coherent` (and at 678.5 s
also `supported_layer_shape`); at 679–679.5 s the segment first fails
`formation_witness`, whose formation first fails `bounded_stable_front`
because `mean_relative_front=.0411 <= .12`. The bounded predicate uses
`span <= max(3, h * .015)` and `mean_relative_front > .12`, not front rise.
ENTRY-SPLASH false tracks `0020`/`0032` passed `directed_front`, and `0036`
passed `stable_layer`; POST-FOAM and DRAIN have zero confirmed Foam. For
Accum `h=583.2` gives `8.748`, so span 9 fails. The stable Foam maximum-span
calculation is a Foam fact only and resolves `0027`/`0058` in that section.
Deduplicate segment diagnostics by `segment_id`. These gate/segment counts are
observations, not frame-recall proof.

The rerun's same-frame comparison is complete for the compared fields, with
`1,202/1,202` common rows and zero mismatches. No further Windows diagnostic
rerun is needed before R19 design; the remaining boundaries are named below.

## Closed observations

| Area | Runtime observation | Supported conclusion |
|---|---|---|
| Base lifecycle | all 601 frames were `filled_barrier/INITIAL_FULL_BARRIER`; Oil publication was 0 | R18 fails Base drain presence while suppressing the no-interface prefix/suffix; exact Y remains `NOT_EVALUATED` |
| Base release | The initial-ENTRY hard gate is direct initial-empty behavior; the later partial-release fail-closed result is a distinct contract. Rapid-refill Oil presence is `0` (`FAIL`); exact Y is `NOT_EVALUATED`. Operational `Y <= 800` has 245 release evaluation rows and zero passed, while `Y > 800` entrance rejection is correct safety behavior, not the actual Oil root cause. | The earliest harmful stage is before-or-at `OIL-PHASE-DRAIN` and `NOT_PROVEN`; `sequence_material_ownership_barrier` is a result diagnostic, not predicate input. |
| Accum lifecycle | `FILL_MOTION_OWNER` established a fill chain. Retained owner `000388:0265` has `last_y=219`, `last_frame=398`, and a sequence offset; the established snapshot was retained and non-updated during release checks. | Non-updated describes the snapshot contract; it must not be called causally stale. |
| Accum release | 700–780 s DRAIN-only produced 264 eval rows and 0 passed. `release_evaluations` are evaluation rows, not raw proposals and not a sequential funnel; `release_evaluated=false` means no evaluation rows, not proof the function was not called. | Retained snapshot non-update cause and actual drain candidate identity/direction remain unknown; the later fail-closed result is not evidence that no candidate was evaluated. |
| Foam recall | Top-level eligibility is under `candidate.features`; nested compact fields are separate. 677.5–678.5 s eligibility fails `layer_coherent` (plus `supported_layer_shape` at 678.5 s); 679–679.5 s first fails `formation_witness`, then `bounded_stable_front` with `mean_relative_front=.0411 <= .12`. The bounded predicate is `span <= max(3, h * .015)` and `mean_relative_front > .12`, not front rise. | Gate observations are not a frame-recall claim; exact reviewed Y anchors remain unavailable. |
| Foam precision | ENTRY-SPLASH false tracks `0020`/`0032` passed `directed_front`, and `0036` passed `stable_layer`; POST-FOAM and DRAIN had zero confirmed Foam. | The exact accepting predicate path is recorded above; no Foam span fact belongs outside this Foam section. |

The Base initial-ENTRY hard gate is a different contract from the
post-partial-release fail-closed gate. A failure to establish the initial
entry owner cannot be inferred from (or repaired by) the later owner-loss
path. The lower `Y876–926` entrance rejection is correct safety behavior, not
the actual Oil root cause.

The prior statement “material ownership barrier caused current material veto”
is withdrawn. `sequence_material_ownership_barrier` is computed after lifecycle
resolution in projection. The prior statement “no established Accum fill
chain existed” is also withdrawn: `FILL_MOTION_OWNER` assigns the internal
`established_fill_chain`.

## Named unknowns frozen after the corrected rerun

1. Base actual interface first loss.
2. Accum snapshot non-update cause and actual drain candidate identity/direction.
3. Owner-bounded selector abstain predicate.
4. Exact reviewed Y anchors.

These are diagnostic unknowns, not permission to change thresholds, entrance
bands, Recipe values, or add sample-specific logic. No threshold or design
proposals are made in this evidence. They are sufficient for R19 design input;
no further Windows diagnostic rerun is needed before R19 design.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`,
  `OIL-PHASE-DRAIN`, `FOAM-CANDIDATE`, `FOAM-EPISODE`,
  `TRACE-PUBLICATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F05`, `S11-F07`, `S11-F08`,
  `S11-F09`, `S11-F10`
- First harmful stage: Base is `before-or-at OIL-PHASE-DRAIN and NOT_PROVEN`;
  Accum is
  before or inside partial-fill release but the exact predicate is unknown;
  Foam is candidate eligibility or episode confirmation as separated above.
- Logic-map impact: NONE — this transferred diagnostic record does not change
  the current implementation owner map.
- Failure-registry impact: NONE — this record reports the completed rerun and
  does not change the durable mechanism registry.
