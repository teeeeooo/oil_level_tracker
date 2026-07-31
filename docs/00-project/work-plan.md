# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current gate:** `S6-D User-Confirmed Truth and Category-Balanced Detector-Accuracy Evidence`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Audited feature head:** `ebfbe7f37eccd74ef4fafcf600f798a61d58500e`
**Merged main:** `1debde314a84e14f4d4cb67389878046977296a7`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). S6-C passed fresh repair audit and merged after preserving the frozen annotations and detector comparison while separating provisional JSON from product `.oiltruth`. S6 remains active because user-confirmed accuracy, Windows, long-duration and packaging acceptance are still pending.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Result | `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`; PR #61 passed fresh exact-head audit and guarded squash merge |
| Audited identity | base `774cdda7f35a46f925d2eb1db9d9142de2aece7b`; head `ebfbe7f37eccd74ef4fafcf600f798a61d58500e` |
| Merge identity | `main @ 1debde314a84e14f4d4cb67389878046977296a7` (`docs: add provisional truth comparison for real-video samples`) |
| Contract repair | Four artifacts use `*.provisional-truth.json`; old/new Git blobs, bytes, frozen SHA-256 values and 68 annotations are identical; `.gitignore` equals base |
| Reused evidence | Prior visual review and six detector runs remain valid because video, Recipe, annotation, detector source/settings and generated bundle owners were unchanged |
| Focused validation | Exact identity/scope, product-glob separation, input/Recipe hashes, six bundle reopens, `13 passed`, Markdown links, diff and worktree hygiene exited `0` |
| Accuracy limitation | Silver truth is accepted only as diagnostic evidence; no official detector physical-accuracy acceptance is claimed |
| Next action | Start `S6-D User-Confirmed Truth and Category-Balanced Detector-Accuracy Evidence`; do not tune from provisional evidence alone |

## Accepted meaning and limitations

- S6-A and S6-B qualify execution, reviewability and bundle integrity for repository/local supporting samples; S6-C adds bounded provisional diagnosis.
- No sample has user-confirmed `.oiltruth`; no official MAE, precision, recall, false-positive/negative truth, calibrated level or detector physical-accuracy PASS is claimed.
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

The repair audit reused the prior same-evidence visual review and six detector runs after proving their owners were not invalidated; it did not re-decode complete videos, rerun detector analysis or regenerate bundles. This post-merge Close changed current-state documentation only. It did not perform detector repair/tuning, user-confirmed truth or official accuracy acceptance, Windows GUI/DPI or canonical validation, official long-duration stability, packaging, relocated/clean-PC execution, Unicode/long-path or Windows file-lock/cancellation acceptance, and it did not close S6 or start S7.
