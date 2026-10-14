# Native role ordering: fixed source-balanced comparison

This record owns the separately declared **NRO-1** local experiment. The
[Work Plan](../../00-project/work-plan.md) owns execution state and next action.
The standing user authorization covers staged local implementation, verification,
commit and push; a new physical judgment or Windows task remains a stop point.

## Question and difference from closed trials

The newly [qualified public roles](2026-10-13-existing-material-execution.md#public-lower-rim-reply--2026-10-14)
provide four external Foam-upper paths and three exact glass-rim paths. They share
one exposed recording/frame, not seven independent samples. Together with N1–N5,
there are twelve qualified paths across three recordings. This now permits a
source-separated, two-sided relative comparison that the original two-source
training roster could not supply.

The original native classifier's N3 rejection remains a failure. NRO-1 asks a
different, smaller question: can **within-source external-versus-opposition
supervision** produce a useful relative order on the public source? Scores have
no absolute external/nonexternal meaning or fitted cutoff. Neither maximum score
nor a positive score selects a physical path. N3 enters training in this new
contract and its fit cannot be reported as recovered independent transfer.

This does not establish whether data, loss or the previous representation caused
the old failure. It reuses the encoder to avoid an architecture search and tests
spatial-pattern advantage against a same-protocol RGB-mean ablation. Even a full
pass is exposed relative evidence, not a calibrated classifier, raw Foam front,
full G1, O2 or field acceptance.

The earlier [ordered temporal texture](../../50-diagnostics/s11/2026-10-10-temporal-texture-observation.md)
and [public temporal-detail screen](../../50-diagnostics/s11/2026-10-12-public-compressor-source.md#bounded-temporal-detail-feasibility-screen)
already expose optical-motion ambiguity. The new rim role does not supply the
missing cell-event correspondence, so no temporal-score or temporal-CNN retry is
selected here. No fresh media acquisition or decode is needed.

## Frozen protocol before source execution

- **Fit:** sample5 N1>N2; sample4 N3>N4 and N3>N5. Internal Foam and structure remain
  separate reference roles. The loss is mean `softplus(-(score_pos-score_opp))`
  within a recording, then mean across the two recordings. Three constraints are
  not three independent sources.
- **Final exposed transfer:** public external 963/995/1029/1031 versus rim
  1769/1788/1789, all twelve pair comparisons. Nothing from this recording enters
  gradient updates, early stopping, model selection or cutoff fitting.
- **Population:** keep all 27 saved public fragments and all 5 fit paths. Unreviewed
  public paths stay unreviewed; unresolved orientation/missing side input gets no
  score or negative-success label. The full G0 remains referenced, not relabelled.
- **Input:** the existing ordered complete 7×7 RGB patches, RGB/255, per-side mean,
  unchanged 1,118-parameter encoder. Inference receives only tensors. Source,
  coordinates, role, facets and patch count are not features.
- **Two arms, one fit each:** native spatial patches and the same patches with each
  channel replaced by that patch's mean. Same initialized weights, CPU float32,
  two threads, seed 20261013, Adam 0.001, 1,000 full-batch updates per arm; no
  augmentation, checkpoints, crop/seed/split/threshold/architecture search.
- **Required result:** every native fit and transfer pair must have a strictly
  positive score gap. A tie is failure to establish the order. If the mean arm
  also orders every public pair, record `NO_NATIVE_PATTERN_ADVANTAGE`; do not call
  the native pattern necessary. Any native error closes without promotion.
- **Limits:** 600 s / 1 GB peak RSS / 32 MB scratch / 6 MB retained, within the
  existing aggregate 3 GB isolated workspace. Preserve final weights and complete
  compact scores, not media or dense-feature copies. No production mutation.

The [runner](../../../tests/diagnostics/s11_native_role_order_trial.py) reuses
`s11_native_surface_trial.make_model`, pixel/pin helpers, the native qualifier and
the existing CR1 offline/write guard. A separate entry is necessary because the
old runner deliberately pins its two-source, five-unit absolute-classification
loss/split; changing that entry would rewrite its closed experiment contract.
The new entry owns only preparation, source-balanced order loss and its bounded
evaluation. Prepared inputs and source hashes are committed at a clean head
before fitting; the actual run records that head and refuses output overwrite.

## Preparation verification

The [manifest](../../50-diagnostics/s11/2026-10-14-native-role-order/manifest.json)
and [preparation checks](../../50-diagnostics/s11/2026-10-14-native-role-order/preparation-verification.json)
retain 32 units: 12 qualified, 20 unreviewed, 26 with available input. The six
unavailable public paths stay explicit. Actual preparation ran from `/private/tmp`
and its runtime input loader verified the complete pinned tensor hashes.
**167 focused tests passed in 2.75 s.** The isolated Torch runtime also verified
1,118 parameters, independent NumPy source-balanced loss arithmetic, common-score
offset invariance, three synthetic gradient updates and no access to an unused
transfer tensor. These are engineering checks, not source efficacy.

## Fixed execution result

**`CLOSED_WITHOUT_PROMOTION`.** The source run used clean
`432c9b0e959fa72a9e73b325e231f1e073f4e95d`. Both arms completed exactly 1,000
updates; neither was retried. [Full scores](../../50-diagnostics/s11/2026-10-14-native-role-order/readout.json)
retain all 32 units, 26 available and 20 unreviewed, per arm.

| Fixed arm | Fit order constraints | Public upper-versus-rim constraints |
|---|---:|---:|
| Native spatial patches | 3/3 ordered | **0/12 ordered; all reversed** |
| Per-patch mean RGB | 3/3 ordered | 12/12 ordered |

The native model ranks **every reviewed public rim above every reviewed public
Foam upper**. A monotone score cutoff cannot preserve these uppers while excluding
the rims. No threshold or training-setting adjustment follows. The mean arm's
limited success neither repairs the failed native trial nor establishes an
absolute classifier or source-general physical identity. These twelve comparisons
share one frame and are not twelve independent accuracy cases.

The retained [native weights](../../50-diagnostics/s11/2026-10-14-native-role-order/native-weights.npz)
and [mean-RGB weights](../../50-diagnostics/s11/2026-10-14-native-role-order/mean_rgb-weights.npz)
permit arithmetic checks without retraining. [Independent NumPy float64 verification](../../50-diagnostics/s11/2026-10-14-native-role-order/verification.json)
reproduces all 52 available fragment forwards: maximum absolute logit errors
0.000005407 / 0.000008546, below the arithmetic tolerance 0.0001. Every pair decision
agrees. Both arms started from identical weights; overwrite was refused before
fitting and all result/weight hashes remained unchanged.

The run took 16.795 s with peak RSS 378,208,256 bytes; isolated workspace allocation
was about 746 MB. This is offline diagnostic cost, not detector throughput.
Managed run `native-role-order-20261014-001` retained four final files / 53,477 bytes
and removed four work copies. No source pixels, intermediate checkpoints, decoder,
production consumer, Windows replay or field acceptance was added.

## Milk path review for the frozen mean-RGB reference

The mean-color result warrants only a separately bounded **fixed-weight** check on
another existing source, not promotion or a new fit. Select the existing milk
`s7-settled-native` frame1063 before any model score on that source. Its native
rows Y373/Y384/Y535 expose three complete paths (444/453/687), all with 25 upper
and 25 lower patches. The first two lie around the glass mouth and the third
near the visible upper surface; their exact displayed-path roles are a new question.

The earlier milk reply that the **lower Foam–milk interface is hard to distinguish**
stays closed. Do not ask for that hidden lower interface, a dense mask, full-frame
material labels or a revised beer/water judgment. Current 12 native roles also stay
closed. Reuse the original full-frame PNG and original G0 graph/raster, preserve
all 16 fixed-column native paths and select every fragment at the three stated
rows. No score/length mining, new decode, model inference or training occurs in
this preparation. The mean-RGB weights stay frozen; milk is outside both its fit
sources and original public evaluation, but remains design-exposed development.

The existing native-packet builder, row preparation, renderer and qualifier own
these operations. The renderer now accepts a pinned alternative source image and
multiple rows; its original public layouts retain their bytes. The preparation
budget is 3 MB scratch / 1 MB retained. Only a new question image and essential
binding/verification JSONs are retained; original media and captures are references.

Preparation is complete: [review image](../../50-diagnostics/s11/2026-10-14-native-milk-review/review.png),
[row plan](../../50-diagnostics/s11/2026-10-14-native-milk-review/plan.json),
[source manifest](../../50-diagnostics/s11/2026-10-14-native-milk-review/source-manifest.json),
[complete packet](../../50-diagnostics/s11/2026-10-14-native-milk-review/native-packet.json)
and [proposal](../../50-diagnostics/s11/2026-10-14-native-milk-review/proposal.json).
The actual [qualifier inspection](../../50-diagnostics/s11/2026-10-14-native-milk-review/inspection.json)
reports **three pending subjects, zero qualified targets**. Renderer and inspection
CLIs ran from `/private/tmp`; ROI array equality, path hashes and all 25/25 support
patches pass. [Verification](../../50-diagnostics/s11/2026-10-14-native-milk-review/verification.json)
also confirms both previous public PNGs are byte-identical and the frozen NRO-1
input hashes remain unchanged. The new image was visually checked for complete
paths and legible crops. Seven canonical files total 457,364 bytes; managed run
`s11-native-milk-review-20261014-001` removes the seven work copies and two temporary
legacy-render checks. This preparation closes independently of the pending user
judgment; it does not authorize assigning a role or scoring the new source yet.

Closeout checks pass: detector governance, whitespace, all 1,302 local links in
the seven changed Markdown files, and all **44 managed runs closed without
artifact errors**. No duplicate worktree or retained work copy was created.

### Milk reply and location clarification

The user identifies 444/453 as the cup's upper structural boundary. These two
displayed roles can be bound as structure. For 687, the user cannot locate the
crop and tentatively sees an upper fluid boundary, explaining that the oblique
view can show one fluid boundary as two lines. This is not an exact-path role
confirmation or evidence of two material interfaces. Retain the complete reply;
use `UNASSESSABLE` for 687 **at this display-identification stage**, with no target
or invented role alternatives. This status is not a permanent visibility verdict.

Prepare a location clarification of **the same saved 687 path**, showing its
unchanged crop and magenta path beside the original ROI with a red crop-location
box. Reuse the existing renderer through an optional locator mode; keep the first
question, confirmed structures and prior lower-interface reply closed. No model
score, retraining, new frame or new path selection follows. This reply/locator run
has 3 MB scratch / 1 MB retained limits and uses existing source pixels and G0.

The [verbatim reply](../../50-diagnostics/s11/2026-10-14-native-milk-review/reply.json)
and [actual qualification](../../50-diagnostics/s11/2026-10-14-native-milk-review/qualification.json)
bind **two structure paths and one unqualified path**. Together with the prior
twelve roles this is fourteen qualified paths in four recordings: six external,
two internal and six structure. No positive milk path has been qualified.

The [location image](../../50-diagnostics/s11/2026-10-14-native-milk-review/location.png)
and [single-path proposal](../../50-diagnostics/s11/2026-10-14-native-milk-review/location-proposal.json)
clarify 687 only. Its [inspection](../../50-diagnostics/s11/2026-10-14-native-milk-review/location-inspection.json)
is pending, not a replacement answer. [Checks](../../50-diagnostics/s11/2026-10-14-native-milk-review/location-verification.json)
prove identical subject bytes and identical RGB-plus-magenta crop at 8× zoom;
the red box locates source rectangle `[1092,518,1170,555]`. Both previous public
images and the first milk image remain byte-identical under their original CLI
conditions. Actual qualifier/renderer/inspection CLIs ran from `/private/tmp`.
Managed run `s11-native-milk-location-20261014-001` retains six canonical files /
356,707 bytes, removes ten temporary copies/checks and makes zero model calls.

### Located reply and fixed mean-RGB milk protocol

The user then confirms 687: **“foam의 실제 상단임 큰 방울 한개의 상단이네”**.
Bind only this exact path as `EXTERNAL_FOAM_UPPER`. Its single-large-bubble context
does not establish a stable Foam layer, dense front, episode boundary or two
material interfaces. The previous location-unassessable status stays historical;
the explicit located reply supersedes it for the same subject hash.

**MRO-1** is a fixed-weight falsification check of the limited NRO-1 **mean-RGB**
reference, not another fit or a revival of the failed native arm. Before scoring:

- Freeze source/input manifest and the saved weight hash
  `064fdf34926b08ddaf93b45ea549f186b618b013a27ab7ed91fb544356d6a9b9`.
- Use the existing mean-patch transform, ordered side pooling and encoder without
  any updates, calibration, crop/score selection or alternative arm. Reproduce all
  26 prior mean-RGB scores within arithmetic tolerance 0.0001 before milk inference.
- Retain all 16 milk paths: 13 available, 3 unresolved orientations; 3 qualified
  and 13 unreviewed. The only physical comparisons are **687 > 444** and **687 > 453**.
  Missing/unreviewed paths supply no target or negative success; no highest-score
  winner or absolute cutoff is selected.
- A nonpositive gap falsifies this reference on the milk order. Both positive
  gaps yield only `LIMITED_EXPOSED_ORDER_ONLY`, not source-general accuracy or a
  production promotion. Both comparisons share one already exposed frame.
- Require unchanged parameters and saved weight bytes. Limit execution to 60 s,
  500 MB RSS, 3 MB scratch / 1 MB retained within the existing 3 GB workspace.
  Preserve small scores and checks; do not copy weights, source pixels or tensors.

The [followup entry](../../../tests/diagnostics/s11_native_role_order_followup.py)
reuses the existing encoder, pin/patch helpers, transform, comparison and offline
guard. A separate inference-only entry preserves the frozen runner's original
fitting contract; it loads its final weights strictly and has no optimizer path.
The qualifier binds the newly confirmed path before any model call. The original
failed trials and production/Windows gates remain unchanged.

The [located reply](../../50-diagnostics/s11/2026-10-14-native-milk-review/location-reply.json)
is bound by the [original qualifier](../../50-diagnostics/s11/2026-10-14-native-milk-review/location-qualification.json).
All fifteen roles are now closed at displayed-path precision. The
[followup manifest](../../50-diagnostics/s11/2026-10-14-native-milk-order/manifest.json)
and [preparation checks](../../50-diagnostics/s11/2026-10-14-native-milk-order/preparation-verification.json)
verify 13 exact input tensors and the full sixteen-path denominator. **21 focused
tests pass in 0.15 s** (10 new followup checks plus 11 order checks); actual prepare
CLIs from the repository and `/private/tmp` produce identical bytes. No model was
called during reply binding or preparation.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F09`, `S11-F10`.
- First harmful stage: the earlier absolute native classifier rejects N3; this comparison does not repair that classifier or establish a production causal loss. It tests a distinct relative-order capability with newly qualified source opposition.
- Existing feature coverage: saved original G0 native RGB/masks/path context only. sample4 Recipe exclusions/templates remain empty; Local XY OFF. Run preparation, automatic static learning, Artifact consumers, sequence and report are bypassed. Closed D2/Local XY results remain controls, not new efficacy claims.
- Execution scope: NRO-1 completed exactly two fixed offline fits. Milk reply/locator preparation uses no model; the located reply now qualifies 687. The separately frozen MRO-1 followup will load only the existing mean-RGB weights, reproduce prior scores and compare the complete milk roster without fitting. No video decode, temporal inference, production detector/Recipe, Windows execution or report reading.
- Logic-map impact: NONE — no executing production owner, numeric source, schema or setup feature changes. The diagnostic reuses existing frozen input/model owners with a separate loss/data contract.
- Failure-registry impact: NONE — source-specific cutoff rescue, unreviewed-winner promotion and field claims remain prohibited; no failure class is retired.
