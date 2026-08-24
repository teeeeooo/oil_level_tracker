# S11-R16 Directed Tracklet and Material Lifecycle Architecture

**Status:** `PROPOSED REPLACEMENT`

## Authority boundary

This document defines the R16 replacement candidate. It is not yet the active
field detector authority and does not supersede the
[R15 architecture](s11-r15-state-aware-material-ownership-architecture.md).
Promotion requires an independent audit of the exact committed head before
push, followed by a new private-Windows Base/Accum replay of that pushed head.
The current gate is owned by the [work plan](../00-project/work-plan.md); local
execution results are preserved in the
[R16 evidence record](../60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md).

One production detector continues to serve Base and Accum. Product code may
not branch on video identity, Glass identity, field timestamp, reviewed Y or
truth data. Every numeric Oil result remains one selected candidate observed in
that exact frame.

## Replacement reason

R13–R15 treated candidate connectivity, component identity, material phase and
final path choice at partially overlapping stages. Private evidence exposed the
failure modes:

- an adjacency/component path could change physical row without an explicit
  ownership transfer;
- a completed-fill veto could erase a valid later drain owner after selection;
- R15 initial-EMPTY admission assumed lower-entry evidence preceded an anchor,
  while the audited Accum component formed an upper anchor before its later
  lower-band observation; and
- post-selector member confidence could censor a physical row after another
  representation had already won owner selection.

R16 replaces those seams with a one-way chain:

```text
same-frame candidates and typed evidence
  -> same-row hypotheses
  -> bounded directed physical tracklets
  -> causal material-phase owner and allowed tracklet IDs
  -> candidate-publishable row hypotheses
  -> fixed-lag interface selector
  -> invariant check
  -> same-frame public projection
```

## Directed physical tracklets

`oil_interface_tracklets.py` owns physical identity. Candidates within the
bounded row tolerance become one same-frame row hypothesis while retaining
every original candidate and its offset. Tracklets then use deterministic
one-to-one assignment against only the bounded active set.

- many-to-one or one-to-many matches inside the assignment-cost ambiguity
  margin are incompatible branches; an established parent owns a split child
  only when it is also that child's clear predecessor, so a nearby child with
  another clear physical predecessor does not cause a false split;
- an ambiguous established parent terminates, every involved child becomes an
  incompatible new ID and no child silently inherits the old identity;
- a tracklet may be provisional, confirmed, continuing, lost or terminated;
- confirmation is bounded to six sampled frames and loss to two frames;
- confirmation profiles distinguish anchor/corridor, anchor/trajectory,
  entrance/motion and motion/trajectory evidence;
- direction, net progress, motion support/coverage and material conflict are
  tracklet evidence, not source-name authority; and
- bounded retro-admission may publish an earlier witness only when the same
  physical tracklet confirms within the fixed lag. It never creates a missing
  coordinate.

Physical IDs never merge across a phase handoff. The row hypothesis ID and
selected original-candidate offset remain available for provenance.

## Forward material-phase lifecycle and bounded onset intent

`oil_phase_lifecycle.py` owns `OPEN`, `FILLING`, `FILLED_BARRIER` and
`DRAINING`. It consumes admitted physical rows, not only rows that currently
pass final publication confidence. This separation lets phase ownership
survive a weak frame without allowing that weak frame to become numeric.

The lifecycle emits one allowed-tracklet set per frame:

- `None` means ordinary open selection;
- a singleton means only that physical owner may compete;
- an empty set means the phase barrier or ambiguity requires `UNKNOWN`.

Fill and drain handoffs require a unique mutually compatible successor.
Ambiguous successors produce `UNKNOWN` and do not destroy a still-valid prior
owner. A drain owner that exceeded its bounded loss interval may transfer phase
ownership to one uniquely confirmed, directionally compatible and
material-clean re-entry within one ordinary physical jump. Compatibility
requires the new row not to reverse above the prior phase Y beyond the normal
handoff tolerance. The owner chain records that transfer while preserving
distinct physical IDs.

Drain release, direct continuation, successor handoff and phase re-entry all
apply both track-history material conflict and the complete current-row
material veto. A clean direct member cannot mask a same-row material-path
sibling at or above the conflict limit.

