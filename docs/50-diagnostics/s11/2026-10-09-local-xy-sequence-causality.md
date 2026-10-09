# Local XY sequence causality and separate Foam-front review

The saved Local XY pair exposes three different losses: committed Oil-owner
selection at 52 s, ambiguous Oil association followed by failed confirmation at
54–56 s, and independent Foam front/episode decisions. This is a numerical
causal readout, not an accepted detector repair. The [Work Plan](../../00-project/work-plan.md)
owns the next transition and the unchanged O2 OPEN / FIELD FAIL disposition.

## Scope and verification

Source HEAD: `3c6df8e08bfd2ab43e00a4c5e463813ba8e1fcc0`.
The [completed comparison](../../60-evidence/s11/2026-10-09-local-xy-implementation.md)
supplies OFF/scoped raw candidates, recipes and expected completed detections.
The existing `ObservationSequenceResolver` is observed through process-local
wrappers adapted from the [October 8 causal audit](2026-10-08-d2-registration-sequence-causality.md).
Every wrapper returns its original result. No frame detector or video decoder
is run, and no policy, production source, recipe or label is changed.

- **226/226 complete detections match**: 113 OFF and 113 scoped, including
  candidates, metrics, flags, coordinates and decision witnesses.
- All **222 source/runner pins** match the original comparison; source and
  saved inputs remain byte-identical before/after observation.
- The saved FULL component capture is hash-verified and its complete scoped
  output equals NONE. It supplies actual component-front geometry, not new
  detector results.
- The [machine record](2026-10-09-local-xy-sequence-causality.json) preserves
  pins, decisive assignment/confirmation/selection records, Foam evaluations,
  script text and the local artifact inventory. Full traces remain in
  `sample/output/s11-local-xy-sequence-20261009-001/`; they are retained evidence.

Source frame = sequence offset × 15; time = offset / 2. Cross-run track IDs are
implementation identities and do not establish physical correspondence.

## Oil: selection, association and confirmation are separate

**51.5 → 52 s.** Scoped selection first chooses Y805 from track
`oil-tracklet:000102:0022`, with bounded score 6.584569 versus the Y830
representative of track `000102:0023` at 6.413818. The 0.170751 margin exceeds
the existing 0.08 competing-owner abstention margin. At 52 s the admitted,
publishable phase proposal Y833 in track `000102:0023` has score `-inf`:
the committed predecessor belongs to `000102:0022`, and there is no permitted
owner-chain handoff. Y821 from that committed owner wins at 7.935913.
Its local emission, 0.680801, is lower than Y833's 0.720011; increasing the
target's local score does not remove the forbidden transition.

**54 s.** Three established tracks terminate through the existing ambiguity
rules. The boundary-region row at median Y850 receives two established-parent
costs **0.643284 / 0.661409**, a 0.018125 gap inside the same 0.08 margin.
The competing parents have previous median rows Y829 and Y861.5. A second
conflict involves the Y869.5 row. No assignments survive at this offset.

The Y850 row restarts as `oil-tracklet:000108:0026`, with its first observation
marked incompatible. Its material-path, distributed-Sobel and high-recall
members include anchors, but that incompatible observation cannot provide
confirmation evidence. The later compatible medians are:

| Time | Median Y | Anchor signal | Included in confirmation |
|---|---:|---|---|
| 54 s | 850 | yes | no: incompatible branch |
| 54.5 s | 851.5 | no | yes |
| 55 s | 852.5 | no | yes |
| 55.5 s | 852.5 | yes | yes |
| 56 s | 851 | yes | yes |

At the last endpoint there are four compatible observations, two anchor frames
against a required three, and 0.5 px net progress against 5.2 px. The previous
window reaches only 1 px. No confirmation profile passes. The reported
`INCOMPATIBLE_BRANCH` failure describes the track history; it does **not** mean
every later observation is individually incompatible or that the track can
never recover. The actual bounded evidence still fails without the first row.

**Competing 56 s winner.** Track `000109:0028` associates median rows
823.5 → 838 → 866 at 54.5/55/56 s. Three observations, two anchors, a physical
proposal flag and 42.5 px directed progress satisfy `ANCHOR_TRAJECTORY`.
At 56 s its publishable row representative is phase-scan Y874; after the
55.5 s UNKNOWN, it scores 0.264504 versus UNKNOWN 0.217841. No competing
publishable Oil owner is available for the margin check. Its final selection
follows the lower glass rim in the prior review.

This contrast identifies a failure risk, not permission to force admission:
a regional target can remain provisional while a different geometrically
plausible chain confirms. Restoring OFF track IDs is not a physical repair.
For example, OFF's later Y851 owner previously associates a Y880.5 row to Y848.
Neither coordinate proximity, motion nor the binary physical-proposal flag
certifies the cross-frame physical identity of these associations.

