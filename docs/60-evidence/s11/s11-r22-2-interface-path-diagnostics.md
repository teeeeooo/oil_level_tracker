# R22-2 Native Path Diagnostics Evidence

## Scope and source identity

This records the [R22-2 diagnostic change](../../20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md).
It preserves R22 behavior and does not qualify Windows accuracy. FIELD FAIL
remains the disposition. The [work plan](../../00-project/work-plan.md) owns the
next transition and current acceptance.

- Clean comparison baseline: Git archive of `85995b66b9f36c5126881ab7d3e6a8c204679c17`.
- Baseline detector: `opencv-phase-detector-r22-1-interface-diagnostics-v1`.
- Candidate detector: `opencv-phase-detector-r22-2-interface-path-diagnostics-v1`.
- Both resolvers: `r22-oil-ownership-evidence-replacement-v1`.
- Candidate diagnostic schema: `r22-2-interface-path-diagnostics-v1`.
- Candidate source is the code committed with this record, not the baseline
  SHA alone. No private Windows execution of R22-2 is claimed here.

## Reviewed inputs and interpretation limits

The user supplied four R22-1 single-candidate Windows reports. Native media and
trace were not exported. Physical labels below are the user's direct review;
scalar measurements do not establish those labels independently.

| Reported checkpoint | Reviewed physical relation | Diagnostic observation |
|---|---|---|
| BASE frame 14386 material_path Y=411.5 | actual boundary vicinity | central sector near contrast -0.05606; peak Y=405 |
| BASE frame 14362 material_path Y=438 | false candidate; reviewed boundary near 412.5 | central near +0.02643, far +0.06262 |
| Accum frame 16280 calibrated_high_recall Y=213 | reviewed boundary vicinity | central near +0.03335; peak Y=216, gradient -0.091187 |
| Accum frame 16280 material_path Y=217 | nearby candidate, exact physical identity not certified | central near -0.12218; same peak Y=216 and gradient |

The adjacent Accum candidates also share sector-3 peak Y=218 and gradient
-0.077771, while near-band signs differ. These are same-raster measurements,
not independent corroboration. From the existing half-open band formula, moving
the scalar center four pixels can move those structures between near bands and
the excluded center. Whether each generator's native sector row represents the
physical interface was not recorded in R22-1 and remains a Windows unknown.

The existing synthetic stripe/step control further prevents interpreting
positive near-minus-far contrast alone as an interface classifier. No operating
threshold is justified from this small, selected set. Earlier LVLM coordinates
and candidate inventories were corrected by direct human review; they are not
reintroduced as truth. Canonical operational truth remains in the
[reviewed-truth owner](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).

## Source inspection and implementation

The existing material generator computes sector paths and scalar medians, then
previously discarded native geometry at candidate construction. The existing
spatial fallback serves a different owner. R22-2 extends the material generator
with optional capture rather than adding another finder or rerunning it.

Frame-local sidecars retain native IDs, X bounds, Y, signed contrast, strength,
winning contrast channel and scale through candidate assembly. The existing
diagnostic measurement helper now serves both original and native X extents.
Each native sample includes a candidate-centered control on the same X extent.
The source/Y/index join is checked; unrelated candidates cannot borrow a path.
Peak finding never relocates the sampled path. Missing paths/bands stay explicit.
Nothing enters candidate features or the resolver. Classification and independent
support remain `not_evaluated`.

## Focused controls

Focused diagnostics, material-path and existing characterization tests:
**21 passed**. Controls cover capture-on/off exact candidate equality for gray
and material channels, inset crop/sector provenance, a curved native path,
unchanged original measurements, same-X control centers, duplicate/rejected
candidates, non-borrowing, mismatched provenance, masked bands, unchanged peak
centering and strict finite JSON. Real detector and BASIC/FULL writer tests
verify joins after score sorting and completed-sequence annotation.

The original current-frame characterization fingerprint is unchanged. Only the
already-excluded diagnostic namespace differs. Final full-suite checks passed:

- `.venv/bin/python -m pytest -q -m 'not qt_app'`: **1,527 passed**, 254 deselected.
- `.venv/bin/python -m pytest -q -m qt_app`: **254 passed**, 1,527 deselected.
- Combined canonical coverage: **1,781 passed** across the two process groups.
- Detector governance against baseline `85995b6` and whitespace checks passed.

Final review corrected only the new diagnostic formula string to include its
existing clipping operation. The 21 focused tests and all four candidate
replays were rerun after that metadata correction; the comparison below uses
those final outputs. No numerical algorithm changed in that correction.

## Four public same-runtime comparisons

Both clean R22-1 and R22-2 ran in separate processes with actual FULL JSONL sinks
and output bundles. The existing replay session, frozen-input validation,
runtime-provenance and fingerprint helpers were reused. Qualification windows
remain base_sample_1 0--14.4 s, sample2 0--2 s, sample3 30.03--105 s and sample4
0--56 s, at 2 Hz and the existing public UNKNOWN initial-state configuration.

Runtime and input fingerprints match for each pair: CPython 3.14.4, macOS arm64,
OpenCV 4.14.0 (package 4.14.0.94), NumPy 2.5.1, FFMPEG decoder. This compares
the current runtime, not the unresolved historical Sample4 decoder environment.
No golden or frozen media/recipe/truth hash was replaced.

| Sample | Equal tracking rows | Equal event rows | Trace records | Equal old Oil diagnostics | Added native paths |
|---|---:|---:|---:|---:|---:|
| base_sample_1 | 30 | 10 | 30 | 725 | 173 |
| sample2 | 5 | 4 | 5 | 136 | 36 |
| sample3 | 151 | 35 | 151 | 3,324 | 785 |
| sample4 | 113 | 19 | 113 | 2,549 | 538 |
| Total | **299** | **68** | **299** | **6,734** | **1,532** |

All CSV columns match after excluding only `run_id`. Raw candidates, completed
`sequence` objects and existing state fields also match exactly. For the old
diagnostic comparison, only the new `path_aligned` member is removed and the
schema identity normalized. All original measurement values are equal.

All new diagnostic rows join raw candidates by input index and exact source/Y.
Native paths have bounded source X/Y and exact same-X comparison support.
Every material/raster-material candidate in these traces has a native path;
the other 5,202 candidates explicitly report `no_captured_native_path`.

```text
base_sample_1 5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7
sample2       85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976
sample3       feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1
sample4       e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1
```

## Storage and remaining gates

Compact JSON diagnostic payloads across 299 records increase from 53,459,956 to
77,063,783 bytes (approximately 44%); this excludes other trace fields/images.
Capture and measurement are skipped with debug disabled. Wall times were not
isolated from other verification, so no throughput claim is made.

The [Windows procedure](../../40-operations/s11-r22-2-windows-interface-measurement.md)
starts with Accum frame 16280 material_path Y=217 only. Native-path accuracy,
real/false discrimination, independent support, association repair, initial-FULL
observation and owner handoff remain unvalidated. R22-2 does not fix those
behavioral failures or establish field effectiveness.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: no new decision stage; the bounded diagnostic gap is discarded native geometry and candidate-center-sensitive raster sampling. The first harmful physical stage for additional Windows frames remains unknown until reviewed evidence is collected.
- Logic-map impact: UPDATED — native capture and same-X measurement are documented with R22-2 diagnostic identity and unchanged R22 behavior.
- Failure-registry impact: NONE — measured observability and local equality do not establish a new field failure or repair.
