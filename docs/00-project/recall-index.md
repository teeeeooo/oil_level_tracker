# Recall Index

Compact routes to past decisions and material, for work that depends on the
past or when the reason behind something is unclear.

- **This index owns no current state.** Current owners outrank it.
- **v1 material is read from tag `v1-final`,** for example with
  `git show v1-final:<path>`.

| When you need | Go to | Note |
|---|---|---|
| Why v2 exists; the user's interview answers | `v1-final:docs/60-evidence/s11/2026-10-28-v2-direction-interview-handoff.md` | Both interview tables, the spike's Windows GO result and the seven change requests. The [Product SSOT](../10-product/product.md) holds the current decisions |
| Web UI spike code and criteria | branch `spike/webui`, `spikes/webui/` (`README.md`, `WINDOWS_REQUEST.md`) | Port `context.py`, `render.js` and the `server.py` bind fix after review. The request also names the field inputs |
| Field videos and their v1 Recipes | `spike/webui:spikes/webui/WINDOWS_REQUEST.md`; [V2-1 Windows result](../60-evidence/2026-10-29-v2-1-recipe-windows-result.md) | `SPL#4_Cooling_onoff_#2.mp4` (53,165,455 bytes); `SPL#1_Heating_coldstart.mp4`. Use the bundle manifest's source, not the bundle capture path. The V2-1 result lists both videos' size, fps and frame count, and the v2 Recipes left on the Windows PC |
| Judgment rule semantics to port | `v1-final:src/oil_tracker/domain/judgment.py` (`judge_samples`), `domain/recipe.py` (`JudgmentRule`), `domain/enums.py` (`JudgmentMode`) | RECOVERY / HOLD_BELOW_ZERO / HOLD_ABOVE_ZERO |
| User-reviewed truth for SPL#1 | `v1-final:docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | The user's video review, including FULL acceptable from about 672 s |
| Why S11 stopped; detector failure history | `v1-final:docs/00-project/work-plan.md`, `v1-final:docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | Frozen; read only for context |
| v1 local experiment outputs | `~/Developer/oil_level_tracker-v1-evidence/` (not in Git) | 150 managed runs; see its README. Keeping or deleting it is the user's call |
| Why the Oil draft is method B, with quick delete and the point line | [draft comparison](../50-diagnostics/2026-10-29-draft-method-comparison.md), [its Windows result](../60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md) | Every edge-based method followed Foam or fixed bands; the user chose B plus editing aids. Also the 202.1 s that started the A4 work |
| Why the analysis decodes in software; where its time goes | [A4 timing result](../60-evidence/2026-10-29-v2-2-analysis-timing-windows-result.md), [slowest-PC result](../60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md) | SPL#1: 87.4 s on the workstation, then 46.4 s with the medians on worker threads; 169.7 s on the slowest PC (Xeon E5-1620 v3), CPU-bound in decoding. Hardware decoding is slower on both. The second lists the candidates for less CPU work. In the app the workstation took 60.6 s ([V2-2 flow result](../60-evidence/2026-10-29-v2-2-analysis-flow-windows-result.md)) |
| A Windows request to copy | [2026-10-29-v2-2-analysis-flow-windows-request.md](../40-operations/2026-10-29-v2-2-analysis-flow-windows-request.md); [2026-10-29-v2-1-recipe-windows-request.md](../40-operations/2026-10-29-v2-1-recipe-windows-request.md) | Commit ZIP and PowerShell per-file SHA-256 check, new Python 3.14 venv, [에이전트]/[사용자] steps, criteria fixed before the run, one result block; `scripts/inspection_summary.py` and `scripts/recipe_summary.py` print the exact values |
| Why the editor works as it does (V2-3) | [Product SSOT](../10-product/product.md) §6, [editor.html](../../design/mockup/editor.html), [DESIGN.md](../../DESIGN.md) §5 | The user's decisions of 2026-10-29: re-analysis keeps the overlapping edits, a Save button with a question on leaving, the snap on at 8 px, one range tool for delete and "cannot judge", the smooth or pointed grab, named tool buttons |
| A request for a PC without an agent | [2026-10-29-v2-2-slowest-pc-timing-windows-request.md](../40-operations/2026-10-29-v2-2-slowest-pc-timing-windows-request.md) | The user runs three commands; the script measures stage by stage, prints a short source digest and writes a Markdown result (`scripts/time_analysis.py`) |
| v1 documentation conventions | `v1-final:docs/README.md` | v2 keeps the numbered folders, date catalog, roadmap, execution policy and this index. It drops the S11 governance hook and the experiment-artifact tool |
