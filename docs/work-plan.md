# Current Work Plan

**Milestone:** `V2 — Graph-editing inspection` / `ACTIVE` (started 2026-10-28).
**Decisions:** [decisions.md](decisions.md). **Visual rules:** [../DESIGN.md](../DESIGN.md).

## v1 handover

- **v1 is preserved** as tag `v1-final` and branch `archive/v1`. S11 is
  frozen as unmet: O2 OPEN, final Windows disposition FIELD FAIL.
- **v1 local evidence** (`sample/output/`, 150 managed runs) moved outside
  the repository to `~/Developer/oil_level_tracker-v1-evidence/`. Whether to
  delete it is the user's call.
- **Remote branches:**
  - The five already merged into v1 `main` were deleted.
  - These stay because v1 docs cite them: `codex/ui-ux-refresh`,
    `work/s11-spatial-identity-20261008`,
    `work/s11-windows-first-detector-20261008`.
- **`spike/webui`** stays as the reference for porting the editor drawing
  code.

## Work order (first version)

| Step | Scope | State |
|---|---|---|
| 1 | Start: freeze S11, v1 tag and archive, `main` reset, deferred cleanup | DONE (2026-10-28) |
| 1a | `DESIGN.md` (Fluent 2, light, domain colour roles) | IN PROGRESS |
| 1b | Static editor layout mock-up (`design/mockup/editor.html`) | NOT STARTED |
| 2 | Recipe screen: Glass ellipse, zero line, judgment rule | NOT STARTED |
| 3 | Analysis: context image and Oil draft, with progress and cache | NOT STARTED |
| 4 | Editor: grab/pencil, "cannot judge", lines, memos, zoom/pan/axis input, frame and video | NOT STARTED |
| 5 | Judgment, override, report, submit/lock, versions | NOT STARTED |
| 6 | Windows packaging and field-video acceptance | NOT STARTED |

## Next

- **Authorized now:** steps 1–1b only (user: "v2 시작하고 3번까지만
  진행해줘").
- **Next action:** the user reviews the mock-up. Step 2 starts only when the
  user says so.
