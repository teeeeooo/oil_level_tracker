# Result Observation Report Architecture

## Purpose and authority

This document owns the durable responsibility boundary for turning immutable analysis results and source-video frames into a user-facing Oil observation report. Current sequencing belongs to the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md); acceptance belongs to the [result observation report validation contract](../30-validation/result-observation-report-validation.md).

The report is an explanation of what was observed in the sight glass. It is not a detector-debug dump and it is not a second detector or trajectory estimator.

## Product outcome

A user who opens only `report.html` must be able to determine, for each Glass:

- whether the observed Oil generally rose, fell, held or changed in multiple phases;
- the highest and lowest observed Oil positions and their source-video times;
- when bounded Foam observation episodes began and ended;
- other material landmarks such as compressor start, Oil-drop start and zero crossing when present;
- which graph spans lack direct numeric Oil observation;
- what the source frame looked like at each selected landmark.

## Layer ownership

```text
immutable TrackingSamples + domain EventMarkers + Recipe + Session
                         |
                         v
             report presentation builder
        summary / intervals / bounded landmarks
                 |            |            |
                 v            v            v
          graph renderer   capture store   HTML reporter
```

### Detector and result owners

S5-B/S11 remains the only owner of canonical numeric Oil publication. S5-A and its temporal gate remain the owners of accepted Foam observations. The report must not feed either owner, alter serialized history or write a value into a missing sample.

### Report presentation builder

The application-layer builder is the single owner of report narrative, graph landmarks, bounded Foam presentation episodes and unavailable-interval descriptions. Reporting and storage adapters consume this model; they do not independently select every domain event.

The builder may derive presentation facts only from:

- immutable finite Oil/Foam values already stored on `TrackingSample`;
- stored fill state and timestamps;
- domain events already produced by the analysis pipeline;
- Recipe geometry/unit metadata and Session timing.

It may not inspect detector candidates, debug traces or truth annotations.

## Oil trajectory presentation

The Oil graph uses the existing preferred-value rule: smoothed value first and same-unit raw value only as fallback.

Finite stored Oil anchors remain the only graph vertices. Presentation distinguishes two edge types:

- **direct observed span:** consecutive finite samples, rendered as a solid Oil segment;
- **observation-gap bridge:** the last finite anchor before one or more missing samples joined directly to the next finite anchor, rendered as a dashed, lower-emphasis segment.

A bridge contains only its two existing endpoint anchors. It creates no intermediate value, sample, cursor/overlay position, CSV cell, event evidence or detector-history input. There is no line before the first finite anchor or after the last finite anchor. An all-missing Oil series remains empty.

Unknown/no-interface information remains visible using restrained state or unavailable highlights. It must not visually overwhelm the trajectory. Foam retains gap-preserving rendering because Foam absence is meaningful.

## Extrema and trend summary

The highest and lowest Oil landmarks are selected from the same finite preferred Oil anchors drawn by the graph. Positive height means above the configured zero line; maximum numeric height is the highest observed Oil and minimum numeric height is the lowest observed Oil.

Extrema are observations, not claims about an unobserved interval. Wording must use forms such as “관측된 최고 유면” and “관측된 최저 유면.” If no finite Oil exists, no extrema or movement direction is claimed.

The overall movement sentence compares observed start/end anchors with a bounded scale-aware hold tolerance and reports rise, fall, approximate hold or mixed movement. It must say that the statement is based on observable anchors whenever missing intervals exist.

## Foam presentation episodes

Report Foam episodes are a presentation grouping over accepted stored Foam observations, not a new Foam detector result.

- An unconfirmed one-sample Foam-like observation does not create a report episode.
- A single stored public Foam sample explicitly marked as strong/moderate accepted evidence may create an episode because the detector temporal gate already confirmed its onset; report presentation does not impose the same gate twice.
- Stored temporal-pending flags may connect confirmed public observations and defer disappearance within the bounded dropout tolerance, but cannot start an episode or provide a Foam graph coordinate.
- A short dropout no longer than the bounded presentation tolerance may be bridged inside one episode.
- Longer absence separates episodes.
- The report exposes at most three most material episodes per Glass, ordered by time after selection.
- Episode start uses the first accepted Foam sample.
- Episode time is never backdated to a detector-pending sample hidden before publication.
- Episode end uses the first subsequent non-Foam sample when disappearance is observed. If Foam persists through analysis end, the report does not claim a disappearance time.

The complete ungrouped domain event history remains available in `events.csv` and Result Review. Presentation grouping must not rewrite it.

## Landmark selection

The report uses a bounded set of at most twelve landmarks per Glass. Highest/lowest Oil and retained Foam episode boundaries have priority, followed by compressor start, Oil-drop start, zero crossings/recovery and boundary appearance. Administrative/debug-quality events such as analysis bookkeeping, low-confidence transitions, detection loss and generic review-required rows remain available in result data but are not expanded into the main capture gallery.

Each landmark owns:

- Korean label and plain-language explanation;
- source timestamp and optional interval;
- the nearest official sample used for overlay values;
- optional source domain event provenance;
- generated relative capture path.

## Capture responsibility

For each selected landmark, the capture adapter:

1. seeks the original source video at the landmark timestamp;
2. draws the configured Glass ellipse and zero line;
3. draws stored Oil and Foam positions when present;
4. crops with bounded context around the Glass ellipse;
5. may upscale a very small crop for report legibility without changing or inferring any guide position;
6. adds only a timestamp/visual legend needed to interpret the guide colors;
7. stores the image inside the bundle and exposes it inline in the report.

Candidate lines, scores, rejection reasons, confidence decimals and debug-trace details are forbidden in these user captures. Dedicated debug assets remain separate.

## HTML information hierarchy

The main report order is:

1. run identity and overall judgment;
2. combined movement graph;
3. per-Glass observation summary;
4. annotated detail graph;
5. inline key-moment capture cards;
6. concise unavailable-interval explanation;
7. plain-language judgment guidance and warnings;
8. collapsible technical/settings provenance.

Raw event/debug tables, confidence-percentage judgment strings and raw metadata dictionaries are not main-report content. `tracking_data.csv`, `events.csv`, Result Review and optional debug artifacts remain the detailed engineering/audit surfaces.

## Compatibility and preservation

- Existing Recipe, tracking CSV and review semantics remain unchanged.
- Adding `MAXIMUM_OIL_LEVEL` extends the event vocabulary without changing existing event meanings or columns.
- Missing Oil remains missing in every persisted data surface.
- Retrospective FULL/EMPTY cannot create a report Oil anchor or extrema.
- Report generation remains offline and uses bundle-relative assets only.
- Bundle staging, cancellation, atomic replacement and resource cleanup remain mandatory.
- No source/video/Recipe/truth identity branch is allowed.
