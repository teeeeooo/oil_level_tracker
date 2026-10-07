# A2 ordered spatial patch correspondence — cadence diagnostic

Date: 2026-10-07. Frozen probe `0f5eed7`; recorded-geometry clarification and
completed-run head `d0f40c8`. Status: bounded measurement complete; intermediate
physical agreement awaiting human review. No production adoption; `FIELD FAIL`.

## Human constraint and hypothesis

The user confirms **“연속해서 이어짐. 단, 유면의 오르내림이 급격하게 이뤄짐”**:
the actual Oil boundary continues between 42.5 and 44 s while rapidly rising and
falling. The [attributed reply](../../50-diagnostics/s11/2026-10-07-sample4-temporal-context-human-reply.json)
does not supply intermediate coordinates, a numeric speed bound or a contour.
It closes the prior continuity question, not the accuracy of a computed track.

The [frozen contract](../../20-architecture/s11-interface-observability-witness-architecture.md#a2-ordered-patch-temporal-correspondence--bounded-diagnostic)
tests whether retaining ordered BGR appearance across a recorded candidate and
using native-frame correspondence avoids sparse-cadence aliasing. It compares
the same full-ROI vertical search at 30 fps and 2 fps. There is no displacement
penalty, small-motion bound, polarity veto or chosen-Y threshold. Per-channel
mean centering removes additive offsets; all forward/reverse losses and exact
ties remain available. This extends the existing offline temporal probe because
its fixed-coordinate registered residual cannot express displaced patch matches.

The accepted production replay uses `SAMPLING_FPS=2.0`; this experiment does not
change that setting or replay production at a different cadence. No whole-ROI
camera transform, glare exclusion or physical material classification is claimed.

## Execution and observations

All inputs are the previously saved original 40–45 s PNG crops. The matcher sees
only BGR rasters and recorded geometry, with the search bounded to the original
104×104 ROI. The BW=3 envelope has radius 10 / height 21; it includes the center
gap beyond original O1 bands. Each recorded center/native sector view is retained
separately, including missing sectors and deduplicated coincident centers.

Seven starting candidates comprise four confirmed target observations and three
wrong-target observations at 40/42/42.5/44 s. Both directions and both cadences
produce **156 appearance chains and 6,240 links**. Physical labels apply only to
the starting candidates; none transfers automatically to subsequent rows. This
is not 6,240 independent reviewed examples. No exact tie occurred in this run.

The central recorded strip X=[584,605), starting at the correct 42.5 s candidate
Y835, shows a material cadence difference:

| Time | 30 fps appearance match Y | 2 fps appearance match Y |
|---|---:|---:|
| 42.5 s, initial query | 835 | 835 |
| 43 s | 829 | 885 |
| 43.5 s | 830 | 885 |
| 44 s | 839 | 885 |

At 44 s the already confirmed actual Oil candidate is Y844. These appearance
rows are neither detector candidates nor accepted scalar observations. No pixel
tolerance or complete native-path truth is invented to score them. The 2 fps
central chain jumps to the lower part of the glass at 43 s and stays there. Its
first jump fails reverse correspondence; later matches there are reciprocal.
Reverse consistency after a jump therefore cannot retrospectively validate it.

The five center-sector matches at 44 s are [834,848,839,851,836] for 30 fps and
[835,845,885,843,836] for 2 fps. They are separate appearances, not one fitted
physical contour. A median would hide both disagreement and the lower alias.

| Cadence | Starting candidate role | Reciprocal / measured links |
|---|---|---:|
| 30 fps | Confirmed target seed | 2,999 / 3,150 |
| 30 fps | Wrong-target seed | 2,688 / 2,700 |
| 2 fps | Confirmed target seed | 183 / 210 |
| 2 fps | Wrong-target seed | 176 / 180 |

Wrong-target seeds can have excellent reciprocal appearance correspondence.
Neither a low matching loss nor reciprocal consistency is a sufficient Oil
identity rule. No threshold sweep, score fit, identity prediction or W3 efficacy
score is produced from this measurement. The sparse central chain is unsuitable
for adoption; native cadence's intermediate physical agreement is still unknown.

## Verification, review and preservation

**26 focused tests passed**, covering large displacement, additive exposure,
reciprocal recovery, repeated/constant pattern ambiguity, static structure without
identity, ordered-pattern differences hidden by pooling, border unavailability,
invalid input and the unchanged earlier registered-residual contract. All
production-source hashes and saved raster/packet/probe pins were rechecked.

The initial adapter assumed every sector had a `candidate_center` entry and
aborted before a result was emitted. Some recorded sectors contain a deduplicated
native-path entry instead. The corrected adapter keeps every recorded geometry
view; that clarification was committed before the completed run. No experiment
parameter was changed in response to results.

The [receipt](2026-10-07-a2-patch-correspondence.json) retains the frozen spec,
source/input hashes, per-chain summaries, aggregate counts and full artifact pins.
Full forward/reverse loss curves, scripts and review remain under
`sample/output/s11-a2-patch-correspondence-20261007-001/`. Original audit/worktree
evidence is preserved. These unique local artifacts are not disposable scratch.

The synchronized review shows original pixels alongside the central orange
30 fps hypothesis and pink 2 fps hypothesis. Pink appears only at actual compared
frames; no intermediate line is interpolated. Optional cyan guides show only
the already reviewed endpoints. Browser checks verified playback, frame jumps,
and hiding the sparse hypothesis on intervening frames.

The pending question is whether orange follows actual Oil through 42.5–44 s or
drifts onto another layer/pattern. This judges the computed correspondence,
not the already established physical continuity. Until resolved, there is no
basis to turn the appearance chain into identity, transplant it into W3 as a
positive prediction, or change authority/selection.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the existing confirmed alternatives still lose eligibility at `OIL-AUTHORITY`; this diagnostic additionally observes a sparse-cadence appearance alias, not a proven cause of the production rejection.
- Logic-map impact: NONE — an offline measurement owner is extended without production wiring, authority, association or publication changes.
- Failure-registry impact: NONE — the experiment illustrates existing motion/appearance identity leakage; no failed mechanism is promoted or retired and no private-coordinate rule is added.
