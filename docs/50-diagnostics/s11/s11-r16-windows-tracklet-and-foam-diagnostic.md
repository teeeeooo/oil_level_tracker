# S11-R16 Windows Tracklet and Foam Diagnostic

## Disposition

The R16 private-Windows replay failed detector accuracy while its completed-
window provenance contract passed. This diagnostic narrows the code-supported
failure boundaries before a successor design. It deliberately rejects the
preliminary extraction mistakes and several root-cause claims that the source
does not prove.

The authoritative run counts and identity are recorded in the
[R16 Windows field result](../../60-evidence/s11/s11-r16-secure-windows-field-result.md).

## Corrected observability boundary

Top-level debug `positions`, `state` and `candidates` describe the current-frame
detection. Nested `sequence` describes completed-window resolution and is the
object projected to CSV. Completed-window Oil and Foam both have exact selected
same-frame candidate and CSV equality in the audited bundle.

For an unconfirmed physical tracklet, `_finalize_track()` records only the
terminal failure reason. It does not copy a `_WindowEvidence` witness into the
observation. Consequently trace values such as `net_progress=0`, `direction=0`,
`motion_support=0` and `confirmation_support=0` are default observability
values, not the measured maxima that caused rejection. They cannot prove that
the configured initial state was absent or that registered motion was never
computed.

## Base Oil failure boundary

The Base failure has two independently observed stages.

1. Proposal recall is incomplete. The reviewed row has no ±25 px candidate at
   540 s and no ±80 px candidate at 674 s.
2. When a reviewed-near row exists, as at 634 s, its physical tracklet does not
   form a confirmation profile.

All 454 tracklets are provisional. The terminal reason distribution proves:

- 349 tracks never contained the required configured entrance-band origin;
- 102 tracks never reached minimum net progress in any bounded confirmation
  window; and
- three passed earlier gates but lacked sufficient motion or anchor evidence.

`_track_failure_reason()` tests these categories sequentially, so
`ENTRANCE_ORIGIN_MISSING` and `INSUFFICIENT_NET_PROGRESS` are not a circular
dependency on one track. The evidence supports **partial proposal recall plus
bounded confirmation-profile failure**. It does not support a universal
`direction=0 + motion=0` root cause or cumulative-distance confirmation, which
could incorrectly admit oscillating reflections.

## Accum Oil failure boundary

The confirmed initial-EMPTY entrance rule successfully removes R14's four
stationary pre-entry false runs. Removing or globally widening that rule would
discard a demonstrated improvement.

The admitted lower-entry track establishes that R16 can form a real upward
physical trajectory. Accuracy later fails through more than one stage:

- at 684 s the reviewed row is absent from the admitted top-K set;
- at 689 s no reviewed-near proposal is present; and
- after those upstream losses, the selector can only choose a surviving
  publishable tracklet or UNKNOWN.

The repeated `tracklet_material_conflict=0.913` value on the continuing
tracklet is its confirmation-witness aggregate copied forward. It is not a
current-frame conflict measurement and does not prove that a live universal
material veto was ignored. The material lifecycle already applies both
track-history and complete current-row material vetoes to drain release,
continuation, handoff and drain re-entry. A universal selector-level conflict
veto would repeat earlier S11 failures where real lower Oil overlapped broad
Foam/material evidence.

After 702 s, newly observed mid-glass rows cannot independently satisfy the
initial-EMPTY lower entrance origin. The prior fill chain survives only its
bounded loss/handoff window and no longer supplies an owner. The structural
gap is therefore **safe mid-glass reacquisition of a previously established
filling interface after physical-owner loss**, not proof that the initial state
should be mutated globally. Any successor design must keep the initial-EMPTY
guard and require explicit prior-owner continuity, physical compatibility and
ambiguity bounds.

## Foam failure boundary

The R16 episode owner computes material support from score, texture, whiteness,
area, width, fill, bottom connectivity and glare opposition, then confirms a
group from mean material/coherence/static evidence and registered dynamic-frame
coverage. The reviewed false Base and Accum groups satisfy this contract and
are therefore selected and projected consistently.

The bundle proves:

- learned static opposition did not match the false regions;
- registered dynamic evidence is also high on some false regions; and
- the current episode aggregate does not separate 52 reviewed real Foam rows
  from 50 reviewed false rows (Base 5 plus Accum 45).

It does not prove that the static map was absent, or whether false motion came
from exposure, camera motion, Oil movement or another physical source. It also
does not establish that no multivariate use of existing evidence can separate
the cohorts merely because every individual feature range overlaps.

Foam publication without a resolved Oil row is an intentional independent
owner contract. Making Foam conditional on Oil would repeat the R12--R15 alias
failure and remove real Foam when Oil is missing. The correction boundary is
episode-level material/temporal discrimination. Reviewed trajectories suggest
front-Y evolution, area evolution and spatial persistence as evidence to
evaluate, not yet-authorized implementation rules.

## Lessons retained from R11--R16

A successor design must not repeat these failed approaches:

- unbounded or future-supported bootstrap of a long path;
- generic authority for a lower reserve or stationary entrance structure;
- source-family priority or candidate-only Oil/Foam alias authority;
- broad material-conflict vetoes that suppress real lower Oil;
- component/path continuity that transfers physical identity implicitly;
- fixed coordinate, timestamp, Glass/video identity or Artifact exceptions;
- Foam publication made dependent on resolved Oil; or
- global threshold reduction that trades initial-EMPTY/Artifact safety for
  recall.

The preserved contracts are initial-EMPTY suppression, real lower-entry
admission, exact same-frame candidate ownership, sequence-to-CSV equality,
independent real Foam recall, calibrated Artifact rejection and fail-closed
ambiguity.

## Next design boundary

The next design must address three bounded responsibilities without merging
them into one owner:

1. Base proposal/physical confirmation for a slowly evolving visible
   interface;
2. Accum truth-row proposal/admission plus bounded filling-owner reacquisition
   after loss; and
3. Foam episode material/trajectory discrimination while preserving Oil-
   independent publication.

No implementation choice is authorized by this diagnostic. Exact algorithms,
new evidence fields and validation fixtures belong to the successor design and
validation contract.
