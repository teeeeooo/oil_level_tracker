# D2 ordered-column clearance and first image interpretation

**Result:** measurement complete; useful spatial contrast, no classifier or
production promotion. **Checkpoint:** f1260 local protrusion interpretation
requested from the user. The [Work Plan](../../00-project/work-plan.md) owns current
state. [O2 acceptance](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance)
remains unmet and Windows disposition stays `FIELD FAIL`.

## Image inspection and ownership

The user authorized the assistant to inspect images first and request only
ambiguous judgments. The assistant inspected existing original crops at all seven
A2 anchors, the three target/wrong-target reference displays, and then original
f1259/f1260/f1261 pixels for the local ambiguity below. This is **assistant visual
interpretation**, not a new human label or independent physical truth.

At f1200/f1260, the wrong-target references lie near lower bands, spatially apart
from where the upper texture ends. This observation does not settle their cause:
the prior human result remains f1200 **UNRESOLVED**, f1260 lower rim **TENTATIVE**.
The f1320 human contact reply and f1275/f1320 A/B material judgments remain closed.
No region/material label is transferred to other frames or whole sectors.

Existing `oil_material_path.material_layer_context_features` and
`_terminal_material_partition` already summarize material rows. Side-LBP and
region-residual diagnostics already compare side appearance. The new measurement
extends the same saved-edge diagnostic owner with **ordered per-column first-edge
distances**, which those summaries do not retain. It neither segments a physical
region nor repeats the failed exact T-arm representation.

## Frozen measurement and execution

