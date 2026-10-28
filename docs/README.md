# Documentation Map and Authority

This file is the **documentation-routing SSOT**.
- It classifies documents and points to their current owners.
- It does not duplicate project state or execution policy.
- Read it before you create, move, rename or archive a document, or when the
  right owner is unclear.

## Fresh reading path

Read only what the task needs:
1. **Current state and authorization:**
   [00-project/work-plan.md](00-project/work-plan.md).
2. **Goal, acceptance criteria and product decisions:**
   [10-product/product.md](10-product/product.md).
3. **Module boundaries:**
   [20-architecture/architecture.md](20-architecture/architecture.md).
4. **Visual rules:** [../DESIGN.md](../DESIGN.md).
5. **Milestone order:** [00-project/roadmap.md](00-project/roadmap.md).
6. **Past decisions or v1 material:**
   [00-project/recall-index.md](00-project/recall-index.md).

## Directory taxonomy

| Directory | Responsibility | Authority boundary |
|---|---|---|
| `00-project/` | work plan, roadmap, execution policy, recall index | project sequence and current step; not feature design |
| `10-product/` | Product SSOT and later user-facing contracts | goal, acceptance criteria, durable behaviour |
| `20-architecture/` | module boundaries, invariants, data schemas | accepted structure; not a work chronology |
| `30-validation/` | validation and acceptance procedures that elaborate the SSOT §2 | what must be shown for acceptance |
| `40-operations/` | Windows requests, package and manual procedures | how to perform a check; not proof that it passed |
| `50-diagnostics/` | investigations and probes | causal support; never current authority |
| `60-evidence/` | completed results: Windows results, acceptance judgments | historical proof; its status wording does not become current authority |
| `70-reference/` | external material and provenance | supporting only |
| `90-archive/` | superseded documents | not current authority |

Create a directory when its first document is needed.

## Authority hierarchy

When documents disagree, use the owner of the responsibility in question:
1. goal, acceptance and product decisions —
   [10-product/product.md](10-product/product.md);
2. milestone order and state — [00-project/roadmap.md](00-project/roadmap.md);
3. the exact current step — [00-project/work-plan.md](00-project/work-plan.md);
4. verification, Windows-run, publication and closeout rules —
   [00-project/execution-policy.md](00-project/execution-policy.md);
5. module boundaries — [20-architecture/architecture.md](20-architecture/architecture.md);
   visual rules — [../DESIGN.md](../DESIGN.md);
6. validation procedures, then operations;
7. diagnostics, evidence and reference as supporting provenance;
8. the archive and the v1 tag, only for historical context.

## Update rules

| A change to… | Goes in |
|---|---|
| the current step, a blocker or the next transition | `00-project/work-plan.md` |
| milestone order, scope or state | `00-project/roadmap.md` |
| goal, acceptance criteria or a product decision (needs the user) | `10-product/product.md` |
| module boundaries or a saved-data schema | `20-architecture/` |
| colours, type or layout rules | `../DESIGN.md` |
| a completed Windows result or an acceptance judgment | `60-evidence/YYYY-MM-DD-topic.md` |
| a new route to past material | `00-project/recall-index.md` |

- Current-state documents are rewritten, not appended to. History lives in
  Git.
- Do not copy current status into evidence or architecture for convenience.

## Dates and the catalog

- **Every Git-tracked file under `docs/` is listed in the
  [date catalog](catalog-by-created-date.md),** grouped by folder and then
  by first Git-add date (KST).
- **Update the catalog in the same change** that creates or moves a file.
- **The pre-push hook checks it:**
  - `.githooks/pre-push` runs `scripts/check_docs_catalog.py`;
  - install the hook with `scripts/install_git_hooks.sh`.
- **File names:** owners keep stable names. One-off records use
  `YYYY-MM-DD-topic.md`.
