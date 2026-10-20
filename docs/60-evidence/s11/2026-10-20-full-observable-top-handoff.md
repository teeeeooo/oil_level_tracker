# S11 FULL observable-top handoff — 2026-10-20

## Current disposition

S11 ACTIVE / O2 OPEN / Windows FIELD FAIL. Default R22 + R22-3/O1 and every
experiment flag are unchanged; this session made **no production change**.
[Work Plan](../../00-project/work-plan.md) is the only current-state and
authorization owner. Everything below is committed and pushed. All 104 managed
runs check clean.

The user chose to **pause the layered-Foam line and start the FULL
observable-top question (B)** next.

## What this session settled

| Item | Outcome | Owner |
|---|---|---|
| ATG-1 | Same texture-support mechanism at Windows Accum 673–677 s; at 677–679 s an upper anchor demotes the boundary | [ATG-1](../../50-diagnostics/s11/2026-10-20-accum-texture-gate.md#decision) |
| Foam-collapse target | User: best = air–liquid top **and** liquid–liquid layer; fallback = air–liquid top | [Reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#accum-foam-collapse-target--2026-10-20) |
| LBW-1/2/3 | Layer-bottom witness; LBW-3 (first supported bottom) transferred to held-out 673–677 s (0/24 negatives) but is blind at 678.5 s (Foam fading). Closed | [LBW-3](../../50-diagnostics/s11/2026-10-20-layer-bottom-witness-3.md#windows-held-out-result) |
| ARV-1 + review-010 | 678.5 s anchor Y229 **is** the air–liquid top (fallback met; published Y238 is not); 677 s anchor Y235 is the **air–Foam top** | [ARV-1](../../50-diagnostics/s11/2026-10-20-approach-review.md#review-010-result) |
| LBQ-1 | Unit-qualified support moves anchors to the layer bottom; publication then fails at selection (42.5 s Y805) and fill phase (48.5–56 s). Closed | [LBQ-1](../../50-diagnostics/s11/2026-10-20-layer-bottom-qualified-authority.md#results-and-decision) |
| SFR-1 | Both LBQ-1 failures come from **one mixed-identity owner** (F04) that alternates between rows above the Foam row and the layer bottom; the unit is a 12 px role band, not a position | [SFR-1](../../50-diagnostics/s11/2026-10-20-selection-fill-review.md) |
| LBT-1 | Topology rule E1 (no Oil above the layer bottom in the ordered-lower context) removes the mixing. Best sample4 baseline of the line (42/42.5/44/52 s within C1; wrong 42 s Y868 minimum gone). Closed on 1/246 opposed reselection and 5 Foam-episode changes; pre-registered outcome **G**: 54.5 s fill confirmed | [LBT-1](../../50-diagnostics/s11/2026-10-20-layer-bottom-topology.md#results-and-decision) |

## Paused line: layered Foam (resume after B)

- **What works:** the LBW-3 unit as a role witness plus E1 topology, limited to
  the ordered-lower context. Tools: `tests/diagnostics/s11_layer_bottom_topology.py`
  (frozen `142ec42`), reusing `s11_layer_bottom_qualified_authority.py` and
  `s11_layer_bottom_witness.py`.
- **Open issues at pause:**
  1. outcome G (fill geometry, which B should resolve);
  2. Foam publication following Oil in the 5 all-Oil withdrawal conditions,
     the same set seen in TPA-1/LBQ-1/LBT-1 (F06);
  3. 39.5–40 s frames where the Foam row lies below the unit (outside the
     context).
- **User decision for the successor (LBT-2):** option (b). A Foam change is no
  longer an automatic stop. It is judged against truth or a human review, and
  only a wrong change stops the run. Pre-register this before the run.
- **A Foam-visible fill guard (option A) was considered and not started.** If B
  replaces the proximity rule, it is unnecessary. If B only adds top-exit, A's
  problem remains.
- Windows S2 for this line still needs review-011 (unread layered frames
  672–677.5 s) first, then a separate go.

## Root issue for B: no defined observable top

The Oil phase owner infers FULL from geometry that has no defined "observable
top". Two rules fail in opposite directions:

| | sample4 (LBT-1 outcome G) | Windows BASE refill (top-exit preflight) |
|---|---|---|
| Rule | Fill confirmation: a rising anchored chain whose last row is within the top 27 % (`entrance_band_ratio`) and has risen ≥ 20 % of the height | Top-exit: the owner reaches `ellipse.center_y − radius_y` within tolerance, then vanishes |
| Geometry | Ellipse Y798–902; band ends Y826; the reviewed level Y829–844 sits 3–18 px below it | Configured top Y211.6 (allowed ≤ Y220.9); effective-mask top Y243 |
| Result | Not full, read as FULL (`FILLED_CAP_VETO` 54.5–56 s) | Full (674–675 s), never FULL; also an observation gap: the last selected Oil is Y352 (672.5 s), 109 px below the mask top |
| Sources | [LBT-1 G](../../50-diagnostics/s11/2026-10-20-layer-bottom-topology.md#results-and-decision), [SFR-1 finding 2](../../50-diagnostics/s11/2026-10-20-selection-fill-review.md#finding-2--the-unit-marks-a-role-band-not-a-position) | [Top-exit preflight](2026-10-16-top-exit-full.md#windows-geometry-preflight-received--condition-failed) |

FILLED is also **not reversible** by a persistent visible interface: only a
downward drain release lifts the cap. This is deliberate. Windows BASE FULL
has known false anchors (721 s), so making it reversible touches F05.

**Earlier rule still in force:** do not substitute the mask edge for the
physical top or reduce the margin before the *meaning* of the top input is
defined
([top-exit evidence](2026-10-16-top-exit-full.md#geometry-limitation-and-windows-boundary)).
The user owns that definition.

## First tasks for the next session (B review; desk work first)

1. **Bounded recall:**
   - [top-exit FULL evidence](2026-10-16-top-exit-full.md) and the
     [Windows top-exit procedure](../../40-operations/s11-current-windows-field-qualification.md#top-exit-full-comparison);
   - the design section
     [October 16 top-exit FULL closure](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-16-top-exit-full-closure);
   - logic map §4.3 (phase) and §4.4 (top-exit route);
   - failure registry `S11-F05` and `S11-F08`.
2. **Inventory every use of the top geometry** in source:
   - `entrance_band_ratio` (fill confirmation; it also appears in
     `oil_interface_selector.py`);
   - `drain_entrance_ratio`, `completed_fill_*`;
   - the R21 refill closure and `oil_top_exit_full.py`.

   For each, record which FULL/EMPTY transition it decides.
3. **Reconcile a sample4 discrepancy:** the top-exit evidence table lists
   sample4 "configured top Y808 / mask top Y811". Both `sample/sample4.oilrecipe`
   and the P5 bundle snapshot give an ellipse top of **Y798** (center 850,
   radius_y 52, margin 0.08). Find which quantity Y808 was before using either.
4. **Write a B design review** under `50-diagnostics/s11/`. It holds the
   decisions only the user can make:
   - what "observable top" means per Glass: the effective-mask top or a
     human-confirmed physical top;
   - whether top-exit **replaces** the 27 % proximity confirmation or only
     adds to it;
   - how to investigate the Windows Y352 observation gap. Is it in the saved
     ④ trace? If so, a read-only extraction request in the established Windows
     style.
5. No detector change, flag, Windows run or tuning until the user chooses.

## Constraints to preserve

- Private Windows media stays on Windows; requests are Korean text, and the user
  transcribes the results back. Reuse the ④ bundle. O2 human reviews go through the
  existing `prepare → link-bundle → record` workflow; the next free case ID is
  **review-011**.
- Keep review-006 pending and untouched, the 721 s false anchor, the 723/771 s
  protections, and FULL CONDITION FAILED / ⑧ NOT RUN. Sample3 stays
  quarantined.
- The Windows nine-segment truth is the oracle; detector output is not truth.
  sample4 is development data and Windows 673–679 s has been read.
- Freeze protocol and tool before execution; no tuning after results.

## Reproduce locally

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests --ignore=tests/diagnostics
.venv/bin/python scripts/check_detector_governance.py --base-ref HEAD --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
```

The LBT-1 run reproduces with
`.venv/bin/python -m tests.diagnostics.s11_layer_bottom_topology --work <new managed work dir>`
(about 4 minutes).

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F10`.
- First harmful stage: for the paused layered-Foam line, `OIL-TRACKLET` mixed identity (SFR-1), removed by LBT-1 E1. For B, `OIL-PHASE-FILL`/`OIL-PHASE-DRAIN` FULL inference from undefined top geometry (LBT-1 outcome G; Windows top-exit preflight).
- Existing feature coverage: sample4 P5 saved raw/Recipe with the 246-condition SOI population; the Windows ④ FULL+ON v2 bundle (read-only extractions and review-009/010); the top-exit route remains default OFF and unexercised on Windows.
- Execution scope: handoff only; no runtime exercised beyond the linked studies.
- Logic-map impact: NONE — handoff document; ownership and control flow unchanged.
- Failure-registry impact: NONE — pointers are in the linked studies.
