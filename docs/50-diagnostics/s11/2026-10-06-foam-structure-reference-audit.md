# Foam structure context and physical-reference gap

Date: 2026-10-06. Source base: `de3ef6ce5d4ddf5f9eb09d86700d53b570c50da4`.
Scope: saved rasters/metadata and pinned recipes only. No video decode, detector
run, production change, formal label edit or Windows rerun.

The [frame480 rim attribution](../../60-evidence/s11/2026-10-06-foam-edge-selection-feasibility.md#frame480-orange-c1-confirmed-glass-rim--2026-10-06)
closes the physical identity question for that displayed C1. This investigation
reuses `s11_foam_support_geometry.measure`, `_structural_support_boxes` and
`_structural_substrate_relation`; no second runtime structure owner is added.
Repository search found configured ellipse masks and artifact-template geometry,
but no registered physical rim contour for these recipes. All three recipes have
zero artifact templates. The crop ellipse cannot silently become that reference.

## Measurements and checks

All retained components from the original three-frame capture and the two-time
capture were included: five frames, 23 components and 84 ordered distinct
component pairs. All 152 read input files were hash-preserved. Captured pixel
counts/boxes agree with the label rasters; replay of the existing structural-box
and substrate helpers matches the recorded predicates for all23 components.
Configured-ellipse radial coordinates were checked under joint translation and
uniform scaling. Seventeen existing geometry controls pass, including identical
boxes with different actual support and missing/masked corridors.

For each support pixel, `rho = hypot((source_x-cx)/rx, (source_y-cy)/ry)` uses the
**configured recipe ellipse**. Pixel quantiles are descriptive geometric values,
not distances to a verified physical rim, material scores or candidate rankings.
The recipe IDs match the captures and recipe hashes match the original inventory.
No ellipse fitting, threshold search or negative-to-positive label conversion ran.

| Same-frame C2 relative to C1 | Box below gap | Actual fully visible below-support gaps | Columns within existing 12px gap bound |
|---|---:|---|---:|
| sample4:420 | −8px | 20–28px | 0 |
| sample4:450 | −4px | 22–29px | 0 |
| sample4:480 | 12px | 28–35px | 0 |

These are gaps strictly between support pixels, not between inferred physical
surfaces. At420/450 the old broad box relation reports substrate; at480 C1 is not
classified structural, so it supplies no structural box. Actual-column placement
explains why broad-box association can reject separated material support, but
removing that veto alone cannot establish a correct Foam front: earlier C2 review
contains both Foam and central structure edges. Base/sample2 C2–C1 pairs have no
common support columns; their below-gap values remain null, not zero/infinite.

| Case/component | rho minimum | median | maximum | Review scope |
|---|---:|---:|---:|---|
| sample4:450 C1 | 0.542 | 0.656 | 0.809 | confirmed rim at450 |
| sample4:480 C1 | 0.532 | 0.643 | 0.740 | confirmed rim at480 |
| sample4:480 C2 | 0.019 | 0.272 | 0.516 | human boundary points; no pure-mask truth |
| sample2:30 C1 | 0.844 | 0.869 | 0.897 | confirmed rim |
| sample2:30 C2 | 0.000 | 0.576 | 0.920 | Foam region with suspected reflection; mixed support |

The same physical class occupies different recipe-relative radii. A global
peripheral exclusion would miss the sample4 rim or risk censoring other material.
This observation rejects treating the current ellipse or a fitted radius cutoff
as physical truth; it does not prove that calibrated structure context cannot
help. It also does not label all sample2 C2 pixels as true Foam at the wall.

## Next bounded human input

Physical C1 identity is already known. The missing input is the location of the
**inside edge of the glass rim**, distinct from the configured crop ellipse and
from the already reviewed Foam upper edge. The new frame480 view requests about
6–10 approximate points on visible left/bottom/right portions of that inside
edge. Obscured parts can be skipped, or the user can state not assessable. Do not
interpolate skipped portions, fit a closed circle, infer rim thickness, generate
an exclusion mask or apply the points across frames without separate support.
This is development reference evidence, not a required new runtime calibration.

Why ask now: actual-pixel geometry has resolved the old box association issue,
and the user has established the rim's identity, but neither supplies a complete
physical rim boundary for testing structure-reference proposals. The candidate
mask is a detected subset, not a physical outline. Using the recipe ellipse or
that mask as the outline would substitute an unverified proxy for the missing
reference. Preserve sample2's mixed/reflection qualification and the missing
Base Foam support as opposing cases in any eventual behavior repair.

The page is self-contained, preserves source coordinates, supports point undo,
JSON download and separate localStorage keyed by report hash. It does not read or
modify the previous Foam click page. Existing C1 pixels can be toggled; the
configured ellipse is off by default. No path is fitted through clicks. User
submission/attribution is supplied by the subsequent human reply, not inferred
from a browser autosave.

Safari did initially open its file chooser. The explicit **Open** action was then
completed, and fresh AX plus screenshot verified the rendered original/overlay
page. A temporary test click produced a source coordinate and was undone;
`points=[]` and count0 were verified before handoff. No test point is human truth.
Do not report success merely from entering a file URL in Safari.

## Local artifacts

Directory: `sample/output/s11-local-foam-structure-context-001/` (private, ignored).

| File | SHA-256 |
|---|---|
| `run.py` | `47f97eb94af16d05ee3709572eafd22b56bd7709e83d5bc7a500a35da16a5c06` |
| `report.json` | `8c4989c3c1dc599826d3b6b19acdaad9af946efaf1a4e90f5186838061a8e0f5` |
| `receipt.json` | `da86e9a1b6afdae9f0435d18ae0e3433e2ee0f03960d40384c9e5fd2a4ba3b90` |
| `rim-review.html` | `3449b6726663f2cdca34fe67c772b4befe91f6fe943cf80e7a148a349cbba051` |
| `review-receipt.json` | `b89259fe32f5e560fe97ca9088eb4fc9ee3ba5190037004921dd396a3e76fd5b` |

The measurement receipt pins four outputs including the runner and all152 input
files. The separate review receipt pins two inputs and the HTML/builder. Complete
per-column arrays remain local. No measured output was overwritten.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: spatial structure admission misses the confirmed narrow rim; broad-box substrate association also opposes separated material. A physical rim-reference contour is absent; removing either gate or using crop geometry alone cannot establish front identity.
- Logic-map impact: NONE — read-only saved-component/helper comparison and a local reference-point viewer have no production caller, authority or prediction output.
- Failure-registry impact: NONE — geometry-as-identity, blanket masks, global cutoffs, private Y branches and cross-material authority remain prohibited; no replacement mechanism is promoted.

FIELD FAIL / NOT_EVALUATED, O2 open and W5/O3 gated remain. No Windows work is
needed at this checkpoint. The [work plan](../../00-project/work-plan.md) owns
current state and the subsequent transition after the human reference reply.
