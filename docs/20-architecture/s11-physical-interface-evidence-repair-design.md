# S11 Physical Interface Evidence Repair Design

**Design status:** proposal for implementation and validation; not an accepted
runtime architecture. Revision naming and runtime promotion are not assigned
by this document. The [work plan](../00-project/work-plan.md) owns execution state.

[R22-2 native path diagnostics](s11-r22-2-interface-path-diagnostics-architecture.md)
extends R22-1 measurement extraction only. It does not implement the proposed
`OilInterfaceWitness` classifier, independent-support promotion, physical
association, handoff or direction-neutral observation described below. A
captured path is generator evidence, not a certified physical interface.

## Problem and chosen direction

The [reviewed R22 investigation](../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md)
identifies two different failures. A visible Accum boundary has an admitted
tracklet but cannot replace the allowed fill owner, while its independent
representation support is blocked by broad texture conflict. In BASE, an
off-boundary candidate and a real boundary share one tracklet, creating an
upward trajectory which correctly fails the existing downward release test.

The design gives current-frame interface evidence an explicit, shared contract.
That evidence supports independent corroboration, physical association and
phase ownership. Motion remains a separate measurement over verified
associations. A visible interface may be observed without declaring drainage.

The design covers four changes, in this order:

1. Measure local interface structure and distinguish texture presence from
   contradictory internal structure; use this in independent corroboration.
2. Prevent uncertain physical associations from contributing direction,
   progress or confirmation evidence.
3. Replace fill-owner handoff's source-family privilege with current interface
   evidence and an explicit, bounded ownership transition.
4. Add a separately validated direction-neutral visible-interface phase for
   initial-FULL reacquisition and established-fill stabilization.

Items 1--3 must work before item 4 can be enabled. None is a claim that all
reported Windows gaps will be repaired.

## 1. Interface evidence and independence

### Responsibility and data

Add an immutable per-candidate `OilInterfaceWitness` at `FRAME-EVIDENCE` /
`OIL-CANDIDATE`, normalized by `OilCandidateEvidenceIndex`. This is a proposed
type. The witness is computed from the current source raster and effective
mask before authority, selection or final Foam publication. It includes:

| Field group | Required meaning |
|---|---|
| Provenance | Source-frame index, crop transform, candidate identity, measurement channel and shared derivation identity; array sort order is not identity |
| Spatial support | Valid common column sectors, local contour Y per sector, edge localization and uncertainty; missing sectors stay unavailable |
| Two-sided context | Signed band contrast and material/texture summaries immediately above and below the contour in each valid sector, with broader context for internal stripes |
| Opposition | Existing artifact, border, exclusion, glare and optics evidence plus local internal-structure evidence; no final Foam decision |
| Decision | `INTERFACE_SUPPORTED`, `INTERNAL_OR_ARTIFACT`, or `UNRESOLVED`, with evaluated predicates and availability |

Reuse the material path's five-sector decomposition as the initial bounded
measurement grid; at least three spatially distinct usable sectors are needed
for the new distributed witness. Sample other candidate families on the same
grid. Do not assume that an aggregated median Y describes a curved contour.
Per-sector bands must exclude the edge itself and respect the effective mask.
Persist small descriptors, not full frame histories. Evidence enrichment does
not add proposals or enlarge the candidate beam.

An edge peak alone, material-mask bottom, high row texture, two generator names,
or vertical ordering is insufficient. `INTERFACE_SUPPORTED` needs localized
boundary support and a coherent two-sided partition across the valid sectors,
with usable artifact/optics evidence and no contradictory internal-stripe
context. Photometric sign is measured; Oil is not universally assumed dark or
bright. The new measurements must distinguish interface partition from a
bright stripe inside otherwise comparable material on both sides.

The current scalar `material_texture_conflict` remains in diagnostics and in
legacy behavior until its replacement is validated. A new high-texture route
requires the positive local partition witness for both participating peers;
it does not zero the scalar or remove artifact/optics gates. Missing new
descriptors cannot activate this route. Existing clean-evidence routes retain
their current requirements during implementation comparison.

