# S11 Slice D Effectiveness Reconciliation

Date: 2026-08-08

Accepted baseline: `main @ 090444dccce2397835d10c159c8fb2ee2933da6c`

Status: `ACCEPTED — simplified detector baseline proceeds to final Windows field-workflow validation`

## Objective and authority

Slice D is the Orchestrator-owned read-only reconciliation gate after accepted Subtractive Detector Simplification Slices A–C. It asks whether the remaining local-corpus misses demonstrate a material general detector failure class that warrants another bounded source gate. It does not authorize source tuning, interpolation or a new detector mechanism by itself.

## Current production replay

The accepted baseline was replayed with the actual `OpenCvPhaseDetector`, static-artifact learning, serialized detector owner and the established 2 FPS qualification windows:

| Sample | Window | Rows | Numeric Oil | Longest missing span |
| --- | --- | ---: | ---: | ---: |
| `base_sample_1` | `0.0–14.4 s` | 30 | 3 | `8.9 s` |
| `sample2` | `0.0–2.0 s` | 5 | 2 | `0.5 s` |
| `sample3` | `30.03–105.0 s` | 151 | 42 | `17.0 s` |
| `sample4` | `0.0–56.0 s` | 113 | 62 | `3.5 s` |
| **Corpus** |  | **299** | **109** |  |

The accepted Slice C result is therefore reproduced: `109/299` numeric Oil.

The retained 13-frame user-confirmed truth surface is `8/13` numeric with MAE `5.4375 px`, median error `6.5 px` and maximum error `11 px`.

## Residual-gap attribution

The longest base-sample gap (`5.5–14.4 s`) is not a clean general positive-evidence failure. Frozen provisional visual notes mark the same interval as dominated by the static explanatory overlay and reflections, with the physical interface not reliably separable from those artifacts. Safe abstention is preferable to promoting the overlay as Oil.

The longest sample3 gap (`67.03–84.03 s`) overlaps frozen no-interface/unclear evidence and severe motion, reframing blur and dark/off-center illumination around `70–80 s`. This is not evidence that an otherwise clearly observable common interface class lacks a detector mechanism.

Later sample3 visually identifiable points still include misses, but the production stream is bracketed by useful accepted anchors (for example around `88–100 s`) and the remaining local gaps are materially shorter. Sample4's remaining longest gap is `3.5 s`; its accepted anchors now densely represent the same observed Oil trajectory.

The remaining misses therefore do not collapse into one material, repeatable, hard-safe general failure class across the four-video corpus.

## Retained safety evidence

Current-main preservation validation was executed with:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_oil_controlled_benchmark.py \
  tests/test_oil_single_frame_observability_contract.py \
  tests/test_s11_spatial_path_probe.py \
  tests/test_s11_spatial_production_fallback.py
```

Result: `356 passed in 144.67 s`.

This covers the retained collision/glare/structure/Foam/no-interface and bounded Spatial production surfaces used by the reconciliation. No source or test file was modified.

## Decision and claim boundary

**Slice D accepts the simplified A–C detector source baseline.** No additional detector mechanism is authorized from the available evidence. A future source gate requires new evidence of a material general failure class rather than an isolated hard/occluded scene or a desire to increase publication count.

This is an available-corpus effectiveness decision, not category-balanced or general-field detector-accuracy PASS. Full repository/canonical/E2E and Windows validation were not run as Slice D evidence. The exact next S11 gate is the target-Windows final field-workflow validation using the existing operational checklist.
