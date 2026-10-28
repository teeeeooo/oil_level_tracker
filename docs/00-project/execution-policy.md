# Repository Execution Policy

**Status:** `ACTIVE`

This document owns only the repository-specific rules for verification,
Windows runs, publication and formal completion. The user-level agent
harness owns generic autonomy and approval behaviour.

## Proportional verification

Use the smallest evidence that proves the changed contract. Broaden it only
when a failure, an impact across owners or an open acceptance risk requires
it.

| Change | Evidence |
|---|---|
| Documentation | `scripts/check_docs_catalog.py`, `tests/test_docs_catalog.py` and `git diff --check` |
| `domain`, `analysis`, `storage` | Focused unit tests for the changed behaviour |
| `server`, `web` | API tests, plus a Playwright browser smoke check on macOS for visible behaviour |
| Platform and package | A Windows run (below). macOS results never stand in for it |

A passing local suite never substitutes for a criterion that requires
Windows.

## Windows runs (one-way)

Development happens on macOS. Windows is reached only through the user.

1. **The request.** It is a Korean instruction document under
   `docs/40-operations/` that states:
   - the exact source identity: branch, commit and per-file SHA-256;
   - the environment setup;
   - the inputs and the steps;
   - the pass criteria, fixed **before** the run;
   - one fixed result block to return.
2. **The result** comes back as relayed text and may contain transcription
   slips.
   - Identify runs by their logged values.
   - Recheck any derived counts against the listed rows.
3. **The record.** The judged result goes in `docs/60-evidence/` as
   `YYYY-MM-DD-topic.md`. It judges the result against the pre-fixed
   criteria and names the commit that was run.

## Exact-head review

A review, an acceptance check or a Windows run names the exact commit it
judges. Changing the code afterwards makes a new head. Only the evidence
that the change invalidates needs rerunning.

## Publication boundary

These happen only when the user's granted authority covers them:
- merging to `main`, release and deployment;
- deleting remote data or branches;
- irreversible migration.

Within that authority, verify the intended branch and head before
publishing. Verify the remote state after publishing.

## Current-state closeout

- **`work-plan.md`:** update it when the current step, its blocker or the
  next transition changes. It holds the current state only; history lives
  in Git and `60-evidence/`.
- **`roadmap.md`:** update it when milestone order, scope or formal state
  changes.
- **Formal `DONE`:** a milestone is `DONE` only when implementation, its
  acceptance and its publication are complete. Local tests alone do not
  make it `DONE`.
