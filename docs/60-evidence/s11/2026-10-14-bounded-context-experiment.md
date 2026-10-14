# S11 bounded context experiment — 2026-10-14

Base HEAD: `7a57064046b0c650f552f6e4d9e2ceb73002972f`.
Current-state owner: [Work Plan](../../00-project/work-plan.md).
User objective: finish detector work within 3–4 work rounds; evaluate whether reports communicate Oil/Foam movement, not perfect point detection.

## Frozen question before execution

DTO-1: Does a seed-free, illumination-order-invariant temporal texture observation provide useful upper/lower role information missing from static native inputs?
At each raw ROI pixel, measure changes of eight ternary neighbour-order relations across exactly 13 consecutive frames ending at each of the eight existing corpus frames. No fitted parameters, brightness/Canny threshold, optical-flow matching, interpolation or new physical labels.
For an existing path, use its original 7×7 upper/lower sampling centers. Score is lower-side mean turnover minus upper-side mean turnover. Higher score is the fixed Foam-upper ordering hypothesis. The static ordinal-complexity difference is an ablation only, not a revived classifier.
For raw coverage, retain the full center-column score distribution independently of Canny/white seeds. The marked base region is a regional availability check, not exact-path success.

Population: complete 109-path corpus plus 26-path and two-path immutable extensions (137 paths, 19 qualified, 118 unknown). Five recording hashes, eight source frames. Decode 13 trailing frames per anchor; verify final ROI against the pinned saved original. No sample3 decoding, new clips, model restoration, fitting or production behavior change.
Comparison: keep all available and unavailable subjects. Evaluate all same-frame qualified upper-versus-internal/rim orders, plus N3 versus N5 as an explicitly cross-time opposition. Report N1 disjunction and liquid contacts separately. Do not count correlated paths as independent sources or missing support as a correct rejection.
Synthetic controls: constant image, positive affine brightness change without clipping, static translated texture, and static nonrigid optical warp. A nonzero dynamic response on a structure falsifies standalone physical authority, regardless of real ordering successes.
Decision: useful local ordering may justify further observation research, not production. Failure over multiple scene types closes this fixed family without threshold/window/scale retries. An isolated failed point does not itself establish a report-level blocker.
Resources: CPU only, 104 requested decoded frames, <1 GB peak RSS, <120 seconds probe time, 20 MB scratch and 2 MB retained machine evidence; dense stacks released after each anchor.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: existing base f144 upper loss is before material components; DTO-1 tests raw temporal information, not a demonstrated Windows or episode repair.
- Existing feature coverage: unchanged existing source crops and native side supports; current-frame side eligibility remains the old qualified support. Raw temporal calculation deliberately bypasses material/Canny seeds, learned static maps, Artifact templates and session state. It does not establish effective-mask validity across past frames. Local XY stays OFF; retired overlay and model trials stay closed.
- Execution scope: diagnostic-only raw-video context and saved path sampling; no current detector winner, completed resolver, CSV/report publication, model fit or Windows execution. Original source hashes and anchor raster equality are required. Canonical Windows evidence is reused separately at its saved scope.
- Logic-map impact: NONE — new diagnostic has no production caller and does not change setup, ownership or publication.
- Failure-registry impact: NONE — explicitly tests the known motion/optical-warp ambiguity rather than granting temporal activity identity authority.

## Executed result and disposition

DTO-1 executed once, with no parameter revision. The full 137-path population was preserved: 19 qualified, 118 unknown; 101 input-available and 36 unavailable. Five recording hashes / eight anchor frames supplied 104 decoded source frames. Each anchor ROI matched its previously saved RGB pixels byte for byte. Thirteen frames mean different time spans at different source rates; this trial does not establish sampling-rate invariance or independent filming sessions.

| Frozen comparison | Temporal ordinal turnover | Static ordinal ablation | Interpretation |
|---|---:|---:|---|
| Sample4 N3 versus internal N4 | 1/1 | 1/1 | Local true-upper ordering preserved |
| Sample4 N3 versus rim N5, different times | 1/1 | 1/1 | Cross-time opposition, not an independent recording |
| Public compressor, four upper paths versus three rim paths | 12/12 | 9/12 | All comparisons come from one frame; not twelve independent successes |
| Milk bubble versus two cup rims | 0/2 | 1/2 | Required local upper-role ordering fails |
| Total diagnostic orders | 14/16 | 12/16 | Not precision/recall, whole-video effectiveness or report acceptance |

Water N1 (Foam/liquid disjunction) scores 0.166412 versus internal N2 0.026300; the disjunction is retained, not counted as a certain Foam success. The public liquid-upper contact scores 0.177147, above every certain Foam-upper score in this trial. Temporal activity is therefore not an Oil/Foam role separator. Other liquid-contact scores remain in the complete readout rather than becoming negative labels.

At local base f144, all 16 inspected center rows Y365–380 now have finite raw temporal values despite missing old seeds. Around the regional marked upper Y367–370 the score is negative (about -0.015094 to -0.003614); it turns positive lower down. This is raw availability, **not recovery of the marked upper**, a selected contour or a physical accuracy result. No maximum, threshold or nearest path was selected.

Both constant and non-clipping positive-affine brightness controls return zero. Static texture translated within the lower half returns +0.528486; a static texture under nonrigid optical warp returns +0.326743. Both exceed the real upper scores. These counterexamples disprove using DTO-1 alone as material/upper-boundary authority. The milk miss alone is not treated as a report-level veto; the authority ambiguity, unresolved seed-free physical path, and absence of integrated report benefit prevent promotion.

