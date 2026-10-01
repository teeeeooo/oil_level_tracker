# S11 O2 spatial-context source adapter — local verification

Base: `dfe56af` plus the preceding uncommitted structure-context closeout and
array-prototype work, published together with this adapter. Scope: read-only
measurement on existing source frames, not identity classification or production
integration. Private Windows execution is pending; FIELD FAIL remains unchanged.

## Change and reuse decision

`tests/diagnostics/s11_spatial_context_run.py` supplies the IO/receipt/CLI boundary
around the label-free `s11_spatial_context_probe.measure_context`. It is separate
from the stored-record target audit because that audit has no source pixels, and
from the array function to keep measurement independent of labels/video IO.

Discovery checked existing source probes, the video reader, review/bundle link
owner, packet verifier, recipe mask/preprocessing owners and row arithmetic.
The adapter reuses `ResultBundleReader`, `s11_review_records.load_link`, bundle
identity/indexed packet verification, `OpenCvVideoReader`, `build_mask_bundle`,
`preprocess`, `review_geometry`, and existing O1 band arithmetic. No production
source was changed, no duplicate candidate generator/score/decoder was introduced.

The source-byte hash, bundle identity, packet-to-trace equality and exact linked
scene are checked before decoding. Existing reader seek may advance at most 120
frames, accepting only the requested backend-reported index. Decoded dimensions,
witness crop origin/size and complete original geometry are checked. Original
recipe settings and current code/runtime hashes accompany raw raster hashes.
The 512-point resource cap accommodates both candidate-center/native-path
inventories; this replaces the 128-point array-prototype cap without dropping
points. No label class affects selection, pixels or profile extent.

Outputs in a new external directory: `experiment.json`, generated `summary.md`,
source/crop/gray/effective/glare PNGs, per-X SVG plots and last-written
`complete.json`. Every output has a file hash; every input has before/after hashes.
Source/crop images are unannotated. Numeric plots retain gaps and original
candidate markers; JSON owns their exact values. Existing O1 bands remain intact.

## Reconstruction limitation and controls

No historical decoded-pixel hash exists in the old packet. Therefore video/index
association is not claimed to prove historical pixel identity. Existing gray and
support band fields are recomputed by their arithmetic owner, recording all
mismatches. Absolute 1e-10 tolerance concerns floating arithmetic only in 0..1 gray
units. A baseline `DIFFERENT` result prevents an extent-only comparison until
reconstruction is understood; COMPLETE still means execution, not efficacy.
Masked/cropped extent and horizontal averaging remain explicit limitations.
Human idx0/idx20 ambiguity, all original labels and all previous scores are unchanged.

## Verification

```bash
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_spatial_context_run.py \
  tests/unit/test_s11_spatial_context_probe.py \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_s11_review_records.py \
  tests/unit/test_s11_structure_context.py
```

**99 passed in 4.64 s.** This includes 17 new source-adapter controls and the 19
array-prototype controls, plus related aggregation/records/structure contracts.
Tests use actual synthetic indexed bundles and generated videos, including two
distinct frames in one source bundle. The real CLI executes in a Unicode,
non-repository cwd with closed stdin/explicit UTF-8. Checks cover exact geometry
inventory, baseline witness preservation, decoded raster/PNG equality, receipts,
all output hashes and all original file bytes. Wrong video/bundle/link/scene/
packet/revision, writer lock, decoder overshoot, source dimensions/crop mismatch,
mid-measurement and mid-publication input mutation all fail without COMPLETE.
Baseline controls retain arithmetic parity and explicitly detect gray drift.

Governance, changed-document links and whitespace checks accompany publication.
These checks validate the local execution path only. Actual Windows codec/recipe
reconstruction and wider spatial information in private frames remain unmeasured.

## Next action

Run the [Windows procedure](../../40-operations/s11-o2-local-shadow-evaluation.md#ordered-spatial-context--existing-two-source-frames)
on existing review-002 rev14 and review-003 rev4, original R22-3 bundle and linked
SPL#1 source video. Return the generated summary and receipt/input/output checks,
including baseline band status/counts. Keep raw outputs local. No new labeling,
frame interval, score tuning, template registration or detector replay is requested.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: finite sampling can omit a remote transition in constructed rasters; a corresponding private physical identity failure cause is still unproven. This adapter tests provenance and measurement availability, not a repair.
- Logic-map impact: NONE — offline diagnostic entry only; no production extraction/authority/association/publication changed.
- Failure-registry impact: NONE — no new field cause or efficacy result; motion/coordinate/private-case shortcuts remain prohibited.