Source/tests/design were frozen at `48f89da` before numeric readout. The
[design contract](../../20-architecture/s11-interface-observability-witness-architecture.md#ordered-column-clearance--fixed-v1-preflight)
pins the local preflight SHA-256
`a619a609f6a11744ed622f4ab556d9c641848a418cdcae1d22bccde0e78125f7`.
The [machine receipt](2026-10-08-d2-column-clearance.json) preserves the exact HEAD,
55 input/source pins, runner/output hashes, reviewed summaries and display binding.
Detailed artifacts remain in `sample/output/s11-d2-column-clearance-20261008-001/`.

For every original sector column, record edges in |Y−reference|≤b, then scan
outwards above/below until an edge, mask or crop boundary. Missing reference bands
are unavailable; masked/crop-ended rays are censored lower bounds, **not** measured
edge distances. No reference Y is moved. All original b=3/6/9 scales are retained;
native geometry takes precedence without filling missing native sectors.

All 153 candidates were measured before loading validated frozen truth. Descriptive
joins retain 7 targets, 3 wrong targets and 143 unreviewed candidates. The run used
2,031 unique views and took about 0.73 s locally. All 55 input/source pins match
before/after; no video decode, detector rerun, prediction/scoring or label edits.
These already inspected images are exposed regression, not calibration or holdout.

## Primary f1320 relation

The fixed source-X interval is [566,625). Each row below uses columns where both
outward rays hit an observed edge; all these columns also have an edge somewhere
in the reference band. Δ is distance to the lower edge minus distance to the
upper edge. Positive Δ describes more edge-free space below, not empty material.

| Reference | b | Observed reference columns | Both edge hits | Below farther / equal / above farther | Median Δ px |
|---|---:|---:|---:|---|---:|
| idx9 target | 3 | 59 | 57 | 56 / 1 / 0 | +11 |
| idx21 wrong target | 3 | 59 | 59 | 26 / 5 / 28 | 0 |
| idx9 target | 6 | 59 | 57 | 54 / 1 / 2 | +7 |
| idx21 wrong target | 6 | 59 | 59 | 39 / 2 / 18 | +4 |
| idx9 target | 9 | 59 | 57 | 50 / 1 / 6 | +6 |
| idx21 wrong target | 9 | 59 | 56 | 39 / 7 / 10 | +4 |

This represents a spatial contrast that the exact-arm marker missed. Two lower
rays at idx9 are censored at every scale; three upper rays at idx21 are censored
at b=9. Those columns are excluded from Δ, with their lower bounds retained.
Columns and scales are correlated measurements, not independent success trials.

## Preserved controls and overlap

For the full original geometry of each reviewed candidate, medians below use only
columns with a recorded band edge and two observed ray-edge hits. Each cell shows
**median Δ (paired-column count)**. Different native/center extents and missingness
remain explicit; these medians do not define a candidate decision.

| Frame / candidate | Existing role | b=3 | b=6 | b=9 |
|---|---|---:|---:|---:|
| f1140 / 9 | target | +9.5 (56) | +7 (63) | +6.5 (64) |
| f1200 / 4 | target | +13.5 (70) | +11 (74) | +10 (73) |
| f1200 / 10 | wrong target | −15 (67) | −15.5 (62) | −9 (53) |
| f1260 / 4 | target | +4 (71) | +12 (71) | +12 (72) |
| f1260 / 15 | wrong target | −18 (43) | −15 (35) | −8.5 (30) |
| f1275 / 12 | target | +4 (63) | +3 (68) | +10 (69) |
| f1320 / 9 | target | +9 (67) | +6 (68) | +4 (68) |
| f1320 / 21 | wrong target | 0 (69) | +3.5 (64) | +4 (57) |
| f1485 / 19 | target | +19 (61) | +17 (64) | +16 (64) |
| f1560 / 20 | target | +16 (47) | +17 (69) | +16 (70) |

The two lower wrong-target references have the opposite distance ordering. The
pink f1320 reference shares positive ordering at larger scales: at b=6 its median
exceeds f1275's target; at b=9 it equals f1320's target. Therefore a simple positive
median or a retrospectively selected scale is not a justified discriminator.
No source-family, location, chosen sector, nearest-Y or threshold rescue follows.
The positive pattern across the seven targets is an exploratory clue, not recall
or O2 success. Optical copies and genuine plain interfaces remain opposing controls.

## One unresolved local shape and user checkpoint

The f1260 target at saved reference Y839 has a bright downward protrusion within
source X[581,605), Y[839,848). At b=3, for example X584 has an upper ray edge at
Y825 and a lower edge at Y844, so Δ=−9; X600 has Y829/Y844 and Δ=−5. The columns
immediately outside this feature can have large positive Δ. These are saved edge
locations, **not** physical contour labels.

The assistant's original-pixel inspection cannot determine whether the protrusion
is part of the fluid's irregular boundary/bubble geometry, an overlapping optical
pattern, or mixed. Three adjacent frames span only 0.067 s and do not settle it.
The prior f1260 target binding is unchanged; the question is not a repeat Oil-Y
review or an attempt to relabel the earlier lower wrong target.

`f1260-protrusion-review.png` shows an unannotated original, the same original with
a display-only cyan box and orange reference, saved Canny, and three unenhanced
nearest-neighbour original zooms. Input/script/output hashes are in the display
receipt. No private Windows image or file transfer is requested.

**Question sent:** does the bright protrusion inside the cyan box belong to the
fluid boundary's actual irregularity/bubbles, to overlapping glass/reflection
patterns, or is it unresolvable from this material? The answer affects whether
an additional lower edge is geometry to preserve, an optical counter-control,
or an unresolved component. Pending that answer, do not add a lower-edge veto,
ignore the protrusion, snap the reference, or proceed to a classifier. A response
will remain qualitative; it does not create pixel masks or scalar tolerances.

## Verification

37 focused tests pass: the original 19 arm contracts plus 18 new clearance
contracts. They cover direction ordering with equal edge counts, mask interruption,
crop censoring, plain boundaries, no-edge reference bands, fractional coordinates,
input immutability, bounds and identical optical/fluid raster counterexamples.
The unchanged frozen reader validates the real entry-path packet/snapshot joins.
Governance, documentation links and whitespace checks accompany publication.
No production behavior, report, Windows acceptance or independent temporal claim
is made by this diagnostic.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: no new production first cause is established. The new spatial readout has scale-dependent overlap and an unresolved local protrusion before any classifier/authority stage.
- Logic-map impact: NONE — ordered ray geometry is an offline extension of the saved-edge diagnostic owner; production control flow and physical authority are unchanged.
- Failure-registry impact: NONE — the experiment preserves known geometry/optical ambiguity and no-retuning constraints; it proves no new field cause or accepted correction.
