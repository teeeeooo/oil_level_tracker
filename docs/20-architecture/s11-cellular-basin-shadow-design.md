# S11 cellular-basin candidate readout

Status: experimental contract, frozen separately before each trial, 2026-10-08.
The [completed trial evidence](../60-evidence/s11/2026-10-08-cellular-selector-closeout.md)
records rejection without production promotion; current status belongs to the Work Plan.
Base: `c4814bdc25c4da22776d985fbb7a2d66fbc4e1e8`; main remains `49c6d3a`.

## Windows-first question and bounded scope

Windows reviewed ENTRY-SPLASH must not become Foam, FOAM-LAYERED needs separate
Oil/Foam identities, and POST-FOAM/DRAIN must not transfer to residue. The W3
Windows audit establishes that aggregate material strength and row admission
cannot decide identity. Private Windows pixels are unavailable in this checkout.
This experiment addresses bubbly/non-bubbly spatial arrangement, not the distinct
BASE clear oil-air release problem. No Windows improvement is inferred locally.

The already reviewed A/B interpretation in sample4 supplies the physical model:
bubbly fluid above the Oil boundary, less-bubbly liquid below. Rather than another
near/far histogram or uniform-intensity plane, measure two-dimensional cellular
texture and its distribution over the whole available regions. A structure tensor
uses both gradient directions; its smaller eigenvalue measures local multi-direction
variation. This is an observable, not a chemical/material certificate. Crossed
reflections and printed cellular patterns can collide and remain explicit limits.

## Frozen measurement and operating point

Raw uint8 BGR, original effective AND nonglare mask; no recipe changes. Grayscale
is OpenCV BGR2GRAY, then Gaussian sigma 1. Sobel 3x3 gradients scaled by 1/8;
tensor products are Gaussian pooled at sigma=max(1,min(H,W)/40). Cellular energy
is sqrt(max(0, smaller tensor eigenvalue)); no supervised fitting or sign tuning.
All Gaussian operations use normalized valid-pixel weights. Gradient support
requires a valid 3x3 neighbourhood; pooled tensor validity requires at least 0.5
of the Gaussian weight. Invalid pixels are unavailable, not clean liquid.
For each recorded native sector (candidate-centre sectors only when no native
geometry exists), use all valid pixels above/below its current Y, excluding the
central +/-2 px band. Each side needs 16 pixels and at least four occupied rows.
The signed rank-biserial contrast is 2*P(upper energy > lower energy)-1, with ties
worth one half. Candidate score is the median of at least three distinct available
sectors. A unique maximum score >0 is the frozen exploratory selection; tied
maxima or no positive score abstain. Original candidate Y is never relocated.
Missing sectors, both side distributions and all scores are retained.

Primary regression endpoint: four existing confirmed selections preserved, three
wrong selections not perpetuated, and confirmed alternatives recovered. Report
all seven, not just favourable pairs; partial gain is admissible but not field
acceptance. Reuse immutable W3 target roles and uncertainty. Crossed lines,
stationary cellular patterns, a cellular band with an internal gap, uniform fields,
illumination changes and translated/rescaled scenes are controls. Optical-cellular
collisions must be disclosed and prevent automatic production authority.

The primary method is frozen before measuring real candidates. No radius, sign,
aggregation or threshold sweep is authorized as a reinterpretation of this run.
If rejected, preserve output and close this readout; no report interpolation or
FULL/EMPTY barrier relaxation follows. A successful ranking still requires an
independent identity mechanism before changing production phase admission.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: Windows W3 target/context audit; R20 field consolidation; rejected joint temporal region exchange, side-LBP persistence, LabPics fixed ranking; local Foam gap/structure reviews.
- Prior mechanisms rejected: magnitude-only material identity, local texture histogram alone, motion-only owner promotion, whole-track/family privilege, terminal-barrier relaxation, and new scalar truth inferred from candidate proximity.
- Preserved contracts: no production consumers, unchanged source/recipe/truth, bounded masks/resources, distinct missing evidence, independent Oil/Foam owners and exact original candidate coordinates.
- Difference from prior failures: whole-region ordering of two-dimensional cellular energy is tested against the explicit less-bubbly lower-basin hypothesis, not near/far LBP persistence, raw BGR uniform-plane fitting, pretrained class magnitude or phase-cap removal. Optical/cellular collisions remain a required negative interpretation, not suppressed failures.
- Logic-map impact: NONE — offline experimental candidate measurements add no executing detector owner or production feature.
- Failure-registry impact: NONE — test existing material-identity and structure-confusion risks without asserting a new field cause or repair.

## First readout rejected; extent-supported revision frozen

The first fixed rank-biserial maximum selects a lower near-rim candidate in five
of seven frames; the other two are close to the reviewed target coordinates but
are different unreviewed members. Exact target membership is 0/7. Do not call this
successful or change its saved measurements. A strong distributional difference
across a tiny lower strip does not establish a substantial lower material basin.

