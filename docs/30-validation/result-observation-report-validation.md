# Result Observation Report Validation Contract

## Scope

This contract owns acceptance for the user-facing observation report defined by the [result observation report architecture](../20-architecture/result-observation-report-architecture.md). Detector effectiveness remains owned by the [S11 detector validation contract](s11-real-field-detector-effectiveness.md).

## Automated acceptance

### Immutable-result boundary

- Report building, graph rendering and capture generation do not mutate any `TrackingSample` numeric/state field.
- Missing/non-finite Oil timestamps never appear as graph vertices, CSV values, overlay positions or extrema.
- A graph bridge contains exactly the finite anchor before and after a missing run.
- Foam graph values remain gap-preserving.
- Retrospective FULL/EMPTY cannot produce an Oil landmark.

### Presentation model

- Finite Oil input produces deterministic highest and lowest observed landmarks; all-missing input produces neither.
- Preferred smoothed/raw and px/mm policies match static and Result Review graph values.
- The trend sentence is deterministic and uses observation-qualified wording when gaps exist.
- Unconfirmed one-sample Foam flicker produces no report episode; a single stored temporal-confirmed strong/moderate Foam publication remains eligible without a second presentation gate.
- A bounded short Foam dropout may remain one episode; a longer absence creates separate episodes.
- Foam disappearance is marked only when a subsequent non-Foam sample exists.
- Landmark selection is deterministic and never exceeds twelve per Glass or three Foam episodes.
- Debug/quality events are not selected into the main report capture gallery.

### Static and interactive graph

- Consecutive observed Oil anchors render as solid segments.
- Oil edges crossing missing samples render as dashed bridges while remaining visually connected.
- Highest/lowest and selected physical landmarks are labeled in the static detail graph.
- Unavailable/review indication remains visible without replacing the Oil line.
- Repeated Result Review cursor updates still do not rebuild series or collapse layout.

### Captures and HTML

- Only selected report landmarks create captures.
- Captures are cropped around the configured Glass, include ellipse/zero and available Oil/Foam guides, and exclude detector-debug content.
- `report.html` embeds capture images with Korean labels, timestamps and plain-language descriptions.
- The main report does not expose a raw confidence/event-debug table, confidence-percentage judgment string or raw metadata dictionary.
- Full CSV and optional debug assets remain present and readable.
- All report links are relative and work without network access.
- Cancellation and any output failure leave no finalized partial bundle.

## Four-video field-corpus acceptance

Replay all established qualification windows at 2 FPS using the matching Recipes and the production `OpenCvPhaseDetector`, static-artifact learning and serialized owner:

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
