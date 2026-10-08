# D2-A1 scoped reference and measurement-footprint diagnostics

**Disposition:** bounded diagnostic implementation locally verified; no physical
classifier or detector behavior change. Candidate-owned edge comparison and
D2-B real opposing controls remain incomplete. O2 remains OPEN / FIELD FAIL.
The [machine receipt](2026-10-09-d2-reference-measurement-comparison.json) pins
inputs, runners, implementation source and local outputs against base
`bfb15cdf023ceed513180bc91ca18f9f0f2d31e1`. Live state belongs to
[Work Plan](../../00-project/work-plan.md).

## Human reference attribution received

The user answered **"모두 유리 구조·무늬"** for the previously displayed 44 s
support preview. This attributes only its 125 eligible raw Canny pixels:

- source frame 1320; half-open X[563,598), Y[816,828);
- reference crop origin (543,798), size 104×58; local review rectangle (20,18,35,12);
- reference snapshot SHA-256 `600c6bc47b2b8f5d6a3ac89e80760c5d432d9739434e9c4d48db78394d1abb80`;
- displayed mask SHA-256 `d0238a02681fae24ca4f093290ed8dee9515609e0991201add8c171a766691e8`.

The prior mixed/uncertain demo remains unchanged. A new local diagnostic recipe,
`sample/output/s11-d2-support-comparison-20261009-001/reviewed-f1320-diagnostic-only.oilrecipe`,
changes only that reference's review state. Its SHA-256 is
`0d78fc0637d860ee2802281405462ef0f476e743b9ec3213931449af1c7b2748`.
It retains the previously unpromoted registered-template geometry; this is **not
adoption of that geometry into the sample recipe**. The reply certifies neither
whole-box identity nor another frame's visibility, native path or scalar truth.

## Implementation and reuse

`artifact_reference_diagnostics.compare_reference_measurements` is a pure,
frame-local diagnostic called only by `PhaseDebugProjector.project`. It reuses
the existing reference decoder, shared reference preprocessing identity, A1
lineage and native material-path sidecar. Existing JSONL state publication stores
`artifact_reference_comparison`; no new storage or history owner is introduced.
A small separate module keeps reference asset decoding/review separate from
candidate-measurement projection.

The schema is `s11-reference-measurement-comparison-v1`. Available phase pooled
contrast windows and selected material/raster-material native contrast windows
retain exact source coordinates and original candidate indices. Native contrast
omits the center row, Sobel term and nonlocal normalization dependencies; it is
an explicitly partial footprint, not the complete score dependency mask.
Unavailable families/operations remain explicit. The module never substitutes
candidate envelopes or nearby Canny pixels for candidate-owned observed edges.

The common sampling domain intersects the explicit review scope with reference
and current effective/glare masks and current crop. It reports footprint area,
reference edges sampled/not sampled and sampling fraction. Missing common domains
have null statistics; zero edge denominators have null fractions. Raw edge
correspondence remains unavailable (`edge_overlap=null`), optical visibility is
`NOT_ESTABLISHED`, and physical/target/path/scalar decisions are `NOT_EVALUATED`.

Frame pixels/index/time, Glass geometry, preprocessing, current masks, original
candidate identity/windows and comparator version are hashed. Comparison identity
also includes snapshot, review state and rectangle. No cache or temporal alignment
is retained. Invalid binding fails closed diagnostically; no score, candidate,
matcher rejection, tracklet, phase, selector, observation or report consumes the
new namespace. Debug NONE bypasses it.

## Verification and bounded resources

The original seven focused suites passed **91 tests**. An additional distinct-
candidate permutation control passed; the final diagnostic file passes **29 tests**,
for **92 distinct passing tests** across this scope. Controls include hand-counted
sampling unions, exclusion of center rows, crop/mask censoring, zero denominators,
review-state/rectangle identity, corrupt/legacy/context mismatch, missing family
support, duplicate/permuted indices, resource exhaustion, real detector entry,
metadata neutrality and BASIC/FULL JSONL binding. Production source stayed frozen
through the real-media comparisons; the added test does not invalidate them.

Pre-implementation limits: 16 templates, 128 Oil candidates, 512 pairs, 8,388,608
compared crop pixels, 1 MiB diagnostic record, 32 MiB incremental Python allocation
and 10 ms paired median overhead for the one-reference fixture. Exceeding work
or record caps clears partial results and reports unavailable.

The saved real f1320 detector entry preserves the entire baseline detection and
all old debug state. It records 125/125 reference edges in the common domain,
17,892 output bytes and 144,768 compared crop pixels. Incremental median detector
latency is **2.829 ms** over ten alternating measured pairs after two warm-up
pairs; traced peak Python allocation is **143,050 bytes**. The old debug entry
median was 102.908 ms. Python allocation is not RSS: a separately pinned follow-up
uses the same 32 MiB envelope for three fresh-process RSS pairs. Increments are
1,064,960 / 851,968 / 819,200 bytes (PASS); raw readings and the limited
one-reference scope are preserved in the machine receipt.

