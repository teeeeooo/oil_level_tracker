# S11-R6 Checked-Video Reconciliation

## Responsibility

This diagnostic records the source-image decisions behind the R6 local result.
It is causal support, not current milestone authority. Current sequencing lives
in the [work plan](../../00-project/work-plan.md), the behavior contract in the
[R6 architecture](../../20-architecture/s11-r6-optics-aware-observation-architecture.md),
and completed results in the
[R6 evidence record](../../60-evidence/s11/s11-r6-optics-aware-observation.md).

## Images reviewed

The review used the checked-in MP4 and matching Recipe/truth files, not generated
scores as an oracle. Source ROI contact sheets and final report overlays were
inspected for:

- sample3 `30.03–67 s`, including empty/inflow, turbulent material, the high
  cap, unresolved/full interval and the black/reframe barrier;
- sample3 later recovery/drain anchors through `105 s`;
- sample4 early Foam-absent material boundary and the later white/turbulent
  interval; and
- Base's short checked-in interval containing weak optics and encoded colored
  explanatory strokes.

Generated bundles under `sample/output/s11-r6-optics-aware/` are ignored
forensic output. The reproducible authority is the MP4 + Recipe + truth + source
code + `tests.diagnostics.s11_r6_observation_replay`.

## Sample3 visual finding

Direct review supports a material boundary around source Y `325 px` at
`30.03 s`, rising toward roughly `241–245 px` by `35.5–38 s`. A moving
dark/yellow high cap remains visible near `229–250 px` through approximately
`49 s`; it is not the fixed lower artifact assumed by an older R4 guard. From
about `50–63.5 s`, the raster is full/turbulent enough that a numeric interface
is not supportable. The later black/reframe region around `67 s` is also a hard
UNKNOWN barrier.

The R6 graph reflects those distinctions: observed rise/high runs are solid,
the unsupported intervals contain no CSV/event coordinates, and the report's
dashed connector is display-only. The graph therefore communicates the likely
physical flow without asserting interpolated detector truth.

## Static collision exposed during cleanup

The first R6 candidate implementation accepted one controlled pair whose pixels
were identical but whose hidden labels were “glare” and “Oil.” Five identical
frames were enough for the supplemental material path to become an anchor. That
violated the observability contract and was treated as a detector defect rather
than a stale-test mismatch.

A first repair lowered material-texture anchor authority. It rejected the
collision, but reduced sample4 from `89/113` to `80/113` numeric observations
and created a false unavailable tail from approximately `46–56 s`, despite the
visible boundary annotations. That variant was rejected.

The accepted repair preserves the lower static conflict limit and permits a
bounded higher-conflict material boundary only when registered,
exposure-compensated internal raster change is present. Results:

- the repeated pixel-identical collision pair remains `0/10` numeric;
- sample4 returns to `89/113` with the prior reviewed fingerprint;
- sample4 truth-anchor MAE remains `4.0 px`; and
- all ten evaluated Foam-absent sample4 annotations remain Foam-negative.

This is not Foam authority over Oil. The registered change is copied as generic
same-frame material evidence; Oil/state and Foam still resolve independently.

## Claim boundary

The secure Windows Base/Accum video is unavailable in this checkout. Nothing in
the local sample review proves that R6 rejects the private Base caustic or
acquires the private Accum rise. Those remain explicit field holdout questions.
