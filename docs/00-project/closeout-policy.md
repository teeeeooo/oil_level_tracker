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

## Every closeout

Update [work-plan.md](./work-plan.md) with:

- result;
- exact head;
- completed scope;
- validation evidence;
- findings;
- current gate;
- next action;
- unresolved risks.

The work plan must reflect the authoritative final state of the closeout, including a failed or blocked result. Do not preserve an obsolete next action after a gate changes.

## Roadmap update conditions

Update [roadmap.md](./roadmap.md) only when one of these occurs:

- a milestone starts;
- a milestone completes;
- milestone order changes;
- scope is added or removed;
- a defer or supersede decision is made.

Do not add Worker commits, temporary audit findings, exact validation counts or detailed thresholds to the roadmap.

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