| Recipe/window | Results per run | Before/after and FULL/NONE numeric/CSV equality | FULL trace byte increase |
|---|---:|---|---:|
| base_sample_1, 0–14.4 s | 30 | PASS | 19,922 |
| sample2, 0–2 s | 5 | PASS | 3,274 |
| sample3, 30.03–105 s | 151 | PASS | 101,090 |
| sample4, 0–56 s | 113 | PASS | 74,259 |
| registered diagnostic sample4, 0–56 s | 113 | PASS | 1,763,797 |

All **412 results per compared variant** retain raw/current and completed
detections, tracking fingerprint, tracking CSV and events CSV; baseline/current
FULL also retains every old debug-state field. The registered recipe is compared
against the same recipe at the baseline source, not against the unregistered
recipe. Its known 49.5/52 s regressions are consequently preserved, not fixed.
New records peak at 19,078 bytes over that sequence. Whole-process peak RSS for
baseline/current FULL registered runs is 303,841,280 / 308,559,872 bytes; the
4,718,592-byte difference is an observed process-level comparison, not isolated
allocation or a maximum-input guarantee.

The initial report harness hashed random nested `run_id`, so its report hashes
differed. Original receipts are retained. Supplemental real-pipeline runs compare
all five recipe/window reports after removing **only** that metadata field, and
also compare registered FULL/NONE reports. Normalized content and repeated numeric
fingerprints match. This is a harness correction, not detector/report repair.
The audit reuses the existing pipeline → completed resolver → bundle → CSV/report
entry; only owned immutable debug staging copies use hard links to save local
space. Timings therefore are not general bundle-I/O or Windows throughput claims.
Maximum-size/16-reference and Windows resource acceptance remain unmeasured.

## Fixed existing controls: what the numbers mean

These are reused exposed regression controls, not fresh holdout or new scalar/
path labels. The receipt verifies source frame/Glass/index/family/Y against the
pinned A1 records; reference metadata does not transfer truth to footprint pixels.

| Frame / candidate | Existing role | Available footprint | Reviewed reference edges sampled / currently eligible |
|---|---|---|---|
| 1140 / 9 | target | native contrast | 0 / 122 |
| 1200 / 4 | target | unavailable | unavailable |
| 1200 / 10 | other non-target | native contrast | 0 / 125 |
| 1260 / 4 | target | unavailable | unavailable |
| 1260 / 15 | other non-target | unavailable | unavailable |
| 1275 / 12 | target | unavailable | unavailable |
| 1320 / 9, Y844 | target | native contrast | 0 / 125 |
| 1320 / 21, Y822 | other non-target | phase contrast | 116 / 125 |
| 1485 / 19, Y836 | target | phase contrast | 19 / 109 |
| 1560 / 20, Y833 | target | phase contrast | 51 / 125 |

The 44 s pink candidate samples much of the reviewed reference region while the
orange target's selected contrast windows do not. However, the known targets at
49.5/52 s also sample reviewed structure coordinates. An any-overlap veto would
therefore remove true candidates; zero overlap also occurs on a known non-target.
These are sampling facts, not contour attribution, proof of the cause of a score,
or an operating point. No threshold is selected and no candidate is relabeled.
Four of seven targets and two of three negatives have this footprint basis;
all ten lack candidate-owned raw-edge correspondence. A registered reference
helps locate possible structural contamination but alone does not resolve it.

## Next physical checkpoint

Only two existing saved frames were reused for the next preview, with source
hashes and regression exposure frozen before display. No video or detector was
rerun to make it. The local figure is
`sample/output/s11-d2-support-comparison-20261009-001/f1275-f1320-reference-visibility.png`.
It shows original ROIs and the same half-open rectangle as an outline, without
assigning the 44 s labels to 42.5 s pixels.

**Assistant observation, not human truth:** at 42.5 s the upper repeated curves
remain visible, but the lower part around source Y824–828 meets a bright
bubble/Foam-looking region. I cannot distinguish optical overlap/obscuration
from visible glass pattern alone. Ask whether that same scope is still separately
readable, partly mixed/obscured, or unjudgeable. The previous 44 s attribution and
0/28 s reference refusals remain closed. No exact pixel relabeling is requested.

Stop for this new physical judgment under the user's instruction. A reply would
supply only one visibility-control fact, not all crossing/stationary/opposing
controls, a physical classifier or O2 acceptance. ML remains excluded; no Windows
execution or export is requested. The [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#registered-support-diagnostic-comparison--planned-contract)
and [acceptance levels](../../30-validation/s11-interface-observability-witness-validation.md#registered-support-comparison-gates)
retain the later gates.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: candidate measurement geometry does not establish which physical object produced its contrast; candidate-owned raw-edge support and current optical visibility remain missing. No new private first physical cause is established.
- Logic-map impact: UPDATED — the existing debug projector now publishes a bounded reference-versus-measurement sibling namespace; production owners and their decisions remain unchanged.
- Failure-registry impact: NONE — geometry/identity, lineage and unavailable-versus-negative failure guards are preserved; no failed mechanism is promoted or new field result claimed.
