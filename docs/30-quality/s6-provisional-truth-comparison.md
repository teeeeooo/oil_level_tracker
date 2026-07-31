# S6-C Agent-Assisted Provisional Truth and Diagnostic Comparison

**Workstream result:** extension repair completed on feature head; awaiting fresh exact-head audit
**Milestone:** `S6 — Real-video and Windows validation gate` remains `ACTIVE`
**Scope:** macOS source-tree, four short supporting videos, blind agent-assisted provisional truth only
**Task-start main:** `774cdda7f35a46f925d2eb1db9d9142de2aece7b` (`docs: close S6-B sample qualification`)
**Worker branch:** `feature/s6-provisional-truth-comparison`
**Next gate:** `S6-C Provisional Truth Extension Repair Fresh Exact-Head Auditor`

This evidence is a bounded diagnostic comparison. The annotations are not user-confirmed ground truth, do not replace the product `.oiltruth` workflow, and do not establish official detector accuracy.

## Blind annotation method

The Worker first verified the four video bytes, OpenCV metadata, complete sequential decode boundary and late random seeks. It then read only the videos, fixed Recipe geometry and newly extracted full-frame/ROI images. Existing detector CSV, review index, report and prior detector comparison details were not used to choose frames or assign provisional labels.

The 68-frame set was selected to cover temporal change without whole-video annotation:

| Sample | Selected frames | Selection rationale |
|---|---:|---|
| sample1 | 19 | 11 pre-overlay frames through frame 150, first-overlay frame 151, and 7 later artifact frames |
| sample2 | 9 | even coverage of the accepted fixed-geometry `0.0–2.0 s` window |
| sample3 | 24 | title/approach, fixed-window entry, fill, agitation/full-like state, drain, visible late drain, near-end reframing and decode boundary |
| sample4 | 16 | uniform `0.0–56.0 s` coverage across changing appearance in the small static glass |

Each annotation records `frame_index`, `timestamp_sec`, usability, boundary state, optional y/range, fill-state hint, foam hint, confidence and uncertainty notes. A range is preferred over an unjustified single-pixel value. Reflection, shimmer, glare, blur and overlay are never silently converted to a physical interface. sample1's post-frame-151 `High / 1/3 / Low` overlay is explicitly an artifact, not oil truth.

## Video identity and decode inspection

| Sample | Size / SHA-256 | OpenCV metadata | Sequential boundary | Key visual uncertainty |
|---|---|---|---|---|
| sample1 | `12,408,143 B` / `96cb3339cb90e8f5e7c4f71f5e5890cb12caa8996a432977413e15fe214b2c7e` | `1280×720`, `30.059287442513345 FPS`, 434 declared frames, `14.438133333 s`, H.264 | 434 decoded; last frame `433 @ 14.404865745 s` | weak fixed-looking structure and reflection before the explanatory overlay; overlay dominates afterward |
| sample2 | `1,970,224 B` / `73c6586ac167b7c6267c5729c04f05399a3fadc09852d367c49762501285634f` | `720×1280`, `30 FPS`, 288 declared frames, `9.6 s`, H.264 | 286 decoded; last frame `285 @ 9.5 s`; seeks 286–287 fail | fluorescent reflection, bubbly/condensation-like texture and handheld reframing |
| sample3 | `10,001,682 B` / `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` | `1280×720`, `29.97002997002997 FPS`, 4202 declared frames, `140.206733333 s`, H.264 | 4199 decoded; last frame `4198 @ 140.073266667 s`; seek 4198 succeeds, 4199–4201 fail | fill/agitation transitions, glare, broad interfaces, drain blur and late reframing |
| sample4 | `16,224,936 B` / `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` | `1080×1234`, `30 FPS`, 1684 declared frames, `56.133333333 s`, H.264 | 1682 decoded; last frame `1681 @ 56.033333333 s`; seeks 1682–1683 fail | only `104×104 px` Recipe ellipse diameter, soft transition and increasing yellow glare/foam-like appearance |

The declared duration is `declared_frame_count / FPS`; the last usable timestamp is `last_usable_frame_index / FPS`. The mismatch is preserved rather than normalized away.

## Annotation freeze

Blind annotation completed and the four truth files passed deterministic JSON structure/enumeration/count validation before detector output was inspected. The freeze was recorded at `2026-07-31T14:44:03+09:00`.

| Provisional truth file | Annotations | Frozen SHA-256 |
|---|---:|---|
| `sample/base_sample_1.provisional-truth.json` | 19 | `1bade0423365be7dcda710364607433c36a8fb809c925784c52e9ddf6a940dce` |
| `sample/sample2.provisional-truth.json` | 9 | `193a6c97b318b7d2f24ba8558be2429193a30b8dcab3be533e919eea87961a61` |
| `sample/sample3.provisional-truth.json` | 24 | `adb2f0cff086ec521ca11df9a1a0c4b68373436f974a1c631b01fccc6781e781` |
| `sample/sample4.provisional-truth.json` | 16 | `4d64c35b6b80b63fd928a8d9ada9a06dd5cb4dcc8e371f63e510596517213c26` |

