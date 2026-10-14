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

## Separate-role readiness follow-up

**Executed at saved-input readiness scope; one new path role is pending.** The CR-1 runtime has been
[retired](2026-10-13-post-cr1-review-intake.md#cr1-runtime-retirement-2026-10-14).
The successor role objective and its partial-label boundaries are in the
[existing design owner](../../20-architecture/s11-contextual-role-observation-design.md#separate-foamliquid-role-readiness-after-scm-1).
This follow-up audits the saved components; it does not retry SCM-1 or choose a
replacement score from its outcomes.

The [input plan](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/plan.json)
pins the previous NRO/MRO manifests, SCM manifest/readout and the new reader/tests.
Preserve every one of the 48 paths and original qualifications. Check the exact
source/frame/path and available side-patch counts, finite/ranged prompt values,
independent `math.fsum` prompt means and the complete population. Restore each
qualification's allowed interpretations instead of assuming every old
`EXTERNAL_SURFACE` means Foam. Report source-grouped positive coverage before
any future fitting contract. No coefficients, thresholds or role classifier are
selected in this step; existing semantic maps/weights are not restored.

One new review may address the missing definite native liquid role: public
f1499, X578/Y428, fragment **1463**. It is the sole input-available member of the
three still-unreviewed native paths in the previously reviewed lower interval.
1463 was never covered by the later 1769/1788/1789 rim reply. Keep 1523/1546's
unresolved orientation and unknown roles; do not replace them with fabricated
patches or false-negative successes. Candidate-level practical Oil acceptance
does not certify 1463's full native path. The selection precedes any new role
response and does not use semantic score, path length or a new crop for inference.

The code, tests and input plan were frozen at clean `b4ff286` before execution.
The [readout](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/readout.json)
retains **48 paths / 39 available / 15 qualified / 33 unreviewed**, from four
recordings and five frames. Its status is `ROLE_SUPERVISION_INCOMPLETE`:

| Certain native role | Paths with available input | Source recordings |
|---|---:|---:|
| Foam upper | 6 | 3 |
| Liquid upper | 0 | 0 |
| Internal Foam change | 2 | 2 |
| Structure boundary | 6 | 3 |

N1 remains a Foam-or-liquid disjunction, not a seventh definite Foam upper or a
definite liquid positive. Four source-group coverage folds retain all derivatives
of a recording together. No fold was fitted/evaluated or called untouched.
The missing liquid positives prevent separate positive fit/evaluation coverage;
this finding does not revoke the nine candidate-level Oil controls or their scope.
Even a positive 1463 reply would add only one exposed source, not complete the
training/evaluation contract or establish pure-side material truth.

The [review PNG](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/review.png)
shows the full source location, the unmarked crop at 5× nearest-neighbor scale,
and a marked copy with only the ten saved vertices of 1463. The existing qualifier
prepared the [proposal](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-proposal.json)
from the [review plan](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-plan.json).
Its [inspection](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-inspection.json)
returns `PROPOSAL_VERIFIED_PENDING_REVIEW`, with ten complete patches on each
ordered side and zero new labels. The full 27-path source inventory is preserved.
The crop is for human inspection only; it was not a new model input. All fifteen
previous spatial replies and the milk temporal reply remain closed. The next
step is the actual role of this previously unqualified segment; a still-image
answer will not be expanded into an oscillation or temporal label.

[Verification](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/verification.json)
records **51 focused tests passed**, including 32 new guards for changed vectors,
duplicate identity, role narrowing, unknown/unavailable handling, source aliases,
foreign-cwd CLI and overwrite refusal. The actual reader and both qualifier
entries ran from `/private/tmp` using absolute paths. A separate JSON/hash audit
joined all six qualification documents and recomputed all 78 ordered sides /
724 patch vectors: maximum mean error `3.33e-16`. Source grouping, original
interpretations and complete population agree. The raw display crop equals
the source pixels after declared scaling; overlay coordinates and hashes match,
and the PNG was visually checked. These are input/tool checks, not detector gains.

Managed run `sample/output/s11-semantic-role-readiness-20261014-001` uses
**8 MB scratch / 3 MB retained** bounds and existing application dependencies.
The seven canonical plan/readout/review/verification files total **677,868 bytes**;
the managed record references them without duplicate payloads. Its intermediate
render receipt and temporary plans were removed at closeout. No model, decoder,
training or production consumer ran. The retired CR-1 environment/models/cache
remain absent. Governance and whitespace checks pass; the focused documentation
check finds **282 local links / 54 anchors with no errors**, and all **52 managed
runs** pass closeout checks. O2 OPEN, FIELD FAIL and Local XY OFF are unchanged.

## Foam-lower/liquid reply and second-source preparation

The user answered **“foam 최하단임 유체랑 경계면”** for the exact 1463 view.
The [verbatim receipt](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-reply.json)
binds that statement to the proposal/display hashes. The contact is the Foam
lower boundary meeting bulk liquid, so it supports the separate liquid-upper
role, not Foam upper or internal Foam texture. No temporal movement, pure patch
materials, chemical Oil identity, whole-layer mask or scalar tolerance is inferred.
The original pending proposal/readout stay as the pre-reply checkpoint.

The new adapter, tests and input reply were frozen at clean `ae0e91e` before
the actual run. It reused the frozen native qualifier's path/pixel inspection,
then applied the contact role without the old `OSCILLATING_LIQUID_UPPER` label.
The [qualification and coverage delta](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-qualification.json)
returns `SCOPED_LIQUID_ROLE_BOUND`: **16 qualified / 32 unreviewed**, while all
48 observations, 39 available inputs and fifteen earlier roles remain identical.
The effective roles are six certain Foam uppers, **one certain liquid upper**,
two internal changes, six structures and N1's unchanged disjunction. The liquid
positive belongs to one recording, so `ROLE_SUPERVISION_INCOMPLETE` remains the
source-group coverage result. No new score or classifier was selected.

The next bounded source-only preparation is water C/f1643, whose regional water
surface and X950/Y489–494 interval are already closed. Its G0 inventory has one
interval-compatible native fragment, 1378. B/f1438 instead has three two-vertex
junction fragments at Y485 and one unresolved-orientation fragment at Y488;
none is silently selected or labelled. The existing `native_packet` reader
reconstructed C's [complete 61-path population](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-native-readout.json)
from saved edges: 45 have partial context and 16 have unresolved orientation.
The [manifest](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-manifest.json)
and [review plan](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-plan.json)
pin the old source interval, original pixels, G0 and reused code. The original
qualifier prepared the [proposal](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-proposal.json)
and [inspected it](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-inspection.json):
one 39-vertex path, 14 complete patches per side, `PROPOSAL_VERIFIED_PENDING_REVIEW`,
zero qualified C roles. The [PNG](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review.png)
shows the native cup context and plain/marked 5× details. Its only question is
whether that exact segment corresponds to the already reviewed water surface.
This is a second recording relative to the Miso liquid contact, but the same
water recording as N1/N2 and already exposed. C is outside the frozen 48-path
SCM roster; no semantic vector was generated or silently added to it.

The [verification receipt](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-verification.json)
records **99 focused tests passed**, including 20 new contact-role/identity/scope,
immutable prior-role, one-source coverage and foreign-cwd/overwrite guards.
All three actual CLIs ran from `/private/tmp`. An independent JSON join confirms
the single 1463 override, all 48 unchanged observations and all 61 water path hashes.
Plain PNG pixels equal the original crop after declared nearest-neighbor scaling;
the saved path coordinates reproduce the overlay exactly, and the image was
visually inspected without assigning its physical role.

Managed run `sample/output/s11-liquid-role-reply-20261014-001` budgets **8 MB
scratch / 3 MB retained**. The nine new receipt/qualification/review/verification
files total **483,695 bytes**. It references the canonical outputs and original
source PNG instead of retaining duplicates. Intermediate packet/render records
and temporary plans were removed at closeout. The retired runtime remains absent;
no model, decoder, training, production change or Windows execution occurred.
Governance and whitespace checks pass; 291 local links / 53 anchors have no
errors, and all 53 managed runs pass closeout checks. The next necessary user
judgment is only water-C 1378's native correspondence.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: the fixed semantic support reduction ranks both milk cup structures above the qualified Foam upper. Physical-role observation remains unresolved before any candidate consumer or episode stage.
- Existing feature coverage: all four source controls and the five previously fixed native ROIs; complete local sampling support is verified but transformer dependence spans the entire unmasked ROI. Sample4 exclusions/templates remain empty; Local XY OFF and closed D2/Local XY results are unchanged. Production Recipe defenses, static-learning/reference consumers and report behavior were not exercised.
- Execution scope: historical SCM-1 performed five saved-ROI pretrained batches and remains closed. The separate-role follow-up audits saved vectors/qualification/source coverage. The later liquid adapter binds the actual user reply for 1463 and prepares one exact water-C correspondence using saved pixels/edges. It executes no model, fit, decoder, temporal propagation, machine-created physical labels, production changes, sequence/report replay or Windows qualification.
- Logic-map impact: NONE — this experiment changes no executing production owner, Recipe setup, candidate selection or typed runtime contract.
- Failure-registry impact: NONE — the existing appearance/identity limitations remain; this record adds the scoped semantic-union counterexample without claiming a general theorem about all pretrained models.
