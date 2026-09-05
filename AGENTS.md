# Repository task routing

Use this file as the repository execution entry point. Keep repository policy separate from any external agent, delegation, or subagent policy.

## Default execution behavior

- Complete the user's requested repository task as far as the granted authority allows.
- Infer routine, reversible details from repository context instead of asking for confirmation.
- Ask only when a material ambiguity would change product behavior, authority, or an irreversible/consequential action.
- Do not repeat an approval the user already gave.
- Preserve unrelated working-tree changes. Never overwrite, stage, revert, or fold them into this task.
- Prefer the smallest relevant reading set and the smallest verification set that can establish correctness.

## Repository authority

Before creating, moving, renaming, or editing anything under [`docs/`](docs/), read [`docs/README.md`](docs/README.md). It owns documentation classification and authority routing.

For current project status or the next authorized engineering action, use [`docs/00-project/work-plan.md`](docs/00-project/work-plan.md). For milestone order and state, use [`docs/00-project/roadmap.md`](docs/00-project/roadmap.md).

For repository execution state, verification, exact-head review/freeze, merge/publication, and closeout semantics, follow [`docs/00-project/execution-policy.md`](docs/00-project/execution-policy.md).

## S11 detector changes

If a task changes S11 detector vision/control-flow/publication code, detector architecture/design, or S11 detector diagnostics/evidence, follow [`docs/30-validation/s11-detector-change-governance.md`](docs/30-validation/s11-detector-change-governance.md) before design or implementation. That contract owns the task-specific reading order, history review, evidence routing, and governance checker.

Do not duplicate the detector reading sequence here. The governance contract routes the current logic map, failure registry, active architecture, validation, and reviewed truth.

## Consequential actions

Repository inspection, diagnostics, requested edits, and proportional local verification are not separate approval gates when already within the user's request. Stop only before an action that remains unauthorized and is materially consequential, such as merging to a protected branch, publishing/releasing externally, destructive deletion, or an irreversible migration.

Repository documents define what is allowed and required in this repository. They do not define which agent/session performs the work, delegation strategy, specialist selection, or reasoning settings.