# Repository Supporting Sample

`base_sample_1.mp4` is a short repository-local supporting sample for S6 engineering qualification. It is not canonical detector truth and is not a substitute for user-confirmed `.oiltruth`.

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

## Git policy

The MP4 remains ignored by `sample/*.mp4` and is not added to Git by this qualification. Generated evidence under `sample/output/` also remains ignored. Only the exact deterministic Recipe is allowlisted from the existing `sample/*.oilrecipe` ignore rule.
