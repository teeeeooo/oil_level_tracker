# Documentation Closeout Policy

**Status:** `ACTIVE`

This policy defines which documents change when implementation, audit, validation or planning work closes.

## Allowed status values

Use only:

- `PLANNED`
- `ACTIVE`
- `BLOCKED`
- `VALIDATING`
- `DONE`
- `DEFERRED`
- `SUPERSEDED`

`DONE` is allowed only after implementation, all required validation and merge are complete. A local, feature or failed audit head is never sufficient.

## Formal status and branch-local result

Formal project and document status uses only the allowed values above. Execution stages on an unmerged branch use descriptive results such as `completed on feature head`, `awaiting audit` or `pending cutover`; they do not use `DONE` to describe branch-local completion.

## Closeout record contract

Every closeout result must eventually be reflected in [work-plan.md](work-plan.md) with:

- result;
- exact head and parent when applicable;
- completed scope;
- validation evidence;
- findings;
- current gate;
- next action;
- unresolved risks.

The actor and exact-head state determine when that update occurs. A read-only actor does not mutate a frozen audited or validated head merely to record its result. The next authorized mutation-capable owner must incorporate any deferred closeout result before resuming material changes. Do not preserve an obsolete next action after a gate changes.

## Mutation-capable Worker closeout

A mutation-capable Worker:

- includes its material change and Work Plan update in the same resulting head;
- records the branch state, completed scope, evidence, risks and next gate before audit begins;
- reports the resulting exact head and parent after commit creation;
- does not use branch-local completion as formal `DONE`.

Because a commit cannot contain its own resulting SHA, the Work Plan header records the authoritative head at task start. When it does so, the labels must be `Task-start exact head` and `Task-start exact parent`, or unambiguously equivalent wording; a task-start SHA must not be labeled `Current exact head`. The Worker final report owns the resulting exact head and parent, and the next authorized mutation-capable owner updates the header before another material mutation.

## Read-only Auditor or Validator closeout

A read-only Auditor or Validator:

- does not modify the branch under audit or validation;
- records exact head, result, findings and next gate in its final report;
- leaves a successful immutable validation chain on the same exact head;
- on failure, requires the next authorized Worker to reflect the result in the Work Plan before repair begins;
- leaves successful results for the final merge closeout or an explicit post-merge documentation closeout to incorporate.

A read-only actor is never the mutation owner for the Work Plan on the head it is auditing or validating.

## Exact-head freeze

An exact-head freeze begins when an independent exact-head audit, controlled comparison, canonical validation or final audit starts. During the freeze, do not add or change:

- source;
- tests;
- documentation;
- metadata commits.

If a frozen check fails, end the freeze. The next authorized repair Worker records the failure in the Work Plan, applies the repair and creates a new exact head. If the frozen checks succeed, keep the same exact head as the merge target. Record formal completion only after merge through an explicit post-merge documentation closeout.

## Roadmap update conditions

Update [roadmap.md](roadmap.md) only when one of these occurs:

- a milestone starts;
- a milestone completes;
- milestone order changes;
- scope is added or removed;
- a defer or supersede decision is made.

Do not add Worker commits, temporary audit findings, exact validation counts or detailed thresholds to the roadmap.

## Roadmap replacement and compaction

The Roadmap is not a closeout journal.

- Keep exactly one current entry per milestone.
- Update status, major result and next gate in place rather than appending a new milestone record.
- Compress completed milestones to purpose, formal status, major result, maintenance gate and detail links.
- Remove obsolete prior-state wording; rely on Git history for detailed status transitions.
- Never add a closeout-history, audit-history or validation-history section.

## Work Plan replacement and compaction

The Work Plan manages exactly one active milestone.

- Replace Current gate, Next action, Blocking findings and Open risks with the latest current-state content.
- Remove resolved findings and risks that no longer affect the current decision.
- Keep execution-stage entries short and current; do not preserve earlier stage descriptions as a journal.
- Maintain exactly one `Latest recorded closeout` block and replace the complete block at the next mutation-capable closeout.
- Do not append audit logs, validation logs, commit history or previous closeout blocks.
- Replace the document with the next active milestone when the current milestone closes.
- Create an archive snapshot only with explicit approval for exceptional historical value; do not create one automatically for every milestone.

## Size discipline

Roadmap and Work Plan closeouts must compact obsolete content as part of the same change. Avoid repeating the same fact across sections. Link detailed evidence to architecture or quality documents, external artifacts or Git history. Document growth is not evidence of progress.

## Architecture document update conditions

Update the relevant architecture document when:

- a responsibility boundary changes;
- a domain type or interface changes;
- legacy architecture is removed;
- a new design decision is confirmed.

Draft experiments and rejected alternatives belong in the work-plan findings unless they remain necessary to understand the accepted contract.

## Quality document update conditions

Update the relevant quality document when:

- an acceptance metric changes;
- a fixture category is added or changed;
- a manual validation obligation changes;
- a CPU, memory or packaging gate changes.

## Documentation index update conditions

Update [docs/README.md](../README.md) when:

- a file is added, moved, renamed or archived;
- the authoritative hierarchy changes.

## Feature document ownership

Feature documents own requirements, design and validation contracts for that feature. They do not own the project-wide milestone sequence, active gate or current next-work list. Replace duplicated project status with links to the roadmap or work plan.

## Archive procedure

Move a meaningful but fully superseded document to `90-archive/`. Add a notice at the top that states:

- status `SUPERSEDED`;
- why it is superseded;
- the replacement document links.

Do not delete meaningful historical documents solely to simplify the active structure.

## Link and consistency validation

When documentation changes structure, verify:

- all relative Markdown links;
- root-document links into `docs/`;
- cross-document links and anchors;
- old filename references in source, tests and comments;
- case-sensitive path spelling;
- duplicate ownership of roadmap state or active next action;
- `git diff --check`.

A runtime-only checker may be created under `/tmp`; it must not be committed.
