# S11 Behavioral Lifecycle and Foam Witness Architecture

**Status:** `IMPLEMENTED — LOCAL ACCEPTANCE COMPLETE / WINDOWS REQUIRED`

## Purpose and authority

This document is the active behavior owner for two narrowly bounded adaptations
to the existing S11 detector. It supplements the durable responsibility map;
it does not create a second detector, candidate lane, physical identity owner,
or publication path. The reviewed implementation baseline is
`119f218f2cf232e90f8e591e28feaab54f6fb42f`.
The completed local implementation, audit and final review are recorded in the
[S11 behavioral lifecycle and Foam witness evidence](../60-evidence/s11/s11-behavioral-lifecycle-and-foam-witness.md).

The delayed lifecycle adaptation belongs to
`OilMaterialPhaseLifecycleOwner`, and the bounded Foam formation adaptation
belongs to `FoamEpisodeResolver`. Existing candidate generation, typed
authority, directed tracklets, initial-state safety, direct/near release,
selector, same-frame projection, sequence composition and CSV/publication
provenance remain the authorities named by the current logic map.

No forced revision identifier is assigned. The existing detector and trace
identifiers remain readable compatibility labels. This local implementation
does not repair or qualify the closed Windows field failure.

## Behavioral scope

### Delayed drain readiness

After confirmed initial `EMPTY`, a genuine fill owner can enter the existing
coordinate-free ownerless barrier when its dynamic owner is lost. Direct
partial-fill release remains first, the existing near-snapshot recovery remains
second, and the one delayed attempt remains third after ordinary loss grace.

Before that delayed attempt is consumed, its unique same-frame anchor must
pass every existing phase, authority, tracklet, compatibility and strict
material gate plus one shared drain-readiness predicate:

- the existing confirmed/continuing tracklet direction is positive;
- its existing directional agreement is at least
  `drain_minimum_directional_agreement`; and
- its existing net tracklet progress is positive.

The predicate is evaluated by the same lifecycle helper used by
`_recovery_seed_allowed` and by the delayed seed admission record. A zero,
upward, stationary or otherwise unready row therefore leaves the attempt
available, publishes nothing and retains no candidate history. A later unique
ready anchor can consume the attempt. Multiple ready anchors remain consuming
ambiguity. A ready attempt that fails, expires or becomes ambiguous cannot be
reseeded in the same established-fill episode.

The full drain progress threshold is intentionally not required at seed time;
the existing bounded recovery chain still earns that unchanged threshold after
seeding. This adaptation applies only to delayed attempt admission, not to
direct release, near-snapshot recovery, ordinary continuation or cross-ID
handoff.

### Bounded Foam witness windows

`FoamEpisodeResolver` retains the existing eligible candidate and physical
association track. Formation authority is no longer evaluated over the whole
dynamic segment. For each evidence endpoint it evaluates the maximal suffix
of that segment whose inclusive span is no more than four frame offsets and
2.0 source seconds. Each window applies the existing material, coherence,
dynamic, static, directed-front/stable-layer and final-Oil-alias predicates.

Only same-frame members of a passing, non-aliased window are confirmed. The
confirmed set is the union of those frame IDs, deduplicated; a passing window
cannot bless a distant or aliased window merely through a shared track ID.
Missing frames remain missing. A long track may therefore contain a local
accepted suffix while its remote constant or stale prelude remains
unconfirmed. The accepted episode count is the number of maximal connected
accepted-support runs within the associated track, not the number of
overlapping windows.

The stable-layer branch counts actual dynamic observations, where each row is
dynamic only when
`min(internal_motion, dynamic_support) >= 0.15`. It requires at least three
such observations. The existing substantial two-observation exception remains
available only for exactly two observations, both dynamic, with the existing
area and width footprint. A static extent-changing tail cannot satisfy the
three-observation stable-layer rule.

The helper performs bounded backward scans over each endpoint; under one
sampled row per frame no witness contains more than five frame offsets. It
does not retain quadratic window history. Bounded per-window diagnostics are
supporting evidence only and never become detector authority.

## Preserved ownership and invariants

- Initial `EMPTY` remains a hard lower-entry physical-owner gate; confirmed
  `FULL` remains a coordinate-free barrier.
