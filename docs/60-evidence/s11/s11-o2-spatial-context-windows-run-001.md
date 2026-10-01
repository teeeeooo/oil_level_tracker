# S11 O2 spatial-context Windows run 001 — transferred report

Source revision: `bd0185838c094d2529d6089870e37fb8552d90ed` (GitHub ZIP).
Evidence scope: user-transferred execution summary, not locally accessed private
outputs. COMPLETE, all output hashes and 12 input hashes are reported passing;
schema and artifact transcription are resolved by explicit user correction;
the receipt photograph, explicit output-count correction and supplied summary
resolve the intake questions. Output hash verification remains user-reported,
not independent local hashing of private files.
No rerun, score change, label change or detector improvement is established.

## Reported result

- Original review-002 frame 14386, revision 14; review-003 frame 16280, revision 4.
- Both baseline checks reported MATCH, zero mismatched bands. This supports
  gray/support-band reconstruction on the reported fields, not historical pixel
  equality or physical identity. Supplied summary specifies 0/1416 bands for
  review-002 and 0/1012 for review-003 (0/2428 combined only as an inventory count,
  not independent samples).
- Twelve input files reported unchanged before/after/current: five original bundle
  files, source video, two labels, two packets and two existing bundle links.
- NOT_EVALUATED; EXPLORATORY_UNCALIBRATED; auto_acceptance=false;
  production_decisions_emitted=false; FIELD FAIL; numeric_localization=NOT_MEASURED.
- Source/crop/gray/mask PNGs and ordered strip SVGs are reported retained locally
  in `spatial-context-001`. The supplied summary contains point mappings, coverage and extrema. Actual
  ordered row arrays, plots and crops have not been examined locally; wider
  spatial information/identity utility remains unassessed.

## Local source comparison and report corrections

The runner SHA-256 matches the reported value exactly:
`d412d98b424842c8f2898de3ba74306317164bd4b13438d395f60d91eec3b84d`.

| Item | Transferred text | Locally verified source / arithmetic |
|---|---|---|
| Schema | `s11-02-spatial-context-v1` | `s11-o2-spatial-context-v1`; character at index 4 is lowercase o, code point 111 |
| Artifact | `6aaf5f3ff6c4e1314d0bcb7effb745ff5b721c03940c57002214b039ef544910` | Windows-path reconstruction: `6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910` |
| Hashed outputs | 33 | Listed inventory totals 31: 2 JSON/MD + 10 PNG + 19 SVG; complete.json is an additional unlisted receipt, hence 32 total files for that inventory |

The user explicitly confirmed that the artifact is identical, with `4d08cb`,
and that the schema is `o2`; both prior differences were copying errors. These
two issues are resolved by user confirmation, not by silently rewriting evidence.
The later receipt photograph and explicit user correction confirm 31 hashed
outputs, 32 files including complete.json. The supplied summary resolves per-case
band denominators and mappings. The old typo reappears in the pasted summary
header; retain the user-confirmed corrected artifact above without reopening it.
At this revision code-path keys use native separators, so the artifact itself is
platform dependent: the POSIX reconstruction is
`53fd2b73c8d387eb905d947307b09e18a9d27c3151b905fea0abde85dba93689`.
The Windows expectation above was recomputed using PureWindowsPath keys and the
same current code-file hashes/spec/schema; no source edit or private rerun was
performed. The corrected user-reported artifact matches that Windows expectation
exactly. No artifact-generation change or experiment rerun is needed.

The previous structure-context run's True/111 confirmation belongs to that older
receipt; this run now has its own explicit user correction above. Hand-copied
Glass UUIDs are not authoritative scene records.

## Supplied summary and interpretation

| Case | Frame / revision | Origin / raster H,W | Points / X profiles | Baseline |
|---|---|---|---|---|
| review-002 | 14386 / 14 | [0,211] / [773,578] | 124 / 9 | MATCH, 0/1416 |
| review-003 | 16280 / 4 | [1199,56] / [584,462] | 158 / 10 | MATCH, 0/1012 |

Both requested/decoded frame indices and timestamps match in the supplied
summary, with zero forward decodes. Source Y extents are [211,984) and [56,640).
Every listed observed+unavailable row count equals its case's raster height.
BASE profiles have 62–240 unavailable rows; Accum profiles have 47–180. These
are global counts, not proof that a particular candidate/remote return is visible.

Exact-X inventory relevant to the next inspection:

- BASE native idx8/9/10/11 share profiles 5/6/7 at X=[130,236], [236,343],
  [343,449]. Oil-labeled idx8 Y=[397,396,397], idx9 Y=[382,406,419], and
  structure-negative idx11 Y=[901,925,922] are markers on the same profiles.
  idx10's historical/local judgment conflict remains separate, not repaired here.
- Accum native idx10/15 share profiles 5–9 at X=[1218,1303], [1303,1388],
  [1388,1473], [1473,1558], [1558,1643]. Their Y markers are respectively
  [209,210,217,219,220] and [317,328,313,295,296].
- BASE candidate-center idx0(Y382)/idx20(Y406) share profiles 0–4. This remains
  the human-ambiguous pair, not a forced positive/negative discriminator target.

Sharing a profile is intentional: it is a full-height observation indexed by X,
with each candidate retaining its own Y marker. It is not evidence of candidate
identity or failed separation. 282 point references reuse 19 profiles, so they
are not 282 independent observations. Min/max and row counts erase vertical
order and cannot determine whether a brightness return exists outside O1 bands.

## Next bounded action

Intake reconciliation is closed on the supplied evidence. Do not rerun the source
probe or request schema/hash/count confirmations again. Inspect existing saved
profiles against raw crop/gray/masks on Windows, following the
[stored-output inspection](../../40-operations/s11-o2-local-shadow-evaluation.md#ordered-spatial-context--stored-output-inspection).
Use JSON for numerical geometry/coverage/band extents, images for appearance;
never OCR coordinates. Report absent/censored/ambiguous observations as such.
No new video, labels, detector execution, threshold or identity score is requested.
This step answers whether extra spatial context is observable, not whether an
identity classifier is field qualified. Human idx0/idx20 ambiguity is retained.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: receipt transcription is resolved on supplied evidence; finite-band information loss is only established synthetically, and private wider-context physical efficacy remains unassessed.
- Logic-map impact: NONE — evidence intake only, no implementation change.
- Failure-registry impact: NONE — no new field cause or repair established.
