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
- **Classification:** `EVIDENCE-GATED`
- **Authoritative source / rationale:** the completed offline temporal trajectory probe found insufficient evidence for production interpolation and showed that temporally consistent anchors can reinforce a persistent wrong boundary.
- **Activation condition:** new evidence demonstrates a safe, useful temporal responsibility with explicit provenance and acceptance criteria that cannot be satisfied by the existing current-frame/serialized owner alone.
- **Routing owner:** future architecture plus validation decision; diagnostic provenance lives under [`../50-diagnostics/s11/`](../50-diagnostics/s11/).
- **Current-gate boundary:** no separate production trajectory-estimation responsibility is authorized; this remains evidence-gated and is not the current S11 gate.

## Final Windows field-workflow check after retrospective reconstruction

- **Responsibility:** perform one final target-Windows field workflow check after the active Initial-State Retrospective FULL/EMPTY Reconstruction responsibility is implemented and accepted.
- **Classification:** `RETAINED`
- **Authoritative source / rationale:** Windows canonical/manual/package acceptance is already complete for the prior product baseline, and the S11 detector baseline is now stable for sequencing. Final field replay remains useful only after the new retrospective official semantics are stable.
- **Activation condition:** the active retrospective reconstruction implementation completes its required acceptance so the resulting S11 output semantics are stable for final field verification.
- **Routing owner:** the S11 close/validation owner using the operational Windows procedure under [`../40-operations/`](../40-operations/).
- **Current-gate boundary:** this remains a later closure check after the retrospective reconstruction gate, **not the current engineering gate**.

## Explicitly superseded recurring dependency

Repeated replay of the private Windows field video during every S11 source iteration is **SUPERSEDED as a normal development dependency**. The private video may remain diagnostic corroboration when deliberately available, but iterative S11 source work must not depend on repeated private-field replay. This superseded practice is not a retained commitment.
