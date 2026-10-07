# Result Observation Report Validation Contract

## Scope

This contract owns acceptance for the user-facing observation report defined by the [result observation report architecture](../20-architecture/result-observation-report-architecture.md). Current detector effectiveness remains owned by the [R20 delayed drain reacquisition validation contract](s11-r20-delayed-drain-reacquisition-validation.md); the [cross-revision S11 field-effectiveness umbrella](s11-real-field-detector-effectiveness.md) is historical reference for preserved obligations and R12 results.

## Automated acceptance

### Immutable-result boundary

- Report building, graph rendering and capture generation do not mutate any `TrackingSample` numeric/state field.
- Missing/non-finite Oil timestamps never appear as graph vertices, CSV values, overlay positions or extrema.
- A graph bridge contains exactly the finite anchor before and after a missing run.
- Foam graph values remain gap-preserving, and every finite stored Foam value
  renders a visible point even when isolated or whole-sample `is_valid` is
  false.
- Retrospective FULL/EMPTY cannot produce an Oil landmark.

### Presentation model

- Finite modern Oil input produces deterministic highest and lowest observed landmarks even when Foam-only R7 flags coexist; all-missing input produces neither. Actual legacy R7 Oil still requires anchors. A continuation-only legacy stream produces no extrema in either landmarks or narrative.
- Preferred smoothed/raw and px/mm policies match static and Result Review graph values.
- The trend sentence is deterministic and uses observation-qualified wording when gaps exist. Endpoint similarity must not imply steadiness over U-shaped, inverted-U or gradual-return observations; singleton input cannot establish movement.
- Unconfirmed one-sample Foam flicker produces no report episode; a single stored temporal-confirmed strong/moderate Foam publication remains eligible without a second presentation gate. Pending flags may connect/defer disappearance within the bounded dropout rule but cannot create or backdate an episode or Foam coordinate.
- A bounded short Foam dropout may remain one episode; a longer absence creates separate episodes.
- Foam observation interruption is marked only when a subsequent non-Foam sample exists. The report gives last-observed and subsequent non-Foam times without certifying physical disappearance. State-only Foam support must not be described as an observed front coordinate. Event types, timestamps and source-event bindings remain unchanged by this wording repair.
- Landmark selection is deterministic and never exceeds twelve per Glass or three Foam episodes.
- Debug/quality events are not selected into the main report capture gallery.

### Static and interactive graph

- In the static report, consecutive observed Oil anchors at most two source seconds apart render as solid segments; larger timestamp jumps do not connect.
- Static Oil edges crossing missing samples render as dashed bridges only when their endpoints are at most two source seconds apart. Every anchor remains visible; no point is added. Result Review retains its existing unlimited display bridges and unchanged helper default pending a separate cross-surface decision.
- Highest/lowest and selected physical landmarks are labeled in the static detail graph.
- Unavailable/review indication remains visible without replacing the Oil line.
- Static and interactive graphs show isolated finite Foam points without
  connecting across a missing row.
- Repeated Result Review cursor updates still do not rebuild series or collapse layout.
- Interactive Result Review has no persistent in-plot legend or per-event text;
  Oil, Foam, event and review-interval visibility are controlled outside the
  plot, with review intervals off by default.
- Major physical events are the default graph/list scope, the complete stored
  event history remains selectable, and only the selected event receives a
  vertical emphasis line.
- Confirmed initial-state hold text is user-facing and outside the plot; its
  restrained band still creates no numeric Oil point.

### Result Review interaction hierarchy

- General mode and Debug mode expose separate navigation tabs; candidate/trace
  rows do not appear in the general navigation or detail panel.
- General detail preserves observed and retrospective state as separate fields,
  combines px/optional mm positions, and keeps raw enum, flag, confidence and
  provenance text out of the persistent body.
- Debug detail defaults to `판정 요약`; `후보 비교` contains only five primary
  columns plus the selected score breakdown, and raw trace dictionaries are
  collapsed by default.
- Shared transport regression covers previous/next frame, ±5/±10 seconds,
  direct-time input, immediate empty-slider click seek, bounded drag updates and
  the final release position.

### Captures and HTML

- Selected report landmarks and up to three scene-context requests for one longest internal Oil gap per Glass create captures. Equal longest gaps choose the earliest; no eligible gap creates no scene requests.
- Captures are cropped around the configured Glass, include ellipse/zero and available Oil/Foam guides, and exclude detector-debug content.
- Long-gap endpoint captures use exact stored samples. The midpoint is source-scene-only, with no Oil/Foam guides or synthetic sample/event. Annotated landmark images must not be reused for scene-only requests at the same time. Source decoding time remains visible on the image.
- `report.html` embeds capture images with Korean labels, timestamps and plain-language descriptions.
- The main report does not expose a raw confidence/event-debug table, confidence-percentage judgment string or raw metadata dictionary.
- Full CSV and optional debug assets remain present and readable.
- All report links are relative and work without network access.
- Cancellation and any output failure leave no finalized partial bundle.

## Four-video field-corpus acceptance

Replay all established qualification windows at 2 FPS using the matching
Recipes and the production `OpenCvPhaseDetector`, static-artifact preparation,
current-frame evidence acquisition and the R7 `ObservationSequenceResolver`:

| Sample | Window |
| --- | --- |
| `base_sample_1` | `0.0–14.4 s` |
| `sample2` | `0.0–2.0 s` |
| `sample3` | `30.03–105.0 s` |
| `sample4` | `0.0–56.0 s` |

Acceptance requires:

1. tracking row identities, accepted numeric Oil counts and fingerprints match the current accepted detector evidence, with every intentional detector delta explicitly reconciled;
2. every Glass with finite Oil has visible highest/lowest graph markers and corresponding inline source captures;
3. capture volume is bounded by twelve landmarks plus three longest-gap scene requests per Glass rather than domain-event count;
4. repeated Foam flicker is represented as bounded episodes, not dozens of equal-weight report cards;
5. graph inspection confirms the static two-second bound for solid/dashed spans, readable state indication, preserved anchors and no line outside observed endpoints;
6. source capture inspection confirms the configured Glass is the visual focus and guide lines align with the saved sample;
7. the report can be understood without opening debug trace or CSV, while those files remain available for engineering verification.

Generated replay bundles and screenshots are evidence artifacts, not golden truth. Review must compare the MP4, matching Recipe, tracked truth/provisional annotations and current source across all four samples; no single video may become a presentation-selection branch.

## Claim boundary

Passing this contract establishes that the available four-video results are communicated more clearly. It does not claim general-field detector accuracy, validate every Foam classification, or authorize numeric trajectory interpolation. Final target-Windows workflow validation remains required after source acceptance.

Offscreen GUI regression establishes widget/state behavior only. It does not
establish text fit or interaction quality at Windows 100%, 125% or 150% display
scaling; those checks remain pending until the manual Windows procedure is run.
