# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** first audit failed on product suffix collision; bounded extension repair completed on feature head
**Current gate:** `S6-C Provisional Truth Extension Repair Fresh Exact-Head Auditor`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Task-start exact head:** `b4c3e693add103334aecb3f55fb023f9555fa70f`
**Task-start exact parent:** `774cdda7f35a46f925d2eb1db9d9142de2aece7b`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). The first S6-C audit rejected the provisional artifact suffix collision; the bounded repair preserves the annotations and detector comparison while separating those artifacts from product `.oiltruth`. S6 remains active because repair audit, official detector accuracy, Windows, long-duration and packaging acceptance are still pending.

## Latest recorded closeout

| Item | Current state |
|---|---|
| Result | First S6-C exact-head audit at `b4c3e693add103334aecb3f55fb023f9555fa70f` returned `FAIL`; bounded extension repair completed on the new feature head |
| Audit finding | The provisional artifacts collided with the product-owned `.oiltruth` suffix while carrying an incompatible provisional string schema |
| Repair | Four artifacts renamed byte-for-byte to `*.provisional-truth.json`; provisional `.oiltruth` ignore/allowlist policy removed; references and current state corrected |
| Preserved evidence | 68 frozen annotations, four SHA-256 values, visual review, six production CLI runs and diagnostic comparison remain unchanged and were not regenerated |
| Focused validation | Provisional JSON identity/count checks, product-glob separation, product truth-owner test, Markdown links and diff hygiene |
| Accuracy limitation | Silver truth remains non-user-confirmed provisional evidence; no official detector physical-accuracy acceptance is claimed |
| Next action | Fresh independent S6-C extension-repair exact-head Auditor; no PASS or acceptance is declared on this feature head |

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

This repair Worker did not re-decode or visually review video, modify annotations, rerun detector analysis, regenerate bundles or repeat the broader comparison suite. It also did not perform detector repair/tuning, user-confirmed truth or official accuracy acceptance, Windows GUI/DPI or canonical validation, official long-duration stability, packaging, relocated/clean-PC execution, Unicode/long-path or Windows file-lock/cancellation acceptance. It did not modify production source, tests, dependencies, Recipes, detector settings, MP4 bytes or generated output and did not close S6 or start S7.
