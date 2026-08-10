# S11-R3 Sequence Observability Integrity Architecture

**Status:** `VALIDATING`

The source-tree and available-corpus implementation is accepted in the [R3 evidence record](../60-evidence/s11/s11-r3-sequence-observability-integrity.md). Secure-Windows Base/Accum validation remains outside this document's authority and is routed by the [current work plan](../00-project/work-plan.md).

## Purpose

This document owns the bounded S11-R3 repair for three demonstrated ways in which a technically valid detector trace can misdescribe what a user sees in the sight glass:

1. a fixed Glass appearance can repeatedly acquire Foam publication authority;
2. a wide bounding box containing fragmented material rows can be mislabeled as a coherent Foam layer; and
3. after a Glass becomes full, an upper cap/refraction transition can acquire Spatial Oil authority and create a false numeric plateau or apparent drain in the report graph.

The objective is not a target publication percentage. It is to keep the stored observation stream faithful enough that the report communicates inflow, Foam and later absence of an identifiable interface without drawing a confident line on Glass structure.

This is a corpus-wide responsibility repair. Source video names, frame numbers, Recipe identities, truth values and private Windows timestamps are prohibited production inputs.

## Evidence that reopened the source gate

The private Windows field review is non-exportable diagnostic evidence. It reports nearly constant high Foam scores on a Base Glass with no visual Foam, frequent Foam events on an empty Accum Glass, and resulting fill-state collapse. A stable score alone cannot prove the cause, but its small time variation identifies a missing fixed-appearance opposition rather than a reason to raise the global Foam threshold.

The repository-local `sample3` sequence provides the reproducible companion failure. Blind visual annotations describe:

- visible inflow and an Oil/Foam interface near `30–35 s`;
- Foam/agitation as the level reaches the top; and
- `full_like` / no identifiable Oil-air interface from approximately `36.7–60 s`.

Exact production replay instead publishes a cluster of Oil positions near source Y `213–246` after `42 s`. Direct evidence inspection shows that most of those positions are created by the relative-contrast Spatial fallback. Its sector path follows the dark upper Glass cap into the brighter filled interior. The path is locally coherent, but it does not identify an Oil-air interface.

The later drain interval exposes the companion Foam failure: blind annotations mark Foam absent, while fragmented warm material support produces two additional Foam episodes. Its accepted bounding box is broad enough for the component classifier, but only about `0.13–0.48` of component rows contain a materially wide span. The true inflow Foam has a wide-row fraction of at least about `0.54`; the genuine narrow sample2 layer instead has compactness `1.0`.

The prior four-video fingerprint gate did not expose these errors because it compared output identity and aggregate numeric count, not the physical meaning of a complete state transition. Some existing regression expectations therefore preserve a demonstrated wrong-interface stream and are not acceptance authority for R3.

## External design review

Prior S11 research remains applicable:

- Eppel and Kachman evaluate relative intensity change, edge-density change and gradient direction around a candidate curve rather than accepting a strongest row.
- Eppel's later path/graph work constrains a material boundary across the vessel, but the assumption that a path exists does not make every vessel-contour path a material interface.
- Bobovnik et al. use multiple vertical measurement lines to reject local bubble and droplet outliers.
- Musić et al. show that controlled illumination and image differencing materially improve transparent-container level observation; without that optical control, refraction and Glass appearance remain competing causes.
- IVC's commercial sight-glass video-analytics material advertises multiple algorithms and confidence-bearing readings. It supports exposing uncertainty and application-specific configuration, but publishes no mechanism that can be imported as detector authority.

R3 therefore extends the existing evidence graph instead of adding a new dependency, ML model, Hough tuning or global threshold shift.

## Repair A — dark border-cap structural invalidity

### Failure model

The existing Spatial route proves that a same-polarity path appears across horizontal sectors. Near a Glass border, a saturated dark cap or occlusion can satisfy that proof because the brighter filled interior occupies nearly all remaining effective area. Once the upper candidate is removed, the ordinary D3 comparative route can similarly transfer authority to a weak lower rim candidate.

The candidate is structurally non-identifiable when all of the following current-frame facts hold on the glare-excluded effective raster:

- for an upper cap, pixels above the candidate occupy at most `0.12` of effective visible area, their robust median is at most `0.15` of gray scale, and the lower median is at least `0.15` brighter;
- for a lower cap, pixels below the candidate occupy at most `0.04` of effective visible area, their robust median is at most `0.20` of gray scale, and the upper median is at least `0.15` brighter; or
- outside authoritative Foam context, a subcanonical D3 comparative candidate lacks lower-phase material area when the region below it owns less than `0.18` of effective area.

The constants describe conjunctive topology/photometry classes, not a preferred Oil polarity. The tighter lower-cap area bound preserves the retained real near-bottom sample2 interface. A central bright-reversal boundary, a non-saturated border phase or a candidate with material support on both sides is outside the cap class. Strong canonical/D2/Spatial evidence and accepted-Foam topology keep their existing routes; the `0.18` lower-phase rule limits only weak D3 comparison. It is intentionally asymmetric because a blanket two-sided phase-area floor removes a retained true sample3 filling boundary near the upper edge; saturated upper-cap conflict is already handled by the conjunctive photometric guard.

