# S11-R14 Secure-Windows Field Result

## Result

The exact R14 private-Windows Base/Accum replay failed S11 effectiveness. CSV
publication and final sequence output were internally consistent, but reviewed
Oil/Foam behavior did not meet the field contract. This completed evidence
authorizes R15; it does not authorize private-video coordinates in product
code.

## Run identity

- resolver: `r14-phase-component-replacement-v1`;
- analyzed interval: 480--780 s at 2 FPS;
- records: 601 Base and 601 Accum;
- initial state: Base `FULL_NO_INTERFACE`, Accum `EMPTY_NO_INTERFACE`;
- saved Recipes retained their user-confirmed Artifact templates.

## Final publication

| Glass | Final Oil | Valid Oil | Final Foam | Valid Foam | Unknown |
|---|---:|---:|---:|---:|---:|
| Base | 164 | 164 | 0 | 0 | 437 |
| Accum | 129 | 129 | 23 | 23 | 472 |

Final Oil was counted only when final sequence kind was Oil with finite source
Y. Final Foam flags, sequence Foam Y and CSV Foam Y shared the exact same 23
timestamps.

## Base observation

Base published three Oil runs:

| Time | Frames | Y range | Component |
|---|---:|---:|---|
| 548.0--612.5 s | 130 | 350--391 | `oil-component:114:0` |
| 635.5--640.5 s | 11 | 655--656 | `oil-component:275:4` |
| 660.5--671.5 s | 23 | 352--434 | `oil-component:114:0` |

At the first two intervening gaps, reviewed same-component candidates existed
and the best path often selected Oil, but continuation bounding changed the
frame to UNKNOWN after the last qualified anchor. Incompatible component
handoff itself remained separated by UNKNOWN, as required.

## Accum initial EMPTY observation

Four false Oil runs were published before the reviewed 650 s Oil entrance:

| Time | Frames | Y range | Dominant source |
|---|---:|---:|---|
| 482.0--485.5 s | 8 | 478--479 | material path |
| 494.5--497.5 s | 7 | 478.5--479 | material path |
| 500.0--502.0 s | 5 | 478.5 | material path |
| 534.0--537.0 s | 7 | 478.5--481 | material path |

The rows were stationary lower structures with cluster and trajectory support.
The real Oil later entered through the same lower area and moved upward, so a
fixed coordinate/Artifact exclusion is not a valid repair.

## Accum Foam funnel

In the reviewed 672--780 s interval:

| Stage | Frames |
|---|---:|
| Raw Foam candidate | 113 |
| Sequence eligible | 80 |
| Episode confirmed | 23 |
| Final sequence Foam Y | 23 |
| CSV Foam Y / `foam_is_valid` | 23 |

The 23 confirmed frames were concentrated at 758--774.5 s. A 34-frame eligible
group at 656.5--677 s had material support 0.779, coherent ratio 1.00 and
registered dynamic evidence in 33/34 frames, but was Oil-alias rejected.

Direct code/trace reconciliation showed the signed alias defect at 671.5 s:
FoamY 411 and OilY 327 produced separation -84 px, which passed
`oil_y - foam_y <= 5.832`. Large negative/inverted topology was therefore
treated as same-boundary alias. Candidate-only alias and prior-alias continuation
also had more authority than final independent Foam ownership.

Later parent groups correctly retained only their dynamic-onset subgroups:
18 confirmed frames from the 738.5--769.5 s group and five from the
771.5--779.5 s group. Static Y80 prefixes remained unconfirmed.

## Disposition

R14 is a failed field holdout with useful partial recovery. R15 must preserve
same-frame provenance and component isolation while replacing initial-EMPTY
admission, one-sided continuation, Foam/Oil alias ownership and detached Foam
shape classification.
