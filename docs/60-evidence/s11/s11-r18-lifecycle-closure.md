# S11-R18 Lifecycle Closure Evidence

## Disposition

R18 passes the local implementation, checked-video, provenance, performance
and repository gates. Its status is **LOCAL PASS / WINDOWS NOT RUN**. The
frozen R17 `windows_sample1_heating_coldstart` bundle is diagnostic input, not
R18 output, and cannot qualify the field gate.

Runtime identity is `opencv-phase-detector-r18-lifecycle-closure-v1`; sequence
resolver identity is `r18-lifecycle-closure-v1`.

## Implemented replacement

The phase owner now receives `confirmed_initial_state` instead of the retired
`empty_entrance_motion_enabled` policy seam. Confirmed FULL starts behind a
coordinate-free `FILLED_BARRIER`; confirmed EMPTY retains its empty allowed-set
hard gate. An established partial fill may reverse to exactly one confirmed,
direction-compatible, material-clean drain tracklet whose current row is
physically adjacent to the last fill observation. Ambiguity remains UNKNOWN,
and neither coordinates nor observations are copied across the handoff.

Foam confirmation no longer accepts generic extent evolution or a separated
layer as independent shortcuts. It requires either directed upward source-Y
front formation or a bounded non-top stable layer. The stable compatibility
path requires three dynamic observations, except that a two-observation layer
may qualify only when both rows have a substantial area and width footprint.
This preserved the reviewed sample3 stable Foam observation without reopening
the narrow two-frame residue path.

Superseded boolean policy branches, extent-only acceptance and the
separated-layer shortcut were deleted rather than retained as fallbacks.
Candidate generation, Oil/Foam resolver ordering, same-frame projection, CSV
mapping, Artifact handling and graph behavior were not changed.

## Implementation commits

- `779115e` — R18 lifecycle-closure architecture and validation design;
- `7cbd060` — explicit Oil initial-state ownership and partial-fill drain
  reversal;
- `fcdc177` — bounded Foam-front formation and R18 runtime identity;
- `eb0ab51` — deterministic R18 four-video replay contract;
- `2b8041e` — reviewed R18 completed-window characterization fingerprint;
- `637daa5` — design/implementation contract alignment; and
- `2e663c0` — substantial two-row stable Foam compatibility with narrow-residue
  rejection.

## Automated validation

- focused Oil/Foam owner suite: 153 passed;
- detector, controlled benchmark, integration and observability suite after
  final Foam correction: 352 passed;
- canonical repository suite: 1,658 passed in 153.88 s;
- Python compilation of `src` and `tests`: passed;
- `git diff --check`: passed; and
- R17/R18 completed-window payload comparison: only the resolver-version field
  changed across diagnostics and the eleven characterized rows.

The reviewed R18 completed-window fingerprint is
`a42ab27a9bc8b0d37161bededc6859d79f4c2cac347dc171418c33c3b3fefa3b`.

## Checked four-video replay

The deterministic 2 FPS replay processed 299 rows and published 162 numeric
Oil rows. The executable gate retained 11/13 checked truth cases, 9.6364 px
numeric-only MAE, 11.9231 px coverage-adjusted MAE, 24.5 px maximum error,
zero sample3 completed-fill Oil, twelve sample3 late-drain Oil rows, eight
sample4 reviewed-range matches and exact same-frame provenance.

| Sample | Rows | Numeric Oil | Foam episodes | Tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 28 | 0 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| `sample2` | 5 | 4 | 0 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| `sample3` | 151 | 29 | 2 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| `sample4` | 113 | 101 | 1 | `0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154` |

The two existing checked-truth misses remain sample2 frame 0/Y592 and sample4
frame 0/Y860.5. R18 does not reinterpret either annotation.

Fingerprint regeneration was reviewed rather than accepted automatically.
Oil counts and checked-truth metrics are unchanged from R17-v3. Sample3 retains
its five Foam rows and two episodes, including the reviewed stable observation.
Sample4 changes from 31 to 28 Foam rows by removing the 54.5, 55.5 and 56.0 s
tail while retaining one episode. These checked videos do not provide exact
Foam-Y truth, so this is bounded regression evidence rather than a field
precision claim.

The reproducibility manifest is
`/tmp/s11-r18-verified-final/replay_manifest.json`. It is an ignored local
artifact; durable counts and hashes are recorded above and in
`tests/diagnostics/s11_r18_lifecycle_closure_replay.py`.

## Performance

An exact-clean-head profile ran at
`2e663c0345906fa1534493b82e5c9bdb5f99d650` on sample4, 0--56 s, 2 FPS,
debug disabled, official static learning and bundle output. All three runs
retained 113 rows, 101 numeric Oil and the reviewed R18 sample4 fingerprint.

| Measurement | R17 median | R18 median |
|---|---:|---:|
| End-to-end wall time | 11.666 s | 11.727 s |
| Real-time factor | 0.2083 | 0.2094 |
| Detector mean latency | 64.404 ms/frame | 64.727 ms/frame |
| Completed-window resolution | 0.1973 s | 0.2016 s |

The measured differences are approximately 0.5--2.2% and do not constitute a
material performance regression. The local manifest is
`/tmp/s11-r18-performance/performance_profile.json`.

## Remaining field gate

R18 must be replayed on Windows from this source and reviewed against all nine
canonical `WS1-*` segments. Acceptance requires BASE FULL-prefix/suffix
suppression, BASE drain ownership and rapid-refill closure, ACCUM EMPTY
suppression, ACCUM partial-fill drain ownership, Foam publication only in the
reviewed Foam-present interval, and exact Oil/Foam same-frame/CSV provenance.

Until that new bundle is reviewed, S11 remains active and R18 is not a
field-qualified detector.
