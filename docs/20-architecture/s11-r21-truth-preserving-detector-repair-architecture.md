# S11-R21 Truth-Preserving Detector Repair Architecture

**Status:** `IMPLEMENTED LOCAL CANDIDATE — WINDOWS QUALIFICATION REQUIRED`

## Purpose and authority

R21 is a bounded successor to the accepted R20 behavioral baseline. The source
base for this repair is `d50c14300b6e0d5be6c03c4487d96c4032fa7857`.
It owns three bounded behavior corrections, two controlled validation surfaces,
and one additive decision-witness surface:

1. initial-`FULL` slow-drain release may use bounded recent physical trajectory
   evidence without changing the established tracklet confirmation contract;
2. an established drain phase may close a rapid refill through either its
   same physical owner or one unique freshly confirmed topward owner, without
   copying tracklet identity or coordinates;
3. Foam stable-layer formation restores the reviewed bounded three-observation
   witness while retaining the segment-level dynamic gate;
4. R20-scale Base and initial-`EMPTY` Accum controls exercise the existing
   physical lifecycle without interpolation or private-field tuning; and
5. bounded Oil/Foam decision witnesses serialize already-computed owner,
   predicate, row/member and selection results without detector authority.

Runtime identity is `opencv-phase-detector-r21-truth-preserving-detector-repair-v1`.
Completed Oil/sequence and lifecycle diagnostics use
`r21-truth-preserving-detector-repair-v1`; the R20 schema remains the readable
legacy predecessor.

## Tracklet evidence contract

`DirectedInterfaceTrackletBuilder` keeps the established confirmation-witness
fields unchanged: `tracklet_direction`, `tracklet_net_progress_px` and
`tracklet_directional_agreement` retain the bounded witness that admitted the
physical tracklet. R21 does not reinterpret those fields globally.

R21 adds three diagnostic/transition fields computed from the bounded recent
confirmation window at each observation:

- `tracklet_recent_direction`;
- `tracklet_recent_net_progress_px`; and
- `tracklet_recent_directional_agreement`.

If an earlier observation was admitted retrospectively but does not yet have
enough local observations to form a recent window, the recent fields fall back
to its already-confirmed witness. This preserves fixed-lag retro-admission.
Once the recent window is mature, it may show a genuine physical reversal while
the original confirmation witness remains unchanged.

The recent fields are additive. They do not change row-hypothesis geometry,
tracklet assignment, authority tiers, selector scoring, ordinary drain
continuation/handoff, R20 delayed-reacquisition readiness, or publication.

## Initial-FULL slow-drain release

For a confirmed initial `FULL_NO_INTERFACE`, the coordinate-free
`FILLED_BARRIER` remains mandatory. The ordinary release predicates remain
unchanged: confirmed compatible tracklet, minimum progress, directional
agreement, top-origin entrance, complete current-row material veto, tracklet
material conflict and current material conflict.

Only the trajectory measurement used by this initial-FULL release is changed:
direction/progress/agreement come from the bounded recent tracklet evidence.
This lets a slowly emerging real interface earn release from its current local
trajectory without changing the historical witness semantics used elsewhere.
Later fill-derived barriers continue to use the established R16/R20 tracklet
fields, so reviewed Sample3 barrier and drain ownership are not reopened.

No material threshold, entrance ratio, candidate threshold or row grouping
rule changes in R21. In particular, an investigated authority-weighted
row-representative proposal was rejected because it changed Sample3 physical
IDs and broke the reviewed onset owner chain.

The R20 Windows report's `19.305343511450385 px` release minimum corresponds to
an effective Glass height of about `772.214 px`. A matching-scale controlled
lifecycle proves that individual 10 px tracklet witnesses remain below that
minimum while the unchanged bounded recovery chain accumulates the physical
2 px/sample drain and releases only after cumulative progress reaches the
existing threshold. R21 therefore does not weaken the progress threshold or
absolute recovery expiry to obtain slow-drain coverage.

## Rapid refill closure

While `DRAINING`, R21 first checks the current row of the existing drain owner.
A same-owner closure retains the bounded recent reversal contract: confirmed
compatible ownership, negative recent direction/agreement/progress, sufficient
topward span, top entrance, bounded anchor-or-motion evidence and unchanged
strict material support.

A high-speed physical refill can legitimately exceed the ordinary downward
tracklet jump and form a new tracklet. After same-owner continuation and any
ordinary downward successor fail, R21 therefore permits one phase-level refill
handoff without merging physical IDs **only when the current drain owner is
absent from that frame**. A present old owner cannot lose phase ownership merely
because its current row fails the downward-continuation predicate; this prevents
an unrelated upper tracklet from stealing an active drain. The fresh row must
independently prove:

- a bounded confirmed compatible tracklet distinct from the drain owner, while
  that old owner has no current-frame row;
- negative recent direction, ordinary agreement and minimum progress;
- topward displacement from the last accepted drain row of at least the
  existing fill-span minimum and presence inside the existing top band;
- `ANCHOR_ELIGIBLE` authority **and** the existing strong registered
  motion/coverage witness; and
- unchanged strict current/history material support.

