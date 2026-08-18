# S11-R12 Phase/Composition Replacement Architecture

**Implementation status:** designed; implementation in progress.

## Purpose

R12 replaces the R11 policies that failed secure-Windows Base/Accum. It is not
an R11 threshold layer and does not introduce per-video behavior. The code is
changed from the R11 source head, but motion-only bootstrap authority,
unbounded Foam-material continuation, distinct-lower direct anchoring,
material-bottom topology veto and shared Oil/Foam validity are removed rather
than guarded by another version branch.

The physical output remains two independently observed series:

- the Oil/air interface; and
- the Foam front, when Foam is present above Oil.

The final graph must show each series when its own observation is defensible.
One unresolved series must not erase a valid observation from the other.

## Replacement pipeline

```text
same-frame raster evidence
  -> representation-family proposals
  -> typed evidence with explicit availability
  -> hard-invalid filtering and reserved family admission
  -> material phase / residue identity
  -> bounded candidate trajectories
  -> Oil path selection
  -> Foam episode selection
  -> Oil/Foam composition and per-series validity
  -> immutable TrackingSample / graph projection
```

Candidate families remain implementation details. `r6`, `r8`, `r9`, `r10` and
`r11` feature names may be read at the compatibility boundary while migration
is incomplete, but no new control-flow branch is named after one of those
versions.

## Typed evidence and missing-value semantics

Every proposal exposes both a value and availability for direct boundary,
phase/material, texture conflict, optics/static opposition, registered motion
and representation corroboration. Missing evidence is unknown, not measured
zero. In particular, a candidate family that never computed material-texture
conflict cannot gain anchor authority by inheriting conflict `0.0`.

Debug trace records the normalized evidence values, availability mask, admission
reason, authority reason, trajectory membership and final selection. It also
distinguishes current-frame preview state from completed-window sequence state.

## Candidate admission

Each representation receives a bounded reserve before a global cap is applied.
A strong upper residue or rim family cannot consume all rows and remove a weaker
lower phase-boundary family before identity/trajectory evaluation. Artifact
templates remain user-confirmed hard negative geometry at the candidate level;
frame-level “some candidate rejected” is diagnostics only.

High recall is allowed at admission. Publication remains conservative. A row
can remain a candidate even when direct phase evidence is weak, but it cannot
become an anchor solely because it moves or persists.

## Phase identity and bounded trajectory

Registered motion is discovery evidence, not physical identity. A motion path
may group and reserve candidates, but anchor authority requires an independent
same-frame identity proof from direct phase/material evidence or corroborating
representations. Path members are re-evaluated individually; two keyframes may
not promote a mixed reflection/liquid/bracket segment.

Trajectory edges are bounded by time, displacement and evidence continuity.
Identity change, excessive gap or unavailable required evidence splits the
component. A valid interface segment may contain continuation rows around an
independent anchor, but an anchor-free motion segment remains review-only.

This replaces R11 calibrated bootstrap. R12 does not emit
`calibrated_bootstrap` authority.

## Foam/residue material identity

Foam material tracking is a bounded observation, not a permanent upper-track
label. It has explicit seed age, maximum missing duration, cumulative drift and
reseed requirements. Identity opposition applies to every Oil candidate family
whose row and material evidence match the active Foam/residue track.

A geometrically lower row is reserved for Oil evaluation, but separation alone
never grants anchor authority. The R11 `foam_distinct_lower_boundary` authority
route is removed. A lower row must pass the ordinary independent Oil identity
and trajectory contract.

## Foam episode continuity

Foam admission supports two shapes:

- a wide coherent layer; and
- a narrower component with strong registered internal/dynamic material
  evolution.

The dynamic narrow route replaces the fixed width-only loss observed on Accum.
Episode linking uses elapsed time and a bounded velocity/jump envelope so a
rapidly rising front is not split merely because sampled rows move more than a
fixed 24 px. A persistence-pending frame may bridge a short dropout, but it can
publish only a same-frame Foam coordinate already present in that frame.

Raw material masks are evidence maps, not a physical Foam-only segmentation.
Their bottom may include the transition and Oil regions. Therefore
`material_component_bottom_y` cannot veto otherwise ordered Oil/Foam fronts.

## Oil/Foam composition

The composition point evaluates front order and independent evidence:

- `foam_y < oil_y` with adequate separation is normal layered composition;
- close same-frame coincidence may be an alias and remains reviewable;
- reversed order is a topology conflict;
- a broad raw material-mask bottom is diagnostic only; and
- missing Oil does not delete confirmed Foam, while missing Foam does not
  delete valid Oil.

No composition rule creates a coordinate. Oil and Foam publication always
retain one selected same-frame candidate each.

## Per-series validity and downstream compatibility

`TrackingSample` owns `oil_is_valid` and `foam_is_valid`. Legacy `is_valid`
continues to mean the state/Oil observation validity used by events, extrema,
judgment and existing CSV consumers. The review graph uses each series' own
validity. Foam confidence and confirmation determine `foam_is_valid` even when
the fill state is `UNKNOWN_REVIEW` because Oil is missing.

Bundle readers treat absent per-series columns as the legacy `is_valid` value,
so old results remain readable. Writers emit the explicit fields. Initial-state
hold remains a downstream state interpretation; it cannot create numeric Oil or
Foam.

## Removed R11 policies

R12 has no alternate fallback to:

- motion-only calibrated bootstrap authority;
- `foam_distinct_lower_boundary` anchor authority;
- indefinite Foam material continuation;
- missing conflict interpreted as conflict-free;
- material-component-bottom hard topology rejection; or
- one shared graph-valid bit for Oil and Foam.

Historical R11 flags may remain in old bundles, but R12 does not emit them as
new authority. No Glass ID, filename, source timestamp or private truth enters
production decisions.

## Performance boundary

Evidence is computed once per candidate/frame and sequence stages reuse typed
rows. R12 must not add another full-frame image pass inside the resolver. Direct
detector time and completed-window resolver time are measured separately; a
correct replacement that materially regresses interactive analysis time does
not pass.