### Independent corroboration

Construct evidence before authority in a directed order: raw witness → eligible
peer relation → independent support → phase identity → authority. A candidate
cannot use its new anchor status to validate the peer that granted that status.
Rejected-by-selection or pruned peers may supply eligible raw evidence; a
hard-invalid peer may not.

Different source-family strings are necessary only where the existing family
contract requires them; they are never sufficient proof of independence.
Duplicated candidates and descendants of one measurement contribute once.
An edge-localization channel and a separately measured region-partition channel
may corroborate on a common physical contour; aliases of one edge extraction
may not. Peer agreement uses common-sector contour overlap and uncertainty as
well as bounded Y distance. Preserve calibrated-only bootstrap prohibitions.

`OilCandidateRef` carries the resulting witness identity and contributing peer
identities. Phase identity and lifecycle consume this same typed result rather
than recomputing different texture/source shortcuts. Existing ordered-lower
contradictions remain explicit vetoes; proximity to a Foam row never creates
Oil identity.

### Material gate consumption

Changing the peer gate alone is insufficient: scalar material conflict is also
read by authority, row/tracklet aggregation, phase admission, release and
selector continuation support. Introduce one typed material-compatibility
decision at these seams for the new witness route. `INTERNAL_OR_ARTIFACT`
remains a veto. `INTERFACE_SUPPORTED` may satisfy material compatibility despite
high broad texture only with the required local partition and independent
support; it does not bypass other authority or lifecycle predicates.
`UNRESOLVED` supplies no exception to existing material gates.

Retain raw scalar values and the legacy threshold outcome in diagnostics next
to the typed outcome. Do not write a fabricated zero into current or historical
conflict. Evaluate compatibility on each actual contributing member/observation:
a true contradiction cannot be erased by a cleaner member, a median or a later
anchor. Unsupported members cannot borrow the row's positive witness to become
publishable. Historical compatibility covers the verified motion/confirmation
observations; no new witness can sanitize a false predecessor.

This is a semantic replacement of broad-texture vetoes where the new witness
is complete. Existing drain direction, minimum progress, entrance and expiry
requirements remain unchanged. Compound extraction-to-publication tests must
prove that a downstream legacy scalar gate does not silently cancel the new
typed decision, and that true material contradictions still block it.

## 2. Physical association before motion

`DirectedInterfaceTrackletBuilder` continues to enforce the existing maximum
gap, jump, prediction, one-to-one assignment and ambiguity bounds. Add a typed
association result: `SAME_INTERFACE`, `DIFFERENT_INTERFACE`, or `UNRESOLVED`.

For candidates with usable witnesses, compare common-sector contour shape and
two-sided context after bounded registration. Use spatially distributed
displacement agreement to distinguish physical movement from selecting another
stripe. A single band-motion scalar, shared direct/ordered class or shared
source does not certify an association. A contradiction must not be averaged
away by other members of a row.

- A stable or moving same-interface match retains its physical tracklet ID.
- A physically different current interface starts a fresh ID and fresh motion
  history. The predecessor's anchor count, direction, progress and lease cannot
  be copied to it.
- An unresolved match cannot add a displacement edge or confirm the previous
  identity. Retain a bounded provisional alternative and publish UNKNOWN until
  identity is established. Do not convert missing evidence into a successful
  same-interface result. Existing ambiguity handling remains active.

Use only verified displacement edges for recent and confirmation trajectories.
Fresh confirmation cannot reach backwards across an unresolved/different edge.
Preserve valid rapid movement and physical reversals when distributed evidence
supports them; do not lower the global jump bound or forbid upward motion.
Existing bounded retrospective confirmation may certify eligible observations
inside its window, but may not import the false predecessor into the new ID.

## 3. Established-fill owner transfer

