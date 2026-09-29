# S11 O2 fixed-score reversal follow-up

Source: subsequent user-supplied Windows analysis of the unchanged run-001
experiment JSON (`664547213e915a2e...`). No private JSON was inspected locally.
The original [run record](s11-o2-fixed-score-windows-run-001.md) remains unchanged.
[Method contract](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md);
[acceptance owner](../../30-validation/s11-interface-observability-witness-validation.md).

## Reported arithmetic attribution

BASE idx8 near Y397 versus idx10 off Y378 at native X=[130,236] has all three
common scales. Stored formulas reportedly reproduce exactly.

| BW | Near C / A / L / combined | Off C / A / L / combined | Order |
|---|---|---|---|
| 8 | .4567 / .7146 / .6590 / .5991 | .2905 / .7110 / .5439 / .4825 | correct |
| 16 | .3681 / .7269 / .3367 / .4483 | .2777 / .7057 / .4961 / .4598 | reversed |
| 24 | .1891 / .7098 / .1236 / .2551 | .1390 / .7063 / .1316 / .2347 | correct |

C and A favor near at every scale; L at BW16 is sufficiently lower for near to
reverse the product. Both separate combined medians are their BW16 values, so
the point ordering is reversed. L never changes sign: the score is nonnegative.
This is an order reversal, not a contrast-polarity change. Median aggregation is
not a vote on three pair outcomes; two correct scale orderings do not guarantee
correct ordering of the two score medians. No implementation error or alternative
aggregation's superiority is established by this example.

BASE idx0 interface uses candidate_center because no native geometry exists;
this is the prescribed representation, not fallback after a native score failure.
It has 3/5 common points. Idx11 non_interface uses native_path, 2/3 common points,
with one common scale per usable point. Reported candidate matched scores:

| Candidate | C | A | Combined |
|---|---|---|---|
| 0 interface | .2427 | .7712 | .3284 |
| 11 non_interface | .2606 | .8034 | .3882 |

All methods reverse this pair. These are feature-score and representation/support
differences; they do not establish that the true interface has physically weaker
visual information. Detailed point distributions were not supplied. No candidate
identity is inferred from point majority or strength.

## Missing evidence attribution and corrections

The report attributes all ten unscorable interface-location pairs to idx8's off
point at X=[449,555], Y405: far_above.gray_mean is null at every scale. Under the
verified source, combined is **null, not zero**, and common_scale_count=0. Raw C/A
may remain available; matched baselines inherit the combined support restriction.
Their raw availability must be checked before describing all three methods as
intrinsically unable to score that point.

The second null native point is idx11 X=[343,449], Y922. It contributes no
interface-only location pairs, because its identity is non_interface. However,
the follow-up's statement that it matches no identity-negative controls conflicts
with known exact-X near points idx8 Y397 and idx9 Y419, and with run-001's two
unscorable identity-negative-control pairs. Source logic predicts those two
matches. Confirm directly from stored pair rows; do not mark that claim verified.
The 17-point inventory includes all native identities, while interface_location
uses only the 14 points belonging to interface identities.

## Remaining bounded check / engineering implication

Windows should read existing outputs to confirm null versus zero for idx8 Y405,
list the unscorable native pair keys separately for each task, and report raw
versus matched C/A/combined availability for that one point. Preserve original
files and score definitions; no new annotation or detector execution is needed.

Evidence now supports testing the dependency on far-band locality separately
from point/candidate aggregation. It does not justify a threshold tweak, selecting
a winning aggregator on this one pair, or promoting alignment to an identity
classifier. Keep the first experiment immutable and require an explicit next
hypothesis before modifying executable scoring. FIELD FAIL remains unchanged.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: reported BW16 locality weighting reverses a reviewed same-X ordering, then separate medians retain the reversal; physical identity discrimination remains unsupported and missing evidence must not be encoded as zero.
- Logic-map impact: NONE — follow-up evidence changes no runtime or score implementation.
- Failure-registry impact: NONE — documents offline hypothesis limitations without asserting a new production mechanism or field repair.
