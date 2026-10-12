# P2 — ordered row-distribution feasibility

**Preflight:** frozen before real comparison; no production consumer.
The product problem is false Oil anchor admission despite retained lower
observations. This pilot tests a distinct optional-reference capability before
changing that authority: can a regional descriptor tolerate rearranged grains
while preserving the difference between a reviewed Oil context and opposition?
It does not claim to fix the new public source or the application.

[Preflight](2026-10-12-p2-row-distributions/preflight.json),
[runner / CDF verifier](2026-10-12-p2-row-distributions/run.py),
and [measured synthetic positive](2026-10-12-p2-row-distributions/synthetic-readout.json)
retain the exact inputs and operation. Current state remains in
[Work Plan](../../00-project/work-plan.md).

## Mechanism and existing ownership

Extend `tests/diagnostics/s11_boundary_temporal_probe.py`, which already owns
three-reference regional comparisons. Reuse the earlier S1 runner's `load_images`
and `region` for its pinned rasters, masks, 25×25 neighborhoods and three existing
references. The old operation and its failed outcome are unchanged.

S1 used pointwise appearance/edge correspondence, which is sensitive to changing
grains. This operation instead compares each horizontal row's empirical BGR
channel populations, retaining vertical row order and the upper/lower partition.
The physical hypothesis is conditional: within a material, grain placement may
change more than its local population, whereas crossing the material boundary
changes the ordered populations. Optical textures can share these populations;
this remains appearance preference, not physical identity.

Unlike earlier pooled LBP persistence, it uses the actual BGR distributions of
reviewed competing regional exemplars and keeps each row separate. Unlike the
closed BGR mean measurement, it retains within-row distribution shape. Horizontal
arrangement and cross-channel joint dependence are discarded; that can increase
false matches and is an explicit failure risk, not proven invariance of real Oil.
The **same-support row-mean ablation** tests whether distribution shape adds any
useful information beyond means. There is no translation/warp search, candidate
snapping, new reference or source-specific inference branch.

## Frozen operation and positive reachability

Use rows0–10 and14–24 of each 25×25 patch, leaving a three-row center gap.
Intersect visibility across query and all three references at the same local
coordinates. Every retained row needs at least eight common columns; otherwise
the whole comparison is unavailable, with that row retained in the record.
No source pixel or missing edge is invented. Existing candidate Y determines the
context; fractional Y retains both floor/ceil contexts and requires agreement.
These are regional bindings, not reviewed exact contours or pure material masks.

For each image, subtract one BGR offset equal to the average of its 22 row means.
For each row/channel, sort those centered common samples and take the mean
absolute paired difference. Divide by510 and average equally over channels/rows.
Centered samples lie in[-255,255], so the cost is in[0,1]. The ablation replaces
sorted distributions with each row's centered channel mean on the same support.
A unique best cost≤0.05 and role margin≥0.01 yields appearance preference; exact
or near ties≤1e-12 and missing comparisons remain unresolved. Constants are fixed
pilot choices, not a calibrated runtime operating point.

The actual synthetic operation measures a shuffled interface population plus
unclipped BGR illumination offset. It yields interface cost0, texture cost
`(24/25)*40/510`, and structure cost `(24/25)*80/510`. All three references have
identical row means, so the ablation ties. Thus an intended positive can reach the
acceptance region; no hand-written feature vector substitutes for measurement.
Thirty-two focused tests pass, including the unchanged S1 tests, independent
empirical-CDF arithmetic, common-mask/unequal-count support, side order, additive
offset, copied-opponent ambiguity, missing references and input preservation.

## Real progression and scope

First compare only the existing **same-frame f1320** confirmed Oil context
(candidate9/Y844) and reviewed wrong target (candidate21/Y822), using unchanged
S1 initial/interface, structure and internal-texture references. These two must
receive interface and opposition appearance preferences respectively, while the
row-mean ablation fails at least one, before the remaining twelve S1 queries run.
A failure closes this operation without a cutoff/window/reference search.
This minimal capability requirement does not demand zero error in every video.

All six other public-source groups remain explicitly unavailable to these
sample4-specific exemplars. The new public compressor anchor also lacks a
separate same-scene initialization set: its reviewed location is not reused as
both training context and independent success. No new human label is requested.
All examples are exposed development, with no untouched holdout claim. A passing
pilot still needs broader controls, workflow-impact acceptance, and the existing
O2/V5/O3 boundaries before any typed evidence can affect production. Foam research
remains independent. No source decoder, application replay or Windows run occurs.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: current public-source evidence locates wrong completed Oil anchor admission; whether this separate regional population operation can distinguish existing Oil/opposition contexts is unmeasured before the frozen real trial.
- Logic-map impact: NONE — extends only the existing offline regional-comparison helper; no runtime caller, coordinate, material gate or selection changes.
- Failure-registry impact: NONE — existing identity, cross-material and tuning failures govern this finite hypothesis; no new field cause or remedy is asserted.
