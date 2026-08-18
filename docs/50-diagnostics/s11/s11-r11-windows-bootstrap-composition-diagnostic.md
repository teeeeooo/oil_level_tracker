# S11-R11 Secure-Windows Bootstrap and Composition Diagnostic

## Scope

This diagnostic reconciles the exact pushed R11 head `e6511ce` against the
private secure-Windows Base and Accum videos. Direct source-frame overlays are
the visual oracle. Aggregate coverage is supporting evidence only.

The first extraction mixed current-frame trace members with final sequence
annotations and also mixed source-frame and ROI-local Y coordinates. The
figures below use `record.sequence`, `tracking_data.csv` and the explicit crop
origin. Those corrections are part of the result, not optional interpretation.

## Final-sequence integrity

Final sequence output and `tracking_data.csv` agree exactly.

| Glass | numeric Oil | CSV numeric Oil | matching Y | invalid selected cardinality |
|---|---:|---:|---:|---:|
| Base | 39 | 39 | 39 | 0 |
| Accum | 418 | 418 | 418 | 0 |

Every numeric row has exactly one selected same-frame Oil candidate and its Y
equals the public raw Oil Y.

## Base: bounded bootstrap still changes physical identity

R11 removed the R10 583-frame retroactive lower-structure run. It did not
recover the reviewed interface at the important 540, 634 and 674 s points:

- 540 s, actual source Y437: no candidate within 25 px;
- 634 s, actual source Y360: candidates at Y380 and Y338 remain continuation
  only and stop at `NO_TRAJECTORY_SUPPORT`; and
- 674 s, actual source Y435: no candidate within 25 px.

The only final numeric output is two late runs. The principal run spans
729.5–744.5 s and contains 31 rows at Y828–873. Twenty-nine rows receive
`calibrated_bootstrap`; eight motion keyframes have registered Oil motion
support 0.183–0.780 and coverage exactly 0.60. A second 746.5–750.0 s run adds
eight rows at Y723–740.

Direct overlays classify representative members as:

| time | selected Y | visual class |
|---:|---:|---|
| 730.5 s | 831 | reflection |
| 735.0 s | 843 | actual liquid interface |
| 743.5 s | 843 | bracket reflection |

The same path therefore changes physical identity even while remaining at a
compatible coordinate. All eight keyframes have zero cross-representation and
zero semantic-corridor support. Existing edge scalars favor reflection rather
than the diffuse true interface: polarity confidence is 0.0019 and broad
strength 0.2234 at 735 s, versus polarity 0.0487 and broad strength 0.2974 at
the 743.5 s reflection.

User Artifact templates correctly reject registered structures near source
Y664, Y898 and Y920–941. The selected Y724–873 path occupies an unregistered
band. A new fixed Y exclusion is not a valid repair because actual liquid and
reflection both occur at Y843.

The root causes are therefore:

1. high-recall generation misses the actual interface in important spans;
2. calibrated motion is allowed to create anchor authority without an
   independently available material-phase identity; and
3. path continuity constrains Y but does not prove that adjacent members are
   the same physical boundary.

## Accum Oil: distinct-lower reserve became generic anchor authority

Accum publishes 418 Oil rows in 34 runs. Wrong rows are dominated by
`foam_distinct_lower_boundary`, including long Y602–606, Y353–557 and Y334–521
runs. The known 683–694 s Y190–209 residue run remains wrong: direct R10/R11
overlay reconciliation places the actual lower Oil interface near Y450.

The observation-only Foam material track seeds on 89 frames, continues on 495
frames and opposes 715 candidates. A selected candidate with
`r11_foam_material_identity=0` does not prove that the track was absent.
Distinct-lower authority requires an active material row and low opposition;
zero is expected for a candidate considered separate from that row.

The failure is the authority policy:

- vertical separation from the long-lived material track can directly create
  an anchor;
- the track may continue candidate-to-candidate for most of the window without
  a bounded reseed age or cumulative drift;
- residue represented by a non-material-path `oil_hypothesis` may bypass the
  material-path-only identity opposition; and
- actual lower candidates near Y450 can remain outside final admission while a
  vertically separated high-recall row is retained and anchored.

Missing candidate-family evidence compounds this result. High-recall candidates
do not provide all texture, optics and signed material terms. Compatibility
projection treats several unavailable conflicts as numeric zero, which is not
equivalent to affirmative clean evidence.

## Accum Foam: real evidence is fragmented and then invalidated

Within 650–700 s, 44 raw Foam-front frames become 22 sequence-eligible frames
and nine confirmed/public Foam rows. The main admission loss is the fixed
`component_width_ratio >= 0.55` requirement: 18 raw candidates fail width and
seven `accepted_strong` current-frame observations are sequence-ineligible,
although registered dynamic evidence distinguishes them from the static Base
false-Foam class.

The confirmed Foam front rises from source Y465 to Y218. Missing admission rows
and rapid 58–65 px changes fragment nine rows into six graph groups. All nine
confirmed rows nevertheless become invalid because the final composer adds
both `R7_FOAM_OIL_TOPOLOGY_CONFLICT` and
`R8_FOAM_OIL_TOPOLOGY_CONFLICT`.

Coordinate-correct mask review uses Accum crop origin Y56:

| time | Foam Y | Oil Y | material bottom | mask source span | Oil-row coverage |
|---:|---:|---:|---:|---|---:|
| 673.0 s | 346 | 450 | 516 | 346–516 | 0.7965 |
| 676.0 s | 224 | 485 | 519 | 224–519 | 0.5952 |

At 673 s, 18.44% of the below-Oil ROI is still selected by the Foam material
mask. At 676 s the raw mask is present even though the current-frame
`foam_accepted_component` image is empty because that image is gated by the
pre-sequence `persistence_pending` decision. The final episode resolver later
confirms the frame.

The material component is therefore a broad Foam/transition/Oil evidence
region, not a Foam-only physical segmentation. Its bottom cannot be a hard
topology veto. The simultaneous `R10_FOAM_LAYER_SEPARATED` and topology-conflict
flags expose the contradiction. Final graph validity then reuses one global
`TrackingSample.is_valid` for Oil and Foam, hiding every confirmed Foam row.

## Required replacement, not an added revision layer

The next detector revision must replace the failed policies:

- motion may discover and retain a recovery path but cannot independently
  create Oil anchor authority;
- candidate evidence must distinguish unavailable from measured-clean terms;
- path identity must include material-side phase change, not only Y/motion;
- a vertically distinct lower row is reserved for ordinary evaluation and is
  not an anchor by separation alone;
- Foam identity continuation is bounded by reseed age and cumulative drift and
  applies by physical identity across candidate families;
- dynamic narrow Foam onset remains eligible;
- the broad material-component bottom is not a hard Oil/Foam topology veto;
  and
- Oil and Foam publication validity are independent graph concerns.

No Base/Accum name, timestamp, path or truth coordinate may enter production
control flow.
