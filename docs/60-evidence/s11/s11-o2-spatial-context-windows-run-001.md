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

## Stored-output inspection report received — interpretation pending

A subsequent Windows report describes native BASE idx8/9/11, Accum idx10/15,
and the BASE idx0/idx20 ambiguous control. It reports local spikes, gradual
changes and censored bands without changing original files or classifier outputs.
The Windows agent reads files directly; text reaches this conversation through
the user's OCR/transcription. Do not attribute a numeric discrepancy to the
Windows reader without tracing the original values. Existing reported
COMPLETE/baseline MATCH is not invalidated by prose discrepancies.

The requested extent question is not yet answered by this report:

1. Most appearance examples span only candidate Y +/-10 px. The report calls
   these outside O1 bands but does not provide the original disjoint band ranges.
   A local spike can lie inside already sampled bands; extra extent is unproven.
   Row-level appearance differing from a band mean also does not prove that a
   *remote* transition was newly observed. Keep resolution and extent distinct.
2. Accum profile 5, X=[1218,1303], is reported to have global minimum 94.1017
   (previous generated summary), yet idx15's Y=307–327 example says 89 to 83.5.
   Those cannot both be values of the same non-null raw `gray_mean` array. The
   cause (transfer typo, wrong profile, indexing/channel or other error) is unknown.
3. The report says all unavailable reasons are None and therefore geometric.
   Source inspection shows `baseline_check.rows[].original` contains only
   available/count/gray_mean/gray_std/glare_fraction, **not reason**. The full
   `baseline_witness.candidates[].sectors[].centers[].scales[].bands[].reason`
   retains the string emitted by `_band`: available, outside_crop, or
   insufficient_visible_pixels. Reading a missing projection key cannot establish
   which path the Windows agent used or the original unavailability cause.
4. Band unavailable is not equivalent to all its profile rows being null. The
   original band also requires complete crop bounds, at least eight visible pixels
   and visible fraction >=0.5. Non-null rows with insufficient band coverage can
   remain inspectable, with uncertainty. Global glare totals likewise do not locate
   glare at a particular candidate without row-specific support.
5. Shape/polarity differences across X do not establish different physical objects;
   neighboring spikes do not establish the same object. BASE idx9 S1 is itself
   described as decreasing, so a blanket Oil-increases/structure-decreases account
   is not supported even by the report. Rejected flags are production history,
   not independent physical identity truth. Candidate/source-Y separation is not
   a classifier. Human idx0/idx20 uncertainty remains unchanged.
6. The report does not give a specific remote source-crop feature/region matched
   to a profile outside the original bands. Image-to-profile correspondence is
   therefore still unverified here, not replaced by the local numeric descriptions.

Next: use the same immutable JSON and images, with no rerun. First return the
exact Accum P5 gray_mean min/max and source Y=307..327 rows (`index=Y-56`), with
counts and nulls, to settle the contradiction. Read unavailable reasons from the
full baseline witness rather than the comparison projection. Then complete the
original eight-strip table with exact disjoint source band ranges, genuinely
outside-band observations, intervening missing support and crop correspondence;
absence/ambiguity/censoring is an acceptable result. Do not force a return or add
an identity threshold. No new scene or expanded experiment is authorized by this
incomplete descriptive inspection.


## Direct-value follow-up — resolved values and remaining geometry mix

The next transferred report resolves the earlier P5 numeric contradiction:
Accum P5's minimum is reported as 94.10 at source Y221 (index165), while
Y307–327 (indices251–271) contains 101.0488–104.5238, peaking at Y321 and
then decreasing to 102.2143. All these rows are observed, effective=visible
82–84 and glare excluded=0. Supersede the previous 89-to-83.5 description;
its error source remains unproven. No source-file mutation is reported.

The Windows follow-up explicitly identifies the prior None reason as a read
from the baseline_check projection. Full witness reasons include
insufficient_visible_pixels and outside_crop. That field-source question is
closed. However, the newly listed per-sector reasons cannot yet be attached to
native points: the report omits center.role and uses ranges consistent with
candidate_center in several native-labelled tables.

Source verification (`_center`, `_measure_sector`, and baseline reconstruction)
establishes the following corrections without needing private outputs:

- canonical_y and center.source_y are already source coordinates. Do not add the
  crop origin again: BASE 397 does not become 608; 922 does not become 1133;
  Accum 217 does not become 273. Only local_y_range receives origin Y.
- Y increases downward: smaller Y is above, larger Y is below. The report's
  ABOVE/BELOW descriptions are reversed.
- A candidate's center and its sector's native path are distinct. For example,
  Accum idx10 has center217 but P8 native219; idx15 has center313 but P8
  native295; BASE idx11 has center922 but P6 native925. Uniform ranges across
  all sectors are not the native ranges when path_source_y varies.
- The listed Accum idx10 local envelope [106,217) is exactly centered at
  local161/source217 for maximum BW18. BASE idx8 [113,260) is centered at
  local186/source397 for BW24. These match candidate-center envelopes, not
  every sector's native geometry. The idx11 near_below [713,721) likewise
  corresponds to source922, not native S1/source901. Do not replace earlier
  native missing counts with these unqualified center rows.
- A min-to-max envelope is not the union of the disjoint four bands. Preserve
  every band's half-open bounds, availability and reason before classifying
  individual rows as inside/outside sampled or usable support.

Illustrative envelopes recomputed from the implemented offsets and previously
supplied integer native Y/BW values follow. These are local source arithmetic,
not a claim to have read the private witness band objects:

| Case / candidate / profile | Native source Y | Maximum BW | Source envelope, stop exclusive |
|---|---|---|---|
| BASE idx11 / P6 | 925 | 24 | [852,999) |
| Accum idx10 / P8 | 219 | 18 | [164,275) |
| Accum idx15 / P8 | 295 | 18 | [240,351) |

Consequently, the reported Accum P8 spike at Y213–221 lies inside idx10's
native envelope (and overlaps existing near bands), but above/outside idx15's
native envelope. It is not outside both. Calling it immediately below a missing
far_above band also mixes source and local coordinates and does not establish
its relation to the native center's unavailable bands. The report's P8 values
must not be compared against P5's global minimum; they are different X strips.

The BASE P6 transition at Y396–407 is above/outside idx11's native envelope.
The Accum P6 bump at Y415–425 is below/outside both native idx10 Y210 and
idx15 Y328 envelopes (max BW18). These reported full-height observations
support a bounded possibility of extra appearance context relative to those
candidates' local bands, not proof of identity or a candidate-specific feature:
each shared-X curve includes the same remote feature regardless of marker.
The sweeping claim that all larger-Y outside observations are crop-edge effects
is contradicted by the reported interior Y415–425 bump. Sparse edge rows need
coverage qualification, but boundary causation itself is not demonstrated by
low counts. Counts of 12/19 'transitions' lack an extraction definition and are
not accepted metrics or a new threshold.

Next action is narrowed to three existing witness centers only: BASE idx11
X=[236,343] native925, Accum idx10 X=[1473,1558] native219 and idx15 at the
same X native295. Read exact candidate/X/role/source_y/sampling_center_local_y;
return each scale's four original band names, local/source half-open ranges,
availability and reason, and classify the already reported remote row intervals
against their exact union. Missing exact match must be reported, never replaced
by the first center or canonical_y. No new transition detector, whole-report
rewrite, video decode, labels, thresholds or source-probe rerun is needed.
Specific raw-crop correspondence remains unverified locally. Existing execution
receipts/baseline MATCH and human idx0/idx20 ambiguity remain unchanged.
