# S6-D1 Mobile-Assisted User-Truth Review Pack

## Status

- **Feature branch:** `feature/s6-d1-mobile-truth-review-pack`
- **Starting production main:** `0f0bf705795ebedc9210c9731e486b194ecded09`
- **Starting commit:** `docs: close S6-E bounded runtime soak screening`
- **Feature-head result:** `S6-D1 REVIEW PACK: PREPARED — USER CONFIRMATION PENDING`
- **Current gate:** `S6-D1 Mobile-Assisted User-Truth Review Pack Fresh Exact-Head Auditor`
- **Next external checkpoint after audit and merge:** `S6-D1 Domain-Owner Mobile Review`
- **Product truth state:** no `.oiltruth` exists or was created
- **Milestone state:** S6 remains `ACTIVE`; S6-D official accuracy remains pending; S7 remains `PLANNED`

This evidence preserves a bounded mobile review pack for 15 decisive frames from four repository samples. It binds every item to a fresh production bundle, exact run ID, exact decoded frame, Glass ID, Recipe identity and source identity. The pack contains agent candidates only. It does not contain user-confirmed truth, product `.oiltruth`, official detector-accuracy metrics or an accuracy PASS.

## Authority boundary

The product truth contract was reviewed directly in `domain/user_truth.py`, `application/services/user_truth.py`, `json_truth_repository.py`, the truth annotation UI owners and their tests. Product truth requires explicit user disposition (`confirmed_correct`, `corrected` or `unusable`) and strict bundle binding through run ID, Recipe ID/hash and source resolution.

This Worker therefore produced only:

- `review-candidates.json` with schema `s6-d1-mobile-review-candidates-v1`;
- clean and comparison PNGs;
- sample contact sheets;
- a mobile questionnaire and plain-text response template;
- bundle and category inspection summaries;
- a complete local SHA-256 manifest;
- an optional mobile ZIP.

No output uses `.oiltruth`, `.provisional-truth.json` or another product-loader suffix. Candidate coordinates are not accepted dispositions. Existing sample3/sample4 domain-owner statements guide physical interpretation but do not establish exact pixel coordinates or bundle-bound product truth.

## Local-only evidence identity

```text
sample/output/s6-d1-mobile-truth-review-pack/worker-0f0bf70-20260731T151330Z/
```

The complete root remains ignored by the existing `sample/output/` rule and is not committed.

| Principal artifact | SHA-256 |
|---|---|
| `build_review_pack.py` | `0c6e00ce95ac4ddb0584ed6f3bb42f155d5cd57813b5db17b6842b3c80b4a883` |
| `finalize_review_pack.py` | `fbc120ae9ad525fd09a14ce0c2727800d282813d6e3a13da948f534d97b1f313` |
| `review-candidates.json` | `2dcf7190fd143716045ed6cddc7f2d166fd07d46c7819a84691d477094e67aee` |
| `mobile-review-questionnaire.md` | `0d1fd0baa8271e093e1908087b9cb0f2ab2fc372ae0a0cf987d088530218f0ca` |
| `review-response-template.md` | `ac88968b7f1cb6e31649317b6030b2f5e2b7990af55ee3450d427b05695c7b69` |
| `pack-summary.json` | `da4f9c2759ceeccbf0441d1e8c22a02539be0cf2e9842ae520cacb1027d644c5` |
| `sha256-manifest.json` | `2b723181ea22284f804d1d613cc7c1fb4bddd17a8c7d427ce9fd4f12b06a854d` |
| `s6-d1-mobile-review-pack.zip` | `fd06ce5e464f6a9f0ec3a72d4c0c1be047b715721fb28ce0ef93a76ccb350855` |

The complete SHA manifest contains 150 local files and excludes only itself to avoid recursive self-hashing. Every listed size and digest was recomputed successfully after finalization. The ZIP contains 39 mobile-review files and no product or provisional truth suffix.

## Fresh production bundle baseline

All four runs used unchanged production CLI source, tracked Recipes, production-default detector settings and fresh output directories. Runs were sequential and all completed lifecycle `1/6–6/6` with exit code `0`. Detector result labels are recorded as context only.

