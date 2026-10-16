# Optional top-exit FULL closure — local preparation

**Status:** local implementation/contract checks complete; actual physical closure
NOT QUALIFIED. Windows geometry preflight is required before a whole-video run.
Current authority remains the [Work Plan](../../00-project/work-plan.md), with
O2 OPEN / FIELD FAIL and the accepted default unchanged.

## Scope and implementation

The user selected ④ FULL+ON v2 closure first, followed by the 721 s non-interface
investigation. The previous cost-first, RGB and two-Glass Local XY trials remain
REGRESSION / NOT_ADOPTED; their output accounting is closed.

`top_exit_full=True` adds `+top-exit-full-v1` and defaults OFF. The existing
`OilPathLifecycleOwner` checks the final selected path after bounded selection
and spike censoring, before state projection. A consecutive mature same-owner
upward trajectory must reach the configured top, then immediately disappear in
usable, unopposed imagery. Its anchor and current material/identity evidence must
qualify. Full state has no Oil coordinate. New interface evidence, unavailable
imagery, empty evidence, ambiguity or stale time clears the state and its witness.
No prior-only or mid-height-disappearance FULL is added.

Numeric nodes are unchanged. `OIL_TOP_EXIT_FULL`, a typed temporal confidence and
the selected frame/owner/Y witness distinguish this inference from current-image
FULL evidence; the raw image likelihood is not rewritten. Independent Foam
composition and final sample/CSV validity use the existing owners. The GUI flag
`--oil-top-exit-full` reaches all four detector entry factories; normal launch
remains unchanged. No new runner, Recipe field, manual label or numeric fallback
was added. Details are in the [design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-16-top-exit-full-closure).

## Verification

- New focused tests: **25 passed**. A synthetic selected rising owner produces
  coordinate-free FULL and real CSV output. Negative controls cover stationary,
  downward, reversal, mid-height, short/provisional and competing owners; material
  opposition; unselected admitted candidates; unavailable/black imagery; empty
  evidence; stale time; and new interface reset. Independent Foam composes with FULL.
- Existing initial-FULL, material phase, resolver and GUI entry suite, together
  with the then-current focused cases: **213 passed**. The final focused cases
  plus Foam, sample quality, trace pipeline and sequence integrity suite:
  **62 passed, 1 skipped**. The latter includes the 25 focused cases; counts are
  not additive. The skipped sample3 corpus check remains quarantined and was not
  bypassed or claimed as passing.
- Full local replay through detector/static preparation → `AnalysisPipeline` →
  output bundle/CSV/report ran both options with NONE and FULL debug. Both modes
  matched the prior retained v2 rows/events/report. CSV Y matched selected output.

| Frozen local input | Rows | v2 → closure Oil | v2 → closure Foam | FULL rows, both |
|---|---:|---:|---:|---:|
| base_sample_1, original Recipe | 30 | 12 → 12 | 0 → 0 | 0 |
| sample4, retained interior Recipe | 113 | 16 → 16 | 76 → 76 | 0 |

Raw inputs, final rows including validity/flags, events and report content match
between options. NONE/FULL also match phase diagnostics. These inputs use initial
FULL as a mechanism stress condition, not physical truth. No Windows media was
accessed. Neither video supplies a qualified positive closure; the positive case
above is synthetic resolver/publication evidence only.

## Geometry limitation and Windows boundary

The endpoint currently uses `ellipse.center_y - ellipse.radius_y`, with the
existing row-direction tolerance `max(1, height * 0.012)`. It does not treat the
whole entrance band, a crop edge or a margin edge as a physical top.
Direct inspection with the real mask builder and frozen local Recipes shows:

| Input | Configured top Y | Effective-mask top Y | Endpoint tolerance | Band reachable in mask |
|---|---:|---:|---:|---|
| base_sample_1 | 218 | 230 | 3.552 | No |
| sample4 | 808 | 811 | 1 | No |

This is an unresolved input/geometry limitation, not successful real-video FULL
recovery. The synthetic resolver fixture bypasses pixel masking and cannot
establish endpoint reachability. The Windows Recipe and actual final visible
interface must be checked before requesting a long run. If its endpoint is also
excluded or its physical meaning cannot be established, return the few geometry
and last-observation values and stop; do not tune margin or widen the gate.

The [Windows procedure](../../40-operations/s11-current-windows-field-qualification.md#top-exit-full-comparison)
contains that preflight and a conditional ④/⑧ comparison, with a short forwarding
prompt. Canonical [reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
keeps BASE 674–675 s uncertain transition and ≥675 s FULL. It is an evaluation
oracle, never a production time rule. Reuse review-004/005 practical multiple
allowances; review-006 remains pending. The later 721 s investigation is separate:
this code preserves existing numeric observations, including known false output,
and does not claim to identify shimmer or fix that selection.

## Reproducibility and retention

Local run: `sample/output/s11-top-exit-full-20261016-001`, based on
`e877cefd5780017c59fe05f3e9ef017f29a8fe09` plus the retained source patch.
The managed manifest binds the changed source bytes, inputs, parameters and
runtime. Patch SHA-256 is
`3f821913a2bc875ae702a1bb34a66868cf04c98776be31d4a44664a4e83b1d1b`.
The final published commit is reported with the handoff; no private-source
hash request is added to the user's Windows prompt.

Reuse the October 15 frozen input files and run the existing
`tests.diagnostics.s11_initial_full_comparison` entry with `--top-exit-comparison`,
with/without `--debug-full`, for base_sample_1 and sample4. These are local replay
commands, not the Windows private-video runner. Retained evidence consists of
two NONE comparison summaries, `summary.json`, and `source.patch`; equivalent
FULL summaries and temporary bundles were removed through managed closeout.
No model fit, detector threshold/ROI change or sample3 run occurred.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`
- Failure-registry entries: `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: existing v2 cannot convert the selected top-exit observation into a coordinate-free temporal FULL state; the new seam addresses that representation gap. Physical success is unknown, and the local mask check proves an endpoint reachability limitation that must be resolved for a real positive case. No new cause for the separate 721 s artifact is inferred.
- Existing feature coverage: local original base Recipe and retained interior sample4 Recipe use ellipse/margin masks (0.08), empty exclusions and no Artifact templates, normal static preparation and explicit initial FULL. Source Recipe initial AUTO is overridden only by the stress-test session confirmation. Initial-FULL v2 is ON in both modes; top-exit is the only comparison variable; cost-first/RGB/Local XY are OFF. Private Windows templates/ROI and physical-top correspondence were not exercised. Default behavior and prior candidate findings are retained.
- Execution scope: synthetic completed resolver/sample/CSV and independent Foam checks plus real GUI construction/CLI forwarding; two local full pipelines with raw detector, completed sequence and final CSV/report, NONE/FULL debug. Mask inspection uses the actual builder on the unchanged local Recipes. No private Windows execution, human top-exit judgment or milestone acceptance is claimed.
- Logic-map impact: UPDATED — add the opt-in launch route and post-selection closure before projection; mark temporal versus image state evidence and downstream coordinate-free validity, without changing numeric selection or Foam ownership.
- Failure-registry impact: UPDATED — F05 permits bounded selected-owner top-exit state evidence while preserving the rejection of prior-only and disappearance-only FULL. F08/F09/F10 negative/reset obligations remain; their historical failures are not promoted to success.
