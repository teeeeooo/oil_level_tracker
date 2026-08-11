# Retained Commitments

This file owns **affirmatively retained work that is not the current executable engineering gate**. It is neither a second roadmap nor a current work plan. Current milestone order and the exact active gate remain owned by [`roadmap.md`](roadmap.md) and [`work-plan.md`](work-plan.md).

## Autosave / abnormal-exit recovery

- **Responsibility:** recover unsaved user work after abnormal process termination without weakening the accepted explicit-save and close-guard semantics.
- **Classification:** `DEFERRED`
- **Authoritative source / rationale:** S9 established explicit Profile dirty/save/close ownership; autosave and crash recovery were deliberately excluded from that release gate.
- **Activation condition:** product priority is explicitly raised after the current detector gate, with a bounded persistence/recovery contract and failure semantics.
- **Routing owner:** future product/workflow slice selected by the project roadmap.
- **Current-gate boundary:** this work remains deferred and is **not the current gate**.

## Observed / estimated / unavailable trajectory responsibility

- **Responsibility:** define, if justified, a product-visible distinction among directly observed Oil, defensibly estimated Oil, and unavailable trajectory regions.
- **Classification:** `ACTIVATED / ROUTED TO S11-R5`
- **Authoritative source / rationale:** the interpolation-over-accepted-anchors probe remains rejected, but new secure-Windows evidence demonstrates that the existing current-frame/serialized owner cannot compare alternate candidates across time and therefore cannot express the visible physical history.
- **Activation condition:** satisfied by the R5 root-cause evidence; implementation is owned by the current work plan.
- **Routing owner:** [`../20-architecture/s11-r5-sequence-first-trajectory-architecture.md`](../20-architecture/s11-r5-sequence-first-trajectory-architecture.md) and its [`validation contract`](../30-validation/s11-r5-sequence-first-trajectory-validation.md).
- **Current-gate boundary:** R5 may select only a coordinate observed as a same-frame candidate and must label sequence provenance; numeric interpolation/prediction remains unauthorized. Because this responsibility is now current, this entry is retained only as the activation handoff and should be removed when R5 reaches a durable accepted owner.

## Explicitly superseded recurring dependency

Repeated replay of the private Windows field video during every S11 source iteration is **SUPERSEDED as a normal development dependency**. The private video may remain diagnostic corroboration when deliberately available, but iterative S11 source work must not depend on repeated private-field replay. This superseded practice is not a retained commitment.
