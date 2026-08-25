# S11-R18 Lifecycle Closure Architecture

**Status:** `IMPLEMENTED — LOCAL GATE PASS / OPERATOR-REPORTED WINDOWS FAIL; BUNDLE AUDIT PENDING`

## Authority and scope

R18 is a bounded replacement of the two lifecycle gaps demonstrated by the
frozen R17 `windows_sample1_heating_coldstart` evidence. It is not another
candidate-authority layer and does not reinterpret the named unknowns as
facts. One detector continues to serve every Glass; no filename, Glass ID,
timestamp, reviewed coordinate or private-video exception may enter product
control flow.

R18 changes only these owners:

1. `OilMaterialPhaseLifecycleOwner` receives the confirmed initial state
   explicitly, starts confirmed FULL material behind a real phase barrier and
   permits a previously established partial fill to reverse into a drain;
2. `FoamEpisodeResolver` replaces extent-only episode acceptance with bounded
   Foam-front formation; and
3. existing same-frame projection remains the only publication path.

Candidate generation, typed authority, physical tracklet construction,
Artifact rejection, fixed-lag selection, CSV mapping and graph behavior are
outside this change.

## Evidence boundary

The design uses only the frozen R17 evidence:

- BASE remained `OPEN` for 601/601 rows despite reviewed FULL/no-interface
  prefix and suffix segments;
- ACCUM formed a real `FILLING` owner but never entered `FILLED_BARRIER` or
  `DRAINING`, then the confirmed-initial-EMPTY hard gate removed all Oil during
  the reviewed drain;
- 86 Foam rows were confirmed outside the reviewed 672--680 s Foam interval;
  the false Y80 and residue tracks were stationary or moved downward in source
  coordinates, while the reviewed Foam front formed upward; and
- Oil/Foam execution order is known, but its direct causal effect on layered
  Oil accuracy is not proven and exact layered Oil Y is not reviewed.

The last item is deliberately not changed in R18.

## Lessons retained from all S11 attempts

R18 must not recreate any prior failed mechanism:

- no state prior or future motion may become a numeric observation;
- no motion-only bootstrap may promote an unbounded path;
- vertical separation, candidate family, local appearance or broad material
  masks may not grant Oil identity;
- current conflict values may not become a universal material veto;
- track IDs and coordinates may not be copied across a phase handoff;
- initial EMPTY remains a hard material-admission gate until a real lower-entry
  upward owner exists;
- Foam remains independent of Oil availability; and
- coverage, interpolation and candidate presence are not publication truth.

R18 removes superseded policy rather than retaining parallel behavior. The
boolean `empty_entrance_motion_enabled` policy is replaced by the explicit
confirmed initial state. Extent-only Foam confirmation and its separated-layer
shortcut are deleted from the episode acceptance path.

## Explicit initial-state material ownership

`OilMaterialPhasePolicy` owns `confirmed_initial_state` directly.

### Confirmed EMPTY

The existing behavior is preserved. Before a unique dynamic lower-entry fill
owner exists, `allowed_tracklet_ids=frozenset()` and the selector removes all
Oil nodes. A stationary entrance structure, a mid-Glass row or a reason string
such as `FILL_EVIDENCE_ACCUMULATING` cannot bypass this gate.

### Confirmed FULL

The material lifecycle starts in `FILLED_BARRIER`, not `OPEN`. The barrier has
no fabricated fill tracklet and publishes no Oil coordinate. It may release
exactly one independently confirmed, downward, top-origin, material-supported
physical tracklet through the existing drain-release contract. Ambiguous,
upward, stationary, internal or material-opposed rows remain blocked.

This replaces the R17 behavior where confirmed FULL merely influenced the
selector score while the phase owner remained unconstrained. It does not
require image-state likelihood to be serialized or assume that a FULL state
proposal was generated on a particular frame.

After release, existing drain continuation, handoff, loss and re-entry rules
remain authoritative. If the owner disappears, the phase stays fail-closed;
it does not fall back to unconstrained `OPEN`.

## Established partial-fill reversal

A fill that has already produced one unique dynamic lower-entry owner is a
material fact distinct from the initial EMPTY prior. R18 retains the last
established fill chain even when its physical tracklet is lost.

When no current dynamic fill owner remains, that established fill may transfer
to `DRAINING` only if exactly one row satisfies all of the following:

- it is an independently confirmed compatible physical tracklet;
- measured direction is downward and directional agreement meets the existing
  drain contract;
- its current row is within the ordinary physical jump of the established
  fill's last observed interface;
- its current row has complete material support under the existing strict
  material contract; and
