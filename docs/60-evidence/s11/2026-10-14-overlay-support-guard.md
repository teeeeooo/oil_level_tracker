# Chromatic overlay support: input recovery with a sequence regression

**Local disposition: NOT ADOPTED.** B's native input is restored, but one existing
sequence integration test fails. No production merge, detector-effectiveness
acceptance, model revival or Windows PASS follows. The next permitted field work
is a diagnostic A/B comparison, with this known failure visible to the operator.

## Received role and causal evidence

The [direct reply](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-reply.json)
identifies B's removed region as a fluid–empty-space interface wobbling during
continuous inflow. It closes the regional question at source X823:848/Y215:226,
f2339/t78.044633 s. It is not all-pixel material truth, an exact contour, Foam
subtype, measured motion or permission to treat the whole sample3 window as truth.

The unchanged [component audit](../../50-diagnostics/s11/2026-10-14-overlay-component-review.md)
at `220cf1f` finds a 103×29 colorful parent reduced to a 72×7 core by horizontal
opening. The old HUD predicate tests only the core, then dilates it across valid
input. Base's actual HUD controls remain thin before opening (10–14 pixels high).

## Candidate and fixed comparison

Code/plan freeze: `0073defdd34d71c489f63acb4af574a244e7447d`.
Baseline: `747c1bccaa8dab18d6cb3a2b3dc3e549bcfc668f`.
Only `src/oil_tracker/adapters/vision/preprocessing.py` differs in production
source. The [guard](../../20-architecture/s11-chromatic-overlay-support-design.md)
requires the original connected support to satisfy the same thin/wide conditions
as its opened core. Color thresholds, dilation, saturation/caustics, Recipe,
Local XY, generators and sequence owners are unchanged.

The [paired frame readout](../../50-diagnostics/s11/2026-10-14-overlay-component-review/frames.json)
checks A/B and Base f150/151/240, including the real `detect(debug=True)` path:

| Fixed input | Baseline → candidate | Meaning |
|---|---|---|
| A upper/lower patches | 95/95 → 95/95 | Mask byte-identical |
| B upper/lower patches | 0/95 → 95/95 | 1,228 whole-ROI overlay pixels released; regional availability restored |
| Base before/at/after HUD | All three masks byte-identical | Known actual HUD suppression retained |
| Real detector vs direct preprocessing | Equal for both variants/all five frames | Normal frame entry consumes the tested mask |

Two synthetic thick-cap regressions fail on baseline and pass on candidate;
saturation, caustic and separate HUD controls remain protected. The focused
preprocessing/Oil/Foam suite passes 107 tests in 9.11 s; lifecycle/resolver/tracklet
and Foam sequence tests pass 234 in 29.30 s, initially skipping one quarantined
sample3 test. That skip was then explicitly resolved as a **candidate failure**,
not counted as a completed regression pass.

## Completed-window result and blocking failure

The existing witness/report runner executed each variant/source serially in a
fresh process, preserving all four windows and 299 rows per variant. The baseline
uses the pinned original preprocessing function at both production call sites;
all other source is identical. Local source/runtime and complete row/hash records
are retained in compressed [baseline](../../50-diagnostics/s11/2026-10-14-overlay-component-review/replay-baseline.json.gz)
and [candidate](../../50-diagnostics/s11/2026-10-14-overlay-component-review/replay-candidate.json.gz)
manifests. The same existing 13-case comparator passes without regressions;
all numeric Oil rows retain same-frame provenance. These are engineering/legacy
results, not physical accuracy acceptance.

| Source | Rows | Changed tracking rows | Oil numeric baseline → candidate | Seconds baseline → candidate |
|---|---:|---:|---:|---:|
| Base | 30 | 0 | 28 → 28 | 9.673 → 9.654 |
| sample2 | 5 | 0 | 4 → 4 | 2.102 → 2.111 |
| sample3 | 151 | 37 | 29 → 17 | 27.240 → 27.467 |
| sample4 | 113 | 0 | 101 → 101 | 17.756 → 17.755 |

Foam numeric coordinates do not change. sample3 has 4 new Oil values, 16 removed
ones and one changed Y; a lower count is neither physical improvement nor proof
of loss of correct interfaces. The [complete comparison](../../50-diagnostics/s11/2026-10-14-overlay-component-review/replay-comparison.json)
retains all changed fields and all 13 cases. Peak process RSS is at most
289,832,960 bytes; these single local pairs are not a Windows speed benchmark.

