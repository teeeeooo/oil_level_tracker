# S11-R14 Windows State and Foam Ownership Diagnostic

## Disposition

The exact R14 private-Windows replay improved Base recall but failed S11 field
acceptance. It authorizes the R15 replacement architecture; it does not
authorize field-specific coordinates or threshold tuning.

## Base

Base published 164/601 Oil frames in three runs. The main reviewed component
was detected, but anchor-free one-sided tails were removed by continuation
bounding. A brief incompatible component was separated correctly by UNKNOWN.
The failure is continuation ownership after the last qualified anchor, not a
reason to permit direct cross-component Oil transitions.

## Accum initial EMPTY

Accum published four false Oil runs during the reviewed 480--650 s EMPTY
interval. Every run was a nearly fixed Y478--481 lower material path lasting
five to eight frames. The real later Oil entered at the same lower area and
moved upward, so position or Artifact calibration cannot distinguish them.
Initial-EMPTY admission must use bounded direction rather than a fixed Y veto.

## Foam

Accum produced 113 raw Foam frames, 80 sequence-eligible frames and 23 final
confirmed/public frames. Confirmed flags, final sequence Foam Y and CSV Foam Y
had identical timestamps.

The 656.5--677 s eligible group contained a coherent, strongly dynamic real
Foam trajectory but was Oil-alias rejected. Code audit found a signed condition
`oil_y - foam_y <= tolerance`; at 671.5 s it classified OilY 327 and FoamY 411
as the same boundary despite an inverted -84 px separation. R14 also allowed
unselected strong Oil proposals and a prior alias track to veto Foam. These are
material-ownership defects, not missing Foam episode dynamics.

Later confirmed Foam came from dynamic onset subgroups. Static Y=80 prefixes
correctly remained unconfirmed. Large wall/droplet-shaped Foam also exposed a
detector phenotype gap: layer evidence could be weak or fragmented even when a
compact material body was visually present.
