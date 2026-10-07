# Episode source review and detector hypothesis validation — 2026-10-08

## Scope and disposition

The unit of value is whether a report conveys consequential Oil/interface and
Foam movement, order and uncertainty. Perfect per-frame detection is not required.
The [Work Plan](../../00-project/work-plan.md) retains current gates and authority.
The [design](../../20-architecture/s11-episode-source-review-design.md) defines this
bounded implementation; this evidence does not supersede prior accepted work.

Base main: `a5cbf65f44cb2f6c3ff2c2de610bf89eb92467b7`.
Frozen final code: `52003aaa2f9e66e2a85dd8c485fdcf4ba5713b22`.
Branch: `work/s11-episode-texture-20261008`.
Native evidence: `sample/output/s11-episode-texture-20261008-001/`.
Main has not adopted this branch. Production detector behavior is unchanged.
Report implementation is locally verified at the scopes below; independent user
comprehension is NOT_EVALUATED. Windows remains FIELD FAIL, and O2/W4 remain OPEN.
The side-texture diagnostic is CLOSED WITHOUT PROMOTION.

## Implemented report behavior

Each Glass receives at most four source-review windows: the longest internal Oil
observation gap (or a whole-window insufficient-observation context), extrema
plus/minus two seconds, and the longest reported Foam episode. Overlapping extrema
merge; broad gap/Foam context stays separate to preserve a higher-cadence zoom.
The report never interprets absent Foam numbers as proof of physical absence.
Manual previous/next, slider and keyboard navigation use original-frame crops;
there is no autoplay, interpolated trajectory, synthetic Oil guide or new event.

Each window has at most 240 samples at native-or-slower cadence. The ellipse's
bounding rectangle retains rim/reflection evidence. Large crops are downscaled
only, to a 192-pixel maximum dimension; native small crops are not resampled.
Lossless local PNG sprite pages contain at most 40 tiles. JSON records actual
frame identity/time, requested time, crop, resize, sample spacing and unavailable
slots. Missing, duplicate, mistimed or geometry-changing frames stay unavailable;
a stale asynchronous image cannot repaint a missing slot. Cancellation aborts
the transactional bundle. Source-open failure leaves an honest unavailable card.
The HTML labels extrema as detector observations, not certified physical extrema.
Explicit Jinja escaping fixes the existing `.html.j2` suffix detection gap.

The first real-report run exposed repeated random-seek cost. A report-only sampler
now seeks at entry/large jumps and decodes nearby frames sequentially, with a
32-advance budget per requested sample. A 46.48-second gap probe retained 240/240
frames with one seek and 1,393 sequential reads in 11.89 seconds under local load.
Whole-run times are not an isolated repeated performance benchmark.
An independent pixel audit then exposed the inherited valid-zero timestamp fallback.
The report-only reader now preserves backend 0 ms instead of substituting the
request. The shared detector reader remains byte-identical to baseline.

## Real-video and browser verification

Three frozen revisions each ran all four official application/report windows (12 runs this task). The final four match the prior baseline and first revision.

| Sample | Rows | Numeric Oil | Numeric Foam | Review windows | Source frames |
|---|---:|---:|---:|---:|---:|
| base_sample_1 | 30 | 28 | 0 | 1 | 181 |
| sample2 | 5 | 4 | 0 | 1 | 61 |
| sample3 | 151 | 29 | 5 | 4 | 600 |
| sample4 | 113 | 101 | 26 | 3 | 497 |

All 299 tracking rows and event records are unchanged; CSV ignores only run_id. All 1339 source-frame samples pass metadata checks. Independent ordinal decoding verifies 27 selected source tiles pixel-for-pixel. All 95 unique per-bundle HTML/metadata/sprite links resolve. These counts measure integrity and regression, NOT detection recall.


The previous exact-src baseline is the four final reports under
`sample/output/s11-context-validation-20261007-001/final/`; its `src` Git tree is
identical to this task's original main `src` tree. Comparison covers every row,
value, flag, validity and event, not just aggregate counts. Source media, recipes
and truth files are pinned independently and unchanged.

Browser checks use actual file-protocol reports with normal security settings.
Rendered canvas screenshots are compared externally with expected sprite pixels.
Desktop and mobile layouts, buttons, keyboard navigation, no-JavaScript fallback,
missing-frame blanking and stale-load protection are exercised. Successful checks
record no external report requests and no JavaScript exceptions. These are local
Chrome checks, not Windows qualification or independent comprehension measurement.
Source crops and earlier raw-source contact sheets were also visually inspected.

## Separate detector experiment: fixed side-texture persistence

The diagnostic measures rotation-invariant local texture arrangements at two
radii. It is not a retuning of existing brightness/edge scores or the closed A2
raw-region model. Cross-side differences are compared with within-side near/far
variation on recorded native-path geometry. Missing bands remain absent.
Three distinct supported sectors are required. Source family, authority, selected
track, reviewed Y, target label and time do not enter the classifier.
The implementation and rule were frozen before real measurement.

