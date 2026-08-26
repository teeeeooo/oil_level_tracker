# S11-R18 Windows Causal Closure

**Status:** `FROZEN TRANSFERRED AUDIT — INSTRUMENTED WINDOWS RERUN REQUIRED`

## Scope and provenance boundary

This record freezes the final operator-transferred audit of the R18 bundle
`oil_level_analysis_R18개선_add_artifact_modify_20260825_193624`, run ID
`e3e04d74-5943-4508-b303-408f909e347d`, for the private sample identifier
`windows_sample1_heating_coldstart`. The private bundle is not checked into
this repository, so the tables below are transferred evidence rather than a
locally reproducible audit. No detector rerun or source-exact-head proof is
claimed.

Canonical segment membership follows the reviewed-truth contract: the first
decoded 479.9795 s sample belongs to the canonical 480 s start. All 1,202 rows
were assigned exactly once: Base 601 and Accum 601, with no duplicate,
unassigned, or boundary-excluded rows. Nested selected-candidate, completed
sequence, and CSV publication equality had zero mismatches.

## Closed observations

| Area | Runtime observation | Supported conclusion |
|---|---|---|
| Base lifecycle | all 601 frames were `filled_barrier/INITIAL_FULL_BARRIER`; Oil publication was 0 | R18 fails Base drain recall while correctly suppressing the no-interface prefix/suffix |
| Base release | 74 downward confirmed rows were audited; 62 first failed minimum progress and 12 first failed entrance-relative | the strongest lower track (`000201:0182`, Y876–926) failed entrance-relative at 0.86–0.93 versus 0.40; `sequence_material_ownership_barrier` is a result diagnostic, not the predicate input |
| Accum lifecycle | 31 `FILL_MOTION_OWNER` frames established a fill chain; no partial release was published; 700–780 s Oil publication was 0 | absence of `FILL_ESTABLISHED_INTERFACE` does not mean the internal chain was absent; the EMPTY hard gate is the fail-closed result after no release was selected |
| Accum release | the source call preconditions appear satisfied, but the call and row-level predicate results were not serialized | exact first failure among established-fill distance/reversal, material, and ambiguity remains unknown |
| Foam recall | 672–677 s published 11 Foam rows; 677.5–678.5 s was candidate-ineligible; 679–679.5 s was episode-unconfirmed | exact eligibility and episode predicate failures were not serialized; individual Y accuracy remains `NOT_EVALUATED` |
| Foam precision | ENTRY-SPLASH published seven false Foam rows; POST-FOAM and DRAIN published zero | first harmful owner is episode confirmation/publication, but the exact accepting predicate path was not serialized |

The prior statement “material ownership barrier caused current material veto”
is withdrawn. `sequence_material_ownership_barrier` is computed after lifecycle
resolution in projection. The prior statement “no established Accum fill
chain existed” is also withdrawn: `FILL_MOTION_OWNER` assigns the internal
`established_fill_chain`.

## Named unknowns frozen for one rerun

1. Whether `_partial_fill_drain_release_choice()` was actually evaluated on
   each Accum drain frame.
2. Each Accum candidate's ordered predicate results, especially established
   fill last Y, reversal/distance, current and tracklet material conflict, and
   ambiguity.
3. The exact Foam eligibility gate at 677.5–678.5 s.
4. Track/segment membership and the exact Foam segment/formation predicate at
   679–679.5 s and for the seven ENTRY-SPLASH false publications.

These are diagnostic unknowns, not permission to change thresholds, entrance
bands, Recipe values, or add sample-specific logic. R19 behavior design is
held until one same-video Windows run with the causal trace schema closes or
explicitly preserves them.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`,
  `OIL-PHASE-DRAIN`, `FOAM-CANDIDATE`, `FOAM-EPISODE`,
  `TRACE-PUBLICATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F05`, `S11-F07`, `S11-F08`,
  `S11-F09`, `S11-F10`
- First harmful stage: Base is `OIL-PHASE-DRAIN` release admission; Accum is
  before or inside partial-fill release but the exact predicate is unknown;
  Foam is candidate eligibility or episode confirmation as separated above.
- Logic-map impact: UPDATED — trace publication now exposes causal lifecycle
  and Foam gate diagnostics without changing detector ownership.
- Failure-registry impact: UPDATED — R18 causal conclusions, withdrawals, and
  the bounded rerun requirement replace the earlier audit-pending status.
