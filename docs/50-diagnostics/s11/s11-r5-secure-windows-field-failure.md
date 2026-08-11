# S11-R5 Secure-Windows Field Failure

## Responsibility and evidence boundary

This diagnostic records the operator's synchronized visual comparison of R5
against the private Base/Accum field video. The source video cannot leave the
secure Windows machine, so its numerical results are field evidence supplied by
the operator and cannot be reproduced in this checkout. Current sequence and
acceptance belong to the work plan and R6 validation contract.

## Demonstrated failure

R5 increased nominal valid coverage while decreasing physical agreement.

| Glass | Nominal valid | Dominant output | Visual reality | Failure |
|---|---:|---|---|---|
| Base | `594/601` (`98.8%`) | `FULL_WITH_FOAM` `81.5%` | starts FULL, no Foam, descends and recovers | vertical light streak/glare published as Foam; Oil line follows glare |
| Accum | `600/601` (`99.8%`) | `EMPTY_NO_INTERFACE` `92.3%` | EMPTY, rise, turbulent Foam, high, fall | initial EMPTY persists through the complete visible cycle |

The first useful Accum Oil observation occurred only after the visual maximum,
and `OIL_DROP_START` was approximately `49 s` late. Every Base Foam event was a
false positive. Aggregate coverage therefore measured state filling and false
Foam publication, not detector effectiveness.

## Code-level causal chain

Read-only inspection of the exact R5 head found four interacting causes.

1. `preprocessing.py` defines glare only as pixels above one absolute grayscale
   threshold. Unsaturated caustic crescents and vertical reflection ridges are
   invisible to that mask.
2. current-frame Foam is evaluated before Oil and an accepted or strong-pending
   Foam component may mask Oil evidence and constrain candidate topology. The
   supposed later independent sequence cannot recover Oil evidence removed here.
3. the R5 Foam resolver reads the first finite raw Foam candidate without
   honoring current-frame rejection. Mask/front/score jitter can override high
   static overlap and confirm a fixed optical component.
4. the R5 Oil/state lattice treats its input `fill_state` as fresh state evidence,
   repeats the confirmed initial prior in every layer, and only allows an EMPTY
   prior to release through a narrow bottom entrance band. A missed entry makes a
   later mid-glass observation prohibitively expensive.

The Oil resolver also considers current-frame non-selected candidates without an
explicit eligibility bit. This was intended to preserve weak material evidence,
but it cannot distinguish comparative rejection from topology/glare invalidity
when those facts are absent from the candidate packet.

## Why minor tuning is rejected

- raising the Foam score threshold would also remove real Accum Foam because the
  false Base component already scores strongly;
- lowering Canny/Hough or Oil confidence produces more reflection candidates;
- CLAHE is already active and cannot identify optical cause;
- mask turnover without registration/exposure compensation classifies lighting
  jitter as Foam dynamics; and
- interpolation or event debounce can only make the wrong track smoother or the
  late event more stable.

## Required repair class

The evidence reopens detector architecture. R6 must improve the raster evidence
and remove circular publication authority before it tunes report continuity.
The private video stays a holdout: constants may not depend on its identity,
coordinates or event timestamps.
