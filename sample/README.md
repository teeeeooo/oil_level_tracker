# Repository Supporting Samples

These local videos support S6 engineering qualification. They are not canonical detector truth and do not substitute for user-confirmed `.oiltruth`. `base_sample_1.mp4` owns the completed S6-A qualification; sample2/3/4 are the bounded S6-B intake set.

## Sample3 use restriction

**sample3 is retired from routine development and logically quarantined.** Its
original MP4 stays at `sample/sample3.mp4` with the identity below so old evidence
remains reproducible. Do not delete, re-encode, cut new clips, mine more usable
intervals, relabel it or tune a detector to close its numeric gaps. This is an
evaluation-input restriction; the production detector contains no sample-name rule.

Reuse the frozen [A/B Oil-region reply and marked image](../docs/50-diagnostics/s11/2026-10-10-sample3-gap-source-reply.json),
[C/D reply](../docs/50-diagnostics/s11/2026-10-10-sample3-confirmation-role-reply.json)
and [scope disposition](../docs/50-diagnostics/s11/2026-10-10-sample3-evaluation-scope.md).
A/B are approximate regional Oil positives, C is external-frame structure and
D is unassessable from blur. No continuous usable clip, exact pixel tolerance
or new physical accuracy/cadence benchmark is certified between these frames.
New discrimination work starts from the qualified water and scoped sample4
controls routed by the [Work Plan](../docs/00-project/work-plan.md).

The shared diagnostic corpus/session/input loaders and full replay entry points
reject sample3 by default. Corpus-dependent pytest checks explicitly report
`SKIPPED` with `QUARANTINED`; that is not a completed legacy regression PASS.
For a specifically needed existing regression, scope permission to one command:

```bash
python -m tests.diagnostics.s11_corpus_access --purpose legacy-regression -- \
  python -m pytest <required-test-paths>
```

For an existing decode/provenance/output or deterministic behavior check, use
`--purpose engineering-replay` with the required replay command. The wrapper
preserves child arguments/exit status and passes permission to its workers only.
Do not export `OIL_TRACKER_SAMPLE3_PURPOSE` in a shell profile, CI global environment
or test-wide fixture. Manifests retain the explicit purpose and
`physical_acceptance=NOT_EVALUATED` separately from runtime/tracking fingerprints.
The original four-video windows and complete 13-case legacy comparator remain
unchanged: never omit sample3 and label the remaining subset as full PASS.
Purpose selection does not reopen sample3 research; new source qualification
would require a separate change to the current Work Plan.

## Exact identity

| Item | Value |
|---|---|
| Video | `sample/base_sample_1.mp4` |
| SHA-256 | `96cb3339cb90e8f5e7c4f71f5e5890cb12caa8996a432977413e15fe214b2c7e` |
| Size | `12,408,143 bytes` |
| Resolution | `1280 × 720` |
| Frame count | `434` |
| OpenCV FPS | `30.059287442513345` |
| Calculated duration | `14.438133333333333 sec` |
| Codec reported by OpenCV | `h264` |
| Recipe | `sample/base_sample_1.oilrecipe` |
| Recipe SHA-256 | `4e0a0ad729562dac0bc1e75fbdee0c80ff51aaeda0e07d450f15ff878a637ca7` |
| Recipe schema | `1` |

The on-screen title identifies the source context as **“TechTip: Checking Oil Level - Bitzer Compressors.”** This qualification records only the bytes and visible context present in the checkout; it does not establish redistribution rights or detector truth.

## Known visual transition

Frames `0–150` do not contain the explanatory `High / 1/3 / Low` line overlay. The overlay first appears at frame `151`, approximately `5.023405837 sec` at the reported source FPS. A direct horizontal-color-run check found no qualifying red/green overlay at frame `150` and found approximately `244 px` red and `241 px` green runs at frame `151`.

The actual oil-air boundary in the dark sight glass is weak. After frame `151`, the explanatory lines are strong, static horizontal artifacts inside the analysis region. They are deliberately left visible to the detector.

## Deterministic Recipe geometry

The Recipe uses source-frame pixel coordinates from representative frames `0`, `120`, `150`, `151`, `152`, `240` and `433`.

| Field | Value |
|---|---|
| Reference frame | `1280 × 720` |
| Glass count | `1` |
| Ellipse center | `(696.0, 366.0)` |
| Ellipse radii | `(145.0, 148.0)` |
| Zero line Y | `366.0` |
| Margin ratio | `0.08` |
| Exclusions | none |
| Initial state | `AUTO` |
| `mm_per_pixel` | `null` |
| Detector settings | production defaults |

