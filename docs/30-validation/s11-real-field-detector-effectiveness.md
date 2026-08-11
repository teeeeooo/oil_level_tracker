# S11 Real-Field Detector Effectiveness Validation Contract

**Status:** `ACTIVE R6 CONTRACT`

## Scope and oracle

This document owns the durable detector-effectiveness acceptance boundary for
S11. The active production design is R6, defined by the
[durable detector architecture](../20-architecture/s11-detector-responsibility-architecture.md)
and the dedicated
[R6 architecture](../20-architecture/s11-r6-optics-aware-observation-architecture.md).
The exact current action remains in the [work plan](../00-project/work-plan.md),
while completed measurements belong in
[`../60-evidence/s11/`](../60-evidence/s11/).

The primary oracle is direct source-frame review inside each configured Glass
ROI. Checked `.oiltruth`, blind provisional annotations and controlled fixtures
support that review. Historical fingerprints, aggregate publication counts and
prior validation outputs cannot override the images.

## Required production ownership

Validation must prove the following current responsibilities:

1. current-frame processing preserves bounded Oil candidates, typed
   no-interface evidence, optics opposition and raw Foam material independently;
2. final Oil/FULL/EMPTY selection is owned only by `OilObservationResolver`;
3. every numeric Oil result selects an eligible candidate from that same frame;
4. FULL/EMPTY validity requires affirmative current-raster state evidence;
5. the initial state is context/initial distribution only and cannot create
   valid coverage;
6. `FoamEpisodeResolver` confirms Foam only after Oil/state is fixed;
7. raw, rejected or pending Foam cannot mask, select or veto Oil and cannot be
   resurrected by final sequence processing;
8. `ObservationSequenceResolver` is the single final composition point; and
9. no resolver interpolates, carries or invents a coordinate.

Superseded R5 owners and historical D5 Foam-to-Oil routing must remain absent
from production call paths.

## Effectiveness priorities

Acceptance prioritizes physical meaning in this order:

1. no long wrong-interface run on glass structure, glare, caustic reflection,
   encoded overlay or another fixed artifact;
2. no published Foam episode on a directly reviewed Foam-absent interval;
3. timely observation of visible entry, rise, fall, hold, minimum and recovery;
4. graph-gap length and distribution over visually supportable intervals;
5. localization error of accepted observations; and
6. aggregate numeric observation density as supporting evidence only.

A higher coverage number fails when it is produced by prior lock-in, fixed-optics
tracking, false Foam, truth/Recipe identity, interpolation or unsupported state.
An unclear frame may remain `UNKNOWN_REVIEW`.

## Controlled preservation surface

Focused and repository regression tests must preserve all of the following
physical classes:

- hard unavailable, low-exposure and positive no-interface evidence;
- saturated glare and unsaturated vertical caustic/ridge optics;
- exclusion, border-cap, rim, structure and encoded-overlay conflicts;
- static textured reflection and pixel-identical latent-cause collision pairs;
- global exposure changes and subpixel component-mask jitter;
- one droplet, fragmented/non-layer Foam-like material and coherent dynamic Foam;
- strong stationary Oil, moving low-contrast material interfaces and Oil with
  partial glare;
- same-frame candidate provenance, initial-prior release and image-supported
  FULL/EMPTY validity; and
- resolver identity/cardinality and deterministic bounded-resource behavior.

The valid negative and non-regression classes discovered in Slices A–D and
R2–R4 remain preservation obligations. Their historical owner topology and exact
output streams are not preservation obligations when R6 explicitly replaced
them.

## Checked-in video gate

Replay all established qualification windows using each matching MP4, Recipe,
truth/provisional annotation, static-artifact preparation, production detector,
completed-window observation resolver and report path.

For every video, record and directly reconcile:

- visually supportable Oil observations and checked truth error;
- longest missing and gross-wrong-interface runs;
- Foam frames/episodes against annotated present and absent intervals;
- acquisition latency after a visibly entering interface;
- image-supported versus prior-only state duration;
- same-frame provenance for every numeric coordinate; and
- event, extremum and capture agreement with the accepted observation stream.

The complete repository-local corpus is one validation surface. No sample,
timestamp, Recipe, truth row or expected output fingerprint may become a
production branch or single-video tuning target.

Sample3 `30–60 s` must communicate EMPTY/inflow/Foam/full without turning a fixed
row into the trajectory. Retained sample2 stationary Oil and genuine
sample3/sample4 Foam are mandatory non-regressions. Visually unclear or
overlay-dominated spans may remain unavailable.

## Secure-Windows holdout

The exact committed R6 head must be replayed on the private Base/Accum video
before S11 closure.

- Base must publish no Foam over the directly reviewed Foam-absent run, keep
  initial FULL as context only, and acquire the real descending/recovering
  interface without following fixed glare or caustics.
- Accum must retain EMPTY only while same-frame image evidence supports it,
  acquire visible inflow before the former mid-Glass lock-in, retain only the
  bounded turbulent Foam episode, and follow the high/fall trajectory.
- Both Glasses must preserve same-frame numeric provenance and derive lifecycle
  timestamps/captures only from accepted observations.

Any Base false Foam episode, Accum prior lock-in through visible Oil, or long
fixed-optics Oil path is a field failure regardless of aggregate coverage.

## Downstream and report boundary

R6 streams are not eligible for a second retrospective state projection. The
legacy [Initial-State Retrospective Reconstruction](../20-architecture/initial-state-retrospective-reconstruction-architecture.md)
must leave R6 observations unchanged.

Report code may draw only finite stored Oil anchors. A dashed connection across
a missing run is display-only and must not create an intermediate sample, CSV
value, overlay coordinate, event, extremum or capture guide. Foam gaps remain
gaps. Detailed report acceptance belongs to the
[Result Observation Report Validation Contract](result-observation-report-validation.md).

## Historical and claim boundary

R2–R4 architecture/validation documents preserve causal history and fixture
intent. R5 documents preserve a failed design and field-failure record. None is
an alternate current acceptance owner.

Passing local tests establishes only checked-in-corpus suitability for the
secure holdout. It does not establish general-field detector accuracy, authorize
numeric trajectory estimation or satisfy the private Windows gate. The current
local evidence is recorded in the
[R6 evidence record](../60-evidence/s11/s11-r6-optics-aware-observation.md).
