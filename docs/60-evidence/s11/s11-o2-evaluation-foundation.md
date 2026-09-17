# S11 O2 Label and Evaluation Foundation

Date: 2026-09-17. Base: `4840d79f93502055b7c7ca18373003a8cf9b2391`.
Scope: offline diagnostic tooling and controls. Detector runtime remains R22-3;
no classifier, new R revision or field acceptance is introduced. Current gate is
owned by [work-plan](../../00-project/work-plan.md).

## Ownership and reuse

The new diagnostic entry point is
[`s11_interface_shadow_evaluation.py`](../../../tests/diagnostics/s11_interface_shadow_evaluation.py).
It reuses `ResultBundleReader` and indexed `DebugTraceRepository` for exact-frame
access, the existing truth-identity SHA-256 helper, and benchmark canonical JSON
fingerprinting/percentiles. Product `.oiltruth` and detector benchmark owners were
inspected: they own state/scalar-coordinate comparison, not candidate physical
identity/localization labels and partition-contamination guards. The separate O2
module serves that boundary without duplicating readers or changing product UI.

`prepare` captures all selected record witnesses with exact candidate joins and
creates pending/unreviewed labels. `combine` preserves local packet references and
review ownership. `freeze` validates inventory, identity, visibility, partitions
and hashes. `evaluate` consumes a frozen manifest and optional externally generated
shadow predictions. No command runs a detector, changes settings, or consumes a
label as production evidence.

The [procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) describes
work-PC-only use, JSON fields and the next one-frame preparation step. Existing
reviewed cases are regression; original-recording groups are partition-locked.
Data independence and physical labels remain human attestations. A content hash
cannot prove historical non-use of a holdout.

## Verification

- Focused evaluator, witness, indexed trace and bundle reader checks: **92 passed**.
- New evaluator controls: **34 cases**, including a real writer/store/reader
  preparation path (fixture capture/report renderers), sorted candidate joins,
  label/packet tampering, duplicate keys,
  missing frames/candidates, recording aliases, reviewed holdout contamination,
  unknown support, exact-X interval checks and foreign-cwd/non-ASCII subprocess use.
- Canonical non-Qt suite: **1,578 passed**, 254 deselected.
- Canonical Qt suite: **254 passed**, 1,578 deselected.
- After adding per-sector report detail/availability counts and the corresponding
  assertions, the focused group was rerun: **92 passed**. Runtime source and
  unrelated tests were unchanged; no additional detector replay was warranted.
- No source under `src/` changed. Existing R22-3 O1 replay equality evidence was
  not invalidated; no four-video rerun or private Windows run is claimed here.
- Detector governance, 94 local Markdown link targets and whitespace checks passed.
  Main reviewed the complete change directly; no independent-agent audit is claimed.

The [machine control summary](s11-o2-evaluation-control-summary.json) binds tool
and test hashes to two deliberately scripted scenarios. These are test inputs,
not an image classifier or measured field predictions:

| Control | Expected and observed |
|---|---|
| No predictions | NOT_EVALUATED; three missing predictions; visible-frame recall 0 |
| Known true support plus wrong stripe support | one wrong-structure support; verified precision 0.5 |
| One visible frame with candidates, another visible without any | both stay in denominator; localized-support frame recall 0.5 |
| Offset candidate | physical interface identity remains positive; its 7 px interval distance is separate |
| Scripted matching intervals | coverage 1 with width 2 px; this tests arithmetic only |

The evaluation report separates unknown support, abstention, missing predictions,
negative families, label basis and partitions. It never emits automatic acceptance.
An empty holdout has null metrics; it cannot establish generalization. Internal
classifier evidence-weighting independence remains explicitly NOT_EVALUATED.

## Remaining work

On Windows, first prepare one exact reviewed frame from an existing R22-3 bundle
and confirm the pending label packet/joins locally. If R22-3 witness data does not
exist, report that instead of substituting an R22-2 trace. The original video,
images, labels and detailed packets remain on the work PC.

Next complete limited regression labels and declare independent development,
calibration and untouched holdout recording groups. Then implement and evaluate a
shadow model with declared operating points. Synthetic evaluator success does not
satisfy V2/V3 discrimination or authorize O3 support/association. Accum owner
handoff and BASE observation/direction remain later gates; FIELD FAIL is unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: not newly inferred; this offline evaluator separates candidate absence, physical identity and localization while leaving the known production failure stages unchanged.
- Logic-map impact: NONE — no runtime code, registration, debug output, resolver or publication path changes.
- Failure-registry impact: NONE — arithmetic and provenance controls are not field repair or new physical evidence.
