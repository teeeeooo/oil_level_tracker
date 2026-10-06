# S11 recorded-band color-side measurement — local verification

Date: 2026-10-02. Starting repository HEAD: `5e3ec32d93bcf047a6350dff0dd2d1cb8c9f42c3`.
Scope: offline diagnostic source, tests and contracts. No production detector,
O1 trace, label, threshold or accepted field state changes.

## Question and implementation

The [candidate-guided human rationale](s11-o2-identity-context-windows-review-001.md#candidate-guided-human-rationale-received--2026-10-02)
identified apparent side transparency/subtle color and a traversing reflective
boundary for Accum idx10, absent at idx15. Existing positive/negative labels are
retained. The answer is qualitative, not calibrated transparency, exact region
truth or permission to treat gray alignment as identity.

The existing saved-output adapter now accepts `--color-side`; the existing
spatial probe owns `measure_color_side`. It consumes original spatial-context
BGR/gray/effective/glare rasters and recorded bands. It reuses receipt, artifact,
raw identity, geometry/center binding, baseline and preservation gates. It does
not introduce a second loader, detector, video decoder or color-space search.

The [contract](../../20-architecture/s11-interface-observability-witness-architecture.md#w4-recorded-band-color-sides--saved-output-measurement)
fixes B/G/R/gray code-value units, identical visible pixels, per-column
below-minus-above, equal column weights and separate near/far vectors. Opponent
changes B-G/R-G expose chromatic variation but do not label its cause. Empty or
O1-unavailable pairs stay null; partial band observations are explicitly
ineligible. Source X order is retained, vertical band order is averaged.

Output schema: `s11-o2-color-side-v1`; spec: `recorded-band-color-side-v1`.
Three hashed outputs (`experiment.json`, `summary.md`, `color-side.csv`) plus
COMPLETE receipt. Full input recheck precedes the last receipt write.

## Local verification

Executed with repository `.venv/bin/python`:

```text
python -m pytest -q tests/unit/test_s11_spatial_context_probe.py tests/unit/test_s11_spatial_context_run.py tests/unit/test_s11_joint_context.py tests/unit/test_s11_color_side.py
98 passed
```

Nineteen color-specific controls plus shared color/default-mode input guards and
two-case geometry controls cover:

- BGR `[0,0,100]` to `[0,51,0]`: both OpenCV gray30, side delta
  `[0,51,-100,0]`; reversed polarity reverses the vector. This demonstrates
  retained color information, not a whole-O1 witness collision or physical truth.
- Achromatic steps, including zero: opponent deltas zero, observed state retained.
- Mask/glare-hidden color changes: no leakage. Empty and disjoint-column support:
  no fabricated delta. Unequal per-column counts: equal-column result remains
  distinct from pixel-weighted band averaging. Negative differences do not wrap.
- Recorded unavailable/clipped bands: partial observations remain visible in
  diagnostics but pair deltas are null. Count/range/shape/gray/duplicate/resource
  violations reject execution.
- Actual producer fixture, Unicode non-repository CLI cwd, closed stdin and
  explicit UTF-8: native/center roles, exact aliases, CSV numbers, all output
  hashes and source-byte preservation. Two cases keep their own frame/Glass.
- Saved non-gray BGR fixture with unchanged gray180/80: expected near-side delta
  `[-86,-100,-106,-100]` and opponent `[14,-6]` without a new joint gradient map.
- Shared malformed-source guards run in both modes; mutation during color
  measurement/publication and BGR-to-gray mismatch leave no COMPLETE receipt.
- Existing spatial-source and default unpooled-joint regressions remain passing.

These are local synthetic controls, including the real adapter entry. They do
not claim native Windows execution, private RGB separation, physical identity,
calibrated optical transmission or a validated ranking/operating point.

## Code identity for handoff

The local artifact fingerprint over schema/spec/seven code hashes is:
`3425f2db6f176ed52db382b4c2b4db4e94a6cccbf516e6270005ad8806815bcf`.
This is the new diagnostic's code/spec identity, not a private measurement result.

| File | SHA-256 |
|---|---|
| `tests/diagnostics/s11_joint_context_run.py` | `25e2b5c877c8243a4f6db418acaac9acb36a28ad5bf3dbaf504c8d9dc719e726` |
| `tests/diagnostics/s11_spatial_context_probe.py` | `95e3619650da9dc9b31876ed1072608beb9c958deb8ae44cec2273200d7507b7` |

The input source artifact remains
`6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910`.
Original source-runner bytes and production code are unchanged. The retained
joint output is not regenerated; new runner/probe bytes naturally change a future
joint-mode code fingerprint and do not revise old receipts.

## Windows boundary and remaining unknown

Follow [Color-side measurement — existing saved outputs](../../40-operations/s11-o2-local-shadow-evaluation.md#color-side-measurement--existing-saved-outputs)
on the existing spatial-context-001 directory. Return machine summary, 3-output
hash checks, 32-input preservation and fixed CSV subsets: Accum idx10/15 native
all five sectors/three widths/near-far; BASE idx11 native support; unresolved
idx0/20 center control. Numeric arrays remain local. No new human question,
video/bundle read, label edit, overlay or detector run is required.

Whether private color sides differ usefully, overlap, or become unavailable is
unknown until that measurement. Reflections and illumination can create identical
color evidence; the same data cannot independently establish causality. Existing
mask construction may remove color cues. No universal sign, magnitude rule,
spatial continuity or identity gain follows from this diagnostic. W4-R1 remains
closed without promotion; W4-R2 and O2 acceptance remain unmet, FIELD FAIL /
NOT_EVALUATED unchanged. [Validation owner](../../30-validation/s11-interface-observability-witness-validation.md#recorded-band-color-side-controls)
and [canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
continue to own acceptance and field interpretation.

## Windows measurement report received — 2026-10-06

The user returned the bounded `color-side-001` execution report and all three
fixed CSV subsets (60 / 18 / 60 rows). Receipt/output/input checks below are
**attributed Windows results**, not independent local rehashes: private files
were not opened here. The user previously explained that chat transfers may
use OCR; the Windows agent reads files directly. Do not attribute a transfer
discrepancy to the underlying calculation without checking its saved values.

### Execution and provenance as reported

- Receipt and report schema: `s11-o2-color-side-v1`; receipt COMPLETE.
- Color artifact: `3425f2db6f176ed52db382b4c2b4db4e94a6cccbf516e6270005ad8806815bcf`,
  equal in receipt/report and equal to the local code/spec handoff fingerprint.
- Source artifact: `6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910`.
- Source receipt SHA: `8cd5458850df83c132ce1434d0025f34dc449ca8a0528042251676269a2724cb`.
- Source experiment SHA: `08d05685f123fe526090121ead27655c62f1fa7eee59068bd3a65ec5608857d3`.
- Three hashed outputs plus receipt (four files); all three output rehashes
  reported equal to receipt, and all 32 inputs before=after=current bytes.
- Reported output hashes: experiment
  `d41602872696760457518e097d79016f0cff8fe32a44c4b35225a4559bc25788`,
  summary `fc23ba60cb68f6dbfc9784eb06a63db3f89402b18244d2880bdc61baded7d76c`,
  CSV `e1a0e3e6fadf83457b3301dba32fb8c13bf09f2a6dd300fbd3a74f742d29a277`.
- No video/bundle/labels reopened; no detector, decode, label change or new
  human judgment. FIELD FAIL / NOT_EVALUATED, auto_acceptance=false,
  production_decisions_emitted=false and numeric_localization=NOT_MEASURED.
- The return does not separately name the executed ZIP commit or individual
  runner/probe hashes. Matching artifact identity is recorded above; no exact
  executed commit is inferred from it.

The report preserves review-002 f14386 / BASE / rev14 / 124 points and
review-003 f16280 / Accum / rev4 / 158 points. Reported pair-state counts are
479 observed + 265 unavailable + 0 no-paired = 744 for BASE, and
701 + 247 + 0 = 948 for Accum. These equal points × 3 widths × 2 regions;
they are correlated measurements, not independent samples or correct decisions.

Detailed arrays and CSV subsets remain in Windows `color-side-001-notes/`:
`color-side-detail.json`, `bundle-1-main-review-003-idx10-15-native.csv`,
`bundle-2-aux-review-002-idx11-native.csv`, and
`bundle-3-unresolved-review-002-idx0-20-center.csv`.

### Bounded interpretation of the transferred rows

- **Accum main comparison:** idx10 has 27 observed / 3 O1-unavailable pairs;
  idx15 has 30 observed / 0 unavailable. All 15 idx10 near gray deltas are
  negative (−50.351 to −5.340); idx15 near gray deltas range −0.105 to +8.286
  (14 positive, one slightly negative). This is a descriptive difference on
  these recorded supports, not calibrated transparency or an operating rule.
  Far results vary with X/width: idx10 X=[1388,1473), BW6 far has gray +10.610
  while its near is −30.935. Preserve both regions and all widths.
- **Color contribution:** nonzero B−G/R−G side changes occur in both identities.
  They show recorded chromatic variation; they do not establish added identity
  discrimination over gray. No matched-gray physical counterexample, classifier
  ablation or independent validation is supplied by these aggregate rows.
- **BASE auxiliary negative:** idx11 has 8 observed / 10 unavailable pairs.
  Its six observed near gray deltas are also negative (−38.405 to −8.646),
  overlapping the Accum positive's near range. X=[130,236), BW8 far is −68.847.
  Thus negative/large gray contrast is not specific to an interface. This is
  a counterexample to a universal sign/magnitude claim, not a pooled task or a
  same-Glass matched experiment. Unavailable values remain null.
- **Unresolved BASE control:** idx0 and idx20 each have 18 observed / 12
  unavailable pairs. Their vectors vary across X/width/region; numerical
  differences do not resolve the user's physical ambiguity. Historical labels
  are not promoted to certain opposite truth to fit those differences.
- Per-candidate paired-column counts can differ even at the same X/BW. Each
  row uses identical pixels across its channels; that does not imply identical
  support between idx10 and idx15. Aggregate differences cannot establish
  columnwise persistence, connectivity, or a physical boundary.

### Initial transfer discrepancies (resolved below)

1. The transferred summary says Accum baseline MATCH / **1812**; earlier
   transferred prose and the handoff specified **1012**. The private source
   bytes were not locally inspected to establish that earlier number. Read the existing color report's
   `baseline_band_count` and source report's baseline count; do not silently
   replace either value. Baseline counts differ from the 948 color-pair count.
2. Accum idx10 / native_path / X=[1558,1643) / Y=220 / BW12 / near is transferred
   as delta_B=−24.398, delta_G=−21.033, delta_B_minus_G=−3.357. Subtracting the
   displayed B/G gives −3.365, a discrepancy of 0.008, beyond three-decimal
   rounding. Return those three exact saved CSV values (and the corresponding
   JSON pair only if needed); no new calculation window or measurement.
3. The pasted summary omits the `Frame` header although each row includes it;
   current `_write_color_outputs` emits the seven-column header including Frame.
   Its status literal is `o1_unavailable`, not `01_unavailable`. Treat these as
   transfer-format differences pending source text, not reasons to edit outputs
   or modify the runner.

### Saved-value confirmation received — 2026-10-06

User attachment `56077.jpg` shows the Windows saved-file confirmation. Attachment
SHA-256: `a12a4f403ed3d981b6479e775fbae7ee37431e2e3a7d67bd2d7db35d8f865f57`.
This is an image of the Windows report, not direct local access to its CSV/JSON.

- Review-003 `experiment.json`: `baseline_band_count=1812`,
  `baseline_status=MATCH`; BASE remains 1416. The operational handoff's 1012 is
  corrected to 1812. The runner requires reconstructed baseline equality with
  the source report's entire `baseline_check` before publication, then copies
  its count into the color report. Thus the reported successful run supports
  source/count consistency; no new measurement or private rehash was performed
  here. Earlier 1012/2428 prose is superseded for this source; the corrected
  combined inventory is 3228 bands, not independent samples.
- Exact saved CSV values for the specified Accum idx10 BW12 near row:

  | Field | Reported saved value |
  |---|---|
  | delta_B | -24.389599193909543 |
  | delta_G | -21.0327026421854 |
  | delta_B_minus_G | -3.3568965517241445 |

  Local arithmetic on these reported numbers gives exactly the reported B−G
  (float difference 0.0). Three-decimal B is **−24.390**, not the originally
  transferred −24.398. G=−21.033 and B−G=−3.357 were correctly rounded. No CSV
  calculation inconsistency remains supported by this check.

Both substantive intake questions are closed on attributed Windows evidence.
The omitted Frame header and O1/01 lettering in chat remain presentation-only;
the source generator owns those literals, with no output repair requested.
Measurement execution/receipt review is complete on the transferred evidence,
without identity promotion. Preserve all original outputs. No additional private
media, user rejudgment, detector run or threshold selection is needed to close
this intake. W4-R2 entry remains unmet.

## Added-information assessment and measurement disposition — 2026-10-06

Scope: the reconciled transferred rows, existing synthetic controls, measurement
implementation and current candidate-identity acceptance contract. No private
arrays were accessed, no score fitted, and no new Windows work was performed.

### What was established

The measurement retains chromatic degrees of freedom that a gray projection
does not retain. The local equal-gray/different-BGR control demonstrates that
representation difference. The Windows report establishes nonzero chromatic
side differences in this private scene on the reported visible support.
These are different claims: a nonzero opponent delta is not, by itself, a
private equal-gray/opposite-identity control or proof that color repairs a
detector failure. Production already has some color-derived masks/features;
this finding applies to the specified gray side projection, not an assertion
that the whole detector is color-blind.

The following arithmetic covers **all 15 near rows per main candidate**
(five X strips × three widths), using the transferred three-decimal values.
Far rows remain separately retained and are not discarded from the evidence.
Ranges describe correlated measurements; no threshold or candidate score is
derived from their extrema.

| Channel delta | idx10 range; positive/negative rows | idx15 range; positive/negative rows |
|---|---|---|
| gray | −50.351 to −5.340; 0/15 | −0.105 to +8.286; 14/1 |
| B−G | −5.604 to +1.800; 6/9 | −1.103 to +2.029; 11/4 |
| R−G | −0.651 to +5.292; 12/3 | −1.766 to +0.488; 3/12 |

The main candidates differ already in the same-support gray component of this
measurement. Thus showing their color difference cannot isolate an incremental
color benefit. Both identities have positive and negative opponent deltas, and
their one-dimensional ranges overlap. This rules out treating mere nonzero color
or a universal opponent sign as physical identity; it does **not** prove that a
multivariate color/geometry mechanism cannot work. Choosing a favorable X,
width, sign count or vector norm after this result would create a new hypothesis
requiring its own controls, not complete the present experiment.

The color runner also changes the reduction relative to pixel-weighted O1 band
means: it averages same-column differences with equal column weights. Any future
gray-versus-color comparison must use this runner's gray channel with identical
support, not attribute a changed weighting/denominator to color information.

### Existing controls remain useful, with distinct roles

| Control | What it supplies | What it cannot establish |
|---|---|---|
| Accum idx10/idx15 | Same-frame, same-Glass, same-X reviewed positive/negative comparison; central strips have full paired-column support | Added value of color over already-different gray evidence, independent generalization, or physical transparency |
| BASE idx11 | Reviewed structural negative, including observed large negative gray contrasts; useful counterexample to generic brightness-sign reasoning | A same-Glass matched alternative to Accum, a negative label for missing pixels, or a negative with the same full color vector |
| BASE idx0/idx20 | Human-unresolved competing boundaries; useful ambiguity/abstention control | Certain opposing identity truth or a supervised success for whichever candidate a new rule favors |

Candidate identity remains the target; these row signs are neither sector
near/off judgments nor scalar truth. Human absence of a visible interface at
idx15 does not require every optical measurement there to be zero. Full band
availability does not add physical identity, and unavailable bands cannot be
used as a structural-negative feature. No matched-support claim is made for
the edge strips with different paired-column counts.

### Decision and next design gate

**Fixed color-side measurement: COMPLETE, CLOSED WITHOUT PROMOTION.**
Information retention is supported. Incremental candidate-identity benefit is
**NOT ESTABLISHED**, rather than measured to be absent. W4's challenger remains
open; W4-R1 is not reopened and W4-R2/O2 acceptance is not satisfied.

No additional Windows extraction is required to reach this disposition.
Inspecting more columns could answer cancellation or spatial-distribution
questions, but would not alone supply independent physical truth or isolate
added identity benefit. Do not request another general-purpose inspection of
the same two frames merely because the classifier is still missing.

The next local design must specify one candidate-level mechanism before further
private execution, using the existing witness architecture's support/opposition
contract. Its reviewable entry requirements are:

1. Name the observable and explain how geometry-indexed color/gray evidence
   supports a two-sided region interpretation while retaining reflection or
   internal-structure opposition. State how it differs from prior gray-profile,
   alignment, spatial-continuity and polarity-only attempts. A new scalar color
   magnitude or majority sign is not that explanation.
2. Define a gray-only comparator and gray-plus-color challenger with identical
   points, masks, paired columns, reduction, missingness and evaluation target.
   Include achromatic interfaces and chromatic artifacts so that adding color
   is not equivalent to requiring color. Preserve an unresolved output and
   measure coverage as well as errors under the existing W3 evaluator.
3. Identify independent, physically reviewed controls capable of exposing a
   gray-only error or ambiguity and testing whether color corrects it without
   creating new false positives. Exact equality of gray numbers is not required;
   nor may controls be selected to suit the observed opponent signs. Current
   Accum controls remain development evidence, BASE idx11 stays auxiliary, and
   idx0/idx20 stays unresolved. The current return supplies no new independent
   calibration/holdout evidence.
4. If that mechanism or its counter-controls cannot be justified, record the
   specific gap before requesting any new frame, human review or acquisition.
   Do not repeat the closed saved-material inventory or prescribe SPL#2/#3 as
   inputs. No new descriptor, threshold sweep, detector change or private run
   is implied by these design requirements.

This gate is a concrete design obligation, not a claim that every interface must
be optically distinguishable or that controlled acquisition is already required.
The existing [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md)
and [O2 acceptance owner](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance)
continue to own implementation and promotion requirements.

## Candidate mechanism contract and local falsification — 2026-10-06

The [candidate-conditioned region competition contract](../../20-architecture/s11-interface-observability-witness-architecture.md#w4-candidate-conditioned-region-competition--prototype-contract)
now specifies the proposed observable, reuse owners, exact support/geometry
boundary, competing appearance explanations, opposition and candidate-level
evidence. This is a concrete **design contract**, not an implemented classifier.
The [validation matrix](../../30-validation/s11-interface-observability-witness-validation.md#candidate-conditioned-region-competition-controls)
distinguishes executed representation checks from future prototype requirements.

Source review found that four-band step/ramp/ribbon fitting already exists in
`profile_scale`; raw material partition context already exists in
`oil_material_path`; ordered color-side columns and unpooled gray also already
exist. Recoloring the profile or pooling the color rows would not add the proposed
joint chromatic arrangement. The existing source adapter and probe remain the
future reuse points; no competing loader, measurement implementation or private
data run was introduced.

Added a polarity-reversed pair of synthetic controls in
`tests/unit/test_s11_color_side.py`. Alternating equal-gray BGR colors form
horizontal runs in one raster and a staggered pattern in the other. Every band
contains the same two colors per ordered column with identical support. Results:

- Full saved-gray arrays are identical (gray30 everywhere).
- Full color-side result objects are identical, including bands, ordered
  column deltas, counts, means, eligibility and no-decision flags.
- Horizontal RGB adjacency differs in every row. This verifies a loss of joint
  arrangement in the current representation, without assigning either image
  an Oil or structure identity.

Executed locally:

```text
.venv/bin/python -m pytest -q tests/unit/test_s11_color_side.py tests/unit/test_s11_lateral_context_probe.py tests/unit/test_s11_joint_context.py
77 passed in 2.15s
```

No production or diagnostic-runner/probe bytes changed. The reported color
artifact and existing Windows outputs remain valid; a new private run is not
needed to verify this test. No region model was exercised by the 77 passing tests.

**Disposition:** a region hypothesis built only from the existing reduced
color-side output is ruled out as a reconstruction of full 2-D adjacency.
The raw-RGB region-competition hypothesis is PROPOSED, with implementation and
identity benefit unverified. The contract requires a support/color factorial
ablation because an envelope adds pixels between old bands; it explicitly
retains structural/reflection ambiguity and unresolved returns. It cannot enter
Windows or W4-R2 merely by passing this representation test. Next local work
must choose and falsify a concrete bounded region model under that matrix,
including achromatic positives and chromatic/structural counterexamples.

## Region prototype implementation and Windows handoff — 2026-10-06

This section supersedes the preceding design-stage next action. The frozen
[prototype contract](../../20-architecture/s11-interface-observability-witness-architecture.md#w4-candidate-conditioned-region-competition--prototype-contract)
is now implemented as an offline appearance fit, with a
[bounded Windows handoff](../../40-operations/s11-o2-local-shadow-evaluation.md#region-competition--existing-saved-outputs).
It is not an implemented/accepted physical identity classifier. The completed
color-side experiment remains CLOSED WITHOUT PROMOTION.

### Implementation and reuse

- `s11_region_competition.py` owns four fixed linear raw-pixel models (smooth
  plane, recorded-side offset and two centered ribbons), held-out column loss
  and same-side immediate RGB/gray adjacency. A dedicated model module avoids
  placing model fitting in the extraction probe; acquisition is not duplicated.
- `s11_joint_context_run.py --region-competition` reuses receipt/raster/point/
  baseline verification, exact role/alias binding, file bounds and preservation.
  Modes are mutually exclusive. It reads only the original saved spatial output.
- `measure_color_side` supplies the existing BGR/gray/mask/band support validation;
  its code and the spatial producer remain unchanged. The new model then uses
  raw pixels, not the color means, on four fixed support/channel ablations.
- All point/width/view/model rows remain present, including unavailable/rank-
  deficient fits. CSV exposes losses and adjacency, JSON also owns coefficients,
  original/added support, recorded band reasons and observed indicator-edge pairs.
  No model winner, identity score, threshold, scalar or temporal result exists.
- O1 unavailable is not rescued by envelope support. Structural/material/static
  opposition is `not_measured`; reflected and physical steps with identical
  supplied pixels remain physically unresolved. BGR loss versus gray loss alone
  does not quantify identity gain.

Frozen source identity (no private run):

| Item | SHA-256 |
|---|---|
| Joint saved-output runner | `63b54b9f94e9274071aff561c1466c6944df2fb15741b4712740c5e5c20103a1` |
| Region model module | `3627e7c2ad6e218fa797b68500d70e7c8be1e038354bbad32c0ebcd68fb60b17` |
| New region artifact: schema/spec + eight source files | `e6d17b0d54a909f226d265b9202151d017a76f6ed427009095c19b11bb04b3e8` |
| Required original spatial artifact | `6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910` |

Schema is `s11-o2-region-competition-v1`. Three hashed outputs are
`experiment.json`, `summary.md`, `region-competition.csv`; `complete.json`
is published last after a second source-preservation check. Future code changes
produce a different artifact and must not be silently substituted for this run.

### Local verification

```text
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_region_competition.py \
  tests/unit/test_s11_color_side.py \
  tests/unit/test_s11_joint_context.py \
  tests/unit/test_s11_lateral_context_probe.py \
  tests/unit/test_s11_spatial_context_probe.py \
  tests/unit/test_s11_spatial_context_run.py
157 passed in 4.19s
```

Changed-document local paths/anchors (131 links), S11 detector governance and
`git diff --check` also pass. Production detector source is unchanged.

New model controls include both polarities of affine ramp/partition/two ribbon
fixtures, equal-gray color boundary, the complete-color-output adjacency
collision, achromatic channel normalization, support-only perturbation, held-out
pixel exclusion from fitting, mask/glare exclusion with no adjacency bridge,
crop/O1 unavailability, split/rank failure, metadata non-authority and separate
partial-path pieces. These controls establish calculational and synthetic
appearance behavior, not real Oil accuracy, visibility or structure attribution.
A first normalization assertion used an overly strict absolute tolerance at
nonzero loss (~5e-18 float summation difference); it was corrected to relative
1e-12 with a 1e-25 near-zero absolute tolerance. No model rule was tuned to
private values.

The real CLI test uses the actual spatial producer/extractor fixture, a Unicode
path, non-repository cwd, closed stdin and UTF-8 output. It verifies all views,
exact coincident role aliases, three receipt hashes and unchanged saved inputs.
Shared malformed-source guards now cover the new mode as well as old joint/color
modes. Mutation during calculation or publication produces no COMPLETE receipt.
Local tests do not certify native Windows execution.

A local synthetic workload used an 800×600 achromatic raster, 282 points of
100 columns each, three widths (6/12/18), 3,384 factorial views and 13,536 model
fits. It covered 6,345,000 envelope sample pixels and took **8.10 seconds**;
whole-process peak RSS was **154.2 MiB** and JSON serialization 9,359,642 bytes.
This is a size-oriented local smoke measurement, not private-scene timing or a
Windows throughput guarantee. The caps (262,144 per envelope, 50,000,000 summed
per case) fail before fitting; masks and exact widths can change actual work.

### Entry decision and remaining limits

READY FOR BOUNDED WINDOWS SAVED-OUTPUT EXECUTION. The three existing comparison
roles remain unchanged: Accum idx10/idx15 development pair; censored BASE idx11
auxiliary negative; BASE idx0/idx20 unresolved human control. Run all inventory
and retain all four ablations, then return the predeclared same-X slices plus
complete comparison CSV paths. No additional human judgment or source media is
needed for this step. The Windows result itself is still pending.

The prototype assumes shared affine within-patch variation plus a fixed offset;
it does not model arbitrary surfaces, curved illumination, arbitrary ribbon
widths, physical topology or material ownership. Actual partial positives,
optical counterexamples and independent recordings remain unvalidated. Full-rank
fit and lower held-out error do not establish identity. No candidate-wise
prediction/abstention efficacy is claimed from an all-UNRESOLVED appearance ledger.
W4-R2 remains unmet, O2 OPEN, FIELD FAIL and NOT_EVALUATED unchanged.

## Region Windows return and bounded interpretation — 2026-10-06

The user returned `region-competition-001` results for the frozen prototype.
This section supersedes the preceding pending-run status. These are **attributed
Windows results**, not locally rehashed private artifacts. The Windows agent
reads saved files directly; transfer to this chat may involve OCR. A malformed
chat field does not by itself establish a calculation or file-integrity failure.

### Execution receipt and provenance

- Reported schema: `s11-o2-region-competition-v1`; receipt COMPLETE; report and
  receipt artifact equal `e6d17b0d54a909f226d265b9202151d017a76f6ed427009095c19b11bb04b3e8`.
- Source artifact equals the original spatial pin
  `6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910`.
- Three output hashes reportedly match disk (experiment, summary, CSV), plus
  complete.json: four files. Actual three output digest strings were not supplied.
- All 32 saved inputs reportedly preserve before/after/current SHA. Original
  video/bundle/labels were not reopened. No new label, detector or decode occurred.
- Runtime reported: Python 3.14.3 / NumPy 2.5.2 / OpenCV 4.13.0. Elapsed run time
  was not supplied; do not infer Windows throughput from the local benchmark.
- The intended ZIP source was c2102c1. The runner digest matches its pin. The
  initially transferred model-file digest was wrong; the user confirms the
  source pin and receipt code entry match. The transfer items below are closed.
- All decision/acceptance/field flags remain NOT_EVALUATED / false / FIELD FAIL /
  NOT_MEASURED. Physical identity remains UNRESOLVED, opposition not_measured.

| Case | Frame | Revision | Origin / shape | Points | Baseline | Views / observed views | CSV rows |
|---|---|---|---|---|---|---|---|
| review-002 BASE | 14386 | 14 | [0,211] / [773,578] | 124 | MATCH/1416 | 1488 / 888 | 5952 |
| review-003 Accum | 16280 | 4 | [1199,56] / [584,462] | 158 | MATCH/1812 | 1896 / 1304 | 7584 |

Glass IDs match the handoff: BASE `8f94fb85-d98e-4c71-9c97-3085168be1b2`,
Accum `8fb6ebc7-7c56-401e-86c3-05514bf6380b`. Totals are 3,384 views, 2,192
observed views and 13,536 model rows. The remaining 1,192 views are not classified
as a particular missing/rank state from this summary alone. None of these counts
is candidate accuracy, physical coverage or independent sample size.

Local Windows notes reportedly contain all fixed comparisons: `main.csv` 480,
`auxiliary.csv` 144, `unresolved.csv` 480 rows. Fixed excerpts have 32/16/32 rows.
Paths are under `data/region-competition-001-notes/`; original results under
`data/experiments/region-competition-001/`. Those files are not present locally.

### Exact transferred loss excerpts

These are the rounded `heldout_mse` values as supplied, not a new fit. B=recorded
bands; E=candidate envelope. Same X/BW/representation is required for comparison.
The initially missing loss cell is filled from the user’s subsequent saved-row
confirmation below, without interpolation. All 80 excerpt losses are now present.

| Case / idx / basis / X / Y / BW | Support | Channels | smooth | partition | ribbon_bw | ribbon_2bw |
|---|---|---|---|---|---|---|
| r003 / 10 / native / [1388,1473) / 217 / 6 | B | gray | 0.0067251683 | 0.0041084013 | 0.0061413202 | 0.0063929794 |
| same | B | BGR | 0.0067538470 | 0.0040948949 | 0.006130124755688663 | 0.0063899493 |
| same | E | gray | 0.0054596701 | 0.0038924241 | 0.0049699842 | 0.0053469482 |
| same | E | BGR | 0.0054858414 | 0.0038910790 | 0.0049573061 | 0.0053582010 |
| r003 / 15 / native / [1388,1473) / 313 / 6 | B | gray | 0.0006410291 | 0.0006269626 | 0.0006405006 | 0.0006409431 |
| same | B | BGR | 0.0006537169 | 0.0006408335 | 0.0006530197 | 0.0006533139 |
| same | E | gray | 0.0005727846 | 0.0005628317 | 0.0005720674 | 0.0005727864 |
| same | E | BGR | 0.0005820570 | 0.0005729585 | 0.0005813221 | 0.0005818153 |
| r002 / 11 / native / [236,343) / 925 / 8 | B | gray | 0.0055946723 | 0.0055589071 | 0.0051523520 | 0.0048927346 |
| same | B | BGR | 0.0054805115 | 0.0054465033 | 0.0050497103 | 0.0047954546 |
| same | E | gray | 0.0055693106 | 0.0055465429 | 0.0053617699 | 0.0051228918 |
| same | E | BGR | 0.0054257704 | 0.0054038032 | 0.0052204422 | 0.0049884573 |
| r002 / 0 / center / [231,346) / 382 / 8 | B | gray | 0.0033467506 | 0.0029877116 | 0.0030637101 | 0.0027016671 |
| same | B | BGR | 0.0031350944 | 0.0027935731 | 0.0028801336 | 0.0025461833 |
| same | E | gray | 0.0028347237 | 0.0025919422 | 0.0027626874 | 0.0022969185 |
| same | E | BGR | 0.0026658369 | 0.0024373963 | 0.0026029125 | 0.0021728735 |
| r002 / 20 / center / [231,346) / 406 / 8 | B | gray | 0.0020757712 | 0.0019162930 | 0.0022346742 | 0.0022893094 |
| same | B | BGR | 0.0026421357 | 0.0017694755 | 0.0020758003 | 0.0021279037 |
| same | E | gray | 0.0023945746 | 0.0019433487 | 0.0017442930 | 0.0021579484 |
| same | E | BGR | 0.0022133522 | 0.0018026977 | 0.0016342486 | 0.0020086264 |

### Supported interpretation, with limits

For the main excerpt alone, the following arithmetic uses the transferred
rounded values: `100 * (smooth - partition) / smooth`. This is a descriptive
within-view residual reduction, **not a new score, threshold, prediction or
predeclared efficacy endpoint**. Channel spaces are not directly commensurate.

| Support | Channels | idx10 reduction | idx15 reduction |
|---|---|---|---|
| recorded bands | gray | 38.91% | 2.19% |
| recorded bands | BGR | 39.37% | 1.97% |
| envelope | gray | 28.71% | 1.74% |
| envelope | BGR | 29.07% | 1.56% |

1. At the stated Accum X/BW, a fixed side offset explains substantially more
   residual variation for idx10 than idx15. The difference already exists in
   gray; the excerpt does not establish incremental chromatic identity benefit.
   Partition also improves idx15 slightly, so merely improving smooth is not an
   interface certificate. Absolute partition error is smaller for idx15, so
   minimum raw error across candidates is not an identity selector either.
2. After saved-row confirmation, partition is the lowest of the four supplied
   losses in all four views for both idx10 and idx15 at this X/BW. Thus the
   ordering alone does not distinguish the positive and negative candidate.
   Model ordering describes the table, not a generated identity winner.
3. At the stated BASE idx11 X/BW, ribbon_2bw has the lowest supplied error in all
   four views. This is consistent with a different local appearance explanation,
   but does not prove a visible return or structural identity. Indicator-edge
   support was not returned; other sectors/widths remain unavailable locally.
4. Human-unresolved idx0 favors ribbon_2bw in these four views, while idx20
   favors partition on recorded bands and ribbon_bw on envelope support (both
   gray/BGR). Support changes the ordering for the *same* candidate. The original
   human ambiguity is not resolved; idx20 is not a clean negative control.
5. Added envelope pixels change both fitted and tested domains. Smaller MSE
   across supports is not an error reduction on identical observations. All
   models share adjacency numbers within a view; these repetitions are not
   four independent corroborations. Fixed-width fit, neighbor differences and
   coherent brightness patterns do not establish physical connectivity.

This supports a **bounded appearance distinction** at the returned main slice,
not a whole-candidate or cross-sector result. Do not tune a partition-gain cutoff,
count model minima as votes, promote W4-R2 or declare the whole hypothesis failed
from the unresolved control. Full 480/144/480 CSV contents have not been reviewed
here; cross-X/BW robustness and optical/material opposition remain open.

### Transfer reconciliation closed — user confirmation

The user explicitly confirmed both items after the initial report:

1. The model-file hash in the transferred message was wrong. The source pin and
   receipt code entry both use the correct digest
   `3627e7c2ad6e218fa797b68500d70e7c8be1e038354bbad32c0ebcd68fb60b17`.
   The earlier `...32c0abcd...` spelling was a transfer error, not a demonstrated
   source or execution mismatch. No further hash confirmation is pending.
2. Exact saved row: review-003 / idx10 / native_path / X=[1388,1473) / Y=217 /
   BW6 / recorded_bands / BGR / ribbon_bw:
   - `train_pixels = 1536`
   - `test_pixels = 504`
   - `heldout_mse = 0.006130124755688663`

The completed quartet is partition (0.0040948949), ribbon_bw
(0.006130124755688663), ribbon_2bw (0.0063899493), smooth (0.0067538470), in
ascending error order. This closes the missing cell and confirms the local
ordering; it does not change the prior within-view partition-versus-smooth
reduction or establish incremental color/physical identity benefit.

Execution is reported COMPLETE; both substantive transfer items are **CLOSED on
user-confirmed saved values**. This remains attributed evidence; private files
were not rehashed locally. No code, original output, model or label changed.
Elapsed time remains not_reported and is not grounds for a timing rerun.

Next examine the already-saved full main/auxiliary/unresolved comparisons
(480/144/480 rows) across X and BW, retaining model errors, support, missing
states and the four ablations. Their contents have not been received locally.
No additional measurement, repeated receipt check or human rejudgment is needed.
W4-R2 remains unmet and FIELD FAIL / NOT_EVALUATED unchanged.

## Region cross-X/BW return and denominator audit — 2026-10-06

The user returned a summary of the saved-CSV review requested after the region
run. This supersedes the preceding pending-full-review next action. The Windows
agent read saved CSVs directly; only the summary was transferred here, not the
complete pivot/pair tables, exception keys or `review.md`. Counts below are
attributed Windows findings, not independent local recomputation.

### Reported outputs and preservation

Outputs are under `region-competition-001-consistency/`, outside the original
experiment directory:

| File | Reported inventory |
|---|---|
| main-wide.csv | 120 views from 480 model rows |
| auxiliary-wide.csv | 36 views from 144 model rows |
| unresolved-wide.csv | 120 views from 480 model rows |
| main-pairs.csv | 60 nominal candidate pairs |
| unresolved-pairs.csv | 60 nominal candidate pairs |
| main-exceptions.json | 49 exception views |
| auxiliary-exceptions.json | 36 exception views |
| unresolved-exceptions.json | 86 exception views |
| review.md | Full Windows analysis, not transferred here |

The report states no missing/duplicate model during pivot, no null-to-zero
conversion, and no ties. Exception categories/keys were not supplied; these
counts must not become an independent sample size, error rate or identity vote.
The original region CSV reportedly retained its SHA before/after; the transferred
abbreviation is `41a1c138..766538e`, not a complete digest. No digest is reconstructed
from that abbreviation. No measurement, model/threshold change, video decode,
label edit or user rejudgment was performed.

### Findings supported at the reported scope

1. **Main:** all 108 finite views reportedly have partition < smooth, with zero
   smooth-better views. Both idx10 and idx15 contribute, so this relation alone
   cannot distinguish their existing identities. This does not rule out every
   possible magnitude-based or combined classifier. The mean partition/smooth
   ratio reportedly grows from 0.86 to 0.91 with BW; an aggregate trend does not
   establish monotonic behavior at every exact X/support/channel key.
2. **Model ordering:** the report gives idx15 ribbon_2bw versus partition counts
   of 28 versus 24 and describes minimum-error-model changes with X/BW. These
   are reported ordering counts, not an identity decision or a magnitude of
   improvement; their exact key sets are not locally available.
3. **Auxiliary idx11:** ribbon_2bw reportedly has the lowest error at BW8 in both
   X=[130,236) and [236,343). Partition/ribbon_bw ordering changes between the
   strips. BW>=16 is reported o1_unavailable throughout this comparison; it
   supplies no evidence of a stable ordering at larger widths.
4. **Unresolved idx0/idx20:** idx20 candidate_envelope ribbon_bw versus partition
   is reported as 10 versus 6, with ordering differences concentrated in envelope
   support. The report's 30/60 mismatch rate requires the denominator audit below.
   Neither a different minimum-error model nor a shared one resolves the human
   ambiguity, and idx20 is not converted into clean negative truth.
5. **Ablations:** gray/BGR differences reportedly have mixed signs. Main envelope
   versus recorded-band comparisons give 44 ce<rb and 10 ce>rb, with exception
   keys saved on Windows. Different supports change fit and test observations;
   these are loss comparisons across domains, not 44 improvements on identical
   observations. No incremental chromatic identity benefit is established.

The full-review return extends the excerpt interpretation: shared partition
improvement and changing model ordering do not provide an identity rule. It does
not prove that all spatial classifiers are impossible, nor does it satisfy R2.
No additional descriptor, width search, cutoff or model-to-identity conversion
is justified solely by these counts.

### Unresolved-pair denominator audit

The report says “30 mismatches among 60 comparable pairs (50%)” and separately
reports partition comparisons as 18/18. The handoff's 60 pairs are the nominal
inventory (5 X strips × 3 widths × 4 support/channel views), including unavailable
entries. Inventory count is not automatically the number of comparable pairs.
Prior availability reports suggest excluded pairs, but do not substitute for the
actual pair-table state counts. The 50% interpretation is therefore **unconfirmed**;
no replacement percentage is asserted here.

One bounded read of existing `unresolved-pairs.csv` should return:

- total pairs; both candidates eligible (each has four observed, finite model
  errors); only one eligible; neither eligible, with these categories summing
  to the total;
- within both-eligible pairs: same minimum-error model, different minimum-error
  model, and any tied minimum (either side), retaining exact stored equality;
- whether the reported 30 mismatches exclude one-sided/unavailable/null pairs,
  and what the reported partition 18/18 compares and uses as its denominator;
- the unavailable pair keys (X/BW/support/channels) sufficient to explain the
  denominator, without new appearance analysis or refitting.

Do not silently count null-versus-model as a model mismatch. If partition-only
comparison uses a different eligible set, name that set separately. Existing
files remain unchanged; a short reconciliation note may be saved outside the
experiment. The already-closed receipt/code pin and missing ribbon cell are not
reopened. FIELD FAIL / NOT_EVALUATED, original labels and human uncertainty remain
unchanged while this arithmetic clarification is pending.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: private identity failure remains unknown; source review establishes that gray side projections omit chromatic values. The transferred Windows rows report color variation and the two intake discrepancies are reconciled, but this does not establish omitted chromatic information as the cause of detector failure.
- Prior mechanisms reviewed: O1 gray/support bands, saved BGR crops, color-dependent glare/Foam owners, existing four-band profile and material partition owners, row/column pooling and joint-gradient aliases, full color-side adjacency collision, raw 2-D fixed plane/partition/ribbon models and support/channel ablations, existing candidate-guided human rationale and unresolved BASE control.
- Prior mechanisms rejected: gray alignment or color magnitude as identity, truth-Y distance, shared reflected appearance as physical continuity, missing-as-zero, label-conditioned pixel selection and private-coordinate thresholds.
- Preserved contracts: generic bounded diagnostic, exact saved geometry/provenance, independent Oil/Foam, unchanged labels, fail-closed unavailable support and separate Windows field acceptance.
- Difference from prior failures: fixed same-pixel color and raw-pixel region models test information retention/appearance with separate support ablations before any physical classifier; it grants no selection or production authority.
- Logic-map impact: NONE — the saved-output diagnostic does not alter the executing detector path or production publication.
- Failure-registry impact: NONE — neither synthetic controls nor the attributed Windows color rows establish a private causal failure or field repair.
