# Public compressor source intake — 2026-10-12

The user identifies the bright horizontal layer's upper boundary near **50 s**
in [미소냉동's public video](https://www.youtube.com/watch?v=mHOS1-1ck60&t=50s)
as a Foam upper, and subsequently confirms its lower boundary as an Oil upper.
This is a new regional principle-check input. It does not supply exact pixel
truth, a continuous benchmark or a detector success. The
[Work Plan](../../00-project/work-plan.md) owns further work.

## Source and exposure

The [source-screen preflight](2026-10-12-public-compressor-source/screen-preflight.json)
was written before source viewing, bounded to at most two located public videos.
Only the first was inspected; the second was not acquired or evaluated. Browser
views near 25/50/75 s and a native view near 50 s preceded the separate
[12-view native review plan](2026-10-12-public-compressor-source/native-review-plan.json).
This is exposed development intake, never a reserved or blind holdout. It is
separate from the already closed S3 experiment and does not replace its inputs.

The [curated provenance](2026-10-12-public-compressor-source/provenance.json) records:

| Property | Retained value |
|---|---|
| Public source | `mHOS1-1ck60`, 미소냉동, published 2020-03-10 |
| Title | 압축기 오일포밍(Oil Foaming)현상과 대책_냉동기초 실무 |
| Local original | `sample/public_miso_mHOS1-1ck60.mp4`, ignored by the existing media rule |
| Size / SHA-256 | 13,480,200 bytes / `68ead21680534b7bbc06de9b556f5d3a2c4576dd7eaa85c6d50b90534daecc15` |
| Download | Public unauthenticated format 136; original video-only MP4, no audio or re-encode |
| Decoded metadata | 1280 × 720; 7,496 frames; OpenCV FPS 29.97002997002997; calculated duration 250.116533 s |

The publisher metadata rounds FPS to 30 and duration to 250 s; actual decoder
timestamps are recorded separately. The download used yt-dlp 2026.8.19 installed
only in a temporary directory and the existing macOS CA file for verified TLS.
No project dependency or authentication was added. The original download was
moved once into the ignored media location. No full video or transient signed
download URL is committed.

The full-file identity differs from the four retained original local sources.
The viewed hardware/framing also differs from the inspected sample4 first frame
and sample3's already-retained review image. This limited check is not proof of
whole-source or scene independence. No new sample3 decode or mining was performed,
and its retirement remains unchanged. The new source has no numbered sample alias,
Recipe or automatic corpus registration.

## What the views establish

The [renderer](2026-10-12-public-compressor-source/render.py) reuses the application
`OpenCvVideoReader` and existing diagnostic corpus-access guard. It does not call
a detector, invent a reader, create a Recipe or score physical accuracy. The
[native readout](2026-10-12-public-compressor-source/native-review.json) records all
12 requested/actual times, decoded indices and native BGR hashes.

The [lossless main frame](2026-10-12-public-compressor-source/native-at-50.png)
is frame **1499 at 50.016633333 s**, returned by a 50 s timestamp seek. It is a
near-time native reference, not a claim to capture the browser decoder's exact
frame at reported currentTime 50.023306 s. No exact frame annotation is inferred
from the user's regional browser judgment.

The [context sheet](2026-10-12-public-compressor-source/source-contact-sheet.jpg)
shows the fixed requests at 25, 40, 45, 48, 49, 50, 51, 52, 55, 60, 65 and 70 s.
Tiles are half-size context views, not measurement rasters. Inspection finds:

- At 25 s the hardware appears at a different size/angle and the glass is dark.
  The subtitle describes an Oil context; it is publisher context, not a new
  human-qualified Oil label.
- The bright layer is visible in the 40–55 s sampled views. The camera moves,
  changing the glass center; by the 55 s view it is substantially closer. These
  isolated views do not certify an uninterrupted physical event or stable Recipe.
- At 60/65/70 s the selected frames are explanation slides. The full recording
  must not be treated as a continuous measurement scene.
- Near 50 s both the broad bright layer and fine marks around/in the glass are
  visible. Their individual identity as bubbles, droplets, reflection or glass
  texture remains unqualified. Larger visible geometry alone is not accuracy.

The source therefore adds regional Foam/Oil **principle** context and a same-scene
role contrast: the layer's upper and lower boundaries have different target roles.
It does not yet add a numerically labeled **failure-response** benchmark, a
temporal **workflow** benchmark, a calibrated tolerance, or a replacement for the
existing qualified water/sample4 controls. The frozen seven-source P0 roster
remains an unchanged baseline; this intake is separately routed.

## Closed upper and lower judgments

The [verbatim upper-role reply](2026-10-12-public-compressor-source/upper-role-reply.json)
records **“밝은 층의 윗 경계가 Foam 상단으로 보인다”**. That question is CLOSED.
No exact X/Y, neighbouring-frame truth, timing or detector approval follows.

The [lower-role reply](2026-10-12-public-compressor-source/lower-role-review.json)
records **“아랫경계는 oil 상단 맞음”**. That question is also CLOSED. The bright
layer's lower boundary against the dark region beneath it is a regional Oil
upper, supporting an Oil/Foam role comparison within this scene. Neither answer
labels exact pixels or neighbouring frames; no exact pixel specification has
been requested. Do not repeat either physical-role question.

## Current-frame baseline and resolution preflight

The [four-call preflight](2026-10-12-public-compressor-source/current-frame-preflight.json)
freezes one source-prepared inner-glass ellipse and unchanged detector defaults.
It reuses `OpenCvPhaseDetector.detect` through the existing diagnostic Recorder,
with fresh state for native NONE/FULL and half-resolution NONE/FULL. All candidates,
diagnostic images/state and source-coordinate projections are retained. The
half-size input uses area resampling and explicit pixel-center coordinate mapping;
rounding remains with the existing geometry owners. No alternate Recipe or
parameter search follows a result.

This measures current-frame representation and local resolution sensitivity.
Both NONE/FULL pairs must agree before causal interpretation. It does not execute
a completed session, confirm an episode, evaluate continuity, test a new physical
selector, or reopen S3. Regional role judgments are evaluation context only; no
numeric precision/recall or universal minimum-resolution requirement follows.

<a id="fixed-result-and-remaining-position-review"></a>

### Fixed result and closed position review

The preflight was committed at `a486049` before execution. The
[saved readout](2026-10-12-public-compressor-source/current-frame/current-frame-readout.json)
pins the executed [runner](2026-10-12-public-compressor-source/inspect_detector.py)
and retains four isolated calls through the existing current-frame entry point.
The two NONE/FULL pairs have identical complete provisional detections.

| Current-frame observation | Native | Half resolution, projected to native source Y |
|---|---:|---:|
| ROI height × width | 210 × 228 | 106 × 115 before projection |
| Current Oil selection | 321.0 | 322.5 |
| Lower-region Oil hypothesis retained | 430.0 | 428.5 |
| Lower-region material-path candidate retained | 425.0 | 424.5 |
| Proposed Foam component front | 317.0 | 318.5 |
| Oil / Foam candidates retained | 22 / 1 | 19 / 1 |
| Visible center Canny intersections | 13 | 8 |

Both current Oil selections lie toward the upper bright-layer transition, while
lower-region candidates survive. This is a qualitative regional reading, not an
exact-position accuracy score. At native resolution the lower Oil hypothesis
has `typed_ambiguous_hypothesis`; at half resolution it has
`typed_not_temporally_selected`. In both cases the actual current decision is
`initial_shadow_boundary`. Those are current hypothesis/projection reasons, not
completed-window Oil authority results. A new edge generator or simply increasing
resolution does not address the entire observed role-selection problem.

Both Foam components are `accepted_strong` at the spatial stage, with evidence
scores 0.905995 and 0.890840. Both current Foam outputs are null because the fresh
temporal gate has one observation against its required count of two. This expected
first-frame pending state does not establish an episode miss or permission to
relax persistence. The native component front is outside the subsequently
reviewed Foam interval at the fixed column, as joined below.

The rounded native center is X578; the half-resolution center projects to X578.5.
The saved source-coordinate mapping reports this difference rather than pretending
the two sampled columns have identical pixel support. The perturbation also changes
pixel-based preprocessing and geometry rounding. It is one local resolution
sensitivity check, not proof that all old recordings are too small or suitable.

[Artifact verification](2026-10-12-public-compressor-source/current-frame/current-frame-verification.json)
checks eight logical capture outputs, 48 artifact arrays, all 43 candidate projections
and 21 visible-center joins, plus both complete-detection equality pairs and all
221 unchanged production Python files. Measured detection/capture work took
0.664 s with process peak RSS 155,615,232 bytes; import/font-cache preparation is
outside that timer. No full-session resolver, episode evaluation, report, video
decode, production modification or field qualification ran.

The [storage mapping](2026-10-12-public-compressor-source/current-frame/capture-storage.json)
retains the original output names/hashes while storing six distinct payloads.
Large diagnostic JSON is losslessly gzip-compressed; byte-identical FULL detection
records alias the retained NONE records. All eight logical outputs were reconstructed
and checked byte-for-byte before removing the redundant/uncompressed copies. The
runner still emits the original files into a fresh directory; capture semantics
and its executed hash are unchanged.

The user replied **“두 범위 모두 맞음”** to the separate
[source-only position figure](2026-10-12-public-compressor-source/position-review/position-review.png).
The [closed review](2026-10-12-public-compressor-source/position-review/position-review.json)
confirms Foam rows **323–338** and Oil rows **421–435** at native **X578** in this
frame, with pixel-cell bounds [322.5,338.5] and [420.5,435.5]. Both role questions
and both range questions are CLOSED. These are containment intervals, not exact
scalars, unique edges, labels for every enclosed candidate or adjacent-frame truth.
The ranges were proposed after baseline inspection and remain exposed adjudication.
The [figure renderer](2026-10-12-public-compressor-source/prepare_position_review.py)
loads only source pixels and displays no detector predictions.

### Qualified ranges joined to saved observations

The [saved-data join](2026-10-12-public-compressor-source/position-review/position-join.json)
and [reproducer](2026-10-12-public-compressor-source/join_positions.py) add no detector,
video, path generation or selection run. The adapter reads this new capture schema;
the earlier interval reproducers bind different historical captures. All 23 native
candidates, 13 visible center edges and 31 reviewed rows are retained.

| Saved native observation | Relation to reviewed interval | Interpretation |
|---|---|---|
| Visible Canny at X578: Y332,336 | Inside Foam A | Current-frame edge observations survive; neither is individually certified Foam. |
| Visible Canny at X578: Y428,431,433 | Inside Oil B | Lower-boundary observations survive before hypothesis selection. |
| Current raw/public Oil Y321 | 99.5 px above Oil interval | Provisional selection fails interval containment; this is distance to an uncertainty interval, not exact-Y error or a completed-session result. |
| Oil hypothesis idx5/Y430 | Scalar inside Oil interval; rejected as `typed_ambiguous_hypothesis` | A lower alternative survives; its pooled scalar is not a certified fixed-X contour. |
| Material path idx9 | Median Y425; center-sector sample Y429 over X[557,600) | Both scalar values lie in Oil B; the sector sample remains pooled support, not a pixel contour. |
| Selected spatial Foam component | Front Y317, 5.5 px above Foam interval | The front is already incompatible before temporal publication. |
| Same component's visible center occupancy | Y317–349,417–428,447–456 | Foam A lies inside a larger appearance component; replacing global top by first center support still gives Y317. |

The native Oil problem is therefore not complete loss of lower observations.
For Foam, the retained appearance component crosses the reviewed upper range but
its single front points above it. Whole-component/first-support geometry is not
enough to choose this boundary. As in the prior sample4 join, relaxing the later
episode gate cannot turn the retained raw front into the reviewed upper.
This new frame supplies a separate spatial counterexample without certifying the
physical meaning of every component pixel. No exact curve or selected-candidate
identity is inferred from interval compatibility.

The join verified all eight reconstructed logical outputs, all 24 native image
arrays and all 221 production hashes, and reproduced both NONE/FULL byte-equality
pairs. It ran from outside the repository with an explicit root. Half-resolution
physical accuracy remains NOT_EVALUATED because its center is X578.5; native
interval truth is not transferred to the different sampled column.

## Bounded temporal-detail feasibility screen

The next source-only check asks whether individual-cell disappearance or merging
can supply information beyond the closed static appearance and texture-renewal
probes. It does not select a new model. [Myagotin et al. (2012)](https://journals.iucr.org/s/issues/2012/04/00/mo5028/)
use forward/backward optical-flow inconsistency to locate discontinuous changes
in foam radiographs. Their interpretation depends on separating event and other
motion timescales; they explicitly describe competing rapid changes. This is
evidence for a possible observable, not validation on compressor sight-glass video.
Neither the paper's radiographic results nor its operating settings transfer here.

The existing [consecutive-frame correspondence audit](2026-10-09-reference-correspondence.md#consecutive-frame-appearance-tracking)
already records forward/backward errors, and [ordered texture renewal](2026-10-10-temporal-texture-observation.md)
also responds to optical deformation. Merely reversing an error inequality or
substituting dense flow would not add independently supported role information.
A distinct continuation would need a resolved local change in cell relationships,
with maintained neighbouring support and explicit optical/occlusion alternatives.
It would still be a possible Foam-presence witness, not automatically the upper
boundary, Oil identity or a universal detector for stationary Foam.

The [frozen source-detail plan](2026-10-12-public-compressor-source/temporal-detail-preflight.json)
therefore first retains exactly frames1484–1514, spanning one second around the
reviewed anchor, through the existing `OpenCvVideoReader`. The
[adapter](2026-10-12-public-compressor-source/review_temporal_detail.py) saves all
31 unchanged crops, full-frame hashes and five preselected display views. It
verifies the central full frame against the retained native PNG. No registration,
optical flow, threshold, segmentation or detector runs. The review cannot transfer
frame1499 interval truth to neighbours or label every small grain as a bubble.
Do not widen the time/crop search after viewing to seek a desired event.

The plan and adapter were committed at `36973e1` before decoding. The
[readout](2026-10-12-public-compressor-source/temporal-detail/readout.json)
retains frames1484–1514 at 49.516133–50.517133 s in the
[lossless crop archive](2026-10-12-public-compressor-source/temporal-detail/native-crops.npz).
The [five preselected views](2026-10-12-public-compressor-source/temporal-detail/native-detail-sheet.png)
show broad-layer texture and upper-contour changes together with camera movement.
They do not establish an individually identified film-disappearance or cell-neighbour
change. All 31 crops remain available, but no exhaustive cell/event correspondence
is claimed. This is no qualified event, not proof that no event occurred.

The [review and verification](2026-10-12-public-compressor-source/temporal-detail/review.json)
close this bounded screen without a new role operation. All 31 crop hashes,
30 consecutive time steps, five lossless display panels and the native anchor
match; all 221 production hashes remain unchanged. Decode/capture took 0.296 s,
with process peak RSS 157,270,016 bytes. No additional detector ran.

**Design limit:** a directly supported cell-relationship change and its optical/
occlusion opposition are not yet specified. A renamed motion error or texture
renewal score is not the missing information. No temporal classifier, new threshold
or immediate implementation follows, and the old failures remain closed. This
does not establish impossibility for passive video or every non-learned method.
The source is useful for the qualified two-role spatial comparison already made;
its acquisition does not by itself provide the missing role selector. The Work
Plan retains the open design entry and the existing acceptance boundaries.

## Verification and reproduction

[Artifact verification](2026-10-12-public-compressor-source/artifact-verification.json)
checks the source bytes/hash, seven implementation/input pins, all 12 request-time
joins within one source frame, lossless PNG equality with the decoded BGR array,
and the sheet's saved hash/shape. It is integrity evidence, not independent
physical or continuous-story validation. Production behavior is unchanged.

With the pinned local original present, reproduce into a new directory:

```bash
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-public-compressor-source/render.py --root . --output /tmp/s11-public-source-review
MPLCONFIGDIR=/tmp/s11-public-mpl .venv/bin/python docs/50-diagnostics/s11/2026-10-12-public-compressor-source/inspect_detector.py --root . --output /tmp/s11-public-source-baseline
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-public-compressor-source/prepare_position_review.py --output /tmp/s11-public-source-positions
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-public-compressor-source/join_positions.py --root . --output /tmp/s11-public-source-position-join.json
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-public-compressor-source/review_temporal_detail.py --root . --output /tmp/s11-public-source-temporal-detail
```

The renderer refuses to overwrite an existing output directory. A future download
is not assumed to reproduce the same platform encoding; verify the pinned SHA-256
before decoding. The full downloader metadata remains temporary and untracked.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `OIL-CANDIDATE`
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: native current-frame Oil selects Y321 outside reviewed Oil rows421–435 despite retained lower observations. The selected Foam appearance component crosses reviewed rows323–338 but reduces to front Y317 before temporal publication. These are interval incompatibilities, not exact contour labels or completed-window results; native lower-hypothesis ambiguity and half-resolution non-selection remain distinct. Fresh Foam persistence pending is not a demonstrated episode failure.
- Logic-map impact: NONE — reuses the existing video reader for bounded evidence preparation; no production route, geometry policy or selection change.
- Failure-registry impact: NONE — source/role uncertainty and non-transfer of reviewed truth are already covered; no new field failure or repair is asserted.