The repository product `.oiltruth` schema is bundle-bound and represents user confirmation/correction dispositions. These artifacts therefore use a separate `.provisional-truth.json` filename contract with the explicit `agent-assisted-provisional-truth-v1` JSON schema. They do not match the product-owned `*.oiltruth` file dialog or loader. No post-freeze correction has been made.

## First audit failure and bounded repair

The first fresh exact-head audit evaluated `b4c3e693add103334aecb3f55fb023f9555fa70f` and returned `FAIL` for one persisted-contract defect: the provisional artifacts used the product-owned `.oiltruth` suffix despite carrying a separate string schema that `JsonTruthRepository` cannot load as a schema-version-1 `UserTruthSet`.

The bounded repair removes the product-owned suffix from all four provisional artifacts and names them `*.provisional-truth.json`, restoring a clear separation from product user truth. Annotation bytes, counts and frozen SHA-256 values are unchanged. The existing visual review, six detector runs and comparison evidence were not regenerated.

## Fresh detector comparison

After the freeze, six production CLI analyses were run with unchanged Recipes and production-default detector settings. All exited `0`, completed lifecycle stages `1/6–6/6`, and were reopened through `ResultBundleReader`.

| Run | CLI window / sampling | Bundle | Result | Rows / oil numeric / foam numeric |
|---|---|---|---|---:|
| sample1 pre-overlay | `0–4.990138249 s`, compressor `0`, `5 FPS` | `sample/output/s6-provisional-truth-comparison/worker-774cdda-20260731T1445/sample1-pre/oil_level_analysis_20260731_144520` | `REVIEW_REQUIRED` | `26 / 0 / 16` |
| sample1 post-overlay fresh | `5.023405837–14.438133333 s`, compressor `0`, `5 FPS` | `sample/output/s6-provisional-truth-comparison/worker-774cdda-20260731T1445/sample1-post/oil_level_analysis_20260731_144526` | `REVIEW_REQUIRED` | `48 / 0 / 0` |
| sample2 | `0–2.0 s`, compressor `0`, `2 FPS` | `sample/output/s6-provisional-truth-comparison/worker-774cdda-20260731T1445/sample2/oil_level_analysis_20260731_144528` | `REVIEW_REQUIRED` | `5 / 0 / 3` |
| sample3 full | `30.03–105.0 s`, compressor `30.03`, `2 FPS` | `sample/output/s6-provisional-truth-comparison/worker-774cdda-20260731T1445/sample3-full/oil_level_analysis_20260731_144536` | `REVIEW_REQUIRED` | `151 / 0 / 0` |
| sample3 drain fresh | `75.08–105.0 s`, compressor `75.08`, `2 FPS` | `sample/output/s6-provisional-truth-comparison/worker-774cdda-20260731T1445/sample3-drain/oil_level_analysis_20260731_144540` | `REVIEW_REQUIRED` | `61 / 0 / 0` |
| sample4 | `0–56.0 s`, compressor `0`, `2 FPS` | `sample/output/s6-provisional-truth-comparison/worker-774cdda-20260731T1445/sample4/oil_level_analysis_20260731_144546` | `FAIL` | `113 / 0 / 113` |

`oil numeric` means non-null raw oil y; smoothed oil was also null in every row of every run. `foam numeric` means non-null raw foam y. Generated bundles and CLI logs remain ignored output and are not tracked.

### Matching and diagnostic metric rules

Frozen annotations were matched to the nearest sampled detector row with at most `0.11 s` difference at 5 FPS and `0.26 s` at 2 FPS. sample2's four between-sample annotations reuse their nearest row for visual context; the table below uses the five unique detector timestamps for counts. All other listed comparisons map to distinct sampled rows. Unusable and `unclear` boundary annotations are excluded from boundary accuracy-like denominators.

- visible provisional boundary + numeric oil inside the frozen range: range hit;
- visible provisional boundary + null oil: missed-boundary suspicion;
- no-interface provisional state + numeric oil: false-positive numeric suspicion;
- null oil with `UNKNOWN_REVIEW`/invalid row: review-only behavior;
- provisional Foam `present`/`absent` versus raw Foam publication: Foam disagreement;
- provisional Foam `unclear`: excluded from Foam disagreement counts.

These are annotation-point diagnostics, not official accuracy metrics.

| Run | Comparable visible | Comparable no-interface | Oil numeric | Range hit | Visible miss | False numeric | Review-only | Foam disagreement | Disputed/unusable excluded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sample1 pre | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `5 / 7` | 11 |
| sample1 post | 0 | 0 | 0 | 0 | 0 | 0 | 0 | n/a | 8 |
| sample2 | 0 | 5 | 0 | 0 | 0 | 0 | 3 | n/a | 0 |
| sample3 full | 6 | 7 | 0 | 0 | 6 | 0 | 13 | `5 / 10` | 4 |
| sample3 drain fresh | 4 | 0 | 0 | 0 | 4 | 0 | 4 | `0 / 4` | 3 |
| sample4 | 16 | 0 | 0 | 0 | 16 | 0 | 0 | `10 / 10` | 0 |