A separate revision tests an analytically defined support correction, not a radius
or operating-threshold search: multiply each sector's signed rank-biserial effect
by `2*sqrt(p*(1-p))`, where p is the fraction of valid compared pixels above the
cut. This is proportional to the standardized two-sample rank statistic at fixed
observed area. It tends to zero for a vanishing region and is unchanged at equal
support. It asks how much of the observed spatial field the partition explains,
not whether one tiny tail differs from everything else. All rasters, geometry,
validity, median aggregation and tie/abstention rules remain frozen and identical.

This revision is separately identified, preserves the failed primary trial, and
must be tested against analytic unbalanced-strip and two-region controls before
real evaluation. It may improve candidate ranking; it cannot turn statistical
significance or a cellular optical pattern into physical material identity. It
cannot bypass initial FULL/EMPTY, create Oil-air evidence, or suppress real Foam.
Report exact member outcomes AND coordinate differences from reviewed candidates;
neighbouring unreviewed members are neither declared correct nor automatically
wrong. Coordinate differences are not calibrated physical localization errors.

## Co-located boundary revision — separately frozen

Extent-supported trial selects exact reviewed members at 38/40/52 s, but the
42.5 s choice moves from reviewed-candidate Y835 to Y844. It therefore fails the
movement-context test: a better aggregate region partition can blur a rapid local
excursion. Do not mistake its 3/7 exact members or smaller coordinate deviations
for acceptance. No spatial support weight or tensor radius is retuned.

Test a new, explicitly co-located observable: the current vertical image gradient
at the existing candidate's recorded sector geometry. Use the same masked sigma-1
grayscale and Sobel gradients as the tensor. Bilinearly sample gy at current Y-1,
Y and Y+1 for each original X column; require both interpolation rows valid and at
least 16 total valid samples. Mean absolute gy is normalized by the frame's RMS
2-D gradient over valid pixels (zero when RMS <=1e-6). Multiply it into that same
sector's extent-supported signed cellular contrast, then take the unchanged median
over >=3 sectors. This is a conjunction of region arrangement AND current boundary
localization; no fitted blend coefficients, target coordinates, temporal smoothing,
new sampled coordinates or authority bypass. Strong isolated rims lack the lower
basin, and region-only cuts without current edge support cannot rank strongly.

Its endpoint is seven-case movement context as well as exact member accounting:
retain the reviewed direction change around 42.5–44 s; disclose all unreviewed
alternative selections; do not redefine scalar truth. Follow with dense source
video inspection and the other local recordings' negative controls. A printed
cellular half-plane with a real image edge still collides; no physical identity
certificate or automatic production promotion is claimed from this conjunction.

## Bounded selector-only intervention, frozen before replay

The full-video readout confirms a useful sample4 40–44 s coordinate trajectory,
but broad sample2/s3 mistakes prohibit replacing the detector with its global
maximum. A causal intervention tests the smaller question: can the existing
admitted/publishable representation exploit this ranking without changing any
material, initial-state, tracklet, phase, confidence or publication guard?

For each already constructed publishable selector layer, consider only Oil nodes
whose exact current candidate has a finite cellular-boundary score. With >=2 and
no tied scores, permute their EXISTING emission multiset so the largest original
emission goes to the largest cellular score. Do not add score magnitude, create
nodes, replace representative members, change the physical-phase layer or alter
state/unknown emissions. Other nodes stay identical. A tied ranking skips the
entire permutation. The existing bounded selector and allowed-owner constraints
then execute unchanged. Frozen initial state is explicit UNKNOWN for local samples.

This is a counterfactual diagnostic, not an accepted feature. It cannot recover
a candidate removed before retained refs or opposed before tracklet admission.
If raw proposed motion disappears before this seam, report that first recorded
boundary rather than claiming selector tuning solves identity. Same-frame source
coordinates, immutable raw detections and identical lifecycle witnesses must be
verified for all four recordings. Any changed Foam result is disclosed separately,
because the production Foam resolver consumes the resulting Oil alias relation.

The diagnostic entry point is
`tests/diagnostics/s11_cellular_selector_permutation.py`. It reuses the existing
saved-detection restoration and the real completed-window resolver. Its scoped
patch changes only the second layer returned by `build_interface_layers`; the
physical-phase layer and all allowed-owner decisions are compared exactly across
fresh baseline and intervention runs. Missing/nonfinite scores and tied rankings
cannot create candidates. Strict frame/time/Glass, candidate-offset, source and
Y joins bind measurements. Output is a new directory, never an overwritten run.
The process must run alone; the diagnostic patch is not an application extension.

The final result is not a revised operating point. Preserve the failed region
trials and the four paired selector runs, including changed state/Oil output on
other recordings and unchanged Foam. A new hypothesis requires its own design;
neither score rescaling nor admission/barrier relaxation follows from this trial.
