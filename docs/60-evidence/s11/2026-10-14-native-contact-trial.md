# NCT-1 — ordered native-side contact interaction

**Disposition: CLOSED WITHOUT PROMOTION.** Separate targets and the side-interaction
term do not preserve the required controls. No production change or threshold retry
follows. All preceding physical replies retain their original meaning.

## Frozen protocol

This trial tests whether the **combination of two native side appearances**,
with separate Foam/liquid targets, preserves qualified uppers while rejecting
internal changes and structures across exposed source recordings. The
[architecture contract](../../20-architecture/s11-contextual-role-observation-design.md#ordered-side-contact-interaction-trial-nct-1)
defines the fixed kernel, loss, split, operating point and stop rule. Its joint
term differs from the closed native head's additive side score; the additive
and mean-RGB arms isolate that distinction without changing data or geometry.

Inputs reuse the [complete role corpus](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus.json):
109 paths, 84 available native inputs, 17 qualified roles, 92 unknowns, four
recordings and six frames. The runner revalidates the complete corpus and all
source/path/RGB pins before fitting. All 48 saved semantic observations remain
unchanged and unused. Water C requires no new encoder output.

Exactly three arms × four held-recording folds × two independent targets are
fitted: **24 deterministic float64 solves**, using fixed ridge 0.01 and a zero
operating point. Class/source/path balancing prevents the four Miso uppers from
counting as four independent recordings. Opposite positive roles and N1 remain
partially specified; no pure patch labels or new negative truth is invented.
Unknown paths receive diagnostic predictions but no evaluation truth or fit loss.
Unavailable paths receive null scores, and UNKNOWN never counts as correct
opposition. No arm or hyperparameter is selected after inspecting outcomes.

The primary necessary condition is **14/14 Foam controls, 10/10 liquid controls
and N1's disjunction** on held-source predictions. Fitting results are separate.
Any failure closes this fixed operation without promotion. A control pass cannot
establish general classification, an untouched holdout, calibrated confidence,
raw-front recovery, a production consumer or Windows field effectiveness.

Execution entry: `tests/diagnostics/s11_native_contact_trial.py --root <repo>
--plan <plan.json> --output <managed-work>/readout.json`, from `/private/tmp`.
Source, tests, exact input pins and this protocol are frozen at a clean commit
before the run. Current Python/NumPy/Pillow are used, with BLAS/OMP thread limits
of one. Bound execution to 120 s, 1 GB RSS, 8 MB scratch and 3 MB retained. No
retired runtime/model is restored. Retain complete compact scores, final dual
coefficients, source/feature hashes and verification; remove owned intermediates.

## Result and verification

The code, tests, [plan](../../50-diagnostics/s11/2026-10-14-native-contact-trial/plan.json)
and protocol were frozen at **`c40d46e46809d03e4192d13456b9197790b6aeda`**.
The [complete readout](../../50-diagnostics/s11/2026-10-14-native-contact-trial/readout.json)
retains all 109 paths, all 24 fitted coefficient sets and all three arms:

| Held-source result | Native joint (primary) | Native additive | Mean-RGB joint |
|---|---:|---:|---:|
| Foam control decisions correct | 8/14 | 8/14 | 10/14 |
| Liquid control decisions correct | 7/10 | 7/10 | 7/10 |
| N1 disjunction supported | 0/1 | 0/1 | 0/1 |

These are 24 channel-specific control decisions over overlapping native subjects,
not 24 independent recordings. All arms lose the certain Foam upper N3 and both
liquid positives (Miso 1463 and water 1378). The primary Foam channel also accepts
all three Miso rims and both milk cup structures. Its liquid channel accepts N4's
internal Foam change. Native/additive decisions agree on every required control;
their 2 Foam / 18 liquid differences occur only on unreviewed paths. The interaction
term therefore demonstrates no required-control benefit. Mean RGB's two additional
correct rim decisions do not erase its positive losses or select it for adoption.

Fitting is not confused with held-source evaluation: primary liquid fits classify
all their fitting controls correctly, then lose both source-held-out positives.
Primary Foam fits themselves retain one error in three folds. The result rejects
this fixed operation; it does not prove a universal impossibility for local RGB
or establish that contact/source confounding caused every failure.

[Verification](../../50-diagnostics/s11/2026-10-14-native-contact-trial/verification.json)
records **47 focused tests passed**, including 23 new interaction, independent
primal/dual arithmetic, partial-target, source-isolation and CLI guards. A separate
image/JSON calculation verifies all 1,130 native patch tensors, 252 feature hashes,
24 normal equations and 504 held-source scores from saved coefficients without
another fit. Maximum score error is `2.22e-14`; maximum equation residual is
`4.35e-14`. Its first audit used a different array memory layout; adopting the
already-declared contiguous tensor contract reproduces all hashes. Trial code,
coefficients and outcomes were not changed.

The actual CLI ran from `/private/tmp` in **1.0043 s**, with **177,242,112 bytes**
peak process RSS. This is an offline control trial, not detector throughput.
The current Python 3.14.4 / NumPy 2.5.1 / Pillow 12.3.0 environment was sufficient;
no model or retired environment was restored. The plan, complete result and
verification total **209,389 bytes** in one canonical folder. Managed run
`sample/output/s11-native-contact-trial-20261014-001` references those files rather
than keeping duplicate media/tensors. O2 OPEN, FIELD FAIL and Local XY OFF remain.

## Next evidence boundary

The native liquid corpus has one **Foam-contact** positive in Miso and one
**air-contact** positive in water. Each contact type currently occurs in only one
recording, so holding either source out also removes that contact type from fit.
This is a coverage limit, not a proven causal explanation or license to retune NCT-1.

Reuse the earliest non-initial accepted sample4 candidate, f1140 idx9, only to
locate a new correspondence review. Its scalar Y844/pooled generator support does
not label a native edge. In the existing source ROI, the horizontal transition
has the already-saved row Y841 and one incident fragment, 708. Prepare that entire
path and retain the complete frame inventory, with no model score or length-based
selection. Ask its physical contact role only after source/path/display checks.
N5 is a different frame and the previously rejected f1140 candidate rims stay
rejected; none supplies 708's answer. A reply may extend scoped contact diversity;
it will not reopen this kernel trial or imply a successful detector.

### Prepared 708 correspondence review

The [source manifest](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-manifest.json)
and [complete inventory](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-native-readout.json)
retain **26 native paths: 16 with partial context, 10 unresolved orientations**.
The [preparation plan](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-plan.json)
selects every fragment at the visually located, still-unlabelled source row Y841:
exactly one, 708. This is not a nearest-Y truth join to the Y844 candidate.
The [proposal](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-proposal.json)
contains all 35 saved vertices, and the existing qualifier's
[inspection](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-inspection.json)
returns `PROPOSAL_VERIFIED_PENDING_REVIEW`, **zero qualified subjects**.

The [direct PNG](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review.png)
shows the entire 104×104 glass ROI at 5× nearest-neighbor scale, plain on the left
and with the exact path on the right. No new video decode or estimated contour
was used. The new question is whether that displayed path meets Foam and liquid,
liquid and empty space, or has another/unreadable role. It does not reopen prior
candidate approvals, rim judgments, N3/N4 or the milk lower-boundary uncertainty.

[Display verification](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-verification.json)
confirms original crop equality and exact overlay vertices/hash. Each side has
15 complete patches; three pixels per side touch/cross the saved path, so these
remain mixed context, never pure material labels. Both existing qualifier CLIs
ran from `/private/tmp`. No score, fit or corpus qualification was added.

Managed run `sample/output/s11-native-contact-review-20261014-001` preserves these
seven files (**143,468 bytes**) in one canonical folder and removes its temporary
plans. The original 109-path/17-role corpus stays frozen. Only the new exact
physical correspondence is pending before dependent work continues.

Both runs are closed with no duplicate working payloads. All **56 managed runs**
pass the artifact check; governance and whitespace checks pass. Focused links
across the changed owners pass (281 local links / 51 anchors). Commit/push preserves
the failed experiment and pending review; neither action adopts detector behavior.

## 708 reply and append-only contact extension

The subsequent exact user reply is **“거품 하단과 액체의 경계”**. Bind it only to
the displayed 35-vertex fragment 708 as `FOAM_LOWER_LIQUID_INTERFACE`: a definite
bulk-liquid-upper relation, not Foam upper, pure side materials, motion, an exact
product scalar or a whole-layer label. The original proposal/inspection above
remain the pre-reply checkpoint. The new [reply](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-reply.json)
pins that subject and display; the candidate's Y844 remains separate from native Y841.

The [extension reader](../../../tests/diagnostics/s11_native_role_extension.py)
reuses the frozen corpus reconstruction, native-packet validator and liquid reply
qualifier. A separate append entry is necessary because the original corpus and
NCT-1 source pins are frozen. It retains only the new frame's complete population
and a base-corpus pin, rather than duplicating all 109 earlier rows. It must reject
an incomplete population, conflicting source/frame/path, old-frame replacement,
role overwrite or changed original pixels. Unknown and unavailable paths remain
explicit; no semantic vectors are fabricated.

Before execution, the [extension plan](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension-plan.json)
pins code, tests and inputs. The actual entry is the extension CLI with absolute
paths from `/private/tmp`; retain the delta and verification only, with 2 MB
scratch / 300 KB retained. Independently check the new patches directly against
the original image and all earlier rows against the pinned corpus. Count positive
recordings separately for Foam-contact and air-contact, grouping every sample4
frame together. This binding is not a new fitting operation or NCT-1 retry.

Execution at **`f4339e8`** completed from `/private/tmp`. The
[delta](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension.json)
adds all **26 paths**, with exactly one qualified contact and 25 unknowns. The
combined population has **135 paths / 18 qualified / 117 unknown**, 100 available
native inputs and the same 39 saved semantic inputs, in four recordings / seven
frames. The 18 are 6 certain Foam uppers, 3 certain liquid uppers, 2 internal
changes, 6 structures and N1's original disjunction. Sample4 f450/f1140/f1620
stay in one source group; adding a frame does not add a recording.

[Independent verification](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension-verification.json)
checks all **264 new native patches / 32 side hashes** directly against the original
PNG, all 109 earlier rows unchanged, complete new-frame inventory and source-group
separation. **51 focused tests pass**. The delta and receipt total 130,918 bytes;
managed run `s11-native-contact-bind-20261014-001` retains only canonical references.
No model was loaded, fitted or scored, and no detector behavior changed.

Foam–liquid contact now has **two positive recordings** (Miso and sample4).
Liquid–air contact still has **one** (water), even though water A/C are two frames.
This clears only the first contact type's source-diversity gap. It neither certifies
native training readiness nor changes NCT-1's failed result. The next bounded
reuse check concerns the already exposed sample3 A/f2249, whose baseline input
was available; B/f2339's missing baseline input and unadopted overlay guard are
not a substitute. Existing regional/candidate replies do not supply an exact
native-path contact label. No new clip, whole-window benchmark or automatic fit
is authorized by this source check.

### A contact-type review and native representation limit

The bounded read-only A/f2249 check reproduces the archived RGB and visibility
hashes using the baseline preprocessor from `747c1bcc` (SHA-256 `55e33486…`),
the unchanged saved Recipe and original full-frame PNG. The resulting Canny
raster has **no visible vertices or fixed-column fragment**. This differs from
the existing candidate's available 95/95 RGB patches: candidate context availability
does not imply that the native-edge representation contains a boundary. It is
not a new claim that the production detector has no candidate or output.

The [source-only preparation](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-plan.json)
therefore asks only the **contact type at the already accepted A point**. The
rendered yellow cross is a point, never a fabricated horizontal edge. The complete
original ROI and full-frame locator retain context; all existing A/B candidate
acceptance, B's fluid–empty-space reply, C/D judgments and whole-window quarantine
remain intact. No user label is transferred from B to A. The question is whether
liquid there meets empty space or Foam, another boundary, or cannot be assessed.

This is a narrow source-qualification extension of the Work Plan, not routine
sample3 development or tuning. A reply can constrain the contact scope of a
separate representation design; it still cannot supply a missing native path.
Do not lower Canny thresholds, invent a contour from Y219, apply the unadopted
overlay guard or retrain a closed operation to clear the gap. Once contact scope
is known, distinguish existing candidate-level observations from a separately
designed/tested native representation before any future model contract.

The [review record](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-review.json)
and [direct PNG](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-review.png)
retain the exact source/candidate pins and empty native population. There are
38,311 visible ROI pixels but zero Canny pixels; available candidate-side context
therefore must not be reported as a ready native-path input. The original baseline
preprocessor is loaded by the existing comparison helper, not substituted with
the unadopted current guard. This question creates **zero new native labels**.
[Independent verification](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-verification.json)
checks every plain/point-panel pixel and reproduces the zero Canny raster directly
from original pixels, unchanged Recipe thresholds and baseline operations.
The image was visually inspected with its full-frame locator. The actual CLI
ran from `/private/tmp`; owned font caches and temporary plans are removed at
managed closeout. Only the physical contact-type reply is pending.

The first artifact check found 6,437,055 scratch bytes against the 5 MB plan:
imported reporting dependencies had generated font caches. After the writer
stopped, those owned caches were removed without losing scientific payload or
changing the original budget record. Managed run
`s11-native-contact-a-review-20261014-001` retains 142,284 bytes in five canonical
files. Both new runs are closed; all **58 managed runs** pass with no remaining
artifact errors. No retired model/runtime or duplicate source media was restored.

### A contact reply received

The user subsequently replied **“액체–빈공간”**. The
[attributed reply](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-reply.json)
binds that answer only to the existing A/f2249 candidate point. It adds no native
label or pure-side, motion, exact-Y or whole-window truth. The earlier pending
review remains an immutable pre-reply record. The 135-path / 18-qualified corpus
is unchanged, and NCT-1 remains closed. The separate
[raw-front audit](../../50-diagnostics/s11/2026-10-14-raw-front-inventory.md) owns the
next representation investigation; it cannot infer a contour from this reply.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: prior shared surface observations fail qualified uppers versus structure before candidate consumption. In the later A-only check, native-edge geometry is already absent before role input, although the original material-path candidate exists. These are separate representation and observation limits; neither establishes a repair or loss of the production candidate/owner/report path.
- Existing feature coverage: the closed NCT trial reused six pinned native frames and fixed 7×7 side footprints. The 708 extension adds one complete saved frame. The subsequent A-only check reconstructs baseline preprocessing/Recipe masks and matches archived RGB/visibility; it finds no native edge and changes no threshold, mask or candidate. Sample4 exclusions/templates remain empty and Local XY OFF; completed D2/Local XY failures remain controls. Session/static-learning, production candidate/episode and report paths are bypassed, so these operations cannot establish their efficacy or failure.
- Execution scope: the completed offline trial performed the 24 predeclared kernel solves; it stays closed. The extension CLI reuses the original qualifier to bind 708 and append the entire frame population without changing frozen observations. The separate A contact preparation reuses one original PNG, baseline preprocessing and the existing graph owner, then renders a point-only contact question; the empty native population remains empty. No additional model call, fit, source video decode, temporal propagation, model download, GUI, production sequence/report replay or Windows qualification. Existing replies are never expanded to native paths, pure-side labels or unknown-path negatives.
- Logic-map impact: NONE — this adds an offline research operation; no executing production owner, setup parameter or runtime schema changes.
- Failure-registry impact: NONE — separate-head/support testing refines the existing appearance and coupling risks; no accepted repair or new general failure theorem is claimed.