### Authority rule

A dark border-cap hypothesis is hard structural/border conflict:

1. it cannot become the canonical boundary;
2. it cannot enter D2/D3 comparative recovery;
3. it cannot be the semantic anchor or local-tie owner;
4. it cannot receive Spatial fallback authority; and
5. it cannot reduce no-interface likelihood merely by remaining the strongest competing hypothesis.

The raw observation and hypothesis remain available for debug provenance. The repair removes authority, not evidence.

Rejecting this candidate does not itself prove `FULL_NO_INTERFACE`. If the remaining current-frame evidence is insufficient, ambiguity remains the correct result. R3 must not turn the private field initial state or a prior rising line into detector truth.

## Repair B — learned static-Foam opposition

### Failure model

S5-A strong evidence currently bypasses the moderate-evidence persistence chain. A fixed residue, diffuse opacity or reflection that repeatedly satisfies the same component rules can therefore publish Foam on every sampled frame and obtain fill-state and Oil-context authority.

### Learned prior

The existing analysis preparation already decodes bounded start/middle/end representative frames and learns one static horizontal-artifact map per Glass. R3 uses the same frames and lifecycle to build a second bounded map:

1. run the unchanged current-frame S5-A classifier on each representative frame;
2. retain only candidate-bearing strong or moderate current-frame S5-A masks; weak, ambiguous and glare-rejected masks remain empty;
3. mark a pixel static only when accepted support persists at the existing `0.75` learning fraction; with three preparation frames this requires support in all three; and
4. store one crop-sized `uint8` map per Glass, cleared by the existing reset boundary.

No ordinary weak/ambiguous score becomes static proof. A short real Foam episode present in only one representative frame therefore does not poison the prior.

### Publication rule

For a current accepted Foam component, calculate the fraction of its support overlapped by the learned static-Foam map. At overlap `>= 0.80`, the component keeps its current-frame score and debug mask but receives a `static_rejected` temporal/publication outcome:

- no public Foam candidate is emitted;
- no Foam tracker update occurs;
- no Foam-derived fill state occurs; and
- no S5-A to S5-B Foam context authority is granted.

This is fail-closed when a real Foam layer is visually indistinguishable from fixed appearance in all representative frames. It does not claim to detect every intermittent fixed-pattern false positive, and it does not replace later Windows evidence.

## Repair C — row-coherent Foam publication proof

### Failure model

Foam component width is a bounding-box property. A wandering or refractive warm pattern can therefore span much of the Glass over its total height even when each occupied row contains only a small fragment. Current-frame score and bottom connectivity alone do not prove a layer that a user would identify as Foam.

For every raw accepted Foam component, R3 reuses the existing row-topology census and requires either:

- materially wide support on at least `0.50` of component rows; or
- a narrow component with width ratio at most `0.50` whose materially spanning rows have median compactness at least `0.95`.

The second branch preserves genuine partial/narrow Foam instead of imposing a universal full-width rule. A raw accepted component that satisfies neither branch receives `incoherent_rejected`: score, mask and component diagnostics remain available, but no public Foam candidate, tracker update, fill-state authority or Oil-context authority is emitted.

This is a topology proof, not a new Foam score. The existing wide/hollow structural check remains independent defense in depth, and actual optical texture is not inferred from sample identity or trajectory truth.

## Ownership and resource boundaries

- S5-A remains the current-frame Foam classifier.
- The existing Foam temporal/publication gate owns learned-static and row-coherence opposition outcomes; it gains one scalar overlap and one current-frame boolean input and retains no raster history.
- `OpenCvPhaseDetector` owns the already-established per-Glass learned raster lifecycle.
- S5-B remains the only current-frame Oil semantic owner, and its serialized reducer remains the only online Oil temporal owner.
- No public schema, Recipe field, truth input, result interpolation or report-derived feedback is added.
- Work remains bounded by three preparation frames, one extra Foam classification per preparation frame, one `uint8` map per configured Glass and one current-component row census already bounded by the crop.

## Sequence and report consequence

Removing a wrong full-state Oil anchor may reduce numeric coverage and make a report bridge longer. That is an intended improvement when the removed point represents Glass structure. The report may connect surviving finite observations only through its existing dashed display-only bridge and must continue to show the underlying unavailable/review state. It may not replace the removed point with interpolation.

## Non-goals

R3 does not authorize:

- global Foam-score, whiteness, Hough, Canny, confidence or ambiguity retuning;
- forcing `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE` from trajectory direction alone;
- correcting a private-video coordinate offset without a source-coordinate reproduction;
- a new optical-flow, graph-cut, ML or GPU runtime;
- weakening accepted glare, exclusion, authoritative-Foam topology or observational-equivalence protection; or
- declaring the private Windows defect closed from repository-local results.

## Stop boundary

Narrow or revert a mechanism if it removes a retained truth-near material interface, converts a controlled glare/structure collision to numeric Oil, suppresses repository-local genuine Foam, requires sample identity, or improves only aggregate count while leaving sequence meaning worse.
