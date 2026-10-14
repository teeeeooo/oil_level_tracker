# Fixed pretrained semantic-context comparison (SCM-1)

This investigation tests one additional observation, not a replacement detector.
Current authority remains in the [Work Plan](../../00-project/work-plan.md).
The [milk reply](2026-10-14-milk-bubble-context/temporal-reply.json) closes the
same-object question with qualitative growth toward image right. It does not
supply exact temporal paths, pure-side masks or event truth.

## Hypothesis and closed controls

The local RGB models have already confused actual Foam uppers and glass rims.
NRO-1 and its fixed milk followup remain closed. Appearance similarity to local
references, raw edge topology, optical flow and temporal texture also remain
insufficient identity evidence. SCM-1 adds **external pretrained text/region
supervision plus the complete existing analysis ROI**, instead of fitting another
head to the same few paths or treating motion as material identity.

[CLIPSeg](https://github.com/timojl/clipseg) adds a text-conditioned segmentation
decoder to CLIP; its [paper](https://openaccess.thecvf.com/content/CVPR2022/papers/Luddecke_Image_Segmentation_Using_Text_and_Image_Prompts_CVPR_2022_paper.pdf)
and [implementation documentation](https://huggingface.co/docs/transformers/model_doc/clipseg)
describe that pretrained objective. This motivates a bounded capability test,
not a claim that natural-image training covers refrigeration glass or Foam.
Model training exposure to these public recordings is unknown.

## Protocol fixed before inference

- One checkpoint: `CIDAS/clipseg-rd64-refined`, repository revision
  `999e0328d9e10b484360c477313983f9afdd7050`; safetensors SHA-256
  `d00ca85d6b859f9d07b7cfb8ef26fe9771cb275b34c9368f2ecf603139307f55`.
  Use `transformers==4.57.6`, CPU float32, two threads, evaluation/inference mode.
  No local fitting, prompt/model/crop search, remote inference or application dependency.
- Fixed literal prompts, in order: **`foam`, `liquid`, `glass rim`**. The third
  is descriptive context only, not an alternate score to select after outcomes.
- Reuse all **48 paths**, 15 qualified / 33 unknown, from the frozen NRO and milk
  manifests. There are 39 available / 9 unavailable paths, four recordings and
  five source frames. Original partitions are historical; nothing enters fit.
- Use each frame's **existing native analysis ROI**, recovered from the pinned G0
  or milk packet geometry. Existing captures include both full frames and saved
  ROIs; reconcile their image origins, and verify every sampled 7×7 RGB patch
  against its existing hash after cropping. Do not choose a new crop around a path.
- Apply the checkpoint's native 352×352 bilinear resize and pinned normalization.
  The square resize changes aspect ratio; record the exact source-to-model scale.
  All model outputs depend on the whole ROI, including areas outside the local
  visible support. The old complete-side test bounds only **where scores are
  sampled**, not the transformer's receptive field or pure material truth.
- Bilinearly upsample all three logit planes to the native ROI with
  `align_corners=False`, then sigmoid. Define foreground support at each pixel as
  `max(foam, liquid)`. This is a frozen fuzzy union, **not a calibrated probability**.
  N1 permits either fluid/Foam external interpretation, so a Foam-only classifier
  would improperly narrow its label. Apply the same union to every source.
- For each available path, mean each existing 7×7 patch, then mean patches equally
  within each side. The sole order score is **lower foreground mean minus upper
  foreground mean**. Retain separate prompt means and rim values for diagnosis.
  No rim veto, fitted weight, threshold, maximum-path selection or pixel truth.
- Reuse exactly 17 existing positive/opposition constraints: N1>N2, N3>N4/N5,
  12 public upper/rim pairs, and milk 687>444/453. N3>N5 spans two frames of the
  same recording; the other comparisons are within one frame. All required gaps
  must be strictly positive. A tie/reversal closes this fixed observation without
  promotion. Even 17/17 would establish only limited exposed order, not accuracy,
  calibration, full G1/O2, stable Foam-layer detection or BASE/Accum recovery.
- The 25-frame qualitative milk relation supplies no additional scored units.
  This spatial experiment cannot test temporal identity or growth preservation;
  any later consumer still needs that separate obligation.

Input bindings, source, model files, installed package versions and processor
geometry must be frozen at a clean commit before the five scored forwards.
Synthetic geometry/aggregation tests and checkpoint loading do not count as
source efficacy. There is no repeated source forward for score tuning.

## Isolation and retention

Reuse the existing ignored research environment and offline/write guard. Add the
minimum CLIPSeg dependencies without changing the pinned Torch/NumPy/Pillow core.
Download only the pinned safetensors and required tokenizer/config files, with
verified TLS and hashes; never upload source images or load remote Python code.
The existing retained CR1 checkpoint remains under the user's retention decision;
this one separately pinned semantic checkpoint joins the same environment set,
not a per-run model copy. Both count toward the unchanged **3 GB aggregate cap**.
No further checkpoint accumulation follows from a failed result.

Preparation has an incremental 1.2 GB allowance including transient files; check
the actual allocated and logical footprint before/after installation and download.
Scored inference limits: 900 seconds, 2.5 GB peak RSS, 32 MB scratch, 6 MB retained,
and 3 GB aggregate workspace. Use managed setup and source-run entries. Stream
five ROIs; retain complete per-patch means, pair results, provenance and numerical
verification, not dense heatmaps or copied source images. Close failed runs too.

The new diagnostic entry is separate because existing NRO/MRO runners own frozen
fit/weight contracts. It reuses their input validators, exact patch/pin helpers,
comparison arithmetic and CR1 resource/write/network guard. It owns only this
pretrained inference and signed semantic support reduction.

## Preparation checks

The [setup receipt](2026-10-14-semantic-context/setup.json) pins the downloaded
604,641,231 bytes, checkpoint/config/tokenizer hashes, implementation files and
the resulting package versions. Fourteen packages were added; every previously
installed package retains its version. Both complete S11 evidence trees plus the
research workspace total **1,546,584,064 allocated bytes**, conservatively inside
the unchanged 3 GB limit. No source image was uploaded or newly decoded.

**40 focused tests pass**, including ROI origin reconciliation, missing/duplicate
support refusal, pixelwise union, signed order, independent interpolation and
the real CLI outside the repository. A synthetic checkpoint smoke test loads
all 150,747,746 parameters with no missing/unexpected/mismatched keys. Independent
Pillow preprocessing matches exactly; independent native support sampling differs
by at most 0.0000000645. Synthetic image changes alter each text-conditioned
output; this establishes computational reachability, not physical discrimination.
The smoke uses one synthetic batch and **zero source forwards**. Its 1.463 GB
peak RSS fits the declared source-run ceiling. The inherited guard blocks
network/outside writes, including additional library initialization attempts.

The [manifest](2026-10-14-semantic-context/manifest.json) pins all five existing
ROIs, their pixel hashes and scales, all 48 path identities by reference, the
17 comparisons, implementation, model and runtime. Scored inference has not run
at this preparation checkpoint.

## Completed execution

The [fixed source result](../../60-evidence/s11/2026-10-14-semantic-context.md)
closes SCM-1 without promotion: 15/17 orders, with both milk upper/rim comparisons
reversed. It owns measured results and verification; the protocol above is the
pre-execution contract and has not been adjusted to the outcomes.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F09`, `S11-F10`.
- First harmful stage: known local appearance observations misorder qualified physical upper/structure paths; SCM-1 tests whether pretrained ROI semantics supply a different bounded order signal. Production's earlier loss remains unchanged.
- Existing feature coverage: pinned native RGB/geometry and all four source-role controls, including N1's compatible fluid interpretation and sample4's existing 104×104 ROI. Recipe learning, static templates, exclusions, downstream Artifact consumers and Local XY are not executed; sample4 exclusions/templates remain empty, Local XY OFF, and the completed D2/Local XY comparisons stay closed. Semantic context sees the unmasked existing ROI; this is not evidence about unexercised Recipe defenses.
- Execution scope: completed isolated CLIPSeg load and five saved-ROI forwards through `tests/diagnostics/s11_semantic_context_trial.py`, with existing qualification/input loaders and 17 bounded order comparisons. No video decode, temporal propagation, new physical labels, production consumer, sequence/report replay, Windows qualification or field acceptance.
- Logic-map impact: NONE — the optional offline diagnostic is not imported or registered by the application and changes no production executing owner or data contract.
- Failure-registry impact: NONE — the proposed pretrained observation does not retire local appearance, optical-warp or wrong-boundary counterexamples; its own result must retain any new failure.
