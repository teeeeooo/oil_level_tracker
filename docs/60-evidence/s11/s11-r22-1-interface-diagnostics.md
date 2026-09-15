# R22-1 Interface Diagnostics Local Evidence

## Scope and identities

This records local verification of the
[R22-1 measurement-only change](../../20-architecture/s11-r22-1-interface-diagnostics-architecture.md).
It is not field accuracy acceptance or implementation of the later behavioral
repair proposal. Windows effectiveness remains FIELD FAIL.

- Baseline source: clean Git archive of `706f398c0684cc2a68ecfa250729caa9a7b8927e`.
- Baseline detector: `opencv-phase-detector-r22-oil-ownership-evidence-replacement-v1`.
- Candidate: working tree over that base, detector
  `opencv-phase-detector-r22-1-interface-diagnostics-v1`.
- Both completed resolvers: `r22-oil-ownership-evidence-replacement-v1`.
- New payload: `r22-1-interface-raster-diagnostics-v1`.

Candidate working-tree files are not identified by the baseline SHA alone.
Any source archive must include its own file-hash manifest. No commit, push or
Windows execution is claimed by this evidence.

## Raster and integration checks

The new tests measure a true intensity step and an internal stripe with the
same near-band contrast and raw material value. Their broader context differs:
the step retains its far-band contrast while the stripe returns to the original
material. Additional controls cover uniform material, inverse contrast, curved
sector boundaries, source/crop offsets, missing material/static context,
masked/glared/clipped bands, duplicate/rejected/outside candidates and strict
finite JSON serialization.

These show that the diagnostic fields expose distinctions in constructed
images. They do not establish a reliable classifier for real Oil versus
reflection. Classification remains `not_evaluated`.

Integration tests verify debug-on/off current and completed candidate/output
equality, and BASIC/FULL JSONL retention after sequence annotation. Every
diagnostic candidate joins the raw trace candidate through the new original
input index despite score sorting. The measurement namespace is absent from
the detection's resolver-facing debug metrics.

## Tests and corrections

- Initial focused diagnostic, JSONL and Oil integration run: **29 passed**.
- Full non-Qt run: **1,520 passed, 2 failed, 252 deselected**. Both failures were
  addressed: the new test now explicitly reads UTF-8, and the old current-frame
  characterization excludes only the newly added diagnostic namespace.
- The original characterization fingerprint constant was retained. All legacy
  state, candidates, metrics, profiles and image fingerprints must still match.
- Focused rerun of all new diagnostics, characterization and test-authoring
  policy: **18 passed**, including both formerly failing cases. The entire
  non-Qt suite was not rerun after those two test-only corrections.
- Qt suite: **252 passed, 1,522 deselected**.
- Source/tests compile check passed. Detector governance, documentation links
  and whitespace are checked for this final change as well.

## Four-video baseline comparison

Use the checked public recipes and existing qualification windows at 2 Hz:
`base_sample_1` 0--14.4 s, `sample2` 0--2 s, `sample3` 30.03--105 s,
`sample4` 0--56 s. The standard replay harness confirms UNKNOWN initial state
for these public comparisons. No claim about the private initial-FULL/EMPTY
episodes follows from these public inputs.

The clean baseline and candidate were run in separate Python processes using
the same interpreter/media/recipes. First compare ordinary runs. Then run the
candidate with an actual `JsonlDebugTraceWriterFactory`, BASIC trace and
`OutputBundleStore`; setting the trace level alone without the sink factory
does not exercise measurement extraction in `AnalysisPipeline`.

The trace-enabled candidate also matched the clean baseline. All CSV columns
were compared after excluding only `run_id`; no coordinate, confidence, state,
validity, flag or event columns were excluded.

| Public sample | Tracking rows equal | Event rows equal | Trace records | Oil diagnostic rows |
|---|---:|---:|---:|---:|
| base_sample_1 | 30 | 10 | 30 | 725 |
| sample2 | 5 | 4 | 5 | 136 |
| sample3 | 151 | 35 | 151 | 3,324 |
| sample4 | 113 | 19 | 113 | 2,549 |
| Total | **299** | **68** | **299** | **6,734** |

Every diagnostic row was joined back to its raw candidate by original input
index and checked for source/Y equality. Source-frame indices matched their
containing record. BASIC happened to capture every sampled frame in these
inputs; it remains a sparse policy generally.

Tracking fingerprints matched baseline and candidate:

```text
base_sample_1 5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7
sample2       85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976
sample3       feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1
sample4       e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1
```

Sample4's previously documented historical-runtime discrepancy is unchanged;
its historical golden was not replaced. The baseline comparison is against
the same current runtime, not a claim that historical replay provenance is fixed.

## Cost and remaining validation

Compact JSON encoding of the new payloads totaled 53,459,956 bytes across the
299 captured records (excluding all existing trace fields/images). This is a
real diagnostic storage cost; FULL image trace adds its existing image cost.
The measurement stage is skipped with debug disabled. Replay wall times were
not isolated from concurrent test load, so no throughput claim is made.

Windows must now measure the reviewed actual and false boundaries. Real-video
discriminability, operating thresholds and a future classifier remain unproven.
Use the [one-frame Windows procedure](../../40-operations/s11-r22-1-windows-interface-measurement.md)
before requesting broader analysis.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: no new detector decision stage is introduced; the diagnosis targets missing spatial evidence for previously observed identity/texture failures. Windows discrimination is not yet measured.
- Logic-map impact: UPDATED — R22-1 runtime identity and its debug-only raster route are documented without changing decision owners.
- Failure-registry impact: NONE — local observability and equality controls do not establish a new field mechanism or repair historical failures.
