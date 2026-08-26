# S11-R18 Causal Trace Observability Architecture

**Status:** `COMPLETED — DIAGNOSTIC-ONLY WINDOWS CAUSAL CLOSURE` for the failed R18 baseline

## Purpose

The transferred R18 Windows audit reached the implementation boundary but
could not distinguish several predicates because the completed trace stored
only the lifecycle result. This addendum exposed the already-computed causal
decisions for one bounded same-video rerun, whose closure is frozen in the
[R18 Windows causal closure](../50-diagnostics/s11/s11-r18-windows-causal-closure.md).
It did not alter candidate
generation, authority, tracklets, lifecycle transitions, selection, Foam
publication, Recipe settings, thresholds, or CSV values.

## Ownership

### Oil phase diagnostics

`OilMaterialPhaseLifecycleOwner` remains the sole owner of fill/barrier/drain
decisions. Its release predicates now produce a typed evaluation containing:

- stage, row/tracklet identity, row and entrance Y;
- initial-FULL entrance-relative and policy inputs;
- partial-fill established owner, owner chain, last Y/frame, reversal and jump
  inputs;
- ordered confirmation, compatibility, direction, progress, agreement,
  geometry, material-veto and material-conflict predicate results;
- first failed predicate, qualifying IDs, selected ID, and ambiguity; and
- final allowed-set mode (`unconstrained`, `hard_gate`, or `owner_bounded`).

The lifecycle boolean uses the same predicate evaluation that is serialized.
Projection copies the immutable diagnostic into the `sequence_` state. It
does not recompute or reinterpret a release.

### Foam diagnostics

`CurrentFrameEvidenceOwner` records the four existing eligibility predicates:
coherence, static-artifact clearance, glare clearance, and supported layer
shape. `FoamEpisodeResolver` assigns bounded trace-only track/segment IDs and
records the existing material, coherence, static, dynamic, alias, and
formation predicate results. Directed-front and stable-layer formation expose
their branch inputs and first failure.

The accepted boolean is computed from this same evaluation. Track IDs are
diagnostic labels scoped to the completed sequence; they grant no authority.

### Trace boundary

`JsonlDebugTraceWriter` serializes the new nested dictionaries under:

- `sequence.state.sequence_material_phase_diagnostics`;
- `sequence.state.sequence_foam_episode_diagnostics`; and
- selected/raw Foam candidate eligibility predicate fields.

The diagnostic schema label is `r18-field-causal-observability-v1`. Existing
trace consumers remain compatible because the fields are additive and JSON
safe. The trace remains non-authoritative and cannot change `AnalysisResult`,
CSV, events, graphs, or bundle validity.

## Non-goals

- no R19 behavior repair;
- no initial-state, entrance, progress, material, Foam, or alias threshold
  change;
- no private-video, Glass, timestamp, coordinate, or truth branch;
- no UI or graph change; and
- no claim that the instrumented source is field-qualified; R18 remains
  Windows-field FAIL after the completed causal rerun.

## History Review

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`,
  `OIL-PHASE-DRAIN`, `FOAM-CANDIDATE`, `FOAM-EPISODE`,
  `TRACE-PUBLICATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F05`, `S11-F07`, `S11-F08`,
  `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: R5 missed-edge permanent lock, R16/R17 physical
  owner and provenance diagnostics, R18 initial-FULL barrier, partial-fill
  release and Foam formation, plus the transferred R18 causal closure.
- Prior mechanisms rejected: no softened gate, wider entrance band, global
  threshold, state-fed coordinate, candidate-only publication, or private
  exception is introduced; those repeat F05/F08/F10 failures.
- Preserved contracts: same-frame Oil/Foam provenance, independent validity,
  fail-closed ambiguity, bounded owners, immutable Recipe/output semantics,
  and canonical reviewed truth.
- Difference from prior failures: this was additive observation of the active
  predicates, not another detector mechanism or a coverage repair. The
  completed rerun closes compared-field invariance and names the remaining
  release/Y unknowns without changing R18 behavior.
- Logic-map impact: UPDATED — the current map now records the completed
  diagnostic-only causal surface and frozen R18 result while routing the
  implementation-current map separately from approved R19 design.
- Failure-registry impact: UPDATED — the registry now records completed causal
  evidence, exact Foam gate closure, release unknowns and the approved R19
  design-only successor.
