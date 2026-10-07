# S11 episode source review and texture probe

Base: `a5cbf65f44cb2f6c3ff2c2de610bf89eb92467b7`.
Current acceptance and field state remain owned by [Work Plan](../00-project/work-plan.md).
This contract is frozen before fresh candidate measurements.

## Product unit and bounded implementation

Judge whether the report conveys consequential Oil/Foam episode direction,
ordering and uncertainty. Do not optimize perfect per-frame recall or erase
rapid real motion. Numerical observations, events, verdicts and truth remain intact.

Provide an offline, manually scrubbable source-frame sequence for the longest
internal Oil-observation gap, the two report extrema, and the longest reported Foam episode. A missing/all-missing
or endpoint-only record additionally needs whole-window context when no internal
gap exists. Merge overlapping extrema requests, retain reasons, order by time, and limit
to four requests per Glass. Keep broad gap/Foam context separate so it cannot
swallow a higher-cadence extrema zoom. Extrema receive two source seconds on each side,
clipped to the analysis interval. This is a review budget, not a detector rule.

Each request uses at most 240 source-frame samples at no faster than native
cadence, independently of detector sampling. Long requests explicitly disclose
subsampling; no interpolation, loop or real-time playback claim. Source crops
include the ellipse bounding rectangle, preserving surrounding optical artifacts.
Keep aspect ratio, downscale only to a 192-pixel maximum dimension, and use
lossless PNG sprite pages of at most 40 tiles. Disclose crop/resize and actual
frame/time for every sample. Native-sized small sight glasses are not downscaled.

No measured Oil/Foam guides are added. Missing/duplicate/mistimed/geometry-changing
frames are unavailable rather than carried; missing source is nonfatal, while
cancellation aborts the transactional result bundle. Use only local relative
assets and embedded JSON; no fetch, CDN, autoplay, service or raw-video copy.
A static preview and metadata remain usable without JavaScript. Jinja HTML
escaping is explicit because the actual template filenames end in `.j2`. Mark extrema as
detector observations needing source comparison, never certified physical extrema.

## Separate detector experiment: side-texture persistence

Inspect existing variance/edge-density owners first. Unlike the closed raw-BGR
shared-plane region model, measure distributions of rotation-invariant local
binary-pattern arrangements, with radii 1 and 2, on the original same-frame raster.
The new measurement is diagnostic-only and never imported into production.

For each original native-path sector (candidate-center geometry only where no
native geometry exists), take paired near/far bands on both sides of its recorded
Y. Use an eroded effective/nonglare mask; never fill absent sectors. Band thickness
is max(4, round(min(image dimensions)*0.06)), capped at 32; leave a two-pixel
boundary exclusion. Each band requires at least 16 valid pixels. Histograms retain
10 uniform-pattern bins per radius and are equally weighted across radii.

The frozen sector margin is the minimum cross-side Jensen-Shannon distance minus
the maximum within-side near/far distance. A positive margin supports persistent
texture change rather than a local narrow return. Candidate support requires at
least three complete sectors with positive margin. No score, source family,
authority tier, selected track, reviewed position, label or time enters inference.
This explicit majority tolerates local occlusion but is not a confidence estimate.

Same-texture steps, narrow ribbons, illumination-only differences and missing
support are synthetic opposition controls. A stationary textured half-plane is
an explicit collision: appearance cannot distinguish its physical origin. This
measurement alone is not sufficient Oil/Foam identity and cannot be promoted
regardless of a favorable local result. Preserve this limitation in W3 output.

Freeze the implementation and operating point after synthetic checks and before
reading new real measurement values. Predict all 153 previously bound candidates,
then use existing W3 exploratory evaluation with original labels/snapshot. Compare
seven confirmed targets, three rejected targets and four protected correct
selections. No tuning on this comparison; failures close this model. Existing
videos remain exposed development/regression, not independent holdout.

## Verification

- Planner: clipping, overlaps, tie order, absent Oil, sparse timestamps and bounds.
- Source renderer: original-pixel equivalence, native cadence, long-window cap,
  missing/duplicate/mistimed source, open failure, cancellation, geometry change.
- Offline browser: file protocol, slider/keyboard navigation, missing-frame blank,
  JS disabled fallback, local assets, no console/network errors, mobile layout.
- Four fresh official application/report windows; compare all 299 stored rows,
  validity, events and numerical fingerprints to the hash-verified exact-src baseline.
- Focused tests, relevant integration/policy tests and exact canonical coverage.
  A timed-out or failed run remains recorded; Windows/Qt stability is separate.

## History Review

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F06`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: existing local variance/edge-density, A2 region-exchange all-abstention, native-patch drift, report context compression and extrema residuals.
- Prior mechanisms rejected: closed-score retuning, motion-only authority, scalar interpolation, whole-track/family privilege and private-Y branches.
- Preserved contracts: same-frame provenance, independent Oil/Foam, frozen inputs, explicit missingness, separate O2/Windows acceptance.
- Difference from prior failures: spatial texture arrangement is separately measured; source-frame review is presentation only and never repairs detector coordinates.
- Logic-map impact: UPDATED — bounded source-frame review is registered under presentation only; detector control flow remains unchanged.
- Failure-registry impact: NONE — known optical/identity ambiguities remain guarded and no new physical cause is claimed.