- Direct and near-snapshot release precedence and all existing direction,
  jump, loss, material, ambiguity, handoff and evidence-window limits remain
  unchanged.
- Tracklet IDs remain distinct across handoff; no row, ID or coordinate is
  copied. Candidate-only, continuation-only, provisional, unknown,
  incompatible and material-opposed rows cannot bootstrap the delayed route.
- Foam remains independent of Oil and may publish with Oil unknown. Final
  same-frame Oil aliasing remains bounded and symmetric; unselected Oil,
  broad masks and prior alias history cannot veto Foam.
- Every numeric Oil/Foam value remains a selected same-frame candidate. Oil
  selected Y, completed sequence raw Y, `TrackingSample` raw Y and CSV raw Y
  remain equal. No interpolation, carry, snapshot coordinate or retrospective
  backfill is introduced.
- `TrackingSample.oil_is_valid` and `foam_is_valid` remain independent, and
  traces remain non-authoritative provenance.

## Residual and deferred surfaces

This implementation intentionally does not widen or redesign the remaining
field-unknown surfaces:

| Surface | Disposition and activation requirement |
|---|---|
| Base release | Deferred. Requires a reviewed physical candidate/identity and a bounded owner path before any release threshold or entrance change is considered. |
| Base rapid refill after drain | Deferred separately. Requires an explicit established refill owner, top closure and suffix-safe drain-to-fill state design; no row-only reversal is added here. |
| Accum initial entry | Preserved hard lower-entry admission. Requires source-backed candidate/phase evidence before any confidence or publishability change. |
| Accum fill continuity/layered/post-Foam | Deferred. Requires physical association and material evidence; no fake coordinate or material relaxation is permitted. |
| Accum drain continuation/re-entry | Preserved strict reversal, jump, direction and material contracts; field unknowns are not tuned here. |
| Windows field qualification | Deferred and still required. The user-reported field result remains `FIELD FAIL`; no local-to-Windows PASS extrapolation is made. |
| Decision-witness observability package | Retained design-only optional work, separate from this behavior owner and not a prerequisite for the repairs. |

## History Review

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: proposal/authority starvation, motion/bootstrap overreach, initial-state asymmetry, component identity leakage, owner-loss/reacquisition dead ends, unbounded future-supported Foam episodes, Foam/Oil coupling, provenance ambiguity and global-threshold escape hatches; the R18/R19/R20 architecture and validation records, canonical reviewed truth and R20 consolidation were also reviewed.
- Prior mechanisms rejected: threshold widening, private field/time/coordinate branches, motion-only authority, ID or coordinate merging, whole-track Foam acceptance, total-row stable support, unbounded retry/window search, selector/projection repair, interpolation/carry and telemetry-only substitution.
- Preserved contracts: typed same-frame candidates, directed physical tracklets, initial `EMPTY`/`FULL` safety, bounded lifecycle and Foam association, fail-closed ambiguity/material handling, independent Foam composition and exact selected-candidate/sequence/CSV provenance.
- Difference from prior failures: delayed readiness prevents an irreversible attempt decision on a directionally irrelevant anchor without rearming a failed real attempt; local Foam windows prevent remote evidence from conferring authority on a stale prefix while retaining bounded sparse and sustained positive formation.
- Logic-map impact: `UPDATED — the current map now records the delayed drain-readiness conjunct and bounded Foam witness authority at the existing lifecycle and episode owners.`
- Failure-registry impact: `UPDATED — F07 and F08 current notes now route these constrained adaptations through the existing guarded mechanisms; no new failure class is introduced.`

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: the approved delayed repair is at delayed attempt admission after established owner loss (`OIL-PHASE-FILL`/`OIL-PHASE-DRAIN`); the Foam repair is at local episode confirmation (`FOAM-EPISODE`). Windows field effectiveness and reviewed-Y outcome remain unknown.
- Logic-map impact: `UPDATED — existing owner details and bounded diagnostic authority are revised to match the implementation.`
- Failure-registry impact: `UPDATED — existing F07/F08 guards are clarified without adding a mechanism entry or claiming field causality.`
