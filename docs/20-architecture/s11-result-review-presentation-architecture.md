# S11 Result Review Presentation Architecture

**Status:** current presentation-only contract for the interactive Result Review surface

## Purpose and authority

This document owns the S11-facing boundary between immutable result data and
the interactive Result Review graph. The broader report and result semantics
remain owned by the
[result observation report architecture](result-observation-report-architecture.md).
Detector ownership remains in the
[current detector logic map](s11-current-detector-logic-map.md).

The Result Review surface helps a user find and inspect meaningful moments. It
does not create observations, reinterpret candidates, or promote presentation
state into detector evidence.

## General review hierarchy

General review defaults to a quiet graph:

- Oil and available Foam trajectories are the primary series;
- zero and analysis boundaries remain low-emphasis, unlabeled guides;
- compressor start and major physical events use compact marks without
  persistent text inside the plot;
- review intervals are available through an explicit display toggle and are
  off by default;
- a selected event alone receives a vertical emphasis line; and
- a confirmed initial FULL/EMPTY hold remains a disclosed state band with a
  plain-language note outside the plot, never a numeric Oil coordinate.

Oil, Foam, events, and review intervals are independently controllable outside
the plotting area. These controls change only rendering. They do not mutate the
bundle, query model, event list, or tracking rows.

The navigation list defaults to major physical events. The complete stored
event history remains available through the `모든 이벤트` scope. Filtering
the visible event list and graph marks does not remove or rewrite `events.csv`.

## Detail and debug separation

The general detail panel uses user-facing state and event labels. Observed
state and retrospective interpretation remain separate fields. Raw provenance
may remain available as secondary diagnostic metadata, but it must not replace
the visible user-facing meaning.

General review and detector debug are separate modes. General review does not
show detector candidates or trace-only diagnostic text. Debug mode may consume
stored trace records but remains non-authoritative and cannot alter official
samples, events, graph coordinates, or result judgment.

## Compatibility and preserved authority

- `TrackingSample` values and per-series validity remain the only numeric graph
  authority.
- Graph gap bridges remain presentation-only edges between stored finite Oil
  anchors.
- Retrospective FULL/EMPTY state remains non-numeric.
- Major-event selection is a display default, not a new event taxonomy or
  storage filter.
- No detector threshold, candidate ownership, sequence state, CSV mapping,
  report landmark, or reviewed-truth contract changes.

## History Review

- Logic-map nodes: `RESULT-PRESENTATION`, `OIL-PHASE-INITIAL`
- Failure-registry entries: `S11-F05`, `S11-F09`
- Prior mechanisms reviewed: the current Result Review graph builder and UI,
  confirmed initial-state retrospective hold, report landmark selection, and
  the S11-F05/S11-F09 prohibitions on state-created coordinates and
  presentation-created samples.
- Prior mechanisms rejected: no state-to-coordinate projection, candidate or
  trace promotion, graph interpolation, event rewriting, or UI-derived sample
  is introduced because each would cross the existing publication authority.
- Preserved contracts: immutable stored observations, independent Oil/Foam
  validity, non-numeric retrospective state, complete stored event history,
  presentation-only gap bridges, and unchanged reviewed truth.
- Difference from prior failures: this change reduces persistent UI annotation
  and adds display filters around already stored data; it does not increase
  coverage or manufacture detector evidence.
- Logic-map impact: NONE — `RESULT-PRESENTATION` already owns the interactive
  graph model and UI, and its presentation-only boundary remains unchanged.
- Failure-registry impact: NONE — no detector failure mechanism or causal field
  evidence changes; the existing F05 and F09 guards are retained.
