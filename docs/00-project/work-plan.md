# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current gate:** `S6 truth-data planning — user-confirmed .oiltruth and category-balanced detector-accuracy evidence`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Task-start exact head:** `2e4c55d138154cf45ce1c46b57b2d422e309d0c7`
**Task-start exact parent:** `ab61b68d5f9b0df5d40148cc661a370cd2be5214`
**Merged PR:** `#60 — docs: qualify S6 additional real-video samples`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-B is merged and operationally qualified; S6 remains active because detector truth, Windows, long-duration and packaging acceptance are still pending.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Result | `S6-B INTAKE AND QUALIFICATION: PASS`; PR #60 passed fresh exact-head audit and guarded squash merge |
| Audited identity | base `ab61b68d5f9b0df5d40148cc661a370cd2be5214`; head `b68a590a304c41408c5cb236c3274b35c40a1335` |
| Merge identity | `main @ 2e4c55d138154cf45ce1c46b57b2d422e309d0c7` (`docs: qualify S6 additional real-video samples`) |
| Inputs | Local-only ignored `sample2.mp4`, `sample3.mp4` and `sample4.mp4`; exact size/hash, sequential boundaries and fixed-window geometry independently verified |
| Qualification | Four fresh production CLI runs exited `0`, emitted lifecycle stages `1/6–6/6`, reopened through `ResultBundleReader` and matched the preserved Worker outcomes |
| Focused validation | Recipe storage/round-trip, CLI lifecycle progress, result-bundle reader and analysis/reporting tests: `24 passed` |
| Engineering outcomes | sample2 and both sample3 windows: `REVIEW_REQUIRED`; sample4: `FAIL`; numeric oil remained `null` and no result was tuned or normalized away |
| Accuracy limitation | No user-confirmed `.oiltruth`; S6-B is execution, reviewability and bundle qualification, not detector physical-accuracy acceptance |
| Next action | Plan user-confirmed `.oiltruth` and category-balanced detector-accuracy evidence while retaining the remaining Windows, long-duration and packaging gates |

## Accepted meaning and limitations

- S6-A and S6-B qualify execution, reviewability and bundle integrity for repository/local supporting samples.
- No sample has user-confirmed `.oiltruth`; no MAE, precision, recall, false-positive/negative truth, calibrated level or detector physical-accuracy PASS is claimed.
- `REVIEW_REQUIRED` is valid engineering behavior. sample4's `FAIL` is preserved as the current recovery judgment, not promoted to physical truth.
- Numeric `null` remains `null`. Production-default detector settings and evidence-visible artifacts remain unchanged.
- macOS source-tree evidence does not substitute for Windows, packaging, relocation or clean-PC acceptance.
- These short clips and runs do not establish official long-duration CPU or memory stability.
- S6 remains `ACTIVE`; S7 remains `PLANNED` and must not start until the complete S6 gate passes.

## Pending S6 scope

Still pending and not accepted:

- representative user-confirmed `.oiltruth` and category-balanced detector-accuracy evidence;
- additional real samples where the controlled evidence set remains insufficient;
- Windows GUI, manual workflow, DPI and applicable canonical-suite validation;
- stable long-duration CPU and memory behavior;
- PyInstaller one-folder build and packaged runtime qualification;
- relocated package and clean Windows PC execution;
- Unicode and long Windows paths, file locking, cancellation and close behavior;
- final independent S6 acceptance and formal Close.

## Retained contracts

- Repository/local samples are supporting evidence, never canonical truth.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- One unsuitable or difficult sample must not invalidate independent evidence from another sample.
- S5-A Foam independence, S5-B typed observability/temporal ownership and S5-C Qt/headless boundaries remain intact.

## Intentional non-runs

This post-merge documentation Close did not rerun detector qualification or focused tests and did not perform detector tuning, user-truth metrics, Windows GUI/DPI or canonical validation, official long-duration stability, packaging, relocated/clean-PC execution, Unicode/long-path or Windows file-lock/cancellation acceptance. It changed only this current-state Work Plan, did not modify production source, tests, dependencies, Recipes, detector settings, MP4 bytes or generated evidence, and did not close S6 or start S7.
