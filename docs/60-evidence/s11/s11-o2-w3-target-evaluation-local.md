# S11 O2 W3 — separated targets and existing-data audit

Date: 2026-10-01. Base: `62280dbb53dbad500ecae4d70ecdf7ac2180f4c8`.
Scope: offline evaluator extension and a read-only Windows handoff. Production
source and the two original audit specifications are unchanged. No private data,
Windows execution, classifier fit, new annotation or detector replay was performed.

[Architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#w3-separated-shadow-targets)
owns the targets, [validation](../../30-validation/s11-interface-observability-witness-validation.md#w3-separated-target-and-audit-controls)
owns controls, [operations](../../40-operations/s11-o2-local-shadow-evaluation.md#w3-targetcontext-audit--기존-자료로-실행)
owns the Windows command and [work-plan](../../00-project/work-plan.md#s11-work-item-ledger)
owns the next transition.

## Implemented boundary

- Extended the existing shadow evaluator with prediction v2/report v3. Candidate
  identity, exact geometry local support and original-candidate scalar eligibility
  are distinct. Missing predictions, explicit not-evaluated, unresolved and
  unobservable outcomes retain their denominators. Empty visible frames remain
  misses. No scalar accuracy is manufactured from identity or qualitative near.
- Retained v1/no-prediction report semantics. Exploratory v2 imports require
  explicit opt-in, empty fit partitions and regression-only inputs; calibrated
  imports retain existing fit/partition guards. This is scripted contract
  verification, not a new classifier or a calibrated operating point.
- Extended the existing experiment runner with `--target-audit`, requiring exact
  original v1 reference inputs/scores/evaluation reproduction. The helper projects
  context and joins recorded decision facts; it does not implement another scorer,
  label store or detector. Input mutation prevents a COMPLETE receipt.
- Reused existing bundle/index/packet verification. Because the public trace record
  model omits top-level sequence annotations, a bounded indexed raw read obtains
  only that already-recorded snapshot. Joins use original offsets/source/Y, never
  positions in score-sorted sequence candidates. Missing witnesses and pre-retention
  losses remain explicitly unknown; CSV publication is outside this audit.
- Added a generated context/funnel summary so Windows can return useful evidence
  without manually transcribing measurements or exporting complete private JSON.

## Verification

**212 passed in 7.90 s**, including **36 new target/audit controls**:

```sh
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_shadow_targets.py \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_s11_shadow_experiment.py \
  tests/unit/test_s11_identity_profile.py \
  tests/unit/test_interface_shadow_evaluation.py \
  tests/unit/test_s11_review_semantics.py \
  tests/unit/test_oil_interface_witness.py \
  tests/unit/test_s11_review_records.py
```

Controls cover target incompatibility/rejection, v1 equality, original scalar Y,
unknown-truth predictions, explicit missing/abstention, outside-repository CLI
with Korean/spaced paths, actual indexed bundle/packet joins with and without
recorded sequence data, unchanged inputs, overwrite prevention and mutation failure.
The real CLI tests execute the Python entry points locally; they do not establish
Windows platform qualification. No production behavior changed, so full canonical,
Qt, video replay and throughput reruns were outside this bounded verification.

| Checked code/artifact | SHA-256 |
|---|---|
| `s11_shadow_experiment.py` | `35e2630c8ca24ff307f1ad51023ebf0042929047335db8b78cbf0d4ebbcc8157` |
| `s11_interface_shadow_evaluation.py` | `0f0cbe3eb3e162030091a70c3058deefab20a22aee88626ab0ed6f8954d8587d` |
| `s11_shadow_target_audit.py` | `e75af82f50bdbe8a46de221d1f438ac0e02196299d5627fd01da52833759fdf7` |
| Target-audit artifact | `a559dc2b470480e6807c79a1113f03266748fe290452a686a7dab020cd97aa63` |

S11 governance, 117 relative document links/anchors and `git diff --check` passed.
Direct changed-scope review confirmed that the original audit specifications and
production source have no changes.

## Remaining boundary

Windows must now check the actual revision **3 / 14 / 4** labels, original v1
experiment and R22-3 bundle. Private context availability and the recorded loss
stages cannot be inferred from the previously transferred score tables. The audit
adds no labels, predictions, freeze, score thresholds, partition changes or video
execution. An absent recorded witness is an evidence gap to report, not a request
to rerun the detector automatically.

W4 remains unselected: use the returned context/funnel evidence to justify one
mechanism and its positive/negative controls. W2 collection stays conditional,
scalar truth/calibration remains absent and O2 acceptance remains open. Existing
Windows experiments are retained as rejected mechanisms. FIELD FAIL is unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: W1 established a synthetic aggregation target mismatch; private identity loss versus missing context or earlier admission loss remains unknown until the exact stored witnesses are inspected. No private causal conclusion is claimed here.
- Logic-map impact: NONE — changes are offline evaluation/inspection only; mapped production extraction, authority, selection and publication are unchanged.
- Failure-registry impact: NONE — exact provenance, missingness and separated targets protect the existing failure boundaries without claiming a new detector repair.