| Sample | Source window / sampling | Run ID | Tracking rows | Detector label | Bundle tree SHA-256 |
|---|---|---|---:|---|---|
| sample1 | full usable `0.0–14.404865745 s` / `5.0 FPS` | `bbf0f0d6-e8b6-4c52-b15b-ff48a402a75e` | 73 | `REVIEW_REQUIRED` | `406eba3b7a01c9a4595d4fa42e5e8573d1922315bfa0f5f8cc78be880298e64f` |
| sample2 | accepted stable `0.0–2.0 s` / `2.0 FPS` | `1369af1a-9e41-4f85-bfc7-a43d344436c0` | 5 | `REVIEW_REQUIRED` | `b4367aed3e59cb48aeb1e8747124554c6019494ca282077b59e5d3e5a65f1466` |
| sample3 | accepted `30.03–105.0 s` / `2.0 FPS` | `84119a59-0c4c-445e-8653-913bfcabf579` | 151 | `REVIEW_REQUIRED` | `4a6db43c0ed150b52700e87a25c7e8002d0e9e4e83dfd6cc9d5438e0ed0b5ab4` |
| sample4 | accepted `0.0–56.0 s` / `2.0 FPS` | `c9989828-9bc5-4d03-9885-f1adf25b8dc6` | 113 | `FAIL` | `1b6f53f817c49d4b5990192ab3f9120ec17190f6559f201d0ac810e81a7f3167` |

Exact production commands followed this form:

```bash
PYTHONPATH=src .venv/bin/python -m oil_tracker.cli analyze \
  --recipe <tracked-recipe> \
  --video <tracked-source-video> \
  --output <fresh-local-output> \
  --start <accepted-start> \
  --end <accepted-end> \
  --compressor-start <window-start-or-zero> \
  --sampling-fps <5.0-or-2.0>
```

Bundle integrity checks passed for all four runs:

- production `ResultBundleReader` reopen;
- strict truth-bundle identity preview generation;
- required manifest, CSV, Recipe/session snapshot, review index, report, graph and log presence;
- JSON/CSV parsing and exact tracking-row counts;
- source-video resolution validation and metadata match;
- all report-local references resolved;
- all bundle PNGs decoded;
- no hidden staging, `.tmp` or `.part` artifact;
- lifecycle stages `1–6` present and process exit `0`.

## Frozen input identities

| Sample | Source video SHA-256 | Recipe SHA-256 | Frozen provisional SHA-256 |
|---|---|---|---|
| sample1 | `96cb3339cb90e8f5e7c4f71f5e5890cb12caa8996a432977413e15fe214b2c7e` | `4e0a0ad729562dac0bc1e75fbdee0c80ff51aaeda0e07d450f15ff878a637ca7` | `1bade0423365be7dcda710364607433c36a8fb809c925784c52e9ddf6a940dce` |
| sample2 | `73c6586ac167b7c6267c5729c04f05399a3fadc09852d367c49762501285634f` | `061a190996318ecc2520644f21922ca82de24dc5accb91536f127bb3accaa458` | `193a6c97b318b7d2f24ba8558be2429193a30b8dcab3be533e919eea87961a61` |
| sample3 | `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` | `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43` | `adb2f0cff086ec521ca11df9a1a0c4b68373436f974a1c631b01fccc6781e781` |
| sample4 | `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` | `53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849` | `4d64c35b6b80b63fd928a8d9ada9a06dd5cb4dcc8e371f63e510596517213c26` |

Tracked Recipe bytes and each fresh bundle Recipe snapshot are identical. All source, Recipe and provisional hashes remained unchanged after pack generation.

## Exact review-frame selection

The pack contains 15 stable review IDs: sample1 `3`, sample2 `3`, sample3 `4`, sample4 `5`. Requested timestamps are navigation anchors; every item is persisted against its actual decoded timestamp and frame index from the fresh bundle.

| Review ID | Requested | Actual decoded / frame | Candidate Oil Y | Candidate Foam Y | Primary review category | Uncertainty |
|---|---:|---|---:|---:|---|---|
| `S1-01` | 4.800 s | 4.804800 s / 144 | 386.0 | none | weak Oil boundary before overlay | high |
| `S1-02` | 5.200 s | 5.205200 s / 156 | 386.0 | none | first sampled strong overlay context | high |
| `S1-03` | 8.000 s | 7.974633 s / 240 | 386.0 | none | stable High/1/3/Low overlay | high |
| `S2-01` | 0.000 s | 0.000000 s / 0 | none | none | fluorescent reflection, bubbly/full-like texture | medium |
| `S2-02` | 1.000 s | 1.000000 s / 30 | none | none | reflection versus official Foam publication | medium |
| `S2-03` | 2.000 s | 2.000000 s / 60 | none | none | possible no-interface candidate, unconfirmed | medium |
| `S3-01` | 30.030 s | 30.030000 s / 900 | 316.0 | 286.0 | Oil/Foam compound state | high |
| `S3-02` | 34.530 s | 34.534500 s / 1035 | 315.0 | 261.0 | lower Oil–Foam and upper Foam–Gas candidates | high |
| `S3-03` | 95.030 s | 95.028267 s / 2848 | 343.0 | none | oscillating Oil under severe blur | high |
| `S3-04` | 105.000 s | 105.004900 s / 3147 | 361.0 | none | drain onset and focus-loss usability | high |
| `S4-01` | 0.000 s | 0.000000 s / 0 | 860.5 | 850.0 | thin Foam over Oil | medium |
| `S4-02` | 15.000 s | 15.000000 s / 450 | 852.5 | 845.0 | thin Foam over Oil | medium |
| `S4-03` | 30.000 s | 30.000000 s / 900 | 848.5 | 840.0 | oscillating Oil with thin Foam | medium |
| `S4-04` | 49.000 s | 49.000000 s / 1470 | 855.0 | 824.0 | widening/thick Foam over Oil | high |
| `S4-05` | 56.000 s | 56.000000 s / 1680 | 858.5 | 810.0 | Foam-dominant upper region, Oil near lower 1/5 | high |

