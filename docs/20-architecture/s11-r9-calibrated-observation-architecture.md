# S11-R9 Calibrated Observation Architecture

## Purpose

R9 recovers Base-class Oil observations only after explicit operator artifact
calibration, while preserving the already useful Accum/local paths and making
Oil/Foam composition independently auditable. Base and Accum use one detector;
there is no Glass, video, timestamp or filename branch.

## Artifact editing contract

The ellipse editor presents bounded detector point/line/region proposals in a
scrollable panel below a resizable video area. List selection highlights the
matching overlay in magenta. Multi-selection, **모든 후보 선택** and explicit
**선택 후보 일괄 Artifact 지정** are supported.

No proposal changes detection until the operator applies and saves it. Bulk
apply means “apply the reviewed selection,” not “the detector proved every
proposal is an artifact.” Templates remain normalized ellipse geometry and
matching candidates retain `calibrated_artifact:<id>` trace provenance.

## Calibrated high-recall lane

High-recall Sobel proposals exist only when at least one user artifact template
is saved. The generator is bounded to at most twelve rows, excludes flat and
glare-dominated rows, keeps horizontal/distributed support and receives the
same candidate-local registered Oil motion as other proposal families.

These candidates are isolated from the ordinary authority graph:

- they do not consume the ordinary top-k budget;
- they cannot become ordinary semantic seeds;
- they cannot provide cross-representation corroboration;
- they are not path nodes unless the calibrated dynamic bootstrap promotes
  them; and
- a calibrated artifact match remains hard-ineligible.

This prevents calibration from changing a video that already has a qualified
Oil path merely because more weak rows became visible.

## Dynamic bootstrap safety boundary

Bootstrap is a no-qualified-path recovery, not a second resolver. It is disabled
as soon as the existing candidates form any qualified anchor path. Otherwise a
candidate path must:

- contain at least six frames;
- pass ordinary continuation, artifact, ambiguity and track-opposition gates;
- have registered Oil motion and at least 0.60 motion coverage per member;
- remain separated from an eligible Foam front;
- move at least 3.5% of ellipse height (and at least 10 px);
- have at least 0.67 dominant direction consistency; and
- beat any distinct competing path by the bounded competition rule.

Only that one path is promoted to anchor authority. Static rows, two similarly
strong moving paths and already-qualified streams receive no promotion. Final
Oil still selects a same-frame candidate and missing frames remain missing.

## Independent Foam/Oil composition

Oil and Foam may be two vertically separated layers in the same frame. Direct
alias rejection still requires repeated same-frame coincidence with strong Oil.
A previous rejected alias can bridge a short dropout only when the new Foam
episode has at least one new same-frame Oil coincidence. Prior proximity alone
cannot suppress a real Foam episode.

Foam never creates Oil/state authority. Confirmed Foam may be public while Oil
or state is unavailable, with state remaining `UNKNOWN_REVIEW` as applicable.

## Final trace contract

Raw current-frame trace fields and images remain unchanged. Before finalization,
the completed sequence is attached to captured records under `sequence` with:

- final state, positions, confidence and flags;
- initial, post-track and final candidate authority;
- cross-representation and semantic-corridor support;
- track opposition, cluster and trajectory support;
- calibrated seed and Foam-alias evidence; and
- final selection or summarized first reject stage.

This annotation does not rerun detection and does not alter official samples.
It updates byte offsets atomically before writing the debug index.

## Initial state and presentation

A confirmed FULL/EMPTY prior never creates numeric Oil. If no Oil is observed
throughout the window and no direct contradiction exists, report and review
graphs show the confirmed state to the analysis end only as the labeled
`확정 초기 상태 유지 가정` background. CSV, observed coverage, events and
judgment remain based on unmodified observations.

## Performance boundary

Without templates, R9 adds no calibrated raster work. With templates, proposal
count and dynamic paths are bounded; each dynamic-programming node retains at
most four path alternatives. Debug sequence annotation is finalization-time I/O,
not per-frame detector work. Windows acceptance compares debug-disabled detector
time with the same machine and input.

## Prohibited shortcuts

- no automatic acceptance of detector proposals;
- no global Oil/Foam threshold lowering;
- no high-recall corroboration of an existing qualified path;
- no motion-only bootstrap without explicit calibration;
- no stale Foam alias inheritance without current coincidence;
- no carried/interpolated numeric Oil; and
- no initial-state coordinate or hidden graph fabrication.
