# Oil Level Tracker v2 Repository Overlay

The user-level `AGENTS.md` owns generic execution behaviour. This file keeps
only repository-specific routing and invariants.

## Current owners

- **Documentation map and authority:** [docs/README.md](docs/README.md).
  Read it before creating, moving or archiving a document.
- **Current state, next step and authorization:**
  [docs/00-project/work-plan.md](docs/00-project/work-plan.md).
- **Goal, acceptance criteria and product decisions:**
  [docs/10-product/product.md](docs/10-product/product.md). A change to any
  of these needs the user.
- **Module boundaries and dependency rule:**
  [docs/20-architecture/architecture.md](docs/20-architecture/architecture.md).
- **Verification, Windows runs, publication and closeout:**
  [docs/00-project/execution-policy.md](docs/00-project/execution-policy.md).
- **Visual language:** [DESIGN.md](DESIGN.md). It covers colours, type,
  spacing and the domain colour roles. Every screen and the report follow it.
  Add a token there before you use it.
- **Past decisions and v1 material:**
  [docs/00-project/recall-index.md](docs/00-project/recall-index.md).

## Invariants

- **Back end:** Python 3.14, serving only on `127.0.0.1`.
- **Window:** pywebview. Windows uses WebView2.
- **Front end:** plain JavaScript, with no build step and no front-end
  framework.
- **Shared drawing:** one drawing module serves both the editor and the report.
- **No v1 compatibility.** Do not read v1 Recipes (`.oilrecipe`) or result
  bundles.
- **Porting v1 code:** port from tag `v1-final` one file at a time, after
  review. Record the source path in the commit message.
- **No detector.** v2 does not include the v1/S11 detector.
- **Windows is the target; macOS is for development.** Windows runs are
  one-way; follow the execution policy.
- **Hooks:** a new clone installs them with `scripts/install_git_hooks.sh`.
  The pre-push hook checks the docs date catalog.

## Layout

| Path | Contents |
|---|---|
| `src/oil_tracker/` | Python package |
| `tests/` | pytest suite |
| `scripts/` | repository checks and helpers |
| `design/` | design mock-ups; not product code |
| `sample/` | local videos and old sample files; ignored by Git, not product input |
