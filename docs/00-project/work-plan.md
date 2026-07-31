# Rotary Oil Level Tracker — Active Work Plan

**Current milestone:** `S6 — Real-video and Windows validation gate`
**Milestone status:** `ACTIVE`
**Current S6-A result:** `S6-A SAMPLE QUALIFICATION: PASS`
**Current S6-B result:** `S6-B INTAKE AND QUALIFICATION: PASS`
**Current S6-C result:** `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`
**Current gate:** `S6-E Bounded Runtime Soak and Resource-Leak Screening`
**Pending accuracy gate:** `S6-D User-Confirmed Truth and Category-Balanced Detector-Accuracy Evidence`
**Successor milestone:** `S7 / Phase 2C-4 — Annotated MP4 export` remains `PLANNED` and has not started
**Task-start exact head:** `dc6d24448c30e30e1f3e016b397d8522ec17bd05`
**Task-start exact parent:** `1debde314a84e14f4d4cb67389878046977296a7`
**S6-A evidence:** [`../30-quality/s6-base-sample-1-evidence.md`](../30-quality/s6-base-sample-1-evidence.md)
**S6-B evidence:** [`../30-quality/s6-additional-real-samples-evidence.md`](../30-quality/s6-additional-real-samples-evidence.md)
**S6-C evidence:** [`../30-quality/s6-provisional-truth-comparison.md`](../30-quality/s6-provisional-truth-comparison.md)
**Domain-owner addendum:** [`../30-quality/s6-domain-owner-review-addendum.md`](../30-quality/s6-domain-owner-review-addendum.md)

This document owns the current active execution state. Milestone order and formal status remain governed by [`roadmap.md`](./roadmap.md). The post-freeze domain-owner review now supplies higher-authority physical interpretation and field priorities without rewriting the blind provisional evidence or replacing product `.oiltruth`.

## Latest recorded closeout

| Item | Current state |
|---|---|
| S6-C result | `S6-C PROVISIONAL DIAGNOSTIC EVIDENCE: ACCEPTED`; frozen blind evidence and product `.oiltruth` remain separate |
| S6-C merged identity | audited head `ebfbe7f37eccd74ef4fafcf600f798a61d58500e`; merge `1debde314a84e14f4d4cb67389878046977296a7` |
| Documentation close | Post-freeze domain-owner interpretation for sample3/sample4 and field detector priorities are preserved in the linked addendum |
| Frozen artifacts | Four `*.provisional-truth.json` files retain their original bytes, filenames, annotations and frozen SHA-256 values |
| Accuracy status | S6-D product `.oiltruth`, category-balanced evidence and official metrics remain pending; no detector accuracy PASS is recorded |
| Current executable action | Run bounded diagnostic soak and resource-leak screening under S6-E |
| Performance limitation | Current Mac workload prevents precise CPU-throughput acceptance; controlled-idle representative-duration and official long-duration gates remain separate future work |

## Domain-owner priorities retained

1. Separate Oil–Foam and Foam–Gas boundaries when both phases coexist.
2. Suppress fluorescent reflection, glare and bright bands.
3. Suppress Glass rim, fixed structure and paired horizontal lines.
4. Suppress scratches, stains, fogging and other fixed surface artifacts.
5. Track oscillating real Oil level through fill and drain with bounded temporal reasoning.
6. Keep severe blur, focus loss and camera motion as a lower-priority robustness category.

sample4 is the primary Oil-under-Foam separation diagnostic. sample3 remains a compound-state reference and lower-priority poor-image robustness challenge; it must not drive aggressive weakening of artifact rejection.

## Accepted meaning and limitations

- Domain-owner review has greater physical interpretation authority than the blind provisional annotations, but is not yet bundle-bound product `.oiltruth`.
- Oil level and Foam upper front may coexist as separate physical boundaries. Foam presence must not imply automatic Oil `null`.
- sample4 Foam publication is not automatically a false positive; the main suspicion is loss of the real Oil-under-Foam channel.
- sample4's detector `FAIL` does not establish physical recovery failure.
- No official MAE, precision, recall, false-positive/negative rate, calibrated level or detector physical-accuracy PASS is claimed.
- S6-E is bounded diagnostic screening, not official long-duration CPU or performance acceptance.
- S6 remains `ACTIVE`; S7 remains `PLANNED` and must not start until the complete S6 gate passes.

## Pending S6 scope

Still pending and not accepted:

- S6-D user-confirmed product `.oiltruth` and category-balanced official accuracy evidence;
- S6-E bounded runtime soak and resource-leak screening;
- controlled-idle representative-duration performance and official long-duration CPU/memory stability;
- Windows GUI, manual workflow, DPI and applicable canonical-suite validation;
- PyInstaller one-folder build, relocation and clean Windows PC execution;
- Unicode/long paths, file locking, cancellation and close behavior;
- final independent S6 acceptance and formal Close.

## Retained contracts

- Repository/local samples and blind provisional annotations remain supporting evidence, not canonical truth.
- No filename, hash, Recipe ID, frame number or fixture identity may become detector logic.
- Field-priority input does not authorize source repair or threshold tuning without category-balanced evidence.
- S5-A Foam independence, S5-B typed observability/temporal ownership and S5-C Qt/headless boundaries remain intact.

## Intentional non-runs

This documentation-only preservation did not rerun videos, detector analysis, provisional comparison, bundles, runtime soak, source tests, Windows, packaging or accuracy metrics. It did not create product `.oiltruth`, change Recipes, MP4s, generated output, source, tests, dependencies or detector settings, close S6, or start S7.