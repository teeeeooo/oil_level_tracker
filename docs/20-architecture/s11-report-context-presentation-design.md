# S11 Report Context Presentation Design

This bounded design implements the reviewed namespace/wording portion of the
[third audit](../70-reference/s11-audit-2026-10-07/s11-third-audit-report-context-work-spec-2026-10-07.md).
The [report architecture](result-observation-report-architecture.md) owns the
durable report contract; its [validation](../30-validation/result-observation-report-validation.md)
owns acceptance. The [Work Plan](../00-project/work-plan.md) owns adoption status.
The supplied prototype and recovery archives remain immutable historical inputs.

## Namespace and observation wording

`report_presentation.py` remains the owner. Exact legacy Oil flags retain the
R7 anchor-only rule; unrelated Foam flags do not suppress modern Oil extrema.
One report-local eligible-set helper serves both landmarks and narrative, so a
continuation-only legacy stream cannot fall back to unrestricted summary extrema.
This does not change domain-event or initial-state compatibility predicates.

Endpoint comparison is explicitly qualified, including intermediate variation
and singleton observations. Foam labels describe observation start/interruption,
give last-observed and next non-Foam timestamps, and do not certify physical
formation/disappearance. Existing state-only Foam evidence remains state evidence;
wording does not manufacture a front coordinate. Episode formation is unchanged.

The first change is limited to namespace/wording. The second bounded unit below
adds static gap display and scene context. Tracking samples, detector source,
Recipe/truth, event meanings, judgment and field disposition are unchanged.

## Static gap display and scene context

The report adopts the prototype's two-source-second Oil connection cap as an
explicit display policy. It applies both to missing-row bridges and timestamp
jumps, preserving all anchors. The shared series helper remains uncapped by
default so Result Review keeps its existing behavior. The report trend sentence
does not infer mixed observed motion from pairs across a longer gap.

The existing presentation builder selects the longest internal gap per Glass,
with earliest tie-breaking, and emits at most three `ReportSceneCapture` requests.
Endpoints use their stored samples; the midpoint has no sample and no Oil/Foam
guides. These are presentation requests, not synthetic events or samples. The
existing capture store, cancellation/progress and staged bundle path serve them.
Scene-only requests have a distinct cache identity from annotated landmarks.
The report template exposes them separately with observation-qualified captions.

This extends the supplied prototype with bounded scene context in the existing
owners. It does not claim the two-second value is calibrated, certify physical
identity or make static/interactive presentation identical. Source/report interval
review remains the next decision-bearing step; current field gates remain intact.

## Supported extremum landmarks — 2026-10-20

This implements the user-adopted
[P0 extremum display rule](../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20).
The rule lives in the existing eligible-set helper, so landmarks and narrative
still share extremum eligibility. After the R7 anchor-only filter, an observation
stays eligible only when another eligible observation lies within 1 s of source
time and within 5% of the Recipe Glass vertical diameter (`2 × radius_y`).

Unsupported points remain in tracking samples, CSV and graph vertices; they only
receive no maximum/minimum landmark or summary sentence. If nothing is supported,
the report names no extremum. Without Glass geometry, no band can be derived and
the previous unfiltered behavior applies. Domain `MAXIMUM/MINIMUM_OIL_LEVEL`
events and the Result Review engineering surface are unchanged. Landmark
selection, source-review windows and graph labels follow the filtered landmarks
through their existing consumers.

A read-only check rebuilt the presentation from the only stored result bundle,
sample4 from 2026-10-11 (`s11-p5-default-linkage-20261011-001/none`), with the
same 101 Oil values. Band: 5.2 px.
- The former maximum at 44 s (+28 px) is one of the known wrong-target report
  extrema. It has no support, and the maximum moves to 52.5 s (+21 px).
- The 42 s minimum (−18 px), the other known wrong target, keeps a supporting
  neighbor. It therefore remains a visible A-class failure check, not one the
  rule hides.

## FULL/EMPTY bands and judgment reason — 2026-10-21