The two sample3 runs independently agree at the four frozen visible drain points: no oil numeric, `UNKNOWN_REVIEW`, and no Foam publication. No run published a numeric oil false positive against a provisional no-interface frame.

## Sample-level diagnosis

### sample1

Pre-overlay oil behavior is appropriately non-committal for the frozen low-confidence/unclear frames: no raw or smoothed oil y was published. Five of seven provisional Foam-absent comparison points published Foam near `y=421–434`; because the frames contain weak reflections/shimmer and the provisional confidence is low, this is a false-Foam suspicion rather than a confirmed defect.

The fresh post-overlay run classified all 48 rows `UNKNOWN_REVIEW`, published neither oil nor Foam, and marked every row for review. The strong `High / 1/3 / Low` overlay therefore did not become a numeric oil boundary or stale smoothed value. `REVIEW_REQUIRED` is reasonable for this artifact-dominated window.

### sample2

All five unique sampled rows preserve null oil against the provisional full-like/no-interface state, so the strong fluorescent reflection was not promoted to numeric oil. Three rows are `UNKNOWN_REVIEW`; two later rows are `FULL_WITH_FOAM`. This supports safe oil conservatism while leaving Foam correctness inconclusive because every frozen Foam hint is `unclear`.

### sample3

The full run publishes no numeric oil across 151 rows. At six usable visible provisional points—initial/fill frames `900`, `1000` and drain frames near `2700`, `2850`, `3000`, `3147`—the detector reports `UNKNOWN_REVIEW`, producing six missed-boundary suspicions but no false numeric publication. Seven selected full-like/no-interface frames are also `UNKNOWN_REVIEW`, so the behavior is broadly over-conservative rather than selectively conservative only during blur.

The five frozen Foam-present fill/agitation points do not publish Foam; five frozen Foam-absent points also do not publish Foam. Thus the full-window Foam disagreement is `5/10`, concentrated in the visibly agitated/full-like phase. The fresh drain run reproduces the four late visible-boundary misses with no Foam disagreement and excludes the severe blur/reframing points as intended.

### sample4

All 113 rows are `FULL_WITH_FOAM`, all publish raw Foam and none publish raw or smoothed oil. At the 16 frozen visible-boundary points, oil is therefore missed. For the first ten points, where provisional Foam is `absent`, raw Foam is published at `y≈845–850`, close to or inside several frozen oil-boundary ranges. This is a strong channel-confusion suspicion: the same small-glass horizontal transition appears to be treated as Foam while oil remains ambiguous. The late six Foam hints are `unclear` and are excluded.

The `FAIL` event states `Stable recovery above zero was not detected.` It is a deterministic current Recipe judgment produced with no numeric oil publication; it is not provisional evidence that physical recovery failed. Against the frozen annotations it mainly exposes the consequence of the suspected oil/foam channel assignment and cannot be promoted to physical truth.

## Clear findings

- sample1's explanatory overlay does not become numeric oil; fresh post-overlay `REVIEW_REQUIRED` is conservative and appropriate.
- sample2's fluorescent reflection does not become numeric oil; its `REVIEW_REQUIRED` is a defensible conservative outcome.
- current behavior publishes no numeric oil in any of the six runs, so there are zero range hits and zero provisional no-interface numeric false positives.
- sample3 misses all six selected visible points in the full run and all four independently sampled visible drain points in the fresh drain run; the consistent review path is safe but over-conservative.
- sample4 consistently routes a boundary-near horizontal publication through Foam while leaving oil null; its `FAIL` must not be read as physical ground truth.

## Inconclusive findings

- sample1 pre-overlay Foam publication remains disputed because shimmer/reflection and low annotation confidence make Foam absence uncertain.
- sample2 Foam correctness is not classifiable from these frames; the frozen Foam hint is `unclear`.
- sample3's broad fill front and agitation can mix oil surface and Foam, so its initial range and Foam labels remain provisional.
- sample4's `104×104 px` diameter, glare and late yellow appearance limit separation of oil-air boundary from Foam front even though the repeated channel-confusion pattern is diagnostically strong.
- no official MAE, precision, recall, false-positive rate, false-negative rate or detector-accuracy PASS follows from this set.

## Limitations and residual scope

These machine-readable files are agent-assisted silver truth only. They were not produced or confirmed by the test owner, do not carry product user-truth dispositions, and do not replace representative user-confirmed `.oiltruth` or category-balanced accuracy evidence. Nearest-row comparison adds up to half a sampling interval of temporal uncertainty. The 68 selected points are deliberately sparse and do not describe every frame.

No detector source, threshold, dependency, test, Recipe, MP4 byte or generated output was changed or force-added. Any repair suggested by these findings requires a separately authorized Lane C owner.

S6 remains `ACTIVE`; S7 remains `PLANNED`. Windows GUI/DPI, packaging, relocation/clean-PC, Unicode/long-path, Windows file-lock/cancellation, official long-duration stability, user-confirmed truth, merge, synchronization and S6 Close remain outside this Worker.
