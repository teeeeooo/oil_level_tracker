# Retained Commitments

This file owns **affirmatively retained work that is not the current executable engineering gate**. It is neither a second roadmap nor a current work plan. Current milestone order and the exact active gate remain owned by [`roadmap.md`](roadmap.md) and [`work-plan.md`](work-plan.md).

## Initial-state retrospective FULL/EMPTY reconstruction

- **Responsibility:** sequence-level backward inference may allow a later defensible trajectory to retrospectively support an earlier `FULL` or `EMPTY` interpretation.
- **Classification:** `RETAINED`
- **Authoritative source / rationale:** the product contract distinguishes Recipe initial state from detector evidence; Recipe initial state remains a prior and must never be promoted into retrospective truth. A later evidence-bearing trajectory may support retrospective interpretation only through a separately authorized sequence-level owner.
- **Activation condition:** a future sequence-level design has sufficient evidence to define retrospective inference without weakening current-frame/no-interface safety or treating Recipe state as truth.
- **Routing owner:** future architecture/validation slice selected by [`roadmap.md`](roadmap.md) and [`work-plan.md`](work-plan.md).
- **Current-gate boundary:** no implementation algorithm or Lane is preselected, and this is **not the current S11 gate**.

## Autosave / abnormal-exit recovery

- **Responsibility:** recover unsaved user work after abnormal process termination without weakening the accepted explicit-save and close-guard semantics.
- **Classification:** `DEFERRED`
- **Authoritative source / rationale:** S9 established explicit Profile dirty/save/close ownership; autosave and crash recovery were deliberately excluded from that release gate.
- **Activation condition:** product priority is explicitly raised after the current detector gate, with a bounded persistence/recovery contract and failure semantics.
- **Routing owner:** future product/workflow slice selected by the project roadmap.
- **Current-gate boundary:** this work remains deferred and is **not the current gate**.

## Observed / estimated / unavailable trajectory responsibility

- **Responsibility:** define, if justified, a product-visible distinction among directly observed Oil, defensibly estimated Oil, and unavailable trajectory regions.
- **Classification:** `EVIDENCE-GATED`
- **Authoritative source / rationale:** the completed offline temporal trajectory probe found insufficient evidence for production interpolation and showed that temporally consistent anchors can reinforce a persistent wrong boundary.
- **Activation condition:** new evidence demonstrates a safe, useful temporal responsibility with explicit provenance and acceptance criteria that cannot be satisfied by the existing current-frame/serialized owner alone.
- **Routing owner:** future architecture plus validation decision; diagnostic provenance lives under [`../50-diagnostics/s11/`](../50-diagnostics/s11/).
- **Current-gate boundary:** **current production temporal implementation remains unapproved**; this is not the current S11 gate.

## Final Windows field-workflow check after stable S11 baseline

- **Responsibility:** perform one final target-Windows field workflow check after the S11 detector baseline is stable enough to make that replay decision-bearing.
- **Classification:** `RETAINED`
- **Authoritative source / rationale:** Windows canonical/manual/package acceptance is already complete for the accepted product baseline, while detector effectiveness is still changing under S11. A final field workflow check remains useful only after the detector baseline stabilizes.
- **Activation condition:** S11 reaches a stable accepted detector baseline and closure is otherwise justified.
- **Routing owner:** the S11 close/validation owner using the operational Windows procedure under [`../40-operations/`](../40-operations/).
- **Current-gate boundary:** this is a later closure check, **not the current engineering gate**.

## Explicitly superseded recurring dependency

Repeated replay of the private Windows field video during every S11 source iteration is **SUPERSEDED as a normal development dependency**. The private video may remain diagnostic corroboration when deliberately available, but iterative S11 source work must not depend on repeated private-field replay. This superseded practice is not a retained commitment.
