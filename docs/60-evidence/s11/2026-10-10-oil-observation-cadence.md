# Oil observation cadence — scoped one-second target

Date: 2026-10-10. Base: `131dae4c7a4378586caa7bc589dec2f145edc2be`.
The [user answer](../../50-diagnostics/s11/2026-10-10-temporal-usefulness-reply.json)
selects the recommended one-second Oil development target. The original
[question](../../50-diagnostics/s11/2026-10-10-temporal-usefulness-question.json)
remains byte-identical, including its historical pending status. Product §1.2
and the [validation contract](../../30-validation/s11-interface-observability-witness-validation.md#oil-observation-cadence--one-second-development-target)
now own the accepted scope. No universal classifier threshold or field acceptance
follows from this product choice.

## Saved-output measurement

The existing O1 replay snapshots provide source-time CSV rows; W3 owns physical
identity/local/scalar qualification, but its sparse candidate packets cannot
supply dense timeline coverage. The new small
[offline companion](../../../tests/diagnostics/s11_observation_cadence.py)
reuses the saved format and existing W3 I/O/hash/statistic helpers. It executes
no detector and does not change the report's two-second rendering bridge.

All four original saved streams and all 299 rows remain in the readout. These are
old recorded outputs, not fresh current-head replay equality. Finite raw Oil Y
with explicit Oil validity is counted here as **unverified numeric observation**;
it does not establish physical ownership, scalar accuracy or continuous visibility.

| Saved stream | Captured source time (s) | Numeric / all rows | Maximum numeric interval (s) | Numeric pairs over 1 s / all pairs | Leading / trailing unavailable span (s) |
|---|---|---:|---:|---:|---:|
| base_sample_1 | 0–14.4144 | 27 / 30 | 1.001 | 1 / 26 | 1.001 / 0 |
| sample2 | 0–2 | 4 / 5 | 0.5 | 0 / 3 | 0.5 / 0 |
| sample3 | 30.03–105.0049 | 29 / 151 | 46.479767 | 13 / 28 | 0 / 3.470133 |
| sample4 | 0–56 | 101 / 113 | 2.5 | 2 / 100 | 1.5 / 0 |

These whole-span numbers are neither physical PASS/FAIL nor a reason to discard
a recording. Initial no-interface, stationary, obscured and unreviewed periods
are not automatically qualified moving intervals. Base's 1.001-second pair uses
the real source times, rather than rounding to the nominal two-FPS schedule;
no tolerance was fitted after the result. One base numeric with invalid Oil
status is retained and excluded from anchors. Leading/trailing spans are censored
ends, not invented observations. All pair endpoints, per-row values and hashes
are in the [compressed full record](../../50-diagnostics/s11/2026-10-10-oil-cadence-readout.json.gz).

## Existing qualified sample4 movement

The earlier [source reply](../../50-diagnostics/s11/2026-10-07-sample4-temporal-context-human-reply.json)
already confirms one visibly continuous, rapidly moving Oil boundary from
42.5 to 44 seconds. The separate [output review](2026-10-07-sample4-interval-human-reply.json)
marks the 42.5-second completed selection correct and 44 seconds wrong.
The [newly qualified center interval](../../50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.md)
supports the existing 42.5-second Y835 observation without creating a native path.

| Source time | Stored Oil Y | Existing qualification |
|---|---:|---|
| 42.5 s / f1275 | 835 | Correct selected Oil; compatible with reviewed center interval |
| 43 s / f1290 | unavailable | No stored numeric; no new candidate/scalar truth inferred |
| 43.5 s / f1305 | unavailable | No stored numeric; no new candidate/scalar truth inferred |
| 44 s / f1320 | 822 | Already reviewed wrong Oil selection |

The numeric endpoint gap is 1.5 seconds. Once the wrong endpoint is excluded,
there is one supported observation and a **1.5-second trailing span without a
supported output**. This cannot demonstrate the one-second usefulness target;
zero usable pairs is not success. It does not measure whole-video physical
cadence or authorize a new pixel-error tolerance.

The [previous native-frame correspondence experiment](2026-10-07-a2-patch-correspondence.md)
is still closed as a general repair: one short central forward chain was human
confirmed, but other confirmed seeds/directions drifted. Its Y829/830 appearance
matches at 43/43.5 seconds are not new scalar truth, nearest-candidate identities
or production observations. Native sampling alone did not solve identity.

The next bounded causal step is to reuse the existing full-window diagnostic
capture for f1290/f1305 while retaining the seven original controls, all
candidates, actual selection layers and the complete tracking fingerprint.
This can distinguish candidate/authority/selection loss without pretending that
the cadence target supplies a new physical-selection rule. No Windows task or
repeat of the closed source questions is needed for that inspection.

## Verification and reproduction

**18 focused tests pass** in
[`test_s11_observation_cadence.py`](../../../tests/unit/test_s11_observation_cadence.py):
irregular timestamps, sampling holes with no blank rows, inclusive one-second
pairs, zero/single observation, independent Glass streams, nonfinite or broken
identities, input mutation and a real CLI under a Unicode foreign cwd. A second
stdlib readout independently joins every stored row and recomputes all source-time
intervals and exceedance counts; all 299 rows agree and four input hashes are
unchanged. No efficacy is inferred from constructed tests.

```sh
.venv/bin/python tests/diagnostics/s11_observation_cadence.py \
  --saved sample/output/s11-a1-lineage-20261007-001/candidate-base_sample_1-full.json \
  sample/output/s11-a1-lineage-20261007-001/candidate-sample2-full.json \
  sample/output/s11-a1-lineage-20261007-001/candidate-sample3-full.json \
  sample/output/s11-a1-lineage-20261007-001/candidate-sample4-full.json \
  --output /tmp/s11-cadence-new-output.json
```

Choose a new destination: overwriting is refused. The complete preflight, saved
readout and verification are retained locally in
`sample/output/s11-oil-cadence-20261010-001/` and in the compressed record.
Source videos, Recipes, frozen labels and historical 13-reference comparison
semantics remain unchanged.

## Detector Governance

- Logic-map nodes: `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F09`, `S11-F10`.
- First harmful stage: UNKNOWN for the two missing 43/43.5-second outputs; saved CSV confirms absence but supplies no first-reject predicate. The 44-second wrong-target judgment is prior human evidence, not an inferred subtype.
- Logic-map impact: NONE — the companion reads existing saved CSV rows without detector or presentation wiring; this product target cannot publish observations.
- Failure-registry impact: NONE — no identity mechanism is promoted; numeric cadence, matching continuity and rendering remain distinct from physical qualification.