Replace the source-specific condition in `_is_current_fill_anchor_handoff`
with a shared interface-witness requirement. A proposed successor must be a
current admitted anchor with a confirmed, uncontradicted physical identity,
usable current interface evidence and the existing bounded phase geometry.
Continuation authority alone is insufficient. Initial EMPTY entrance remains
the existing dynamic lower-entry contract.

There are two explicit cases:

1. **Identity-preserving handoff:** exactly one successor is independently
   confirmed and physically compatible with the last verified owner observation
   within ordinary loss grace. Transfer phase ownership, append its distinct ID
   and retain a bounded phase link. Do not copy the predecessor's measurements.
2. **Owner correction:** the old owner is positively contradicted and exactly
   one independently confirmed current interface exists. Start a fresh
   direction-neutral observation episode under section 4; do not claim it is a
   continuation of the old structure or inherit its fill/drain motion.

If the predecessor's identity is unavailable rather than positively
contradicted, case 2 does not apply. If an old owner is still valid and competes
with the successor, or multiple successors qualify, emit UNKNOWN and retain
the existing bounded ambiguity/loss handling. Expired snapshots cannot be
refreshed merely because another candidate appears.

The current temporary handoff leaves the original chain unchanged. The proposed
replacement records whether transfer was committed, which fresh owner is
allowed next, and when the link expires. A temporary allowance must not be
reported as a committed transfer. On loss of the successor, do not fall back
to a stale predecessor coordinate or silently return to its identity.

The selector remains a consumer of the explicit allowed owner set. It must not
solve a handoff failure by selecting a higher-scoring unallowed tracklet.

## 4. Direction-neutral visible-interface ownership

Propose an explicit `OBSERVED_INTERFACE` phase, separate from `DRAINING` and
`FILLING`. This is a deliberate extension of the current four-state lifecycle,
not a reinterpretation of the existing `downward_direction` predicate.

| From / trigger | Proposed transition and publication |
|---|---|
| Initial `FILLED_BARRIER`, strong bounded current interface witness | Enter `OBSERVED_INTERFACE` with one fresh owner; publish only an eligible selected current candidate |
| Established fill, confirmed stable interface or qualified owner correction | Enter `OBSERVED_INTERFACE`; preserve material-presence context but do not transfer unverified motion |
| `OBSERVED_INTERFACE`, verified sufficient downward motion | Enter `DRAINING` under existing direction/progress/material requirements using this identity's motion history |
| `OBSERVED_INTERFACE`, verified upward motion | Enter the appropriate fill/refill path with existing direction and closure evidence; no fabricated FULL transition |
| Current supported no-interface FULL evidence | Close observations and return to coordinate-free `FILLED_BARRIER` |
| Missing, hard-invalid or contradictory current row | Publish UNKNOWN immediately; context may survive only the existing bounded loss grace |
| Expired or ambiguous context | Clear owner eligibility and return to the constrained originating context, never unconstrained OPEN |

Initial-FULL admission to this new phase requires all of the following:

- an independently supported current interface witness, including two-sided
  raster partition and artifact/optics clearance, that contradicts a homogeneous
  no-interface interpretation;
- a unique physical owner confirmed within the existing bounded confirmation
  window, using fresh qualifying observations and no unresolved association;
- no hard current no-interface/identity contradiction, competing qualified
  owner, unavailable mandatory evidence or internal-structure classification;
- an eligible actual candidate on every published frame. A window witness
  cannot publish a frame with no eligible boundary candidate.

This is stronger than existing `ANCHOR_ELIGIBLE`/`ANCHOR_CORRIDOR` alone.
Stationarity and persistence are not positive interface evidence. The new route
may observe a genuinely stationary boundary only with independently validated
raster identity. It may not release an existing drain gate on stationary or
upward progress. Homogeneous opaque FULL, fixed reflection, wall residue and
internal stripes remain no-numeric controls.

