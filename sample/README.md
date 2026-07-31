# Repository Supporting Samples

These local videos support S6 engineering qualification. They are not canonical detector truth and do not substitute for user-confirmed `.oiltruth`. `base_sample_1.mp4` owns the completed S6-A qualification; sample2/3/4 are the bounded S6-B intake set.

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

The initial S6-A run found a reproducible CLI lifecycle-progress formatting defect before bundle finalization. After repaired `main @ 8b37ff81…`, the resumed official A/B/C CLI runs completed through lifecycle stages `1/6–6/6` and produced reviewable bundles. See [`docs/30-quality/s6-base-sample-1-evidence.md`](../docs/30-quality/s6-base-sample-1-evidence.md) for the preserved failure, diagnostic evidence and repaired-main official qualification.

## S6-B additional local samples

| Video | Exact identity | Sequential usable boundary | Accepted fixed-geometry window | Recipe |
|---|---|---|---|---|
| `sample2.mp4` | `1,970,224 B`; `73c6586ac167b7c6267c5729c04f05399a3fadc09852d367c49762501285634f` | frames `0–285`; last `9.500000 s` | `0.0–2.0 s` | `sample2.oilrecipe` |
| `sample3.mp4` | `10,001,682 B`; `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` | frames `0–4198`; last `140.073267 s` | `30.03–105.0 s`; fresh drain `75.08–105.0 s` | `sample3.oilrecipe` |
| `sample4.mp4` | `16,224,936 B`; `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` | frames `0–1681`; last `56.033333 s` | `0.0–56.0 s` | `sample4.oilrecipe` |

All three show compressor sight glasses with reviewable phase evidence. sample2 has handheld reframing and a strong fluorescent reflection; sample3 includes fill, agitation, drain, blur and late reframing; sample4 keeps static framing around a small sight glass. The Recipe ellipses use only the stated stable windows. No exclusion hides an in-glass reflection, line, Foam-like region or difficult detector evidence.

The Recipes use deterministic IDs/timestamps, `AUTO`, `mm_per_pixel=null`, margin `0.08`, no exclusions and production-default detector settings. Their SHA-256 values are:

- `sample2.oilrecipe`: `061a190996318ecc2520644f21922ca82de24dc5accb91536f127bb3accaa458`
- `sample3.oilrecipe`: `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43`
- `sample4.oilrecipe`: `53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849`

Production CLI runs completed with exit `0` and lifecycle stages `1/6–6/6`. sample2 and both sample3 windows returned `REVIEW_REQUIRED`; sample4 returned `FAIL`. These are preserved engineering results, not verified physical truth. See [S6-B evidence](../docs/30-quality/s6-additional-real-samples-evidence.md) for commands, bundle inspection and limitations.

## S6-C agent-assisted provisional truth

The four `*.provisional-truth.json` files contain 68 sparse, blind, machine-readable annotations made from video/ROI frames before detector output was inspected:

- `base_sample_1.provisional-truth.json`: 19 annotations;
- `sample2.provisional-truth.json`: 9 annotations;
- `sample3.provisional-truth.json`: 24 annotations;
- `sample4.provisional-truth.json`: 16 annotations.

They use the explicit `agent-assisted-provisional-truth-v1` JSON schema and a separate `.provisional-truth.json` artifact suffix because the product-owned `.oiltruth` schema represents bundle-bound user confirmation/correction. They are silver truth, not user-confirmed ground truth, do not match the product `*.oiltruth` loader/file dialog, and cannot establish official detector accuracy. See [S6-C provisional comparison evidence](../docs/30-quality/s6-provisional-truth-comparison.md) for frozen hashes, selection rationale, uncertainties and fresh detector comparison.

## Git policy

All MP4 files remain ignored by `sample/*.mp4` and are never added by qualification work. Generated evidence under `sample/output/` also remains ignored. Only the four exact deterministic Recipes are allowlisted from the Recipe ignore rule; the provisional JSON artifacts are tracked normally and remain separate from product `.oiltruth`. No MP4 or output allowlist exists.
