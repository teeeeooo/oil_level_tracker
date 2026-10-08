# D2 ordered-column clearance and first image interpretation

**Result:** measurement complete; useful spatial contrast, no classifier or
production promotion. **Checkpoints:** f1260 local protrusion identified by the user as a glass-pattern
lower semicircle; 0/28 s correspondence closed as Foam-obscured. The subsequent
recipe-workflow audit below records an existing input omitted from this capture.
The [Work Plan](../../00-project/work-plan.md) owns current
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
or an unresolved component. This initial checkpoint was answered below. Its safeguard remains: do not add
a lower-edge veto, ignore the protrusion, snap the reference or proceed to a
classifier from a qualitative reply. No pixel masks or scalar tolerances follow.

## Human reply and existing static-reference audit

The user replied **“유리 무늬·반사 등이 겹친 것”**, then clarified
**“glass 특유의 원형 무늬의 아래쪽 반원”**. Close the f1260 protrusion question:
the displayed feature is the lower semicircle of a glass-specific circular
pattern, not evidence that the true target boundary has a downward fluid bulge.
Do not mark the entire cyan rectangle as artifact, transfer this reply to nearby
candidates (including idx5/Y844), or erase edges from the input. Genuine target
and optical feature coexist; a first lower-edge hit may belong to the latter.
The original machine/display receipts retain their historical pending bytes;
this section and the Work Plan own the resolved first checkpoint.

The follow-up [optical-reference receipt](2026-10-08-d2-optical-reference.json)
records a read-only check of existing opposition. At the 42 s review box all
216 pixels are effective and none is in the saved glare mask. For central sector
X[584,605), existing near-below bands at b=3/6/9 have `static_available=true`,
`static_overlap=0`, and `glare_fraction=0`. The adjacent sector X[563,584) has
static overlaps 0, 0.031746, 0.047619; do not describe the whole scene as static-free.
`structural_reference_reason=vessel_fitting_geometry_unavailable` remains explicit.
The user-confirmed optical feature demonstrates that zero glare/static response
cannot certify absence of glass structure.

### Existing preparation operator reproduced

The existing schedule owner selects 0, 28 and 56 s from the 0–56 s / 2 FPS
qualification schedule. The unchanged static-prior owner forms each reference's
`preprocess.horizontal_mask`, then keeps pixels whose mean binary presence is
at least 0.75. With three successful references that requires all three. This is
the existing fixed image-processing preparation rule, not a learned model.
The glare owner covers saturation and specific elongated bright features, not
all circular glass patterns; broadening its mask is not implied here.

The bounded audit decoded these three **local sample4** frames plus the 42 s
anchor using the existing reader, geometry and preprocessing. It did not run the
Oil/Foam detector pipeline or change any setting. Relevant owner bytes match the
original A1 capture. At 42 s, reconstructed BGR/effective/Canny/normalized/glare
arrays equal the saved arrays. The reconstructed static prior matches **1,075
available stored static-overlap bands with zero mismatches**; 413 unavailable
bands are not silently assigned values. All 17 audit input/source pins remain
unchanged. This validates the recorded aggregate reconstruction, not byte equality
to an unretained historical full static raster.

| Frame / time | Horizontal-mask pixels inside the 216-pixel review box | Glare pixels |
|---|---:|---:|
| f0 / 0 s, reference | 207 | 0 |
| f840 / 28 s, reference | 132 | 0 |
| f1680 / 56 s, reference | 0 | 0 |
| f1260 / 42 s, current comparison | 71 | 0 |

The current preparation operator consequently retains **zero** static pixels in
this box: the zero-support 56 s reference prevents the required three-way overlap.
The assistant sees a more uniform appearance in that later image. Whether fluid
occlusion, illumination or another optical change caused the missing reference
edge is not mechanically established. Nor are the 0/28 s edge pixels certified as
the same glass semicircle merely because their coordinates overlap.

### Reference-correspondence checkpoint

The assistant inspected enlarged original crops at all four times. At 0/28 s,
fluid/optical structures overlap, so the specific correspondence to the 42 s
human-identified lower semicircle remains ambiguous. The new display
`sample/output/s11-d2-optical-reference-20261008-001/reference-visibility-review.png`
shows original crops and unenhanced local views with the same display box.

The user is asked **which, if either, of 0 s and 28 s permits identifying that
same glass lower semicircle**. This is a new cross-time correspondence question,
not a repeat of the settled 42 s subtype. No automatic transfer to the reference
images is made. Until resolved, do not treat either reference as a clean optical
template, lower 0.75, union the maps, add a per-Glass exclusion, or accept a
candidate using a zero static prior. A positive answer permits designing a
visibility-aware reference comparison with genuine stationary-interface and
coincident-target controls; it does not approve a mask or veto. If correspondence
is unresolvable, retain that limitation rather than choosing a convenient frame.
No Windows execution or private-file export is needed at this checkpoint.