- competing eligible releases are absent; ambiguity yields UNKNOWN.

The phase owner chain appends the new drain tracklet ID. No fill observation,
coordinate, velocity, extrema or tracklet identity is copied. The initial
EMPTY gate is unchanged before an established fill exists, so the demonstrated
480--653 s ACCUM suppression remains intact.

This transition is not a global initial-state mutation and does not widen the
entrance band. It replaces the structural R17 restriction that allowed
`DRAINING` only after a completed-fill barrier.

## Bounded Foam-front formation

R17 accepted a Foam segment when material, coherence and dynamic coverage were
present and any one of front span, area span, width span or separated-layer
evidence evolved. The Windows false tracks satisfied that aggregate contract.

R18 keeps one-to-one front tracks, dynamic-frame segmentation, static
opposition, material support, coherence and same-frame projection. A new
episode additionally requires one of two bounded formation witnesses.

The primary witness is directed upward front formation in source coordinates:

- the segment's first-to-last front displacement must exceed the existing
  geometry-scaled front-evolution distance; and
- a majority of consecutive front steps must agree with upward formation,
  allowing only the existing small row jitter tolerance.

The compatibility witness preserves a reviewed stable Foam layer when at least
three dynamic observations remain spatially bounded, remain away from the top
entrance and show area or width evolution. A two-observation stable layer is
accepted only when both observations have a substantial material footprint in
area and width; narrow residue cannot use this path. Area or width evolution
alone cannot confirm a top-row track, a descending track or an unbounded
track. A separated Oil layer does not bypass either witness. Once a segment is
confirmed, every published row still comes from its own selected same-frame
Foam candidate. Foam remains publishable when Oil is unresolved.

The deleted extent-only alternatives are not retained as fallbacks. This is
the minimum evidence-backed discriminator: reviewed Foam formed upward, while
the frozen false Y80 and wall-residue tracks were stationary or moved in the
opposite direction. Field effectiveness still requires a new Windows replay.

## Intentionally unchanged boundaries

R18 does not:

- reorder Oil and Foam resolution or add a second Oil pass;
- change candidate top-k, source-family priority, global thresholds or
  Artifact templates;
- expand Foam material-identity distance;
- change drain re-entry distance after a drain phase already exists;
- claim exact Oil/Foam Y accuracy where reviewed anchors do not exist; or
- add diagnostics solely to resolve frozen named unknowns.

## Publication and compatibility contracts

Every public Oil and Foam value must retain:

1. exactly one selected nested same-frame candidate of the same kind;
2. selected candidate Y = nested sequence raw Y = CSV raw Y;
3. no coordinate interpolation, carry or synthesis;
4. UNKNOWN when material ownership is absent or ambiguous; and
5. existing stored Recipe and prior-bundle readability.

The resolver version changes only after the implementation and focused
contracts pass. R18 remains locally qualified and field unqualified. The
operator-reported Windows check failed with zero Base Oil and lower Accum Oil
coverage, but no R18 bundle/trace audit is checked in; use the
[R18 field-result record](../60-evidence/s11/s11-r18-secure-windows-field-result.md)
for that bounded disposition.

## History Review

- **Logic-map nodes:** `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`,
  `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `FOAM-EPISODE`,
  `SEQUENCE-COMPOSITION`
- **Failure-registry entries:** `S11-F05`, `S11-F07`, `S11-F08`, `S11-F10`
- **Prior mechanisms reviewed:** R5 edge-gated initial-state release, R6/R7
  missed-entrance recovery, R16/R17 material-phase ownership, and the frozen
  R17 Foam episode failure.
- **Prior mechanisms rejected:** prior-fed numeric state, unconstrained OPEN
  fallback, global entrance/threshold widening, copied phase coordinates or
  track IDs, and extent-only Foam confirmation remain rejected.
- **Preserved contracts:** initial-EMPTY false-Oil suppression, coordinate-free
  state, bounded physical ownership, ambiguity-to-UNKNOWN, independent Foam,
  and exact same-frame sequence/CSV provenance.
- **Difference from prior failures:** R18 intended to replace R17's missing
  FULL barrier and partial-fill reversal with explicit physical releases, but
  its top-origin FULL release reintroduced the R5 missed-edge lock class. The
  operator-reported field failure means that intended distinction did not
  field-qualify the design; runtime causality remains unproven without trace.
- **Logic-map impact:** `UPDATED` — the current map records the implemented R18
  lifecycle, Foam episode and publication owners.
- **Failure-registry impact:** `UPDATED` — the registry records the R18 field
  failure boundary and the R5/R18 recurrence warning.
