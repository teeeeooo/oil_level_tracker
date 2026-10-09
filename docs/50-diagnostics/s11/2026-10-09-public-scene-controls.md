# Public-video scene controls before detector comparison — 2026-10-09

Base: `2f5d814f1dab8201f28884d06dd8f2063fa5905d`.
This continues the [three-video intake](2026-10-09-public-video-intake.md) after
the [path-only rename](2026-10-09-public-video-rename.json). Nine previously
exposed native frames are bound to their source files before viewing any detector
prediction. The [machine record](2026-10-09-public-scene-controls.json) preserves
video/frame/image identity, preflight, display receipt, scripts and interpretation
limits. Current authorization and the next checkpoint remain in the
[Work Plan](../../00-project/work-plan.md).

## Scene inventory

All readings below are **agent provisional**, not human-confirmed physical truth,
candidate target binding, contour labels or scalar annotations. Frame times are
nominal playback times. There is no inference of physical recording speed.

| Case | Frame / seconds | Visible context and proposed purpose | Limitation |
|---|---|---|---|
| s5-empty | 0 / 0 | Empty-looking water glass; fixed rim and patterned base oppose fluid selection | No canonical EMPTY phase or structure mask; refraction may alter appearance |
| s5-inclined | 822 / 27.427 | Strongly inclined upper bubbly-water feature during pouring | Actual displaced surface versus separate splash sheet is unresolved; user interpretation requested |
| s5-settled | 1643 / 54.821 | Comparatively settled upper liquid surface, internal bubbles and persistent glass pattern | No exact contour, scalar or point correspondence |
| s6-empty | 0 / 0 | Empty-looking beer glass with thick base/rim/reflections | No whole-image negative label |
| s6-forming | 146 / 5.840 | Forming froth and upper surface, with turbulent lower transition | Two clean contours are not automatically available |
| s6-layer | 436 / 17.440 | Visible liquid–Foam transition; Foam–air top outside the original source image | Lower interface must not substitute for an unavailable upper target or Foam front |
| s7-empty | 0 / 0 | Empty-looking milk glass with rim and base | No certified alignment or per-pixel structure truth |
| s7-pouring | 532 / 22.189 | White liquid body, incoming stream and frothy/splash-like surface | White appearance alone does not identify Foam; a stream is not automatically a layer surface |
| s7-settled | 1063 / 44.336 | Settled white body and thin bubbly/frothy top | Exact milk/froth dividing contour remains unknown |

Each file remains in the development partition inherited from intake. All nine
frames were already exposed; none becomes an untouched holdout. Keep derivatives
and neighboring frames with the same source group. Different downloads do not
certify independent recording sessions.

## New physical question: inclined water feature

The display compares already saved sample5 f815/f822/f829, approximately
27.194–27.661 s. Only the center panel has an orange rectangle, source
X[800,1110), Y[400,650). It locates the question; it is not a traced contour,
pixel label, exclusion mask or proposed scalar.

The agent leans toward an actual displaced water surface but cannot confidently
exclude a separate elevated splash sheet. This distinction reverses the proposed
control role: protect genuine deformation versus oppose following a separate
splash. The question asks for regional physical interpretation, not exact XY.
Neither role is assigned while the answer is pending. An inconclusive answer
keeps this case unresolved; it does not invite a fabricated label or force a
detector choice.

The linked local display is
`sample/output/s11-public-scene-controls-20261009-001/sample5-inclined-surface-review.png`.
The same folder contains `water-controls.png`, `beer-controls.png` and
`milk-controls.png`. Their hashes and generation script are preserved in the
machine record; original images and MP4 files remain local and ignored.

## Use in the next design

The [closed independent-strip trial](2026-10-09-foam-two-side-transport.md)
matched a confirmed rim seed to other features even when both fitting folds
agreed. New scenes alone do not repair that mechanism. A new proposal must
preserve the spatial relationships of multiple parts of the same feature and
provide independent evidence about the material on each side. Coherent optical
distortion remains an opposing explanation, so spatial agreement alone is not
a physical selector. No concrete new classifier or decision threshold is
established by this inventory.

Use empty/filled water context to test proposed correspondence without treating
empty-frame subtraction or absence of a reference match as fluid proof. Preserve
rapid genuine movement; a control interpretation supplies no speed ceiling or
horizontal flattening rule. Beer supplies separate visibility and boundary-role
opposition, while milk tests whether bright bulk liquid is mistaken for Foam.
Existing sample4 real-front, rim and internal-texture controls still apply.

Once a distinct observable and decision/abstention rule are specified, freeze
the bounded native-pixel comparison before execution. One later fixed,
aspect-preserving reduced-resolution comparison can assess detail loss, with
all derivatives retaining the original partition. It cannot replace the existing
Mac regressions or Windows field gate.

The existing `s11_interface_shadow_evaluation.py` owns packet validation and
metrics, and `s11_target_truth.py` owns physical-to-target binding. They require
actual R22-3 candidate packets and annotations. This inventory supplies source
context only; it does not fabricate an evaluator packet, `.oiltruth`, candidate
label or target-binding artifact. Physical identity, target role, path support,
scalar eligibility and independent Oil/Foam outputs remain separate.

## Verification and disposition

Sixteen input pins match, including all three unchanged videos, the frozen intake
and rename records, nine native rasters and two saved context crops. All nine
case identities are unique and refer to already exposed native intake frames.
The four generated display hashes match their receipt, and all four sheets were
visually inspected. No new video decode, detector run, fitting, Recipe/label edit
or production change was performed. This is control preparation, not efficacy
or field acceptance. The sample5 physical role remains pending at this record.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: NOT_EVALUATED — no detector predictions were generated; the new ambiguity concerns a source scene's physical interpretation, not a diagnosed detector error.
- Logic-map impact: NONE — source-bound scene preparation changes no implementation or responsibility owner.
- Failure-registry impact: NONE — no new mechanism was tested; existing appearance, correspondence, output-coupling and provenance failures remain applicable.