**Status: FROZEN 2026-10-21 before implementation (`67f1484`); IMPLEMENTED;
[local verification](../60-evidence/s11/2026-10-21-initial-state-report-local.md).** The user chose these
changes after the
[⑩ report receipt](../60-evidence/s11/2026-10-21-top-exit-v3-local.md#report-and-judgment-receipt--2026-10-21).
That receipt found two problems:
- the top-exit FULL suffix and any reconstructed prefix are drawn at alpha 0.035
  with no legend;
- the report states only a fixed sentence for `REVIEW_REQUIRED`.

The paired initial-state rule is owned by the
[reconstruction architecture](initial-state-retrospective-reconstruction-architecture.md#modern-stream-continuing-run-rule--2026-10-21).

**A. Detail-graph state bands.**
- **Emphasis:** every FULL or EMPTY interval uses the existing hold emphasis
  (alpha 0.09) and a legend label that names its source:
  - detector state, including top-exit FULL: `FULL 판정` / `EMPTY 판정`;
  - an accepted retrospective prefix: `초기 상태 재구성 (FULL)` /
    `초기 상태 재구성 (EMPTY)`;
  - the all-missing hold: the existing `확정 초기 상태 유지 가정 (…)`.
- **Grouping:** intervals are grouped by state and source. The UNKNOWN band is
  unchanged.
- **No new data:** no Oil line, vertex or value is added.
- **Combined graph:** unchanged and lines only. Bands from several Glass on one
  axis would be ambiguous. (Superseded on 2026-10-22 by the per-Glass strip
  below.)

**C. Judgment guidance.** The `판정 안내` sentence gains a plain-Korean reason.
- **Source:** the reason is mapped from the stored judgment note's known forms:
  - valid-coverage shortfall, with both percentages;
  - no samples, or no compressor start for RECOVERY;
  - recovery found, late or absent;
  - hold maintained, or the excursion/violation duration;
  - retrospective provenance or conflict.
- **Fallback:** an unknown form adds nothing.
- **No raw text:** the raw English note is never shown, which keeps the main
  report free of debug strings.

**Unchanged:** events, judgment, CSV, bundle files and Result Review.

**Expected on ⑩:**
- the BASE graph shows the 674–780 s top-exit FULL as a labelled band;
- with the paired rule, it also shows the 480–548 s prefix as `초기 상태 재구성
  (FULL)`;
- BASE `판정 안내` names the coverage reason or, after the paired rule, the level
  result;
- Accum names its 6.0% coverage shortfall.

## Combined-graph state strip and source patterns — 2026-10-22

**Status: FROZEN 2026-10-22 before implementation (`db83c59`); IMPLEMENTED;
[local verification](../60-evidence/s11/2026-10-21-initial-state-report-local.md#combined-graph-strip-and-band-patterns-e1e2--2026-10-22).**
The user chose E1/E2 from
the graph limits named in the
[top-exit and report handoff](../60-evidence/s11/2026-10-21-top-exit-report-handoff.md#open-choices-after-that-the-user-decides):
- the combined graph has no state bands;
- bands from different sources share one colour, so only the legend tells a
  reconstructed FULL from a detector FULL.

**E2. Source patterns, both graphs.**
- **Colour stays by state:** FULL blue, EMPTY amber; UNKNOWN keeps its grey.
- **Pattern by source:**
  - detector state, including top-exit FULL (`FULL 판정` / `EMPTY 판정`):
    solid, as now;
  - an accepted initial-state reconstruction (`초기 상태 재구성 (…)`):
    diagonal hatching;
  - the all-missing hold (`확정 초기 상태 유지 가정 (…)`): dots.
- **Emphasis:** the detail-graph fill keeps the 2026-10-21 alpha (0.09;
  UNKNOWN 0.065). Hatching and dots use the state colour at a stronger alpha so
  they read at a glance. The legend shows each pattern.

**E1. Combined-graph state strip.**
- **Layout:** a strip under the combined lines shares their time axis. It has
  one row per Glass, in result order, labelled with the Glass name.
- **Content:** each row draws exactly that Glass's detail-graph bands, with the
  same grouping, extents, labels and patterns, UNKNOWN included. The fill is
  stronger than in the detail graph because no line runs over it.
- **Lines stay separate:** the line plot above stays lines only. Each Glass
  gets its own row, which removes the 2026-10-21 objection to bands from
  several Glass on one axis.
- **Fallback:** no strip is drawn when no Glass has a band.

**Unchanged:** samples, events, judgment, CSV, bundle files, the report
template and Result Review. No Oil line, vertex or value is added.

**Confirmation on the next Windows report:** each strip row matches its Glass's
detail-graph bands, and each band's pattern matches its legend entry.

## Per-sample band cells — 2026-10-22

**Status: FROZEN 2026-10-22 before implementation.** The user chose option A
after a rendered comparison of two fixes for the defect seen on Windows
([SPL#4 receipt](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-receipt--2026-10-22)):
- **Defect:** a run spans its first to its last sample, so a one-sample run
  has no width. It is invisible, yet its label enters the legend (Accum
  `EMPTY 판정`, 24.5 s). Runs of different states are also one sample interval
  apart, so the blank where a one-sample run sits has no explanation.
- **Rejected option B:** dropping zero-width runs from the drawing and the
  legend. It would hide a published state and keep the blank.
- **Comparison (scratch):** synthetic SPL#4-like values and an existing local
  sample4 `tracking.csv`. Across the 47 local report bundles, 149 of 260
  UNKNOWN runs are one sample long, so none of them is visible now.

**Rule, both graphs:**
- **Cells:** each sample owns the time from halfway to its previous sample to
  halfway to its next one. A run covers its samples' cells, so a one-sample
  run is one sample interval wide and neighbouring runs meet.
- **Ends:** no band starts before the first sample or ends after the last one.
- **Gaps:** a cell reaches at most 1 s from its sample, half the report's 2 s
  line-connection limit (`REPORT_MAX_CONTEXT_GAP_SEC`). A longer gap stays
  blank and splits the run, as the Oil line already breaks there. Below 0.5
  samples per second, every sample is therefore its own 2 s cell.
- **Single sample:** a Glass with one sample has no cell width and draws no
  band.
- **Limit:** on a long graph one cell can be narrower than a pixel and shows
  only as a faint line.

**Unchanged:** grouping by state and source, labels, colours, patterns,
emphasis, the strip layout and its no-band fallback; samples, events,
judgment, CSV, bundle files, the report template and Result Review. No
threshold is added.

**Confirmation on the next Windows report:** a one-sample run draws a narrow
band in its state colour that matches its legend entry, and runs of different
states meet without a blank.

## History Review

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R1 observed-run/display-bridge distinction; R7 anchor-only extrema; current independent Oil/Foam validity; the three supplied 2026-10-07 audits and report-context prototype.
- Prior mechanisms rejected: Foam flags granting Oil authority, unrestricted fallback from legacy anchor eligibility, numeric interpolation/carry, treating missing Foam as physical disappearance, and promoting local report checks into field success.
- Preserved contracts: immutable stored observations, same-frame provenance, independent series, actual legacy anchor protection, bounded existing episode/landmark selection, unchanged event history and separate field qualification.
- Difference from prior failures: repair report interpretation inside its existing owner without changing upstream identity, numeric publication, detector thresholds or candidate selection; summary and landmarks share extrema eligibility, long display connections are bounded and context-only captures cannot create measurements. The 2026-10-20 support rule selects only which stored value is labeled; it neither removes nor rewrites values.
- Existing feature coverage: reuses the Recipe ellipse `radius_y` already used by the movement-summary tolerance, the R7 anchor eligibility and the existing landmark consumers (graph renderer, source-review window planner, capture store). No Recipe, session or detector setting is added.
- Execution scope: unit tests through `build_glass_report_presentation` cover isolated spikes, window/band edges, no supported point, R7 anchors and missing geometry. No detector run, full report bundle replay or Windows run was exercised; field disposition is unchanged. The 2026-10-21 band/reason section was frozen from the read-only ⑩ receipt before any code change, then implemented with renderer and presentation unit tests and a rendered ⑩-like check; no Windows run. The 2026-10-22 strip/pattern section was frozen before any code change, then implemented with renderer unit tests and rendered SPL#4-like, ⑩-like and no-band checks from synthetic values; no Windows run yet. The 2026-10-22 band-cell section is frozen from a scratch rendered comparison (synthetic SPL#4-like values and an existing local sample4 `tracking.csv`) before any code change; it is not yet implemented.
- Logic-map impact: NONE — the 2026-10-22 band-cell section is frozen but unimplemented; the `RESULT-PRESENTATION` row, which already records the source patterns and the combined-graph strip, changes with its implementation.
- Failure-registry impact: NONE — existing F09/F10 guards apply; no failed detector mechanism is retired or promoted.
