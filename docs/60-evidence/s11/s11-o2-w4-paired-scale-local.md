# S11 O2 W4 — paired-scale local comparison preparation

Date: 2026-10-01. Base: `57b39dcc29df4c40d2b35470f81fdcae22031ef2`.
Scope: one offline local-position aggregation experiment, prepared for Windows.
No private packets, new labels, detector replay or production changes were used.
The two original audit specifications are preserved. FIELD FAIL is unchanged.

[Specification](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md#w4-paired-scale-local-comparison),
[architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#w4-paired-scale-comparator-boundary),
[validation](../../30-validation/s11-interface-observability-witness-validation.md#w4-paired-scale-controls),
[Windows procedure](../../40-operations/s11-o2-local-shadow-evaluation.md#w4-paired-scale--기존-라벨-실행)
and [live status](../../00-project/work-plan.md#s11-work-item-ledger) retain their separate owners.

## Decision and implementation

W3 established context availability, not a candidate-identity discriminator.
Material direction varies and zero static/glare overlaps both identities. A new
partial-support/opposition identity formula is not justified by that evidence.
The narrower fixed-score loss already observed is separable: two scales favored
the near point, while independently taken point medians chose a reversed scale.

The existing experiment runner now compares median paired score differences with
independent medians on identical jointly available widths and exact same-X points.
It preserves C/A/L, geometry, all v1 scores, candidate identity and scalar outputs.
Legacy support-to-intersection changes are separately exposed. Human labels choose
comparison pairs only. No source/Glass/frame/coordinate-specific score branches,
new descriptor, fitted coefficient, threshold or classifier was added.

The synthetic positive repairs a reversal; its inverse exposes a regression.
A three-point cycle explicitly defeats any inference of a total candidate rank.
These controls show that the mechanism is an experiment, not an accepted fix.
W1 candidate-identity pooling and O2 acceptance remain open. A private local-order
benefit would not close them or authorize W5 phase/association changes.

## Verification

**233 distinct tests passed**, including **21 new paired-scale controls**.
The integration group below passed 221 tests in 8.19 s:

```sh
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_paired_scale.py \
  tests/unit/test_s11_shadow_experiment.py \
  tests/unit/test_s11_identity_profile.py \
  tests/unit/test_s11_shadow_targets.py \
  tests/unit/test_s11_review_semantics.py \
  tests/unit/test_s11_review_records.py \
  tests/unit/test_interface_shadow_evaluation.py \
  tests/unit/test_oil_interface_witness.py
```

After adding the declared rejection rule to artifact/summary metadata, a focused
run of `test_s11_paired_scale.py` plus `test_s11_target_aggregation_contract.py`
passed **33 tests in 0.55 s** (21 paired tests repeated, 12 W1 controls additional). A final Markdown table
layout repair was followed by **21 paired tests passing in 0.36 s**, including
the actual CLI and generated-output receipt check.

Controls cover repaired and new reversals, ties/zero/null, exact shared widths,
permutations, duplicate/mismatched geometry rejection, support loss, metadata
blindness, pair cycles, target/basis separation and unknown-label preservation.
The actual Python CLI ran outside repo cwd using Korean/spaced paths and validated
reference equality, unchanged inputs, output receipt hashes and no overwrite.
Reference drift and incompatible modes fail before publication. No private efficacy
or Windows platform PASS is inferred from this local entry-path test.

| Checked identity | SHA-256 |
|---|---|
| `s11_shadow_experiment.py` | `b6afbf86718742e27cac02dda60f5dbcd9b76ad6c8ea35adeb3b1bd1398e4645` |
| Paired-scale artifact | `b4503f39d31a733c0821c677c581098a9fdb5b6273e6af6d5e0544ee3104ba5d` |

S11 governance, **133 changed-document relative links/anchors** and
`git diff --check` passed. Direct changed-scope review confirmed unchanged
production source, original audit specifications and evaluator behavior. Full detector/Qt/video/performance requalification
is outside this offline aggregation change; mapped production behavior is unchanged.

## Windows boundary and result decision

Run only `--paired-scale` with active revisions 3/14/4 and the original fixed-score
v1 reference. No 1.85 GB debug trace, video, W3 rerun, freeze or new labels are needed.
Return generated summary and COMPLETE/reference/output/input verification. Native
same-X interface location is primary, non-interface same-X is a separate control;
candidate centers remain separate. All changed pairs and scale support counts
must be read, not just the motivating BASE win. No primary net gain or any native
negative-control regression rejects replacement on these controls. Zero-pair cases
cannot establish success. Windows efficacy is pending.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: independent scale reduction can reverse a local score ordering; the physical identity and production rejection causes remain unresolved. Paired reduction itself can regress and cycle.
- Logic-map impact: NONE — existing offline score/pair orchestration is extended; production candidates, temporal logic, selection and publication are untouched.
- Failure-registry impact: NONE — explicit controls preserve local-edge-versus-identity distinctions and do not claim calibrated field repair.