The ellipse represents the inner circular sight-glass analysis area. External subtitle, logo and equipment-label regions remain outside it. No exclusion zone hides the `High / 1/3 / Low` overlay. The centerline zero reference is reproducible geometry, not a calibrated physical datum or a detector-tuning target.

Recipe identifiers and timestamps are deterministic:

- Recipe ID: `71f5f146-cb3f-57a8-8075-31a2ba18165f`
- Glass ID: `1a188c16-6295-56a7-bd61-61a78b7ef058`
- Created/updated: `2026-07-30T00:00:00+00:00`

## Intended use

This sample may be used to check:

- MP4 decode and metadata;
- Recipe load and round-trip;
- pre-overlay, transition and post-overlay engineering behavior;
- canonical ambiguity/no-interface projection;
- Oil/Foam output separation;
- result-bundle construction and offline asset integrity;
- short-run resource diagnostics.

It must not be used to claim that a detected boundary is physically correct, or to report MAE, precision, recall, false-positive/false-negative truth, calibrated millimetres or detector accuracy PASS. No detector branch may depend on this filename, its hash, frame `151`, its Recipe ID or any fixture identity.

## Reproduction commands

From the repository root:

```bash
shasum -a 256 sample/base_sample_1.mp4 sample/base_sample_1.oilrecipe

PYTHONPATH=src .venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/base_sample_1.oilrecipe \
  --video sample/base_sample_1.mp4 \
  --output sample/output/s6-base-sample-1/run-b-full \
  --start 0 \
  --end 14.438133333 \
  --compressor-start 0 \
  --sampling-fps 5.0
```

The initial S6-A run found a reproducible CLI lifecycle-progress formatting defect before bundle finalization. After repaired `main @ 8b37ff81…`, the resumed official A/B/C CLI runs completed through lifecycle stages `1/6–6/6` and produced reviewable bundles. See [`docs/60-evidence/s6/s6-base-sample-1-evidence.md`](../docs/60-evidence/s6/s6-base-sample-1-evidence.md) for the preserved failure, diagnostic evidence and repaired-main official qualification.

## S6-B additional local samples

| Video | Exact identity | Sequential decode boundary | Historical engineering replay window | Recipe |
|---|---|---|---|---|
| `sample2.mp4` | `1,970,224 B`; `73c6586ac167b7c6267c5729c04f05399a3fadc09852d367c49762501285634f` | frames `0–285`; last `9.500000 s` | `0.0–2.0 s` | `sample2.oilrecipe` |
| `sample3.mp4` | `10,001,682 B`; `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` | frames `0–4198`; last `140.073267 s` | `30.03–105.0 s`; fresh drain `75.08–105.0 s` | `sample3.oilrecipe` |
| `sample4.mp4` | `16,224,936 B`; `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` | frames `0–1681`; last `56.033333 s` | `0.0–56.0 s` | `sample4.oilrecipe` |

All three show compressor sight glasses. sample2 has handheld reframing and a strong fluorescent reflection; sample3 includes fill, agitation, blur and glass-position changes; sample4 keeps static framing around a small sight glass. These are preserved historical execution windows, not certified continuously visible interfaces or stable geometry. In particular, sample3's 30.03–105s and fresh-start 75.08–105s windows are not usable physical-accuracy clips under the fixed Recipe. Follow the sample3 restriction above; no new exclusions or Recipe corrections are implied.

The Recipes use deterministic IDs/timestamps, `AUTO`, `mm_per_pixel=null`, margin `0.08`, no exclusions and production-default detector settings. Their SHA-256 values are:

- `sample2.oilrecipe`: `061a190996318ecc2520644f21922ca82de24dc5accb91536f127bb3accaa458`
- `sample3.oilrecipe`: `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43`
- `sample4.oilrecipe`: `53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849`

Production CLI runs completed with exit `0` and lifecycle stages `1/6–6/6`. sample2 and both sample3 windows returned `REVIEW_REQUIRED`; sample4 returned `FAIL`. These are preserved engineering results, not verified physical truth. See [S6-B evidence](../docs/60-evidence/s6/s6-additional-real-samples-evidence.md) for commands, bundle inspection and limitations.

## S6-C agent-assisted provisional truth

The four `*.provisional-truth.json` files contain 68 sparse, blind, machine-readable annotations made from video/ROI frames before detector output was inspected:

- `base_sample_1.provisional-truth.json`: 19 annotations;
- `sample2.provisional-truth.json`: 9 annotations;
- `sample3.provisional-truth.json`: 24 annotations;
- `sample4.provisional-truth.json`: 16 annotations.

