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

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: comparison-report provenance semantics — historical frozen equality was described as execution-time label preservation; actual script joins and discrimination remain unverified, with no new production failure inferred.
- Logic-map impact: NONE — transferred comparison evidence does not change detector, serializer or classifier execution.
- Failure-registry impact: NONE — this records an existing provenance boundary and named unknowns, not a new detector cause or accepted repair.