With explicit `legacy-regression` access,
`tests/test_s11_sequence_observability_integrity.py` passes on the substituted
baseline (1 test, 20.40 s) and **fails on candidate** (20.81 s). The first failing
assertion is line 110: f2413/t80.513767 s now publishes Y237 inside the historical
[37,81) barrier. The [failure log](../../50-diagnostics/s11/2026-10-14-overlay-component-review/integrity-candidate.txt)
is retained unchanged. Later assertions are not claimed to have executed.
No assertion, old `.oiltruth`, window, skip or threshold was changed to get PASS.
The entire sample3 timeline remains physically quarantined; this local failure
cannot be silently dismissed or converted into new physical labels.

Thus input availability and sequence preservation are separate outcomes. The
guard remains on an unmerged candidate branch for [Windows diagnostic comparison](../../40-operations/s11-overlay-support-windows-comparison.md).
That comparison must expose this local failure and evaluate the existing nine
reviewed private-field segments. It cannot erase the local failure or qualify
production adoption by aggregate counts. No private video was run on this Mac.

## Reproduction and retention

Use the frozen [paired plan](../../50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json)
and a fresh managed `work/` directory. At the source freeze, run:

```bash
.venv/bin/python -m tests.diagnostics.s11_overlay_mask_comparison \
  --plan docs/50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json \
  --output <work>/frames.json
.venv/bin/python -m tests.diagnostics.s11_corpus_access --purpose engineering-replay -- \
  .venv/bin/python -m tests.diagnostics.s11_overlay_mask_comparison \
  --plan docs/50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json \
  --sample sample3 --variant candidate --output <work>/sample3-candidate.json
```

Repeat the second command serially for `base_sample_1`, `sample2`, `sample3`,
`sample4`, baseline then candidate. The wrapper reuses the existing pipeline,
temporary bundle cleanup and audit helpers. Load retained gzip manifests with
`gzip.open` and pass the dictionaries to
`tests.diagnostics.s11_resolver_replacement_compare.compare` to reproduce the
13-case result. The extra `row_changes` table compares all CSV fields in order;
frame/time identities must match first. Historical qualification/causal plans
retain their old source pins and must be rerun at their matching freeze.

Managed runs: `s11-overlay-component-audit-20261014-001` and
`s11-overlay-pair-20261014-001`. Only canonical component statistics, compact full
row manifests, differences, the failing assertion and the
[verification record](../../50-diagnostics/s11/2026-10-14-overlay-component-review/verification.json)
are retained. Temporary bundles, redundant worker summaries and caches are removed
at closeout. The paired run removed 21 temporary files; the causal run removed
its one duplicate output. All 37 managed runs are closed and pass the lifecycle
check with zero errors. New reply/artifact pins, compressed 299-row/13-case
reconciliation and changed-document links pass; governance and whitespace checks
pass. The checkout has one worktree. No original video, capture bank or old frozen
evidence is deleted.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `OIL-TRACKLET`, `OIL-PROJECTION`
- Failure-registry entries: `S11-F02`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: B's valid regional input is removed by chromatic-overlay classification after opening loses parent thickness. Restoring that input also changes later sample3 Oil ownership; the exact cause of those sequence changes is not established by row counts.
- Existing feature coverage: original Recipe ellipse/margin/default settings execute; A/B/Base have empty exclusions/templates. Existing four-window sessions and static-reference preparation execute in the paired pipeline, with unchanged settings/initial-state confirmation. Local XY OFF and D2/Local XY closures are preserved; no new Artifact setup, crop or model is used.
- Execution scope: direct preprocessing and real frame detection, then original four-window analysis/resolution/report construction with serial fresh workers. sample3 is explicit engineering/legacy reproduction, not new physical scoring. No Windows or new training execution. One local sequence test fails and blocks adoption.
- Logic-map impact: UPDATED — records original connected support as an additional HUD prerequisite inside shared preprocessing; routes and independent role owners remain unchanged.
- Failure-registry impact: NONE — this scoped input/sequence tradeoff is retained as a candidate result, not a newly accepted field mechanism; current failures and no-tuning rules still apply.
