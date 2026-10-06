# Saved-sequence boundary temporal residuals — 2026-10-06

Status: MEASUREMENT_COMPLETE_NOT_EVALUATED; FIELD FAIL. This is a bounded Mac
regression diagnostic, not a Foam selector, Windows qualification or O2 acceptance.

## Source and measurement

Base source: `7bbf71480a7b0f9855f36b513b32bf10e993cd4e` plus the exact diagnostic
source hashes below. The [architecture](../../20-architecture/s11-foam-component-diagnostics-architecture.md#offline-registered-boundary-residuals)
owns support and abstention semantics. Existing translation/exposure math is
reused; optional translation reasons prevent a rejected zero-shift fallback from
being mistaken for observed stationarity. Runtime decision consumers are unchanged.

- Case `sample4:450`; record `f000000450_fb759bff9e59`;
  run `26b0eaed-5cdf-4eb8-a416-18b30936902d`;
  Glass `ecb6e1ec-0259-5982-a35f-7cb1f7075af2`.
- Anchor frame450 (15s); source origin [543,798], shape104×104.
- Saved frames390–510 inclusive (13–17s), excluding the anchor self comparison:
  120 pairs. No new decode, detector, tracker, label or recipe execution.
- 683 fixed anchor-coordinate points: all top columns of five retained components
  and all native-path columns of Oil candidates idx9–14. Radii2/4 give 163,920
  query rows. These are fixed pixel neighbourhoods, not temporal material tracks.
- Capture receipt plus87 outputs and motion-review receipt plus124 outputs:
  213 inputs preserved. No new physical Foam mask or glare mask is propagated.
- NumPy2.5.1 / OpenCV4.14.0. Detailed arrays, runner and hashes remain locally in
  `sample/output/s11-local-boundary-temporal-001/`.

## Observations and limits

All120 pairs passed the existing numerical registration gates. Current-to-anchor
shift spans dx −0.133749..0.097982 and dy −0.140829..0.558423 px; maximum reciprocal
translation error is 7.33e−08 px. Reciprocal agreement does not establish a correct
physical camera model: both estimates use the same changing ROI.

The following are medians of fully observed window-mean absolute gray differences
(raw code values), not MSE, displacement, detection rates or independent samples.
All four alternatives share pixel support; radius is a fixed inspection scale.

| Anchor group | Radius | Fully observed / all frame-queries | Direct | Exposure only | Registered | Registered + exposure |
|---|---|---|---|---|---|---|
| C1_support_top | 2 | 9360/9360 | 4.1600 | 4.9502 | 4.0500 | 4.5004 |
| C1_support_top | 4 | 9360/9360 | 4.0556 | 4.6891 | 3.8184 | 4.3569 |
| C2_support_top | 2 | 5760/5760 | 16.9600 | 17.4072 | 16.1591 | 16.6399 |
| C2_support_top | 4 | 5760/5760 | 18.6667 | 19.2160 | 17.7752 | 18.3729 |
| C4_support_top | 2 | 0/2400 | null | null | null | null |
| C4_support_top | 4 | 0/2400 | null | null | null | null |

C1 is the human-attributed lower rim; C2 is a Foam-region support with known
central circular structure involvement. C2 neighbourhood change is larger, but a
fixed structure can be surrounded or covered by changing Foam. High residual is
therefore not sufficient evidence that its saved top is a Foam–air boundary.
Exposure fitting does not uniformly reduce residuals. C4 has no fully observed
query windows; its summary is null, not zero or proof of a stationary structure.

Geometric mask validity does not exclude glare or identify visible material.
Registered interpolation, finite crop, overlapping queries and shared frames
limit interpretation. No structure geometry, exact contamination interval,
Foam front, motion-only identity or repaired public output is established.

## Human correspondence checkpoint

The prior [human clarification](2026-10-06-foam-front-alternatives.md#human-clarification--regularly-spaced-circular-structures)
identifies fixed, regularly spaced circular structures. Do not ask that identity
question again or use it to label all C2 pixels.

A local original-RGB/stored-top viewer divides all48 C2 columns into four equal
12-column segments, chosen by geometry rather than residual magnitude:
A [571,583), B [583,595), C [595,607), D [607,619). Each keeps the actual stored
per-column Y; no fitted contour or interpolation is introduced. The user is asked
which parts follow Foam–air, structure, mixed or unclear features. No answer has
been recorded at publication of this measurement; no formal truth is auto-assigned.

Local viewer: `sample/output/s11-local-boundary-temporal-001-notes/segment-review.html`.
Its manifest SHA-256 is
`302825b70fae4e3783d76023904646cdc8286e9c11018c70cedfe6caa119140d`.
Plain/path panels, toggle and browser rendering were checked. Enlargement adds no
information beyond the original104×104 pixels. Separate residual plots are
measurement illustrations, not the primary human identity display.

## Human A–D correspondence received

The user replied to the displayed original/path review:

> A,C,D는 foam 경계를 따라감
> B 위쪽 ^ 모양(B의 우측)은 가운데 구조물을 따라감, 아래쪽(B의 좌측)은 foam의 경계를 따라감

| Display segment | Source X [start, stop) | Human path correspondence |
|---|---|---|
| A | [571,583) | Follows Foam boundary |
| B | [583,595) | Mixed: left/lower part follows Foam; right/upper `^` follows central structure |
| C | [595,607) | Follows Foam boundary |
| D | [607,619) | Follows Foam boundary |

These are direct human observations of the existing yellow C2 path at frame450.
The four X ranges come from the pinned display manifest, not newly estimated
human endpoints. The user did not give an exact split X within B; preserve the
left/lower versus right/upper description without inventing a pixel cutoff.
No per-pixel structure mask, replacement contour through B, subpixel accuracy or
per-frame truth for the other120 frames is assigned. The whole B segment must not
be treated as structure, and the whole C2 top must not be accepted as pure Foam.

This closes the A–D location question. It supports a local representation failure:
one retained support-top path follows different physical features along X. The
existing whole-component residual cannot adjudicate that mixed path. A also has
an arched appearance in the saved path, yet is attributed to Foam; an arch-shaped
veto would therefore discard a human-attributed Foam segment. This is an agent
inference from the displayed geometry plus this reply, not a new human rule.

The next bounded local task is to inspect the already saved per-column edge
alternatives around B against this correspondence, preserving A/C/D as positive
path context and B as mixed context. Establish whether an alternative Foam edge
is represented before designing selection. Do not lower thresholds, hardcode
these coordinates, flatten/interpolate B, transfer identity through time, or
remove the C1 veto as a sufficient repair. No repeated structure/segment question
or Windows execution is needed merely to record this answer.

The original measurement and review manifest remain unchanged. The separate
local reply is
`sample/output/s11-local-boundary-temporal-001-notes/reply-001-path-correspondence.json`,
SHA-256 `cbdabc2e65d83ce61b17404e6c750745dfdd39590f27f40f8f53c68ff94e8ad1`.
Its verbatim text, frame/component identity and manifest hash preserve attribution;
formal labels, Windows target truth and runtime behavior are unchanged.

## Saved B alternatives — representation check and next review

Following the A–D reply, the existing front-alternative report was read without
rerunning extraction, registration, video decode or detection. Its report hash is
`877ca4ec045149f0905eac3bf1e2ba6243a18287a95946fbb2796a084ccaafcb`.
All twelve B columns and both original ±4/±8 inspection radii are retained;
there is no strength cutoff, nearest winner, tuned radius or interpolated path.
The split between the human's left/lower and right/upper descriptions stays
qualitative. The existing A/C/D attributions are not reopened.

| Segment | Radius | Single / multiple / no bracketed peak / censored columns | Peak intervals |
|---|---|---|---|
| A | 4 | 4 / 4 / 4 / 0 | 12 |
| A | 8 | 0 / 12 / 0 / 0 | 33 |
| B | 4 | 6 / 6 / 0 / 0 | 20 |
| B | 8 | 0 / 12 / 0 / 0 | 43 |
| C | 4 | 11 / 1 / 0 / 0 | 13 |
| C | 8 | 0 / 12 / 0 / 0 | 32 |
| D | 4 | 8 / 4 / 0 / 0 | 16 |
| D | 8 | 0 / 12 / 0 / 0 | 34 |

All48 C2 column windows are fully observed at both existing radii. Multiple image
peaks persist in all48 columns at radius8, including human-attributed Foam and
mixed parts. At radius4, A has four columns without a bracketed peak despite its
Foam-boundary attribution. Neither a unique peak nor peak absence establishes
physical identity or physical absence.

The full B inventory below lists exact half-open source-Y plateau ranges.
A one-pixel range [846,847) means the saved peak pixel Y846. These are grayscale
appearance measurements, not candidate-specific physical interface labels.

| Source X | Existing C2 top Y | Radius4 peak ranges | Radius8 peak ranges |
|---|---|---|---|
| 583 | 844 | [841,842), [843,844), [846,847) | [841,842), [843,844), [846,847), [851,852) |
| 584 | 845 | [844,845) | [844,845), [851,852) |
| 585 | 845 | [844,845) | [839,840), [844,845), [851,852) |
| 586 | 845 | [845,846) | [839,840), [845,846), [851,852) |
| 587 | 844 | [845,846) | [839,840), [845,846), [851,852) |
| 588 | 844 | [841,842), [845,846) | [838,839), [841,842), [845,846) |
| 589 | 840 | [837,838), [842,843) | [833,834), [837,838), [842,843), [846,847) |
| 590 | 839 | [837,838) | [833,834), [837,838), [842,844), [846,847) |
| 591 | 839 | [837,838) | [833,834), [837,838), [843,844), [846,847) |
| 592 | 840 | [838,839), [843,844) | [833,834), [838,839), [843,844), [846,847) |
| 593 | 840 | [838,839), [843,844) | [833,834), [838,839), [843,844), [846,847) |
| 594 | 841 | [838,839), [841,842), [843,844) | [835,836), [838,839), [841,842), [843,844), [846,847) |

In the displayed upper-right lobe, X589–594 each has a saved Y846 appearance peak
at radius8, while radius4 excludes that lower alternative. These coordinates
identify existing measurements; they do not define the human's exact structure
interval. Radius8 also retains other peaks (including X590's [842,844) plateau).
The representation therefore contains lower alternatives, but the current
attribution does not establish which, if any, is the actual Foam–air boundary.
It could instead be a lower Oil–Foam boundary, structure, optical texture or an
occluded boundary. More alternatives are not demonstrated recall/identity gain.

A new local review shows original RGB beside B with its neighbouring columns,
source X/Y axes, optional yellow original top and cyan outlined peak pixels.
All stored peaks are displayed equally; none is connected, ranked or selected.
Radius4/8 controls only choose which saved view to display. The user is asked
whether the actual Foam upper boundary is visible in B's structure-following
part and whether it coincides with an existing alternative. Occluded/unclear/no
matching alternative are valid outcomes; no contour through the structure is
fabricated. This is a new missing boundary correspondence, not a repeat of the
closed structure or A–D question.

Local review directory: `sample/output/s11-local-b-alternative-review-001/`.
Manifest SHA-256:
`b336dc63a2b886b2578d0d79c78a9b6d62667d79ad0094fc2150e9ab83b34111`.
The manifest retains full original identity, B column projections, input hashes,
selection rule and unset physical identity/front. Its receipt pins the preparation
script, manifest and self-contained viewer. All94 inputs were verified before and
after: 88 capture files, four front-alternative outputs/receipt, review manifest and
human reply. Display coordinates equal the earlier pinned A–D top exactly.
Browser rendering, both radii, both toggles and all12 table rows were checked
without script errors. No source implementation or formal labels changed.

At this publication checkpoint the boundary-visibility answer is pending.
No Windows run is required; FIELD FAIL, O2 and Windows target truth remain unchanged.

## Verification and provenance

Focused tests: 22 passed across `tests/unit/test_s11_boundary_temporal_probe.py`
and `tests/test_temporal_raster_evidence.py`. Synthetic controls include exposure
and translation, mask-hole interpolation, localized appearance change, numerical
failure and rejected high-response registration. They validate measurement
semantics, not material identity.

On the saved120 pairs, all240 forward/reverse translation tuples exactly match
the helper from base source. Output hashes and all213 input hashes were rechecked.
The optional diagnostic dictionary changes no production tuple or gate. No full
runtime detector replay or Windows validation is claimed.

| File | SHA-256 |
|---|---|
| `sample/output/s11-local-boundary-temporal-001/run.py` | `8d5d9d08c9c66107f8863b92aaa092ca890c4a0b8f2eed0bf21f9ca8e643c445` |
| `tests/diagnostics/s11_boundary_temporal_probe.py` | `6dcbc3c805fefd7c3eb9349d156d2e00a769530cde3bc35f3cf1fcd133b389ba` |
| `src/oil_tracker/adapters/vision/temporal_raster_evidence.py` | `c2d6a4222e06cbffb3c32b8bc6b13f6142d810b9febabfa86afd6542107b9f15` |
| local `report.json` | `60fd9986688c3043f9bc68fc475850a1c3d35f55a7a1e3f9bd26569ffdcf0088` |
| local `summary.md` | `8f2dd66c184f2c4a75db3d19db72b0cb3fa4c2024d1fd1d1b27c5ba14f1176ae` |
| local `residuals.npz` | `ad3718dcb4dcde8d9f5e50b22020efea5b78ca775b77a9289bc754d476100245` |
| local `queries.csv` | `9568a028b8fc1d93f4e48e50b86d7fb7202c17cb251f97e7e99961ddac9f3605` |
| local `receipt.json` | `fc8722173d87827665f33e0e2b7a3826165cd59dc3cab92154d86473c66fec1f` |

## Windows connection and disposition

Windows passive-review truth remains 75 candidates with10 target/65 non-target;
physical identity and uppermost-target role stay separate. This Mac experiment
investigates a Foam failure mode with its own source lineage. Neither its motion
observations nor any later A–D answer transfer labels to Windows candidates.
A future behavior candidate must separately evaluate the pinned Windows controls
and independent recording roles under the [O2 acceptance owner](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance).
No predictions, W4-R2 entry, field PASS or W5/O3 promotion result from this probe.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: exact structure-versus-Foam front attribution remains unknown; saved support-top geometry can include fixed structures and residual change does not resolve it.
- Logic-map impact: NONE — an offline probe reuses existing registration/exposure owners; optional reasons leave runtime gates and return tuples unchanged.
- Failure-registry impact: NONE — motion-only identity, component identity leakage and threshold shortcuts remain rejected; no new behavior or efficacy claim.
