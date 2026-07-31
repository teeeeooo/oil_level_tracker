# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current gate:** `S6 remaining validation planning — additional real samples, Windows, long-duration and packaging`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Task-start exact head:** `72133e4004cde7d46eadc7747d23c04c1c237161`
**Task-start exact parent:** `8b37ff81c5d0aa55bf0449f1dbf07d9377b61cd4`
**Durable S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-A qualifies one repository supporting sample only; it does not close S6 or authorize S7.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Result | `S6-A SAMPLE QUALIFICATION: PASS` |
| Pull request | `#58 — docs: qualify S6 repository real-video sample`; merged, non-Draft, unresolved threads `0` |
| Audited identity | base `8b37ff81c5d0aa55bf0449f1dbf07d9377b61cd4`; head `adaf4399b8047193fb506e4219b6da343563722e` |
| Merge identity | `main @ 72133e4004cde7d46eadc7747d23c04c1c237161` (`docs: qualify S6 repository real-video sample`) |
| Completed scope | Short macOS source-tree CLI and result-bundle qualification for `sample/base_sample_1.mp4` with the deterministic repository Recipe |
| Validation evidence | Official pre-overlay, full-range and fresh post-overlay A/B/C runs completed with exit `0`, lifecycle stages `1/6–6/6`, complete reopenable bundles and `REVIEW_REQUIRED`; detailed identities, results and limitations remain in the durable evidence document |
| Current finding | The supporting sample is operationally qualified, but detector physical accuracy is not established |
| Next action | Plan and execute the remaining S6 evidence for additional real samples, Windows, long-duration behavior and packaging |

## Accepted meaning and limitations

- `PASS` means the short repository supporting-sample CLI and bundle qualification completed on the recorded macOS source-tree environment.
- `REVIEW_REQUIRED` is a valid engineering outcome. Ambiguous or conflicting evidence must remain reviewable rather than being forced to a numeric oil level.
- The sample has no user-confirmed `.oiltruth`; no MAE, precision, recall, false-positive/false-negative truth, calibrated physical level or detector accuracy PASS is claimed.
- The known `High / 1/3 / Low` overlay remains visible to the detector. Its observed candidates and the retained ambiguous result are engineering behavior, not verified physical labels.
- macOS source-tree evidence does not substitute for Windows acceptance. This short sample does not establish long-duration acceptance, and a source-tree run does not establish packaging, relocation or clean-PC acceptance.
- S6 remains `ACTIVE`. S7 remains `PLANNED` and must not start until the complete S6 gate passes.

## Pending S6 scope

Still pending and not accepted:

- additional representative real compressor videos, including user-confirmed `.oiltruth` where accuracy metrics are required;
- controlled comparison and review across the expanded real-sample evidence set;
- Windows GUI, manual workflow, DPI and applicable canonical-suite validation;
- stable long-duration CPU and memory behavior;
- PyInstaller one-folder build and packaged runtime qualification;
- relocated package and clean Windows PC execution;
- Unicode and long Windows paths, file locking, cancellation and close behavior;
- final independent S6 acceptance and formal Close.

## Retained contracts

- Repository samples are supporting evidence, never canonical truth.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- S5-A Foam independence remains intact.
- S5-B typed observability, canonical ambiguity and serialized temporal ownership remain intact.
- S5-C canonical/Qt lifecycle and headless import boundaries remain intact.

## Intentional non-runs

This documentation-only Close resume did not rerun detector or CLI qualification, official A/B/C executions, Windows validation, long-duration validation, packaging, relocated or clean-PC execution, source tests, Recipe generation, evidence regeneration, validation jobs or branch hygiene. It did not modify source, tests, Recipe, MP4, generated output, quality evidence, dependencies, runtime files, branches or PR metadata.
