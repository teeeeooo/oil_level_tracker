# Chromatic overlay support: input recovery with a sequence regression

**Local disposition: NOT ADOPTED.** B's native input is restored, but one existing
sequence integration test fails. No production merge, detector-effectiveness
acceptance, model revival or Windows PASS follows. The
[received bundle comparison](#received-bundle-comparison--2026-10-14) reports
unchanged final tracking and different downstream interpretation. Further field
inspection uses those saved files; no new video run is requested.

## Active implementation retirement — 2026-10-14

The user explicitly requested cleanup of the unadopted branch and handoff from
main. The guard and its two candidate-only test expectations are therefore
removed from the active tree; both files are restored exactly to `747c1bc`.
The original candidate commit `0073def`, paired measurements and failed sequence
log remain immutable. This is withdrawal, not a repaired or accepted candidate.
Retained diagnostics and qualified roles are integrated separately from behavior;
the [main handoff](2026-10-14-foam-input-handoff.md) records verification and source
identity. Historical source-pinned candidate commands require their original Git
state and must not be silently repointed to restored main.

After restoration, the unchanged sequence integrity test passes **1/1 in 21.13 s**
under explicit `legacy-regression` access. The retained diagnostic and baseline
optics/Foam suites pass **254/254 in 6.67 s**. All production source and the
original optics test file are byte-identical to baseline `747c1bc`. This verifies
withdrawal and engineering preservation; the candidate's original failure and
the field FAIL remain unchanged.

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
production adoption by aggregate counts. No private video was run as part of
that local paired experiment.

## Received bundle comparison — 2026-10-14

**Scope:** user-supplied text, not locally re-read bundles or a new execution.
The user explicitly sets aside the baseline-manifest mismatch for this output
comparison. Both runs reportedly use the same 1920×1080, 23.976 fps,
98,413-frame H.264 source, byte-identical Recipe, 480–780 s at 2 Hz, compressor
start 485 s, BASE FULL / Accum EMPTY confirmations and FULL trace. The report
lists Darwin/arm64 metadata; retain that qualification limit without rejecting
the output comparison or requiring a rerun. Private files remain on Windows;
permitted text can be relayed.

| Reported result | Baseline → candidate | Supported reading |
|---|---|---|
| Tracking | 1,202 rows, all 22 non-run-ID columns equal, including flags and validity | No final-output improvement reported; internal masks/candidates are not proven equal |
| Events | 123 → 124; 117 common, 6 baseline-only, 7 candidate-only | Three Foam differences are capture numbering only |
| New event occurrences | Minimum 669.50 s; maximum 678.51 s; drop 715.51–717.01 s | Existing event types, not newly introduced definitions or new detector observations |
| BASE retrospective | ACCEPTED FULL, effective coverage 100% in both | Same reported interpretation, not proof of correct drain/refill tracking |
| Accum retrospective | ACCEPTED EMPTY / 69.88% → UNRESOLVED / 5.99%; `R17_OBSERVATION_UNAVAILABLE` | State-aware coverage changed, not a measured boundary-accuracy loss |
| Baseline Accum prefix | EMPTY through 677.01 s; appearance at 677.51 s | Conflicts with reviewed inflow from about 653 s; higher coverage is not a restoration target |
| Trace | 1,202 records, 601 per Glass; same capture reasons; 1,763 → 1,895 MB reported | File size does not establish that overlay support caused the extra 132 MB |

**User follow-up:** BASE detection also remains at **0%**, according to the
user. This is a reported operational failure, not a newly calculated per-segment
metric; this latest report supplies neither its exact numerator/denominator nor
a new trace loss analysis. Prior analyses below already identify scoped losses.
The reported failure must not be obscured by retrospective FULL coverage of
100%. BASE drain/refill requires visible Oil tracking, while its full/no-interface
prefix and suffix correctly require no boundary.

The cited 13-case PASS is the existing four-source local comparison, not new
private-field acceptance. The local sequence failure is sample3 f2413 with 37
changed tracking rows, **not** this Accum retrospective difference.

### Source-based interpretation of the difference

Read-only review at `73ad051` found the already adopted
[October 7 compatibility repair](2026-10-07-event-compatibility.md), `ccfb6fa`:
unrelated `R7_FOAM_*` flags previously selected legacy Oil handling. Restricting
that handling to actual Oil markers changes extrema/drop eligibility and
retrospective hard-barrier handling while preserving tracking samples. The
received baseline's R7-anchor explanation and candidate's unavailable barrier
are consistent with this known correction. This is a supported explanation to
check, not a verified causal attribution for the private bundles. Do not undo
that repair or call the difference an overlay-induced regression.

The current [`CsvExporter`](../../../src/oil_tracker/adapters/reporting/csv_exporter.py)
exports all 23 `TrackingSample` fields. The
[`outcome assembler`](../../../src/oil_tracker/application/services/analysis_outcome.py)
uses those samples, the Recipe and initial confirmation; no hidden candidate or
mask state enters this derivation. Identical ordered inputs under the same
outcome code produce the same semantic result apart from run identifiers. Those
outcome owners are identical in the specified local `747c1bc` / `0073def` pair.
Thus identical CSV plus different interpretation is not evidence of a mask-only
cause. This does not make a repeated baseline-manifest audit a prerequisite.

Existing event and retrospective suites pass **47 tests in 0.34 s** during this
receipt review. They verify local contracts, not private bundle contents. No
production code, threshold, Recipe, stored result or truth was changed.

### Physical acceptance and next evidence

The [reviewed source](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
remains the oracle. No per-segment numeric runs, Y direction or missing/wrong
durations were supplied in this latest comparison summary. The assessments below
apply only to that receipt; they do not supersede prior bundle investigations or
mean these segments have never been analyzed:

| Segment ID | Receipt assessment |
|---|---|
| `WS1-BASE-FULL-PREFIX` | NOT_EVALUATED; per-segment output absent |
| `WS1-BASE-DRAIN` | NOT_EVALUATED; overall coverage is not interface-tracking evidence |
| `WS1-BASE-RAPID-REFILL` | NOT_EVALUATED; per-segment output absent |
| `WS1-BASE-FULL-SUFFIX` | NOT_EVALUATED; per-segment output absent |
| `WS1-ACCUM-EMPTY` | NOT_EVALUATED; per-segment output absent |
| `WS1-ACCUM-ENTRY-SPLASH` | Tracking NOT_EVALUATED; baseline EMPTY extension conflicts with reviewed inflow |
| `WS1-ACCUM-FOAM-LAYERED` | Tracking NOT_EVALUATED; the same EMPTY extension overlaps this interval |
| `WS1-ACCUM-POST-FOAM` | NOT_EVALUATED; per-segment output absent |
| `WS1-ACCUM-DRAIN` | NOT_EVALUATED; a drop event alone cannot establish continuous tracking |

### Existing bundle-analysis reuse — planning correction

The user pointed out that substantial bundle analysis had already been completed.
Repository reconciliation confirms the following records. The preceding request
to repeat a whole-bundle nine-segment/first-loss diagnosis is withdrawn.

| Existing record | Reusable finding and limit |
|---|---|
| [R18 causal closure](../../50-diagnostics/s11/s11-r18-windows-causal-closure.md#completed-causal-observability-rerun) and [R20 consolidation](s11-r20-windows-evidence-consolidation.md#check0404a--base-release-funnel) | R18 accounts for all 1,202 rows across nine segments, with zero BASE Oil publication. R20 records direct/recovery release failures and again zero BASE drain/refill publication. These are their recorded runs, not new measurements of the October 14 candidate |
| [R22 reviewed-interface findings](../../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md#confirmed-transferred-observations) | At BASE f14386, an actual-interface candidate exists and direct initial-FULL release fails only `downward_direction`. At Accum f16280, the reviewed Y213 candidate belongs to `000388:0186` while allowed owner `000381:0181` excludes it before scoring. These are distinct recorded loss boundaries, not a complete whole-window causal proof |
| [Closed D1 reconciliation](2026-10-08-next-work-intake.md#d1-saved-record-reconciliation--closed) and [confirmed phase/owner fields](2026-10-08-next-work-intake.md#phase-and-owner-fields-confirmed) | BASE review-002 has seven `PHASE_HARD_GATE` losses; Accum review-003 has ten `OWNER_NOT_ALLOWED` losses. BASE interface idx8/9 and non-interface idx20 pass the same admission flags and face the same hard gate. D1 explicitly requires no further Windows lookup or rerun |

The known checkpoint losses constrain the existing
[physical-interface repair proposal](../../20-architecture/s11-physical-interface-evidence-repair-design.md)
and its [positive/opposition controls](../../30-validation/s11-physical-interface-evidence-repair-validation.md).
They do not establish physical identity from admission flags or justify removing
the gate. The 28 D1 pre-retention causes and the earliest physical failure over
the complete window remain unknown. Historical sparse candidate/region judgments
are not continuous exact contour truth. The
[rejected R23 polarity experiment](../../50-diagnostics/s11/s11-r23-native-polarity-rejection.md)
also remains closed; these records do not authorize its retry or a closed-model refit.

Disposition remains **NOT ADOPTED; no reported final-output gain**. The corrected
[follow-up](../../40-operations/s11-overlay-support-windows-comparison.md#5-수신-결과-이후-기존-bundle만으로-확인)
reuses these findings for the next local observation/control design under the
Work Plan, with initial-FULL admission and owner handoff as separate later
consumers. It requests no new Windows return. Further field work must identify a
specific missing fact required by that design, rather than repeat a completed audit.
Do not restore EMPTY through 677 s or relax barriers to raise coverage. The
local sample3 failure, closed model trials and deferred performance work retain
their existing dispositions.

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

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `OIL-TRACKLET`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`
- Failure-registry entries: `S11-F02`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: B's valid regional input is removed by chromatic-overlay classification after opening loses parent thickness. Restoring that input changes later sample3 ownership; its cause is not established by row counts. The received private report shows unchanged tracking and a separate interpretation difference consistent with the prior compatibility repair. Prior R22/D1 evidence already identifies BASE hard-gate and Accum allowed-owner losses at reviewed checkpoints; whole-window first physical loss remains unlocalized. This reconciliation adds no detector execution or new physical labels.
- Existing feature coverage: original Recipe ellipse/margin/default settings execute; A/B/Base have empty exclusions/templates. Four-window sessions and static preparation execute with unchanged settings/initial-state confirmation. Local XY OFF and D2/Local XY closures remain. The received private comparison reports identical Recipe/session and FULL trace with confirmed FULL/EMPTY; exact ROI/exclusion/template values are unavailable in the relayed text and are not inferred.
- Execution scope: original direct preprocessing/frame checks and four-window replay retain their frozen scope. Receipt review adds source inspection and 47 event/retrospective tests. Retirement restores baseline source, verifies 254 diagnostic/optics/Foam tests and the one existing sequence test with explicit legacy access. No new Windows/private-video/training execution or physical scoring; the failed candidate is withdrawn rather than repaired.
- Logic-map impact: UPDATED — removes the retired original-support HUD prerequisite from current execution and records restored baseline preprocessing. Existing publication/retrospective owners and downstream order remain unchanged.
- Failure-registry impact: NONE — this scoped input/sequence tradeoff is retained as a candidate result, not a newly accepted field mechanism; current failures and no-tuning rules still apply.
