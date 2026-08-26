# S11-R19 Bounded Drain-Release Chain Architecture

**Status:** `DESIGN APPROVED — IMPLEMENTATION PENDING`

## Authority and scope

R19 is a narrow Oil lifecycle correction based on the frozen R18 causal
Windows rerun. It changes only drain admission in
`OilMaterialPhaseLifecycleOwner`. Candidate generation, authority, physical
tracklet construction, fixed-lag selection, projection, Foam eligibility and
Foam episode confirmation remain unchanged.

The field evidence closes what R18 did and did not prove:

- Base remained behind `INITIAL_FULL_BARRIER` for all 601 sampled rows and
  published no Oil in the reviewed drain;
- the lower `Y > 800` cohort was correctly rejected by the existing entrance
  gate, while the operational `Y <= 800` cohort contained 245 release
  evaluation rows and no release;
- Accum retained an established-fill snapshot throughout the reviewed drain,
  evaluated 264 release rows and selected none; and
- a modal failed predicate is not the identity of the reviewed interface, and
  release-evaluation rows are neither raw proposals nor a sequential funnel.

R19 therefore does not relax `drain_entrance_ratio`, `maximum_jump_px`,
material conflict, tracklet confirmation or selector thresholds. It adds one
bounded phase-evidence route for the case where no single current tracklet
contains enough release motion but a unique, physically continuous sequence
of independently confirmed rows does.

Foam is intentionally outside R19. The R18 rerun already identifies its
current gates (`layer_coherent` and `bounded_stable_front`), but it does not
provide a safe generic discriminator that separates the seven ENTRY-SPLASH
false publications from every reviewed Foam observation. Combining that
separate change with Oil lifecycle recovery would make the field result
causally ambiguous.

## Preserved direct-release path

The existing R18 paths remain first and authoritative:

1. initial FULL direct release requires one row to pass the complete
   `_drain_release_evaluation()` contract;
2. established partial-fill direct release requires one row to pass the
   complete `_partial_fill_drain_release_evaluation()` contract; and
3. more than one direct qualifying ID remains ambiguous and fails closed.

The recovery chain is evaluated only when the matching direct path has zero
qualifying rows and is not ambiguous. A direct release is never replaced,
rescored or delayed by recovery evidence.

## Release-phase evidence chain

The chain is material-phase evidence, not a physical tracklet. It records an
ordered owner-ID history while leaving every `OilCandidateRef`, tracklet ID,
observation and coordinate unchanged.

Each active chain stores constant-size causal state:

- release stage (`initial_full` or `partial_fill`);
- seed anchor Y and current row Y;
- current owner and the ordered tuple of distinct owner IDs;
- first, last and last-forward-progress frame offsets;
- observation and transition counts;
- nonnegative and negative source-Y transition counts; and
- net source-Y progress from the seed.

No past coordinate is published, copied into a successor or injected into the
selector. The tuple of owner IDs is phase provenance only.

### Common row admission

Every seed and successor row must independently satisfy all of these checks:

- bounded tracklet admission with a non-`NONE` confirmation profile;
- compatible physical identity;
- anchor authority on the current row;
- no current material veto;
- tracklet and current material conflict below the existing material limit;
  and
- a real same-frame Oil candidate reference.

Tracklet direction, tracklet net progress and tracklet directional agreement
are deliberately not reused as chain motion. Those values describe one
bounded tracklet and are the exact fragmentation boundary R19 addresses.
Chain direction and progress are recomputed solely from the ordered same-frame
row coordinates admitted above.

### Initial-FULL seed

An initial-FULL chain may seed only while the phase is `FILLED_BARRIER`, the
direct release has no qualifying ID, and the row's existing
`entrance_relative` value passes `drain_entrance_ratio`.

This preserves the R18 rejection of the lower `Y > 800` structure. A row that
missed the entrance band cannot become a recovery seed merely because it later
moves downward.

### Partial-fill seed

A partial-fill chain may seed only after an established fill exists, no
dynamic fill owner exists, direct partial release has no qualifying ID, and
the row:

- is no higher than the existing reversal tolerance permits; and
- lies within one existing `maximum_jump_px` of the retained established-fill
  Y.

The retained fill observation is an anchor for admission only. It is not
published and it is not counted as a new current-frame candidate.

### Unique continuation and handoff

A chain advances only through a current admitted row satisfying:

- frame gap from the last chain row is at most
  `maximum_lost_frames + 1`;
- absolute source-Y step is at most `maximum_jump_px * gap`; and
- source Y does not reverse upward beyond the existing handoff reversal
  tolerance.

Existing-owner continuation is preferred. Cross-ID handoff requires a mutual,
one-to-one clear choice using the existing handoff ambiguity margin in both
predecessor-to-successor and successor-to-predecessor directions. Competing
clear choices reset the involved chains and keep the frame fail-closed. Owner
IDs are appended only when they change and are never merged.

