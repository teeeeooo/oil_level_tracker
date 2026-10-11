# P5-S3 intensity-integrated enclosed regions — 2026-10-12

**CLOSED WITHOUT PROMOTION.** The actual operation reaches the intended synthetic
positive region but misses both predeclared real Foam uppers. This ends this fixed
appearance model before the broader comparison. It does not establish that the
recordings are unsuitable, that every non-learned method is impossible, or that
the product should accept the missed events.

The [Work Plan](../../00-project/work-plan.md) owns the next transition. The
[design](../../20-architecture/s11-interface-observability-witness-architecture.md#p5-s3-threshold-integrated-enclosed-regions--frozen-feasibility)
and [validation](../../30-validation/s11-interface-observability-witness-validation.md#p5-s3-staged-extremal-region-checks)
own the frozen operation and progression conditions.

## Freeze, ownership and information tested

The [preflight](2026-10-12-p5-extremal-regions/preflight.json) was committed in
`bec60f5` before either synthetic or real execution, over baseline `22c35ec`.
Its SHA-256 remains
`535967a2cc8bb1bbb745fbe1c630cc9fc1e05dea4a9242d8c98cd166f576da87`.
The [runner](2026-10-12-p5-extremal-regions/run.py) pins its implementation,
fixtures, inputs and execution head in the [full readout](2026-10-12-p5-extremal-regions/readout.json).
The code was an uncommitted implementation over that frozen head during execution;
the recorded file hashes identify the actual executed implementation.

Discovery found existing connected-component geometry, nominal connectivity and
side-texture owners, but no intensity-level-set integral in source, scripts or
diagnostics. The new measurement extends
[`s11_side_texture_probe`](../../../tests/diagnostics/s11_side_texture_probe.py).
Its caller is this saved-raster runner; no runtime registration or consumer is
added. Existing S2/LBP operations are retained. The isolated runner reads the
already pinned artifact formats because the historical S2 loader is local to
its frozen script; that script is not rewritten to change its historical hash.

The additional observation is contrast duration: at each integer grayscale cut,
measure the area of complete four-connected bright/dark regions, then integrate
their area over all 255 cuts. The same-pixel ablation takes the largest area at
one cut. Both retain closure and size constraints. This differs from single-Canny
separation and four-direction derivative conjunction, while retaining their
important limit: copied or reflected patterns can produce identical inputs.
Region appearance therefore remains UNRESOLVED physical evidence, with no scalar.

## Staged results

Thirteen constructed controls were executed. Strong stationary/inclined cells
below a plain upper side reach upper-like appearance. One-level contrast with
the same geometry falls below the integrated floor while the ablation still
calls it upper-like. Internal cells, a plain structural step, uniform pixels,
cropped/missing/partial support and copied/warped-copy collisions retain their
predeclared outcomes. Polarity reverses the cut-axis spectrum but preserves its
integral, maximum and decisions; equality does not mean identical cut indices.

The representative stage then measured **all 171 actual center-edge queries**
from four saved native rasters, without labels entering inference. Five queries
fall inside the four previously human-qualified source intervals:

| Qualified context / source Y | Upper integrated support | Lower integrated support | Integrated appearance | Peak-only ablation |
|---|---:|---:|---|---|
| sample4 Foam upper / 813 | 0 | 0 | low support — missed positive | low support |
| Water A Foam upper / 477 | 0.000012 | 0.019805 | low support — missed positive | upper-like |
| Water B surface / 485 | 0.001172 | 0.008452 | low support | internal-like |
| Water B surface / 488 | 0.002374 | 0.013856 | low support | upper-like |
| Water C surface / 491 | 0.003060 | 0.002980 | low support | upper-like |

Both sides are fully available at every qualified query. The failure is therefore
not caused by the pilot's complete-rectangle availability rule at these points.
At sample4, neither requested 6-by-13 side rectangle contains any eligible
complete region at any cut. This is a statement about these local rectangles and
this size/closure rule, not about all pixels, visible Foam, or native resolution
in general. At A, lower support is just below the frozen 0.02 floor. Lowering the
floor would change the experiment after its result; it would not supply the
absent sample4 observation. No such change was made.

B/C satisfy the necessary measured-opposition condition, but zero of two Foam
positives survive. This cannot be credited as a useful partial detector. The
exact source-Y833 internal-texture guide still has no center Canny query; it
remains unassessed rather than snapped to another edge. All 42 inventory entries
are retained: four have only representative-stage measurements and **38 are
NOT_RUN**. The failed gate prevents the broader comparison, behavior work and
Windows shadow for S3. S1/S2 are not reopened.

## Verification and reproducibility

The focused new/previous operation suite passed **31 tests in 0.39 s**:

```bash
.venv/bin/python -m pytest -q tests/unit/test_s11_extremal_regions.py tests/unit/test_s11_spatial_conjunction.py
```

The [independent verifier](2026-10-12-p5-extremal-regions/verify.py) checks all 171
queries, all 342 side records (322 available), coordinate joins, interval joins,
resource bounds and the full retained inventory. A separate pixel flood, without
OpenCV or the implementation's distinct-level optimization, reconstructs all
255 cuts on all **10 qualified side rectangles**. The
[verification receipt](2026-10-12-p5-extremal-regions/verification.json) records
PASS, 16 pinned inputs and 221 unchanged production Python files.

The real representative measurement took 2.392 s; process peak RSS was 85,164,032
bytes, including preparation and synthetic work. These satisfy the diagnostic's
60 s / 512 MiB bounds, not an application performance qualification. S3 decoded
no video and changed no production, Oil, Foam episode, report or field behavior.
R22 / Local XY OFF / O2 OPEN / FIELD FAIL remain.

Reproduce into new output paths; the scripts refuse to overwrite evidence:

```bash
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-p5-extremal-regions/run.py --root . --output /tmp/s11-s3-readout.json
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-p5-extremal-regions/verify.py --root . --output /tmp/s11-s3-verification.json
```

The verifier verifies the committed readout beside its script. Historical S2
whole-file pins still refer to its recorded source revision; adding the S3
operation changes the containing module's hash without changing S2's function.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: the proposed region-appearance measurement loses both qualified positives before any raw-front selection or episode consumer; sample4 has zero eligible side-region area and A falls below the fixed contrast-area floor. This is the pilot's first loss, not a new attribution of production failure.
- Logic-map impact: NONE — an existing offline diagnostic owner is extended with no executing application route, physical authority or consumer change.
- Failure-registry impact: NONE — existing representation/role, provenance and no-retuning guards cover this bounded appearance failure; no new field cause or repair is claimed.
