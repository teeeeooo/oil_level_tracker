# Report source-context implementation and validation — 2026-10-07

## Scope and disposition

Purpose: preserve the user's understanding of major Oil/interface and Foam motion
in the report, not maximize per-frame detector recall. This is a separately
implemented report candidate, not a physical-identity or field-acceptance claim.
Current milestone/gates remain owned by [Work Plan](../../00-project/work-plan.md).
Design: [bounded source context](../../20-architecture/s11-report-source-context-design.md).

Base: `a17d9871693ea23efc7da141fb599b6f5ba472b7`.
Frozen tested source: `c688b3e0e171916a8821d0564bf064eed783f2d0`.
Local branch: `work/s11-context-validation-20261007`; main was not modified.
Native evidence: `sample/output/s11-context-validation-20261007-001/`.
New worktree: `/Users/sunjaekim/Developer/oil_level_tracker-s11-context-validation-20261007`.

## Implemented behavior

A separate RGB time–height image uses row medians over the central 40% of the
configured ellipse bounding width. Spatial compression is limited to 240 height
bins and temporal sampling to 360 columns per Glass, no faster than the analysis
rate. There is no detector/candidate/truth input, interpolation or carry.
Requested/actual decoded time, frame ID, spatial bin edges and missingness are
written to an offline JSON asset. Decode/seek failures remain blank; invalid
native cadence is unavailable; source-open failures are disclosed and cancellation
still aborts the transactional bundle. Numerical tracking, CSV, events, Recipe,
Result Review and domain judgment are unchanged. Foam direct connections in both
static graphs now obey the existing two-second report horizon, retaining markers.
The report explicitly separates configured-rule judgment from detection accuracy,
Oil endpoint-gap dashes from Foam-series dashes, and source appearance from
Oil/Foam identity. It discloses reflection, structure, overlays, camera/exposure
change, suppressed local curvature/bubbles and temporal undersampling.

## Completed real-video verification

Four source windows were run on baseline, initial candidate and final candidate
(12 official application/report runs). `verification-final.json` and
`final-replay-receipt.json` record exact commands, source/input hashes and checks.
All 12 video/recipe/truth inputs stayed unchanged. All final source hashes stayed
fixed during replay. The initial and final context PNGs are byte-identical.

| Sample | Window (s) | Rows | Numeric Oil | Numeric Foam | Source columns |
|---|---|---:|---:|---:|---:|
| base_sample_1 | 0–14.4 | 30 | 28 | 0 | 29/29 |
| sample2 | 0–2 | 5 | 4 | 0 | 5/5 |
| sample3 | 30.03–105 | 151 | 29 | 5 | 150/150 |
| sample4 | 0–56 | 113 | 101 | 26 | 113/113 |
| Total | exposed public/local corpus | 299 | 162 | 31 | 297/297 |

All tracking fingerprints, values/validity/flags, events, executed recipes, truth
comparison outputs and provenance match baseline. CSV compares ignore only
`run_id` and event `capture_path`. Numeric Oil without same-frame provenance: 0.
These are non-regression counts, NOT detection accuracy or physical absence.
All 44 HTML image/metadata asset references resolve internally and PNGs decode.
This is not a cross-browser visual/layout verification.

## Direct source/report inspection
Raw source contact sheets and all four context images were directly viewed.
Sample3's longest interval between Oil observations is 46.4798 s (34.5345–81.0143)
and covers substantial visible change. The source image exposes that appearance
without inventing a trajectory. Sample4 separates moving bright appearance from
a largely fixed lower band, but this does not classify either material.
Base contains explanatory overlay lines, which correctly remain in the raw image.
Sample2's central median suppresses individual bubbles; no-Foam numeric output is
not a physical-absence judgment and the context image is not a bubble classifier.

The exposed target correspondence control is unchanged: correct Oil selections at
38/42.5/49.5/52 s survive; incorrect selections at 40/42/44 s remain. In particular,
the wrong 42/44 s values remain the report's minimum/maximum observations. This
important residual presentation/identity problem is NOT repaired by the new asset.
Matched-candidate coordinates are not promoted to independently calibrated scalar
truth, and the seven-frame score is not the product acceptance unit.

A separate frozen diagnostic contract also checked sample4 38–46 s at native
30-fps request cadence: 241/241 source columns available. Original recipes were
unchanged. This zoom reveals finer variation than the broad 2-fps image; the
previously human-confirmed rapid rise/fall must not be suppressed as noise simply
because sampled endpoints look similar. The zoom is not a production feature or
new human validation. See `native-context-contract.md` and `native-context-38-46/`.

The source renderer performs additional bounded seeks/decodes. Initial pipeline
elapsed totals were 281.25 s baseline and 341.24 s candidate; these are not an
isolated repeated performance benchmark. Final runs overlapped regression tests,
so their larger elapsed time is not an uncontaminated overhead estimate.

## Automated validation

- Focused report/source/graph controls: **55 passed** before full enumeration.
- Initial single-process non-Qt run: **900-second timeout**, preserved as incomplete.
- File-sharded non-Qt inventory: all **2,189** exact node IDs executed; **2,187 passed / 2 failed**. Qt run: **254 passed** (73.67 s). Total complete enumeration: **2,443 cases, 2,441 passed / 2 test-authoring policy failures**; no skipped case.
- New source-context test omitted an explicit UTF-8 read encoding. Existing `test_s11_target_truth.py` CLI test omitted `stdin=DEVNULL`; the latter reproduces on untouched main (**3 passed / 1 failed** policy cases).
- Test-only correction commit: `1336e4dd939451a2cd83d8d71c9114e97995a828`. All affected tests and policy/report controls rerun: **83 passed** (23.33 s).
- `validation-matrix-final.json` proves exact full-inventory coverage, both initial failures and every changed test case rechecked, unchanged production `src` tree, and unchanged 12 inputs. A complete post-correction monolithic suite was NOT rerun; do not shorten this result to an unqualified full-suite PASS.

The first exception control found two failures for NaN/Inf native FPS; these were
repaired before final source freeze. `exception-red.log` remains preserved.
Do not label the initial interrupted single-process suite as a passing run, nor
claim the historical intermittent A0Q Qt issue resolved from one successful run.

## Acceptance boundary and next priority

Locally useful source context is demonstrated; independently measured user
comprehension is NOT_EVALUATED. The existing seven targets are exposed regression
material, not a held-out efficacy corpus. This candidate does not promote A2,
complete O2/O3, relax authority, or qualify Windows. All nine canonical private
Windows segments remain NOT_EVALUATED in this session and prior FIELD FAIL stands.

Next assess whole consequential episodes: direction/order, Oil/Foam separation,
misleading extrema and long wrong paths, honest uncertainty and original evidence
integrity. Small misses/errors that do not alter the episode should not block
progress indefinitely. Sample4 wrong extrema and sample3 missing numerical
context remain visible residuals, not successes disguised by the added image.
Do not reopen the closed all-abstention region-exchange scorer, privilege entire
tracks/families, interpolate observations or convert a smooth source-image ridge
into physical identity. Source context supplements existing acceptance owners.

## Detector Governance

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: `RESULT-PRESENTATION` amplifies inherited wrong extrema and does not expose source appearance throughout long numeric gaps; upstream identity failures remain unresolved.
- Logic-map impact: UPDATED — source-context readout and independent static Foam gap display are registered under presentation only.
- Failure-registry impact: NONE — F09/F10 remain applicable; no new detector failure mechanism or physical-identity repair is claimed.
