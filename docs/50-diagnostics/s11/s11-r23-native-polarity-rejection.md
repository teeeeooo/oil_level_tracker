# R23 native-polarity association experiment — rejected

## Disposition and scope

On 2026-09-17 the user authorized implementation, validation, commit and push
after the R22-2 Windows reports. A bounded association veto was implemented
locally, tested, and **rejected**. It is not in the running detector. R22-2
source and R22 resolver behavior are preserved; no R23 release or field repair
is claimed. Current sequencing remains owned by the [work plan](../../00-project/work-plan.md).

## Reviewed evidence corrections

- BASE f14386: the user separately confirmed native sector 1, X [130,236),
  Y382 and sector 4, X [449,555), Y417 near the actual interface. Scalar Y411.5
  cannot be applied as exact truth at every X. Sector 4's diagnostic peak Y410
  and positive peak gradient do not invalidate its reviewed path Y417.
- BASE f14362: the user rejected sector 2 Y437 because it is close to the
  interface but consistently offset. This establishes a **localization
  mismatch**, not the identity of an internal reflection or different material.
  Its exact error and acceptable localization interval remain unmeasured.
  The earlier stronger “different structure” label is not a certified negative
  for a physical-interface classifier. Other native points are not relabeled.
- The corrected sector 1 raw means give path contrast 0.02366352201257854
  and candidate-center contrast 0.023399926008140393. The earlier discrepancies
  were report transcription errors, not an inconsistent trace.
- Accum f16280: reviewed Y213 remains the actual-boundary reference. Nearby
  material-path Y217 and its native sectors remain measured proposals, not
  independently certified support. Shared gray/Sobel/material derivation must
  not be counted as independent evidence merely because measurements agree.

These are transferred human-review facts and bounded report checks, not a
claim that private images were reexamined locally. No private video is stored.

## Rejected mechanism

The prototype reused existing material-path samples, carried at most five
gray-channel polarity descriptors through the typed evidence owner, and
compared exact common native X extents. Three common sectors with consistently
opposite contrast could prevent a position-changing temporal link from
inheriting confirmation and motion history. No absolute dark/bright Oil rule,
diagnostic peak recentering, source-specific Y, or private timestamp was used.

Nevertheless, polarity was still only a shared appearance cue, not a physical
identity decision. Three agreeing sectors did not fix that semantic gap.
Restricting the veto to unconfirmed tracks also failed protected observations.

The first variants also altered same-frame grouping or pruned alternative
edges before ambiguity resolution. This can change competing assignments and
create a new winner; a negative local cue is not permission to promote that
winner. The final prototype preserved row grouping and the ambiguity graph,
checked only the chosen link, reserved both endpoints on rejection, and
limited the veto to unconfirmed tracks. It still failed acceptance.

## Public regression measurements

Comparison baseline: `0963e384e1604b5439e017e5ada2deec5c12b009`.
The existing replay harness, frozen media/recipe/truth inputs and runtime
fingerprint `7b14134e3f811d06e45ea2cd44686b5ffedd22dc7e2848fd2e04bd838f8aa20d`
were used. Input records and runtime fingerprints matched before comparison.
No checked truth, tolerance or golden was changed.

| Prototype | Compared truth cases | Observed regressions |
|---|---:|---|
| A: row splitting and edge pruning | 13 across four public clips | Base annotations 144/156: error 13→22.5 px; Sample3 annotation 1035: 1→31 px |
| B: preserve rows, require displacement beyond existing row tolerance | 5 across Base/Sample3 | Base 144/156 and Sample3 900 become missing; Sample3 1035 remains 31 px error |
| C: preserve ambiguity graph, veto chosen link | 5 across Base/Sample3 | Base 144/156 become missing |
| D: unconfirmed tracks only, final archived prototype | 5 across Base/Sample3 | Base 144/156 still become missing |

Annotations 144 and 156 both map to the existing sampled row at 5.005 seconds;
they are two protected cases, not two distinct sampled frames. An annotation
being approximate or historically visually censored was not used to waive the
current protection contract. Later variants were not run on all 13 cases after
their subset already failed; no complete-suite PASS is claimed for them.

The numerical records and exact compared fingerprints are in the
[machine-readable results](s11-r23-rejected-native-polarity-results.json).
The earlier 1,537-pass/2-fail non-Qt experimental run and subsequent focused
Sample3 failures also exposed changed protected owner-gap behavior. Those runs
are prototype failures, not the final restored-tree verification.

## Counterexample and reproducibility

Four added tests construct one known curved interface, translate it upward or
downward, reverse its photometric polarity, and vary exposure before tracklet
confirmation. They use the production raster path generator and existing
tracklet builder. The native contrasts actually reverse on at least three
sectors; candidate positions still follow the known curve. All four pass on
the restored runtime and fail with the archived prototype (two IDs instead
of one). This is a direct positive-control counterexample to the veto.

The [non-executing prototype patch](s11-r23-rejected-native-polarity-prototype.patch)
has SHA-256 `e59730535f6eb646edac80c810e50eb9566f04d37d134552e8e100fad7d6b002`.
It applies to source at the baseline commit; it is historical experimental
evidence, **not a selectable implementation or a patch to deploy**. To repeat
the counterexample, use a disposable baseline checkout, apply this patch there,
using `git apply --unidiff-zero`, copy the current
`tests/unit/test_oil_interface_tracklets.py` into that checkout,
and run `pytest -q tests/unit/test_oil_interface_tracklets.py -k real_curve`.
Run from that checkout: its conftest intentionally owns the source import path.
The expected prototype result is four failures. The patch preserves the final
prototype only; earlier variant numbers are measured evidence, not claims that
the patch reproduces those earlier variants.

## Next design obligation

Return to the [physical-interface design](../../20-architecture/s11-physical-interface-evidence-repair-design.md)
and [acceptance gates](../../30-validation/s11-physical-interface-evidence-repair-validation.md).
Establish a contour/context witness that separates positional uncertainty,
legitimate photometric variation and contradictory structure using paired
public/synthetic rasters before coupling it to assignment. Native polarity can
be an input but cannot alone supply `DIFFERENT_INTERFACE` or an association
veto. Preserve the complete ambiguity graph; do not treat removal of a
competitor as new positive authority. Accum material compatibility/handoff and
initial-FULL visible-interface admission remain separate unimplemented gates.
No further Windows extraction or rerun is needed for this rejected experiment.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-TRACKLET`, `OIL-SELECTOR`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: experimental tracklet association/confirmation; shared photometric opposition incorrectly broke continuity, and earlier edge pruning also changed assignment competition. Physical causes of the private gaps remain separately bounded.
- Logic-map impact: NONE — all prototype production edits were removed; R22-2 runtime remains exact baseline source.
- Failure-registry impact: UPDATED — F04 records this rejected polarity-only identity shortcut and its paired controls.
