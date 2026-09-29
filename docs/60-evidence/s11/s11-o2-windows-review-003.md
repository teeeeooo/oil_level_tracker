# S11 O2 Windows review-003 — Accum candidate identity reviews

Recorded: 2026-09-28. Source: user-transferred Windows completion report.
Private media, packet, labels and bundle receipt were not opened or rehashed on
this machine. This is bounded annotation-workflow evidence, not classifier or
field qualification. The [work plan](../../00-project/work-plan.md) owns current
sequencing; the [O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md)
and [validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own workflow and acceptance. This does not amend
[canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).
Private filenames, absolute paths and business identifiers are omitted here.

## Reported execution and candidate binding

| Item | Transferred value |
|---|---|
| Review | review-003, newly created |
| Bundle | Existing R22-3 bundle reused; no detector rerun |
| Target | Accum, source frame 16280, timestamp 679.0117 s |
| Partition | regression, previously reviewed checkpoint |
| Recording group | recording-A, same original recording group as review-002 |
| Bundle/source receipt | Registered, s11-o2-bundle-link-v1 |
| Candidate input index | 19, discovered in current packet rather than assumed |
| Kind / source | oil_air / calibrated_high_recall |
| Canonical Y | 213, source-frame Y |
| Witness geometry | candidate_center only, five sectors spanning X [1199,1661), Y213 |
| Witness SHA-256 | 8ccc113e5dc3cf1a6738bb10e6be0ee6cd2419ab9f19796e7852e64a3ac70b20 |

The report identifies reuse of the existing bundle but does not independently
restate its detector/resolver/witness version fields or continuation-tool commit.
Earlier user-attested ZIP identities are not newly verified execution hashes.
The overall X extent does not specify each sector's individual interval and must
not be substituted for that geometry when recording path judgments.

## Human judgment reuse and scope

Windows reported checking the same video, exact zero-based frame, Glass,
source-frame coordinate, source and kind against the earlier direct human review
that confirmed the interface near Y213. The stored candidate identity is
**interface**, with review basis **prior_direct_review_exact_geometry_checked**.
No repeated image question was asked. Discarded LVLM readings Y137 and Y123 were
not used as truth.

Visibility is **visible**. No contour or path_reviews were generated. Identity
reuse does not certify a horizontal Y213 line across all five sectors, numeric
position tolerance, or another candidate's native path. The report's unusual
phrase about correspondence is treated as its claimed matching result, not a
separate technical verification method.

## Reported persistence and remaining scope

- Revision **0 → 1**; logical label SHA prefix **fdceb10b... → 373594f7...**.
  Only prefixes were supplied; no full hash is reconstructed here.
- Inventory: **27 candidates = 1 interface + 26 unreviewed**.
- Review-002 revision 14 / SHA prefix `102919b6...` and visibility remain unchanged.
  Its r10 frozen snapshot (`ce9c4373...`) and NOT_EVALUATED readiness report were
  reported preserved. Neither is an evaluation of review-003.
- No code modification or detector rerun was reported. Review-003 freeze,
  prediction evaluation, owner strings and classifier-status output were not
  included in this summary; do not infer those checks from identity completion.

This closes the requested single-candidate identity task by user report. The
frame remains partially reviewed. Alongside the BASE records it supplies another
regression example; it does not establish independent-recording diversity or
holdout performance.

## Revision 2 — material_path identity reviewed directly

The subsequent user-transferred report identifies the current packet's
`candidate_input_index=10`, `source=material_path`, `kind=oil_air`, canonical
source Y217. Witness SHA:
`315e0aee4d41f428b166106519c5af0bb140b74a1b7f3ad6f60a36bb58d74fd4`.
Its native path has five sectors with source Ys spanning 209–220. Individual
current sector coordinates were not included in this report.

The guide displayed the native path in cyan and reference Y213 in white. The user
was asked whether the path, considered as a whole, represents the actual liquid
interface and answered **interface**. Earlier evidence explicitly deferred this
candidate's physical judgment, so a new direct question was appropriate; no label
was inferred from Y213 proximity. The stored basis is **direct_human_review**.
The reference line is not certified contour truth across all X positions.

- Revision **1 → 2**; logical label SHA prefix **373594f7... → de4ac088...**.
- Inventory: **27 = 2 interface (IDs 10 and 19) + 25 unreviewed**.
- No path_reviews or contour were generated. Candidate 10's identity does not
  certify any of its five sector positions or establish independent support for
  candidate 19; shared feature derivation remains a separate question.
- This report does not restate owner values, visibility status, other-review
  hashes or freeze/evaluation checks. The earlier reported state is retained as
  historical evidence, without claiming a new verification of those fields.

## Revision 3 — five native-path positions reviewed directly

The user reports a slightly inclined interface and directly confirms all five
candidate 10 native-path positions as **near_interface**. S1–S5 below are the
review display labels, not assumed array indices. Source X extents are half-open
under the existing geometry contract; Y is source-frame Y.

| Display segment | Source X | Native source Y | Judgment |
|---|---|---|---|
| S1 | [1218, 1303) | 209 | near_interface |
| S2 | [1303, 1388) | 210 | near_interface |
| S3 | [1388, 1473) | 217 | near_interface |
| S4 | [1473, 1558) | 219 | near_interface |
| S5 | [1558, 1643) | 220 | near_interface |

- Revision **2 → 3**; logical label SHA prefix **de4ac088... → da8bbb92...**.
- Candidate 10 native-path summary: near 5, off 0, uncertain 0, unreviewed 0;
  reviewed point count 5, qualitative review coverage 1.0.
- Identities 10 and 19 remain interface; visibility remains visible. There are
  still 25 unreviewed identities out of 27 proposals.
- No candidate-center reviews or contour were generated. Full qualitative
  review coverage does not establish numeric error, an accepted tolerance,
  independent support, or classifier performance.
- Review-002 revision 14 / SHA prefix `102919b6...`, its frozen r10 snapshot
  (`ce9c4373...`) and NOT_EVALUATED readiness report were reported unchanged.
- No code change, detector rerun, freeze or evaluate was performed in this step.
  Stored reviewer/basis fields were not restated in this transferred summary;
  the user explicitly reports direct confirmation of the five positions.

## Revision-3 freeze and no-prediction readiness — transferred completion

Windows reports successful pre-status, freeze, evaluate and post-status with no
validation errors. Label revision 3 and logical SHA prefix `da8bbb92...` remained
unchanged. Owners are reported as `reviewer-001` for label_owner and split_owner;
dataset_id is `o2-regression-review`. Packet/witness and bundle-link correspondence
were reported valid; this machine has not independently checked the private files.

| Artifact / field | Reported value |
|---|---|
| New frozen file | frozen-review-003-r3.json |
| Frozen schema | s11-o2-frozen-labels-v2 |
| Frozen content SHA-256 | 85951f3044f0c53958663cc3be5f0a8d6128f9fe63cf5a4791d16fa0cfe1a929 |
| New readiness file | readiness-review-003-r3.json |
| Report schema | s11-o2-shadow-report-v2 |
| Status / auto_acceptance | NOT_EVALUATED / false |
| prediction_sha256 | null |
| frozen_labels_sha256 | Reported equal to the frozen content hash |
| Field disposition | FIELD FAIL |

Candidate 10 retains five near-interface native points, no off/uncertain/unreviewed
points and qualitative review coverage 1.0. Identity counts remain two interface
and 25 unreviewed, visibility visible. Candidate 19 has no native geometry; its
identity does not create a native path.

Across all 27 proposals, native-path totals are near 5, off 0, unreviewed 24,
reviewed 5, coverage approximately **5/29 = 0.1724**. Candidate-center totals are
near 0, off 0, unreviewed 129, reviewed 0, coverage 0. These counts do not mean
that each proposal has native geometry. Candidate 10's five candidate-center
points are available for review but all unreviewed: **available witness geometry
and a derived status inventory are not automatically generated human labels**.
No candidate-center path_reviews were reported saved.

Localization was reported not_measured: matched sectors 0, unmatched 10,
reviewed contour coverage 0, unmatched positive candidates 2 (IDs 10 and 19).
The existing evaluator places these sector metrics under
`localization.all_interface_proposals`; the two positives contribute five native
points and five candidate-center fallback points respectively. This is absence of
reviewed numeric contour matches, not model misclassification. Supported-proposal
count 0 is expected without predictions and does not mean the model rejected them.

### Report wording and named serialization uncertainty

The report calls contour “absent (undefined)”. `undefined` is not a JSON value,
and current evaluator validation reads each `case["contour"]` directly. Earlier
reports said no contour was created; that does not prove whether the serialized
case field is an empty list, missing, or was inspected at a different level.
Successful validation and this wording must not be used to silently equate those
states. At the next read-only extraction, report the exact case-level JSON path,
key presence and value/type, without editing labels to fit an expectation.
The report's shorthand `localization.status` likewise is not a verified full
JSON path. Physical judgments remain unchanged by these reporting questions.

Review-002 revision 14 / SHA prefix `102919b6...`, its r10 frozen hash
`ce9c4373...` and NOT_EVALUATED readiness were reported preserved. No combine,
code change, detector rerun or new human labels occurred in this step.

## Next bounded task after readiness

Pause additional human questions. Prepare a read-only label-to-witness comparison
from the existing reviewed examples, keeping identity and qualitative path labels
separate. Resolve the exact contour/metric paths during extraction, and record
the source label revision and hash for each input. In particular review-002's r10
snapshot lacks its later negative labels and must not stand in for revision 14.
Inspect existing extraction helpers before adding code. Use only existing
measurements, preserve missing values and shared derivation, and assess a named
discrimination hypothesis rather than treating source names as independent votes.
This regression set cannot establish thresholds, holdout performance or field PASS.

## Revision 4 — one native-path negative reviewed, 2026-09-29

The user reports completion of the single additional review requested after the
[corrected BASE comparison](s11-o2-windows-review-comparison.md). No further
candidates were reviewed and no detector rerun or threshold change occurred.
This is transferred Windows evidence; private inputs were not checked locally.

Selection used shared exact X intervals and median absolute Y distance from
candidate 10, without alignment/contrast filtering. The supplied ranking lists
candidate 15 (five common intervals, 96 px), 13 (five, 172 px), 11 (five, 198 px),
12 (three, 96 px), and 16 (three, 96 px). Candidate 15 was selected; no duplicate
full path was reported. Candidate 14, previously listed among unreviewed native
candidates, is absent from this ranking; its exclusion reason was not supplied,
so exhaustive ranking is not independently established. This does not invalidate
the explicit human judgments on the selected geometry.

Candidate 15 is `material_path`, identity **non_interface**, with artifact_tags
**[]** (no tag specified). Its witness SHA is supplied only as
`d9fd8e43...71009`. Descriptive prose about reflection/structures inside the oil
region must not silently become a stored artifact tag. Canonical Y, kind and
stored reviewer/basis fields were not restated in this summary.

| Reported sector | Source X | Native source Y | Human judgment | Absolute Y distance from candidate 10 at same X |
|---|---|---|---|---|
| 0 | [1218, 1303) | 317 | off_interface | 108 |
| 1 | [1303, 1388) | 328 | off_interface | 118 |
| 2 | [1388, 1473) | 313 | off_interface | 96 |
| 3 | [1473, 1558) | 295 | off_interface | 76 |
| 4 | [1558, 1643) | 296 | off_interface | 76 |

The distances above are local arithmetic from supplied geometry: median 96 px,
range 76–118 px. They are proposal-to-proposal distances, not measured errors
against human contour. Sector 0–4 are retained as reported; earlier candidate 10
S1–S5 were display labels, so cross-candidate matching uses X geometry rather
than assuming identical sector numbers. Native qualitative coverage is 5/5.

- Revision **3 -> 4**; logical label SHA **da8bbb92...bf9e0 -> 5cbebd88...089e**.
  Digests are partial and are not reconstructed here.
- Candidate 10 retains interface identity and five near native judgments;
  candidate 19 retains interface identity. Candidate-center judgments and numeric
  contour were not generated. Prior visible status is not newly restated.
- Derived current identity inventory, assuming the reported single-candidate
  change: **27 = 2 interface + 1 non_interface + 24 unreviewed**.
- Derived native inventory: **29 = 5 near + 5 off + 19 unreviewed**, with no
  uncertain judgments reported. This is arithmetic from earlier inventory and
  the new review, not a newly executed status result on this machine.
- Four history snapshots are reported with the previous SHA retained. The
  summary names `labels.json.history`; do not infer a switch away from the
  established v2 active label file without checking the actual current path.
- Packet, bundle-link and `frozen-review-003-r3.json` were reported unchanged.
  The r3 frozen/readiness artifacts do **not** include candidate 15's new labels
  and must not be used as the current comparison input. No new classifier result
  or field qualification is reported.

This adds an **identity-negative/off** control, not an **interface/off** control.
Accum still has no reviewed misplaced segment belonging to an interface-labeled
candidate. Consequently a candidate 10 versus 15 feature comparison cannot
isolate localization independently of identity. Nor does one relatively distant
negative certify difficult near-boundary reflection discrimination.

Next, stop human questions and compare those two candidates' existing native
measurements on Windows using current revision-4 labels and exact geometry joins.
Reuse extraction/validation helpers and write a new output; preserve old reports
and frozen files. Keep Accum widths 6/12/18 separate from BASE widths 8/16/24.
Return compact per-width distributions for above/below alignment and signed/
normalized contrast, plus common-X point comparisons where useful. Compute all
summaries from the same rows and retain missing/null counts. This tests whether
the proposed alignment cue also responds to the known negative; it does not
select a threshold or demonstrate generalization. Candidate 19 remains an
identity-only positive and contributes no native rows. Record current input
revision/hash and report preservation before/after; no additional freeze or
detector rerun is needed for this descriptive comparison.

## Revision-4 native comparison returned, 2026-09-29

Windows reports a new `idx10_idx15_native_path_comparison.json`, containing 30
scale rows (two candidates times five sectors times three widths), summaries and
input hashes. Current label logical SHA remains `5cbebd88...089e`, revision 4;
the r3 frozen snapshot was preserved and not used as current truth. All five
exact X intervals matched; only native_path geometry was measured. Input packet
file SHA `49c3aef5...affd` and label byte SHA `b9ec72be...d3e4` were reported
unchanged before/after. Partial byte and logical hashes are distinct evidence.
No new annotation, contour, detector run or operating point was produced.

Reported medians and ranges, rounded as transferred:

| Width | Field | idx10 interface/near median [min, max] | idx15 non-interface/off median [min, max] | Range overlap |
|---|---|---|---|---|
| 6 | above alignment | 0.8693 [0.6766, 0.9786] | 0.6068 [0.3663, 0.6805] | yes |
| 6 | below alignment | 0.8814 [0.7813, 0.8880] | 0.5735 [0.3272, 0.6942] | no |
| 6 | signed delta | -0.0944 [-0.1975, -0.0660] | 0.0182 [0.0044, 0.0222] | no |
| 6 | normalized delta | -0.9777 [-2.3984, -0.8997] | 0.2220 [0.0892, 0.6477] | no |
| 12 | above alignment | 0.7704 [0.6423, 0.9426] | 0.6002 [0.3317, 0.6157] | no |
| 12 | below alignment | 0.8271 [0.7173, 0.8640] | 0.6004 [0.3071, 0.7220] | yes |
| 12 | signed delta | -0.0843 [-0.1267, -0.0522] | 0.0177 [0.0054, 0.0291] | no |
| 12 | normalized delta | -1.1327 [-2.6186, -0.4211] | 0.3163 [0.1476, 0.7094] | no |
| 18 | above alignment | 0.7229 [0.6314, 0.9220] | 0.5867 [0.3323, 0.6362] | yes |
| 18 | below alignment | 0.8206 [0.7261, 0.8437] | 0.5957 [0.3240, 0.7322] | yes |
| 18 | signed delta | -0.0881 [-0.1463, -0.0209] | 0.0226 [-0.0007, 0.0325] | no |
| 18 | normalized delta | -1.2073 [-2.7689, -0.1824] | 0.4227 [-0.0177, 0.7370] | no |

Each candidate/width/field reports five present values and zero null or missing.
Local arithmetic confirms the twelve overlap flags from the supplied extrema;
private raw values and medians were not independently recomputed here.

The prose claim that candidate 15 has delta >= 0 throughout is incorrect:
width 18 minima are -0.0007 signed and -0.0177 normalized. The valid conclusion
is disjoint ranges for these two candidates, not perfect separation by sign.
Nor is "strongest discriminator" established generally: one positive and one
negative candidate in one frame provide no calibrated classifier ranking.
Normalized delta derives from signed delta and a local denominator, so their
joint separation is not two independent corroborating votes.

Together with BASE, this closes the requested descriptive comparison: contrast
separates this Accum pair, but BASE near points have both polarities and overlap
its off controls; above-band alignment separates BASE's interface-location groups
at two widths, but structural controls also score inside the near range. Neither
a universal polarity rule nor a universal alignment rule is justified. Do not
equate Accum 6/12/18 px widths with BASE 8/16/24 px widths. No rule is fitted from
these regression checkpoints, and their identity/localization labels remain
separate.

### Transition from repeated comparisons to an O2 experiment

Stop additional per-candidate comparison requests on these reviewed frames.
Current code inspection confirms the existing shadow evaluator accepts imported
candidate decisions with frozen-label/witness hashes and classifier artifact
identity. It does not implement the classifier; its path summaries report human
judgments and candidate support, not a separate predicted near/off confusion
matrix. A future localization predictor must therefore have an explicit separate
prediction/evaluation contract rather than masquerade as candidate identity or
invent numeric contour truth.

The next decision is the experiment's data split, before choosing a model or an
operating point. The existing V3 validation owner and prediction loader require
development/calibration provenance; regression cannot select the operating point.
Keep reviews 001/002/003 as regression. A bounded Windows inventory should report
available original recording groups and truly unused episodes using anonymous
IDs, including copied/trimmed/transformed descendants and prior review exposure.
Do not relabel current reviews, create splits automatically, or pretend adjacent
frames are independent recordings. With the current recording-group partition
guard, episode-only separation within one recording requires an explicit leakage
assessment and contract change, not a filename workaround. If the necessary data
are unavailable, record that limitation before promising calibrated shadow
decisions; read-only contract/design work can still proceed locally.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: no new detector failure inferred; this records scoped reuse and a subsequent direct candidate identity judgment, without promoting scalar Y or whole-candidate identity to full-path truth.
- Logic-map impact: NONE — transferred annotation evidence changes no detector, trace writer, evaluator or UI execution.
- Failure-registry impact: NONE — no new causal mechanism or field repair is established by a single stored identity label.
