# S11-R22 Oil Ownership and Evidence Replacement Architecture

**Status:** `LOCAL ACCEPTED — WINDOWS QUALIFICATION REQUIRED`

## Purpose and authority

R22 replaces the Oil phase/evidence core on the R21 local candidate. It keeps
candidate generation, same-frame provenance, Foam ownership and the existing
fill/refill contracts. The replacement has one production path and is not a
second resolver or a diagnostic fallback.

`OilObservationResolver` owns the completed-window pipeline in this order:

1. `OilAdmissionEvidenceOwner` creates bounded typed current-frame refs.
2. `OilTrackletOppositionOwner` assigns directed physical identities.
3. `OilMaterialPhaseLifecycleOwner` emits immutable per-frame decisions while
   `BoundedOilReleaseEvidenceEngine` owns bounded recovery contexts.
4. `OilResolutionProjectionOwner` serializes those decisions and projects only
   the selected same-frame candidate.

Open/filling, filled-barrier and draining use separate transition functions.
One mutable record owns each frame's diagnostics during bounded retrospective
fill-onset projection; only the completed decisions are frozen.
The lifecycle transition state is explicit and separate from the immutable
`OilFrameDecision`. A diagnostic snapshot cannot alias mutable final state.
The release engine is shared by initial-FULL and phase recovery contexts; its
contexts are bounded and it never emits coordinates or promotes a candidate.

## Typed identity ownership

When a frame contains multiple ordered-lower candidates, only the nearest
independently identified interface can bootstrap authority. A deeper row is
retained as `CONTINUATION_ELIGIBLE` when otherwise usable and carries the typed
`OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER`. This contradiction is
propagated through row ownership before a representative member is selected.
A separate per-frame set of contradicted physical IDs reaches phase evaluation
even when a ref fails current admission and produces no selectable layer node.
It blocks delayed bootstrap and qualification and resets involved delayed
evidence on the same owner. A weak continuation without that contradiction
continues to work. The typed value is production input; diagnostic text is not.

## Cached witness evidence

Tracklet refs retain the confirmation witness start/end frame, observation
count, and recent-window endpoint (resolver frame offsets, not source frame indices). These fields describe the executed
bounded witness and are serialized once with the selected candidate. Existing
direction/progress/agreement fields retain their established meaning; the
cached fields do not turn future or retrospective evidence into current
authority.

## Bounded initial-FULL evidence lease

Initial `FULL_NO_INTERFACE` still starts with a coordinate-free barrier. The
existing direct release and minimum progress, direction, entrance, material,
identity and current-row gates remain mandatory. The replacement adds one
reaffirmable lease only to initial-FULL recovery evidence:

- unrenewed evidence expires at its original absolute window;
- at most one renewal is possible, with total horizon at most twice that
  window and the original seed frame retained as lease origin;
- renewal must occur on or before the old expiry, on the same physical owner
  with no prior cross-ID handoff; a renewed lease also cannot transfer to a
  different owner;
- the current row must be independently identity-valid and anchor-eligible,
  material-clean, currently admitted, confirmed/continuing, and show positive
  additional displacement since the prior certified anchor; and
- gap limits and material/admission gates remain unchanged; typed contradictions
  invalidate initial-FULL and delayed recovery. Stationary/oscillating controls
  cannot accumulate enough displacement, and cross-ID renewal or late anchors
  cannot extend an old lease.

Partial-fill and delayed reacquisition contexts retain their existing absolute
bounded behavior. Renewal never bypasses a missing current row, creates a
coordinate, or changes the delayed one-attempt contract.

## Preserved contracts and field boundary

- One generic detector serves every Glass; no private identity, coordinate,
  timestamp or case-specific branch enters control flow.
- Numeric Oil/Foam values remain selected same-frame candidates with exact
  provenance, and Oil/Foam ownership remains independent.
- Ambiguous, unavailable, lost, incompatible or hard-invalid evidence fails
  closed. No interpolation, carry, report repair or Foam authority leak is
  introduced.
- The local candidate remains field-unqualified; canonical Windows accuracy and
  throughput qualification remain outstanding. Local performance comparison is
  complete in the R22 evidence record.

## History Review

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`,
  `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F08`, `S11-F09`,
  `S11-F10`.
- Prior mechanisms reviewed: R16 directed identity and bounded loss, R18
  lifecycle closure, R19 absolute recovery expiry, R20 delayed readiness and
  direct/near/delayed precedence, and R21 recent trajectory evidence.
- Prior mechanisms rejected: unbounded origin reset, unconditional expiry
  extension, cross-ID renewal, diagnostic-text checks, coordinate/snapshot
  carry, candidate-family privilege and private field branches.
- Preserved contracts: typed authority, distinct physical identities,
  coordinate-free barriers, bounded ambiguity/loss, current-row admission,
  exact same-frame provenance and independent Foam publication.
- Difference from prior failures: one same-owner reaffirmation is a bounded
  initial-FULL lease transition with an immutable origin and explicit witness;
  contradiction is typed before row-member selection and delayed evidence is
  reset on the involved owner.
- Logic-map impact: UPDATED — R22 now owns the Oil phase/evidence seam and
  cached witness fields.
- Failure-registry impact: NONE — existing mechanisms remain the failure
  history; R22 is the bounded replacement and does not rewrite observations.