All candidate coordinates and their stored uncertainty ranges fall inside the corresponding Glass ellipse. `none` means that the Worker did not invent a physical coordinate. For sample2, the pack asks the user whether a true no-interface/full-like state exists; it does not claim that category as confirmed.

Each `review-candidates.json` item also records:

- exact bundle run ID and Glass ID;
- source frame dimensions and ellipse/crop geometry;
- source, Recipe, Recipe-snapshot and provisional hashes;
- official detector fill state, Oil/Foam publication, confidence, validity and flags;
- candidate Oil/Foam coordinates and ranges;
- reflection/overlay/structure bands when relevant;
- category, uncertainty, provenance and a bounded review question;
- clean, comparison and contact-sheet asset paths.

## Review asset contract

For each ID the pack contains:

1. **Clean review crop:** surrounding context plus a subtle Glass-height ruler, with no detector or candidate boundary line.
2. **Candidate comparison image:** official detector publication as solid lines, agent candidate as dashed lines and reflection/overlay/structure candidates as yellow bands or lines.

The image header explicitly states `candidate, not user truth`. Detector and candidate lines are never rendered with the same style.

| Sample | Individual clean/comparison files | Asset-tree SHA-256 | Contact-sheet SHA-256 |
|---|---:|---|---|
| sample1 | 6 | `0cef92ee6cb90352058a74df476dbe3eeee88727a080f06980237d1f2d28673e` | `5280fe3608a48fd3d1657520cafb949464e6f24def8623e61fc582a60289901f` |
| sample2 | 6 | `2a44f6464c8f7664b9d50cb35f722a487d8a4ad50f6cc9c9143803db08fb7e0b` | `9d08b874357bb451003ebcd327fcce7fab61db9a67c9ba9ebb0aff10d2ad86cb` |
| sample3 | 8 | `4434f0cbab8f32b9c7e42fed2427541c9cabcd2a91af13825e766372c5cc5f40` | `14e33f721bdd50acd8cf0324d747cc9b8f4695f05b8bf9d9f1d101dd3389c2cd` |
| sample4 | 10 | `74584426e6c56567c242a8a16742f34ea266f8a36c8cfbe748816395245598f1` | `a1a84aeff5fef48144a5db028e73b5c746de45d9ff4b1bab1cc9de3d97bae5a3` |

All 30 individual images and four full-resolution contact sheets exist and decode. The ZIP contains the mobile README, questionnaire, response template, candidate/category manifests, individual assets and contact sheets; fresh production bundles remain outside the mobile ZIP but under the same ignored provenance root.

## Candidate provenance and uncertainty

Five authorities remain explicitly separate:

| Source | Permitted use in this pack | Not permitted |
|---|---|---|
| Fresh official detector output | comparison context and exact official publication | treating detector output as truth |
| New clean-frame agent visual review | propose candidate coordinates/ranges and questions | assigning a user disposition |
| Frozen provisional annotation | preserve prior sparse range/category context | rewriting it or calling it user-confirmed |
| Existing sample3/sample4 domain-owner statement | physical interpretation of Oil/Foam roles and field priority | claiming exact pixel or exact bundle confirmation |
| Future user response | later approval, correction or unusable decision | inference before the user reviews the pack |

Sample-specific boundary:

