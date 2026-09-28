# S11 O2 Windows label-to-witness comparison — transferred preparation report

Recorded: 2026-09-28. Source: user-transferred Windows completion summary.
Private inputs, generated comparison tables and the new Windows script were not
available in this checkout and were not directly inspected. This records reported
artifact creation and inventory checks, not verified measurement extraction or
discrimination. The [work plan](../../00-project/work-plan.md) owns current state;
the [O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) and
[validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own workflow and acceptance. [Canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
is unchanged.

## Reported artifacts and execution scope

- The review-003 selection file was moved to the separate selections directory
  with matching SHA prefix `3056aaad...`. References after the move were not
  described; no broken reference or successful relocation test is inferred.
- Windows created `tests/diagnostics/s11_review_comparison.py` (345 lines,
  12 functions) and reports reusing `fingerprint_json` from the existing evaluator.
  This file is absent in the present checkout. Other loader/validator reuse,
  actual code version and comparison entry-path checks have not been supplied.
- New local outputs: manifest (3.4 KB), Table A identity summary (30 KB, 73 rows),
  Table B native-path detail (103 KB, 55 rows), Table C native-path aggregate
  (6.9 KB, three rows). Full artifacts remain on Windows. The row grain and
  individual metric distributions are not established by these names alone.

## Inventory reconciliation

| Review | Candidate identities | Native-path point judgments |
|---|---|---|
| 001 | 23 non_interface; 20 center-only and 3 native-path proposals | 9 unreviewed |
| 002 | 6 interface, 2 non_interface, 15 unreviewed | 10 near, 7 off |
| 003 | 2 interface, 25 unreviewed | 5 near, 24 unreviewed |

These match the previously transferred [review-001](s11-o2-windows-review-001.md),
[review-002](s11-o2-windows-review-002.md) and
[review-003](s11-o2-windows-review-003.md) counts: 73 proposals, and 55 native
points = 15 near + 7 off + 33 unreviewed. Native points, scales and proposals are
not independent frames. Review-002 and review-003 share recording-A. No native
point labels are inferred from review-001's negative candidate identities.

## Hash comparison interpretation

| Review | Reported labels_content_sha256 prefix | Frozen content prefix | Reported labels_unchanged |
|---|---|---|---|
| 001 | 2351a65e... | no frozen file | null |
| 002 | 7d1d4749... | ce9c4373... (r10) | false |
| 003 | 85951f30... | 85951f30... (r3) | true |

This flag compares current content to a historical frozen snapshot. It does
**not** establish whether this comparison execution changed the source labels.
Review-002 differs as expected after revisions 11–14, which added two interface
identities, two non-interface identities and further path judgments after r10.
It must not be reset to match r10. Review-001's null means no frozen comparison,
not failed preservation. Reported labels_content digests are not the previously
reported whole-document status labels_sha256; verify each payload definition
before comparing across these fields.

Before/after hashes for this comparison run were not supplied. If none were
captured, mark that original-run preservation check unverified rather than
reconstructing a pre-run hash from the current file. A later controlled read-only
run can establish its own preservation evidence, not retroactive proof.

## Needed before using the comparison to design a classifier

1. Inspect the script's label/packet loading, hash validation, candidate and
   exact-geometry joins, metric extraction and grouping. Hash serialization reuse
   alone does not establish correct provenance or arithmetic. Report unmatched,
   duplicated and excluded rows and missing-value handling.
2. Obtain actual measurement distributions, separated by review, geometry basis
   and scale: candidate interface/non_interface and explicitly reviewed native
   near/off. Include valid/missing counts and descriptive ranges, plus overlapping
   examples. Current transferred findings are label inventories, not evidence that
   any feature separates the classes. Do not tune a threshold on this regression set.
3. Resolve review-003's exact case-level contour key/value/type and metric paths;
   the earlier “undefined” report is still unresolved. Do not edit human labels.

No additional image judgments are needed for this audit. No model, operating
point, new independent support or field PASS is established. Classifier status
remains NOT_EVALUATED; private originals remain the annotation authority.

## Pasted script and measurement-report audit — 2026-09-28

The user subsequently supplied script text and a measurement summary. This is a
static audit of that pasted text against the repository's v2 schema and evaluator;
no Windows source file, private dataset or generating-script byte hash was received.
The original artifact-creation report above is retained as historical evidence.
**The comparison is not accepted as input to classifier/threshold decisions yet.**
Human labels and previously reported review snapshots are not invalidated by
faults in this downstream comparison.

### Script findings

| Location in pasted script | Finding and consequence |
|---|---|
| fingerprint_json | Locally redefined, not imported from the existing evaluator. Matching serialization is duplication, not the reported function reuse. |
| load_review | Selects cases[0] and frames[0], opens a hardcoded packet path and builds dictionaries without duplicate checks. Does not call load_packets/validate_labels or verify case/packet/candidate hashes against references. Calculating digests later does not validate these joins. |
| build_table_b/build_table_c | Keys path_reviews by X range alone, dropping geometry_basis and source_y. Candidate-center and native reviews can collide; differing Y can be mislabeled. Existing geometry_key includes all three components. No silent dict overwrite is acceptable as a join check. |
| build_table_b reviewer | **Withdrawn for the photographed code.** The OCR/pasted text omitted a nesting level. Image 55082, displayed line 227, reads pr["review"]["reviewer"], matching v2. |
| build_table_c/group_summary | **Withdrawn for the photographed code.** The pasted indentation was not faithful. Images 55084–55085 show band aggregation and bw_summary assignment inside the bandwidth loop, with return inside group_summary and entries.append outside it. |
| uncertain handling | scale_stats omits uncertain; encountering it would index a missing key. The counter also conflates uncertain with unreviewed. Current reports have no uncertain labels, so this is a latent defect, not proof of altered current counts. |
| extract_* / outputs | .get collapses missing keys and null; requested static_overlap, glare_fraction and lineage are omitted. Table A contains labels/metadata, not identity feature summaries. Table C code uses means, while the report claims medians/ranges from an unidentified calculation. |
| build_manifest/main | glob iteration selects whichever frozen/readiness file is visited last, without explicit pairing or content-hash validation. labels_sha256 here is a file-byte hash, not the status logical hash. No source pre/post comparison is made. Output files are opened with w, so a rerun overwrites prior artifacts. |

The two withdrawn findings describe defects in the transferred text, not the code
shown in the subsequent photos. The claim that the photographed generator cannot
run because of those defects is withdrawn. Photos do not independently bind source
bytes to an earlier execution or explain the report's median calculation.

### Ten-photo verification and correction

The user explained that the pasted text was extracted from images and provided
ten photos (55077–55086). Review of the displayed code confirms the two corrections
above. No Windows source file export is required or requested; file execution and
private-data checks remain on Windows. The full code was not reconstructed into a
repository implementation from photographs.

The photographed code still shows locally redefined fingerprint_json, first-case/
first-frame selection without existing validators, X-only path joins, no uncertain
scale group, .get missing/null conflation, means rather than medians, glob-based
last-file selection and output overwriting. These are the remaining review issues.
They do not prove that the current labels were misjoined: for example, no reviewed
candidate-center points or uncertain judgments were reported in this dataset.
Controls are needed to establish correctness rather than assume either corruption
or successful validation from matching aggregate counts.

### Report arithmetic, scope and interpretation findings

- Review-002's four native-path interface candidates have **14 sectors = 10 near
  + 4 off**, not 17 = 10 near + 7 off. Adding the three non-interface candidate-11
  sectors gives the overall 17 = 10 near + 7 off. Table n=14 is consistent with
  the former inventory, but does not validate its measurement values.
- The listed null-delta causes account for **3 + 3 + 1 = 7** scale rows, not the
  asserted nine. Reconcile actual keys before claiming a 9/165 missing rate.
- Section 7 inspected witness/contour metadata instead of human label
  `labels["cases"][...]["contour"]`. Thus the previous contour serialization
  question remains unresolved. Candidate witness contour metadata is not human
  numeric truth. Existing witness models also represent center-only candidates'
  contour metadata; native-only existence must not be assumed.
- Near_below normal_alignment medians in the report are near/off **0.762280 /
  0.737322**, **0.737457 / 0.756310**, **0.745364 / 0.758691** across widths 8/16/24.
  The latter two are lower for near, contradicting the blanket higher-near claim.
- Near_below gradient_magnitude near/off is **0.004045 / 0.004618**,
  **0.003421 / 0.004209**, **0.003202 / 0.004131**: lower for near at every shown
  width, contrary to its description as slightly higher. The claim that
  near_below alignment is always highest/far_above always lowest also has table
  counterexamples, including review-001 width 8 near_above alignment 0.822615
  exceeding near_below 0.814661.
- A candidate having both near and off points does not prove a sector-level
  feature cannot discriminate them. Overlapping displayed marginal ranges also
  do not establish a multivariate classifier's impossibility. Conversely, one
  negative candidate's disjoint ranges cannot select a general operating point.
- The displayed band tables largely give medians and n, not ranges; claims of
  heavy overlap or a strongest discriminator are not demonstrated by those
  tables alone. Table B covers native paths only; center-only labeled candidates
  are omitted from feature comparisons despite being present in Table A.
- Review-003 cross-review rows have up to 24 values, while the explicitly reviewed
  native positive has only five points. Clarify whether these rows describe the
  unreviewed group or another filter; they cannot stand in for reviewed interface
  measurements. Differences in material_mean do not establish physical material
  composition. Feature-missingness can be expected yet still affect comparisons.

### Required next evidence, without more human labeling

Keep the script and private inputs on Windows. Record current code hashes and
identify any separate median/report computation; if the old execution is not
recoverable, state that limit without manufacturing evidence. Preserve old outputs
and reconcile the remaining scope/schema findings, excluding the two withdrawn
OCR findings. A corrected comparison should reuse existing load_packets,
validate_labels, geometry_key and fingerprint_json rather than reimplementing
provenance, handle every judgment/missing state, and group actual metric rows by
review/identity-or-path-judgment/geometry/scale with explicit counts. Store outputs
under a new run directory and hash source files before and after that new run.
Keep original-run immutability unverified if no original pre-run hashes exist.
Use constructed controls for geometry collisions, duplicate/missing joins,
multiple bandwidths, uncertain labels and missing values before rerunning on
private inputs. Generate the replacement numeric report from the same validated
metric rows as its tables, so denominators, null lists and direction descriptions
can be reconciled. Return only permitted verification/measurement summaries; no
additional image labeling or private source export is required. The classifier
remains unbuilt and field disposition unchanged.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: comparison-report provenance semantics — historical frozen equality was described as execution-time label preservation; actual script joins and discrimination remain unverified, with no new production failure inferred.
- Logic-map impact: NONE — transferred comparison evidence does not change detector, serializer or classifier execution.
- Failure-registry impact: NONE — this records an existing provenance boundary and named unknowns, not a new detector cause or accepted repair.