Keep initial EMPTY ineligible for this route until its own entrance is
established. Do not mutate the configured initial state. Each supported current
observation refreshes only the ordinary owner-loss age; an absent row cannot
refresh it. Reacquisition needs a fresh bounded witness, not an extended lease.
Keep existing direct/near/delayed drain ordering for frames qualifying those
routes; the new observed-interface route follows them and cannot override
ambiguity or a hard veto reported by a prior route. It does not reset a
consumed delayed attempt in an existing episode.

Downstream projection must audit every phase switch. This state means visible
Oil with unknown movement direction; it does not manufacture fill/drain events,
change coordinate conversion or become a fallback coordinate. Final Foam
resolution remains independent.

## Decisions, calibration and implementation boundary

The chosen owner boundaries, required predicates, fail-closed behavior and
transition semantics above are design decisions. Numeric operating points for
partition strength, contour/context similarity, registration uncertainty and
internal-stripe discrimination are **not yet validated** by the transferred
scalar reports. They must be selected from public/synthetic positive and
negative raster controls before enabling the corresponding new route. Reuse
existing spatial, temporal and resource bounds where applicable; do not choose
thresholds to include a private Y jump or make a private conflict value pass.

The current scalar evidence lacks per-sector two-sided context and provenance
lineage needed to claim these witnesses already exist. Implementation must
add those bounded measurements and serialize the actual decisions. If the
controls cannot distinguish a stationary interface from an internal structure,
section 4 remains unenabled; do not weaken its evidence requirements.

Implementation sequence is witness extraction and controls, independent support,
association and confirmation, committed fill handoff, then the new phase and
projection audit. Initial-FULL adoption is a distinct acceptance gate. The
[validation contract](../30-validation/s11-physical-interface-evidence-repair-validation.md)
defines the required cases and measurements. No production change is made by
this proposal.

## Diagnostics

Record actual predicate inputs, thresholds, availability and reasons rather
than rerunning decisions for trace output. Include:

- stable candidate identity, peer measurement lineage and peer exclusion;
- interface/partition/stripe decision and usable sectors;
- predecessor/current row identities, association result, displacement edges
  actually included in each motion window;
- phase handoff versus owner correction, attempted/committed distinction,
  allowed-set exclusion and ambiguity before path scoring;
- visible-interface acquisition/expiry/closure source, current witness endpoint,
  and chain-specific reset identity and reason.

Persist resolver offset and source-frame index as separate fields. Document
whether a legacy candidate offset refers to pre-sort input; do not relabel it
as the serialized array index. Diagnostic detail must not change output.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 cross-representation texture veto and material-member temporary handoff; R16/R21 bounded association and confirmation; R18 initial-state and partial-fill gates; R19/R22 release lease bounds; R10/R11 smooth false-identity paths and F06's textured true/false material counterexamples.
- Prior mechanisms rejected: scalar texture neutralization, generator-count identity, globally reduced jump thresholds, stationary drain release, continuation-only takeover, stale owner or coordinate copy, unrestricted OPEN recovery, lease extension as an identity repair, and private video/Glass/coordinate conditions.
- Preserved contracts: one generic detector, bounded current-candidate provenance, initial EMPTY entrance, independent Oil/Foam, fail-closed ambiguity, no carried/interpolated observations, verified physical IDs before motion and unchanged drain direction/progress/entrance/expiry bounds.
- Difference from prior failures: new local raster witnesses must establish spatial interface identity before support, association and ownership; direction-neutral observation is a separately gated proposed phase. It explicitly changes the old assumption that initial-FULL numeric admission requires drain evidence, without calling a stationary row a drain release. F05/F08 negative controls remain mandatory and this extension is not enabled or accepted by this document.
- Logic-map impact: NONE — the map describes executing R22; this proposal names future changes without representing them as implemented.
- Failure-registry impact: NONE — existing failures constrain the proposal; the proposed stationary-interface extension requires its own acceptance evidence before any current contract is revised.
