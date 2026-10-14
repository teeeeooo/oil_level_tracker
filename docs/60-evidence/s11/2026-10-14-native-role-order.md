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

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F09`, `S11-F10`.
- First harmful stage: the earlier absolute native classifier rejects N3; this comparison does not repair that classifier or establish a production causal loss. It tests a distinct relative-order capability with newly qualified source opposition.
- Existing feature coverage: saved original G0 native RGB/masks/path context only. sample4 Recipe exclusions/templates remain empty; Local XY OFF. Run preparation, automatic static learning, Artifact consumers, sequence and report are bypassed. Closed D2/Local XY results remain controls, not new efficacy claims.
- Execution scope: the planned diagnostic CLI prepares pinned qualified paths and all saved public alternatives, then performs exactly two fixed offline fits with one final exposed evaluation per arm. No video decode, temporal inference, production detector/Recipe, Windows execution or report reading.
- Logic-map impact: NONE — no executing production owner, numeric source, schema or setup feature changes. The diagnostic reuses existing frozen input/model owners with a separate loss/data contract.
- Failure-registry impact: NONE — source-specific cutoff rescue, unreviewed-winner promotion and field claims remain prohibited; no failure class is retired.
