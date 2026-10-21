# Initial-state continuing-run rule and report bands — local implementation

**Status:** IMPLEMENTED / LOCAL VERIFICATION PASS / Windows NOT RUN. These
changes are downstream of the detector; detector output and the top-exit v3
option are unchanged. O2 OPEN / FIELD FAIL and review-006 pending are unchanged.
Current authority is the [Work Plan](../../00-project/work-plan.md).

## What was built

The rules were frozen at `67f1484` before any code change, from the
[⑩ report receipt](2026-10-21-top-exit-v3-local.md#report-and-judgment-receipt--2026-10-21)
and the user's decisions:
- **B, [continuing-run rule](../../20-architecture/initial-state-retrospective-reconstruction-architecture.md#modern-stream-continuing-run-rule--2026-10-21)**
  (`initial_state_reconstruction.py`):
  - **Scope:** modern streams only; legacy R7 anchor streams keep their path.
  - **Barriers:** the sequence resolvers' ordinary-UNKNOWN markers are no longer
    barriers. Hard failures and published Foam still are.
  - **Run:** it starts at the first accepted boundary and ends at a step above
    `temporal_max_jump_px` or at a barrier.
  - **Decisive move:** two consecutive boundaries beyond the existing tolerance
    on the same side. If that move is toward the prior's direction the result is
    ACCEPTED; if it goes the other way, CONFLICT. Otherwise UNRESOLVED.
  - **Topology:** stays provenance only.
  - **Provenance:** `initial_state_retrospective_v2`, with three evidence frames.
- **A, [state bands](../../20-architecture/s11-report-context-presentation-design.md#fullempty-bands-and-judgment-reason--2026-10-21)**
  (`graph_renderer.py`):
  - every FULL/EMPTY band is drawn at alpha 0.09 and labelled by source:
    `FULL 판정` / `EMPTY 판정`, `초기 상태 재구성 (…)` or
    `확정 초기 상태 유지 가정 (…)`;
  - the combined graph is unchanged.
- **C, judgment reason** (`report_presentation.py`):
  - `판정 안내` appends plain-Korean reasons for the known note forms;
  - unknown forms add nothing, and the raw English note is never shown.
- **Logic map:** the `RESULT-PRESENTATION` row records A and C.

**Module SHA-256:**

| Module | SHA-256 |
|---|---|
| `initial_state_reconstruction.py` | `9fd04d25a10860fb5ba506311170209e71a9cfb09803f6166a1de5a4f93e1eed` |
| `graph_renderer.py` | `a4776e06ff95f0ad44acd308f18e417d2645ffb2189ddac11ff870dd1217ebf5` |
| `report_presentation.py` | `6a1b0b512f8008bda71de4ae6bcb452e0c7a9295753b4edff06f446a10d6469f` |
| `oil_top_exit_full.py` | unchanged, `10dd3605…6f77d` |

## Verification

- **Reconstruction tests:** 51 passed
  (`tests/test_initial_state_retrospective_reconstruction.py`).
  - **Fixtures rewritten:** the modern fixtures now show a confirmed move with a
    third boundary. Under the frozen rule a single beyond boundary is not
    decisive, so evidence becomes three frames.
  - **New cases:**
    - ordinary UNKNOWN markers do not block;
    - hard failures inside the run do (frame unavailable, fog/glare, detection
      lost, no-interface evidence unavailable);
    - one beyond, stationary and end-after-one stay unresolved;
    - a fall followed by a rise, and the EMPTY mirror, are accepted;
    - a first move against the prior is a conflict;
    - a step above the jump limit stays unresolved.
  - **⑩ BASE shape** (the received Y values for 548.5–568.0 s, the received
    geometry and the 32 px limit): ACCEPTED, with evidence at the first boundary
    and Y374/375. Relative position 0.196.
  - **⑩ Accum shape:** UNRESOLVED, both with a Foam row before the first boundary
    (`AUTHORITATIVE_FOAM`) and without it (the 33 px step).
- **Mutation checks:**
  - treating the ordinary-UNKNOWN markers as barriers again fails 12 cases;
  - deciding on the first beyond boundary fails 9 cases.

  The code was restored before the suite run.
- **Renderer and presentation tests:**
  - **State bands:** a reconstructed prefix is labelled `초기 상태 재구성 (FULL)`
    and a top-exit FULL block `FULL 판정`, both at alpha 0.09. The existing hold
    label test passes.
  - **Judgment guidance:** coverage, retrospective provenance, a violation
    duration with a conflict, and an unknown note all produce the expected
    guidance without the raw English text.
- **Full unit suite** (`tests`, excluding `tests/diagnostics`): 3,821 passed,
  12 skipped. The skips are the quarantined sample3 corpus; they were not
  bypassed.
- **Rendered check:**
  - **Input:** a scratch script built a ⑩-like BASE sequence from the receipt:
    - 137 UNKNOWN rows with the R17 markers;
    - the received Y values for 548.5–581.5 s, with their UNKNOWN gaps;
    - a 30-row top-exit FULL block.
  - **Outcome assembler:** ACCEPTED, with the prefix at 479.98–547.98 s and the
    decisive move at 567.48/567.98 s. `HOLD_ABOVE_ZERO` then passes on the
    level.
  - **Rendered detail graph:** both labelled bands are visible.

  This is a visual check of the code path. The synthetic sequence is not ⑩'s
  output and creates no evidence about its later rows.

## Limits

- **Windows not run.** The ⑩ bundle's official judgment and report stay as
  written; seeing the change on Windows needs a new run.
- **The Accum protection is incidental.** It comes from the Foam barrier and the
  continuity bound, not from direction. A late first catch with neither would be
  accepted.
- **No visual difference between sources.** Bands from different sources share
  one colour and emphasis; only the legend tells them apart.
- **Combined graph unchanged.** It still draws no state bands.

## Detector Governance

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F05`, `S11-F09`, `S11-F10`
- First harmful stage: none in the detector. The ⑩ report problems arose downstream of `PUBLICATION-PROVENANCE`: the retrospective owner treated the resolver's ordinary-UNKNOWN marker as a barrier and required a move between the first two boundaries; `RESULT-PRESENTATION` drew FULL bands at alpha 0.035 without labels and gave no judgment reason.
- Existing feature coverage: the existing confirmed initial state, retrospective projection, `HOLD_ABOVE_ZERO`/`HOLD_BELOW_ZERO` judgment consumption, Recipe `radius_y` tolerance and `temporal_max_jump_px`, and the existing hold band label are reused. Detector output, top-exit v3, events, CSV and bundle files are unchanged; RECOVERY still receives observed samples only.
- Execution scope: unit tests with two mutation checks, the full unit suite and one scratch rendered check built from transferred ⑩ values. No detector run, Windows execution, private media, human review or tuning.
- Logic-map impact: UPDATED — the `RESULT-PRESENTATION` row records the source-labelled FULL/EMPTY bands and the plain judgment reason.
- Failure-registry impact: NONE — no detector mechanism changed. The rule narrows a downstream F05-shaped risk (a confirmed state hidden by soft UNKNOWN markers) without adding a threshold (F10); report wording still adds no measurement (F09).
