# S11-R21 Truth-Preserving Detector Repair Local Evidence

**Status:** `LOCAL PASS / WINDOWS REQUIRED`

## Scope and source identity

This record closes local validation for the R21 truth-preserving detector repair. The behavioral source base is `d50c14300b6e0d5be6c03c4487d96c4032fa7857`; the clean implementation candidate used for final replay and performance evidence is `fe6eb95120ec2016a97fff9a7d8f7ae00481f007` (`feat(detector): add R21 truth-preserving lifecycle repair`). Documentation-only closeout follows that source commit.

Runtime detector identity is `opencv-phase-detector-r21-truth-preserving-detector-repair-v1`; sequence/lifecycle resolver identity is `r21-truth-preserving-detector-repair-v1`. The nested decision-witness schema is `r21-decision-witness-v1`.

R21 keeps the established S11 publication and safety boundaries while making three bounded behavior corrections and adding behavior-neutral observability:

- initial-FULL release may use bounded recent physical tracklet trajectory without weakening the existing progress threshold or R19 absolute recovery expiry;
- DRAINING may close rapid refill through the same owner or one unique independently confirmed fresh topward owner only after the old owner is absent, without copying physical tracklet identity;
- Foam stable-layer formation restores the reviewed three-observation support with at least two dynamic observations while retaining the four-frame / 2.0-second local horizon; and
- Oil/Foam decision witnesses serialize already-computed decisions without becoming authority.

The controlled initial-EMPTY continuity case required no Accum-specific production relaxation.

## Local validation gates

All source/test gates below ran against the R21 implementation tree before documentation-only closeout.

| Gate | Result |
|---|---|
| Focused lifecycle/Foam/tracklet/resolver suite | `197 passed in 40.83s` |
| Full repository suite | `1723 passed`, `0 failed` |
| Headless Qt partition | `252 passed, 1471 deselected` |
| Python compilation | `PASS` |
| `git diff --check` | `PASS` |
| S11 detector governance from `d50c143` | `PASS` |
| Relative Markdown links | `489 checked, 0 missing` |
| Final clean-head four-video replay | exit `0`, `297.61s` |

The focused controls cover recent-vs-confirmation tracklet semantics, R20-scale slow-drain release without expiry weakening, same-owner and fresh-owner rapid refill, old-owner anti-steal, fresh-owner ambiguity, initial-EMPTY unavailable-frame continuity, Foam positive/negative witnesses, and additive Oil/Foam decision-witness serialization.

Production-source review also found no Sample3/video-specific timestamp, Glass identity, reviewed Y coordinate or R20 controlled-scale literal embedded in detector control flow. Runtime identity references are consistently R21.

## Final clean-head four-video replay

The clean `fe6eb95120ec2016a97fff9a7d8f7ae00481f007` source head was replayed with the isolated four-video harness using `--skip-fingerprint-check` so current outputs could be measured without silently replacing a historical golden. Output root: `/tmp/oil_level_tracker_r21_clean_head_replay`.