Exactly one qualifying fresh owner closes to `FILLED_BARRIER` with
`DRAIN_REFILL_HANDOFF_CONFIRMED`; multiple qualifying owners fail closed with
`DRAIN_REFILL_HANDOFF_AMBIGUOUS`. The new tracklet ID is appended only to the
phase owner history. No old tracklet observation, ID, velocity or coordinate is
copied. The closing row remains one selected same-frame candidate; later
no-interface frames remain nonnumeric.

## Foam stable-layer correction

R21 retains the four-frame-offset / 2.0-second witness horizon, association,
material/coherence/static gates, dynamic-frame ratio, final-Oil alias handling
and the directed-front branch.

For the stable-layer branch, the segment-level acceptance gate still requires
at least two dynamic observations. Formation support then requires either:

- at least three bounded same-layer observations total, allowing a third
  locally stable extent-changing observation after two dynamic rows; or
- the existing exactly-two-observation exception, where both rows are dynamic
  and meet the substantial area/width footprint.

A static row cannot bootstrap a segment because the independent segment gate
still requires two dynamic observations. Static top rows, descending residue,
long stale preludes, one-motion spikes and narrow two-frame residue controls
remain rejected.

## Initial-EMPTY controlled behavior

R21 adds no Accum-specific production condition. A controlled initial-`EMPTY`
sequence proves the existing lower-entry owner can track a slow 5 px/sample
rise, leave an explicitly unavailable frame nonnumeric, resume on fresh
same-frame evidence, complete the fill barrier and preserve selected-candidate
provenance. Faster synthetic steps that create competing high-recall physical
hypotheses remain fail-closed; R21 does not widen row grouping or ambiguity
thresholds to make that fixture numeric.

Private Windows observations remain a separate qualification surface. Missing
field candidates cannot be repaired with carry, interpolation, snapshot Y,
reviewed coordinates or a video-specific lane.

## Additive decision-witness observability

R21 activates the retained R20 decision-witness concept as behavior-neutral
telemetry. It does not execute extra detector branches. `OilPathLifecycleOwner`
already builds separate physical-phase and publishable-selector layers; R21
records their actual row memberships rather than recomputing confidence or
publishability. Per-frame Oil witness data joins bounded refs to row hypothesis,
tracklet, authority, phase-admission membership, publishable membership,
allowed owner IDs, selected same-frame member and the already-computed
`direct`/`recovery`/`delayed` predicate records.

Predicate results are normalized to explicit `true`/`false`; a branch that was
not visited is `NOT_EVALUATED`, and a genuinely absent legacy/schema field is
`UNAVAILABLE`. These statuses are trace semantics only. Foam uses its existing
bounded segment/window evaluations and records candidate/track identity,
formation branch/predicates, Oil-alias result and final confirmation outcome.
At most eight per-frame Foam window records are serialized; truncation is
explicit. Oil refs are already bounded by the detector's candidate caps.

The nested schema is `r21-decision-witness-v1`. Because the debug trace final
snapshot already serializes all `sequence_*` metrics, the witness is attached
to the normal sequence annotation without rerunning detection. Runtime output,
selected candidate, phase, events and CSV remain independent of trace capture.

## Preserved invariants and field boundary

- One generic detector serves every Glass; no filename, timestamp, Glass ID or
  reviewed Y enters detector control flow.
- Every numeric Oil/Foam result is one selected same-frame candidate.
- Existing material conflict, ambiguity, jump, loss, handoff and publication
  contracts remain fail-closed.
- Foam remains independent of Oil except for the existing final same-frame
  alias comparison.
- Graph/report/CSV layers do not repair missing detector observations.
- R21 local acceptance is not Windows field qualification. The latest Windows
  disposition remains `FIELD FAIL` until the canonical target replay passes.

## History Review

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-DRAIN`,
  `OIL-SELECTOR`, `FOAM-EPISODE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`,
  `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R10/R11 motion-bootstrap overreach, R16 directed
  identity/reciprocal assignment, R18 FULL barrier and Foam formation, R19
  bounded release recovery, R20 delayed readiness/local Foam windows, the
  transferred R18 Windows causal closure, and the checked Sample3 owner/barrier
  truth.
- Prior mechanisms rejected: global threshold or entrance widening,
  motion-only anchor authority, snapshot/coordinate carry, private
  video/Glass/time branches, identity merge across rapid refill, and changing
  the Sample3 Foam oracle to fit later output.
- Preserved contracts: one generic detector, coordinate-free FULL/EMPTY
  barriers, distinct physical tracklet IDs, bounded ambiguity/loss/recovery,
  two-sided Foam dynamics, selected same-frame Oil/Foam publication and exact
  trace/CSV provenance.
- Difference from prior failures: R21 changes only explicit bounded lifecycle
  witnesses/transitions and behavior-neutral telemetry. R20-scale slow drain
  remains covered by the existing recovery threshold/expiry; fresh refill may
  transfer phase only after old-owner absence and independent new-owner proof.
  Private Windows effectiveness remains unproven.
- Logic-map impact: UPDATED — the current implementation map now names R21
  recent trajectory, rapid-refill phase handoff, corrected Foam stable witness,
  and decision-witness trace behavior.
- Failure-registry impact: UPDATED — the durable registry records R21 as the
  current local candidate and the new anti-identity-leak/no-field-claim guards
  while retaining all earlier failure evidence.
