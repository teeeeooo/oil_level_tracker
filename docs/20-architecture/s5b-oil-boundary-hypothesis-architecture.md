# S5-B Oil Boundary Hypothesis Architecture

## Purpose

S5-B owns the durable Oil observability pipeline. It exists to prevent a physical expectation or a single strong image feature from becoming numeric Oil unless the **current observable evidence** can support a canonical boundary outcome. S11-specific accepted composition responsibilities are consolidated in [`s11-detector-responsibility-architecture.md`](s11-detector-responsibility-architecture.md).

## Physical truth versus observable evidence

Latent physical Oil and detector-observable Oil are different concepts. A frame may physically contain Oil while providing no uniquely identifiable current-frame boundary. Recipe state, fill-state priors, truth files and later frames cannot be used to inject a current numeric boundary.

A non-numeric result therefore means that the detector cannot safely publish a boundary under the current evidence contract; it does not mean that Oil is physically absent.

## Canonical current-frame path

The durable path is:

`raw observations → bounded proposals → semantic hypotheses → typed current observation → canonical evidence validation → serialized temporal reducer → public projection`

Each stage preserves provenance and bounded resource ownership. Numeric Oil originates only from an accepted typed/canonical boundary. Fallbacks may add evidence inside this ownership chain but may not inject a numeric result after it.

## Hard safety and ambiguity

Hard no-interface/unavailable evidence, severe glare/exclusion/border conflict and proven structural/topological invalidity remain fail-closed. Weak or observationally equivalent evidence may remain `AMBIGUOUS`; coverage is never recovered by forcing the strongest row into a boundary.

No-interface is a typed physical observation, not a numeric level. FULL/EMPTY appearance may inform downstream state reasoning only through its accepted typed owner and must not synthesize a boundary.

## Bounded representation and semantics

Observation families may represent different current-frame evidence, but proposal and semantic capacities remain bounded. Ordinary evidence retains its established ownership when additive representation is introduced; a supplemental observation must not silently evict the ordinary decision-facing evidence it was meant to complement.

Semantic scoring may combine correlated photometric/morphological evidence, but direct observability/topology invalidity stays hard. Comparative semantics may rank only candidates that remain admissible under the current hard-safety context.

## Spatial and Foam composition

Spatial positive corroboration and accepted Foam/Oil context are S11 responsibilities layered on this same S5-B pipeline, not alternate publication systems. Their accepted durable contract is owned by [`s11-detector-responsibility-architecture.md`](s11-detector-responsibility-architecture.md).

In particular, accepted Foam context constrains Oil admissibility and independent evidence; it does not replace S5-B with a second semantic authority stack. A hard-invalid Foam-topology hypothesis cannot obtain authority indirectly through comparison or anchoring.

## Serialized temporal ownership

There is exactly one serialized production owner for S5-B temporal state after current-frame canonical evidence. All Glass-local frame reductions, Glass reset, global reset, temporal snapshot and state-count operations enter one owner-defined total order; different-Glass temporal mutation parallelism is not a production requirement.

The owner holds one immutable store value containing Glass-local immutable records. A missing record denotes the canonical initial state without creating live state. A successful mutation prepares the complete replacement store first and then replaces the live owner-state reference exactly once. No field-by-field live mutation, external commit phase, rollback protocol, per-Glass lock graph, lifecycle barrier, generation/CAS token or second temporal store is part of the accepted architecture.

The closed responsibility family is conceptually:

`RunOilFrame → ResetGlass → ResetAll → ReadSnapshot → ReadStateCount`

An ingress sequence defines deterministic ordering for concurrent callers. Re-entry from an active owner command is rejected before enqueue/mutation rather than waiting on the same owner.

For an Oil frame, the sole authoritative sequence is:

`evidence construction → canonical evidence validation → fixed reducer → reduction/store invariant validation → complete replacement-store preparation → one state-reference replacement → return the already prepared canonical outcome`

The fixed reducer creates the decision, next record, canonical outcome and tracker/smoothing actions coherently from one prior record. It is not production-replaceable through a runner, evaluator or callback. Only an accepted boundary outcome owns numeric Oil; accepted no-interface/unavailable/ambiguity/reacquisition-pending outcomes preserve their own non-numeric semantics.

Any failure before replacement leaves the exact prior store unchanged and returns the canonical failure behavior: no numeric Oil or selected candidate, tracker `NO_UPDATE`, smoothing `PRESERVE`, no legacy fallback and no post-failure promotion. There is no load-bearing validation or failure conversion after the successful state replacement.

Detector projection is one-way. Downstream code may project the already accepted closed outcome, but it cannot reread temporal state, independently reject a committed outcome, select a raw candidate after canonical publication or inject a numeric Oil result.

Result-layer interpolation, offline trajectory estimation and retrospective initial-state reconstruction are not part of the current production S5-B contract. Any future responsibility requires separate evidence and routing through [`../00-project/retained-commitments.md`](../00-project/retained-commitments.md).

## Historical development evidence

The former mixed architecture/performance chronology is preserved as [`../60-evidence/s11/s5b-oil-boundary-hypothesis-history.md`](../60-evidence/s11/s5b-oil-boundary-hypothesis-history.md). Exact frame counts, repair chronology and audit status in that record are historical evidence, not current architecture truth.
