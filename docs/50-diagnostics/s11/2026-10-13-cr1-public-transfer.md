# CR1 fixed-bank public-source transfer — 2026-10-13

**COMPLETE_DIAGNOSTIC_ONLY; no promotion.** The preflight and adapter were committed
at `9e106cd830286a18787465865dbcf1dfa7395fb7` before model execution. This is one exposed-development
comparison on the already reviewed public-miso frame, after separating the
[sample4 practical acceptance](2026-10-13-cr1-competitor-role.md) from physical truth.
The [Work Plan](../../00-project/work-plan.md) owns progression. This record does
not reopen CR1's original failed trial or select an operating point.

## Frozen input and reuse

The [preflight](2026-10-13-cr1-public-transfer/preflight.json) pins the unchanged
CR1 encoder implementation, dependency versions, readiness/model hashes, three
sample4 reference images, original visibility masks and public source artifacts.
The [position reply](2026-10-12-public-compressor-source/position-review/position-review.json)
confirms Foam-upper rows323–338 and Oil-upper rows421–435 at native X578 in
f1499 / 50.01663333333334 s. It establishes containment, not a unique edge or truth
for every row/candidate in those ranges.

The full floor/ceil cover of both pixel-cell intervals gives **35 regional
anchors**: Foam range Y322–339 and Oil range Y420–436. Every anchor remains
`UNREVIEWED_ANCHOR`; no middle row, strongest edge or score maximum is selected.
This roster tests context representation over position uncertainty. It is not a
subset of a new detector candidate-accuracy population or a set of 35 positives.
The source is exposed development, with no untouched holdout or proved episode
independence. The second, low-quality public source and sample3 are not used.

Reuse the frozen encoder, descriptor, rank/missing/tie rules, model loading,
CPU limits and offline runtime guard from `probe.py`. The
[transfer adapter](../../../tests/diagnostics/s11_contextual_role_transfer.py)
adds only native rectangle padding and dimension-aware strip weights/support:
the historical helper assumes a 104-square ROI and cannot address this native
210×228 ROI without a separate geometry boundary. Reference weights at edge104
are tested bit-for-bit against the original helper. No old runner is changed.

## Geometry and execution boundary

Public pixels retain their native coordinates and resolution before encoding.
Add nine invalid rows above and below the 210×228 crop, then use the existing
single 228→224 encoder resize. Invalid padding becomes the encoder's normalization
mean. Full/local use the same transform, visibility and ±12 native strip offsets;
local keeps the same 25×25 box without enlarging it. Source X578 stays X578.

The public token spacing is 14.25 native pixels versus 6.5 for the unchanged
sample4 references. This is a disclosed source/scale transfer, not newly calibrated
localization or a perfectly isolated causal context intervention. All 35 anchors
have 21 common visible columns before scoring. Upper/lower token overlap varies
from 0.20095693779904308 to 0.5, so native pixel sampling is not independent token
evidence. The geometry controls passed **13 tests in 0.14 s** before scoring.

The real encoder must first pass a four-forward pixel control on the new padded
geometry: changing remote pixels leaves local tokens identical, changes full
tokens, and leaves the strip descriptor defined. Then run the entire fixed roster
once. Bound execution to 64 forwards, 180 s, 10 s per forward and 2 GB peak RSS;
keep the existing 3 GB total footprint cap with a conservative external reservation.
There is no video decode, production detector, new environment or network fallback.

Retain each anchor's three raw role scores, availability, preference and token
support for both views. A favourable row or range average is not physical success.
An inability of every sampled anchor to meet the local-role condition can limit
this fixed comparison; it does not establish universal model failure. The existing
bank has no Foam-upper class, so Foam-upper context cannot become a calibrated
negative or an upper-front detector. `tau_support` and physical accuracy stay unset.

Stop after this comparison or an input/control/resource failure. No crop, scale,
bank, margin or source retry follows from an unfavourable result.

## Complete comparison and interpretation

The [complete readout](2026-10-13-cr1-public-transfer/readout.json) preserves all
35 anchors, 70 three-class vectors and their actual support weights. All anchors
were measured with 21 common columns; there were no missing results or ties.

| User-confirmed containment region | Anchors | Full preference | Local preference | Local interface score range |
|---|---:|---|---|---|
| Foam upper | 18 | interface 16, texture 2 | interface 18 | 0.243390–0.384663 |
| Oil upper | 17 | structure 17 | interface 6, texture 11 | 0.298809–0.521209 |

Within the Oil region, local preference is interface at Y420–422 and Y434–436,
and texture at Y423–433. Neither group has point-level truth. The ranges overlap
in absolute interface support; this is not a calibrated confidence comparison.
Do not select the favourable anchors, treat the regional roster as required
variants of one candidate, or call all 18/17 anchors physical positives/negatives.

This result does not establish reliable Oil-versus-Foam-upper role separation
by the fixed three-reference bank. The bank has no Foam-upper reference; upper
context favouring interface is therefore not a measured false positive. Likewise,
Oil-region texture preference is not candidate-level false-negative evidence.
The source/scale transfer does not identify which of appearance, token footprint,
reference scope or exact edge position caused the preference. A cutoff cannot
resolve that missing semantic qualification, and no cutoff is fitted here.

Keep the earlier `SCOPE_LIMITED_USEFULNESS` finding at its original scope. This
separate diagnostic adds no promotion, independent evaluation, native candidate
selection, physical cadence or report-effect claim. The sample4 B practical
acceptance remains separate from physical truth. Further Oil policy work needs
qualified inputs and a justified observation operation; do not silently replace
the bank/crop after this result. Foam-upper research remains an independent P5-a
design with its own controls before any raw-front or episode change.

## Execution, verification and retention

Execution used the existing isolated CPU environment from `/private/tmp`, the
unchanged encoder and all 159 readiness model/source pins. All 16 preflight pins,
native source-crop pixels, mask arrays, query roster and reference input hashes
matched. The actual pixel control passed: remote-pixel changes affected full
tokens while local tokens stayed exactly equal, and descriptors remained defined.
The two denied audit events were the deliberate network/write guard smoke checks.
No other denied event, network access or video decode was needed.

- Total measured runtime: **6.527 s**, including **4.785 s** encoder load and
  **0.076 s** saved-raster preparation; this is not video/report/Windows timing.
- **46 forwards**, maximum **0.052759 s** each; **601,554,944 bytes** peak RSS.
- Workspace allocated bytes at measurement: **743,653,376**; the additional
  **500,000,000-byte** external reservation keeps the total below the 3 GB cap.
- Post-run saved audit: preflight/roster equality, all 70 finite score vectors,
  preferences/margins and unit-mass strip weights pass. No model rerun is needed.

Managed run `public-transfer-20261013-001` is closed. It reuses the canonical
preflight and **152,343-byte** complete readout, with no duplicate media, dense
token maps or retained work output. Review retention when a successor replaces
this source/geometry comparison's decision value. The 13 pre-inference geometry
tests and actual integration run validate the adapter's tested path, not a
detector improvement or field acceptance.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-PROJECTION`, `FOAM-CANDIDATE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: physical-role qualification remains unresolved in this offline transfer; no candidate-selection stage was executed. Interval containment cannot be expanded into per-anchor truth, and the existing bank has no Foam-upper prototype.
- Logic-map impact: NONE — this is an offline input/geometry comparison using an existing fixed encoder/bank; no runtime selection, scalar publication or Foam episode owner changes.
- Failure-registry impact: NONE — existing coordinate/provenance and threshold-rescue guards apply; no new mechanism or field repair is claimed.
