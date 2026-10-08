# D2 registered structure support — information boundary and design

The existing recipe selection stores a location envelope, not the selected
object's observed contour. Reconstructing two saved setup frames confirms this
information loss. A reference-support design is now specified in the
[architecture owner](../../20-architecture/s11-interface-observability-witness-architecture.md#registered-support-reference--proposed-input-contract).
Its interaction scope needs a product decision: whether recipe authors may
optionally narrow the structural portion when a proposed line mixes objects.
No detector behavior, recipe schema or UI has been changed.

## Reuse and exact scope

Source HEAD: `a239578e65fe240864dbaf2d33ebf20aeeef3687`.
Reuse the two fresh setup captures from the
[recipe comparison](2026-10-08-d2-recipe-artifact-comparison.md), the saved A1 Canny
rasters and the existing `build_mask_bundle`, `preprocess`,
`attach_spatial_signature`, `template_from_candidate` and `artifact_match_score`.
No frame detector, video reader, completed resolver, Windows task or model runs.
Fourteen input/source pins are checked before and after. Original crop pixels and
reconstructed Canny match the saved arrays exactly. All **22 Oil signatures at
42 s and 24 at 44 s** reproduce exactly; each setup inventory also contains one
Foam candidate, which is outside this Oil support audit.

The [machine receipt](2026-10-08-d2-registered-support-design.json) includes pins,
the frozen preflight, measurements and runner source. Local outputs are under
`sample/output/s11-d2-structure-support-20261008-001/`. The assistant inspected
the original and diagnostic displays. That interpretation is not a new human
pixel label. Prior target, semicircle and obscured-reference replies stay closed.

Discovery also reused the recorded structure-context audit, O1 witness geometry,
native path diagnostics, ordered-column clearance and saved Foam support geometry.
Those owners preserve raw context, sector geometry or raster positions; none
binds an operator's selected structure to exact reference support. They should
not be repurposed to invent such a binding. The real proposal/UI/recipe path is
the extension point. No additional analysis pipeline or scorer is justified.

## Demonstrated loss before matching

For Oil, `phase_frame_detection` supplies the frame's shared `horizontal_mask`
to the signature function. This is Canny after the existing horizontal closing,
not an individual candidate's native contour. In candidate Y ± 2 pixels,
`attach_spatial_signature` takes the first and last occupied X columns. It drops
interior occupancy, connectivity and pixel Y; angle is zero and height is five
pixels. `template_from_candidate` doubles the height for registration. Empty
support instead falls back to the ellipse extent. No appearance pixels, visibility
state or source-frame binding are retained in `ArtifactTemplate`.

| Saved setup candidate | Source X span | Signature band Y | Horizontal-mask pixels | Raw Canny pixels in band | Added / removed relative to raw Canny |
|---|---|---|---:|---:|---:|
| f1260 idx5, Y844 | [551,639) | [842,847) | 180 | 75 | 121 / 16 |
| f1320 idx21, Y822 | [559,636) | [820,825) | 324 | 110 | 222 / 8 |

The extra pixels are morphology output, not observed new edges. These counts
describe representation, not true/false support labels. F1260 idx5 is the earlier
unlisted Y844 proposal; it is not declared an artifact by the local semicircle
judgment and is never registered here. F1320 idx21 is the already bound false
candidate; its precise optical subtype remains unresolved.

For each saved candidate, replace the signature input by (a) only its two X
endpoints, or (b) a horizontal row at Y−2 with the same endpoints. Preserve the
candidate scalar and all non-signature features. The actual unchanged production
functions return **identical signatures and match score 1.0 in all three cases**.
The two replacement supports are synthetic controls, not purported observations.
They prove the old signature cannot recover which pixels or contour were meant;
they do not prove that a richer reference alone will distinguish fluid from glass.

## Why automatic component selection is insufficient

The prior f1260 display box X[581,605), Y[839,848) contains the user-identified
glass lower semicircle, but it is not a pixel truth mask. The saved 8-connected
Canny raster has two components touching it:

| Component | Pixels in box | Pixels outside box | Source bounding box |
|---|---:|---:|---|
| 3 | 14 | 755 | [555,804,636,877) |
| 18 | 23 | 2 | [581,841,596,849) |

The first reaches far beyond the feature into other scene edges. Within the
Y844 signature band, 57 horizontal-mask pixels are inside the display box and
123 are outside. Therefore neither the entire proposed line, the display box,
nor the whole connected component is automatically certified as structure.
The saved figure `support-information-review.png` shows this information loss
without altering the input pixels or repeating the settled subtype question.

## Resulting design and decision boundary

The bounded proposal is to retain an immutable **registration reference** at
the existing list-selection step: original local pixels, visibility and raw-edge
rasters, exact frame/Glass/geometry/proposal provenance, and the precise support
actually reviewed. Keep proposal generation geometry distinct from object
attribution; retain unresolved portions. A native sector path is not automatically
a reviewed continuous contour, and a centered scalar line supplies no such path.

Use this reference as explicit negative evidence only where correspondence and
visibility are established. A same-position match, a missing structure, an
occluded reference or simultaneous fluid/structure support cannot produce a hard
negative or positive fluid identity. Geometry-only legacy registrations cannot
be upgraded by guessing their old source image or tracing their rectangle.
Capturing a reference is a prerequisite, not a complete matcher or accepted
physical discriminator. The old production path remains unchanged pending a
separate validated challenger and acceptance.

The proposed user flow is concrete: select an existing proposal → see the
original with its actual contributing pixels/available native path → accept an
unambiguous structural portion, optionally narrow mixed support if that extra
interaction is allowed, or keep it unresolved. Cropping a region restricts where
to inspect; it does not label every pixel inside the region. No exhaustive tracing
or per-frame review is proposed. Original private-copy Apply/Cancel semantics
remain the integration boundary.

**Product question submitted:** may the recipe author optionally specify a
smaller region/contour portion when the proposal mixes structure and fluid, or
must setup remain list selection only? This changes the available input and the
user's calibration burden, so it is not an implementation detail to silently
choose. Under list-only setup, preserve the same reference/provenance, but mixed
support stays unresolved; there is no automatic whole-component fallback.
No answer is inferred from elapsed time. No dependent UI/schema/matcher work is
started while this choice is pending.

Required later controls are isolated visible structure, a true boundary away
from it, genuine crossing/stationary overlap, obscuration, mixed/disconnected
support, unavailable native path, geometry/remapping mismatch and legacy recipes.
Cross-time physical correspondence must be reviewed or remain unknown. The
earlier temporal-patch and connectivity failures are not reopened. Existing
seven target/three negative anchors remain exposed regression, not new holdouts.
No Windows request or file export is needed for this design decision.

## Verification and disposition

Forty-six signature equalities, two saved-Canny equalities, six 1.0 match-score
checks and input immutability assertions pass. No production tests are rerun for
an unchanged implementation. Document governance, local links/retained obligations
and whitespace checks accompany publication. No physical accuracy, new scalar
truth, O2 acceptance or field improvement is claimed. ML remains excluded and
`FIELD FAIL` is preserved.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: support attribution is already lost when shared horizontal-mask extrema become the registration signature. This demonstrable information loss limits the proposed repair; it is not a new claim that this projection is the sole first physical cause of the previous sequence errors.
- Logic-map impact: NONE — existing production owners are observed without mutation; reference preservation and optional interaction remain proposed, with no classifier or behavior consumer.
- Failure-registry impact: NONE — the new source-backed collision and mixed-component examples refine existing F04/F10 limits without a new accepted mechanism or field result.
