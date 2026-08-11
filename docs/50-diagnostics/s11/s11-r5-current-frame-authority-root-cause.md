# S11-R5 Current-Frame Authority Root-Cause Record

## Responsibility

This record explains why the latest secure-Windows R4 result reopens the detector architecture and why another threshold/rejection patch is not the selected repair. Current sequencing belongs to the [work plan](../../00-project/work-plan.md); behavior and acceptance belong to the linked [R5 architecture](../../20-architecture/s11-r5-sequence-first-trajectory-architecture.md) and [validation contract](../../30-validation/s11-r5-sequence-first-trajectory-validation.md).

## Latest secure-Windows evidence

Direct visual review reports:

- Base starts `FULL_NO_INTERFACE`, contains no Foam, later exposes a descending boundary from the top, reaches a physical low and recovers;
- Accum starts `EMPTY_NO_INTERFACE`, later admits Oil from the bottom, has a bounded turbulent Foam interval, reaches a high and drains;
- R4 yields only `157/601` valid Base samples and `69/601` valid Accum samples;
- `UNKNOWN_REVIEW` occupies `71.9%` of Base and `87.0%` of Accum;
- Oil publication is about `9.7%` and `8.0%` even though roughly ten candidates are generated per frame;
- Base glare/residue remains raw Foam-like with a nearly constant score around `0.826–0.868`; and
- an incorrect lower candidate and the first point after long gaps can control extrema and event timing.

R3/R4 rejection layers reduced some false public Foam, but did not change the underlying evidence or the authority ordering. Rejected Foam continues to dominate diagnostics, weak Oil candidates still compete frame by frame, and the serialized temporal owner receives only the already reduced current observation.

## Earliest architectural loss

The production boundary is currently:

```text
many current-frame hypotheses
  -> current-frame semantic winner / ambiguity
  -> one canonical observation
  -> serialized temporal reducer
```

The temporal reducer cannot compare the candidate at Y=A in this frame with alternative candidates at Y=A in adjacent frames after current-frame semantics has discarded them. It can preserve or reacquire only the canonical current observation. Consequently:

- repeated frame-local ties become long UNKNOWN gaps;
- a fixed high-scoring artifact can repeatedly re-enter as the only canonical candidate;
- continuity cannot rescue a visually weak but consistent meniscus;
- initial FULL/EMPTY is treated as a short-lived tracker state rather than a sequence prior; and
- event code sees disconnected accepted points and assigns physical meaning to a sparse first/last point.

This is a responsibility-ordering defect. Lowering candidate thresholds would increase both true paths and false artifact paths without giving the system a way to distinguish them.

## Repository-local corroboration

The checked-in sample3 blind visual record covers the useful empty/inflow/agitation/full transition. Earlier hypothesis audits found correct-range material representation in most clear visual anchors even when final numeric Oil was absent. Direct image review also shows that later accepted full-state positions can lie on a dark Glass cap, demonstrating that temporal consistency of accepted values alone is unsafe.

The previous offline temporal probe accepted only production-published anchors and attempted a tightly bounded linear bridge. It recovered too little and could reinforce a persistent wrong boundary. It therefore does not refute sequence reasoning over the pre-selection candidate lattice; it refutes interpolation over already committed output.

Local validation has three known blind spots:

1. thirteen sparse truth points do not describe complete transitions;
2. exact output fingerprints preserve wrong output as readily as right output; and
3. synthetic negatives prove bounded mechanisms but do not reproduce private optics.

R5 keeps those assets as regression evidence and adds dense source-image review as the physical oracle.

## External-design reconciliation

The existing implementation-reference review supports the selected direction:

- constrained path/curve work treats a material interface as a spatially coherent path rather than a single strongest row;
- multi-line level measurement rejects local bubbles/droplets through cross-location agreement;
- adjacent-frame differencing supplies evidence that fixed vessel appearance lacks; and
- transparent-container benchmarks show that uncontrolled reflection/refraction remain first-class competing causes.

These sources do not provide transferable constants or prove Foam from motion alone. R5 uses them only to assign responsibilities: current frames generate material alternatives; temporal sequence reasoning compares those alternatives; static/motion evidence opposes artifacts; UNKNOWN remains available.

## Why incremental R4 tuning is rejected

The following proposed changes do not address the earliest loss:

- raising Foam score/whiteness removes real dark or chromatic Foam together with false glare;
- lowering Oil confidence/ambiguity increases fixed-edge selection;
- changing Hough/Canny weights creates more candidates when about ten already exist;
- a hard bottom-row penalty encodes one private symptom and can remove a real low interface;
- stronger Foam authority worsens Oil/state corruption; and
- numeric interpolation makes a smooth graph without proving the physical path.

The selected repair is a bounded architectural replacement at final-analysis authority, not a greenfield image detector. Existing proposal/evidence generation remains reusable and can be separately improved only if the R5 representation audit proves it insufficient.

## Claim boundary

The private Windows raster cannot be reproduced locally. R5 may be implemented and locally qualified against the four checked-in videos, but only a new secure-Windows replay can establish whether the Base/Accum failure is closed. The Accum narrative itself contains conflicting Foam onset timestamps (`492 s` and `672 s`); neither is runtime or tuning truth until direct review resolves it.
