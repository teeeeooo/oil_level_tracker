# S11-R10 Calibrated Path and Layer Validation

## Automated source gate

Run focused Artifact UI, calibrated proposal/path, Foam resolver, interactive
graph, static report graph, trace and detector integration tests. Follow with
the reproducible four-video and user-like calibration replays, a debug-disabled
performance comparison and the full repository suite. Require Python compile
and `git diff --check` success.

Intentional numeric deltas must retain same-frame provenance and be reconciled
against checked truth or direct image review. R10 may improve calibration
coverage but must not regress the accepted uncalibrated safety corpus, publish
Base/sample2/sample4 false Foam or fill the reviewed unclear sample3 39–90 s
span with inferred Oil.

## Calibrated proposal/path acceptance

Tests must prove:

- no-template input creates no calibrated candidates or bootstrap;
- saved Artifact matches remain hard-rejected;
- the fixed candidate budget retains both strong and vertically distributed
  weak rows;
- a slow path with sparse registered-motion keyframes and safe continuation
  members can be promoted;
- missing frames are not interpolated;
- static, insufficient-span, insufficient-keyframe and competing paths remain
  unresolved;
- an existing qualified ordinary path disables calibrated bootstrap; and
- every promoted/public Oil row is an exact candidate in that frame.

Final trace must distinguish continuation, motion keyframe, promoted seed,
trajectory selection and first reject stage.

## Foam/Oil and graph acceptance

Tests must prove:

- repeated practically coincident Foam/Oil rows may still be rejected as an
  alias;
- inverted public Oil/Foam topology is rejected even when separation exceeds
  the small same-boundary tolerance;
- a confirmed dynamic Foam front 17 px above selected Oil remains public under
  the representative secure-Windows geometry/settings;
- an unselected coincident proposal cannot erase a separated selected pair;
- unresolved Oil may suppress Foam only through repeated strong,
  low-artifact same-frame proposals and the bounded candidate-only tolerance;
- Oil temporal jump settings cannot widen Foam/Oil identity tolerance;
- Foam publication never changes selected Oil provenance;
- confirmed Foam remains stored when state is `UNKNOWN_REVIEW` and
  whole-sample `is_valid` is false;
- isolated finite Foam samples render visible markers in Result Review and
  static report graphs; and
- gaps remain gaps with no fabricated Foam coordinate.

## Artifact editor acceptance

Render and inspect the dialog at 980×700 and 1200×840, then exercise it at
100%, 125% and 150% Windows scale. At first open:

- video and Artifact panes do not overlap;
- the Artifact purpose, **Detector 후보 찾기** and bulk actions are visible
  without scrolling;
- the dialog exposes resize/maximize affordances;
- the horizontal splitter is draggable and neither child collapses; and
- proposal/template lists remain usable at minimum size.

Single/multiple/list-all selection must highlight the exact overlays. Only
selected proposals may be applied; cancel, Recipe dirty state, ellipse, zero
line and exclusion editing must retain existing semantics.

## Secure-Windows Base/Accum gate

Run the exact pushed R10 head with the same private videos, Recipes, reviewed
Artifact templates, cadence and bounds used for R9.

For Base, reconcile source-frame Oil near 540, 634 and 674 s. Record candidate
distance, calibrated pool retention, motion-keyframe/path membership, first
numeric acquisition, numeric coverage, longest missing run and every reviewed
wrong-interface run. Require zero public Foam. Coverage is not a PASS if a
static/wrong path wins.

For Accum, inspect Oil rise, Foam onset, separated Oil/Foam layers, highest Oil
and later recovery. Record public Oil and Foam independently. Confirmed Foam
must be visible in CSV and graph even when the composed sample is invalid.
Any alias rejection must report effective identity tolerance and the exact Oil
row used; a distinct layered pair must not be rejected through temporal jump
tolerance.

Verify final `sequence` trace against `tracking.csv`, graph, events and captures.
Every numeric Oil requires same-frame provenance and every public Foam requires
a confirmed dynamic episode. Compare debug-disabled detector time with R9 on
the same machine.

Passing local gates does not establish private-field or general-field accuracy.
That claim remains pending until this secure-Windows gate is reconciled.
