# S11 O2 reference uncertainty and model abstention audit

Date: 2026-10-01. Base HEAD: `89acfb0` plus the pending context-reconciliation
documents. Scope: source review, nine new synthetic controls and interpretation
contract clarification. Production, scorers, evaluator implementation, schemas,
private labels and past score outputs are unchanged. FIELD FAIL is retained.

## Question and bounded recall

The [transferred context reconciliation](s11-o2-identity-context-windows-review-001.md)
records the user's uncertainty about BASE idx0/idx20 even after about ten seconds
of surrounding formation/motion evidence. Neither stronger glare nor motion was
a conclusive physical discriminator. This is not a request to force that pair's
ordering or silently replace its binary labels. Prior W1/W3 controls already
separate identity, local path support, scalar eligibility and model abstention.

## Existing owners and findings

| Owner | Observed behavior | Interpretation |
|---|---|---|
| [Label validation / identity](../../../tests/diagnostics/s11_interface_shadow_evaluation.py) | `uncertain` and `unreviewed` exist separately for identity and path truth | No new label schema or parallel uncertainty store is required |
| Same owner's `summarize` | Human identity by model-decision confusion; unverified support separate from TP/FP; recall and abstention denominators retained | Unknown truth cannot certify a supported prediction. Verified precision is conditional on definite labels, not physical certification |
| Same owner's `summarize_targets` | Missing predictions remain explicit; uncertain/unreviewed local truth is not verified decisive success; full point/frame counts retained | Abstention, unavailable evidence, non-evaluation and missing predictions are not interchangeable |
| Same owner's `evaluate` | Prediction document must target exact frozen-label content hash | A changed reference needs separately identified evaluation; free-text rationale is not parsed into labels |
| [Rank experiment `evaluate_case`](../../../tests/diagnostics/s11_shadow_experiment.py) | Only interface/non_interface identities form identity pairs; candidate inventory/ranking still includes other identities | Relabeling a negative uncertain can remove a reversed pair without changing any score; not a method gain |
| [Review records](../../../tests/diagnostics/s11_review_records.py) | Existing attributed revision, history and migration flow | Use only for a separately authorized formal revision; this audit does not edit any private reference |

The source search covered existing label validation/recording, rank evaluation,
separated-target evaluation, callers and existing semantics/target tests. The
owners already implement the required distinction. A runtime fix, supplemental
CLI, score weight or case-specific abstention rule would add unsupported behavior.

## New controls and verification

Nine tests were added to existing test owners:

1. Six parameterized full-`evaluate` controls cross constructed uncertain human
   identity/local truth with the five identity decisions and a missing prediction.
   Verify unchanged candidate/frame/point denominators, no verified identity or
   local success, unverified support, explicit abstention/missing counts, null
   undefined conditional metrics, and immutable inputs. The remaining known
   positive abstains and still has zero recall.
2. One full-evaluator provenance control changes only a constructed rationale
   note: stale prediction-label provenance is rejected; explicitly matching new
   provenance yields identical metrics; original evaluation reproduces exactly.
   This is an in-memory synthetic alternate document, not a private freeze edit.
3. Two ranking controls replace a constructed negative identity with uncertain
   or unreviewed in an alternate fixture. A reversed pair disappears while raw
   measurements, scores, two-candidate ranking coverage and path judgments remain.
   The original pair/result reproduces unchanged. This demonstrates why changed
   label support cannot be counted as a scoring improvement.

```sh
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_shadow_targets.py \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_s11_review_semantics.py
```

**94 passed in 5.03 s**, including the nine new controls and existing label-history,
CLI, target-separation, all-abstain, missing/unobservable and raster controls.
Scripted model decisions are evaluation probes, not an implemented classifier.
No private image or Windows artifact was loaded here. Documentation/governance
checks cover the companion edits; no field efficacy follows from these tests.

## Decision

The uncertainty interpretation review is complete locally. The
[architecture contract](../../20-architecture/s11-interface-observability-witness-architecture.md#human-reference-uncertainty-and-model-abstention)
and [validation controls](../../30-validation/s11-interface-observability-witness-validation.md#w3-separated-target-and-audit-controls)
make the existing behavior explicit. Operations link the human qualification to
future interpretation without rewriting old machine reports. No Windows rerun,
additional human clarification or repeat viewing of the same clip is needed for
this task. Current labels stay pinned; historical "correct/reversed" means
agreement/disagreement with those labels, with the reported uncertainty attached.

Candidate-identity improvement remains open. A later W4 mechanism needs a distinct
observable and separate positive, negative and unresolved controls; ambiguity
about idx20 does not establish that all structural negatives are ambiguous or
repair the other failures. No candidate identity, scalar accuracy, calibrated O2
acceptance or production abstention behavior is promoted here. Collection remains
conditional on an evidence-bearing question, not an automatic broader video scan.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: an interpretive error would treat uncertain human reference as certified physical truth or a changed pair denominator as a scoring gain; no evaluator/runtime defect or private physical cause was established.
- Logic-map impact: NONE — synthetic tests and interpretation contracts only; runtime extraction, identity, selection, publication and offline evaluator implementation are unchanged.
- Failure-registry impact: NONE — existing provenance and no-private-shortcut guards are exercised; no new field repair is claimed.
