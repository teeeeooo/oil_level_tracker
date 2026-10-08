# D2 saved-edge contact representation readout

**Disposition:** CLOSED WITHOUT PROMOTION for `saved-canny-local-arm-contact-v1`.
**Question:** can the existing saved Canny raster, read as exact local graph arms,
represent the [f1320 human contact relation](2026-10-08-d2-contact-observability.md#contact-interpretation-received--2026-10-08)?
This completed Mac experiment is neither an Oil classifier nor a Windows result.
The [Work Plan](../../00-project/work-plan.md) owns the next transition;
[Witness Validation](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance)
retains the unmet O2 gate and `FIELD FAIL` remains unchanged.

## Frozen scope and execution

Source/tests/design were committed as `9937b33` before measuring real rasters.
The [fixed design](../../20-architecture/s11-interface-observability-witness-architecture.md#saved-edge-contact-measurement--fixed-v1-preflight)
pins preflight SHA-256 `69c2ec764c3618dd5b76bb6e538918012a0c248bdc3756693ffb8fe7318567fe`.
The [machine receipt](2026-10-08-d2-saved-edge-contact.json) preserves the full
source HEAD, 54 input/source hashes, runner/output hashes, runtime and summaries.
Local detailed artifacts remain under
`sample/output/s11-d2-edge-contact-20261008-001/`.

- Reused seven A1 saved Canny crops and matching effective/glare masks. No Canny
  recomputation, image enhancement, detector replay or video decode.
- Measured all 153 existing A2 candidates at their original W1 native geometry,
  otherwise their recorded candidate center. Missing native sectors stay absent.
- Retained all three existing band widths b=3/6/9, with patch radii 6/12/18.
  No chosen scale, new Y, threshold adjustment or candidate ranking.
- A marker requires distinct left/right/up arms after removing a 3×3 junction
  core from the center's 8-connected component. This is a raster-shape definition,
  not a direct measurement of physical contact.
- Loaded and validated frozen truth only after persisting all raw measurements.
  The descriptive join has 7 target, 3 wrong-target and 143 unreviewed candidates;
  all are previously exposed regression. Wrong-target does not imply non-interface.

All 54 pins match before/after. Seven crops are 104×104 at source origin [543,798].
The largest per-frame patch workload was 2,448,516 pixels against a 50,000,000
bound. The run took about 1.02 s on Python 3.14.4 / OpenCV 4.14.0 / NumPy 2.5.1;
this is a local diagnostic timing, not a production performance benchmark.

## Primary f1320 result

The predeclared central comparison uses source X in **[566,625)**. Idx9 has the
recorded native Y844 there; idx21 uses its candidate-center Y822. Requested
centers are all raster positions within each original Y corridor, including
positions without an edge. Fully observed means the complete local patch stays
inside effective/non-glare support. Edge counts below are correlated centers,
not independent physical contacts or confidence.

| b / radius | Idx9 fully observed / requested | Idx9 upper-contact markers | Idx21 fully observed / requested | Idx21 upper-contact markers |
|---|---:|---:|---:|---:|
| 3 / 6 | 413 / 413 | 0 | 393 / 413 | 0 |
| 6 / 12 | 633 / 767 | 0 | 377 / 767 | 0 |
| 9 / 18 | 589 / 1121 | 0 | 136 / 1121 | 0 |

At b=3, idx9 has 61 observed edge centers: 60 `two_arm_shape` and one
`complex_or_short`. Thus the primary miss at this scale is **not explained by
missing masks**. Idx21 has 109 visible edge centers: 40 two-arm, 62 complex/short,
two no-reaching-arm and five unavailable. Neither produces an upper-contact
marker. Larger scales retain missingness explicitly and do not recover the marker.

The assistant directly inspected the original crop and saved Canny image, then
rendered `f1320-edge-contact.png` as a coordinate-preserving comparison. The saved
raster retains a long lower contour near the orange reference while many upper
curves end or turn above it. Inference: the exact local T-arm definition does not
encode the user's region-level “touch and end” relation. This does **not** prove
that the image or all Canny geometry has lost every usable relation; the failure
belongs to the frozen edge-plus-local-arm representation. Blur/quantization,
edge extraction and physical optics have not been causally separated.

The human reply stays valid. Glass pattern/low-resolution attribution stays
**tentative**; no new physical subtype, contour label or scalar truth is created.

## Opposing and preserved controls

| Existing band width | Targets with ≥1 upper-contact marker / 7 | Wrong targets with ≥1 marker / 3 |
|---|---:|---:|
| 3 | 1 / 7 | 0 / 3 |
| 6 | 1 / 7 | 0 / 3 |
| 9 | 0 / 7 | 0 / 3 |

Only f1260 idx4 has markers: one at b=3 and four at b=6. These are descriptive
presence counts, **not recall/specificity or an operating point**. A marker-only
filter would lose most known targets and the primary confirmed contact, so the
zero wrong-target marker count is not suppression success. No W3 prediction or
score was produced. All 143 unreviewed candidates retain their unknown truth.

Nineteen synthetic contracts passed before the real readout, including upper/
lower T, crossing, plain line, disconnected/gapped strokes, locally reconnected
arms, crop/mask exclusion, coordinate preservation and resource limits. An
identical structural T produces the same readout as a fluid T: even a positive
marker cannot alone certify Oil identity. A genuine plain stationary interface
may have no contact marker; it must not become a negative label.

## Consequence and remaining design boundary

Close this frozen representation without promotion or scale/threshold/gap-filling
continuation. No production source, labels, recipe, report or accepted detector
behavior changed. D1 and the Windows D2 control lookup remain closed.

A follow-up must represent the **boundary of the upper textured region relative
to the lower region**, rather than require exact pixel attachment to a three-arm
junction. That is a new observable/representation contract, not permission to
rename existing contrast, component count or motion into identity. Before another
run, specify its region/contour construction, unavailable state and optical/
structural counter-controls using the existing owners. It must preserve genuine
plain interfaces and later combine with independently validated temporal evidence.
No successful discriminator, scalar calibration or production entry is established.
No additional user judgment or Windows request is needed to close this readout.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: this diagnostic's exact local-arm representation fails the primary human-positive relation before any candidate decision. The production final-selection first cause and optical subtype remain unknown.
- Logic-map impact: NONE — a pure offline diagnostic reads saved rasters and geometry; no production owner, publication path or physical authority changes.
- Failure-registry impact: NONE — the bounded result refines the local representation limit under existing geometry/support/retuning failures; it establishes no new field cause or accepted mechanism.
