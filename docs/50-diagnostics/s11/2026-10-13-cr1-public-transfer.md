# CR1 fixed-bank public-source transfer — 2026-10-13

**Preflight frozen before model execution.** This is one exposed-development
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
bank, margin or source retry follows from an unfavourable result. Managed run
`public-transfer-20261013-001` will retain this preflight and the compact complete
readout, referencing existing originals rather than copying them. Token maps and
scratch metadata are disposable. Review retention when a successor replaces this
source/geometry comparison's decision value.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-PROJECTION`, `FOAM-CANDIDATE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: unknown for this unexecuted transfer; original context preferences do not establish physical role, and interval containment cannot be expanded into per-anchor truth.
- Logic-map impact: NONE — this is an offline input/geometry comparison using an existing fixed encoder/bank; no runtime selection, scalar publication or Foam episode owner changes.
- Failure-registry impact: NONE — existing coordinate/provenance and threshold-rescue guards apply; no new mechanism or field repair is claimed.