In an initially visible/unknown interface context, a central
`MOTION_TRAJECTORY` activates `FILLING` only when it has strong registered
motion support and coverage and no current or bounded-retained strong anchor
interface is still established. In confirmed initial `EMPTY`, the existing
lower-entrance `ENTRANCE_MOTION` evidence is required instead. Anchor profiles
alone remain evidence accumulation; they do not manufacture fill intent.

When one dynamic fill owner activates, the lifecycle may link one unique
immediately preceding admitted row using the normal jump, maturity and
ambiguity rules. The predecessor ID is prepended only to the phase owner chain:
no observations, extrema, direction or coordinates transfer between physical
tracklets. Bounded onset-intent metadata constrains only frames where that
predecessor was actually observed; a gap is `UNKNOWN`. An ambiguous or absent
predecessor never authorizes a foreign coordinate.

`FILLED_BARRIER` supplies no Oil owner until a physically confirmed downward
release exists. Internal full/turbulent cap rows therefore cannot compete merely
because their local emission is high.

## Publication and fixed-lag selection

`oil_interface_selector.py` owns publication-layer construction and fixed-lag
selection. The phase layer and publication layer are intentionally different:

- phase reasoning sees admitted physical hypotheses;
- publication sees only a row with at least one same-frame member that passes
  authority, tracklet admission, compatibility, trajectory and the existing
  candidate-level `minimum_final_confidence` gate.

Publication exposes one deterministic candidate member per row hypothesis.
Ordering uses emission, confidence, authority, local quality, Y and source; it
does not depend on incoming candidate order. A high-emission but
non-publishable representation cannot win and then poison a publishable sibling.
R16 does not pool evidence across siblings and does not introduce row-level
confidence. A row whose members all fail candidate-level confidence remains
non-publishable.

The selector first filters by the phase lifecycle's allowed physical IDs, then
scores a six-frame lookahead, at most seven layers including the current frame.
Oil-to-Oil transitions require the same physical tracklet ID or two adjacent
IDs in the explicit phase owner chain. A close competing physical owner within
the ambiguity margin yields `UNKNOWN`; no source priority or case-specific
coordinate breaks the tie.

The former post-path continuation owner is now an invariant assertion. It may
detect a programming error but cannot reselect an owner or turn one selected
physical row into another. Spike suppression remains a censor only and never
interpolates.

## Causality, complexity and dependency direction

The individual confirmation and fixed-lag stages both use a six-sampled-frame
policy, but six is not the end-to-end commit horizon. Confirmation of the first
witness can require five additional future frames, while onset intent or the
selector can use a six-frame future bound. The canonical end-to-end lag is
therefore `6 + (6 - 1) = 11` sampled frames, a 12-frame inclusive envelope
from `t` through `t+11`. `OilObservationResolverConfig` exposes this as
`end_to_end_commit_lag_frames`.

An adversarial composed regression proves both sides of the contract: evidence
at `t+7` may still alter onset reason/owner metadata after a prefix ending at
`t+6`, while data appended after a prefix ending at `t+11` cannot change the
target Y, physical tracklet, material phase, reason or owner chain.

Tracklet matching is bounded by active tracklets and per-frame row hypotheses;
selection and onset intent retain their six-frame stage bounds. No whole-video
unbounded graph or backward coordinate repair is introduced.

The resolver remains a facade over admission, tracklet/opposition, material
phase, selector and projection owners. A decomposition guard caps
`oil_observation_resolver.py` at 2,700 lines and `OilPathLifecycleOwner` at 260
lines. Dead completed-fill reacquisition and duplicate bounded path policies
are absent.

## Non-authorities and local acceptance choice

Truth, provisional annotations, aggregate coverage, private timestamps and
debug overlays validate but never alter production selection. R16 also does
not authorize threshold reduction, cross-row confidence pooling or a
case-specific proposal generator.

R16 adopts the explicitly authorized safety-first local contract. Aggregate
checked-truth coverage is diagnostic, not authority to force a row. The
replacement assertions require the reviewed initial owner, cap barrier,
directional drain release/handoffs, conflict/reversal-window abstention and
same-frame provenance directly.
The candidate-level reasons are preserved in the
[R16 owner audit](../50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md).
This choice does not lower candidate confidence, pool row evidence or waive the
pending private-Windows gate.