- **sample1:** no existing user confirmation. The weak Oil candidate is deliberately high-uncertainty; High/1/3/Low graphics are separately marked as explanatory overlay.
- **sample2:** no existing user confirmation. The candidate leaves Oil and Foam coordinates empty and asks whether a full-like/no-interface state exists after excluding fluorescent reflection and bubbly texture.
- **sample3:** existing domain-owner statements support compound-state, dual-boundary, oscillation and drain interpretation. Exact source-Y candidates remain agent proposals, and the severe focus-loss items may be marked unusable by the user. sample3 remains lower-priority robustness evidence rather than the primary field tuning target.
- **sample4:** existing domain-owner statements support simultaneous Oil and Foam, thin-to-thick Foam evolution and Oil near the lower fifth late in the clip. Official Foam publication and agent Oil/Foam candidates remain separately rendered; Foam presence is not used to justify Oil `null`.

## Category coverage and gaps

| Category | Review IDs | Current status |
|---|---|---|
| clean/weak Oil boundary | `S1-01–S1-03` | candidate covered; user confirmation pending |
| strong overlay | `S1-02`, `S1-03` | covered |
| fluorescent reflection | `S2-01–S2-03` | covered |
| bubbly texture | `S2-01–S2-03` | covered |
| Oil/Foam dual boundary | `S3-01`, `S3-02`, `S4-01–S4-05` | candidate covered; user confirmation pending |
| thin Foam | `S4-01–S4-03` | candidate covered; user confirmation pending |
| thick Foam | `S4-04`, `S4-05` | candidate covered; user confirmation pending |
| Oil-under-Foam | `S4-01–S4-05` | candidate covered; user confirmation pending |
| oscillating Oil | `S3-03`, `S4-03` | candidate covered; user confirmation pending |
| severe blur/focus loss | `S3-03`, `S3-04` | lower-priority robustness review |
| no-interface | `S2-01–S2-03` | possible candidate only; not claimed |

The current samples do not supply representative evidence for:

- scratch;
- fogging/stain;
- clean rim-adjacent Oil boundary;
- high-quality field fill/drain;
- clean full/empty no-interface;
- category-balanced independent field-video coverage.

These gaps remain future clean-field-video obligations. They are not synthesized from the current frames.

## Validation

The local pack passed all required checks:

- four production CLI runs exited `0` and completed lifecycle `1/6–6/6`;
- four bundles reopened with integrity PASS;
- review count `15`, within the required `12–16` range;
- stable review IDs are unique;
- every item resolves to exact bundle, run, frame, timestamp and Glass identity;
- all candidate coordinates are inside valid ROI bounds;
- all clean, comparison and contact-sheet images exist and decode;
- all four contact sheets contain the expected review IDs;
- candidate and SHA manifests parse;
- all 150 complete-manifest entries recompute without mismatch;
- source, Recipe and provisional hashes match the frozen identities;
- no `.oiltruth` file exists in the repository or generated root;
- generated artifacts are ignored under `sample/output/` and no non-ignored local asset was created.

Targeted suite:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_user_truth_domain.py \
  tests/test_json_truth_repository.py \
  tests/test_truth_export_controller.py \
  tests/unit/test_result_bundle_reader.py \
  tests/unit/test_source_video_resolver.py
```

Result: `64 passed in 6.69s`; exit code `0`.

## Mobile response format

The local `review-response-template.md` provides one block per review ID. The user can answer without calculating pixels:

```text
S1-01:
- 결과: 승인 / 수정 / unusable
- Oil: 승인 / 위치 수정(위·아래 또는 Glass 높이 비율) / 없음
- Foam: 승인 / 위치 수정(위·아래 또는 Glass 높이 비율) / 없음
- 강한 선: reflection / overlay / structure / 해당 없음
- 메모:
```

The same block is repeated for `S1-01–S1-03`, `S2-01–S2-03`, `S3-01–S3-04` and `S4-01–S4-05`. User responses remain external review input until a later authorized S6-D2 Worker creates bundle-bound product `.oiltruth` from only the explicitly approved or corrected frames.

## Intentional non-runs and next owner

This Worker did not:

- create, load as product truth, or modify `.oiltruth`;
- modify the four provisional truth files;
- modify source, tests, dependencies, settings, thresholds, Recipes or original MP4s;
- compute detector accuracy metrics or claim accuracy PASS;
- assign `confirmed_correct`, `corrected` or `unusable` on behalf of the user;
- run Windows, packaging, performance, long-duration or GUI acceptance;
- merge, synchronize the registered checkout, close S6, start S7, or clean existing branches/worktrees/evidence.

The next owner is the **S6-D1 Mobile-Assisted User-Truth Review Pack Fresh Exact-Head Auditor**. Only after Auditor PASS and merge does ownership move outside the coding workflow to the user for **S6-D1 Domain-Owner Mobile Review**. After explicit user responses, a separate S6-D2 Worker may create product `.oiltruth` for approved frames.
