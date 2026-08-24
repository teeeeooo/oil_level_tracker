# S11-R17 Physical Observation Ownership Architecture

**Status:** `DESIGN ACCEPTED — IMPLEMENTATION AUTHORIZED`

## Authority and acceptance boundary

R17 is the successor to the field-failed R16 detector. It is designed from the
complete S11 history: the initial report/observation repair, slices A--D,
R2--R4 current-frame opposition, and every R5--R16 private-field failure. R16
remains the integrated baseline until this design is implemented and locally
validated. Only a new private-Windows Base/Accum replay can establish field
effectiveness.

One detector serves every Glass. Product control flow may not depend on a
video, Glass ID, timestamp, reviewed coordinate or truth annotation. Every
public Oil or Foam coordinate must remain one selected candidate from the same
source frame and must equal the sequence and CSV raw coordinate.

## What the S11 attempts established

The successor does not repeat these failed approaches:

- R1 proved that report interpretation cannot repair missing or wrong detector
  observations.
- S11-A--D and R2--R4 retained useful proposal, Artifact, static opposition and
  row-coherence evidence, but repeated rejection layers did not establish
  temporal physical identity.
- R5 proved that maximizing sequence coverage over weak current-frame evidence
  publishes glare and initial-state priors as if they were measurements.
- R6 proved that candidate eligibility and anchor authority are different
  contracts; a current-frame selected bit cannot become completed-window truth.
- R7 proved the value of explicit candidate/continuation/anchor tiers and
  independent Oil/Foam publication, while exposing representation gaps.
- R8--R10 proved that Artifact removal and motion bootstrap can recover
  proposals but cannot independently establish material identity. Sparse motion
  paths may change from liquid to reflection at a compatible Y.
- R11 proved that vertical separation from a broad Foam/material component is
  not Oil anchor authority and that component masks are not Foam-only truth.
- R12 proved that candidate-family-specific conflict exceptions leak false
  semantic anchors; typed evidence must apply uniformly.
- R13 proved that local appearance and distance adjacency cannot be promoted to
  component identity before a physical owner exists.
- R14 proved both that a real component needs bounded continuation beyond sparse
  anchors and that confirmed initial EMPTY must reject a stationary lower row.
- R15 proved that Oil/Foam aliasing must use final same-frame Oil only and that
  Foam must remain publishable without Oil. Its state-aware ownership still did
  not close the private holdout.
- R16 proved same-frame provenance and explicit tracklet/phase ownership, but
  mixed initial-state admission into physical-tracklet confirmation, truncated
  proposal diversity before row formation, and grouped Foam episodes by time
  without physical front identity.

## Replacement pipeline

```text
typed same-frame candidates
  -> row-diverse admission beam
  -> initial-state-neutral physical tracklets
  -> state-aware material-phase admission and bounded re-entry
  -> fixed-lag interface selection
  -> same-frame Oil projection

eligible Foam candidates
  -> one-to-one physical Foam-front tracks
  -> track-level material/evolution confirmation
  -> same-frame Foam projection independent of Oil availability
```

The replacement keeps proposal, physical identity, material phase, selection
and projection as one-way owners. No downstream stage invents a coordinate or
changes a candidate's source frame.

## Row-diverse Oil admission

Candidate capacity is applied to same-row hypotheses, not to a prefix of raw
candidate families. Candidates within the existing geometry-relative row
tolerance share one admission row while retaining their original offsets and
evidence. The bounded beam then keeps the best rows with deterministic vertical
diversity before it restores the member candidates required for provenance.

This replaces the R16 raw `top_k` plus separate high-recall prefix. It prevents
multiple representations of one strong but wrong row from consuming the whole
beam, while giving no recovered row anchor authority. Artifact rejection,
typed authority and candidate-level confidence remain unchanged.

## Physical Oil tracklets are initial-state neutral

