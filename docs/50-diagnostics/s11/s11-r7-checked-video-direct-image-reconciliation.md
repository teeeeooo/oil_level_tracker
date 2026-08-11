# S11-R7 Checked-Video Direct-Image Reconciliation

**Status:** `COMPLETE — LOCAL CORPUS ONLY`

## Scope and oracle

This diagnostic records the direct-image review that shaped the R7 implementation.
It is causal evidence, not the current project gate and not a detector-accuracy
claim. Current sequencing remains in the
[work plan](../../00-project/work-plan.md); completed validation is recorded in
the [R7 evidence](../../60-evidence/s11/s11-r7-evidence-tiered-trajectory.md).

The oracle order was:

1. decoded source frames inside the configured Glass ROI;
2. checked `.oiltruth` points and blind provisional annotations;
3. final overlays, graph, events and captures; and
4. aggregate counts/fingerprints only as deterministic regression alarms.

No sample name, video hash, Recipe identity, truth row or reviewed timestamp is
used by production selection logic.

## Directly reviewed sequences

### Sample3, `30.03–105 s`

Frames at approximately `30.03`, `34.53`, `38.03`, `60`, `67`, `92.53` and
`101.03 s` were inspected against the configured ROI and final graph.

- The early physical trajectory enters near source Y `316–325`, rises toward
  `~240–260`, contains bounded turbulent/Foam material and then loses a
  defensible visible interface.
- The black/reframed raster near `67 s` is unavailable, not FULL/EMPTY or Oil.
- A later draining trajectory reappears near source Y `309` and proceeds toward
  `~360`; it is a separate observed run rather than an interpolated continuation
  of the early trajectory.
- R7 retains two bounded public Foam episodes in the early run. It does not claim
  frame-complete Foam or FULL observation through the visually difficult middle
  interval.
- The report connects the two finite Oil runs only with a lower-emphasis dashed
  display bridge over an explicitly unavailable band. No intermediate CSV value,
  event coordinate or capture guide is created.

The accepted output therefore communicates entry/high/Foam and the later drain,
but remains conservative through `37.54–92.03 s`. That gap is a known local
recall limitation, not proof of absent physical Oil.

### Sample4, `0–56 s`

Frames at approximately `0`, `3`, `15`, `30`, `35.5`, `49` and `56 s` were
inspected. The real meniscus occupies a narrow, slowly changing band around
source Y `~840–860` over the reviewed sequence.

Three wrong-path families were found during implementation:

1. a lower terminal/rim row near Y `882–884` at `2.5–3.0 s`;
2. a stronger internal dynamic texture partition near Y `820–836` around
   `18.5–20.0 s`; and
3. a short high partition near Y `827` at `35.5 s`.

The final R7 path censors those rows rather than interpolating over them. It keeps
the image-supported meniscus run around Y `837–857`, publishes no Foam, and
returns to `UNKNOWN_REVIEW` when later evidence cannot defend a unique row.

## Causal findings and implemented response

| Finding | R7 response |
|---|---|
| old current-frame `selected`/shadow continuity could seed final authority | completed-window resolver ignores those fields and assigns typed authority |
| two strong seed rows could lend anchor authority to a contradictory weak third row | weak-member trend compatibility is required; seed authority is not inherited |
| a strong terminal-backed row could lose to a similar ordinary row in the same frame | same-frame terminal-peer competition is evaluated before temporal path selection |
| a fixed rim and a stationary real meniscus both recur at similar Y | recurrence opposition is relieved only by candidate-local registered Oil evolution; motion never creates authority by itself |
| one-frame partition changes could become extrema | short weaker partition spikes are censored to UNKNOWN and are never interpolated |
| Oil and Foam shared a global motion cue | registered Oil motion is candidate-band local; Foam retains an independent material-motion owner |
| duplicated dark-cap rules diverged between proposal families | hard terminal-cap topology is shared in `oil_phase_topology.py` |

These are evidence and authority repairs, not globally relaxed thresholds. The
legacy raw feature name `r6_material_path` remains only for compatible proposal
schema/debug data; it carries no R6 final-selection authority.

## Remaining limits

- Sample3 Foam recall is intentionally sparse and the full/no-interface middle
  interval is not directly established by local R7 output.
- Sample4 remains unavailable after the retained run despite later visually
  plausible boundary frames; R7 prefers a gap to an unsupported reacquisition.
- The checked Base provisional annotations label early frames unclear, while two
  checked truth anchors support the retained early path. This conflict is
  preserved rather than converted into a general accuracy claim.
- The private Base/Accum Windows rasters are unavailable in this checkout. Only
  the exact pushed R7 head can resolve whether their true interfaces exist in the
  candidate lattice and whether the new authority tiers select them correctly.

If the Windows true boundary is absent from the raw candidate lattice in clear
frames, the next problem is representation/acquisition. Further score relaxation
must stop at that point.