All 153 bound candidates were predicted, then evaluated through the existing W3
exploratory evaluator with original labels: 150 UNRESOLVED, three supported.
None of the seven confirmed Oil targets or four protected correct selections is
supported. The three reviewed wrong targets also abstain; this is not rejection
as a positively identified artifact. The three supported candidates are unreviewed.

For the fixed three-sector rule, all three paired true candidates have a lower
third-largest sector margin than their wrong alternative:

| Frame | True margin | Wrong margin |
|---|---:|---:|
| 1200 | -0.106180 | -0.015066 |
| 1260 | -0.122299 | -0.105992 |
| 1320 | -0.053670 | -0.043954 |

Any common threshold admitting those true candidates also admits their paired
wrong candidates. This ordering check did not change the operating point.
Static textured optical half-planes remain an explicit appearance collision.
The model is CLOSED WITHOUT PROMOTION; do not resume it by lowering thresholds.
This is a bounded model failure, not a claim that detector improvement is impossible.
Production detector behavior and W3 labels were not changed.

## Sample3 whole-episode detector audit

Observer-only serialization surrounds the unchanged sequence resolver and returns
its original object. The complete 30.03–105-second run has 151 rows, 29 numeric Oil
observations and 122 UNKNOWN rows. Its final tracking fingerprint matches the
ordinary application run. These are output counts, not physical detection accuracy.

The longest adjacent-numeric interval is 34.5345–81.014267 seconds (46.479767 s),
with 92 missing rows. Of these, 89 have at least one internally publishable row
before final selection. That internal designation does NOT prove physical Oil.
Phase reasons are FILLED_CAP_VETO in 87 rows, FILL_MOTION_OWNER in four and
FILL_SPAN_MATERIAL_VETO in one. Three rows have no publishable row, three have
owner-bounded exclusion and 86 reach another final abstention.

Thus simply generating more boundaries is not an adequate explanation or repair.
The next detector investigation should target whole-episode phase/ownership and
interface reappearance using positive and negative controls, not disable filled-cap
protection or promote every rejected candidate. The current audit is diagnostic,
not authorization to bypass O2/O3 entry or proof that the guard itself is wrong.

## Automated validation and retained failed attempts

Final source `52003aaa2f9e66e2a85dd8c485fdcf4ba5713b22`: **2,488 passed**, including **254 Qt** and **2,234 non-Qt** cases. Exact node-ID reconciliation has no missing, duplicate, skipped, unexpected or failed cases. Four non-Qt file shards and a separate Qt run cover the complete canonical inventory. The earlier feature and performance revisions independently passed 2,482 and 2,486 cases. After the timestamp repair, 105 focused cases passed before final complete enumeration. A passing local Qt run does not close historical intermittent A0Q or Windows stability.

The first focused command used a nonexistent test path and collected no tests;
the corrected command and later canonical enumeration include the actual policy
module. The first browser QA attempted forbidden pixel reads from a local-file
canvas; the working QA uses browser screenshots without changing browser security.
The first independent pixel reference used timestamp seeking and landed one frame
later at an NTSC boundary. Independent sequential ordinal decoding replaced that
reference method. It then found the actual-zero metadata defect, which was fixed
in the report reader and covered by focused and final regression reruns.
All failed logs are retained; none is counted as PASS or silently overwritten.

## Residuals and next transition

The new report makes raw movement review available inside the report itself; it
does not repair sample4's wrong numerical extrema, fill sample3's numerical gap,
or prove that users interpret every episode correctly. No smooth source-image
ridge, appearance score or movement cue is promoted to physical Oil/Foam identity.
Raw and numerical layers remain explicitly separate. Local small misses that do
not change episode interpretation should not create an endless acceptance loop.

Next use consequential episodes to check direction/order, Oil/Foam separation,
misleading extrema, sustained wrong paths and honest uncertainty. Independent
comprehension remains a separate, unmeasured acceptance axis. The current source
videos are exposed development/regression material, not a held-out efficacy set.
All private Windows canonical segments remain NOT_EVALUATED in this session;
FIELD FAIL and historical A0Q stability uncertainty remain in force.

Reproduction and exact hashes are in the companion JSON. Native report bundles,
source measurements, W3 output, test inventories, traces and browser screenshots
remain under the evidence root. No raw video or browser profile is committed.
The three implementation commits separate the feature, decode scheduling and
actual-zero timestamp repair; the final documentation commit changes no code.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: inherited identity/publication failures create wrong extrema and long numerical gaps; presentation amplifies them without episode source evidence. Sample3's detailed final-stage audit is observational, not a new physical-cause claim.
- Logic-map impact: UPDATED — bounded source-frame review is registered under presentation only; production detector control flow is unchanged.
- Failure-registry impact: NONE — existing guards remain applicable; no new physical-identity mechanism is adopted.