`oil_interface_tracklets.py` owns only observed physical identity. It no longer
interprets `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE`, entrance bands or fill
semantics. A tracklet's direction is measured from its own observations.

Physical confirmation uses the existing typed profiles:

- two independent anchor observations confirm an anchor corridor;
- an anchor plus directional progress confirms an anchor trajectory; or
- directional progress plus registered motion confirms a motion trajectory.

There is no entrance-motion physical profile. Entrance is a material-phase
admission fact, not evidence that two rows are the same physical boundary.
Unconfirmed tracklets retain their best measured bounded-window evidence in the
trace; default zeros are never presented as the measured reason for failure.

This replacement lets a slow, repeatedly anchored Base interface become a
physical tracklet without weakening the initial-EMPTY guard. A stationary lower
structure may be physically repeatable, but it cannot become the Accum fill
owner because it has no upward material progression.

## State-aware material phase and re-entry

`oil_phase_lifecycle.py` remains the only owner of initial-state semantics.

- Confirmed initial EMPTY admits its first fill owner only from the lower
  entrance band with independently confirmed upward direction, progress and
  motion/anchor evidence.
- Confirmed initial FULL admits a descending physical interface without
  requiring that the same physical confirmation window also prove entrance
  motion.
- Once a fill phase has an established owner, loss of that physical track ID
  does not reset the semantic world to the initial EMPTY prior. One unique,
  independently confirmed, directionally compatible and material-clean row may
  reacquire phase ownership inside a bounded time/geometry corridor. The new
  physical ID is appended to the phase owner chain; observations and extrema
  are never copied between IDs.
- Ambiguous, reversed, material-opposed or corridor-external re-entry yields
  UNKNOWN. The initial lower-entry guard remains unchanged for the first owner.

This is a phase handoff, not global mutation of `initial_state`, and it does not
authorize a mid-Glass candidate merely because a prior owner once existed.

## Physical Foam-front episodes

R17 replaces time-only candidate grouping and average-score confirmation with
bounded one-to-one Foam-front tracks. A candidate joins a track only when frame
gap, source-Y motion and component extent are compatible. Competing clear
predecessors split the episode rather than pooling evidence.

A track is publishable only when it has:

- at least two registered-dynamic observations;
- coherent material support across the confirmed segment;
- no dominant learned-static explanation; and
- material evolution: a moving front, changing component extent, or a narrow
  onset that becomes a materially wide/large layer.

Constant-Y glare/residue cannot become Foam from score, whiteness or one motion
spike alone. Narrow real onset remains eligible when it evolves into a layer.
Oil availability is not required. Final same-frame Oil may reject only a
repeated same-boundary Foam track; unselected Oil proposals and inverted
topology cannot veto Foam.

The old `_candidate_groups`, `_dynamic_onset_groups`, `_episode_accepted` and
`_supported_episode` policies are deleted rather than wrapped.

## Preserved contracts

R17 must preserve:

1. Accum initial-EMPTY stationary-structure suppression;
2. real lower-entry upward Oil admission;
3. calibrated Artifact rejection and the shared Oil optics contract;
4. independent real Foam publication when Oil is unknown;
5. final-Oil-only, signed Oil/Foam identity comparison;
6. UNKNOWN for ambiguity and missing observations;
7. exactly one selected same-frame candidate for every public series value;
8. sequence raw Y = CSV raw Y; and
9. no interpolation, coordinate carry or cross-track extrema inheritance.

## Structural constraints

R17 modifies the existing owners instead of adding a parallel resolver. Failed
entrance logic is removed from the physical builder, raw-prefix admission is
replaced, and time-only Foam helpers are deleted. Version-prefixed legacy flags
remain readable where bundle compatibility requires them, but obsolete R16
control paths do not remain active beside R17 behavior.

The implementation may not solve a field failure by lowering a global Oil/Foam
threshold, widening the EMPTY entrance band, adding a private coordinate rule or
making Foam dependent on public Oil.
