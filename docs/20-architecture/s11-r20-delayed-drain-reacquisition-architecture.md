# S11-R20 Delayed Drain Reacquisition Architecture

**Status:** `IMPLEMENTED — LOCAL PASS / WINDOWS REQUIRED`

## Purpose and authority

R20 adapts the existing R19 bounded drain-release chain at the
`OilMaterialPhaseLifecycleOwner` boundary. It addresses the case where an
initial-`EMPTY` material phase established a genuine fill owner, lost that
owner before `DRAINING`, and later exposes a fresh, independently identified
drain candidate outside the retained fill snapshot's ordinary jump.

R18 direct release remains the first authority. R19 near-snapshot recovery
remains the second authority. R20 delayed reacquisition is a third, strictly
bounded lifecycle route. Candidate generation, typed authority, physical
tracklet identity, selector, projection, Foam and publication remain owned by
their existing modules.

## Owner and state

The sole owner is `OilMaterialPhaseLifecycleOwner`.

`PartialFillOwnerlessBarrier` is coordinate-free phase context. It records
that the same established material episode has lost its dynamic fill owner;
it retains only bounded episode provenance, loss frame and ordinary grace
context. It accumulates no rows, coordinates, scores, motion or lookahead.
The retained fill snapshot Y/frame is diagnostic context only and is never an
identity predicate for delayed reacquisition or a publication coordinate.

`DelayedDrainReacquisitionAttempt` is one bounded R19-shaped evidence chain per
established-fill episode. It starts only from a unique fresh current
`ANCHOR_ELIGIBLE` row. A delayed attempt does not stretch an existing physical
tracklet: every new tracklet ID stays distinct and is appended to phase
provenance only after confirmation.

## Ordered lifecycle behavior

For an established initial-`EMPTY` fill with no dynamic fill owner:

1. keep the existing upward fill re-entry path first;
2. evaluate direct partial-fill release, unchanged;
3. evaluate R19 near-snapshot recovery, unchanged; and
4. only after ordinary loss grace, evaluate the unused R20 delayed attempt.

The ordinary grace is `maximum_lost_frames + 1`. During grace the barrier is
active but delayed seeding is unavailable, and earlier frames remain
`UNKNOWN`/nonnumeric. No later result backfills that interval.

The delayed route is eligible only while initial state is confirmed EMPTY, an
established fill exists, no dynamic fill owner has reappeared, direct and
near-snapshot recovery have no current qualifier or ambiguity, the episode
context is unchanged, and its one delayed attempt is unused. The first frame
with one or more qualifying delayed anchors consumes the attempt. Exactly one
anchor starts a chain; multiple qualifying anchors are ambiguity and consume
the attempt without publication. A failed, expired or ambiguous attempt
cannot reseed until a newly established fill episode exists.

An active attempt is closed on successful drain confirmation, owner/context
change, dynamic fill reappearance, direct or near recovery release, or the
existing R19 loss, stagnation, material, step, ambiguity and absolute evidence
window bounds. The ownerless barrier is reset on those context changes and is
never carried into a new fill episode.

## Delayed seed and chain contract

A delayed seed must be one unique same-frame row that independently passes:

- existing common recovery admission and strict current/tracklet material
  support;
- a real same-frame Oil candidate;
- `ANCHOR_ELIGIBLE` authority;
- `DIRECT_INTERFACE` or valid `ORDERED_LOWER_INTERFACE` phase identity;
- bounded admitted tracklet with a non-`NONE` confirmation profile;
- compatible, non-provisional physical identity; and
- elapsed ordinary loss grace with the unused ownerless barrier active.

The delayed seed deliberately has no retained-snapshot distance predicate.
Snapshot distance is diagnostic only (`snapshot_distance_used_for_identity` is
false). No motion-only, direction-only, recurring-Y, source-family,
candidate-only, continuation-only or stale-snapshot seed is allowed.

After seeding, the existing R19 chain rules remain unchanged: same-owner
continuation may use continuation authority; every cross-ID handoff requires
fresh anchor authority and reciprocal one-to-one clear choice; each step is
bounded by the existing gap, jump, reversal, material and ambiguity limits;
and cumulative positive progress plus directional agreement must qualify
exactly one chain. The current row on confirmation is the sole allowed
`DRAINING` owner and the only row eligible for selection/publication.

## Bounds and invariants

No Recipe, Glass-specific, video-specific, timestamp-specific or coordinate-
specific setting is added. Existing `maximum_jump_px`,
`maximum_lost_frames`, `fill_evidence_window_frames`, direction, material,
ambiguity, selector lookahead and commit bounds are reused unchanged.

The barrier is one constant-size phase state. At most one delayed attempt is
active per established-fill episode. Its evidence lifetime starts at the fresh
seed and expires under the existing inclusive R19 window rule. Owner IDs and
observations remain bounded by that window and existing candidate/tracklet
capacity.

Initial EMPTY remains a hard gate before a real fill owner. Initial FULL
remains a coordinate-free barrier and does not use delayed partial-fill
reacquisition. Numeric Oil remains a selected same-frame candidate; no stale
snapshot/seed coordinate, carry, interpolation or retrospective publication is
possible. Ambiguity and material opposition fail closed. Foam behavior is
unchanged and independent.

## Diagnostics and compatibility

Lifecycle diagnostics use `r20-delayed-drain-reacquisition-v1` and retain all
R18/R19 field meanings. They add ownerless-barrier state, loss epoch/age and
grace, established snapshot provenance and diagnostic distance, one-attempt
state, explicit direct/near/delayed evaluation ordering/source, delayed seed
predicate records, active chain summaries and reset/ambiguity causes. These
fields are observational only and cannot affect admission, ranking, selection
or publication.

`OilObservationResolver`, sequence and detector version identifiers advance to
the R20 identifier. Selector, projection, CSV, graph/report, event and Foam
semantics remain behavior-compatible apart from carrying the additive
lifecycle diagnostics.

## History Review

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`,
  `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`,
  `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`,
  `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R16 reciprocal physical ownership, R17
  owner-loss dead end, R18 initial-FULL/partial-fill lifecycle closure and
  causal rerun, and R19 bounded direct/near recovery and local validation.
- Prior mechanisms rejected: global jump/entrance/authority widening,
  motion-only bootstrap, stale ID or coordinate transfer, unconstrained OPEN
  fallback, unbounded path search, selector/projection repair, private field
  identity, interpolation/carry, Foam coupling and golden regeneration.
- Preserved contracts: one generic detector, initial-EMPTY safety,
  coordinate-free FULL, independent same-frame anchor/material identity,
  distinct physical IDs, bounded reciprocal handoff, ambiguity/material
  opposition to UNKNOWN, exact selected-candidate/sequence/CSV provenance,
  bounded resources and unchanged Foam.
- Difference from prior failures: R20 retains a constant-size ownerless phase
  barrier, waits through ordinary loss grace, permits one fresh-anchor attempt
  per established-fill episode and applies the existing bounded chain only to
  current evidence. It does not use elapsed loss age or snapshot distance as
  physical identity.
- Logic-map impact: `UPDATED — the design gate intentionally left the current
  map on R19 pending implementation; the implementation and local-evidence
  gate now records R20 lifecycle behavior in the current map`.
- Failure-registry impact: `NONE — R20 is a bounded closure of existing F04,
  F05, F08, F09 and F10 guards, with F02 preserved as the proposal/authority
  funnel guard`.
