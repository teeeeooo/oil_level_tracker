# Oil Level Tracker v2 Repository Overlay

The user-level `AGENTS.md` owns generic execution behaviour. This file keeps
only repository-specific routing and invariants.

## Current owners

- **Current state, next step and authorization:**
  [docs/work-plan.md](docs/work-plan.md).
- **Product decisions** (what v2 does and does not do):
  [docs/decisions.md](docs/decisions.md). A change to a decision needs the
  user.
- **Visual language:** [DESIGN.md](DESIGN.md). It covers colours, type,
  spacing and the domain colour roles. Every screen and the report follow it.
  Add a token there before you use it.

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
  one-way:
  1. write the request as a Korean text instruction;
  2. results come back as relayed text;
  3. identify runs by their logged values, not by memory.

## Layout

| Path | Contents |
|---|---|
| `src/oil_tracker/` | Python package |
| `tests/` | pytest suite |
| `design/` | design mock-ups; not product code |
| `sample/` | local videos and old sample files; ignored by Git, not product input |
