# Foam structure context and physical-reference gap

Date: 2026-10-06. Source base: `de3ef6ce5d4ddf5f9eb09d86700d53b570c50da4`.
Scope: saved rasters/metadata and pinned recipes only. No video decode, detector
run, production change, formal label edit or Windows rerun.

The [frame480 rim attribution](../../60-evidence/s11/2026-10-06-foam-edge-selection-feasibility.md#frame480-orange-c1-confirmed-glass-rim--2026-10-06)
closes the physical identity question for that displayed C1. This investigation
reuses `s11_foam_support_geometry.measure`, `_structural_support_boxes` and
`_structural_substrate_relation`; no second runtime structure owner is added.
Repository search found configured ellipse masks and artifact-template geometry,
but no registered physical rim contour for these recipes. All three recipes have
zero artifact templates. The crop ellipse cannot silently become that reference.

## Measurements and checks

All retained components from the original three-frame capture and the two-time
capture were included: five frames, 23 components and 84 ordered distinct
component pairs. All 152 read input files were hash-preserved. Captured pixel
counts/boxes agree with the label rasters; replay of the existing structural-box
and substrate helpers matches the recorded predicates for all23 components.
Configured-ellipse radial coordinates were checked under joint translation and
uniform scaling. Seventeen existing geometry controls pass, including identical
boxes with different actual support and missing/masked corridors.

For each support pixel, `rho = hypot((source_x-cx)/rx, (source_y-cy)/ry)` uses the
**configured recipe ellipse**. Pixel quantiles are descriptive geometric values,
not distances to a verified physical rim, material scores or candidate rankings.
The recipe IDs match the captures and recipe hashes match the original inventory.
No ellipse fitting, threshold search or negative-to-positive label conversion ran.

| Same-frame C2 relative to C1 | Box below gap | Actual fully visible below-support gaps | Columns within existing 12px gap bound |
|---|---:|---|---:|
| sample4:420 | −8px | 20–28px | 0 |
| sample4:450 | −4px | 22–29px | 0 |
| sample4:480 | 12px | 28–35px | 0 |

These are gaps strictly between support pixels, not between inferred physical
surfaces. At420/450 the old broad box relation reports substrate; at480 C1 is not
classified structural, so it supplies no structural box. Actual-column placement
explains why broad-box association can reject separated material support, but
removing that veto alone cannot establish a correct Foam front: earlier C2 review
contains both Foam and central structure edges. Base/sample2 C2–C1 pairs have no
common support columns; their below-gap values remain null, not zero/infinite.

| Case/component | rho minimum | median | maximum | Review scope |
|---|---:|---:|---:|---|
| sample4:450 C1 | 0.542 | 0.656 | 0.809 | confirmed rim at450 |
| sample4:480 C1 | 0.532 | 0.643 | 0.740 | confirmed rim at480 |
| sample4:480 C2 | 0.019 | 0.272 | 0.516 | human boundary points; no pure-mask truth |
| sample2:30 C1 | 0.844 | 0.869 | 0.897 | confirmed rim |
| sample2:30 C2 | 0.000 | 0.576 | 0.920 | Foam region with suspected reflection; mixed support |

The same physical class occupies different recipe-relative radii. A global
peripheral exclusion would miss the sample4 rim or risk censoring other material.
This observation rejects treating the current ellipse or a fitted radius cutoff
as physical truth; it does not prove that calibrated structure context cannot
help. It also does not label all sample2 C2 pixels as true Foam at the wall.

## Prepared checkpoint before the double-rim clarification

Physical C1 identity is already known. The missing input is the location of the
**inside edge of the glass rim**, distinct from the configured crop ellipse and
from the already reviewed Foam upper edge. The new frame480 view requests about
6–10 approximate points on visible left/bottom/right portions of that inside
edge. Obscured parts can be skipped, or the user can state not assessable. Do not
interpolate skipped portions, fit a closed circle, infer rim thickness, generate
an exclusion mask or apply the points across frames without separate support.
This is development reference evidence, not a required new runtime calibration.

Why ask now: actual-pixel geometry has resolved the old box association issue,
and the user has established the rim's identity, but neither supplies a complete
physical rim boundary for testing structure-reference proposals. The candidate
mask is a detected subset, not a physical outline. Using the recipe ellipse or
that mask as the outline would substitute an unverified proxy for the missing
reference. Preserve sample2's mixed/reflection qualification and the missing
Base Foam support as opposing cases in any eventual behavior repair.

The page is self-contained, preserves source coordinates, supports point undo,
JSON download and separate localStorage keyed by report hash. It does not read or
modify the previous Foam click page. Existing C1 pixels can be toggled; the
configured ellipse is off by default. No path is fitted through clicks. User
submission/attribution is supplied by the subsequent human reply, not inferred
from a browser autosave.

Safari did initially open its file chooser. The explicit **Open** action was then
completed, and fresh AX plus screenshot verified the rendered original/overlay
page. A temporary test click produced a source coordinate and was undone;
`points=[]` and count0 were verified before handoff. No test point is human truth.
Do not report success merely from entering a file URL in Safari.

## Local artifacts

Directory: `sample/output/s11-local-foam-structure-context-001/` (private, ignored).

| File | SHA-256 |
|---|---|
| `run.py` | `47f97eb94af16d05ee3709572eafd22b56bd7709e83d5bc7a500a35da16a5c06` |
| `report.json` | `8c4989c3c1dc599826d3b6b19acdaad9af946efaf1a4e90f5186838061a8e0f5` |
| `receipt.json` | `da86e9a1b6afdae9f0435d18ae0e3433e2ee0f03960d40384c9e5fd2a4ba3b90` |
| `rim-review.html` | `3449b6726663f2cdca34fe67c772b4befe91f6fe943cf80e7a148a349cbba051` |
| `review-receipt.json` | `b89259fe32f5e560fe97ca9088eb4fc9ee3ba5190037004921dd396a3e76fd5b` |

The measurement receipt pins four outputs including the runner and all152 input
files. The separate review receipt pins two inputs and the HTML/builder. Complete
per-column arrays remain local. No measured output was overwritten.

## Double-rim outer points received — 2026-10-06

The user completed the Safari input and clarified:

> 완료
> 근데 한가지 알려주고 싶은게 있음. 테두리가 2중임 내가 지금 찍은건 테두리 중 바깥 경계임.

The downloaded JSON contains18 points (18 distinct XY;17 distinct X) for the
exact frame480/Glass/run/record already pinned above. All points are inside the
saved crop. The raw1443-byte download is retained byte-for-byte. Its hardcoded
`role=glass_rim_inner_edge` is **superseded by the human clarification** in a
separate attributed reply: `user_marked_outer_boundary_of_double_rim`.
Likewise, `visibility=not_submitted` was a page default; completion is attributed
to the chat reply, not inferred from autosave. Raw JSON remains unchanged.
The user's wording does not specify a full physical annulus or its thickness.

At each marked point's exact X, compare only saved support pixels. Signed
differences below are `nearest_support_source_y - marked_source_y`, positive
down. No line is interpolated between marks; no tolerance is introduced.

| Saved component | Marks with same-X support | Exact marked-pixel hits | Nearest signed Y difference |
|---|---:|---:|---|
| C1 (human-confirmed rim) |9|0|+1 to +5px|
| C2 (reviewed Foam/structure mixed support) |6|0|−28 to −23px|
| C3 |4|0|−61 to −41px|
| C4 |2|0|−16 to −12px|
| C5 |1|0|−27px|

All five retained components are reported; missing common-X support is null,
not evidence that a physical feature is absent. Approximate human points need
not coincide with support pixels. These distances neither contradict the user's
C1 rim attribution nor establish an inner boundary. Existing frame480 Foam
clicks are retained and joined only where X matches; they are not rim points.

This closes the outer-reference recording step. The two physical boundaries
must remain distinct before testing how a structure reference relates to the
interior observation area. The current saved support/recipe ellipse cannot
provide the missing inner boundary or a rim thickness. A separate page therefore
keeps the18 outer points fixed in white and requests approximately6–10 blue
points on the visible inner boundary of the double rim, nearer the observation
area. Obscured portions can be skipped, and not-assessable is an explicit answer.
This is a location question, not another C1 identity or Foam-edge judgment.

The page reuses the earlier viewer and source image with a distinct storage key
and download name. Outer-reference hash is embedded in its new reply. C1 and
recipe overlays default off. The Safari file chooser was explicitly completed;
AX and screenshot verify the rendered image, white outer marks and zero new
inner points. Old tabs and inputs remain intact. No automated test clicks were
added in this page.

Local directory: `sample/output/s11-local-foam-rim-reference-001/` (ignored).

| File | SHA-256 |
|---|---|
| `browser-reply-raw.json` | `47762c97782412416965bdb7508d58277067ff6a14315b99eafde960fe12b822` |
| `reply-attribution.json` | `d40fc173e5ff4e03fe05dc7dfe620790148da016a2ff4a06f649e79ad7560b45` |
| `correspondence.json` | `f5ecfe2b7cca04c0c5f57d6c0a59d0116ba2e483f229f37dabb6b028e64a2ba8` |
| `record_reply.py` | `a0843dee75e7b3f6927608c26f1230012b9121c9dffc2147e1a9e559ce54701f` |
| `receipt.json` | `69e04ff3ad41cad0aa6d8f61ef681b035b8396c6bd0af8923f58a13853aa8434` |
| `inner-rim-review.html` | `7802c8751d2bf941be5abd7bd5c143544ec9fe325e31a7358ee0bc2e719846e0` |
| `review-receipt.json` | `f31a9c3065ec105b09558ec95ed8ba8217b825dd77afda5bf6217287a9895c52` |

Eleven direct input files, including both earlier receipts and their pinned
outputs, are verified unchanged. The new receipt pins four outputs; the separate
review receipt pins the reused inputs and two viewer outputs. This is not a new
152-input audit, decoder run, detector run or geometry-test run. Runtime, recipes,
formal labels, Windows target truth and all acceptance gates remain unchanged.

## Inner points received with click uncertainty — 2026-10-06

The second Safari reply contains21 inner-boundary points (21 distinct XY,
20 distinct X), bound to the same frame480 identity, source-report hash and the
outer attributed-reply hash. The user submitted the reply with this qualification:

> 완료했어, 마우스로 클릭하다보니 픽셀이 약간 오차가 있을수있음

The raw1679-byte download is preserved. Completion is recorded from the chat;
the page's `not_submitted` default is not human uncertainty or a missing reply.
`localization_uncertainty_px=null` means no numeric error bound was supplied.
Do not turn “약간” into an invented ±1/2/3px tolerance, snap clicks to image edges,
or require the user to repeat the completed annotation to obtain pixel truth.
The point-location checkpoint is complete at this approximate evidence level.

All five saved components were compared at the marked source X only. Values are
nearest support Y minus inner mark Y, positive down; these are recorded coordinate
differences, not calibrated physical distances or certified inside/outside labels.

| Component | Inner marks with same-X support | Nearest signed Y difference |
|---|---:|---|
| C1 (rim, previously human-confirmed) |13|+8 to +15px|
| C2 (Foam/structure mixed support) |9|−22 to −17px|
| C3 |7|−58 to −31px|
| C4 |3|−7 to −1px|
| C5 |1|−19px|

No inner mark coincides exactly with a component pixel. C4's1px difference is
particularly unsuitable as a robust side/identity claim under unknown click
error. At the five exactly shared X coordinates of the two rim replies, outer
minus inner Y is6–9px. This is sparse vertical separation of two approximate
mark sets, **not rim thickness**. Missing X is not interpolated; repeated X with
different Y is preserved. Existing Foam points remain a separate reference.

The evidence supports retaining distinct rim and material spatial references for
development; it does not establish a general detector. In particular, C1 must
not be automatically relabeled as occupying the entire strip between the marks:
its saved support also extends below the outer marks, and the two named physical
boundaries do not define a complete exclusion region. Inner/outer clicks are not
propagated to frame420/450, sample2, BASE, or the Windows truth snapshot.

### Existing-owner reuse assessment and implementation choice

Source inspection follows the existing caller rather than adding a new rim
classifier. `GlassGeometry` stores a crop ellipse, rectangular exclusions and
point/line/region `ArtifactTemplate` entries. `roi_editor_dialog.py` owns template
registration; `artifact_calibration.py` owns matching. These templates do not
store two sampled rim curves or click uncertainty. They are not a lossless
representation of this reply.

In `CurrentFrameEvidenceOwner.observe`, the Foam path calls
`attach_spatial_signature` and `apply_artifact_templates` **after** spatial
component selection and the temporal gate have yielded a Foam candidate. A
matching template clears that candidate; this path does not rerank the retained
components to restore C2. Registering the clicked lower rim as an existing
template therefore cannot by itself repair both C1 false admission and the
earlier C2 substrate veto. No such registration or runtime replay was performed.

The initial follow-up mistakenly asked whether to add one-time rim registration
or automatic inference. The user corrected that premise: the existing app already
lets the human specify the detection ellipse, intended to bound the interior.
The user also clarified that the Mac video regions were **agent-created through
image analysis when the recipes were prepared**, not personally set by the user.
This resolves the question; no additional input contract is needed. The prior
source search identified the fields but missed their existing operational purpose.
The lower-rim admission must first be assessed against the agent-prepared ROI,
not treated as proof that a new rim classifier or registration UI is required.

Local directory: `sample/output/s11-local-foam-inner-rim-reference-001/` (ignored).

| File | SHA-256 |
|---|---|
| `browser-reply-raw.json` | `547835d9902c349d7c1effacd921f6cc036be9afbb51d75bd3e5ab914b5c85e7` |
| `reply-attribution.json` | `93ea9608f364d18d9f25e04c2bce85ea2edcda8119a6212f36c03ce6ed46da1a` |
| `correspondence.json` | `e474806681b620b0302df296d0e824b652d40159494fac92dd33041d496f1443` |
| `record_reply.py` | `17001a23c63fec56fbee5bec36e70d1e6357e022814133cb291461d6cfbc6be3` |
| `receipt.json` | `63dc2193fb12fd22ba8c63e845f3cd5b4881e790e578149d605fcb7a81969177` |

Sixteen direct input files are verified unchanged; the receipt pins four outputs.
Point counts, ordered coordinates, crop bounds, exact identity/hash joins and
all saved-component comparisons are asserted. Full arrays and user raw downloads
remain local. This does not rerun the earlier17 geometry tests or any detector.


## Existing ellipse/margin contract and saved-mask replay

The product specification §6.3 explicitly says Detection Margin exists to prevent
locking onto the glass rim/gasket. `RoiEditorDialog._ellipse_changed` updates the
working Glass ellipse; `VideoOverlayCanvas._add_selected_overlays` shows the
inward margin. `build_mask_bundle` derives the bounding crop, rasterizes the
ellipse, shrinks its axes by `1-margin_ratio`, and removes exclusions. The same
`effective_mask` is passed to preprocessing and `detect_bottom_connected_foam`
by `CurrentFrameEvidenceOwner.observe`. Thus the ellipse is **both** the source
of crop bounds and the user-controlled detection-domain geometry. Calling it
merely crop geometry was incomplete. It still is not automatically verified
physical truth when an agent selected it.

A bounded replay calls this existing mask builder on a blank full-size canvas
(the RGB values do not affect geometry; no video is decoded), using each pinned
recipe. Across all five saved frames, effective-mask pixels match the captured
mask exactly (0 mismatches), and all23 retained components have zero pixels
outside that effective mask. The original capture/recipe files remain unchanged.

For sample4, the saved supporting recipe specifies center(595,850), radii(52,52),
margin0.08 and no exclusions. Runtime raster axes after margin are(48,48), with
source mask bounding box[547,802,644,899). Frame480 C1 has313/313 pixels inside
this mask; all21 approximate inner-rim marks are also inside. The selected ROI
therefore includes the human-confirmed rim: this is not evidence of mask leakage
or an ignored ellipse. Its description explicitly identifies a deterministic
supporting-evidence recipe, not canonical detector truth. User attribution owns
who set it; Git history is not used to infer a human review that never occurred.

The earlier score/gate diagnoses remain descriptions of behavior **under that
broad saved input**. They do not establish failure under a human-corrected ROI.
Changing the recipe is a distinct input intervention, not a detector improvement;
keep the old run intact and compare both inputs explicitly. A corrected ROI will
not by itself settle central structures or mixed Foam edges that remain inside.

Mask artifacts in the inner-reference directory:

- `mask-audit.json`: `9e827708c9e508348b39d96d373f159852bfb04d2929491ea00d8f39417ab818`
- `mask-audit-receipt.json`: `90338da4625727e242dc0aa003a8028a19f6a8b21e9013be9221930a714e40fc`

The receipt pins the runner/report and26 direct inputs. It covers geometry-mask
replay only; it emits no Oil/Foam predictions. Two existing mask controls pass.

### Existing ROI editor handoff

A local launcher `review_roi.py` reuses the product's `RoiEditorDialog`, without
adding a new registration workflow. It displays the saved frame480 RGB crop at
its native104×104 pixels, translates the existing ellipse into crop coordinates
for editing, and restores source coordinates in the output. No video decode is
needed. The original recipe is never written: Apply exports only
`sample4-roi-proposal.json` with the old/new ellipse, origin and recipe/image hashes;
Cancel saves no proposal. Other recipe fields, including margin, are preserved.
Only the ellipse proposal is collected in this bounded handoff. A subsequent
local run must use a separately identified recipe and recheck the material
controls; these point annotations are not fitted into a replacement ellipse.

The native window's accessibility state and screenshot verify the saved RGB,
ellipse handles, inward green margin and Apply/Cancel controls are visible.
`roi-editor-handoff.json` pins the launcher, original recipe/image and existing
UI owners. No ellipse edit or Apply was performed by the agent.

## Human ROI applied and bounded comparison — 2026-10-06

The user completed Apply in the existing editor and confirmed “수정해서 적용했어”.
The exported source-frame ellipse is center(594.4975845410628,839.6167471819646),
radii(38.267310789049915,33.913043478260875). Only that ellipse changes in a
separate `sample4-human-roi.oilrecipe`; original recipe bytes, margin0.08,
zero line, settings, labels and reviewed points remain unchanged. This is an
input correction using the app's existing contract, not a detector-code change.

At source `ce55d48605a3d28fd07a07672a16ec4690aacf7b`, eight independent
current-frame calls compare original and corrected ROI at sample4 frames420,
450 and480, plus original-ROI BASE156 and sample2/30 controls. Each call starts
with a fresh detector; no temporal/completed-window acceptance is claimed.
Saved full-frame RGB is reused where available; frames420/480 are decoded at
exact frame indices, with exact equality to the previously saved review crop.
All five original-ROI component diagnostics and positions reproduce the saved
baseline. The older three-frame capture predates the optional diagnostics in
`temporal_raster_evidence.py` (`1d4343a`); the source difference is explicitly
recorded, and baseline equality is asserted rather than assuming identical code.

Corrected crop origin is[556,805], shape[69,77], effective support3515 pixels.
The table uses original diagnostic component IDs, not new rank IDs:

| Frame | Original C1 pixels remaining inside new mask | Original C2 pixels remaining | Original C2 overlap with newly selected support | New Foam spatial status / source Y | Current-frame Oil Y |
|---|---|---|---|---|---|
|420|25/560|320/320|297/320|accepted_strong /841|854|
|450|0/514|335/335|289/335|accepted_strong /839|854|
|480|0/313|337/337|319/337|accepted_strong /833|null (ambiguous)|

The retained C1 pixels at420 do not overlap the new selected support. All22 raw
Foam clicks at420 and38 at480 remain in the corrected effective mask. Pixel
retention is not proof of front accuracy: C2 was already reviewed as containing
both Foam and central structure. The newly selected upper support still shows
that central rise; the crop correction does not resolve it. Component shapes and
scores also change because cropping alters preprocessing support and normalized
geometry, so this is not simply deleting the old C1 from an otherwise fixed list.

All three corrected spatial candidates have no structural-substrate predicate;
all remain `persistence_pending`, with null current-frame Foam output. Fresh
single-frame state cannot establish a Foam episode. Current-frame Oil becomes
854 at420/450, while480 stays ambiguous. The earlier450 human Oil-path record
near853 is relevant context but does not label the new420 output or certify
localization. BASE156/sample2/30 preserve their previous diagnostics and null
Oil/Foam outputs; this does not qualify their agent-prepared ROIs as human truth.

### Analysis correction and artifacts

The initial local helper mistakenly indexed the saved rank raster with its
original generator `label`. `foam_component_labels` contains `diagnostic_id`.
`support-analysis.json` explicitly supersedes **only** the initial report's
`historical_support_retention` fields, joining by diagnostic ID and asserting
each pixel count against the saved component. Detector outputs, input hashes,
positions and baseline equality are unaffected. Both reports/receipts remain
preserved; the table above uses the corrected support analysis.

Local output: `sample/output/s11-local-human-roi-comparison-001/` (ignored).

| Artifact | SHA-256 |
|---|---|
|Separate recipe|`8f67b4120f20c4222645ffb3b5d25b971de9c3dacdea506238902d98e439543b`|
|`report.json` (support-count fields superseded as above)|`b43f4156794f04b1cd56d75c6b6eed3a0fb6d29794db3edf132968cac4fa51ff`|
|`receipt.json`|`75d1a9e658401a808e278295eb7edb6cac88444d97130d067c7593ee3e1a7afe`|
|`support-analysis.json`|`a4b16d8d8c80743e83b837e73373a39c8e94556088a2def63e1fc541b26e6a5b`|
|`analysis-receipt.json`|`4b1534c3a8aae2e7dac0fcd51c481f48d88dfa253754177d5069e75b202f7d90`|
|`review.html`|`0be9d0f1f022b0934d4a2951eb3b6d46227bc4eccbd290fc9a6725cf1857f3ee`|

The run receipt pins203 outputs and32 preserved inputs. The analysis receipt
pins its three outputs and saved inputs. Source files remain unchanged.

### Next human checkpoint

Safari **수정 ROI — Oil 위치 확인** displays the same original RGB crops with a
switch to hide overlays. Magenta is the current-frame Oil scalar, drawn only
across effective-mask support; it is not a measured contour. Cyan shows the
selected spatial Foam support and its column-wise upper pixels, not confirmed
Foam publication. The native browser page and image rendering are verified.
The specific open question is whether **frame420/14s Oil Y854** is the actual
Oil–Foam boundary, near but offset, or another/uncertain feature. Existing Foam,
rim and central-structure judgments are retained without asking them again.
No Windows run or formal truth/label transfer is requested.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: the agent-prepared detection ROI includes the rim. Under that input, spatial structure admission misses the confirmed narrow rim and broad-box substrate association also opposes separated material. Correct the existing ROI before attributing remaining behavior to a detector deficiency under human-set geometry; removing gates cannot establish front identity.
- Logic-map impact: NONE — bounded same-code current-frame ROI comparison and local review viewers do not change production owners or acceptance authority.
- Failure-registry impact: NONE — geometry-as-identity, blanket masks, global cutoffs, private Y branches and cross-material authority remain prohibited; no replacement mechanism is promoted.

FIELD FAIL / NOT_EVALUATED, O2 open and W5/O3 gated remain. No Windows work is
needed at this checkpoint. The [work plan](../../00-project/work-plan.md) owns
current state and the subsequent transition after the new Oil-position review.