## Foam: a recorded edge convention changes before episode rejection

Current Foam measurements remain equal between OFF and scoped. Their final
Foam endpoint losses predate the scope, but the exact episode windows need not
be equal: final Oil availability participates in segmentation after independent
Foam detection. This preserves two series and does not give Foam authority
over Oil selection.

The FULL capture records the selected bright component as follows. Source
bounds are half-open; `lower` therefore uses bottom minus one. These are
detector component descriptions, not physical labels.

| Time | Component Y range | Phenotype | Front convention | Component front | Current public Foam |
|---|---|---|---|---:|---:|
| 53 s | [808,833) | detached_droplet | upper | 808 | 808 |
| 54 s | [808,834) | detached_layer | lower | 833 | 833 |
| 54.5 s | [808,835) | detached_layer | upper | 808 | unavailable: persistence pending |
| 55 s | [858,884) | none | upper | 858 | unavailable: persistence pending |
| 55.5 s | [810,838) | detached_layer | lower | 837 | 837 |
| 56 s | [810,839) | detached_layer | lower | 838 | 838 |

`foam_front_detector._detached_material_phenotype` chooses the lower edge for
the detached-layer cases carrying `front_from_lower_edge`; the existing
structural-substrate relation supplies this flag. Thus part of the front jump
is a change in the measured edge of the component, not demonstrated physical
Foam motion. The component mask's material identity is still not certified.
At 55 s the selected component itself changes; its strong component score
does not bypass the separate current-frame persistence guard.

The unchanged episode owner supplies these exact rejection predicates:

| Endpoint / variant | Eligible candidate-front rows | Formation failure |
|---|---|---|
| 54 s / both | 813,811,808,813,833 over 52–54 s | rise −20 px, agreement 0.5; stable span 25 px exceeds 3 px |
| 56 s / OFF | 808,837,838 at 54.5/55.5/56 s | rise −30 px; stable span 30 px; extent evolution also false |
| 56 s / scoped | 837,838 at 55.5/56 s | stable span 1 px passes, but two-observation substantial-layer support and extent evolution fail |

Material, coherence, static and dynamic segment predicates pass in these
windows. The scoped 56 s window excludes 54.5 s because the missing 55 s sample
and changed final-Oil availability split the dynamic segment. This difference
must not be described as identical Foam processing after composition. An
eligible sequence candidate can still exist when current publication is
persistence-pending. None of these facts establish that the rejected front is
the correct physical Foam front; relaxing formation now would skip that test.

## Physical review boundary and next design

The [original/guide comparison](2026-10-09-local-xy-foam-front-review.png)
uses stored originals at 54/55.5/56 s and short cyan guides at the stored Foam
proposal coordinates. All four read inputs are hash-preserved. The guides are
scalar indicators, not traced contours or new pixel labels. Oil's already
confirmed yellow-Foam/dark-Oil target remains closed.

**Agent interpretation, not human truth:** the guides appear within the
yellow/bright material, near the lower part of the brighter cap. It is unclear
whether both sides are Foam with an internal appearance difference or the
guide marks a physically distinct Foam/material boundary. This is the next
human checkpoint; no exact XY or Windows work is needed.

The answer determines whether D5 must first repair raw front meaning or can
study loss of a physically supported front at episode confirmation. If the
front remains unassessable, keep that branch unresolved. A correct physical
boundary is not automatically the product's Foam-front target: compare its
role with [the separate Foam definition](../../rotary_oil_level_tracker_ssot_spec.md#117-foam-front-정의)
before behavior changes. Do not silently redefine the product or switch all
detached components to their upper/lower edge.

For Oil, this saved-input investigation is complete. Any subsequent O2 support
proposal must distinguish actual candidate support and cross-frame identity
before using the current row group as proof. Keep 52 s selection and 54–56 s
admission as separate regression checks. Do not repeat the reciprocal-assignment
probe, remove its physical-child guard, lower anchor/progress thresholds,
copy neighboring truth, or expand the local mask to each new winner. No O3/O4
entry or Oil/Foam behavior repair is adopted by this readout.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F07`, `S11-F10`.
- First harmful stage: the first physical association error remains unknown. Supported numerical losses are committed-owner selection at 52 s and ambiguity/confirmation at 54–56 s. Foam component-front edge convention changes before episode rejection; whether this is physically wrong awaits the bounded review.
- Logic-map impact: NONE — existing owners are observed without source, policy, control-flow or publication changes.
- Failure-registry impact: UPDATED — F04 records the exact ambiguity/confirmation contrast; F07 records edge-convention changes and the separate raw/episode review boundary.