They use the explicit `agent-assisted-provisional-truth-v1` JSON schema and a separate `.provisional-truth.json` artifact suffix because the product-owned `.oiltruth` schema represents bundle-bound user confirmation/correction. They are silver truth, not user-confirmed ground truth, do not match the product `*.oiltruth` loader/file dialog, and cannot establish official detector accuracy. See [S6-C provisional comparison evidence](../docs/60-evidence/s6/s6-provisional-truth-comparison.md) for frozen hashes, selection rationale, uncertainties and fresh detector comparison.

## S6-D2 user-confirmed product truth

The four product-owned `.oiltruth` files materialize the explicit S6-D1 user response against the exact preserved D1 production bundles:

- `base_sample_1.oiltruth`: 3 annotations;
- `sample2.oiltruth`: 3 annotations;
- `sample3.oiltruth`: 4 annotations, including 2 `unusable` focus-loss frames;
- `sample4.oiltruth`: 5 annotations.

They contain 15 exact reviewed frames in total. The fresh product translation is `13 corrected + 2 unusable`; user approval of a D1 agent candidate is not interpreted as approval of detector output. See [S6-D2 user-confirmed product truth](../docs/60-evidence/s6/s6-d2-user-confirmed-product-truth.md) for exact bundle identities, coordinates, error semantics, derivative-ZIP provenance and validation.

These truth files do not make the current sample set category-balanced official accuracy evidence and do not establish detector accuracy PASS. The four `*.provisional-truth.json` files remain separate immutable blind evidence.

The [2026-10-10 source/annotation audit](../docs/60-evidence/s11/2026-10-10-local-truth-and-evaluation-audit.md)
qualifies future use: nine of the 13 Oil coordinates originate in approved
agent proposals with uncertainty ranges, and four in user ruler percentages.
Their original scalar values remain historical regression references, but none
has been certified here as an exact contour at the new fixed-center X. The
base f156 no-Foam annotation conflicts with a later Foam–air observation; the
disputed physical claim is quarantined pending reconciliation. Original agent
ranges are not automatically approved tolerances. Use the
[current validation strata](../docs/30-validation/s11-interface-observability-witness-validation.md#local-source-and-truth-qualification)
to separate engineering compatibility, supported physical claims, ambiguous or
unusable evidence, and legacy scalar agreement. Keep all cases and qualifications
visible instead of treating the entire four-video set as uniformly precise truth.

## S11 public-video development intake (2026-10-09)

Three additional local downloads have been screened without detector execution:

| File | Original download name | Intended development use |
|---|---|---|
| `sample5.mp4` | `public_water_fill_pexels_6381722.mp4` | Empty-glass pattern reference, moving/deforming water surface with bubbles, and later settled surface |
| `sample6.mp4` | `public_beer_fill_pexels_5538050.mp4` | Separate liquid/Foam boundaries; Foam top becomes cropped and unavailable |
| `sample7.mp4` | `public_milk_fill_pexels_11158788.mp4` | Opaque white liquid versus surface froth; fixed-rim/base opposition |

The [intake assessment](../docs/50-diagnostics/s11/2026-10-09-public-video-intake.md)
and its machine record retain hashes, metadata, inspected frames, exposure and
limitations. All three are development-intake exposures, not untouched holdout,
canonical truth or field acceptance. The truth audit above qualifies use of both
old and new recordings by observation/role. Existing Recipes and historical
four-video scalar comparisons retain their original identities. No MP4 or
generated-image tracking is added.
The [rename receipt](../docs/50-diagnostics/s11/2026-10-09-public-video-rename.json)
maps the frozen intake's original paths to the current names and verifies identical
video hashes. Historical intake artifacts and generated-image paths are preserved.

## Git policy

All MP4 files remain ignored by `sample/*.mp4` and are never added by qualification work. Generated evidence under `sample/output/` also remains ignored. Only the four exact deterministic Recipes are allowlisted from the Recipe ignore rule. The provisional JSON artifacts and four product `.oiltruth` files are tracked normally, remain semantically distinct, and no truth file is stored inside a result bundle. No MP4 or output allowlist exists.

S11 corpus-dependent canonical tests treat those ignored videos as optional local evidence with mandatory identity when present. The checked-in S11-A evidence manifest owns the four MP4 SHA-256 values: a complete matching local corpus runs with the explicit purpose above; otherwise corpus-dependent tests report `SKIPPED / QUARANTINED`. Missing required MP4s remain `SKIPPED / NOT AVAILABLE`; any present wrong-hash file is a hard identity failure even when another video is missing or permission is absent; and an admitted hash-correct file that cannot be decoded is a hard decode failure. Tests never form a partial 13-row S11 aggregate, and this policy does not redistribute or track the MP4 bytes.
