# S11 User Report Observability Diagnostic

Date: 2026-08-09

Reviewed head: `e27b2cca93bf261c6d56528f21f5d260cd40b37d`

Status: source defect classified; implementation authority is owned by the current work plan

## Question

Does the accepted detector/result pipeline currently turn the source sight-glass video into a report from which a normal user can understand the Oil-level movement and the important physical moments?

The question is deliberately different from detector-debuggability. Candidate scores, rejection reasons, Spatial sectors and temporal state are needed to improve code, but they are not the primary content of a field-facing observation report.

## Historical reconstruction

| Stage | Accepted responsibility | What remained outside that stage |
| --- | --- | --- |
| MVP | tracking CSV, generic events, static graphs, one capture per event and an HTML table | no report-specific narrative or landmark selection |
| Phase 2B/2C | read-only Result Review, event navigation and a separate developer-debug surface | the static HTML report retained the original generic event-table structure |
| S4 | stable analysis lifecycle, Korean graph labels/fonts, full Glass analysis bounds and cancellable image/report output | event meaning, capture composition and report information hierarchy were unchanged |
| S5-A | bounded Foam/shimmer discrimination and separate Foam temporal ownership | no presentation episode owner to suppress user-facing Foam flicker |
| S5-B/S6 | typed Oil observability, canonical numeric publication, one serialized temporal owner and available-corpus qualification | ambiguity and low coverage became correctly explicit, but the report still presented internal result volume rather than an observation story |
| S11 D1-D5/A-D | positive-evidence preservation, semantic authority slimming, Foam/Oil composition repair and broader usable observed coverage | no new report-selection or narrative responsibility |
| S11 observed-anchor repair | stored finite Oil anchors became one graph-only presentation polyline without numeric interpolation | every gap bridge looked like an ordinary observed segment; generic event lines and the MVP HTML/capture layout remained |

This history shows that the detector and the report solved different problems. S11 improved whether real evidence survives to an official observation. It did not decide which observations a field user needs to see or how source-video evidence should be summarized.

## Reproduced current behavior

The checked-in source and the latest ignored four-video replay bundles were inspected without changing detector state.

### Graph

- Finite Oil anchors are connected, so the graph no longer breaks into isolated points.
- A direct observed span and a bridge across many missing samples use the same solid style.
- `UNKNOWN_REVIEW` hatching can cover most of the plotting area and visually dominate the Oil movement.
- Every domain event becomes an unlabeled vertical line. The graph does not identify the highest Oil, lowest Oil or consolidated Foam episodes.
- The title foregrounds result state and valid-data percentage rather than the observed movement.

### HTML report

- The main Glass section is a raw event table with enum names, confidence decimals and nullable Oil/Foam fields.
- Source metadata is emitted as a raw dictionary.
- Event captures are links only; the report does not show the relevant frame beside a human-readable explanation.
- There is no maximum-Oil landmark or narrative statement of the start/end direction, observed range or long unavailable spans.

### Capture volume and composition

The latest replay bundles produced the following event/capture volume:

| Sample | Event rows | Capture files | Foam event rows |
| --- | ---: | ---: | ---: |
| `base_sample_1` | 13 | 13 | 2 |
| `sample2` | 11 | 11 | 3 |
| `sample3` | 73 | 73 | 37 |
| `sample4` | 60 | 60 | 18 |

Every event, including analysis bookkeeping, low-confidence transitions and repeated Foam flicker, receives a full-frame capture. The capture uses an English enum banner but does not crop around the configured Glass or draw the accepted Oil/Foam/zero lines. This is useful as a raw audit artifact but poor as a report explanation.

Generated bundles under `sample/output/` are forensic support only. The reproducible authority remains current source, the four Recipes/videos and the tracked truth/provisional annotations.

## Root cause

The missing responsibility is a **user-facing observation presentation model** between immutable analysis results and static report adapters.

Today the adapters receive the entire `AnalysisResult` and independently expose nearly everything:

```text
AnalysisResult
  -> capture every EventMarker
  -> draw every event as a line
  -> render every event as a table row
```

There is no owner that answers:

- what overall Oil movement can be stated from observed anchors;
- which extrema and physical transitions are report-worthy;
- which Foam detections belong to one bounded episode;
- which source frames best explain those moments;
- how to expose observation gaps without making the graph unreadable.

## Selected repair

Introduce a read-only report-presentation owner downstream of official observations.

1. Preserve every official `TrackingSample`, detector outcome, CSV value and temporal state.
2. Draw contiguous observed Oil runs as solid and graph-only bridges across missing samples as dashed, using only the two stored anchors at each bridge endpoint.
3. Add maximum and minimum observed-Oil landmarks using the same preferred value policy as the graph.
4. Consolidate accepted Foam observations into bounded presentation episodes, ignoring one-sample flicker and bridging only a short dropout.
5. Select a bounded set of physical landmarks for the report instead of capturing every diagnostic/administrative event.
6. Decode the source frame for each selected landmark, draw the configured Glass/zero/Oil/Foam guides and crop around the Glass.
7. Replace the main raw-event/debug layout with a Korean observation summary, annotated graph, inline landmark captures and a restrained unavailable-interval explanation. Keep full CSV and Result Review/debug assets available outside the report narrative.

## Why detector tuning is not selected

The accepted Slice D reconciliation found no remaining material general hard-safe detector failure class across the current corpus. More importantly, the reproduced report defect exists even when the detector has already produced useful anchors. Report selection and evidence composition can materially improve user understanding without weakening Oil/Foam/no-interface safety or inventing numeric samples.

Detector work may be reopened later only by new current-frame evidence. It is not part of this repair.