| Video | Rows | Numeric Oil | Foam episodes | Current tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 28 | 0 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| `sample2` | 5 | 4 | 0 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| `sample3` | 151 | 29 | 2 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| `sample4` | 113 | 101 | 1 | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` |

Combined checked truth remained 13 cases / 11 numeric, mean absolute error `9.6363636364 px`, maximum absolute error `24.5 px`, coverage-adjusted MAE `11.9230769231 px`, and same-frame provenance `PASS`. The only retained checked-truth misses remain Sample2 frame 0 and Sample4 frame 0.

Sample3 restored the protected early-Foam truth rather than fitting the later R21 implementation artifact. Its accepted Foam episodes are `30.530–32.532s` and `37.037–38.038s`; therefore the first accepted Foam observation remains no later than the protected `30.60s` criterion. Sample3 completed-fill Oil remains nonnumeric and late-drain numeric count remains 12.

## Sample4 fingerprint reconciliation

The checked-in `d50c143` R18/R20 replay constant for Sample4 is historical fingerprint `0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154`. The current clean R21 replay instead produced `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1`, so this delta was investigated rather than accepted as an R21 golden change.

A clean detached worktree at the unchanged source base `d50c14300b6e0d5be6c03c4487d96c4032fa7857` was run with the same current repository `.venv` and the same local Sample4 media. The historical `0f202947...` guard failed after one complete repeat because the baseline itself produced 113 rows, 101 numeric Oil rows and current fingerprint `e447626b...`.

The baseline and R21 Sample4 `tracking_data.csv` files were then compared row-by-row. All 113 rows were identical in every tracking field except the per-run `run_id`; Oil/Foam values, fill state, confidence, validity and flags were unchanged. The current local `sample4.mp4` SHA-256 is `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892`.

This establishes that the current `e447626b...` fingerprint is not caused by the R21 source delta. It does not establish whether the historical drift came from media replacement, dependency/runtime evolution or another environment difference because the historical ignored-media hash is not recorded. The historical golden was therefore **not regenerated or changed**.

## Repeated clean-head performance

R21 performance used the repository `s11_r16_performance_profile` harness on clean source head `fe6eb95120ec2016a97fff9a7d8f7ae00481f007`, debug trace `NONE`, normal static learning and official bundle output. Each sample ran three repeats with its observed numeric-count and current tracking-fingerprint guard.

| Video | Median end-to-end | Realtime factor | Median detector mean |
|---|---:|---:|---:|
| `base_sample_1` | `41.0691s` | `2.8520` | `995.264 ms/frame` |
| `sample2` | `8.8162s` | `4.4081` | `1214.772 ms/frame` |
| `sample3` | `149.3149s` | `1.9917` | `789.573 ms/frame` |
| `sample4` | `76.9104s` | `1.3734` | `478.031 ms/frame` |

All 12 R21 performance repeats retained their expected row counts, numeric counts and current fingerprints.

For direct code-delta comparison, Sample4 was also run three times from clean detached base `d50c143` under the same current Python 3.14.4 / OpenCV 4.14.0 / NumPy 2.5.1 environment and the same media, guarded with the baseline-reproduced current `e447626b...` fingerprint.

| Metric | `d50c143` baseline | R21 | Delta |
|---|---:|---:|---:|
| End-to-end | `76.8718s` | `76.9104s` | `+0.050%` |
| Realtime factor | `1.372711` | `1.373400` | `+0.050%` |
| Detector mean | `477.592 ms/frame` | `478.031 ms/frame` | `+0.092%` |
| Detect stage | `53.9679s` | `54.0175s` | `+0.092%` |
| Completed-window resolve | `1.67327s` | `1.69986s` | `+1.590%` |
| Outcome assembly | `0.15335s` | `0.15821s` | `+3.166%` |

The end-to-end and detector differences are approximately noise-scale on this host; no material R21 throughput regression is established. These measurements are comparative macOS evidence, not Windows throughput claims.

## Safety and field boundary

R21 local controls prove bounded generic behavior; they do not prove the private Windows failure had the same causal mechanism. The initial-FULL slow-drain control keeps the existing R19 absolute expiry and progress threshold. Rapid refill requires independently confirmed current evidence and cannot transfer physical tracklet identity. Initial-EMPTY continuity does not widen candidate grouping or ambiguity thresholds. Decision witnesses remain telemetry only.

No field-specific timestamp, Glass identity, reviewed coordinate, interpolation, backfill or report-side repair was introduced. No protected Foam oracle was weakened and no historical tracking golden was regenerated.

The latest Windows disposition remains `FIELD FAIL`. Canonical Windows replay against the reviewed Base/Accum truth is the outstanding field gate; local R21 success must not be promoted to field PASS.

## History Review

- Logic-map nodes reviewed/updated: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `FOAM-EPISODE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries reviewed: `S11-F02` through `S11-F10` as applicable to R21 authority, lifecycle, Foam, provenance and field-effectiveness boundaries.
- Preserved mechanisms: coordinate-free initial FULL/EMPTY safety, bounded R19 recovery expiry, R20 delayed readiness, distinct physical ownership, material/ambiguity fail-closed behavior, selected same-frame publication and independent Foam composition.
- Rejected mechanisms: global threshold/entrance widening, slow-drain expiry weakening without causal proof, video/time/Y-specific branches, snapshot carry, identity merge across rapid refill, report-side repair and moving the Sample3 Foam oracle to the later 37-second episode.
- Difference from predecessor failures: R21 changes only explicit bounded recent trajectory/refill/Foam witness semantics and additive diagnostics; Windows effectiveness remains deliberately unclaimed.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `FOAM-EPISODE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: local R21 controls address bounded initial-FULL release, drain-to-refill closure and Foam formation at their existing lifecycle/episode owners; the first harmful stage in the private Windows Base/Accum failure remains unproven until deliberate field replay.
- Logic-map impact: `UPDATED — the current map records R21 recent trajectory, rapid-refill phase handoff, corrected Foam stable support and decision-witness telemetry without changing publication authority.`
- Failure-registry impact: `UPDATED — R21 is recorded as the locally validated candidate while predecessor failures and the field FAIL boundary remain preserved.`

## Remaining gate

After normal publication of the locally accepted candidate, the next material S11 transition is deliberate target-Windows qualification using the canonical reviewed truth and Windows procedure. If that replay remains `FIELD FAIL`, a subsequent revision must begin from newly observed physical-stage evidence rather than synthetic success alone.
