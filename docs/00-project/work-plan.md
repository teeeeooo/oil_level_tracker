# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `INTAKE AND QUALIFICATION COMPLETE ON FEATURE HEAD — AWAITING AUDIT`
**Current gate:** `S6-B Additional Real-Video Sample Qualification Fresh Exact-Head Auditor`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Task-start exact head:** `ab61b68d5f9b0df5d40148cc661a370cd2be5214`
**Task-start exact parent:** `72133e4004cde7d46eadc7747d23c04c1c237161`
**Worker branch:** `feature/s6-additional-real-sample-qualification`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). The resulting feature-head SHA is owned by the Worker final report and Draft PR snapshot because a commit cannot record its own identity.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Result | S6-B intake and macOS source-tree qualification completed on the Worker feature head; independent audit remains pending |
| Inputs | Local-only ignored `sample2.mp4`, `sample3.mp4` and `sample4.mp4`; exact size/hash and sequential usable boundaries verified |
| Tracked scope | Three deterministic Recipes, exact Recipe allowlist, sample documentation, S6-B quality evidence, documentation index and this Work Plan |
| Qualification | Four fresh production CLI runs completed with exit `0`, lifecycle stages `1/6–6/6` and complete readable bundles |
| Engineering outcomes | sample2 and both sample3 windows: `REVIEW_REQUIRED`; sample4: `FAIL`; no result was normalized or tuned away |
| Findings | No numeric oil was published; sample2/sample4 published Foam behavior; sample3 retained ambiguity/no-interface behavior with limited full/fresh sensitivity |
| Current blocker | None for Worker handoff; final exact-head audit is required before merge |
| Next action | Fresh Auditor independently verifies sample identity, decode boundaries, Recipes, CLI/bundle evidence, bounded diff and limitations |

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

- fresh independent S6-B exact-head audit, guarded merge and post-merge documentation Close;
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

This Worker did not run or claim detector tuning, user-truth metrics, Windows GUI/DPI or canonical validation, official long-duration stability, packaging, relocated/clean-PC execution, Unicode/long-path or Windows file-lock/cancellation acceptance. It did not modify production source, tests, dependencies, detector settings or MP4 bytes, and did not merge, approve, transition the PR to Ready, synchronize the primary checkout, close S6 or start S7.
