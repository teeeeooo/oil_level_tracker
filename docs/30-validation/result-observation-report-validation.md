# Result Observation Report Validation Contract

## Scope

This contract owns acceptance for the user-facing observation report defined by the [result observation report architecture](../20-architecture/result-observation-report-architecture.md). Detector effectiveness remains owned by the [S11 detector validation contract](s11-real-field-detector-effectiveness.md).

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

- Finite Oil input produces deterministic highest and lowest observed landmarks; all-missing input produces neither.
- Preferred smoothed/raw and px/mm policies match static and Result Review graph values.
- The trend sentence is deterministic and uses observation-qualified wording when gaps exist.
- Unconfirmed one-sample Foam flicker produces no report episode; a single stored temporal-confirmed strong/moderate Foam publication remains eligible without a second presentation gate. Pending flags may connect/defer disappearance within the bounded dropout rule but cannot create or backdate an episode or Foam coordinate.
- A bounded short Foam dropout may remain one episode; a longer absence creates separate episodes.
- Foam disappearance is marked only when a subsequent non-Foam sample exists.
- Landmark selection is deterministic and never exceeds twelve per Glass or three Foam episodes.
- Debug/quality events are not selected into the main report capture gallery.

### Static and interactive graph

- Consecutive observed Oil anchors render as solid segments.
- Oil edges crossing missing samples render as dashed bridges while remaining visually connected.
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

- Only selected report landmarks create captures.
- Captures are cropped around the configured Glass, include ellipse/zero and available Oil/Foam guides, and exclude detector-debug content.
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
3. capture volume is bounded by the landmark contract rather than domain-event count;
4. repeated Foam flicker is represented as bounded episodes, not dozens of equal-weight report cards;
5. graph inspection confirms direct observed runs, dashed missing-run bridges, readable state indication and no line outside observed endpoints;
6. source capture inspection confirms the configured Glass is the visual focus and guide lines align with the saved sample;
7. the report can be understood without opening debug trace or CSV, while those files remain available for engineering verification.

Generated replay bundles and screenshots are evidence artifacts, not golden truth. Review must compare the MP4, matching Recipe, tracked truth/provisional annotations and current source across all four samples; no single video may become a presentation-selection branch.

## Claim boundary

Passing this contract establishes that the available four-video results are communicated more clearly. It does not claim general-field detector accuracy, validate every Foam classification, or authorize numeric trajectory interpolation. Final target-Windows workflow validation remains required after source acceptance.

Offscreen GUI regression establishes widget/state behavior only. It does not
establish text fit or interaction quality at Windows 100%, 125% or 150% display
scaling; those checks remain pending until the manual Windows procedure is run.
