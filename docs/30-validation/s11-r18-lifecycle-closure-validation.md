# S11-R18 Lifecycle Closure Validation

## Gate

R18 is locally acceptable only when the explicit initial-state lifecycle,
partial-fill reversal, bounded Foam formation, checked-video replay,
provenance, performance and full repository gates pass. The frozen R17 Windows
bundle is historical evidence and must not be rerun or treated as R18 output.

## Focused Oil lifecycle assertions

### Confirmed FULL

- The lifecycle begins in `FILLED_BARRIER` with an empty allowed set and no
  numeric Oil.
- A stationary, upward, internal, provisional, material-opposed or ambiguous
  row cannot release the barrier.
- Exactly one confirmed downward top-origin row releases `DRAINING` and becomes
  the sole allowed owner.
- The release appends only the observed drain tracklet ID and preserves exact
  same-frame selection.
- Owner loss stays fail-closed and cannot restore unconstrained `OPEN`.

### Confirmed EMPTY and partial reversal

- The pre-entry EMPTY hard gate is unchanged.
- A stationary lower row and a mid-Glass downward row cannot become the first
  material owner.
- A unique lower-entry upward owner establishes filling exactly as in R17.
- Without an established fill, a downward tracklet cannot start a drain.
- After an established fill owner is lost, exactly one confirmed clean
  downward tracklet whose current row is physically adjacent to the last fill
  row starts `DRAINING`.
- A reversed, distant, provisional, material-opposed or ambiguous release is
  rejected and the frame remains UNKNOWN.
- The new drain ID is appended to the phase owner chain; track observations and
  coordinates remain separate.

All existing filled-barrier release, drain continuation, successor, re-entry,
same-row material-veto and ambiguity tests remain required.

## Focused Foam assertions

- A coherent dynamic front with sufficient upward displacement and directional
  agreement confirms.
- Rapid upward formation across bounded sample gaps remains one episode.
- A constant Y80-style track does not confirm, even with strong dynamic values.
- A downward-moving splash or wall-residue track does not confirm, even when
  score, whiteness, material support, coherence, area and width are strong.
- A stable non-top layer may confirm only with at least three dynamic,
  spatially bounded observations and area or width evolution.
- A two-observation stable layer requires a substantial material footprint in
  both area and width; a narrow two-frame residue remains rejected.
- Area-only and width-only evolution do not confirm a top-row, descending or
  spatially unbounded track.
- A separated Oil layer does not bypass directed formation.
- Foam remains independently publishable when Oil is unknown.
- Final-Oil same-boundary alias rejection and inverted-topology diagnostics
  remain unchanged.
- Every confirmed Foam row has exactly one selected same-frame Foam candidate.

## Historical failure non-regression

The focused suite must retain the lessons of the S11 attempts:

- no unbounded bootstrap or future-supported prefix;
- no lower-reserve, candidate-family or broad-mask anchor authority;
- no universal material-conflict veto;
- no physical-ID merge during phase handoff;
- no Oil dependency for real Foam;
- no initial-EMPTY suppression regression; and
- no graph or report value without a final sequence observation.

## Repository and checked-video gates

Run, in order:

1. focused lifecycle, Foam, selector, resolver and sequence tests;
2. the exact four-video checked replay and its R14 audit functions;
3. same-frame provenance and sequence/CSV integration tests;
4. direct resolver performance checks against the accepted R17-v3 ceiling;
5. the full repository test suite;
6. Python compilation; and
7. `git diff --check` plus a scoped diff audit for deleted superseded paths.

The checked replay must report all 13 truth cases, numeric coverage,
numeric-only and coverage-adjusted MAE, maximum error, sample3 completed-fill
suppression, sample3 late-drain coverage, sample4 reviewed-range matches and
same-frame provenance. Fingerprints are never regenerated automatically.

## Private-Windows acceptance

A later Windows replay must use the canonical
[`windows_sample1_heating_coldstart` truth](windows-sample1-heating-coldstart-reviewed-truth.md)
and enumerate all nine `WS1-*` segments. R18 passes the field gate only if it:

- preserves the 347-row ACCUM EMPTY absence contract;
- suppresses numeric BASE Oil in both FULL/no-interface segments;
- follows the BASE drain and closes safely after the rapid refill;
- creates a real ACCUM drain owner and follows the 700--780 s downward
  interface without adopting wall residue;
- publishes Foam only in the reviewed 672--680 s Foam-present segment, subject
  to separately reviewed point accuracy; and
- preserves exact selected-candidate/sequence/CSV equality for both series.

The existing R17 bundle cannot prove these outcomes. Until a new bundle is
reviewed, the final status is `LOCAL PASS / WINDOWS NOT RUN`, never field PASS.
