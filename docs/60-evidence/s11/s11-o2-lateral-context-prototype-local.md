# S11 O2 ordered column-side context — local prototype

Base: `eac6d1f0634525d9bf8f4b86ea46b246e74b1a59`.
Scope: fixed-raster information controls for horizontal arrangement after the
[one-dimensional feasibility decision](s11-o2-spatial-context-feasibility-local.md).
No private frame, new Windows execution, classifier or production change.

## Result

An ordered per-column view of the two sides of a supplied candidate retains
horizontal information that can be lost in both the complete O1 witness and the
full-height row profile. Two constructed sector-mirrored rasters produce equal
O1 witnesses and row contexts but different ordered side-column observations.
Both photometric polarities pass this comparison with fixed auxiliary inputs.
This distinguishes image arrangement, not Oil versus structure.

The limitation is also executable: different two-dimensional arrangements can
have equal row means **and** equal side-column means. Combining these summaries
still does not recover the pixels, connected regions or physical ownership.
No physical identity score or region-adjacency claim is justified by this result.

## Ownership and implementation

Extended the existing diagnostic owner
`tests/diagnostics/s11_spatial_context_probe.py` with `measure_lateral_context`.
It calls the existing `measure_context` for raster/geometry validation and the
row comparison, and reuses `row_features.masked_row_mean` on transposed band
patches for column arithmetic. No parallel geometry validator, path search,
gradient operator, connected-component implementation or score owner was added.

Source discovery covered the witness's `_extra_channels`/`_center`, diagnostics
`_measure_sector`, row features, material paths, spatial path probe, preprocessing,
Foam membership and artifact connected components; responsibility-name searches
also covered src/tests repository-wide. Existing material/spatial paths generate
or select geometry; the new function measures only the exact supplied geometry.
Existing gradient/band summaries pool across columns; they do not retain the
ordered side-column means. Foam/artifact membership is not reused as Oil truth.

Inputs are the same uint8 raw raster, effective/glare masks, exact source points
and integer crop origin, plus an explicit integer band width (1–128). This width
is a measurement parameter, not an identity threshold. The O1 half-up sampling
convention is preserved. For local center c and width b the windows are
[c-b-1,c-1) and [c+2,c+b+2), both stop-exclusive. Each point retains its source
X/Y, basis, sampling center and ascending source X columns.

Each side preserves requested/clipped local and source ranges, crop completeness,
requested/in-crop depth, column effective/visible/glare-excluded counts, mean and
state. Partial windows retain measurements with crop_complete=false. Empty rows
or columns never wrap to the opposite crop edge; no visible samples become null,
while observed black remains zero. Sparse counts are not sufficient support.
Signed below-minus-above differences are in raw-gray units, null if either side
has no observed mean; unequal/partial support is retained rather than certified
comparable. There is no O1 `available` assertion or automatic gap interpolation.

Resource bounds inherit the existing 4096-axis/512-point limits and add 65,536
total point-columns and width128. The returned row_context is the original row
observation, not an independent vote. Spec `ordered-column-side-context-v1`
always emits NOT_EVALUATED and no score or threshold. The existing source CLI
continues to invoke only measure_context; it does not run this lateral prototype.
The module's code hash changes, but no historical artifact/receipt is rewritten
and no rerun of spatial-context-001 is requested.

## Verification

Added 19 cases in `tests/unit/test_s11_lateral_context_probe.py`:

- Full O1 and row-profile collision versus column distinction, both polarities;
  exact input preservation and strict JSON serialization.
- Mask/glare hiding all differences retains a collision; counts expose loss.
- Nonzero origin, fractional center, separate native/center bases and point order.
- Observed black, one-pixel support, zero support and glare retain distinct states.
- Top, partial and fractional bottom crop windows never wrap or silently complete.
- Vertical rearrangement within bands remains a column-summary collision;
  a joint row/column marginal collision still loses two-dimensional arrangement.
- Identical pixels and a possible reflection return never receive identity.
- Invalid band width, invalid geometry, output inventory bound and empty input.

Actual O1 comparisons reuse the real witness extractor with fixed mask/material/
Canny fixtures, not a full production preprocessing/proposal run. Synthetic scene
names and shapes are not assumed physical labels or field success rates.

```bash
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_lateral_context_probe.py \
  tests/unit/test_s11_spatial_context_probe.py \
  tests/unit/test_s11_spatial_context_run.py \
  tests/unit/test_s11_target_aggregation_contract.py
```

**80 passed in 3.22 s**, including the existing real synthetic bundle/video CLI
entry and receipt/mutation guards. Architecture, validation and current-state
documents are aligned; link, whitespace and detector-governance checks accompany
the change. Production source and decision behavior are unchanged.

## Decision and next boundary

Retain this local diagnostic as an information-retention control, not a complete
two-dimensional mechanism. No private Windows collection or relabeling is needed
to establish its known marginal collision. Before any further measurement rollout,
the next local hypothesis must retain a joint pixel/edge relation (rather than
more row/column aggregates), explain its candidate-relative physical hypothesis,
and pass the joint-marginal collision as well as mask and identical-image controls.
Existing raw crop/gray/mask files already retain the pixels; saving them again
is not a new observation. A connected bright region or coherent edge alone is
not Oil identity. W4 candidate identity and O2 acceptance remain open; FIELD FAIL
and the human idx0/idx20 ambiguity remain unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: horizontal pooling loses arrangement in constructed rasters; ordered column sides recover some of it but joint row/column summaries still collide. Private physical identity failure remains unproven.
- Logic-map impact: NONE — the existing offline measurement owner gains a local array function; production extraction, authority, selection and publication do not change.
- Failure-registry impact: NONE — no field repair is established and no appearance/geometry-only identity authority is introduced.
