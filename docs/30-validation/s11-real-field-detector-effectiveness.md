# S11 Real-Field Detector Effectiveness Validation Contract

**Status:** `DURABLE CROSS-REVISION UMBRELLA — R12 CLAUSES SUPERSEDED`

This document preserves the durable S11 field-effectiveness oracle, safety
obligations and cross-revision non-regression boundary. It is not the current
implementation or acceptance owner. Current acceptance is owned by the
[R21 truth-preserving detector repair validation](s11-r21-truth-preserving-detector-repair-validation.md),
with the required post-push [current-candidate Windows field procedure](../40-operations/s11-current-windows-field-qualification.md)
and [canonical reviewed truth](windows-sample1-heating-coldstart-reviewed-truth.md).
The active behavior remains local and field-unqualified; the canonical Windows
replay remains required and no Windows PASS is claimed. R12/R18/R19/R20
architecture, head and owner references below are retained as historical or
predecessor context and are superseded as current ownership by the active
behavior contract.

## Scope and oracle

This document owns the durable cross-revision detector-effectiveness boundary
for S11. The current implementation-specific acceptance contract is the [R21
truth-preserving detector repair architecture](../20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md)
and [validation/work specification](s11-r21-truth-preserving-detector-repair-validation.md).
The exact current action remains in the [work plan](../00-project/work-plan.md),
while completed measurements belong in
[`../60-evidence/s11/`](../60-evidence/s11/).

The primary oracle is direct source-frame review inside each configured Glass
ROI. Checked `.oiltruth`, blind provisional annotations and controlled fixtures
support that review. Historical fingerprints, aggregate publication counts and
prior validation outputs cannot override the images.

## Historical R12 ownership baseline (preserved)

The following R12-specific ownership and safety baseline is preserved for
historical comparison. It is not the current implementation contract; current
R21 ownership and acceptance are defined by the linked R21 architecture and
validation contract above.

The historical R12 baseline required:

1. current-frame processing preserves bounded Oil candidates, typed
   no-interface evidence, optics opposition and raw Foam material independently;
2. final Oil/FULL/EMPTY selection was owned only by the R12
   `OilObservationResolver`;
3. every candidate has one explicit final authority tier, and old current-frame
   temporal selection has no final anchor authority;
4. every numeric Oil result selects an anchor- or continuation-eligible candidate
   from that same frame;
5. FULL/EMPTY validity requires affirmative current-raster state evidence;
6. the initial state cannot create observed coverage but may support a separately
   proven leading-prefix retrospective interpretation;
7. `FoamEpisodeResolver` confirms Foam only after Oil/state is fixed and only
   from bounded multi-frame material evolution, including the dynamic-narrow
   shape route;
8. raw, rejected or pending Foam cannot mask, select or veto Oil and cannot be
   resurrected by final sequence processing;
9. `ObservationSequenceResolver` is the single final composition point;
10. no resolver interpolates, carries or invents a coordinate;
11. calibrated high-recall candidates receive bounded admission but cannot
    become an anchor through motion or calibration alone;
12. missing evidence is unavailable rather than conflict-free zero; and
13. Oil and Foam use separate graph-validity bits after composition.

Superseded R5–R11 policy owners, motion-only bootstrap,
`foam_distinct_lower_boundary` authority and historical D5 Foam-to-Oil routing
must remain absent from production call paths.

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
output streams are not preservation obligations when R6/R7 explicitly replaced
them.

## Cross-revision checked-in video obligations

These obligations remain part of the durable field-effectiveness boundary.
The current execution route is the active candidate validation contract plus the
current-candidate Windows field procedure, not an R12-head replay.

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

## Historical R12 secure-Windows holdout (preserved)

The R12-head holdout wording below records the historical R12 gate and result
boundary. It is not the current execution route or an assertion of Windows
PASS; the current post-push gate is R21 as linked above.

The exact committed R12 head was required to be replayed on the private Base/Accum video,
both without calibration and with operator-selected detector artifact proposals,
before S11 closure.

- Base must publish no Foam over the directly reviewed Foam-absent run, keep
  initial FULL as context only, and acquire the real descending/recovering
  interface without following fixed glare or caustics. Candidate recall must be
  measured against corrected source-frame overlays; old bundle coordinates and
  detector candidates mislabeled as truth are not an oracle.
- Accum must retain EMPTY only while same-frame image evidence supports it,
  acquire visible inflow before the former mid-Glass lock-in, retain only the
  bounded turbulent Foam episode, and follow the high/fall trajectory.
- Both Glasses must preserve same-frame numeric provenance and derive lifecycle
  timestamps/captures only from accepted observations.
- Historical R12 final authority and first reject stage were read from the R12
  `sequence` trace annotation, not reverse-calculated from the pre-resolver
  record.
- A distinct Accum Oil/Foam pair must remain independently publishable; stale
  alias history without current same-frame coincidence cannot reject Foam.
- Base's former Y724–873 reflection/bracket path must not gain authority from
  registered motion alone. Accum's former Y190–297 residue path must not gain
  authority from vertical separation or an expired material identity.
- A confirmed Accum Foam point may be graph-valid while Oil/state is unknown;
  broad material-mask bottom overlap is not by itself topology failure.

Any Base false Foam episode, Accum prior lock-in through visible Oil, or long
fixed-optics Oil path is a field failure regardless of aggregate coverage.

## Historical R12 downstream and report boundary

R12 detector samples remain immutable historical records, but their leading
unresolved prefix was
eligible for the separately persisted
[Initial-State Retrospective Reconstruction](../20-architecture/initial-state-retrospective-reconstruction-architecture.md)
when current-run confirmation and anchor-grade direction evidence satisfy its
contract. This interpretation must not change observed coverage or create a
coordinate.

Report code may draw only finite stored Oil anchors. A dashed connection across
a missing run is display-only and must not create an intermediate sample, CSV
value, overlay coordinate, event, extremum or capture guide. Foam gaps remain
gaps. Detailed report acceptance belongs to the
[Result Observation Report Validation Contract](result-observation-report-validation.md).

## Historical and claim boundary

R2–R4 architecture/validation documents preserve causal history and fixture
intent. R5–R11 documents preserve failed designs, local evidence and field
failure records. None is an alternate current acceptance owner.

Passing local tests establishes only checked-in-corpus suitability for the
secure holdout. It does not establish general-field detector accuracy, authorize
numeric trajectory estimation or satisfy the private Windows gate. The historical
local R12 disposition is recorded in the
[R12 evidence](../60-evidence/s11/s11-r12-phase-composition-replacement.md); the
[R6 evidence](../60-evidence/s11/s11-r6-optics-aware-observation.md) remains
historical comparison only. Current R21 local acceptance and its remaining
Windows requirement are recorded in the
[R21 evidence](../60-evidence/s11/s11-r21-truth-preserving-detector-repair.md).