A chain also resets when it loses all rows beyond the ordinary loss window,
encounters incompatible/material-opposed evidence, or makes no new forward
source-Y progress for `fill_evidence_window_frames`. The last rule reuses an
existing bounded evidence window: a stationary structure cannot remain a
latent release seed indefinitely.

### Chain confirmation

The chain qualifies only when all of the following are true:

- net source-Y progress from seed to current row is positive and at least the
  existing geometry-scaled drain minimum progress;
- the fraction of nonnegative source-Y steps meets the existing drain minimum
  directional agreement;
- the current row still passes common row admission; and
- exactly one chain qualifies on the frame.

On confirmation, the current row's physical tracklet becomes the sole allowed
drain owner, the distinct recovery owners are appended to the material-phase
owner chain, and the phase becomes `DRAINING`. Only the current same-frame row
may be selected and published. Earlier chain frames remain UNKNOWN/no-interface
where R18 left them; R19 performs no retrospective fill or interpolation.

If zero chains qualify, the existing barrier or initial-EMPTY fail-closed
result remains. If multiple chains qualify, the frame is ambiguous and no Oil
node is allowed.

## Lifecycle placement

```text
initial FULL FILLED_BARRIER
  -> direct release (unchanged)
  -> otherwise bounded initial-FULL release chain
  -> unique confirmation: DRAINING(current physical owner)
  -> no/ambiguous confirmation: FILLED_BARRIER, no Oil

established partial fill, no dynamic fill owner
  -> direct partial release (unchanged)
  -> otherwise bounded partial-fill release chain
  -> unique confirmation: DRAINING(current physical owner)
  -> no/ambiguous confirmation: OPEN + initial-EMPTY hard gate, no Oil
```

Once `DRAINING` exists, R18 continuation, successor handoff, loss and re-entry
remain unchanged. R19 does not create a second drain tracker.

## Diagnostics and versioning

The Oil lifecycle diagnostic schema becomes
`r19-bounded-drain-release-v1`. Existing R18 release-evaluation fields remain
byte-compatible in meaning. Each frame additionally records:

- recovery stage and whether recovery was evaluated;
- active chain summaries with seed/current Y, frame offsets, owner IDs,
  observation/transition counts, progress and directional agreement;
- each chain's ordered predicates and first failed predicate;
- qualifying and selected recovery owner IDs;
- ambiguity and reset reason; and
- whether the final release source was `direct` or `recovery`.

The resolver and detector versions advance to an R19 bounded-release-chain
identifier only after focused, replay, provenance, performance and full-suite
gates pass. Recipe schema and stored settings do not change because R19 adds no
new tuning parameter.

## Safety and non-goals

R19 must not:

- widen an entrance band, jump limit, conflict limit or direction threshold;
- use a filename, Glass ID, timestamp, source coordinate or reviewed truth in
  runtime logic;
- let a lower false structure seed initial-FULL recovery;
- treat current-frame candidate count or release-evaluation count as recall;
- merge physical tracklet IDs or inherit a predecessor's tracklet extrema;
- authorize a motion-only or material-opposed release;
- backfill prior numeric Oil, carry a coordinate through UNKNOWN or synthesize
  a coordinate;
- weaken confirmed-initial-EMPTY suppression before a real fill exists; or
- alter Foam behavior in the same change.

R19 remains field unqualified until the canonical Windows video is replayed.
The frozen evidence does not prove that a qualifying recovery chain exists; a
safe no-op on that video is preferable to admitting an unbounded or ambiguous
path.

## History Review

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: R5 edge-gated initial-state release and permanent-lock failure, R6/R7 missed-entrance recovery, R16/R17 one-to-one physical ownership and drain handoff, R18 explicit initial-FULL and partial-fill direct release, and the frozen R18 causal Windows rerun.
- Prior mechanisms rejected: global threshold or entrance widening, motion-only bootstrap, prior-fed numeric state, unbounded historical path search, physical-ID merging, coordinate inheritance, unconstrained OPEN fallback and retrospective publication remain rejected.
- Preserved contracts: independently confirmed same-frame candidates, anchor/material authority, bounded one-to-one handoff, ambiguity-to-UNKNOWN, initial-EMPTY pre-entry suppression, lower-structure entrance rejection, unchanged Foam behavior and exact selected-candidate/sequence/CSV provenance.
- Difference from prior failures: R19 does not let a prior or one missed edge create numeric output; it accumulates only current, independently confirmed and material-supported rows through bounded clear phase handoffs, resets stationary/ambiguous chains, and publishes only the unique current owner after the existing progress and agreement contracts are satisfied.
- Logic-map impact: NONE — this design defines pending R19 behavior; the current implementation map remains R18 until implementation passes and the map is updated in the implementation commit.
- Failure-registry impact: NONE — the frozen R18 evidence already owns the failure boundary; implementation evidence will update the registry only after the new mechanism is exercised.
