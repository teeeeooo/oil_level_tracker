# Pretrained semantic ROI comparison: fixed observation rejected

**SCM-1 is CLOSED_WITHOUT_PROMOTION.** The fixed observation orders 15 of 17
existing constraints, but ranks both milk cup-top structures above the actual
large bubble top. This is not a detector improvement or a 15/17 accuracy estimate.
The [Work Plan](../../00-project/work-plan.md) owns the next transition.

## Scope and result

The [protocol](../../50-diagnostics/s11/2026-10-14-semantic-context.md) and
[input/model/runtime manifest](../../50-diagnostics/s11/2026-10-14-semantic-context/manifest.json)
were committed at clean **`6735985e294e589f7a605ec0acb1c066cbb8a3a2`** before
source inference. There was one checkpoint, one fixed three-prompt set, five
existing analysis ROIs and exactly five source forward batches. No training,
prompt/crop/aggregation retry, video decode, new physical label or production
consumer ran.

The [complete readout](../../50-diagnostics/s11/2026-10-14-semantic-context/readout.json)
keeps all 48 paths: 39 scored / 9 unavailable, 15 qualified / 33 unknown, across
four exposed recordings. There is no independent untouched test set. N3>N5 uses
two frames of one recording; all other required pairs share a source frame.

| Existing source controls | Ordered | Result |
|---|---:|---|
| Water N1>N2 | 1/1 | Scoped order only; N1 permits fluid/Foam interpretations |
| Sample4 N3>N4/N5 | 2/2 | Scoped order only; no native material classification |
| Public compressor four Foam uppers / three rims | 12/12 | Twelve comparisons within one frame |
| Milk actual bubble top 687 / cup structures 444·453 | **0/2** | Both orders reversed |

The fixed score is the lower-minus-upper mean of the pixelwise maximum of
`foam` and `liquid` support. It is not a calibrated probability or a class cutoff.

| Milk path | Qualified role | Fixed score |
|---|---|---:|
| 444 | Cup-top structure | 0.0412641888 |
| 453 | Cup-top structure | 0.0137967715 |
| 687 | Actual top of one large bubble | 0.0100431729 |

The 687–444 gap is **−0.0312210159** and 687–453 is **−0.0037535986**.
Neither an order-preserving cutoff nor selecting the highest-scoring path can
repair these two counterexamples. Unknown paths remain unknown, including any
that score above a reviewed path.

## What the saved components explain

For all 30 qualified side records, the fuzzy-union mean equals the `liquid`
mean within 1e−14 arithmetic tolerance. The combination therefore hides the
different Foam response in these sampled supports. This concerns model outputs,
not a physical conclusion that these pixels contain pure liquid.

The saved Foam lower-minus-upper difference at milk 687 is about 0.09263, versus
0.01626 / 0.00532 at the cup structures. However, substituting that response alone
would introduce a different counterexample: sample4's true upper N3 has about
0.01258, below internal-Foam N4's 0.01366. These are diagnostic calculations from
the saved prompt means, **not selection of a replacement score or a second
accepted trial**. Pretrained category context alone has not supplied physical
boundary-role authority at the required supports.

The [same-bubble/rightward-growth reply](../../50-diagnostics/s11/2026-10-14-milk-bubble-context/temporal-reply.json)
remains one qualitative temporal relation. The fixed anchor participates in the
spatial comparison; the 24 preceding frames are not additional labelled examples.
This run establishes nothing about temporal identity, rupture/merger, whole-layer
stability or Foam episodes.

## Engineering verification

The source runner used absolute paths from `/private/tmp`. The
[verification receipt](../../50-diagnostics/s11/2026-10-14-semantic-context/verification.json)
checks 78 side records / 724 patch means with an independent `math.fsum`
reduction; maximum saved-mean error is 3.34e−16. Every required pair decision
matches. During the source run, independent float64 native-pixel interpolation
differs from the Torch reduction by at most **6.91e−7**, and all 17 order signs
agree. The complete parameter-state hash matches the synthetic preparation and
is unchanged after inference. Reusing the output path is rejected before model
loading, with all bytes unchanged.

The preparation's **40 focused tests** cover input geometry, refusal boundaries,
union/order arithmetic, interpolation and CLI routing. Checkpoint loading has
no missing, unexpected or mismatched parameters. All existing source-role/input
validators also ran. No production detector or GUI dependency changed.

Measured isolated runtime is **9.5722 seconds**, including 5.7748 seconds for
import/model loading, with **1,349,795,840 bytes peak RSS**. Workspace allocation
was 1,436,307,456 bytes; conservatively adding both complete S11 evidence trees
still leaves the run below 3 GB. These are offline diagnostic measurements, not
the Windows detector performance backlog or throughput qualification.

## Retention and next design boundary

Retain the fixed protocol, setup/input pins, complete compact support/pair table
and independent verification. No dense semantic maps or copied source frames
were written. The failed fixed observation does not justify another prompt,
checkpoint, crop or cutoff search. [Closeout](../../50-diagnostics/s11/2026-10-14-semantic-context/closeout.json)
removes the eight newly downloaded model assets and fourteen newly installed
packages after verification. The original research packages keep their versions,
and the retained DINO checkpoint's bytes are unchanged. The repository's own
distribution metadata is visible through `src/`, was not installed for SCM-1,
and is preserved. This releases about 690 MB; only compact results remain.
Reproducing the closed model run requires deliberately restoring its exact
recorded optional runtime and public checkpoint. The existing input validators
still pass after removal. No historical source/result pins were rewritten.
Both managed SCM-1 runs are closed with canonical evidence by reference; all
**51 managed runs have zero artifact errors**. Temporary plan/selection files and
five source-run scratch files were removed. Governance and whitespace checks pass.

Any successor must define Foam and liquid observations separately, preserve the
known true upper and internal/structure controls, and declare its source-grouped
supervision and evaluation before fitting. The saved prompt vectors can support
that design without another source forward; they are not new material truth or
a reason to repeat the closed physical questions. BASE/Accum admission, raw Foam
front recovery, V4/V5 shadow and integrated Windows/report acceptance remain
separate required stages.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F09`, `S11-F10`.
- First harmful stage: the fixed semantic support reduction ranks both milk cup structures above the qualified Foam upper. Physical-role observation remains unresolved before any candidate consumer or episode stage.
- Existing feature coverage: all four source controls and the five previously fixed native ROIs; complete local sampling support is verified but transformer dependence spans the entire unmasked ROI. Sample4 exclusions/templates remain empty; Local XY OFF and closed D2/Local XY results are unchanged. Production Recipe defenses, static-learning/reference consumers and report behavior were not exercised.
- Execution scope: one offline pretrained CLIPSeg execution from saved RGB, five batches / three fixed text queries, 48 paths and 17 required comparisons; zero fit updates, decoder calls, temporal propagation, new labels, production changes, sequence/report replays or Windows qualification.
- Logic-map impact: NONE — this experiment changes no executing production owner, Recipe setup, candidate selection or typed runtime contract.
- Failure-registry impact: NONE — the existing appearance/identity limitations remain; this record adds the scoped semantic-union counterexample without claiming a general theorem about all pretrained models.