**Disposition: raw observation implemented and locally useful ordering demonstrated; NO PRODUCTION PROMOTION.** Keep the diagnostic result. Do not tune its window, cutoff, scale, or add a second head to rescue this fixed experiment. No claim that all temporal representations are impossible follows. No new detector version, learned model, mask change, candidate acceptance, episode relaxation or Windows run was introduced.

## Independent checks and resources

The probe took **6.5757 s**, including the source-pin reads and decoding in its timed body; imports are excluded. Peak process RSS on Darwin was **264,962,048 bytes**. This is a diagnostic workload, not product throughput or a projected Windows performance result.

A separate verifier decoded the same 104 frames again, recomputed ternary changes through independent integer comparisons/accumulation and independently sampled every original side and all **3,298 center rows**. All **137 subjects** and source hashes/timestamps matched; maximum absolute arithmetic difference was **5.551115123125783e-17**. Total decoding was 104 probe + 104 verification executions, not 208 distinct frames. No new temporal window or parameter was selected during verification.

**65 tests passed in 15.82 s**: the 17 new ordinal-contract tests plus the existing geometry, Foam component diagnostics and Foam evidence tests. The earlier 17-test standalone run is a subset, not an extra 17 distinct tests. No full canonical, Qt, completed-sequence or Windows acceptance run is claimed. Production `src/` is unchanged from the starting main.

## Mac / Windows evidence coverage and project implications

This review follows the current source/truth owners and retained counterexamples, rather than replaying every historical experiment. It does not claim to have watched every full recording or accessed private Windows pixels.

| Source family | Reused scope; new execution |
|---|---|
| Local base_sample_1 | f144 lower/upper replies and raw-stage proof; new 13-frame DTO window and independent verification. Never equate it with Windows BASE |
| Sample2 | Existing early Oil/Foam, reflection and reframing qualifications; no new decode or new scalar truth |
| Sample3 | Existing A/B, C/D, overlay failure and quarantine; no new decode, mining or accuracy claim |
| Sample4 | Existing wrong extrema, real rapid movement, true Foam upper, internal/rim/lower-contact controls; three new DTO windows |
| Water / sample5 | Existing inclined, entry, Foam/liquid and no-Foam qualifications; two new DTO windows |
| Beer / sample6 | Existing front/back single-layer and cropped-upper limits; no new labels or decode |
| Milk / sample7 | Existing confirmed large bubble and cup-rim opposition; one new DTO window |
| Public Miso compressor | Existing four upper and rim/contact roles; one new DTO window |
| Public Cold117 source | Existing still-frame uncertainty retained; no blanket exclusion or new label |
| Private Windows evidence | Canonical nine-segment behavior; completed R18/R20/R22/D1 findings and latest comparison receipt reused. No private-video access or new Windows execution |

The [existing Windows reconciliation](2026-10-14-overlay-support-guard.md#existing-bundle-analysis-reuse--planning-correction) already locates BASE hard-gate and Accum allowed-owner losses at reviewed checkpoints. Removing those gates is not justified: BASE positive and non-interface rows share the relevant admission flags. The latest 1,202-row comparison and 69.88% to 5.99% interpretation change are not DTO results, and do not prove overlay causality. Keep Darwin metadata distinct from target-Windows qualification and do not request a redundant bundle audit.

The [saved report audit](2026-10-13-program-review-intake.md#이번에-실제-확인한-범위) already shows wrong targets selected as the 42 s minimum and 44 s maximum in sample4. Those can distort the reported movement story; raising numeric coverage cannot solve that. Foam's raw upper miss is a separate failure, not evidence to loosen episode formation. These existing integrated findings have higher completion priority than another isolated path label.

## Reproduction and handoff

Canonical local run: `sample/output/s11-dto1-20261014-001`. Its `.artifact-run.json` pins the original preflight, 16 inputs and the probe/runner. `evidence/readout.json` retains the complete maps-as-profiles, 137 subjects, comparisons, source receipts and synthetic controls; `evidence/verification.json` retains independent arithmetic. The first 4,071 UTF-8 bytes of this document preserve the exact pre-execution text (SHA-256 `a7e2c86559a2f0e518f4cbaaaa2ab713b840e90b91dd9b13881054e53f91abff`); the lifecycle guard rejected a duplicate preflight copy, so it is discarded rather than retained again.

Code: `tests/diagnostics/s11_dense_temporal_role_probe.py`, `s11_dense_temporal_role_run.py`, `s11_dense_temporal_role_verify.py`; tests: `tests/test_s11_dense_temporal_role_probe.py`. The runner uses the Mac research environment and saved ignored local videos/PNGs. A GitHub source ZIP alone does not contain those inputs; this is not a Windows operator command.

For an explicitly necessary reproduction, create a fresh managed run using the original manifest's purpose/inputs/sources/parameters and budgets; compare all frozen input and code SHA values first. Run `.venv/bin/python -B tests/diagnostics/s11_dense_temporal_role_run.py --work <new-managed-work>`, then `.venv/bin/python -B tests/diagnostics/s11_dense_temporal_role_verify.py --readout <new-managed-work>/readout.json --output <new-managed-work>/verification.json`. Both outputs refuse overwrite. Repetition is not the next product task; reuse this completed result.

The [Work Plan](../../00-project/work-plan.md#bounded-completion-budget--2026-10-14) owns the user-requested 3–4-round completion budget. Existing O2/V5, behavior, Windows and report acceptance contracts remain intact. This evidence records no formal S11 completion or supported-domain reduction.