### Reference reply and existing recipe workflow

**Human reply received, 2026-10-08:** both 0 s and 28 s overlap Foam and do not
permit clear identification of the semicircle. This closes the correspondence
question as unresolved from those images; it does not weaken the separate 42 s
glass-pattern identification. Neither earlier frame is certified as a clean
optical reference. Historical JSON/display receipts retain their original bytes.

The user also identified an existing product input: during recipe creation the
operator can inspect detector proposals and choose structures. Source inspection
at `3a45eb4bf227c62057c0b3d8a8e76853858e43d6` confirms the complete ownership route:

| Responsibility | Existing owner and observed behavior |
|---|---|
| Entry and proposal | `bootstrap.py` wires `OpenCvArtifactProposalService`; `MainWindow.open_roi_editor` supplies it and the current frame. The proposal adapter detects on a copy with templates cleared, then returns bounded boundary/glare proposals. |
| Explicit selection | `RoiEditorDialog._accept_artifact` appends only selected proposals to its working copy. Main-window Apply replaces the edited Glass and marks the recipe dirty. Unselected proposals are not saved as non-structure or fluid truth. |
| Persistence | `InspectionRecipe.to_dict/from_dict` round-trips `geometry.artifact_templates`. `ArtifactTemplate` stores ID/kind/normalized center/width/height/angle/name/note. It contains no curve samples or reference pixels. Recipe preflight context includes the templates. |
| Runtime use | `CurrentFrameEvidenceOwner.observe` checks selected Oil and Foam; the frame projector signs and checks assembled candidates. `apply_artifact_templates` marks matches rejected and retains their trace. `candidate_is_eligible` also excludes calibrated matches. This is an active rejection mechanism, not unused metadata. |

The static preparation map and user-confirmed templates are separate inputs.
`attach_spatial_signature` summarizes support near a candidate's scalar Y as
position/extent; matching does not trace the circular pattern or identify the
material covering it. A real interface at matching geometry can also be rejected.
The existing same-Y/different-X test protects a spatially separate candidate,
not a coincident fluid crossing. Nor does removing one false candidate prove that
the remaining candidate will pass physical, phase and final-selection gates.

**Exact local input inventory:** `sample/sample4.oilrecipe`, SHA-256
`53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849`, has no raw
`artifact_templates` field for `ecb6e1ec-0259-5982-a35f-7cb1f7075af2`.
The exact A1 `frames-final/capture-manifest.json`, SHA-256
`fca7623eddf3b8b199a2090a257ebab73fb4a620f2f8c50a6605ab0129045b45`, records that
Glass with `artifact_templates=[]`. Missing in the source and empty in the
normalized capture are distinguished. This diagnostic therefore did **not** test
a recipe with user-registered structures. No claim about an uninspected Windows
recipe follows.

**Assessment:** explicit structure registration can reduce the need to infer a
known artifact's identity automatically. Its practical gain remains unmeasured
here. Reuse the existing workflow first, with separate registered/unregistered
inputs and true-interface crossing controls as specified in the
[design owner](../../20-architecture/s11-interface-observability-witness-architecture.md#user-confirmed-recipe-artifacts--reuse-before-new-inference).
The qualitative 42 s judgment is not silently converted into a template, mask or
new candidate label. Source, recipe, frozen measurements and production behavior
remain unchanged; no detector rerun, new video read or Windows task was performed
for this source audit.

Focused existing tests: **23 passed, 5 deselected**, covering proposal generation,
explicit UI acceptance on a private copy, display/bulk selection/removal,
normalized recipe round-trip, legacy missing fields, geometric rejection and
preflight invalidation. Command: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m
pytest -q tests/unit/test_artifact_calibration.py
tests/unit/test_artifact_proposal.py tests/unit/test_preflight_context.py
tests/gui/test_guided_workbench_ux.py -k 'artifact or geometry or context'`.
These confirm existing contracts, not real-scene accuracy or Windows GUI behavior.

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

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: no new production first cause is established. The new spatial readout has scale-dependent overlap; the human-identified glass semicircle is absent from the reconstructed static prior because the 56 s reference has no local edge support. This explains the recorded prior, not the production final-selection first cause.
- Logic-map impact: NONE — ordered ray geometry is an offline extension of the saved-edge diagnostic owner; production control flow and physical authority are unchanged.
- Failure-registry impact: NONE — the experiment preserves known geometry/optical ambiguity and no-retuning constraints; it proves no new field cause or accepted correction.
