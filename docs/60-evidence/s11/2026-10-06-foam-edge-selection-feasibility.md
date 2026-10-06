# Foam edge-selection feasibility and two-time review — 2026-10-06

Base source: `731502f568df0c5644734e140e8dfb7294cd03eb`.
Status: bounded appearance-rule audit complete; no rule promoted. FIELD FAIL /
NOT_EVALUATED. Existing runtime, labels and Windows truth are unchanged.

## Ownership and design decision

The [annotated B reply](2026-10-06-boundary-temporal-residuals.md#annotated-b-boundary-reply-received)
shows that a tentatively human-attributed upper Foam edge survives among saved
alternatives even where the existing support top follows a structure. Selection
must therefore separate component material support from physical-front identity.

Existing owners were inspected by responsibility: `foam_front_detector.py` owns
support/component gates; `oil_material_path.py::_path_for_seed` selects polarity
paths with sector contrast/jump/material criteria; `s11_spatial_path_probe.py`
orders candidate-centred sector runs. They do not implement this exact read-only
question over all saved per-column peak intervals with all ties retained. Calling
them here would change inputs and introduce thresholds/proposal decisions. A
small local audit instead consumes the existing front-alternative JSON. It is
not a replacement runtime path generator and has no production caller.

Proposed separation remains: retain same-frame alternatives; establish material
and structural opposition independently; only then assess a front's spatial and
temporal compatibility, with unresolved support remaining unavailable. Physical
identity cannot be supplied by a geometric optimum. This turn tests the proposed
appearance shortcuts before introducing an acceptance mechanism. It does not
implement a purported physical selector with missing evidence.

## Exhaustive saved-inventory audit

Input: canonical `s11-local-foam-front-alternatives-002/report.json`, all14 retained
components, both pre-existing radii4/8, all574 occupied columns (1,148 views).
No image measurement, detector run, decode, strength cutoff or tuned parameter
was added. All93 inputs were rehashed before/after: 88 capture files, four
front-alternative files/receipt, and the red-mark attributed reply.

Counterfactual appearance rules, never runtime selections:

- Strongest: retain every equal-maximum vertical-magnitude peak pixel.
- Lowest: largest source Y among retained peaks.
- Nearest: retain every pixel tied in absolute distance to the original support top.
- Smoothest: minimize sum of absolute adjacent-column Y changes over each maximal
  consecutive, fully observed, nonempty column run. Every integer row in a saved
  plateau remains a state. No jump cutoff, strength weight, start/end anchor,
  private coordinate rule or tie-breaking is used. Forward/backward dynamic
  programming reports every row lying on some globally minimum-cost path.
  Censored, absent-peak and missing columns split runs; none is bridged.

The all-optimal membership calculation was compared against exhaustive path
enumeration on four small branching/tie/one-column examples. There are39 runs in
the saved inventory. This checks the diagnostic arithmetic, not detector efficacy.

The eleven tentatively marked B columns are a post-observation development
comparison, not exact contour truth, a held-out set, or a performance denominator:

| Existing radius | Mark represented | Strongest contains mark | Lowest contains mark | Nearest contains mark | Global minimum-variation membership contains mark |
|---|---|---|---|---|---|
| 4 | 5/11 | 5/11 | 5/11 | 5/11 | 5/11 |
| 8 | 11/11 | 1/11 | 7/11 | 5/11 | 11/11 |

At radius8, each marked B coordinate is also the only optimal Y at its column,
but the complete48-column C2 path is not unique: X596/597 each retains Y846 or
Y852 in the optimal membership. Total minimum variation is19 px. A row's presence
in the membership does not mean arbitrary combinations of such rows form an
optimal path; the audit never joins memberships into a fabricated selected path.

The apparent B success does not validate smoothness as identity. For example,
A X577's existing human-attributed Foam top is Y840, while the smoothest membership
is Y846; C X598–606 moves to Y852 versus original top Y845–846; much of D also
moves toward Y852. These are geometric discrepancies with prior qualitative
Foam-path attribution, not calibrated per-pixel errors. They are sufficient to
withhold a whole-path improvement claim based only on B. Both human rim controls
also produce complete radius8 smooth paths (sample4 C1:78 columns; sample2 C1:9).
Thus existence of a smooth path does not distinguish Foam from structure.

The rule audit rejects promotion of strongest/lowest/nearest/continuity alone.
It does not prove all spatial methods impossible. Neither the larger radius nor
a newly weighted combination is adopted based on this single exposed frame.

## Needed evidence and prepared human checkpoint

The user already established that circular structures stay fixed while surrounding
Foam changes. The missing item is the actual Foam-front location at another saved
time, not the structures' identity again. Frame450's tentative red marks cannot
be transferred across frames. To test later temporal correspondence with a
physical reference rather than appearance self-consistency, prepare exactly two
original saved times: frame420 (14s) and frame480 (16s), anchor450 ±30frames.
These offsets were stated before inspecting the two images; no frame was selected
by favorable algorithm output. Both lie in the already saved13–17s sequence.

The local viewer shows:

- original14s and16s ROI images and their same-coordinate enlarged context;
- anchor15s with the prior approximate tentative annotation, only on that anchor;
- source axes and the old B X-range as location guides, no detector path transferred;
- optional user click points with displayed coordinates and clear/reset control.
  Points are temporary in-browser aids, not automatically submitted or saved labels.

Question: where is the actual Foam upper boundary near the central structure at
14s and16s? Visible portions, occluded, or unclear are valid responses. This is a
bounded two-frame development review, not an independent recording or a request
to relabel the full sequence. No answer is assumed while the question is pending.

All126 preparation inputs are preserved: 124 motion-review outputs, their receipt,
and the prior annotated reply JSON. The same104×104 ROI and source origin[543,798]
are retained. The context display is X[571,619), Y[830,859); full original crops
remain visible. Enlargement adds no information. No new decoding or detector run.
Browser rendering, image loading, coordinate clicks on both frames and point reset
passed without page errors. Test clicks were cleared and are not human replies.

## Artifacts and scope of verification

Local audit: `sample/output/s11-local-edge-selection-audit-001/`.
Local review: `sample/output/s11-local-foam-two-time-review-001/`.
Both preserve scripts, manifests/reports and separate output receipts. No new
production code was introduced, so no runtime suite rerun is claimed or needed
for these saved-data calculations and review preparation.

| Artifact | SHA-256 |
|---|---|
| `s11-local-edge-selection-audit-001/run.py` | `1cf3d7f92fe656a32e5f91a48eba31763726586f6ea2754dc399737a29b2e18b` |
| `s11-local-edge-selection-audit-001/report.json` | `c831a7014c9345521362ada8ef4288a14d5f0bb9156ae73faa2bef1d61183955` |
| `s11-local-edge-selection-audit-001/receipt.json` | `37e09dfa4c820ed7497b0f141c2f06dde8b5e697e53a111c41d732ed0991344d` |
| `s11-local-foam-two-time-review-001/prepare.py` | `54d7a1f1e7e2f39cd4d3e408c5a62d51e8bfd84f356c47e8586e13d6ffde8af5` |
| `s11-local-foam-two-time-review-001/manifest.json` | `194bb6857b5bfcd8275ad281777b0ee6390acff7f8ea74e513f351791108a5a7` |
| `s11-local-foam-two-time-review-001/viewer.html` | `300dfc3342f83bff9ef422e4be14c36db35b5b3521360d25cffdb3e9400dff36` |
| `s11-local-foam-two-time-review-001/receipt.json` | `70334a0d3b7c5b0d4de0baab89cdcec96ce81ba802ceb1eaa22b25db9ce59130` |

The [current work plan](../../00-project/work-plan.md) owns the pending checkpoint.
Windows75-candidate target truth remains separate; no prediction comparison or
[O2 acceptance](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance)
is claimed. FIELD FAIL and the independent-recording requirement remain unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: frame480 confirmed rim C1 escapes spatial structural rejection and passes material admission before score ordering; mixed component tops and the earlier substrate false rejection remain opposing failures. No repaired front is established.
- Logic-map impact: NONE — saved-JSON rule audits and original-image review have no production caller or decision authority.
- Failure-registry impact: NONE — no motion-only identity, geometry-as-identity or private-coordinate shortcut is promoted; existing recurrence guards apply.

## Two-time human clicks preserved and same-frame capture — 2026-10-06

The user placed points in the existing Safari viewer and explicitly asked to
continue. Safari's selected page text exposed the complete JSON; it was parsed
without OCR and compared to the saved arrays in original order. Both comparisons
passed (22 clicks at420 and38 at480). The original viewer was not reloaded or
cleared. Capture is a supplemental human correspondence record, not formal O2
truth or a complete contour.

| Frame | Raw clicks | Unique XY | Unique X | Marked source Y range |
|---|---|---|---|---|
| 420 /14s | 22 | 22 | 22 | 844–846 |
| 480 /16s | 38 | 35 | 34 | 835–844 |

At480, (575,838), (593,840) and (595,842) each occur twice. X577 has both
Y837 and838. All clicks, duplicates, order and alternatives remain in the raw
reply. No averaging, nearest winner, interpolation or click tolerance was added.
The14 exact common X locations have source-coordinate differences Y480−Y420
from−8 to−1px. Within B, the only common X values are583 (−6px) and587 (−5px).
These are sparse human-marked location differences, not material flow, velocity,
calibrated localization errors or camera-corrected motion. Existing whole-ROI
registration estimates are retained as context and not applied to human labels.
Frame450's tentative screenshot mapping remains a separately attributed record.

The correspondence audit preserves132 input files, including original review
inputs and the saved temporal report. The click record closes the two-time
Foam-location question; do not ask the user to draw these points again.

### Bounded current-frame diagnosis

Executed source: `7fa7e343c48d4dbbbb6159f9cd52dad96931a6f1`, unchanged production
files. The local harness and source-file hashes are pinned in the new capture.

Saved review PNGs did not contain current-frame detector candidates at420/480.
Reuse the existing local capture harness's production entry path:
`_load_cases` for the unchanged sample4 recipe, `OpenCvPhaseDetector.detect`,
`JsonlDebugTraceWriter` FULL output, and `extract_frame`. The new local harness
reads exactly these two full source frames with fresh detector state per frame;
there is no sequence replay, learning, completed-window resolution or human-point
input to detection. This step **does include two source-frame decodes and detector
calls**; it is distinct from the preceding saved-data-only correspondence audit.

Both decoder indices/timestamps match420/14s and480/16s. Each decoded ROI and
actual detector `original_roi` is pixel-equal to the already reviewed saved PNG.
Source origin[543,798] and104×104 shape match. All139 inputs and the captured source
file hashes are unchanged. There are56 hashed capture outputs plus the receipt.
The existing front-alternative runner then measures every retained component
with unchanged radii4/8, preserving57 capture files; all9 components are retained.
No runtime code, threshold, label or selected behavior was edited.

| Frame | Component | Spatial status | Selected spatially | Source box | Score |
|---|---|---|---|---|---|
| 420 | C1 | weak_rejected; structural=true | yes, best rejected component | [552,845,631,889) | 0.908777 |
| 420 | C2 | weak_rejected; substrate=true, shape_ok=false | no | [570,840,620,853) | 0.732141 |
| 480 | C1 | accepted_strong; structural=false | yes | [585,862,631,889) | 0.840447 |
| 480 | C2 | accepted_strong; detached_droplet, substrate=false | no | [570,833,611,850) | 0.742296 |

Component IDs are local to each frame, not tracked physical IDs. At480, both C1
and C2 pass spatial admission and the existing ordering chooses C1. Its first
support pixel at the23 unique human XY points with matching X is31–39px below
the marked boundary. At420, C1's corresponding difference is26–35px below at
all22 points. Its scalar top alone is misleading:420 C1's global Y845 happens
to equal much of the marked boundary while its actual same-X top is far below.
Do not use a component's global minimum Y as proof of path correspondence.

At420 C2 has same-X support for22/22 unique clicked points; its top exactly
matches4 and its radius8 alternatives contain12. At480 C2 has same-X support
for29/35 unique clicked points, top matches3 and radius8 alternatives contain8.
The other six points have no C2 support column; all other components remain in
the report. These are exact integer membership descriptions of approximate human
points, **not** calibrated recall/accuracy or a reason to tune the window radius.
Lack of exact peak membership does not mean the person selected a wrong boundary.

Both frame records have null raw/smoothed Oil and Foam positions. At480 the
current-frame Foam owner is `persistence_pending`, with one pending observation
and two required. Thus this is a spatial selection discrepancy, not evidence of
a published false Foam value or a completed-window failure. At420 the state is
`weak_rejected`. Fresh-state static context is empty, so no claim is made about
how a historically accumulated static model would behave.

### Next bounded human check

The new16s view keeps plain RGB beside actual C1/C2 support pixels and the user's
red points. Orange C1 covers the lower curved rim-like region; this is an agent
visual description. Its precise physical attribution at480 is not silently
inherited from the previously reviewed frame450 C1. Ask whether this selected
orange region is glass structure, Foam, mixed, or unclear. Do not request a new
Foam contour or classify all cyan C2 pixels as pure Foam. This check distinguishes
an admitted structural competitor from a differently located material region
before designing a replacement for the spatial structure/selection mechanism.

The first Safari-open attempt returned a locked-Mac tool error; the user reported
the Mac was not locked. Reconnecting succeeded and the new tab was opened and
visually verified, while the original point-review tab remained intact. A static
side-by-side PNG was also generated and visually inspected. The local HTML
viewer provides independent overlay toggles. The earlier click data is
already saved, so browser state is no longer its only copy. Windows execution is
not needed at this checkpoint. No broader field replay or R2/O3 entry follows.

### New local artifact pins

All private pixels and detailed JSON remain under `sample/output/`.

| Artifact | SHA-256 |
|---|---|
| `s11-local-foam-two-time-review-001-notes/clicked-points.json` | `b1a9006f9649d07409a492ce610d26cb800935d419777ce30cf4307be032e4e9` |
| `s11-local-foam-two-time-review-001-notes/reply-001-boundary-correspondence.json` | `1386d7326f5e6c77a1e7eb4bd59f83db9505005808b36d5a8818e26966a9421e` |
| `s11-local-foam-two-time-review-001-notes/correspondence-audit.json` | `661e734185bbcb026c8ce0cca777c3d14b1b7da5fb377a909502f8f44414a478` |
| `s11-local-foam-two-time-capture-001/receipt.json` | `364250b530ded1120137a9d3d280ff480329cfa6fa5be4d9c91fa78a965e3b00` |
| `s11-local-foam-two-time-capture-001-notes/report.json` | `5128a650c92fab0ac04bd09e2830d3706c17fd1ac4641263ba47fff93527bb4d` |
| `s11-local-foam-two-time-capture-001-notes/receipt.json` | `729bb115240689203e7d62365b8ab8a086bf4c8b5007fe6f40cf5684cceaba36` |

The new capture's scope/source/code hashes are in `capture.json` and `capture.py`;
the comparison report pins66 files. `render-receipt.json` separately pins the
static preview and rendering script. Original captures/reviews and Windows
75-candidate target truth remain unchanged. The Detector Governance block above
applies: actual same-X support and admission precede spatial selection; this new
capture exposes a discrepancy without assigning physical identity or changing a
runtime owner. FIELD FAIL / NOT_EVALUATED remains unchanged.


## Frame480 orange C1 confirmed glass rim — 2026-10-06

The user's exact reply is **“주황색은 글래스 테두리야”**. It binds to the
prepared sample4/frame480 (16s) orange C1: diagnostic_id1, original component
label5, source box `[585,862,631,889)`, 313 support pixels. The local reply pins
the exact viewer, capture receipt, run and record IDs. This is a candidate-bound
structure attribution; it does not label all C2 pixels, transfer another frame's
identity, alter formal labels, or change the Windows75 target truth.

The user also reported that Safari had previously stopped at the file-open
screen. The earlier claim of uninterrupted successful display is therefore
qualified: its past cause is not established. On this turn a fresh Safari AX
read and screenshot show the actual original/support comparison, orange C1,
cyan C2 and red points, with no file-open dialog. No reload or alteration of the
original point tab was needed. The pending question in the immutable historical
viewer is closed by this reply, not an outstanding request.

### Stored-raster causal check

`record-rim-reply.py` reads the saved component-label raster and invokes the
existing `_wide_hollow_component_metrics` helper for all5 frame480 components.
Structural predicates and recorded wide-row/compactness values reproduce; a
separate decomposition of the current score expression matches all5 scores
(abs tolerance1e-12 for arithmetic verification only). All62 pinned inputs are
unchanged. No video decode, detector run or parameter change occurred.

| C1 structural conjunct | Measured value | Predicate result |
|---|---|---|
| width ratio >=0.70 | 0.4423076923 | false |
| fill ratio <0.30 | 0.2520128824 | true |
| wide-row fraction >=0.25 | 0.2962962963 | true |
| row compactness median <0.65 | 1.0 | false |

The conjunction is false. A partial curved rim can have compact individual rows
without being Foam; the present broad/hollow rule does not reject this observed
fragment. C1 then passes `bottom_connected and white_ok`, area/height, texture
and score gates, resulting in `accepted_strong`. Its phenotype is `none`;
the bottom-connected branch does not require a detached material phenotype.

C1's score0.8404473715 exceeds C2's0.7422964852. Both have the same accepted
status priority, so `_component_sort_key` uses score before front Y. C1 receives
0.09 from bottom connection and0.10199 from height (C2:0 and0.06422). Appearance
and texture contributions are similar; C2 has the larger fill contribution.
This explains the observed ordering without claiming that removing a single
term would yield a validated repair. First address the admitted structure,
rather than treating score order alone as the root cause.

The fresh-state owner remains `persistence_pending`, with all public Oil/Foam
positions null. A spatial false admission is established; a temporal/field false
publication is not. No sequence replay or accumulated static model was tested.

### Retained reply and audit

Local directory: `sample/output/s11-local-foam-two-time-capture-001-notes/`.

| File | SHA-256 |
|---|---|
| `reply-002-frame480-rim.json` | `c1d93492ec3fe2746b8a42344e5e8ef14397c60ba94a7d7a3130996581259ffb` |
| `rim-admission-audit.json` | `a8de647bdd5c183d6ea400eb388d083f11f6e83d5089c4f9bf2860e157d6a9af` |
| `record-rim-reply.py` | `b3a01e1468db368f4a2178ed85eeb8a794b4d7f15254247fb9a4a258474cf61b` |

`rim-reply-receipt.json` records all62 input hashes and these outputs. Prior
capture/comparison/viewer artifacts remain unchanged. The next local design
must confront this narrow rim false admission together with the earlier broad
rim and substrate false rejection, while retaining the mixed C2 boundary. No
threshold fit, pure-material assumption, identity promotion or W5/O3 entry
follows. FIELD FAIL / NOT_EVALUATED remains unchanged.
